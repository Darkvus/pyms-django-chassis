"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandParser


def run_folderddd(module: str, actor: str | None = None) -> None:
    """Generate DDD folder structure for a module."""
    if actor:
        base_path = Path("apps") / actor / module
    else:
        base_path = Path("apps") / module

    # Define the DDD directory structure
    directories: list[Path] = [
        base_path / "api" / "v1",
        base_path / "application" / "services",
        base_path / "application" / "use_cases",
        base_path / "domain",
        base_path / "infrastructure" / "services",
        base_path / "infrastructure" / "repositories",
    ]

    # Create all directories
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # Define files to create with their content
    files: dict[Path, str] = {
        # API layer
        base_path / "api" / "__init__.py": "",
        base_path / "api" / "v1" / "__init__.py": "",
        base_path / "api" / "v1" / "serializers.py": f'"""\n    Serializers for {module} API v1.\n"""\nfrom __future__ import annotations\n',
        base_path / "api" / "v1" / "urls.py": f'"""\n    URL configuration for {module} API v1.\n"""\nfrom __future__ import annotations\n\nfrom django.urls import URLPattern, path\n\nurlpatterns: list[URLPattern] = []\n',
        base_path / "api" / "v1" / "views.py": f'"""\n    Views for {module} API v1.\n"""\nfrom __future__ import annotations\n',
        # Application layer
        base_path / "application" / "__init__.py": "",
        base_path / "application" / "services" / "__init__.py": "",
        base_path / "application" / "services" / "dtos.py": f'"""\n    DTOs for {module} application services.\n"""\nfrom __future__ import annotations\n',
        base_path / "application" / "services" / f"{module}_service.py": f'"""\n    Service for {module}.\n"""\nfrom __future__ import annotations\n',
        base_path / "application" / "use_cases" / "__init__.py": "",
        base_path / "application" / "use_cases" / "dtos.py": f'"""\n    DTOs for {module} use cases.\n"""\nfrom __future__ import annotations\n',
        base_path / "application" / "use_cases" / f"{module}_use_case.py": f'"""\n    Use case for {module}.\n"""\nfrom __future__ import annotations\n',
        # Domain layer
        base_path / "domain" / "__init__.py": "",
        base_path / "domain" / "aggregates.py": f'"""\n    Aggregates for {module} domain.\n"""\nfrom __future__ import annotations\n',
        base_path / "domain" / "entities.py": f'"""\n    Entities for {module} domain.\n"""\nfrom __future__ import annotations\n',
        base_path / "domain" / "value_objects.py": f'"""\n    Value objects for {module} domain.\n"""\nfrom __future__ import annotations\n',
        base_path / "domain" / "repositories.py": f'"""\n    Repository interfaces for {module} domain.\n"""\nfrom __future__ import annotations\n',
        # Infrastructure layer
        base_path / "infrastructure" / "__init__.py": "",
        base_path / "infrastructure" / "services" / "__init__.py": "",
        base_path / "infrastructure" / "repositories" / "__init__.py": "",
    }

    for file_path, content in files.items():
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")

    location = f"apps/{actor}/{module}" if actor else f"apps/{module}"
    print(f"DDD structure created at: {location}")  # noqa: T201


class Command(BaseCommand):
    """Django management command to generate DDD folder structure."""

    help = "Generate DDD folder structure for a module"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("module", type=str, help="Name of the module (aggregate root)")
        parser.add_argument("--actor", type=str, default=None, help="Name of the actor (optional)")

    def handle(self, *args: Any, **options: Any) -> None:
        module: str = options["module"]
        actor: str | None = options.get("actor")
        run_folderddd(module, actor)
        self.stdout.write(self.style.SUCCESS(f"DDD folder structure created for '{module}'"))
