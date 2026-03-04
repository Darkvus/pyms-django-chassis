<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=26&duration=3000&pause=1000&color=44D492&center=true&vCenter=true&width=680&lines=pyms-django-chassis;Django+microservices%2C+batteries+included;DDD+scaffolding+out+of+the+box;Convention+over+configuration" alt="typing animation" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.11_%7C_3.12_%7C_3.13_%7C_3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2_%7C_5.x_%7C_6.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
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

<div align="center">

![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=flat-square&logo=opentelemetry&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)
![Textual](https://img.shields.io/badge/Textual-TUI-6D28D9?style=flat-square)
![uv](https://img.shields.io/badge/uv-DE5FE9?style=flat-square&logo=uv&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=flat-square&logo=poetry&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=flat-square&logo=ruff&logoColor=black)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

**🏛️ BaseModel**
UUID PK · timestamps · soft-delete · `restore()` · `hard_delete()` · bulk ops with optional signals

</td>
<td width="50%">

**🏗️ DDD Scaffold CLI**
Layers by actor: `api/v1/` · `application/` · `domain/` · `infrastructure/`

</td>
</tr>
<tr>
<td>

**📡 Observability**
Structured JSON logging · OpenTelemetry tracing · B3 propagation · OTLP export · trace context vars

</td>
<td>

**🏢 Multi-tenancy**
Schema-based tenant isolation via `django-tenants` (PostgreSQL)

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
Database router for read/write separation

</td>
<td>

**🧙 Interactive CLI**
TUI wizard (Textual) or automatic fallback to plain prompts

</td>
</tr>
</table>

---

## 📦 Installation

```bash
# Core only
pip install pyms-django-chassis

# Recommended profile for most microservices
pip install "pyms-django-chassis[baas]"

# Add the TUI wizard on top of any profile
pip install "pyms-django-chassis[baas,tui]"

# Everything
pip install "pyms-django-chassis[all]"
```

### Optional extras

| Extra | Packages | Description |
|-------|----------|-------------|
| `monitoring` | `opentelemetry-api` · `sdk` · `propagator-b3` · `exporter-otlp-proto-http` | Distributed tracing + OTLP export |
| `aws` | `boto3` | AWS Secrets Manager |
| `tenant` | `django-tenants` · `psycopg2-binary` | Schema-based multi-tenancy (PostgreSQL) |
| `docs` | `drf-spectacular` | OpenAPI · Swagger UI · ReDoc |
| `restql` | `django-restql` | Dynamic field filtering via query params |
| `import-export` | `django-import-export` | CSV / XLSX import and export |
| `dev-tools` | `django-debug-toolbar` · `django-extensions` | Development utilities |
| `tui` | `textual` | Interactive terminal wizard (see CLI) |
| `baas` | `tenant` + `docs` + `restql` + `monitoring` + `aws` | Backend-as-a-Service profile |
| `daas` | `tenant` + `docs` + `restql` + `import-export` + `monitoring` + `aws` | Data-as-a-Service profile |
| `all` | all of the above except `tui` | Full feature set |

> [!NOTE]
> `tui` is not included in `all`. Install it explicitly if you want the interactive wizard.

---

## 🚀 Quick Start

### 1. Generate a new microservice

```bash
pip install "pyms-django-chassis[tui]"
pyms-django startproject my-service
```

The wizard covers **3 steps + confirmation**:

| Step | Fields |
|:----:|--------|
| **1 · Project Setup** | Package manager (`uv` / `poetry`) · `SERVICE_NAME` · `BASE_PATH` · Python version (3.11–3.14) · Django version (4.2 LTS – 6.0) |
| **2 · Features** | Multi-tenancy toggle · Extras with inline descriptions · live counter `N/7` · synced `all` checkbox |
| **3 · DDD Structure** | Module name · Actor (optional) |
| **Confirmation** | Full summary · Generate / Cancel · `Escape` goes back |

**Generated layout:**

```
my-service/
├── manage.py
├── pyproject.toml                   # uv (PEP 621) or poetry
├── Dockerfile                       # Multi-stage build
├── docker-compose.yml               # Includes PostgreSQL when multitenant=True
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml          # Ruff hooks
├── ruff.toml
├── README.md
├── config/
│   ├── settings/
│   │   ├── base.py                  # Production — all settings
│   │   └── dev.py                   # Local — inherits base, DEBUG=True
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    └── <module>/
        ├── apps.py
        ├── migrations/
        └── ...                      # DDD structure (see folderddd)
```

### 2. Inherit chassis settings

```python
# config/settings/base.py
from pyms_django.settings.main import *  # noqa: F401,F403

SERVICE_NAME = "ms-orders"
BASE_PATH    = "/orders"
MULTITENANT  = False

INSTALLED_APPS = [*INSTALLED_APPS, "apps.orders"]  # noqa: F405

LOCAL_APPS: list[tuple[str, str]] = [
    ("apps.orders.usuario.api.v1.urls", BASE_PATH),
]
```

```python
# config/settings/dev.py
from config.settings.base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
```

---

## 🖥️ CLI

```
pyms-django <command> [args]

Commands:
  startproject <name>           Generate a complete microservice
  folderddd <module> [--actor]  Add DDD structure to an existing project
```

### `folderddd`

Generates (or extends) the DDD structure of a module. Can be called multiple times to add new actors without touching existing ones.

```bash
# No actor — all layers directly under apps/{module}/
pyms-django folderddd orders

# With actor — each actor gets its own full stack
pyms-django folderddd orders --actor user
pyms-django folderddd orders --actor manager
pyms-django folderddd orders --actor internal

# Special actor — no api/ layer
pyms-django folderddd orders --actor shared
```

**Generated structure:**

```
apps/
└── orders/                          # Django app  (name="apps.orders")
    ├── __init__.py
    ├── apps.py                      # OrdersConfig, label="orders"
    ├── migrations/
    │
    ├── user/                        # actor with full DDD stack
    │   ├── api/v1/
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── application/
    │   │   ├── services/
    │   │   │   ├── dtos.py
    │   │   │   └── orders_service.py
    │   │   └── use_cases/
    │   │       ├── dtos.py
    │   │       └── orders_use_case.py
    │   ├── domain/
    │   │   ├── aggregates.py
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   └── repositories.py
    │   └── infrastructure/
    │       ├── models.py            # extends BaseModel
    │       ├── services/
    │       └── repositories/
    │
    └── shared/                      # no api/ — code shared between actors
        ├── application/
        ├── domain/
        └── infrastructure/
            └── models.py
```

> [!TIP]
> `shared` is a reserved actor name. You can call `folderddd` as many times as needed to add actors without touching existing ones.

**Register the app in settings:**

```python
# config/settings/base.py
INSTALLED_APPS = [*INSTALLED_APPS, "apps.orders"]  # noqa: F405

LOCAL_APPS: list[tuple[str, str]] = [
    ("apps.orders.user.api.v1.urls", BASE_PATH),
    ("apps.orders.manager.api.v1.urls", f"{BASE_PATH}/manager"),
]
```

---

## 🧱 BaseModel

All generated models extend `BaseModel`:

```python
from pyms_django.models import BaseModel
from django.db import models


class Order(BaseModel):
    # ── Inherited fields ─────────────────────────────────
    # id          → UUIDField        auto-generated, non-editable
    # created_at  → DateTimeField    auto_now_add
    # updated_at  → DateTimeField    auto_now
    # deleted_at  → DateTimeField    null  (soft-delete marker)
    # active      → BooleanField     True by default
    #
    # objects      → active records only
    # all_objects  → no filter applied

    name = models.CharField(max_length=255)

    class Meta:
        active_signals_bulk_operations = True  # emit post_save on bulk ops
```

| Method | Behaviour |
|--------|-----------|
| `instance.delete()` | Soft-delete: `active=False` + `deleted_at=now()` |
| `instance.restore()` | Undo soft-delete |
| `instance.hard_delete()` | Permanently remove from the database |
| `qs.hard_delete()` | Bulk permanent delete via queryset |
| `Model.bulk_create(objs)` | Mass insert, emits `post_save` if `active_signals_bulk_operations=True` |
| `Model.bulk_update(objs, fields)` | Mass update, emits `post_save` if `active_signals_bulk_operations=True` |

---

## 💥 Domain Exceptions

```python
from pyms_django.exceptions import DomainException, TypeException, LogLevel, ErrorDetail


class UserNotFoundError(DomainException):
    code = "user_not_found"
    description = "The requested user does not exist"
    type = TypeException.BUSINESS   # → HTTP 400
    log_level = LogLevel.WARNING

# Raise with field-level details
raise UserNotFoundError(
    field="user_id",
    details=[ErrorDetail(code="invalid_uuid", description="Not a valid UUID")],
)
```

| `TypeException` | HTTP status |
|-----------------|-------------|
| `VALIDATION` | 400 |
| `BUSINESS` | 400 |
| `PERMISSION` | 403 |
| `TECHNICAL` | 500 (default) |

**Standardised error response:**

```json
{
  "messages": [
    {
      "type": "ERROR",
      "code": "user_not_found",
      "description": "",
      "field": "user_id",
      "details": [
        {"code": "invalid_uuid", "description": "Not a valid UUID"}
      ]
    }
  ],
  "trace_id": "a1b2c3d4e5f6..."
}
```

> The `description` field is intentionally empty in HTTP responses for domain exceptions — details are only logged server-side.

---

## 📡 Observability

### Structured JSON logging

Every log line is enriched with service metadata and the current trace context:

```json
{
  "message": "REQUEST",
  "timestamp": "2026-03-04T10:30:45.123456+00:00",
  "severity": "INFO",
  "service": "ms-orders",
  "version": "1.2.0",
  "trace": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "span": "x1y2z3a4b5c6d7e8",
  "url": "http://localhost:8000/orders/",
  "method": "POST"
}
```

Fields `trace` and `span` are populated from the active OpenTelemetry span when the `monitoring` extra is installed, or from B3 headers extracted by `TracingMiddleware` otherwise — so trace IDs always appear in logs even without an OTel SDK.

### Masking sensitive payloads

```python
# config/settings/base.py
DISABLED_PAYLOAD_LOGGING = {
    "/api/login/": ["password", "token"],
    "/api/users/": ["email"],
}
```

### OpenTelemetry tracing

Install the `monitoring` extra and point the collector URL:

```bash
pip install "pyms-django-chassis[monitoring]"
```

```python
# .env
METRICS_COLLECTOR_URL=http://otel-collector:4318
```

The `TracingMiddleware` creates a SERVER span for every request and propagates B3 headers to downstream calls automatically.

---

## ⚡ Built-in Endpoints

All microservices expose these routes without any additional configuration:

| Route | Description | Requires extra |
|-------|-------------|----------------|
| `GET /{BASE_PATH}/health-check/` | Liveness probe | — |
| `GET /{BASE_PATH}/version/` | Artifact version (read from `pyproject.toml`) | — |
| `GET /{BASE_PATH}/dependencies/` | Dependency tree | — |
| `GET /{BASE_PATH}/schema/` | OpenAPI schema | `docs` |
| `GET /{BASE_PATH}/` | Swagger UI | `docs` |
| `GET /{BASE_PATH}/redoc/` | ReDoc | `docs` |

---

## 🏢 Multi-tenancy

Enable schema-based multi-tenancy (PostgreSQL only):

```python
# config/settings/base.py
from pyms_django.settings.main import *  # noqa: F401,F403

MULTITENANT = True

TENANT_APPS: list[str] = [
    "apps.orders",
]
```

When `MULTITENANT = True` the chassis automatically:

- Sets `DATABASES["default"]["ENGINE"]` to `django_tenants.postgresql_backend`
- Prepends `TenantMainMiddleware` as the first middleware
- Rebuilds `INSTALLED_APPS` with the required `django_tenants` ordering
- Adds `TenantSyncRouter` to `DATABASE_ROUTERS`

> [!IMPORTANT]
> The `tenant` extra must be installed: `pip install "pyms-django-chassis[tenant]"`

---

## 🔀 Read Replicas

```python
# config/settings/base.py
ACTIVE_DATABASE_READ = True

DATABASES = {
    "default": {   # write
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "primary-db.example.com",
        ...
    },
    "read_db": {   # read replica
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "replica-db.example.com",
        ...
    },
}
```

```python
from pyms_django.db.utils import get_read_db_alias

queryset = Order.objects.using(get_read_db_alias()).filter(active=True)
```

---

## 📄 OpenAPI Components

Reusable OAS definitions to keep schema annotations DRY:

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter
from pyms_django.oas.parameters import HEADER_USER_ID_PARAM
from pyms_django.oas.responses import BAD_REQUEST_RESPONSE, INTERNAL_SERVER_ERROR_RESPONSE


@extend_schema(
    parameters=[OpenApiParameter(**HEADER_USER_ID_PARAM)],
    responses={
        400: BAD_REQUEST_RESPONSE,
        500: INTERNAL_SERVER_ERROR_RESPONSE,
    },
)
def my_view(request):
    ...
```

---

## ⚙️ Settings Reference

All variables below can be overridden in your `config/settings/base.py` after the star import.

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | `"to-be-defined"` | Service identifier — used in logs |
| `BASE_PATH` | `""` | URL prefix for all routes |
| `MULTITENANT` | `False` | Enable schema-based multi-tenancy |
| `ADMIN_ENABLED` | `False` | Mount Django admin at `{BASE_PATH}/admin/` |
| `LOCAL_APPS` | `[]` | List of `(urls_module, prefix)` tuples to register |
| `TENANT_APPS` | `[]` | Apps isolated per tenant (multitenant only) |
| `HEADER_USER_ID` | `"User-Id"` | Header name for the authenticated user UUID |
| `HEADER_APP_ID` | `"App-Id"` | Header name for the calling application ID |
| `ACTIVE_DATABASE_READ` | `False` | Route read queries to `read_db` |
| `DISABLED_PAYLOAD_LOGGING` | `{}` | Map of path → fields to mask in request logs |
| `API_VERSION` | `"v1"` | Default API version prefix for the chassis router |

**Environment variables** consumed directly:

| Variable | Used for |
|----------|---------|
| `DJANGO_SECRET_KEY` | `SECRET_KEY` |
| `DJANGO_DEBUG` | `DEBUG` (`true`/`false`) |
| `DJANGO_ALLOWED_HOSTS` | `ALLOWED_HOSTS` (comma-separated) |
| `DATABASE_ENGINE` | DB engine (default `sqlite3`) |
| `DATABASE_NAME` | DB name |
| `DATABASE_USER` | DB user |
| `DATABASE_PASSWORD` | DB password |
| `DATABASE_HOST` | DB host |
| `DATABASE_PORT` | DB port |
| `LOG_LEVEL` | Root log level (default `INFO`) |
| `METRICS_COLLECTOR_URL` | OTLP collector endpoint |

---

## 🐍 Django Compatibility

| Django | Support |
|--------|---------|
| 4.2 LTS | ✓ |
| 5.0 | ✓ |
| 5.1 | ✓ |
| 5.2 LTS | ✓ |
| 6.0 | ✓ |

The chassis uses `STORAGES` (available since Django 4.2) and avoids deprecated APIs, making it forward-compatible across all supported versions. The CLI lets you choose the exact Django version when generating a new microservice.

---

## 📋 License

[MIT](LICENSE) © PyMS Contributors
