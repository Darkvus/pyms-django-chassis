"""Tests for pyms_django.db.utils."""

from __future__ import annotations

from django.test import override_settings

from pyms_django.db.utils import DEFAULT_DB_ALIAS, READ_DB_ALIAS, get_read_db_alias


class TestGetReadDbAlias:
    @override_settings(ACTIVE_DATABASE_READ=False)
    def test_returns_default_when_disabled(self) -> None:
        assert get_read_db_alias() == DEFAULT_DB_ALIAS

    @override_settings(ACTIVE_DATABASE_READ=True, DATABASES={"default": {}, "read_db": {}})
    def test_returns_read_db_when_enabled_and_configured(self) -> None:
        assert get_read_db_alias() == READ_DB_ALIAS

    @override_settings(ACTIVE_DATABASE_READ=True, DATABASES={"default": {}})
    def test_returns_default_when_read_db_not_in_databases(self) -> None:
        assert get_read_db_alias() == DEFAULT_DB_ALIAS
