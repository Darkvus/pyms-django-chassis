"""
pyms-django-chassis
Test settings.
"""

from __future__ import annotations

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "pyms_django.base",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "pyms_django.handlers.errors.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
}

ROOT_URLCONF = "pyms_django.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SERVICE_NAME = "test-service"
BASE_PATH = ""
ARTIFACT_VERSION = "0.0.1-test"
DISABLED_PAYLOAD_LOGGING: dict[str, list[str]] = {}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
