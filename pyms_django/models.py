"""Base Django models for pyms-django-chassis microservices.

Provides soft-delete support, UUID primary keys, and timestamp fields
via ``BaseModel`` and ``BaseModelReplicatedData``.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar

from django.db import models
from django.db.models import QuerySet


class SoftDeleteQuerySet(QuerySet["BaseModel"]):
    """QuerySet with soft-delete support.

    Overrides ``delete`` to mark records as inactive instead of removing them.
    """

    def delete(self) -> tuple[int, dict[str, int]]:  # type: ignore[override]
        """Soft-delete all records in the queryset.

        Sets ``active=False`` and records the deletion timestamp.

        Returns:
            Tuple of ``(count, {model_label: count})``.
        """
        count = self.update(active=False, deleted_at=datetime.now(UTC))
        return count, {self.model._meta.label: count}

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Permanently delete all records from the database.

        Returns:
            Tuple of ``(count, {model_label: count})``.
        """
        return super().delete()


class ActiveItemManager(models.Manager["BaseModel"]):
    """Manager that filters only active (non-deleted) records."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(active=True)


class BaseModel(models.Model):
    """Abstract base model with UUID PK, timestamps, and soft-delete support.

    All microservice models should inherit from this class.

    Attributes:
        id: UUID primary key, auto-generated on creation.
        created_at: Timestamp set automatically when the record is created.
        updated_at: Timestamp updated automatically on every save.
        deleted_at: Timestamp set when the record is soft-deleted; ``None`` otherwise.
        active: ``False`` when the record has been soft-deleted.
        objects: Manager returning only active records.
        all_objects: Unfiltered default manager.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    active = models.BooleanField(default=True)

    objects: ClassVar[ActiveItemManager] = ActiveItemManager()
    all_objects: ClassVar[models.Manager[BaseModel]] = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using: str | None = None, _keep_parents: bool = False) -> tuple[int, dict[str, int]]:  # type: ignore[override]
        """Soft-delete the record by marking it as inactive.

        Sets ``active=False`` and ``deleted_at`` to the current UTC time.
        The record remains in the database.

        Args:
            using: Database alias to use for the save operation.
            _keep_parents: Present for API compatibility; not used.

        Returns:
            Tuple of ``(1, {model_label: 1})``.
        """
        self.active = False
        self.deleted_at = datetime.now(UTC)
        self.save(update_fields=["active", "deleted_at", "updated_at"], using=using)
        return 1, {self._meta.label: 1}

    def restore(self) -> None:
        """Restore a previously soft-deleted record.

        Sets ``active=True`` and clears ``deleted_at``.
        """
        self.active = True
        self.deleted_at = None
        self.save(update_fields=["active", "deleted_at", "updated_at"])

    def hard_delete(self, using: str | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Permanently delete the record from the database.

        Args:
            using: Database alias.
            keep_parents: Whether to keep parent rows for multi-table inheritance.

        Returns:
            Tuple of ``(count, {model_label: count})``.
        """
        return super().delete(using=using, keep_parents=keep_parents)

    @classmethod
    def bulk_create(
        cls,
        objs: list[Any],
        batch_size: int | None = None,
        ignore_conflicts: bool = False,
        update_conflicts: bool = False,
        update_fields: list[str] | None = None,
        unique_fields: list[str] | None = None,
    ) -> list[Any]:
        """Bulk-create records, optionally emitting ``post_save`` signals.

        Wraps Django's ``bulk_create`` and fires ``post_save`` for each created
        instance when ``Meta.active_signals_bulk_operations`` is ``True``.

        Args:
            objs: List of model instances to create.
            batch_size: Number of records per database query.
            ignore_conflicts: Ignore uniqueness constraint violations.
            update_conflicts: Update conflicting rows instead of ignoring.
            update_fields: Fields to update on conflict (requires ``update_conflicts``).
            unique_fields: Fields used to detect conflicts.

        Returns:
            List of created model instances.
        """
        result = super().bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )
        if getattr(cls._meta, "active_signals_bulk_operations", False):
            from django.db.models.signals import post_save

            for obj in result:
                post_save.send(sender=cls, instance=obj, created=True)
        return result

    @classmethod
    def bulk_update(
        cls,
        objs: list[Any],
        fields: list[str],
        batch_size: int | None = None,
    ) -> int:
        """Bulk-update records, optionally emitting ``post_save`` signals.

        Wraps Django's ``bulk_update`` and fires ``post_save`` for each updated
        instance when ``Meta.active_signals_bulk_operations`` is ``True``.

        Args:
            objs: List of model instances to update.
            fields: Names of fields to update in the database.
            batch_size: Number of records per database query.

        Returns:
            Number of rows matched by the update.
        """
        result = super().bulk_update(objs, fields, batch_size=batch_size)
        if getattr(cls._meta, "active_signals_bulk_operations", False):
            from django.db.models.signals import post_save

            for obj in objs:
                post_save.send(sender=cls, instance=obj, created=False)
        return result


class BaseModelReplicatedData(BaseModel):
    """Abstract base model for records replicated from an external source.

    The ``id`` field has no default value; it must be provided explicitly
    (typically the UUID assigned by the upstream system).
    """

    id = models.UUIDField(primary_key=True, editable=False)

    class Meta:
        abstract = True
