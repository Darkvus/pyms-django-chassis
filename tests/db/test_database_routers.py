"""Tests for pyms_django.db.database_routers."""
from __future__ import annotations

from unittest.mock import MagicMock

from django.test import override_settings

from pyms_django.db.database_routers import ReadWriteRouter


class TestReadWriteRouter:
    def setup_method(self) -> None:
        self.router = ReadWriteRouter()
        self.model = MagicMock()

    @override_settings(ACTIVE_DATABASE_READ=False)
    def test_db_for_read_returns_default_when_read_disabled(self) -> None:
        assert self.router.db_for_read(self.model) == "default"

    @override_settings(ACTIVE_DATABASE_READ=True)
    def test_db_for_read_returns_read_db_when_enabled(self) -> None:
        assert self.router.db_for_read(self.model) == "read_db"

    def test_db_for_write_always_returns_default(self) -> None:
        assert self.router.db_for_write(self.model) == "default"

    def test_allow_relation_always_true(self) -> None:
        obj1, obj2 = MagicMock(), MagicMock()
        assert self.router.allow_relation(obj1, obj2) is True

    def test_allow_migrate_true_for_default(self) -> None:
        assert self.router.allow_migrate("default", "myapp") is True

    def test_allow_migrate_false_for_read_db(self) -> None:
        assert self.router.allow_migrate("read_db", "myapp") is False

    def test_allow_migrate_false_for_other_db(self) -> None:
        assert self.router.allow_migrate("other", "myapp") is False
