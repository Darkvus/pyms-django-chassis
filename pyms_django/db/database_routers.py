"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db.models import Model


class ReadWriteRouter:
    """Database router that directs reads to read_db and writes to default."""

    def db_for_read(self, model: type[Model], **hints: Any) -> str:
        """Route read operations to the read replica if available."""
        if getattr(settings, "ACTIVE_DATABASE_READ", False):
            return "read_db"
        return "default"

    def db_for_write(self, model: type[Model], **hints: Any) -> str:
        """Route write operations to the default database."""
        return "default"

    def allow_relation(self, obj1: Model, obj2: Model, **hints: Any) -> bool:
        """Allow relations between objects in default and read_db."""
        return True

    def allow_migrate(self, db: str, app_label: str, model_name: str | None = None, **hints: Any) -> bool:
        """Only allow migrations on the default database."""
        return db == "default"
