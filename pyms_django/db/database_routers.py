"""Database router for directing reads to a read replica in pyms-django-chassis."""
from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db.models import Model


class ReadWriteRouter:
    """Database router that directs reads to read_db and writes to default."""

    def db_for_read(self, model: type[Model], **hints: Any) -> str:
        """Return the database alias to use for read operations.

        Args:
            model: The Django model class being queried.
            **hints: Routing hints from the ORM.

        Returns:
            ``"read_db"`` when ``ACTIVE_DATABASE_READ`` is enabled, otherwise ``"default"``.
        """
        if getattr(settings, "ACTIVE_DATABASE_READ", False):
            return "read_db"
        return "default"

    def db_for_write(self, model: type[Model], **hints: Any) -> str:
        """Return the database alias to use for write operations.

        Args:
            model: The Django model class being written.
            **hints: Routing hints from the ORM.

        Returns:
            Always ``"default"``.
        """
        return "default"

    def allow_relation(self, obj1: Model, obj2: Model, **hints: Any) -> bool:
        """Indicate whether a relation between two objects is permitted.

        Args:
            obj1: First model instance.
            obj2: Second model instance.
            **hints: Routing hints from the ORM.

        Returns:
            ``True`` to allow all cross-database relations.
        """
        return True

    def allow_migrate(self, db: str, app_label: str, model_name: str | None = None, **hints: Any) -> bool:
        """Indicate whether a migration should run on the given database.

        Args:
            db: Target database alias.
            app_label: Label of the Django app being migrated.
            model_name: Optional name of the model being migrated.
            **hints: Additional routing hints.

        Returns:
            ``True`` only when *db* is ``"default"``.
        """
        return db == "default"
