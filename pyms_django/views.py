"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
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
    """Returns the service version."""

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []

    def get(self, request: Request) -> Response:
        """Return the current artifact version."""
        return Response({"version": getattr(settings, "ARTIFACT_VERSION", "unknown")})


class DependenciesTreeView(APIView):
    """Returns the dependency tree from pyproject.toml."""

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []

    def get(self, request: Request) -> Response:
        """Read and return the project dependencies."""
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
    """
    ModelViewSet that uses RestQL for dynamic field selection
    when a 'query' parameter is present.
    """

    def get_serializer_class(self) -> type:
        """Return RestQL-enabled serializer if query param is present."""
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
