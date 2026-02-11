"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from pathlib import Path

import toml


def get_version_from_pyproject(base_dir: str | Path | None = None) -> str:
    """Read the version from pyproject.toml."""
    if base_dir is None:
        base_dir = Path.cwd()
    pyproject_path = Path(base_dir) / "pyproject.toml"
    if pyproject_path.exists():
        data = toml.load(pyproject_path)
        return str(data.get("project", {}).get("version", data.get("tool", {}).get("poetry", {}).get("version", "unknown")))
    return "unknown"
