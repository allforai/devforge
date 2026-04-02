"""Workspace onboarding filesystem helpers."""

from __future__ import annotations

from pathlib import Path
def read_readme_excerpt(root: Path) -> str:
    """Read a short README excerpt when available."""
    for name in ("README.md", "README", "readme.md"):
        path = root / name
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            return text[:400]
    return ""
