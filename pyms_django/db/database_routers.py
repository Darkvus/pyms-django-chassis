"""Database router for directing reads to a read replica in pyms-django-chassis."""
from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from django.db.models import Model


class ReadWriteRouter:
    """Database router that directs reads to read_db and writes to default."""

    def db_for_read(self, _model: type[Model], **_hints: object) -> str:
        """Return the database alias to use for read operations.

        Args:
            _model: The Django model class being queried.
            **_hints: Routing hints from the ORM.

        Returns:
            ``"read_db"`` when ``ACTIVE_DATABASE_READ`` is enabled, otherwise ``"default"``.
        """
        if getattr(settings, "ACTIVE_DATABASE_READ", False):
            return "read_db"
        return "default"

    def db_for_write(self, _model: type[Model], **_hints: object) -> str:
        """Return the database alias to use for write operations.

        Args:
            _model: The Django model class being written.
            **_hints: Routing hints from the ORM.

        Returns:
            Always ``"default"``.
        """
        return "default"

    def allow_relation(self, _obj1: Model, _obj2: Model, **_hints: object) -> bool:
        """Indicate whether a relation between two objects is permitted.

        Args:
            _obj1: First model instance.
            _obj2: Second model instance.
            **_hints: Routing hints from the ORM.

        Returns:
            ``True`` to allow all cross-database relations.
        """
        return True

    def allow_migrate(self, db: str, _app_label: str, _model_name: str | None = None, **_hints: object) -> bool:
        """Indicate whether a migration should run on the given database.

        Args:
            db: Target database alias.
            _app_label: Label of the Django app being migrated.
            _model_name: Optional name of the model being migrated.
            **_hints: Additional routing hints.

        Returns:
            ``True`` only when *db* is ``"default"``.
        """
        return db == "default"
