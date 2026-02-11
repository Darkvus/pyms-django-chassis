"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from typing import Final

from django.conf import settings

DEFAULT_DB_ALIAS: Final[str] = "default"
READ_DB_ALIAS: Final[str] = "read_db"


def get_read_db_alias() -> str:
    """Return the appropriate read database alias."""
    if getattr(settings, "ACTIVE_DATABASE_READ", False) and READ_DB_ALIAS in settings.DATABASES:
        return READ_DB_ALIAS
    return DEFAULT_DB_ALIAS
