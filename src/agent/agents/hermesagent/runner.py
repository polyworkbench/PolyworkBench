"""Hermes Agent runner for LongHorizon.

Deploys the Hermes Agent harness framework inside a docker container and
executes tasks through its Python-based bench runner protocol.

Docker image is resolved by harness name: `longhorizon-hermesagent:v1`
(not per-task like Terminal_Bench's `tb2-{task_id}:v3`).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.agent.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.agent.harness_registry import resolve_image
from src.agent.utils.docker_utils import (
    WORKSPACE_DIR,
    close_proc_log,
    copy_dir_from_container,
    copy_file_from_container,
    copy_file_to_container,
    copy_tests_to_container,
    exec_in_container,
    remove_container,
    run_background,
    setup_workspace,
    start_container,
)

logger = logging.getLogger(__name__)

HERMES_HOME = "/root/.hermes"
HERMES_INSTALL_DIR = "/opt/hermes"
HERMES_VENV_PYTHON = "/opt/hermes/.venv/bin/python3"
BENCH_CONFIG_CONTAINER_PATH = "/tmp/hermes_bench_config.json"


class HermesAgentAgent(BaseAgent):
    """Hermes Agent harness for LongHorizon evaluation.

    Deploys the Hermes Agent framework (open-source coding agent) inside
    a harness-named container. The docker image is pulled by harness name,
    not task name.
    """

    def __init__(
        self,
        openrouter_api_key: str = "",
        openrouter_base_url: str = "",
        brave_api_key: str = "",
        image: str | None = None,
    ) -> None:
        self.openrouter_api_key = (
            openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        ).strip()
        self.openrouter_base_url = (
            openrouter_base_url
            or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        ).strip()
        self.brave_api_key = (
            brave_api_key or os.environ.get("BRAVE_API_KEY", "")
        ).strip()
        self._image = image

    @property
    def harness_name(self) -> str:
        return "hermesagent"

    @property
    def docker_image(self) -> str:
        if self._image:
            return self._image
        return resolve_image(self.harness_name)

    @property
    def expects_gateway(self) -> bool:
        return False

    @property
    def transcript_container_path(self) -> str:
        return "/root/.openclaw/agents/main/sessions/chat.jsonl"

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        """Execute a LongHorizon task using the Hermes Agent harness.

        Flow:
          1. Start container with harness image (by harness name)
          2. Mount task inputs
          3. Configure Hermes (hermes.yaml, .env)
          4. Write bench runner config (model, prompt, API key)
          5. Run bench_runner.py via the Hermes venv
          6. Wait for completion or timeout
        """
        elapsed_time = float(spec.timeout_seconds)
        agent_proc = None

        try:
            # Build environment
            env = {
                "OPENROUTER_API_KEY": self.openrouter_api_key,
                "OPENROUTER_BASE_URL": self.openrouter_base_url,
                "BRAVE_API_KEY": self.brave_api_key,
                **spec.extra_env,
            }

            # Start container using harness-named image
            start_container(
                container_name=spec.task_id,
                docker_image=self.docker_image,
                inputs_path=spec.inputs_path,
                extra_env=env,
            )

            # Setup workspace and tests
            setup_workspace(spec.task_id)
            tests_dir = spec.task_dir / "tests"
            if tests_dir.is_dir():
                copy_tests_to_container(spec.task_id, tests_dir)

            # Configure Hermes
            self._configure_hermes(spec.task_id)

            # Build the full prompt
            system_prompt = (
                f"You are an expert agent in a restricted, non-interactive environment. "
                f"Solve the task efficiently before the timeout ({spec.timeout_seconds}s). "
                f"Run all processes in the foreground. Provide a complete solution with no placeholders. "
                f"Your output must be written to {WORKSPACE_DIR}/answer.json.\n\n"
            )
            full_prompt = system_prompt + spec.instruction

            # Write bench runner config
            self._write_bench_config(
                spec.task_id,
                full_prompt,
                spec.model,
                spec.thinking,
            )

            # Run bench runner
            start_time = time.perf_counter()
            agent_proc = run_background(
                spec.task_id,
                bash_cmd=(
                    f"cd {HERMES_INSTALL_DIR} && "
                    f"{HERMES_VENV_PYTHON} -c \""
                    f"import json; "
                    f"config = json.load(open('{BENCH_CONFIG_CONTAINER_PATH}')); "
                    f"from hermes_agent import Agent; "
                    f"agent = Agent("
                    f"  model=config['config']['model'], "
                    f"  api_key=config['config']['api_key'], "
                    f"  base_url=config['config']['base_url']"
                    f"); "
                    f"agent.run(config['prompt'])\""
                ),
                log_path=spec.output_dir / "agent.log",
            )

            logger.info("[%s] Waiting for hermes-agent to finish...", spec.task_id)
            try:
                agent_proc.wait(timeout=spec.timeout_seconds)
                elapsed_time = time.perf_counter() - start_time
                logger.info(
                    "[%s] hermes-agent finished, elapsed: %.2f seconds",
                    spec.task_id,
                    elapsed_time,
                )
            except subprocess.TimeoutExpired:
                logger.info("[%s] hermes-agent timed out", spec.task_id)
                elapsed_time = float(spec.timeout_seconds)
                agent_proc.kill()
                agent_proc.wait()

            if agent_proc:
                close_proc_log(agent_proc)

            return AgentExecution(
                elapsed_time=elapsed_time,
                error=None,
                gateway_proc=None,
                agent_proc=agent_proc,
            )

        except Exception as exc:
            if agent_proc is not None:
                close_proc_log(agent_proc)
            logger.error("[%s] hermes-agent execution error: %s", spec.task_id, exc)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error=str(exc),
                gateway_proc=None,
                agent_proc=agent_proc,
            )

    def collect_usage(
        self, task_id: str, output_dir: Path, elapsed_time: float
    ) -> dict[str, Any]:
        """Collect token usage from Hermes session logs."""
        usage: dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
            "elapsed_time": round(elapsed_time, 2),
        }
        output_dir.mkdir(parents=True, exist_ok=True)

        # Try to copy transcript
        transcript_host = output_dir / "chat.jsonl"
        ok = copy_file_from_container(
            task_id, self.transcript_container_path, transcript_host
        )
        if ok and transcript_host.exists():
            parsed = self._extract_usage_from_jsonl(transcript_host)
            usage.update(parsed)

        # Also extract from session logs as fallback
        if usage["request_count"] == 0:
            session_usage = self._extract_from_session_logs(task_id, output_dir)
            if session_usage["request_count"] > 0:
                usage.update(session_usage)

        # Copy session logs for archival
        hermes_log_dest = output_dir / "hermes_session"
        hermes_log_dest.mkdir(parents=True, exist_ok=True)
        copy_dir_from_container(task_id, f"{HERMES_HOME}/sessions", hermes_log_dest)

        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    def _configure_hermes(self, task_id: str) -> None:
        """Configure hermes-agent inside the container."""
        # Create necessary directories
        exec_in_container(
            task_id,
            f"mkdir -p {HERMES_HOME} {HERMES_HOME}/sessions "
            f"$(dirname {self.transcript_container_path})",
        )

        # Write hermes.yaml
        hermes_yaml = (
            "tools:\n"
            "  profile: coding\n"
            "  web:\n"
            "    search:\n"
            "      enabled: true\n"
            "      provider: brave\n"
        )
        exec_in_container(
            task_id,
            f"cat > {HERMES_HOME}/hermes.yaml <<'EOF'\n{hermes_yaml}EOF",
        )

        # Write .env
        hermes_env = (
            f"OPENROUTER_API_KEY={self.openrouter_api_key}\n"
            f"OPENROUTER_BASE_URL={self.openrouter_base_url}\n"
            f"BRAVE_API_KEY={self.brave_api_key}\n"
        )
        exec_in_container(
            task_id,
            f"cat > {HERMES_HOME}/.env <<'EOF'\n{hermes_env}EOF",
        )

        # Symlink workspace
        exec_in_container(
            task_id,
            f"ln -sfn {WORKSPACE_DIR} {HERMES_HOME}/workspace",
        )

        logger.info("[%s] hermes-agent configured", task_id)

    def _write_bench_config(
        self,
        task_id: str,
        prompt: str,
        model: str,
        thinking: str | None,
    ) -> None:
        """Write bench runner config JSON into the container."""
        reasoning_config = None
        if thinking:
            t = thinking.strip().lower()
            if t in ("off", "none", "disabled", "false"):
                reasoning_config = {"enabled": False}
            elif t in ("on", "enabled", "medium", "true"):
                reasoning_config = {"enabled": True, "effort": "medium"}
            elif t == "high":
                reasoning_config = {"enabled": True, "effort": "high"}
            elif t in ("low", "minimal"):
                reasoning_config = {"enabled": True, "effort": "low"}
            else:
                reasoning_config = {"enabled": True, "effort": t}

        config_payload = {
            "config": {
                "model": model,
                "api_key": self.openrouter_api_key,
                "base_url": self.openrouter_base_url,
                "max_iterations": 90,
                "reasoning_config": reasoning_config,
            },
            "prompt": prompt,
        }

        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config_payload, f, ensure_ascii=False)
            config_tmp = f.name

        try:
            copy_file_to_container(task_id, config_tmp, BENCH_CONFIG_CONTAINER_PATH)
        finally:
            Path(config_tmp).unlink(missing_ok=True)

    def _extract_from_session_logs(
        self, task_id: str, output_dir: Path
    ) -> dict[str, Any]:
        """Extract usage from Hermes session JSON files."""
        usage: dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }

        sessions_dir = output_dir / "hermes_session"
        if not sessions_dir.exists():
            return usage

        total_requests = 0
        for session_file in sorted(sessions_dir.glob("session_*.json")):
            try:
                payload = json.loads(session_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            messages = payload.get("messages", [])
            if isinstance(messages, list):
                total_requests += sum(
                    1 for m in messages
                    if isinstance(m, dict) and m.get("role") == "assistant"
                )

        usage["request_count"] = total_requests
        return usage

    @staticmethod
    def _extract_usage_from_jsonl(jsonl_path: Path) -> dict[str, Any]:
        """Extract usage from OpenClaw-compatible JSONL transcript."""
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
