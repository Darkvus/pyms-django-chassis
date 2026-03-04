"""Tests for pyms_django BaseModel (soft-delete, restore, managers)."""
from __future__ import annotations

import uuid

import pytest
from django.db import models

from pyms_django.models import BaseModel, BaseModelReplicatedData


# Concrete model for testing (uses in-memory SQLite via test settings)
class SampleModel(BaseModel):
    name = models.CharField(max_length=100, default="test")

    class Meta:
        app_label = "base"



@pytest.mark.django_db
class TestBaseModelSoftDelete:
    def _create(self, name: str = "item") -> SampleModel:
        obj = SampleModel(name=name)
        obj.id = uuid.uuid4()
        obj.save()
        return obj

    def test_delete_sets_active_false(self) -> None:
        obj = self._create()
        obj.delete()
        obj.refresh_from_db()
        assert obj.active is False

    def test_delete_sets_deleted_at(self) -> None:
        obj = self._create()
        obj.delete()
        obj.refresh_from_db()
        assert obj.deleted_at is not None

    def test_restore_sets_active_true(self) -> None:
        obj = self._create()
        obj.delete()
        obj.restore()
        obj.refresh_from_db()
        assert obj.active is True
        assert obj.deleted_at is None

    def test_hard_delete_removes_record(self) -> None:
        obj = self._create()
        pk = obj.pk
        obj.hard_delete()
        assert not SampleModel.all_objects.filter(pk=pk).exists()

    def test_objects_manager_excludes_inactive(self) -> None:
        active = self._create("active")
        deleted = self._create("deleted")
        deleted.delete()
        pks = list(SampleModel.objects.values_list("pk", flat=True))
        assert active.pk in pks
        assert deleted.pk not in pks

    def test_all_objects_includes_inactive(self) -> None:
        active = self._create("active2")
        deleted = self._create("deleted2")
        deleted.delete()
        pks = list(SampleModel.all_objects.values_list("pk", flat=True))
        assert active.pk in pks
        assert deleted.pk in pks

    def test_delete_returns_tuple(self) -> None:
        obj = self._create()
        result = obj.delete()
        assert result == (1, {"base.SampleModel": 1})


@pytest.mark.django_db
class TestSoftDeleteQuerySet:
    def test_queryset_delete_soft_deletes_all(self) -> None:
        for _ in range(3):
            obj = SampleModel(name="qs")
            obj.id = uuid.uuid4()
            obj.save()

        count, info = SampleModel.objects.filter(name="qs").delete()
        assert count == 3
        assert SampleModel.all_objects.filter(name="qs", active=False).count() == 3

    def test_hard_delete_removes_all(self) -> None:
        for _ in range(2):
            obj = SampleModel(name="hard")
            obj.id = uuid.uuid4()
            obj.save()

        SampleModel.objects.filter(name="hard").hard_delete()
        assert SampleModel.all_objects.filter(name="hard").count() == 0


class TestBaseModelReplicatedData:
    def test_id_has_no_default(self) -> None:
        field = BaseModelReplicatedData._meta.get_field("id")
        assert not field.has_default()
