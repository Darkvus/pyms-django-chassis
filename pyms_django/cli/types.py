"""Shared data types for the pyms-django CLI."""

from __future__ import annotations

from typing import TypedDict


class ProjectConfig(TypedDict):
    """Configuration collected from the user for project generation."""

    package_manager: str  # "uv" | "poetry"
    service_name: str
    base_path: str
    python_version: str  # "3.11" | "3.12" | "3.13"
    django_version: str  # pip constraint e.g. ">=4.2,<5.0"
    multitenant: bool
    extras: list[str]
    module_name: str
    actor: str  # "" if not specified
