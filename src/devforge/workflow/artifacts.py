"""exit_artifacts existence and size checking for the workflow engine."""

from __future__ import annotations

from pathlib import Path


def check_artifacts(root: Path, paths: list[str]) -> bool:
    """Return True iff every path in paths exists relative to root and has size > 0."""
    return all(
        (root / p).exists() and (root / p).stat().st_size > 0
        for p in paths
    )
