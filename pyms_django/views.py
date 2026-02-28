"""API views for service metadata endpoints in pyms-django-chassis."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import toml
from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class VersioningView(APIView):
    """View that returns the current service artifact version."""

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []

    def get(self, request: Request) -> Response:
        """Return the artifact version.

        Args:
            request: Incoming HTTP request.

        Returns:
            JSON response with ``{"version": "<artifact_version>"}``.
        """
        return Response({"version": getattr(settings, "ARTIFACT_VERSION", "unknown")})


class DependenciesTreeView(APIView):
    """View that returns the project dependency list from ``pyproject.toml``."""

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []

    def get(self, request: Request) -> Response:
        """Return the list of project dependencies.

        Args:
            request: Incoming HTTP request.

        Returns:
            JSON response with ``{"dependencies": [...]}``, or an empty dict on error.
        """
        pyproject_path = Path.cwd() / "pyproject.toml"
        if not pyproject_path.exists():
            return Response({"dependencies": {}})
        try:
            data = toml.load(pyproject_path)
            deps = data.get("project", {}).get("dependencies", [])
            return Response({"dependencies": deps})
        except Exception:
            logger.exception("Failed to read pyproject.toml")
            return Response({"dependencies": {}})


class RestQlModelViewSet(viewsets.ModelViewSet):  # type: ignore[type-arg]
    """``ModelViewSet`` that enables RestQL field filtering via a ``query`` param.

    Falls back to the base serializer class when ``django-restql`` is not
    installed or when no ``query`` parameter is present in the request.
    """

    def get_serializer_class(self) -> type:
        """Return a RestQL-enhanced serializer class when appropriate.

        Returns:
            A subclass of the base serializer with ``DynamicFieldsMixin`` mixed in
            when ``django-restql`` is available and a ``query`` param is present,
            otherwise the base serializer class.
        """
        base_class = super().get_serializer_class()
        if "query" in self.request.query_params:
            try:
                from django_restql.mixins import DynamicFieldsMixin

                if not issubclass(base_class, DynamicFieldsMixin):
                    return type(
                        f"RestQL{base_class.__name__}",
                        (DynamicFieldsMixin, base_class),
                        {},
                    )
            except ImportError:
                pass
        return base_class
