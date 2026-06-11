"""Container lifecycle management for LongHorizon.

Supports Docker backend for container management.

Key design difference from Terminal_Bench:
  - Terminal_Bench: docker_image = f"ziheliu/tb2-{task_id}:v3" (per-task)
  - LongHorizon:   docker_image = resolve_image(harness_name) (per-harness)

Usage:
  # Docker mode - for local testing with API keys like Minimax
  python -m src.agent --task HQ-01_neurips_to_acl --harness openclaw
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Default container workspace path
WORKSPACE_DIR = os.environ.get("LONGHORIZON_WORKSPACE_DIR", "/workspace")


# ============================================================================
# Public API
# ============================================================================


def start_container(
    container_name: str,
    docker_image: str,
    inputs_path: Path,
    *,
    extra_env: dict[str, str] | None = None,
    extra_volumes: dict[str, str] | None = None,
) -> str:
    """Start a container for task execution.

    Args:
        container_name: Unique identifier for this container.
        docker_image: Image name (resolved from harness name).
        inputs_path: Host path to input files.
        extra_env: Environment variables to inject.
        extra_volumes: Additional volume mounts.

    Returns:
        Container identifier.
    """
    return _docker_start_container(
        container_name, docker_image, inputs_path,
        extra_env=extra_env, extra_volumes=extra_volumes,
    )


def setup_workspace(container_name: str) -> None:
    """Initialize the writable workspace inside the container."""
    subprocess.run(
        ["docker", "exec", container_name, "/bin/bash", "-c",
         f"chmod -R u+w {WORKSPACE_DIR} 2>/dev/null || true"],
        capture_output=True, text=True,
    )
    logger.info("[%s] Workspace initialized at %s", container_name, WORKSPACE_DIR)


def copy_tests_to_container(container_name: str, tests_dir: Path) -> None:
    """Copy the test directory into the container for grading."""
    if not tests_dir.is_dir():
        logger.warning("[%s] Tests directory not found: %s", container_name, tests_dir)
        return

    subprocess.run(
        ["docker", "exec", container_name, "mkdir", "-p", f"{WORKSPACE_DIR}/tests"],
        capture_output=True, text=True,
    )
    r = subprocess.run(
        ["docker", "cp", f"{tests_dir}/.", f"{container_name}:{WORKSPACE_DIR}/tests/"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.error("[%s] Failed to copy tests: %s", container_name, r.stderr)
        return

    logger.info("[%s] Tests copied to %s/tests/", container_name, WORKSPACE_DIR)


def copy_file_to_container(
    container_name: str, host_path: str | Path, container_path: str
) -> bool:
    """Copy a file from host into the container."""
    r = subprocess.run(
        ["docker", "cp", str(host_path), f"{container_name}:{container_path}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning("[%s] File copy failed (%s → %s): %s",
                       container_name, host_path, container_path, r.stderr.strip())
        return False
    return True


def copy_file_from_container(
    container_name: str, container_path: str, host_path: str | Path
) -> bool:
    """Copy a file from the container to the host."""
    Path(str(host_path)).parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["docker", "cp", f"{container_name}:{container_path}", str(host_path)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning("[%s] File copy from container failed (%s → %s): %s",
                       container_name, container_path, host_path, r.stderr.strip())
        return False
    return True


def copy_dir_from_container(
    container_name: str, container_path: str, host_path: str | Path
) -> bool:
    """Copy a directory from container to host."""
    host_path = Path(str(host_path))
    host_path.mkdir(parents=True, exist_ok=True)

    r = subprocess.run(
        ["docker", "cp", f"{container_name}:{container_path}/.", str(host_path)],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        logger.info("[%s] Collected %s → %s", container_name, container_path, host_path)
        return True
    return False


def exec_in_container(
    container_name: str,
    command: str,
    *,
    timeout: int = 3600,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Execute a command inside the container."""
    env_args: list[str] = []
    for key, value in (env or {}).items():
        env_args += ["-e", f"{key}={value}"]
    return subprocess.run(
        ["docker", "exec", *env_args, container_name, "/bin/bash", "-c", command],
        capture_output=True, text=True, timeout=timeout,
    )


def collect_task_output(container_name: str, output_dir: Path) -> None:
    """Collect output files from the container workspace."""
    task_output_dir = output_dir / "task_output"
    task_output_dir.mkdir(parents=True, exist_ok=True)

    # Collect answer.json
    copy_file_from_container(
        container_name, f"{WORKSPACE_DIR}/answer.json", task_output_dir / "answer.json",
    )

    # Copy the whole workspace
    workspace_out = task_output_dir / "workspace"
    workspace_out.mkdir(parents=True, exist_ok=True)
    copy_dir_from_container(container_name, WORKSPACE_DIR, workspace_out)


def remove_container(container_name: str) -> None:
    """Destroy the container."""
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True, text=True)
    logger.info("[%s] Container removed", container_name)


def run_background(
    container_name: str,
    bash_cmd: str,
    log_path: Path,
) -> subprocess.Popen[str]:
    """Start a background process inside the container.

    Returns:
        subprocess.Popen
    """
    return _docker_run_background(container_name, bash_cmd, log_path)


def close_proc_log(proc) -> None:
    """Close the log file handle (if any)."""
    log_file = getattr(proc, "_log_file", None)
    if log_file and not log_file.closed:
        log_file.close()


# ============================================================================
# Docker Backend Implementation (local docker)
# ============================================================================


def _docker_start_container(
    container_name: str,
    docker_image: str,
    inputs_path: Path,
    *,
    extra_env: dict[str, str] | None = None,
    extra_volumes: dict[str, str] | None = None,
) -> str:
    """Start a local docker container."""
    if not inputs_path.is_dir():
        raise RuntimeError(f"Inputs path does not exist or is not a directory: {inputs_path}")

    # NOTE: Do NOT inject proxy env vars into the container.
    # Some images have broken proxy settings baked in that block API access.
    # We explicitly UNSET proxy vars to ensure clean network connectivity.
    env_args: list[str] = [
        "-e", "http_proxy=",
        "-e", "https_proxy=",
        "-e", "HTTP_PROXY=",
        "-e", "HTTPS_PROXY=",
        "-e", "no_proxy=",
    ]

    for key, value in (extra_env or {}).items():
        if value:
            env_args += ["-e", f"{key}={value}"]
            masked = (value[:4] + "***") if len(value) > 4 else value
            logger.info("[%s] Injecting env: %s=%s", container_name, key, masked)

    volume_args: list[str] = ["-v", f"{inputs_path}:{WORKSPACE_DIR}/inputs:ro"]
    for host_path, container_path in (extra_volumes or {}).items():
        volume_args += ["-v", f"{host_path}:{container_path}"]

    cmd = [
        "docker", "run", "-d", "--name", container_name,
        *env_args, *volume_args,
        docker_image, "/bin/bash", "-c", "tail -f /dev/null",
    ]

    logger.info("[%s] Starting docker container (image=%s)", container_name, docker_image)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Docker container startup failed:\n{r.stderr}")

    container_id = r.stdout.strip()[:12]
    logger.info("[%s] Docker container started: %s", container_name, container_id)
    return container_id


def _docker_run_background(
    container_name: str,
    bash_cmd: str,
    log_path: Path,
) -> subprocess.Popen[str]:
    """Start a background process via docker exec."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        ["docker", "exec", container_name, "/bin/bash", "-c",
         f"cd {WORKSPACE_DIR} && {bash_cmd}"],
        stdout=log_file, stderr=subprocess.STDOUT, encoding="utf-8",
    )
    proc._log_file = log_file  # type: ignore[attr-defined]
    logger.info("[%s] Started docker background PID=%s → %s", container_name, proc.pid, log_path)
    return proc
