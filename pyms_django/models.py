"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar, Self

from django.db import models
from django.db.models import QuerySet


class SoftDeleteQuerySet(QuerySet["BaseModel"]):
    """QuerySet that performs soft delete instead of hard delete."""

    def delete(self) -> tuple[int, dict[str, int]]:  # type: ignore[override]
        """Soft delete all records in the queryset."""
        count = self.update(active=False, deleted_at=datetime.now(UTC))
        return count, {self.model._meta.label: count}

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Actually delete records from the database."""
        return super().delete()


class ActiveItemManager(models.Manager["BaseModel"]):
    """Manager that filters only active (non-deleted) records."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(active=True)


class BaseModel(models.Model):
    """
    Base model with UUID PK, timestamps, and soft delete support.
    All microservice models should inherit from this.
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

    def delete(self, using: str | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:  # type: ignore[override]
        """Soft delete: mark as inactive instead of removing from DB."""
        self.active = False
        self.deleted_at = datetime.now(UTC)
        self.save(update_fields=["active", "deleted_at", "updated_at"], using=using)
        return 1, {self._meta.label: 1}

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.active = True
        self.deleted_at = None
        self.save(update_fields=["active", "deleted_at", "updated_at"])

    def hard_delete(self, using: str | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Actually delete the record from the database."""
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
        """Override bulk_create to optionally send signals."""
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
        """Override bulk_update to optionally send signals."""
        result = super().bulk_update(objs, fields, batch_size=batch_size)
        if getattr(cls._meta, "active_signals_bulk_operations", False):
            from django.db.models.signals import post_save
            for obj in objs:
                post_save.send(sender=cls, instance=obj, created=False)
        return result


class BaseModelReplicatedData(BaseModel):
    """
    Base model for replicated data where the ID comes from an external source.
    The id field has no default value.
    """

    id = models.UUIDField(primary_key=True, editable=False)

    class Meta:
        abstract = True
