"""Tenant schema switching utilities for pyms-django-chassis."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def set_tenant_schema(schema_name: str) -> None:
    """Switch the active PostgreSQL schema for the current connection.

    Args:
        schema_name: Name of the schema to activate.

    Raises:
        Exception: Re-raises any error raised by ``connection.set_schema``.
    """
    try:
        from django.db import connection

        connection.set_schema(schema_name)
        logger.debug("Tenant schema set to: %s", schema_name)
    except Exception:
        logger.exception("Failed to set tenant schema: %s", schema_name)
        raise


def set_public_schema() -> None:
    """Reset the active PostgreSQL schema to ``public``."""
    set_tenant_schema("public")
