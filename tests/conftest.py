"""Shared pytest fixtures and session-level DB setup."""
from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup: None, django_db_blocker: object) -> None:  # type: ignore[override]
    """Extend the default DB setup with the SampleModel table used in model tests."""
    with django_db_blocker.unblock():  # type: ignore[attr-defined]
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS base_samplemodel (
                    id VARCHAR(36) PRIMARY KEY NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    deleted_at DATETIME NULL DEFAULT NULL,
                    active BOOL NOT NULL DEFAULT 1,
                    name VARCHAR(100) NOT NULL DEFAULT 'test'
                )
            """)
