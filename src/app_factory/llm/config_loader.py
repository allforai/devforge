"""Load LLM configuration from llm.yaml."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# PyYAML is optional — fallback to manual parsing if not available
try:
    import yaml  # type: ignore
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


_DEFAULT_CONFIG_PATHS = [
    "llm.yaml",
    "llm.yml",
    ".llm.yaml",
]


def _find_config_file(search_dir: str | Path | None = None) -> Path | None:
    """Search for llm.yaml in the given directory or cwd."""
    base = Path(search_dir) if search_dir else Path.cwd()
    for name in _DEFAULT_CONFIG_PATHS:
        path = base / name
        if path.is_file():
            return path
    return None


def _parse_yaml_simple(text: str) -> dict[str, Any]:
    """Minimal YAML-subset parser for flat/nested dicts (no PyYAML needed)."""
    result: dict[str, Any] = {}
    current_section: str | None = None
    current_sub: str | None = None
    section_indent: int = 0
    sub_indent: int = 0

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if ":" not in stripped:
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if value and "#" in value:
            value = value[:value.index("#")].strip()

        if indent == 0:
            current_section = None
            current_sub = None
            if value:
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                else:
                    result[key] = value
            else:
                current_section = key
                result[key] = {}
        elif current_section and indent > 0:
            # If indent drops back to section level, reset sub
            if current_sub and indent <= sub_indent:
                current_sub = None

            if current_sub is None:
                if value:
                    result[current_section][key] = value
                else:
                    current_sub = key
                    sub_indent = indent
                    result[current_section][key] = {}
            else:
                section = result[current_section]
                if isinstance(section, dict) and current_sub in section:
                    section[current_sub][key] = value

    return result


def load_llm_config(
    config_path: str | Path | None = None,
    search_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Load LLM config from file, returning a preferences dict.

    Resolution order:
    1. Explicit config_path
    2. Search for llm.yaml in search_dir or cwd
    3. Return empty dict (mock mode)
    """
    path: Path | None = None
    if config_path:
        path = Path(config_path)
    else:
        path = _find_config_file(search_dir)

    if path is None or not path.is_file():
        return {}

    text = path.read_text(encoding="utf-8")

    if _HAS_YAML:
        raw = yaml.safe_load(text) or {}
    else:
        raw = _parse_yaml_simple(text)

    return _normalize_config(raw)


def _normalize_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert raw YAML structure into the preferences dict the router expects."""
    prefs: dict[str, Any] = {}

    if "allow_live" in raw:
        prefs["allow_live"] = bool(raw["allow_live"])
    if "provider" in raw:
        prefs["provider"] = str(raw["provider"])
    if "model" in raw:
        prefs["model"] = str(raw["model"])
    if "api_key" in raw:
        prefs["api_key"] = str(raw["api_key"])

    # Per-task overrides
    tasks = raw.get("tasks", {})
    if isinstance(tasks, dict):
        for task_name, task_config in tasks.items():
            if isinstance(task_config, dict):
                if "model" in task_config:
                    prefs[f"{task_name}_model"] = task_config["model"]
                if "provider" in task_config:
                    prefs[f"{task_name}_provider"] = task_config["provider"]
                if "api_key" in task_config:
                    prefs[f"{task_name}_api_key"] = task_config["api_key"]
            elif isinstance(task_config, str):
                prefs[f"{task_name}_model"] = task_config

    return prefs
