"""Harness Registry for LongHorizon.

Maps harness names to their docker images. Unlike Terminal_Bench which uses
per-task images (e.g., `ziheliu/tb2-{task_id}:v3`), LongHorizon uses
per-harness images (e.g., `longhorizon-openclaw:v1`).

This design follows WildClawBench's approach where each harness is a mature
agent framework deployed as a pre-built docker image.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HarnessConfig:
    """Configuration for a single harness."""

    name: str
    default_image: str
    env_override_key: str
    description: str = ""


# Registry of all supported harnesses
# Docker images are named by harness, not by task.
_HARNESS_REGISTRY: dict[str, HarnessConfig] = {
    "openclaw": HarnessConfig(
        name="openclaw",
        # NOTE: image names should follow convention: "<user>/<repo>:<tag>"
        # Always pin a concrete tag, not "latest".
        default_image="plkzzwzhang/wildclawbench-ubuntu:openclaw2026.5.28",
        env_override_key="LONGHORIZON_OPENCLAW_IMAGE",
        description="OpenClaw agent framework - general-purpose coding/reasoning agent",
    ),
    "claudecode": HarnessConfig(
        name="claudecode",
        default_image="hanslerli/lhb-claudecode:v1",
        env_override_key="LONGHORIZON_CLAUDECODE_IMAGE",
        description="Claude Code agent framework - Anthropic's coding agent",
    ),
    "codex": HarnessConfig(
        name="codex",
        default_image="hanslerli/lhb-codex:v1",
        env_override_key="LONGHORIZON_CODEX_IMAGE",
        description="OpenAI Codex agent framework",
    ),
    "hermesagent": HarnessConfig(
        name="hermesagent",
        default_image="hanslerli/lhb-hermes:v1",
        env_override_key="LONGHORIZON_HERMES_IMAGE",
        description="Hermes Agent framework - open-source coding agent",
    ),
}


def resolve_image(harness_name: str) -> str:
    """Resolve docker image name from harness name.

    Resolution order:
      1. Environment variable specific to the harness (e.g., LONGHORIZON_OPENCLAW_IMAGE)
      2. Global LONGHORIZON_DOCKER_IMAGE environment variable
      3. Default image from the registry

    This is analogous to WildClawBench's _resolve_image_from_env() pattern,
    but the key difference is the naming: images are identified by harness
    (not by task), so one image can serve all tasks for that harness.

    Args:
        harness_name: The harness identifier (e.g., "openclaw", "claudecode")

    Returns:
        The resolved docker image name (e.g., "longhorizon-openclaw:v1")

    Raises:
        ValueError: If the harness name is not registered.
    """
    config = _HARNESS_REGISTRY.get(harness_name)
    if config is None:
        available = ", ".join(sorted(_HARNESS_REGISTRY.keys()))
        raise ValueError(
            f"Unknown harness '{harness_name}'. Available: {available}"
        )

    # Priority 1: harness-specific env var
    env_image = os.environ.get(config.env_override_key, "").strip()
    if env_image:
        logger.info(
            "Harness '%s' image resolved from %s=%s",
            harness_name,
            config.env_override_key,
            env_image,
        )
        return env_image

    # Priority 2: global override
    global_image = os.environ.get("LONGHORIZON_DOCKER_IMAGE", "").strip()
    if global_image:
        logger.info(
            "Harness '%s' image resolved from LONGHORIZON_DOCKER_IMAGE=%s",
            harness_name,
            global_image,
        )
        return global_image

    # Priority 3: default from registry
    logger.info(
        "Harness '%s' using default image: %s",
        harness_name,
        config.default_image,
    )
    return config.default_image


def get_harness_config(harness_name: str) -> HarnessConfig:
    """Get the full harness configuration.

    Args:
        harness_name: The harness identifier.

    Returns:
        HarnessConfig dataclass with all harness metadata.

    Raises:
        ValueError: If the harness name is not registered.
    """
    config = _HARNESS_REGISTRY.get(harness_name)
    if config is None:
        available = ", ".join(sorted(_HARNESS_REGISTRY.keys()))
        raise ValueError(
            f"Unknown harness '{harness_name}'. Available: {available}"
        )
    return config


def list_harnesses() -> list[str]:
    """Return all registered harness names."""
    return sorted(_HARNESS_REGISTRY.keys())


def register_harness(config: HarnessConfig) -> None:
    """Register a new harness configuration.

    Allows extending the harness registry at runtime for custom frameworks.
    """
    _HARNESS_REGISTRY[config.name] = config
    logger.info("Registered harness: %s (image=%s)", config.name, config.default_image)
