"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def set_tenant_schema(schema_name: str) -> None:
    """Set the PostgreSQL search_path to the given tenant schema."""
    try:
        from django.db import connection
        connection.set_schema(schema_name)
        logger.debug("Tenant schema set to: %s", schema_name)
    except Exception:
        logger.exception("Failed to set tenant schema: %s", schema_name)
        raise


def set_public_schema() -> None:
    """Reset the PostgreSQL search_path to the public schema."""
    set_tenant_schema("public")
