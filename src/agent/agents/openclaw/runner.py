"""OpenClaw agent runner for LongHorizon.

Deploys the OpenClaw harness framework inside a docker container and
executes tasks through its agent/gateway protocol.

Docker image is resolved by harness name: `longhorizon-openclaw:v1`
(not per-task like Terminal_Bench's `tb2-{task_id}:v3`).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))

from src.agent.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.agent.harness_registry import resolve_image
from src.agent.utils.docker_utils import (
    WORKSPACE_DIR,
    close_proc_log,
    copy_file_from_container,
    copy_tests_to_container,
    exec_in_container,
    remove_container,
    run_background,
    setup_workspace,
    start_container,
)

logger = logging.getLogger(__name__)

GATEWAY_PORT = int(os.environ.get("LONGHORIZON_GATEWAY_PORT", "18789"))


class OpenClawAgent(BaseAgent):
    """OpenClaw harness agent for LongHorizon evaluation.

    This agent deploys the OpenClaw framework (a mature agent harness)
    rather than building from scratch. The docker image is pulled by
    harness name, allowing the same image to serve all tasks.
    """

    def __init__(
        self,
        gateway_port: int | None = None,
        openrouter_api_key: str = "",
        openrouter_base_url: str = "",
        image: str | None = None,
    ) -> None:
        self.gateway_port = gateway_port or GATEWAY_PORT
        self.openrouter_api_key = openrouter_api_key or os.environ.get(
            "OPENROUTER_API_KEY", ""
        )
        self.openrouter_base_url = openrouter_base_url or os.environ.get(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        # Anthropic-compatible endpoint (Minimax supports this)
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "") or self.openrouter_api_key
        self.anthropic_base_url = os.environ.get("ANTHROPIC_BASE_URL", "") or ""
        self.default_model = os.environ.get("DEFAULT_MODEL", "")
        self._image = image

    @property
    def harness_name(self) -> str:
        return "openclaw"

    @property
    def docker_image(self) -> str:
        if self._image:
            return self._image
        return resolve_image(self.harness_name)

    @property
    def expects_gateway(self) -> bool:
        return True

    @property
    def transcript_container_path(self) -> str:
        return "/root/.openclaw/agents/main/sessions/chat.jsonl"

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        """Execute a LongHorizon task using the OpenClaw harness.

        Uses OpenRouter provider pointing to Minimax API (OpenAI-compatible).
        The gateway displays model as openrouter/openrouter/X due to a display bug,
        but the actual API call sends the correct model name to the endpoint.
        """
        gateway_proc = None
        agent_proc = None
        elapsed_time = float(spec.timeout_seconds)

        # Resolve model
        model = spec.model
        if self.default_model:
            model = self.default_model

        try:
            # Build environment - use OpenRouter vars pointing to Minimax
            env = {
                "OPENROUTER_API_KEY": self.openrouter_api_key,
                "OPENROUTER_BASE_URL": self.openrouter_base_url,
                **spec.extra_env,
            }

            # Start container using harness-named image
            start_container(
                container_name=spec.task_id,
                docker_image=self.docker_image,
                inputs_path=spec.inputs_path,
                extra_env=env,
            )

            # Aggressively remove proxy from container env (Node.js reads these at process start)
            exec_in_container(spec.task_id, (
                "sed -i '/proxy/Id' /etc/environment 2>/dev/null || true; "
                "sed -i '/proxy/Id' /root/.bashrc 2>/dev/null || true; "
                "sed -i '/proxy/Id' /root/.profile 2>/dev/null || true; "
                "rm -f /etc/profile.d/*proxy* 2>/dev/null || true; "
                "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy"
            ), timeout=10)

            # Install pytest + jsonschema for grading (synchronous)
            exec_in_container(spec.task_id, "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && pip install -q pytest jsonschema 2>/dev/null || true", timeout=120)

            # Setup workspace and copy test files
            setup_workspace(spec.task_id)
            tests_dir = spec.task_dir / "tests"
            if tests_dir.is_dir():
                copy_tests_to_container(spec.task_id, tests_dir)

            # CRITICAL: `openclaw setup` must run first, otherwise ~/.openclaw/openclaw.json
            # does not exist and every later config patch silently fails.
            # The image ships only the binary; the user state dir is created by `setup`.
            r_setup = exec_in_container(
                spec.task_id,
                "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy && "
                # `setup` is interactive in some versions; pipe newlines to accept defaults.
                "yes '' | openclaw setup 2>&1 | tail -50 || true",
                timeout=120,
            )
            logger.info("[%s] openclaw setup => exit=%d, tail=%s",
                        spec.task_id, r_setup.returncode, r_setup.stdout[-400:])

            # Configure OpenClaw with custom provider (writes ~/.openclaw/openclaw.json)
            self._configure_openclaw_openrouter(spec.task_id, model)

            # Verify config was written correctly
            r_verify = exec_in_container(
                spec.task_id,
                "python3 -c \""
                "import json,os;"
                "p='/root/.openclaw/openclaw.json';"
                "print('exists:', os.path.exists(p));"
                "c=json.load(open(p)) if os.path.exists(p) else {};"
                "print('model:', c.get('agents',{}).get('defaults',{}).get('model',{}).get('primary','NOT_SET'));"
                "print('gateway_mode:', c.get('gateway',{}).get('mode','NOT_SET'))\"",
            )
            logger.info("[%s] Config verify: %s", spec.task_id, r_verify.stdout.strip())

            # Diagnostics: dump OpenClaw CLI capabilities + final config (post-setup).
            self._dump_diagnostics(spec.task_id, spec.output_dir / "diagnostics.log")

            # Build the full prompt
            system_prompt = (
                f"You are an expert agent in a restricted, non-interactive environment. "
                f"Solve the task efficiently before the timeout ({spec.timeout_seconds}s). "
                f"Run all processes in the foreground. Provide a complete solution with no placeholders. "
                f"Your output must be written to {WORKSPACE_DIR}/answer.json.\n\n"
            )
            full_prompt = system_prompt + spec.instruction

            # Run agent in --local (embedded) mode.
            # `openclaw agent --help` confirms:
            #   --local   Run the embedded agent locally (requires model provider API keys
            #             in your shell)
            # --local sidesteps the WebSocket gateway entirely, so we don't need to start
            # `openclaw gateway run`. Provider keys come from env (OPENROUTER_API_KEY etc.)
            # plus the auth-profiles.json injected by _configure_openclaw_openrouter().
            #
            # Note: --allow-unconfigured does NOT exist on the agent subcommand
            # (only on gateway). It must NOT be passed here.
            safe_prompt = full_prompt.replace("'", "'\\''")
            start_time = time.perf_counter()
            # gateway_proc remains None — no external gateway needed in --local mode.
            agent_proc = run_background(
                spec.task_id,
                bash_cmd=(
                    f"unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy && "
                    f"export OPENROUTER_API_KEY='{self.openrouter_api_key}' && "
                    f"export OPENROUTER_BASE_URL='{self.openrouter_base_url}' && "
                    f"export ANTHROPIC_API_KEY='{self.anthropic_api_key}' && "
                    f"export ANTHROPIC_BASE_URL='{self.anthropic_base_url}' && "
                    f"openclaw agent --local "
                    f"--session-id chat "
                    f"--timeout {spec.timeout_seconds} "
                    f"--message '{safe_prompt}'"
                ),
                log_path=spec.output_dir / "agent.log",
            )

            # Wait for completion
            logger.info("[%s] Waiting for agent to finish...", spec.task_id)
            try:
                agent_proc.wait(timeout=spec.timeout_seconds)
                elapsed_time = time.perf_counter() - start_time
                logger.info(
                    "[%s] Agent finished, elapsed: %.2f seconds",
                    spec.task_id,
                    elapsed_time,
                )
            except subprocess.TimeoutExpired:
                logger.info("[%s] Agent timed out", spec.task_id)
                elapsed_time = float(spec.timeout_seconds)
                agent_proc.kill()
                agent_proc.wait()

            return AgentExecution(
                elapsed_time=elapsed_time,
                error=None,
                gateway_proc=gateway_proc,
                agent_proc=agent_proc,
            )

        except Exception as exc:
            logger.error("[%s] Execution error: %s", spec.task_id, exc)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error=str(exc),
                gateway_proc=gateway_proc,
                agent_proc=agent_proc,
            )

    def collect_usage(
        self, task_id: str, output_dir: Path, elapsed_time: float
    ) -> dict[str, Any]:
        """Collect token usage from OpenClaw transcripts."""
        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
            "elapsed_time": round(elapsed_time, 2),
        }

        transcript_host = output_dir / "chat.jsonl"
        output_dir.mkdir(parents=True, exist_ok=True)

        ok = copy_file_from_container(
            task_id, self.transcript_container_path, transcript_host
        )
        if ok and transcript_host.exists():
            usage = self._extract_usage_from_jsonl(transcript_host)

        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    def _set_model(self, task_id: str, model: str) -> None:
        r = exec_in_container(task_id, f"openclaw models set '{model}'")
        if r.returncode != 0:
            raise RuntimeError(f"Model setup failed:\n{r.stderr}")
        logger.info("[%s] Model set: %s", task_id, model)

    def _dump_diagnostics(self, task_id: str, log_path: Path) -> None:
        """Dump CLI capabilities + on-disk config so we can debug startup failures.

        Writes:
          - `openclaw --version`
          - `openclaw --help` (top-level)
          - `openclaw agent --help`
          - `openclaw gateway --help`
          - full openclaw.json
          - auth-profiles.json (with key redacted)
        """
        log_path.parent.mkdir(parents=True, exist_ok=True)
        sections: list[str] = []

        def _section(title: str, cmd: str, timeout: int = 30) -> None:
            r = exec_in_container(task_id, cmd, timeout=timeout)
            sections.append(
                f"\n===== {title} =====\n"
                f"$ {cmd}\n"
                f"--- exit={r.returncode} ---\n"
                f"--- stdout ---\n{r.stdout}\n"
                f"--- stderr ---\n{r.stderr}\n"
            )

        _section("openclaw --version", "openclaw --version 2>&1 || true")
        _section("openclaw --help", "openclaw --help 2>&1 || true")
        _section("openclaw setup --help", "openclaw setup --help 2>&1 || true")
        _section("openclaw agent --help", "openclaw agent --help 2>&1 || true")
        _section("openclaw gateway --help", "openclaw gateway --help 2>&1 || true")
        _section(
            "ls ~/.openclaw",
            "ls -laR /root/.openclaw 2>&1 | head -200 || true",
        )
        _section(
            "openclaw.json",
            "cat /root/.openclaw/openclaw.json 2>&1 || true",
        )
        _section(
            "auth-profiles.json (key redacted)",
            "python3 -c \""
            "import json,pathlib;"
            "p=pathlib.Path('/root/.openclaw/agents/main/agent/auth-profiles.json');"
            "d=json.loads(p.read_text());"
            "[v.update({'key':'***REDACTED***'}) for v in d.get('profiles',{}).values() if isinstance(v,dict) and 'key' in v];"
            "print(json.dumps(d,indent=2))\" 2>&1 || true",
        )

        # Connectivity probe: directly hit the upstream provider with a tiny
        # streaming request from inside the pod, so we can tell whether
        # "LLM idle timeout" is a network problem, an auth problem, or the
        # provider simply not streaming.  We try BOTH common Anthropic auth
        # header styles (x-api-key and Authorization: Bearer) plus list models.
        api_key = self.anthropic_api_key or self.openrouter_api_key or ""
        # Derive base URL the same way _configure_openclaw_openrouter does.
        # For MiniMax we know the base is `https://api.minimaxi.com/anthropic`.
        # We pull it back out of the on-disk config so this stays in sync.
        _section(
            "provider baseUrl (from openclaw.json)",
            "python3 -c \""
            "import json;"
            "c=json.load(open('/root/.openclaw/openclaw.json'));"
            "p=c.get('models',{}).get('providers',{});"
            "print(json.dumps(p,indent=2))\" 2>&1 || true",
        )
        _section(
            "DNS + TCP probe (api.minimaxi.com:443)",
            "python3 -c \""
            "import socket;"
            "print('A=', socket.gethostbyname('api.minimaxi.com'));"
            "s=socket.socket(); s.settimeout(5);"
            "import sys; sys.exit(0 if s.connect_ex(('api.minimaxi.com',443))==0 else 1)\""
            " 2>&1; echo exit=$?",
            timeout=15,
        )
        # /v1/models works for most Anthropic-compat backends; harmless if 404.
        # Use a 30s timeout to mirror the real request timing class.
        if api_key:
            _section(
                "curl /v1/models (x-api-key)",
                "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy && "
                f"curl -sS -m 30 -o /tmp/curl_xapi.body -w 'http_code=%{{http_code}}\\nsize=%{{size_download}}\\ntime=%{{time_total}}\\n' "
                f"-H 'x-api-key: {api_key}' "
                "-H 'anthropic-version: 2023-06-01' "
                "https://api.minimaxi.com/anthropic/v1/models 2>&1; "
                "echo '--- body (head) ---'; head -c 800 /tmp/curl_xapi.body 2>&1 || true",
                timeout=45,
            )
            _section(
                "curl /v1/messages with 1-token request (x-api-key)",
                "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy && "
                f"curl -sS -m 60 -o /tmp/curl_msg.body -w 'http_code=%{{http_code}}\\nsize=%{{size_download}}\\ntime=%{{time_total}}\\n' "
                f"-H 'x-api-key: {api_key}' "
                "-H 'anthropic-version: 2023-06-01' "
                "-H 'content-type: application/json' "
                """-d '{\"model\":\"minimax/MiniMax-M3\",\"max_tokens\":4,\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}' """
                "https://api.minimaxi.com/anthropic/v1/messages 2>&1; "
                "echo '--- body (head) ---'; head -c 1500 /tmp/curl_msg.body 2>&1 || true",
                timeout=75,
            )
            _section(
                "curl /v1/messages with 1-token request (Authorization Bearer)",
                "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy && "
                f"curl -sS -m 60 -o /tmp/curl_msg2.body -w 'http_code=%{{http_code}}\\nsize=%{{size_download}}\\ntime=%{{time_total}}\\n' "
                f"-H 'Authorization: Bearer {api_key}' "
                "-H 'anthropic-version: 2023-06-01' "
                "-H 'content-type: application/json' "
                """-d '{\"model\":\"minimax/MiniMax-M3\",\"max_tokens\":4,\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}' """
                "https://api.minimaxi.com/anthropic/v1/messages 2>&1; "
                "echo '--- body (head) ---'; head -c 1500 /tmp/curl_msg2.body 2>&1 || true",
                timeout=75,
            )
        else:
            sections.append("\n===== upstream curl probes =====\n(no api key configured, skipped)\n")

        log_path.write_text("".join(sections), encoding="utf-8")
        logger.info("[%s] Diagnostics dumped to %s", task_id, log_path)

    def _wait_for_gateway(self, task_id: str, max_wait: int = 30) -> None:
        """Poll the in-container gateway until it accepts TCP connections.

        Replaces the previous fixed `time.sleep(3)`, which is unreliable for
        K8S pod cold starts.  We probe the port from inside the pod itself
        (via `exec_in_container`) so we don't depend on host->pod networking.
        """
        port = self.gateway_port
        # Use python -c so we don't rely on `nc` / `curl` being installed.
        probe = (
            f"python3 -c \""
            f"import socket,sys; "
            f"s=socket.socket(); s.settimeout(1); "
            f"sys.exit(0 if s.connect_ex(('127.0.0.1',{port}))==0 else 1)\""
        )
        deadline = time.perf_counter() + max_wait
        attempt = 0
        while time.perf_counter() < deadline:
            attempt += 1
            r = exec_in_container(task_id, probe, timeout=5)
            if r.returncode == 0:
                logger.info(
                    "[%s] Gateway ready on :%d after %d attempt(s)",
                    task_id, port, attempt,
                )
                return
            time.sleep(1)
        # Don't hard-fail: agent may still work in --allow-unconfigured mode.
        logger.warning(
            "[%s] Gateway not responding on :%d after %ds; continuing anyway",
            task_id, port, max_wait,
        )

    def _configure_openclaw_openrouter(self, task_id: str, model: str) -> None:
        """Configure OpenClaw with a custom provider.

        Automatically selects API format based on model name:
        - Models containing 'gemini' use openai-chat API (avoids tool_choice incompatibility)
        - All others use anthropic-messages API
        """
        api_key = self.anthropic_api_key or self.openrouter_api_key

        # Select API format and base URL based on model
        # Anthropic API supports Claude via anthropic-messages format
        # OpenRouter API supports GPT + Gemini via openai-completions
        # Note: Gemini via /api/claude has tool_choice compatibility issues
        model_lower = model.lower()
        if "gpt" in model_lower or "gemini" in model_lower:
            # GPT and Gemini: use OpenAI completions format via OpenRouter
            api_type = "openai-completions"
            base_url = self.openrouter_base_url or "https://openrouter.ai/api/v1"
        else:
            # Claude, MiniMax: use Anthropic messages format
            api_type = "anthropic-messages"
            base_url = self.anthropic_base_url or "https://api.anthropic.com"

        # Use a generic provider name "custom"
        provider_name = "custom"

        config_cmd = f"""python3 -c "
import json, pathlib
config_path = pathlib.Path('/root/.openclaw/openclaw.json')
config_path.parent.mkdir(parents=True, exist_ok=True)
# Tolerate missing/empty config (e.g. when 'openclaw setup' did not pre-create one).
if config_path.exists() and config_path.stat().st_size > 0:
    config = json.loads(config_path.read_text())
else:
    config = {{}}

# Remove web search entirely
config['tools'] = {{'profile': 'coding'}}

# Define custom provider with {api_type} API
config['models'] = {{
    'providers': {{
        '{provider_name}': {{
            'api': '{api_type}',
            'baseUrl': '{base_url}',
            'models': [
                {{'id': '{model}', 'name': '{model}'}}
            ]
        }}
    }}
}}

# Set model to {provider_name}/{model}
config.setdefault('agents', {{}}).setdefault('defaults', {{}}).setdefault('model', {{}})
config['agents']['defaults']['model']['primary'] = '{provider_name}/{model}'
config['agents']['defaults']['models'] = {{'{provider_name}/{model}': {{}}}}
config['agents']['defaults']['workspace'] = '/workspace'

# Force gateway to local-mode so 'openclaw agent' can run without remote auth setup.
# Without this the agent's in-process gateway exits with:
#   'Missing config. Run \`openclaw setup\` or set gateway.mode=local'
config.setdefault('gateway', {{}})
config['gateway']['mode'] = 'local'

config_path.write_text(json.dumps(config, indent=2))
print(f'OK: model={provider_name}/{model}, api={api_type}, baseUrl={base_url}, gateway=local')
"
"""
        r = exec_in_container(task_id, config_cmd)
        logger.info("[%s] %s", task_id, r.stdout.strip())

        # Write auth-profiles with custom provider key
        auth_json = json.dumps({
            "version": 1,
            "profiles": {
                f"{provider_name}:default": {
                    "type": "api_key",
                    "provider": provider_name,
                    "key": api_key
                }
            },
            "lastGood": {provider_name: f"{provider_name}:default"}
        })
        import base64
        b64 = base64.b64encode(auth_json.encode()).decode()
        exec_in_container(
            task_id,
            f"mkdir -p /root/.openclaw/agents/main/agent && "
            f"echo '{b64}' | base64 -d > /root/.openclaw/agents/main/agent/auth-profiles.json",
        )
        logger.info("[%s] Auth key injected for %s provider", task_id, provider_name)

    def _inject_openrouter_key(self, task_id: str) -> None:
        if not self.openrouter_api_key:
            return

        # Write auth-profiles.json directly with a simple echo command
        # (avoids quoting issues with python -c and special chars in API key)
        auth_json = json.dumps({
            "version": 1,
            "profiles": {
                "openrouter:default": {
                    "type": "api_key",
                    "provider": "openrouter",
                    "key": self.openrouter_api_key
                }
            },
            "lastGood": {
                "openrouter": "openrouter:default"
            }
        })
        # Use base64 to safely transfer the JSON content
        import base64
        b64 = base64.b64encode(auth_json.encode()).decode()
        inject_cmd = f"echo '{b64}' | base64 -d > /root/.openclaw/agents/main/agent/auth-profiles.json"
        r = exec_in_container(task_id, inject_cmd)
        # Verify
        r2 = exec_in_container(task_id, "cat /root/.openclaw/agents/main/agent/auth-profiles.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(\"profiles:\", list(d.get(\"profiles\",{}).keys()))'")
        logger.info("[%s] Auth injected: %s", task_id, r2.stdout.strip())

    @staticmethod
    def _extract_usage_from_jsonl(jsonl_path: Path) -> dict[str, Any]:
        """Extract usage statistics from OpenClaw JSONL transcript."""
        totals: dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }
        if not jsonl_path.exists():
            return totals

        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "message":
                continue
            msg = entry.get("message", {})
            if msg.get("role") != "assistant":
                continue
            totals["request_count"] += 1
            usage = msg.get("usage", {})
            totals["input_tokens"] += usage.get("input", 0)
            totals["output_tokens"] += usage.get("output", 0)
            totals["cache_read_tokens"] += usage.get("cacheRead", 0)
            totals["cache_write_tokens"] += usage.get("cacheWrite", 0)
            totals["total_tokens"] += usage.get("totalTokens", 0)
            cost = usage.get("cost", {})
            totals["cost_usd"] += cost.get("total", 0.0)

        totals["cost_usd"] = round(totals["cost_usd"], 6)
        return totals
