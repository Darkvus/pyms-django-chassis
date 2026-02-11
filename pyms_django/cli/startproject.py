"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Final

PYTHON_VERSIONS: Final[list[str]] = ["3.11", "3.12", "3.13"]
EXTRAS: Final[list[str]] = ["monitoring", "aws", "tenant", "docs", "restql", "import-export", "dev-tools"]


def _prompt_choice(prompt: str, choices: list[str]) -> str:
    """Prompt user to select from a list of choices."""
    print(f"\n{prompt}")  # noqa: T201
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")  # noqa: T201
    while True:
        try:
            selection = int(input("Select (number): "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
        except (ValueError, EOFError):
            pass
        print("Invalid selection. Try again.")  # noqa: T201


def _prompt_text(prompt: str, default: str = "") -> str:
    """Prompt user for text input."""
    suffix = f" [{default}]" if default else ""
    value = input(f"\n{prompt}{suffix}: ").strip()
    return value or default


def _prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Prompt user for yes/no."""
    suffix = " [Y/n]" if default else " [y/N]"
    value = input(f"\n{prompt}{suffix}: ").strip().lower()
    if not value:
        return default
    return value in ("y", "yes")


def _prompt_multi_select(prompt: str, choices: list[str]) -> list[str]:
    """Prompt user to select multiple items."""
    print(f"\n{prompt}")  # noqa: T201
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")  # noqa: T201
    print("Enter numbers separated by commas (e.g., 1,2,4):")  # noqa: T201
    while True:
        try:
            selections = input("Select: ").strip().split(",")
            selected = []
            for s in selections:
                idx = int(s.strip())
                if 1 <= idx <= len(choices):
                    selected.append(choices[idx - 1])
            if selected:
                return selected
        except (ValueError, EOFError):
            pass
        print("Invalid selection. Try again.")  # noqa: T201


def _create_manage_py(project_dir: Path) -> None:
    """Create manage.py."""
    content = '''#!/usr/bin/env python
"""Django management script."""
from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
'''
    (project_dir / "manage.py").write_text(content, encoding="utf-8")


def _create_config_settings(
    project_dir: Path,
    service_name: str,
    base_path: str,
    multitenant: bool,
) -> None:
    """Create config/settings.py."""
    content = f'''"""
    Settings for {service_name}.
"""
from __future__ import annotations

from pyms_django.settings.main import *  # noqa: F401,F403

SERVICE_NAME = "{service_name}"
BASE_PATH = "{base_path}"
MULTITENANT = {multitenant}

LOCAL_APPS: list[tuple[str, str]] = [
    # ("apps.<module>.api.v1.urls", BASE_PATH),
]
'''
    config_dir = project_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "__init__.py").write_text("", encoding="utf-8")
    (config_dir / "settings.py").write_text(content, encoding="utf-8")


def _create_config_urls(project_dir: Path) -> None:
    """Create config/urls.py."""
    content = '''"""
    URL configuration.
"""
from __future__ import annotations

from pyms_django.urls import urlpatterns  # noqa: F401
'''
    (project_dir / "config" / "urls.py").write_text(content, encoding="utf-8")


def _create_config_wsgi(project_dir: Path) -> None:
    """Create config/wsgi.py."""
    content = '''"""
    WSGI config.
"""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
'''
    (project_dir / "config" / "wsgi.py").write_text(content, encoding="utf-8")


def _create_config_asgi(project_dir: Path) -> None:
    """Create config/asgi.py."""
    content = '''"""
    ASGI config.
"""
from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
'''
    (project_dir / "config" / "asgi.py").write_text(content, encoding="utf-8")


def _create_pyproject_uv(
    project_dir: Path,
    project_name: str,
    python_version: str,
    extras: list[str],
) -> None:
    """Create pyproject.toml for uv (PEP 621)."""
    extras_str = ",".join(extras)
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
requires-python = ">={python_version}"
dependencies = [
    "pyms-django-chassis[{extras_str}]",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-django>=4.7.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.8.4",
    "pre-commit>=3.5.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
    (project_dir / "pyproject.toml").write_text(content, encoding="utf-8")


def _create_pyproject_poetry(
    project_dir: Path,
    project_name: str,
    python_version: str,
    extras: list[str],
) -> None:
    """Create pyproject.toml for poetry."""
    extras_list = ", ".join(f'"{e}"' for e in extras)
    content = f'''[tool.poetry]
name = "{project_name}"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^{python_version}"
pyms-django-chassis = {{version = "^1.0.0", extras = [{extras_list}]}}

[tool.poetry.group.dev.dependencies]
pytest = ">=8.0.0"
pytest-django = ">=4.7.0"
pytest-mock = ">=3.12.0"
pytest-cov = ">=4.1.0"
ruff = ">=0.8.4"
pre-commit = ">=3.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
    (project_dir / "pyproject.toml").write_text(content, encoding="utf-8")


def _create_dockerfile(
    project_dir: Path,
    python_version: str,
    package_manager: str,
) -> None:
    """Create Dockerfile."""
    if package_manager == "uv":
        install_cmd = """COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev"""
    else:
        install_cmd = """RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev"""

    content = f'''# --- Builder stage ---
FROM python:{python_version}-slim AS builder
{install_cmd}

# --- Runtime stage ---
FROM python:{python_version}-slim
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
'''
    (project_dir / "Dockerfile").write_text(content, encoding="utf-8")


def _create_docker_compose(
    project_dir: Path,
    project_name: str,
    multitenant: bool,
) -> None:
    """Create docker-compose.yml."""
    services = f'''services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env'''

    if multitenant:
        services += '''
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ''' + project_name + '''
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
'''
    else:
        services += "\n"

    (project_dir / "docker-compose.yml").write_text(services, encoding="utf-8")


def _create_env_example(
    project_dir: Path,
    service_name: str,
    base_path: str,
    multitenant: bool,
    project_name: str,
) -> None:
    """Create .env.example."""
    content = f'''DJANGO_SETTINGS_MODULE=config.settings
SERVICE_NAME={service_name}
BASE_PATH={base_path}
MULTITENANT={"true" if multitenant else "false"}'''

    if multitenant:
        content += f'''
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME={project_name}'''

    content += "\n"
    (project_dir / ".env.example").write_text(content, encoding="utf-8")


def _create_gitignore(project_dir: Path) -> None:
    """Create .gitignore."""
    content = '''.venv/
__pycache__/
.env
*.pyc
.mypy_cache/
.pytest_cache/
.ruff_cache/
dist/
*.egg-info/
staticfiles/
db.sqlite3
.coverage
htmlcov/
'''
    (project_dir / ".gitignore").write_text(content, encoding="utf-8")


def _create_pre_commit_config(project_dir: Path) -> None:
    """Create .pre-commit-config.yaml."""
    content = '''repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
'''
    (project_dir / ".pre-commit-config.yaml").write_text(content, encoding="utf-8")


def _create_ruff_toml(project_dir: Path) -> None:
    """Create ruff.toml."""
    content = '''target-version = "py311"
line-length = 120

[lint]
select = ["E", "F", "W", "I", "N", "UP", "ANN", "B", "A", "COM", "C4", "PT", "RET", "SIM", "TCH", "ARG", "PTH", "ERA"]
'''
    (project_dir / "ruff.toml").write_text(content, encoding="utf-8")


def _create_readme(project_dir: Path, project_name: str) -> None:
    """Create README.md."""
    content = f'''# {project_name}

Microservice built with [pyms-django-chassis](https://github.com/pyms/pyms-django-chassis).

## Getting Started

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Start dev server
uv run python manage.py runserver
```
'''
    (project_dir / "README.md").write_text(content, encoding="utf-8")


def run_startproject(project_name: str) -> None:
    """Run the interactive startproject command."""
    print(f"\nCreating microservice: {project_name}")  # noqa: T201
    print("=" * 50)  # noqa: T201

    # 1. Package manager
    package_manager = _prompt_choice("Package manager:", ["uv", "poetry"])

    # 2. SERVICE_NAME
    service_name = _prompt_text("SERVICE_NAME:", f"ms-{project_name}")

    # 3. BASE_PATH
    base_path = _prompt_text("BASE_PATH:", f"/{project_name}")

    # 4. Python version
    python_version = _prompt_choice("Python version:", PYTHON_VERSIONS)

    # 5. Multi-tenant?
    multitenant = _prompt_yes_no("Enable multi-tenancy?", default=False)

    # 6. Extras
    selected_extras = _prompt_multi_select("Select extras to install:", EXTRAS)

    # 7. DDD module
    module_name = _prompt_text("Initial DDD module name (aggregate root):", project_name)

    # 8. Actor (optional)
    actor = _prompt_text("Actor (optional, press Enter to skip):", "")
    actor = actor if actor else None

    # Create project directory
    project_dir = Path.cwd() / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Generate all files
    _create_manage_py(project_dir)
    _create_config_settings(project_dir, service_name, base_path, multitenant)
    _create_config_urls(project_dir)
    _create_config_wsgi(project_dir)
    _create_config_asgi(project_dir)

    if package_manager == "uv":
        _create_pyproject_uv(project_dir, project_name, python_version, selected_extras)
    else:
        _create_pyproject_poetry(project_dir, project_name, python_version, selected_extras)

    _create_dockerfile(project_dir, python_version, package_manager)
    _create_docker_compose(project_dir, project_name, multitenant)
    _create_env_example(project_dir, service_name, base_path, multitenant, project_name)
    _create_gitignore(project_dir)
    _create_pre_commit_config(project_dir)
    _create_ruff_toml(project_dir)
    _create_readme(project_dir, project_name)

    # Generate DDD structure
    original_dir = Path.cwd()
    os.chdir(project_dir)
    from pyms_django.base.management.commands.folderddd import run_folderddd
    run_folderddd(module_name, actor)
    os.chdir(original_dir)

    print(f"\nProject '{project_name}' created successfully!")  # noqa: T201
    print(f"  cd {project_name}")  # noqa: T201
    if package_manager == "uv":
        print("  uv sync")  # noqa: T201
    else:
        print("  poetry install")  # noqa: T201
    print("  python manage.py runserver")  # noqa: T201
