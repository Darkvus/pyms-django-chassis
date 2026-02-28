"""Default Django settings for pyms-django-chassis microservices."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Final

from pyms_django.settings.apps import SHARED_APPS
from pyms_django.settings.middlewares import SHARED_MIDDLEWARE

# --- Core ---
SERVICE_NAME: str = "to-be-defined"
BASE_PATH: str = ""
MULTITENANT: bool = False
ADMIN_ENABLED: bool = False
LOCAL_APPS: list[tuple[str, str]] = []

# --- Paths ---
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent.parent

# --- Security ---
SECRET_KEY: str = os.environ.get("DJANGO_SECRET_KEY", "change-me-in-production")
DEBUG: bool = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS: list[str] = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# --- Multi-tenant ---
TENANT_MODEL: str = "tenants.Tenant"
TENANT_DOMAIN_MODEL: str = "tenants.Domain"
DATABASE_ROUTERS: list[str] = ["pyms_django.db.database_routers.ReadWriteRouter"]

# --- Custom Headers ---
HEADER_USER_ID: Final[str] = "User-Id"
HEADER_APP_ID: Final[str] = "App-Id"

# --- Metrics ---
METRIC_PROVIDER: Any = None
METRICS_COLLECTOR_URL: str = os.environ.get("METRICS_COLLECTOR_URL", "http://localhost:4318/v1/metrics")

# --- Payload Logging ---
DISABLED_PAYLOAD_LOGGING: dict[str, list[str]] = {}

# --- Installed Apps ---
INSTALLED_APPS: list[str] = [
    *SHARED_APPS,
]

# Conditionally add tenant apps
try:
    import django_tenants  # noqa: F401
    INSTALLED_APPS = [
        "django_tenants",
        *INSTALLED_APPS,
        "pyms_django.tenants",
    ]
    DATABASE_ROUTERS = ["django_tenants.routers.TenantSyncRouter", *DATABASE_ROUTERS]
except ImportError:
    pass

# Conditionally add drf-spectacular
try:
    import drf_spectacular  # noqa: F401
    INSTALLED_APPS.append("drf_spectacular")
except ImportError:
    pass

# Conditionally add import-export
try:
    import import_export  # noqa: F401
    INSTALLED_APPS.append("import_export")
except ImportError:
    pass

# Conditionally add debug toolbar
try:
    import debug_toolbar  # noqa: F401
    if DEBUG:
        INSTALLED_APPS.append("debug_toolbar")
except ImportError:
    pass

# Conditionally add django-extensions
try:
    import django_extensions  # noqa: F401
    INSTALLED_APPS.append("django_extensions")
except ImportError:
    pass

# --- Middleware ---
MIDDLEWARE: list[str] = list(SHARED_MIDDLEWARE)

if DEBUG:
    try:
        import debug_toolbar  # noqa: F401
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    except ImportError:
        pass

# --- Templates ---
TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Database ---
DATABASES: dict[str, dict[str, Any]] = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DATABASE_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.environ.get("DATABASE_USER", ""),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", ""),
        "HOST": os.environ.get("DATABASE_HOST", ""),
        "PORT": os.environ.get("DATABASE_PORT", ""),
    },
}

ACTIVE_DATABASE_READ: bool = os.environ.get("ACTIVE_DATABASE_READ", "false").lower() == "true"
if ACTIVE_DATABASE_READ:
    DATABASES["read_db"] = {
        "ENGINE": os.environ.get("READ_DATABASE_ENGINE", DATABASES["default"]["ENGINE"]),
        "NAME": os.environ.get("READ_DATABASE_NAME", DATABASES["default"]["NAME"]),
        "USER": os.environ.get("READ_DATABASE_USER", DATABASES["default"].get("USER", "")),
        "PASSWORD": os.environ.get("READ_DATABASE_PASSWORD", DATABASES["default"].get("PASSWORD", "")),
        "HOST": os.environ.get("READ_DATABASE_HOST", DATABASES["default"].get("HOST", "")),
        "PORT": os.environ.get("READ_DATABASE_PORT", DATABASES["default"].get("PORT", "")),
    }

# --- Auth ---
AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---
LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "UTC"
USE_I18N: bool = True
USE_TZ: bool = True

# --- Static Files ---
STATIC_URL: str = "/static/"
STATIC_ROOT: str = str(BASE_DIR / "staticfiles")
STATICFILES_STORAGE: str = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Default PK ---
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
ROOT_URLCONF: str = "pyms_django.urls"

# --- WSGI / ASGI ---
WSGI_APPLICATION: str = "pyms_django.wsgi.application"
ASGI_APPLICATION: str = "pyms_django.asgi.application"

# --- REST Framework ---
REST_FRAMEWORK: dict[str, Any] = {
    "EXCEPTION_HANDLER": "pyms_django.handlers.errors.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M:%SZ",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# Add drf-spectacular schema class if available
try:
    import drf_spectacular  # noqa: F401
    REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
except ImportError:
    pass

# --- drf-spectacular ---
SPECTACULAR_SETTINGS: dict[str, Any] = {
    "TITLE": SERVICE_NAME,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# --- CORS ---
CORS_ALLOW_ALL_ORIGINS: bool = True

# --- Version ---
ARTIFACT_VERSION: str = os.environ.get("ARTIFACT_VERSION", "unknown")

# --- Logging ---
LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pyms_django.formatters.logging.CustomJsonFormatter",
        },
    },
    "filters": {
        "tenant_context": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: True,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["tenant_context"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "pyms_django": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# --- B3 Propagation ---
try:
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.b3 import B3Format
    set_global_textmap(B3Format())
except ImportError:
    pass
