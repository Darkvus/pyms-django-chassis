"""Built-in configuration ViewSet for pyms-django-chassis."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

if TYPE_CHECKING:
    from rest_framework.request import Request


class ConfigViewSet(viewsets.ViewSet):
    """ViewSet that exposes basic service configuration information."""

    @action(detail=False, methods=["get"])
    def config(self, _request: Request) -> Response:
        """Return the service configuration.

        Args:
            _request: Incoming HTTP request.

        Returns:
            JSON response with ``service_name``, ``base_path``, and ``multitenant``.
        """
        from django.conf import settings
        config_data: dict[str, Any] = {
            "service_name": getattr(settings, "SERVICE_NAME", "unknown"),
            "base_path": getattr(settings, "BASE_PATH", ""),
            "multitenant": getattr(settings, "MULTITENANT", False),
        }
        return Response(config_data)
