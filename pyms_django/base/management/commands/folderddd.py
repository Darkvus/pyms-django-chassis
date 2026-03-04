"""Django management command for scaffolding DDD folder structures."""
from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser


def run_folderddd(module: str, actor: str | None = None) -> None:
    """Create a Domain-Driven Design folder structure for a module.

    The Django app always lives at ``apps/{module}/`` (``apps.py``, ``migrations/``).
    Each actor (e.g. ``usuario``, ``manager``, ``internal``) gets its own sub-folder
    with full DDD layers. The special actor ``shared`` is created without an ``api/``
    layer. Without an actor, all layers are created directly under ``apps/{module}/``.

    Args:
        module: Name of the module (aggregate root) to scaffold.
        actor: Optional actor name. Creates ``apps/{module}/{actor}/`` with its own
            ``api/``, ``application/``, ``domain/`` and ``infrastructure/`` layers.
            Use ``shared`` for code shared across actors (no ``api/`` generated).
    """
    app_path = Path("apps") / module        # Django app root (apps.py, migrations)
    app_name = f"apps.{module}"
    app_class = "".join(word.capitalize() for word in module.replace("-", "_").split("_"))
    app_label = module.replace("-", "_")

    # Each actor owns all its DDD layers under apps/{module}/{actor}/.
    # Without an actor the layers sit directly at the module root.
    # "shared" is a reserved actor name that has no api/ layer.
    if actor:
        ddd_root = app_path / actor
        include_api = actor != "shared"
    else:
        ddd_root = app_path
        include_api = True

    # Define the DDD directory structure
    directories: list[Path] = [
        app_path / "migrations",
        ddd_root / "application" / "services",
        ddd_root / "application" / "use_cases",
        ddd_root / "domain",
        ddd_root / "infrastructure" / "services",
        ddd_root / "infrastructure" / "repositories",
    ]
    if include_api:
        directories.append(ddd_root / "api" / "v1")

    # Create all directories
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # ── Django app boilerplate (always at app_path) ───────────────────
    files: dict[Path, str] = {
        Path("apps") / "__init__.py": "",
        app_path / "__init__.py": "",
        app_path / "apps.py": (
            f'"""\n    AppConfig for {module}.\n"""\n'
            "from __future__ import annotations\n\n"
            "from django.apps import AppConfig\n\n\n"
            f"class {app_class}Config(AppConfig):\n"
            '    default_auto_field = "django.db.models.BigAutoField"\n'
            f'    name = "{app_name}"\n'
            f'    label = "{app_label}"\n'
        ),
        app_path / "migrations" / "__init__.py": "",
        # ── DDD root package ──────────────────────────────────────────
        ddd_root / "__init__.py": "",
        # ── Application layer ─────────────────────────────────────────
        ddd_root / "application" / "__init__.py": "",
        ddd_root / "application" / "services" / "__init__.py": "",
        ddd_root / "application" / "services" / "dtos.py": (
            f'"""\n    DTOs for {module} application services.\n"""\n'
            "from __future__ import annotations\n"
        ),
        ddd_root / "application" / "services" / f"{module}_service.py": (
            f'"""\n    Service for {module}.\n"""\n'
            "from __future__ import annotations\n"
        ),
        ddd_root / "application" / "use_cases" / "__init__.py": "",
        ddd_root / "application" / "use_cases" / "dtos.py": (
            f'"""\n    DTOs for {module} use cases.\n"""\n'
            "from __future__ import annotations\n"
        ),
        ddd_root / "application" / "use_cases" / f"{module}_use_case.py": (
            f'"""\n    Use case for {module}.\n"""\n'
            "from __future__ import annotations\n"
        ),
        # ── Domain layer ──────────────────────────────────────────────
        ddd_root / "domain" / "__init__.py": "",
        ddd_root / "domain" / "aggregates.py": (
            f'"""\n    Aggregates for {module} domain.\n"""\n'
            "from __future__ import annotations\n"
        ),
        ddd_root / "domain" / "entities.py": (
            f'"""\n    Entities for {module} domain.\n"""\n'
            "from __future__ import annotations\n"
        ),
        ddd_root / "domain" / "value_objects.py": (
            f'"""\n    Value objects for {module} domain.\n"""\n'
            "from __future__ import annotations\n"
        ),
        ddd_root / "domain" / "repositories.py": (
            f'"""\n    Repository interfaces for {module} domain.\n"""\n'
            "from __future__ import annotations\n"
        ),
        # ── Infrastructure layer ──────────────────────────────────────
        ddd_root / "infrastructure" / "__init__.py": "",
        ddd_root / "infrastructure" / "models.py": (
            f'"""\n    Django ORM models for {module}.\n"""\n'
            "from __future__ import annotations\n\n"
            "from pyms_django.models import BaseModel\n\n\n"
            f"class {app_class}(BaseModel):\n"
            f'    """{app_class} model.\n\n    Add your fields here.\n    """\n\n'
            "    class Meta:\n"
            f'        app_label = "{app_label}"\n'
            f'        db_table = "{app_label}"\n'
            f'        verbose_name = "{app_label.replace("_", " ")}"\n'
            f'        verbose_name_plural = "{app_label.replace("_", " ")}"\n\n'
            "    def __str__(self) -> str:\n"
            f'        return f"{app_class}({{self.pk}})"\n'
        ),
        ddd_root / "infrastructure" / "services" / "__init__.py": "",
        ddd_root / "infrastructure" / "repositories" / "__init__.py": "",
    }

    # ── API layer (absent for "shared") ───────────────────────────────
    if include_api:
        files.update({
            ddd_root / "api" / "__init__.py": "",
            ddd_root / "api" / "v1" / "__init__.py": "",
            ddd_root / "api" / "v1" / "serializers.py": (
                f'"""\n    Serializers for {module} API v1.\n"""\n'
                "from __future__ import annotations\n"
            ),
            ddd_root / "api" / "v1" / "urls.py": (
                f'"""\n    URL configuration for {module} API v1.\n"""\n'
                "from __future__ import annotations\n\n"
                "from django.urls import URLPattern, path\n\n"
                "urlpatterns: list[URLPattern] = []\n"
            ),
            ddd_root / "api" / "v1" / "views.py": (
                f'"""\n    Views for {module} API v1.\n"""\n'
                "from __future__ import annotations\n"
            ),
        })

    for file_path, content in files.items():
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")

    if actor:
        suffix = " (no api — shared layer)" if not include_api else ""
        location = f"apps/{module}/{actor}{suffix}"
    else:
        location = f"apps/{module}"
    print(f"DDD structure created at: {location}")  # noqa: T201


class Command(BaseCommand):
    """Management command that generates a DDD folder structure for a module."""

    help = "Generate DDD folder structure for a module"

    def add_arguments(self, parser: CommandParser) -> None:
        """Register the ``module`` and optional ``--actor`` CLI arguments.

        Args:
            parser: The argument parser provided by Django's management framework.
        """
        parser.add_argument("module", type=str, help="Name of the module (aggregate root)")
        parser.add_argument("--actor", type=str, default=None, help="Name of the actor (optional)")

    def handle(self, *_args: object, **options: object) -> None:  # noqa: ANN401
        """Execute the command.

        Args:
            *_args: Unused positional arguments.
            **options: Parsed CLI options, including ``module`` and ``actor``.
        """
        module: str = str(options["module"])
        actor: str | None = str(options["actor"]) if options.get("actor") else None
        run_folderddd(module, actor)
        self.stdout.write(self.style.SUCCESS(f"DDD folder structure created for '{module}'"))
