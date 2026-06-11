"""Codex (OpenAI) agent runner for LongHorizon.

Deploys the Codex harness framework inside a docker container and
executes tasks through its CLI-based exec protocol.

Docker image is resolved by harness name: `longhorizon-codex:v1`
(not per-task like Terminal_Bench's `tb2-{task_id}:v3`).
"""

from __future__ import annotations

import json
import logging
import os
import shlex
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
    copy_tests_to_container,
    exec_in_container,
    remove_container,
    run_background,
    setup_workspace,
    start_container,
)

logger = logging.getLogger(__name__)

CODEX_HOME = "/root/.codex"
CODEX_SESSIONS_DIR = f"{CODEX_HOME}/sessions"
CODEX_CONFIG_PATH = f"{CODEX_HOME}/config.toml"
CODEX_PROMPT_PATH = "/tmp/codex_prompt.txt"


class CodexAgent(BaseAgent):
    """Codex (OpenAI) harness agent for LongHorizon evaluation.

    Deploys the Codex CLI agent framework inside a harness-named container.
    The docker image is pulled by harness name, not task name.
    """

    def __init__(
        self,
        openrouter_api_key: str = "",
        openrouter_base_url: str = "",
        image: str | None = None,
        reasoning_effort: str = "medium",
    ) -> None:
        self.openrouter_api_key = (
            openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        ).strip()
        self.openrouter_base_url = (
            openrouter_base_url
            or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        ).strip()
        self._image = image
        self.reasoning_effort = reasoning_effort

    @property
    def harness_name(self) -> str:
        return "codex"

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
        return CODEX_SESSIONS_DIR

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        """Execute a LongHorizon task using the Codex harness.

        Flow:
          1. Start container with harness image (by harness name)
          2. Mount task inputs
          3. Write Codex config (model, provider)
          4. Prepare prompt file
          5. Run `codex exec` with the task instruction
          6. Wait for completion or timeout
        """
        elapsed_time = float(spec.timeout_seconds)
        start_time = time.perf_counter()

        try:
            # Build environment
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

            # Setup workspace and tests
            setup_workspace(spec.task_id)
            tests_dir = spec.task_dir / "tests"
            if tests_dir.is_dir():
                copy_tests_to_container(spec.task_id, tests_dir)

            # Initialize Codex directories and config
            self._prepare_codex_environment(spec.task_id, spec.model)

            # Build the full prompt
            system_prompt = (
                f"You are an expert agent in a restricted, non-interactive environment. "
                f"Solve the task efficiently before the timeout ({spec.timeout_seconds}s). "
                f"Run all processes in the foreground. Provide a complete solution with no placeholders. "
                f"Your output must be written to {WORKSPACE_DIR}/answer.json.\n\n"
            )
            full_prompt = system_prompt + spec.instruction

            # Write prompt to container
            self._write_prompt(spec.task_id, full_prompt)

            # Run Codex
            self._run_codex(
                spec.task_id,
                spec.model,
                spec.timeout_seconds,
                spec.output_dir,
            )
            elapsed_time = time.perf_counter() - start_time

            return AgentExecution(
                elapsed_time=elapsed_time,
                error=None,
                gateway_proc=None,
                agent_proc=None,
            )

        except subprocess.TimeoutExpired:
            logger.info("[%s] Codex timed out", spec.task_id)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error="Codex run timed out",
                gateway_proc=None,
                agent_proc=None,
            )
        except Exception as exc:
            logger.error("[%s] Codex execution error: %s", spec.task_id, exc)
            return AgentExecution(
                elapsed_time=time.perf_counter() - start_time,
                error=str(exc),
                gateway_proc=None,
                agent_proc=None,
            )

    def collect_usage(
        self, task_id: str, output_dir: Path, elapsed_time: float
    ) -> dict[str, Any]:
        """Collect token usage from Codex session logs."""
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

        # Copy session logs
        sessions_dest = output_dir / "codex_sessions"
        sessions_dest.mkdir(parents=True, exist_ok=True)
        copy_dir_from_container(task_id, f"{CODEX_SESSIONS_DIR}", sessions_dest)

        # Find and parse the latest session file
        latest = self._find_latest_session(task_id)
        if latest:
            chat_dest = output_dir / "chat.jsonl"
            copy_file_from_container(
                task_id, f"{CODEX_SESSIONS_DIR}/{latest}", chat_dest
            )
            if chat_dest.exists():
                parsed = self._extract_usage_from_jsonl(chat_dest)
                usage.update(parsed)

        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    def _prepare_codex_environment(self, task_id: str, model: str) -> None:
        """Create Codex config directories and write config.toml."""
        # Create directories
        exec_in_container(
            task_id,
            f"mkdir -p {CODEX_HOME} {CODEX_SESSIONS_DIR}",
        )

        # Normalize model name (strip openrouter/ prefix)
        bare_model = model.split("/", 1)[1] if model.startswith("openrouter/") else model

        # Write config.toml
        reasoning_line = (
            f'model_reasoning_effort = "{self.reasoning_effort}"\n'
            if self.reasoning_effort
            else ""
        )
        config_toml = (
            f'model_provider = "openrouter"\n'
            f'{reasoning_line}'
            f'model = "{bare_model}"\n'
            f'approval_policy = "never"\n'
            f'sandbox_mode = "danger-full-access"\n'
            f'\n'
            f'[model_providers.openrouter]\n'
            f'name = "openrouter"\n'
            f'base_url = "{self.openrouter_base_url}"\n'
            f'env_key = "OPENROUTER_API_KEY"\n'
        )

        exec_in_container(
            task_id,
            f"cat > {CODEX_CONFIG_PATH} <<'EOF'\n{config_toml}EOF",
        )
        logger.info("[%s] Codex config written (model=%s)", task_id, bare_model)

    def _write_prompt(self, task_id: str, prompt: str) -> None:
        """Write the prompt to a file inside the container."""
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
            f.write(prompt)
            tmp_path = f.name

        try:
            from src.agent.utils.docker_utils import copy_file_to_container
            copy_file_to_container(task_id, tmp_path, CODEX_PROMPT_PATH)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def _run_codex(
        self,
        task_id: str,
        model: str,
        timeout_seconds: int,
        output_dir: Path,
    ) -> None:
        """Run `codex exec` with the prompt file."""
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = (
            f"cd {WORKSPACE_DIR} && "
            f"cat {CODEX_PROMPT_PATH} | "
            f"codex exec --skip-git-repo-check --cd {WORKSPACE_DIR} -"
        )

        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        # Write agent log
        (output_dir / "agent.log").write_text(
            (r.stdout or "") + ("\n" if r.stdout else "") + (r.stderr or ""),
            encoding="utf-8",
        )

        if r.returncode != 0:
            raise RuntimeError(
                f"Codex run failed (rc={r.returncode}):\n{r.stderr}"
            )

    def _find_latest_session(self, task_id: str) -> str | None:
        """Find the most recent session file in the container."""
        r = exec_in_container(
            task_id,
            f"find {CODEX_SESSIONS_DIR} -type f -name '*.jsonl' "
            f"-printf '%T@ %P\\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-",
        )
        name = (r.stdout or "").strip().splitlines()[0] if r.stdout else ""
        return name or None

    @staticmethod
    def _extract_usage_from_jsonl(jsonl_path: Path) -> dict[str, Any]:
        """Extract usage from Codex JSONL session file."""
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

        assistant_count = 0
        for line in jsonl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Count assistant messages for request_count
            payload = entry.get("payload") or entry.get("item") or entry
            if isinstance(payload, dict):
                if payload.get("role") == "assistant" or (
                    payload.get("type") == "message" and payload.get("role") == "assistant"
                ):
                    assistant_count += 1

            # Look for usage info
            usage = None
            for key in ("usage", "token_usage", "tokenUsage"):
                if key in entry and isinstance(entry[key], dict):
                    usage = entry[key]
                    break
                if isinstance(payload, dict) and key in payload and isinstance(payload[key], dict):
                    usage = payload[key]
                    break

            if usage:
                totals["input_tokens"] += int(usage.get("input_tokens", usage.get("inputTokens", 0)) or 0)
                totals["output_tokens"] += int(usage.get("output_tokens", usage.get("outputTokens", 0)) or 0)
                totals["cache_read_tokens"] += int(usage.get("cached_input_tokens", usage.get("cacheRead", 0)) or 0)
                totals["total_tokens"] += int(usage.get("total_tokens", usage.get("totalTokens", 0)) or 0)

        totals["request_count"] = assistant_count
        if totals["total_tokens"] == 0:
            totals["total_tokens"] = (
                totals["input_tokens"] + totals["output_tokens"]
                + totals["cache_read_tokens"] + totals["cache_write_tokens"]
            )
        totals["cost_usd"] = round(totals["cost_usd"], 6)
        return totals
