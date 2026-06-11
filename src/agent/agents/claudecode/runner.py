"""Claude Code agent runner for LongHorizon.

Deploys the Claude Code harness framework inside a docker container and
executes tasks through its CLI-based protocol.

Docker image is resolved by harness name: `longhorizon-claudecode:v1`
(not per-task like Terminal_Bench's `tb2-{task_id}:v3`).
"""

from __future__ import annotations

import json
import logging
import os
import shlex
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
    copy_dir_from_container,
    copy_file_from_container,
    copy_tests_to_container,
    exec_in_container,
    remove_container,
    setup_workspace,
    start_container,
)

logger = logging.getLogger(__name__)


class ClaudeCodeAgent(BaseAgent):
    """Claude Code harness agent for LongHorizon evaluation.

    Deploys Claude Code (Anthropic's coding agent) as a mature framework
    inside a harness-named container. The docker image is pulled by
    harness name, not task name.
    """

    def __init__(
        self,
        anthropic_api_key: str = "",
        anthropic_base_url: str = "",
        image: str | None = None,
    ) -> None:
        self.api_key = (
            anthropic_api_key.strip()
            or os.environ.get("ANTHROPIC_API_KEY", "")
            or os.environ.get("OPENROUTER_API_KEY", "")
        )
        self.api_base_url = (
            anthropic_base_url.strip()
            or os.environ.get("ANTHROPIC_BASE_URL", "")
            or os.environ.get("OPENROUTER_BASE_URL", "")
        )
        self._image = image

    @property
    def harness_name(self) -> str:
        return "claudecode"

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
        return "/claude_code/log/chat.json"

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        """Execute a LongHorizon task using the Claude Code harness.

        Flow:
          1. Start container with harness image (by harness name, not task name)
          2. Mount task inputs into /workspace/inputs
          3. Setup workspace and copy tests
          4. Run Claude Code with the task instruction
          5. Wait for completion or timeout
        """
        elapsed_time = float(spec.timeout_seconds)
        start_time = time.perf_counter()

        try:
            # Build environment for the container
            env = {
                "ANTHROPIC_API_KEY": self.api_key,
                "ANTHROPIC_BASE_URL": self.api_base_url,
                "OPENROUTER_API_KEY": self.api_key,
                "OPENROUTER_BASE_URL": self.api_base_url,
                "DISABLE_PROMPT_CACHING": os.environ.get("DISABLE_PROMPT_CACHING", "1"),
                "IS_SANDBOX": "1",
                "CLAUDE_CODE_FULL_LOG_PATH": "./log",
                **spec.extra_env,
            }

            # Start container using harness-named image
            start_container(
                container_name=spec.task_id,
                docker_image=self.docker_image,
                inputs_path=spec.inputs_path,
                extra_env=env,
            )

            # Setup workspace and copy test files
            setup_workspace(spec.task_id)
            tests_dir = spec.task_dir / "tests"
            if tests_dir.is_dir():
                copy_tests_to_container(spec.task_id, tests_dir)

            # Build the full prompt
            system_prompt = (
                f"You are an expert agent in a restricted, non-interactive environment. "
                f"Solve the task efficiently before the timeout ({spec.timeout_seconds}s). "
                f"Run all processes in the foreground. Provide a complete solution with no placeholders. "
                f"Your output must be written to {WORKSPACE_DIR}/answer.json.\n\n"
            )
            full_prompt = system_prompt + spec.instruction

            # Run Claude Code
            self._run_prompt(
                spec.task_id,
                full_prompt,
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
            logger.info("[%s] ClaudeCode timed out", spec.task_id)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error="ClaudeCode run timed out",
                gateway_proc=None,
                agent_proc=None,
            )
        except Exception as exc:
            logger.error("[%s] ClaudeCode execution error: %s", spec.task_id, exc)
            return AgentExecution(
                elapsed_time=time.perf_counter() - start_time,
                error=str(exc),
                gateway_proc=None,
                agent_proc=None,
            )

    def collect_usage(
        self, task_id: str, output_dir: Path, elapsed_time: float
    ) -> dict[str, Any]:
        """Collect token usage from Claude Code logs."""
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

        # Copy Claude Code logs
        log_dest = output_dir / "claude_code_log"
        log_dest.mkdir(parents=True, exist_ok=True)
        copy_file_from_container(
            task_id, "/claude_code/log/usage.json", log_dest / "usage.json"
        )
        copy_file_from_container(
            task_id, "/claude_code/log/chat.json", log_dest / "chat.json"
        )
        copy_dir_from_container(task_id, "/claude_code/log", log_dest)

        # Extract usage from chat.json
        parsed = self._extract_usage_from_chat_json(log_dest / "chat.json")
        if parsed["request_count"] > 0:
            usage.update(parsed)

        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    def _run_prompt(
        self,
        task_id: str,
        prompt: str,
        model: str,
        timeout_seconds: int,
        output_dir: Path,
    ) -> None:
        """Run Claude Code with the given prompt."""
        output_dir.mkdir(parents=True, exist_ok=True)
        cmd = (
            f"cd /claude_code && "
            f"IS_SANDBOX=1 ./start.sh "
            f"--add-dir {WORKSPACE_DIR} "
            f"-p {shlex.quote(prompt)} "
            f"--model {shlex.quote(model)}"
        )
        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        (output_dir / "agent.log").write_text(
            (r.stdout or "") + ("\n" if r.stdout else "") + (r.stderr or ""),
            encoding="utf-8",
        )
        if r.returncode != 0:
            raise RuntimeError(
                f"ClaudeCode run failed (rc={r.returncode}):\n{r.stderr}"
            )

    @staticmethod
    def _extract_usage_from_chat_json(chat_path: Path) -> dict[str, Any]:
        """Extract usage statistics from Claude Code chat.json transcript."""
        totals: dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }
        if not chat_path.exists():
            return totals

        try:
            content = chat_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return totals

        payloads: list[Any] = []
        try:
            parsed = json.loads(content)
            payloads = parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("{"):
                    try:
                        payloads.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        for payload in payloads:
            ClaudeCodeAgent._accumulate_usage(payload, totals)

        totals["total_tokens"] = (
            totals["input_tokens"]
            + totals["output_tokens"]
            + totals["cache_read_tokens"]
            + totals["cache_write_tokens"]
        )
        totals["cost_usd"] = round(totals["cost_usd"], 6)
        return totals

    @staticmethod
    def _accumulate_usage(payload: Any, totals: dict[str, Any]) -> None:
        """Recursively accumulate usage data from a payload."""
        if isinstance(payload, list):
            for item in payload:
                ClaudeCodeAgent._accumulate_usage(item, totals)
            return
        if not isinstance(payload, dict):
            return

        # Check if this dict contains usage info
        if "input_tokens" in payload and "output_tokens" in payload:
            input_tokens = int(payload.get("input_tokens") or 0)
            output_tokens = int(payload.get("output_tokens") or 0)
            cache_read = int(payload.get("cache_read_input_tokens") or 0)
            cache_write = int(payload.get("cache_creation_input_tokens") or 0)

            if input_tokens == 0 and output_tokens == 0 and cache_read == 0 and cache_write == 0:
                return

            totals["input_tokens"] += input_tokens
            totals["output_tokens"] += output_tokens
            totals["cache_read_tokens"] += cache_read
            totals["cache_write_tokens"] += cache_write
            totals["request_count"] += 1

            # Try to extract cost
            cost_details = payload.get("cost_details")
            if isinstance(cost_details, dict):
                totals["cost_usd"] += float(
                    cost_details.get("upstream_inference_cost", 0) or 0
                )
            elif "cost" in payload:
                totals["cost_usd"] += float(payload.get("cost", 0) or 0)
            return

        # Recurse into nested dicts
        for value in payload.values():
            ClaudeCodeAgent._accumulate_usage(value, totals)
