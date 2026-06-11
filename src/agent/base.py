"""Base agent interface for LongHorizon evaluation.

Adapted from WildClawBench's BaseAgent pattern. Each harness (OpenClaw,
ClaudeCode, etc.) implements this interface to provide a uniform execution
and grading protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
from typing import Any


@dataclass(frozen=True)
class AgentTaskSpec:
    """Specification for a single task execution."""

    task_id: str
    task_dir: Path
    instruction: str
    inputs_path: Path
    timeout_seconds: int
    output_dir: Path
    model: str
    harness: str
    difficulty: int = 1
    tags: list[str] = field(default_factory=list)
    thinking: str | None = None
    extra_env: dict[str, str] = field(default_factory=dict)


@dataclass
class AgentExecution:
    """Result of a single agent execution."""

    elapsed_time: float
    error: str | None = None
    agent_proc: subprocess.Popen[str] | None = None
    gateway_proc: subprocess.Popen[str] | None = None


class BaseAgent(ABC):
    """Abstract base class for all LongHorizon agent harnesses.

    Key difference from Terminal_Bench:
      - Terminal_Bench pulls docker images by task name: `tb2-{task_id}:v3`
      - LongHorizon pulls docker images by harness name: `longhorizon-{harness}:v1`

    This allows one docker image to serve multiple tasks, reducing storage
    overhead and simplifying image management.
    """

    @property
    @abstractmethod
    def harness_name(self) -> str:
        """Return the harness identifier used for docker image resolution."""

    @property
    @abstractmethod
    def docker_image(self) -> str:
        """Return the full docker image name (resolved from harness name)."""

    @property
    @abstractmethod
    def expects_gateway(self) -> bool:
        """Whether this harness starts a long-running gateway process."""

    @property
    @abstractmethod
    def transcript_container_path(self) -> str:
        """Path to the chat transcript inside the container."""

    @abstractmethod
    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        """Execute a task and return process handles, timing and error state."""

    @abstractmethod
    def collect_usage(
        self, task_id: str, output_dir: Path, elapsed_time: float
    ) -> dict[str, Any]:
        """Collect token usage and cost for one task."""

    def prepare_grading_transcript(self, task_id: str) -> str:
        """Prepare and return the transcript path used for grading.

        Default implementation returns the raw transcript path.
        Subclasses may override to convert transcripts into a normalized format.
        """
        _ = task_id
        return self.transcript_container_path
