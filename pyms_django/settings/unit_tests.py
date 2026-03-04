"""Minimal Django settings for running pyms-django-chassis unit tests."""
from __future__ import annotations

from typing import Any, Final

DATABASES: Final[dict[str, dict[str, str]]] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

PASSWORD_HASHERS: Final[list[str]] = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

STORAGES: Final[dict[str, dict[str, str]]] = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
