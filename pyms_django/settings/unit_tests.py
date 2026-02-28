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

DEFAULT_FILE_STORAGE: Final[str] = "django.core.files.storage.InMemoryStorage"
