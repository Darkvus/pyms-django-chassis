"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from typing import Final

from django.conf import settings

HEADER_USER_ID: Final[str] = "User-Id"
HEADER_APP_ID: Final[str] = "App-Id"


def get_user_id_from_request(request: object) -> str | None:
    """Extract the User-Id from request headers."""
    header_name = getattr(settings, "HEADER_USER_ID", HEADER_USER_ID)
    meta_key = f"HTTP_{header_name.upper().replace('-', '_')}"
    return getattr(request, "META", {}).get(meta_key)


def get_app_id_from_request(request: object) -> str | None:
    """Extract the App-Id from request headers."""
    header_name = getattr(settings, "HEADER_APP_ID", HEADER_APP_ID)
    meta_key = f"HTTP_{header_name.upper().replace('-', '_')}"
    return getattr(request, "META", {}).get(meta_key)
