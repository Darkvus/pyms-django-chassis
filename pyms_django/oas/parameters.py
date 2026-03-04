"""Reusable OpenAPI parameter definitions for pyms-django-chassis."""
from __future__ import annotations

from typing import Any, Final

HEADER_USER_ID_PARAM: Final[dict[str, Any]] = {
    "name": "User-Id",
    "in": "header",
    "required": False,
    "schema": {"type": "string", "format": "uuid"},
    "description": "UUID of the authenticated user",
}

