<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=26&duration=3000&pause=1000&color=44D492&center=true&vCenter=true&width=680&lines=pyms-django-chassis;Django+microservices%2C+batteries+included;DDD+scaffolding+out+of+the+box;Convention+over+configuration" alt="typing animation" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.11_%7C_3.12_%7C_3.13_%7C_3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.15+-A30000?style=for-the-badge&logo=django&logoColor=white)](https://django-rest-framework.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyms-django-chassis?style=for-the-badge&logo=pypi&logoColor=white&color=0ea5e9)](https://pypi.org/project/pyms-django-chassis)

<p>
  Open-source Django chassis for building production-ready microservices.<br/>
  Cross-cutting concerns out of the box — trace, log, observe, scale.
</p>

</div>

---

## 🛠️ Tech Stack

<div align="center">

[![Tech Stack](https://skillicons.dev/icons?i=python,django,postgres,docker,redis,aws&theme=dark)](https://skillicons.dev)

</div>

<br/>

<div align="center">

![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=flat-square&logo=opentelemetry&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)
![uv](https://img.shields.io/badge/uv-DE5FE9?style=flat-square&logo=uv&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=flat-square&logo=poetry&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=flat-square&logo=ruff&logoColor=black)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

**🏛️ Base Model**
UUID primary key · timestamps · soft-delete · bulk ops with optional `post_save` signals

</td>
<td width="50%">

**🏗️ DDD Scaffold CLI**
Per-actor layers: `api/` · `application/` · `domain/` · `infrastructure/`

</td>
</tr>
<tr>
<td>

**📡 Observability**
Structured JSON logging · OpenTelemetry traces · B3 propagation · OTLP export

</td>
<td>

**🏢 Multi-tenancy**
PostgreSQL schema-based isolation via `django-tenants`

</td>
</tr>
<tr>
<td>

**🔐 Secret Management**
AWS Secrets Manager integration with automatic config loading

</td>
<td>

**📚 API Docs**
Auto-generated Swagger / ReDoc via `drf-spectacular`

</td>
</tr>
<tr>
<td>

**🔀 Read Replicas**
Database router for read/write splitting out of the box

</td>
<td>

**🧙 Interactive CLI**
Textual TUI wizard with step-by-step project generation

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Option A — Interactive wizard

```bash
pip install "pyms-django-chassis[tui]"
pyms-django startproject my-service
```

The TUI wizard guides you through 3 steps:

| Step | Fields |
|:----:|--------|
| **1 — Project Setup** | Package manager · `SERVICE_NAME` · `BASE_PATH` · Python version |
| **2 — Features** | Multi-tenancy · Extras with live selection counter |
| **3 — DDD Structure** | Module name · Actor |

> [!TIP]
> Without `[tui]`, the CLI automatically falls back to plain `input()` prompts.

---

### Option B — Manual setup

```bash
uv add "pyms-django-chassis[baas]"
```

**`config/settings/base.py`** — production settings

```python
from pyms_django.settings.main import *  # noqa: F401,F403

SERVICE_NAME = "ms-my-service"
BASE_PATH    = "/my-service"

INSTALLED_APPS = [*INSTALLED_APPS, "apps.orders"]  # type: ignore[name-defined]  # noqa: F405

LOCAL_APPS: list[tuple[str, str]] = [
    ("apps.orders.api.v1.urls", BASE_PATH),
]
```

**`config/settings/dev.py`** — local development overrides

```python
from config.settings.base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
```

**`config/urls.py`**

```python
from pyms_django.urls import urlpatterns  # noqa: F401
```

```bash
# Development
DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver

# Production (wsgi/asgi default)
DJANGO_SETTINGS_MODULE=config.settings.base gunicorn config.wsgi
```

---

## 🏗️ DDD Scaffold

```bash
# Create the initial module
pyms-django folderddd orders

# Add an actor (usuario, manager, internal …)
pyms-django folderddd orders --actor usuario

# Shared code without api/ layer
pyms-django folderddd orders --actor shared
```

<details>
<summary>📂 Generated structure</summary>

```
apps/
└── orders/                      ← Django app  (apps.orders)
    ├── __init__.py
    ├── apps.py                  ← OrdersConfig
    ├── migrations/
    ├── usuario/                 ← actor: own full DDD stack
    │   ├── api/v1/
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── application/
    │   │   ├── services/
    │   │   └── use_cases/
    │   ├── domain/
    │   │   ├── aggregates.py
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   └── repositories.py
    │   └── infrastructure/
    │       ├── models.py        ← extends BaseModel
    │       ├── services/
    │       └── repositories/
    └── shared/                  ← no api/ — cross-actor shared code
        ├── application/
        ├── domain/
        └── infrastructure/
            └── models.py
```

</details>

Each actor owns its full DDD stack. `shared` is reserved for cross-actor code with no HTTP layer.

---

## 📦 Extras

| Extra | Installs | Purpose |
|-------|----------|---------|
| `monitoring` | `opentelemetry-*` | Tracing + OTLP metrics export |
| `aws` | `boto3` | AWS Secrets Manager |
| `tenant` | `django-tenants` + `psycopg2` | Multi-tenancy |
| `docs` | `drf-spectacular` | OpenAPI / Swagger / ReDoc |
| `restql` | `django-restql` | Dynamic field filtering |
| `import-export` | `django-import-export` | CSV & XLSX bulk operations |
| `dev-tools` | `debug-toolbar` + `django-extensions` | Developer tooling |
| `tui` | `textual` | Interactive CLI wizard |
| `baas` | tenant + docs + restql + monitoring + aws | Backend-as-a-Service profile |
| `daas` | baas + import-export | Data-as-a-Service profile |
| `all` | everything | Full installation |

```bash
pip install "pyms-django-chassis[baas]"
pip install "pyms-django-chassis[monitoring,docs]"
pip install "pyms-django-chassis[all]"
```

---

## 🧱 BaseModel

Every generated model extends `BaseModel` from the chassis:

```python
from pyms_django.models import BaseModel


class Order(BaseModel):
    # ── Inherited fields ───────────────────────────────
    # id          → UUIDField  (auto-generated)
    # created_at  → DateTimeField (auto_now_add)
    # updated_at  → DateTimeField (auto_now)
    # deleted_at  → DateTimeField (null, soft-delete)
    # active      → BooleanField  (True by default)

    # objects      → active records only
    # all_objects  → unfiltered manager

    name = models.CharField(max_length=255)
    ...
```

| Method | Behaviour |
|--------|-----------|
| `instance.delete()` | Soft-delete — sets `active=False` + `deleted_at` |
| `instance.restore()` | Undo soft-delete |
| `instance.hard_delete()` | Permanent removal from DB |
| `Model.bulk_create(objs)` | Batch insert with optional `post_save` signals |
| `Model.bulk_update(objs, fields)` | Batch update with optional `post_save` signals |

---

## ⚡ Built-in Endpoints

Every microservice ships these routes automatically:

| Route | Description |
|-------|-------------|
| `GET /{BASE_PATH}/health-check` | Liveness probe |
| `GET /{BASE_PATH}/version` | Artifact version |
| `GET /{BASE_PATH}/dependencies` | Dependency tree |
| `GET /{BASE_PATH}/schema` | OpenAPI schema *(docs extra)* |
| `GET /{BASE_PATH}/` | Swagger UI *(docs extra)* |
| `GET /{BASE_PATH}/redoc` | ReDoc UI *(docs extra)* |

---

## 📋 License

[MIT](LICENSE) © PyMS Contributors
