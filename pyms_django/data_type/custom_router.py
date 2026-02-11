"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from typing import Any

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class ConfigViewSet(viewsets.ViewSet):
    """ViewSet for exposing service configuration."""

    @action(detail=False, methods=["get"])
    def config(self, request: Request) -> Response:
        """Return service configuration."""
        from django.conf import settings
        config_data: dict[str, Any] = {
            "service_name": getattr(settings, "SERVICE_NAME", "unknown"),
            "base_path": getattr(settings, "BASE_PATH", ""),
            "multitenant": getattr(settings, "MULTITENANT", False),
        }
        return Response(config_data)
