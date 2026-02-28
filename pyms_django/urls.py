"""Default URL configuration for pyms-django-chassis.

Registers health-check, version, dependencies, and optionally
schema (drf-spectacular), admin, and debug toolbar endpoints.
"""
from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.urls import URLPattern, URLResolver, include, path

from pyms_django.views import DependenciesTreeView, VersioningView


def build_path(route: str) -> str:
    """Prepend ``BASE_PATH`` to a route string.

    Args:
        route: Relative URL route to prefix.

    Returns:
        Full path string with ``BASE_PATH`` prepended, always ending with ``/``.
    """
    base = getattr(settings, "BASE_PATH", "").strip("/")
    route = route.strip("/")
    if base and route:
        return f"{base}/{route}/"
    if base:
        return f"{base}/"
    if route:
        return f"{route}/"
    return ""


def health_check(request: HttpRequest) -> HttpResponse:
    """Respond with HTTP 200 OK for liveness probes.

    Args:
        request: Incoming HTTP request.

    Returns:
        Plain-text ``HttpResponse`` with body ``"OK"``.
    """
    return HttpResponse("OK")


urlpatterns: list[URLPattern | URLResolver] = [
    path(build_path("health-check"), health_check, name="health-check"),
    path(build_path("version"), VersioningView.as_view(), name="version"),
    path(build_path("dependencies"), DependenciesTreeView.as_view(), name="dependencies"),
]

# Add drf-spectacular URLs
try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path(build_path("schema"), SpectacularAPIView.as_view(), name="schema"),
        path(build_path(""), SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path(build_path("redoc"), SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
except ImportError:
    pass

# Register LOCAL_APPS URLs dynamically
local_apps: list[tuple[str, str]] = getattr(settings, "LOCAL_APPS", [])
for app_urls, app_base_path in local_apps:
    urlpatterns.append(path(app_base_path.strip("/") + "/", include(app_urls)))

# Conditional admin
if getattr(settings, "ADMIN_ENABLED", False):
    from django.contrib import admin
    urlpatterns.append(path(build_path("admin"), admin.site.urls))

# Conditional debug toolbar
if getattr(settings, "DEBUG", False):
    try:
        import debug_toolbar
        urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    except ImportError:
        pass
