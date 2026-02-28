"""Database utility helpers for pyms-django-chassis."""
from __future__ import annotations

from typing import Final

from django.conf import settings

DEFAULT_DB_ALIAS: Final[str] = "default"
READ_DB_ALIAS: Final[str] = "read_db"


def get_read_db_alias() -> str:
    """Return the appropriate database alias for read queries.

    Returns:
        ``"read_db"`` when a read replica is configured and active,
        otherwise ``"default"``.
    """
    if getattr(settings, "ACTIVE_DATABASE_READ", False) and READ_DB_ALIAS in settings.DATABASES:
        return READ_DB_ALIAS
    return DEFAULT_DB_ALIAS
