# pyms-django-chassis

Open-source Django chassis for building microservices with cross-cutting concerns out of the box.

## Installation

```bash
# Core only
uv add pyms-django-chassis

# With monitoring (recommended for production)
uv add "pyms-django-chassis[monitoring]"

# Full BaaS profile
uv add "pyms-django-chassis[baas]"

# Full DaaS profile
uv add "pyms-django-chassis[daas]"

# Everything
uv add "pyms-django-chassis[all]"
```

## Quick Start

### Create a new microservice

```bash
pyms-django startproject my-service
```

### Or manually

1. Create your project and install the chassis:

```bash
mkdir my-service && cd my-service
uv init
uv add "pyms-django-chassis[baas]"
```

2. Create `config/settings.py`:

```python
from pyms_django.settings.main import *  # noqa: F401,F403

SERVICE_NAME = "ms-my-service"
BASE_PATH = "/my-service/baas/v1"
```

3. Create `config/urls.py`:

```python
from pyms_django.urls import urlpatterns  # noqa: F401
```

4. Run:

```bash
uv run python manage.py runserver
```

## Features

- **Base Model**: UUID PK, timestamps, soft delete
- **Domain Exceptions**: Built-in exception system with standardized error responses
- **Logging**: JSON structured logging with OpenTelemetry trace context
- **Tracing**: Distributed tracing with B3 propagation
- **Metrics**: OpenTelemetry metrics (request count, latency histogram)
- **Multi-tenancy**: PostgreSQL schema-based isolation (optional)
- **API Docs**: Auto-generated Swagger/ReDoc via drf-spectacular (optional)
- **DDD Structure**: Management command to scaffold DDD folder structure
- **Secret Management**: AWS Secrets Manager integration (optional)
- **Read Replicas**: Database router for read/write splitting

## Extras

| Extra | Description |
|-------|-------------|
| `monitoring` | OpenTelemetry tracing + metrics |
| `aws` | AWS Secrets Manager |
| `tenant` | Multi-tenancy with django-tenants |
| `docs` | Swagger/ReDoc with drf-spectacular |
| `restql` | Dynamic field selection |
| `import-export` | Bulk data import/export in admin |
| `dev-tools` | Debug toolbar + django-extensions |
| `daas` | Data as a Service profile |
| `baas` | Backend as a Service profile |
| `all` | Everything |

## License

MIT
