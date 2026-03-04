"""Service version resolution utilities for pyms-django-chassis."""
from __future__ import annotations

from pathlib import Path

import toml


def get_version_from_pyproject(base_dir: str | Path | None = None) -> str:
    """Read the project version from ``pyproject.toml``.

    Searches under ``project.version`` (PEP 621) and falls back to
    ``tool.poetry.version`` for Poetry-managed projects.

    Args:
        base_dir: Directory containing ``pyproject.toml``. Defaults to the
            current working directory.

    Returns:
        Version string, or ``"unknown"`` if ``pyproject.toml`` is absent or
        contains no version field.
    """
    if base_dir is None:
        base_dir = Path.cwd()
    pyproject_path = Path(base_dir) / "pyproject.toml"
    if pyproject_path.exists():
        data = toml.load(pyproject_path)
        poetry_version = data.get("tool", {}).get("poetry", {}).get("version", "unknown")  # type: ignore[union-attr]
        return str(data.get("project", {}).get("version", poetry_version))  # type: ignore[union-attr]
    return "unknown"
