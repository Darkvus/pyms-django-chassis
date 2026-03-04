"""Router utilities for pyms-django-chassis microservices.

Provides ``ChassisRouter`` and ``ConfigViewSet`` for registering versioned
DRF viewsets with a common prefix and optional sub-prefix support.
"""
from __future__ import annotations

from typing import TypeVar

from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import GenericViewSet

T_GenericViewSet = TypeVar("T_GenericViewSet", bound=GenericViewSet)


class ConfigViewSet:
    """Configuration holder for registering a viewset in ``ChassisRouter``.

    Attributes:
        viewset: The ViewSet class to register.
        basename: Base name used for URL reversing.
        version: API version prefix (e.g. ``"v1"``).
        prefix_detail: If ``True``, wraps the prefix in a detail URL pattern.
        sub_prefix: Optional additional path segment appended after the main prefix.
    """

    viewset: type[T_GenericViewSet]
    basename: str
    version: str
    prefix_detail: bool = False
    sub_prefix: str | None

    def __init__(
        self,
        viewset: type[T_GenericViewSet],
        basename: str,
        version: str = settings.API_VERSION,
        prefix_detail: bool = False,
        sub_prefix: str | None = None,
    ) -> None:
        """Initialize ``ConfigViewSet``.

        Args:
            viewset: The ViewSet class to register.
            basename: Base name used for URL reversing.
            version: API version prefix. Defaults to ``settings.API_VERSION``.
            prefix_detail: If ``True``, wraps the prefix in a detail URL pattern.
            sub_prefix: Optional additional path segment appended after the main prefix.
        """

        self.viewset = viewset
        self.basename = basename
        self.version = version
        self.prefix_detail = prefix_detail
        self.sub_prefix = sub_prefix


class ChassisRouter(DefaultRouter):
    """Default router for chassis-based microservices."""

    routes = DefaultRouter.routes
    extra_routes = []

    def __init__(self, common_prefix: str = "", *args: object, **kwargs: object) -> None:
        """Initialize ``ChassisRouter`` with an optional common prefix.

        Args:
            common_prefix: Shared path segment prepended to all registered routes.
            *args: Positional arguments forwarded to ``DefaultRouter``.
            **kwargs: Keyword arguments forwarded to ``DefaultRouter``.
        """

        self.common_prefix = common_prefix
        super().__init__(*args, **kwargs)

    def register(
        self,
        prefix: str,
        viewset: type[T_GenericViewSet],
        version: str = settings.API_VERSION,
        sub_prefix: str | None = None,
        basename: str | None = None,
        **kwargs: object,
    ) -> None:
        """Register a viewset with a versioned and prefixed URL.

        Builds the full URL pattern as ``{version}/{common_prefix}/{prefix}/{sub_prefix}``
        and delegates to ``DefaultRouter.register``.

        Args:
            prefix: Resource-specific URL segment.
            viewset: The ViewSet class to register.
            version: API version prefix. Defaults to ``settings.API_VERSION``.
            sub_prefix: Optional additional path segment appended after prefix.
            basename: Base name for URL reversing. Inferred from the viewset if not provided.
            **kwargs: Additional arguments forwarded to ``DefaultRouter.register``.
        """

        modified_prefix = (
            f"{version}/{self.common_prefix}/{prefix}"
            if self.common_prefix
            else f"{version}/{prefix}"
        )

        if sub_prefix:
            modified_prefix += f"/{sub_prefix}"

        super().register(modified_prefix, viewset, basename, **kwargs)

    def register_multiple_viewsets(
        self, prefix: str, config_viewsets: list[ConfigViewSet], **kwargs: object,
    ) -> None:
        """Register multiple viewsets sharing the same URL prefix.

        Args:
            prefix: Shared resource URL segment.
            config_viewsets: List of ``ConfigViewSet`` instances to register.
            **kwargs: Additional arguments forwarded to each ``register`` call.

        Example:
            ::

                router = ChassisRouter(common_prefix="example")
                router.register_multiple_viewsets(
                    r"examples",
                    [
                        ConfigViewSet(viewset=ListExampleViewSet, basename="list-example"),
                        ConfigViewSet(viewset=DeleteExampleViewSet, basename="delete_example"),
                        ConfigViewSet(
                            viewset=UpdateExampleViewSet,
                            basename="update_example",
                            prefix_detail=True,
                            sub_prefix="update",
                        ),
                    ],
                )
        """

        for element in config_viewsets:
            modify_prefix = prefix
            if element.prefix_detail:
                modify_prefix = f"{prefix}/(?P<id>[^/.]+)"
            self.register(
                modify_prefix,
                element.viewset,
                element.version,
                element.sub_prefix,
                element.basename,
                **kwargs,
            )

    def get_routes(self, viewset: object) -> list[object]:
        """Return the combined route list for a given viewset.

        Prepends any custom routes defined on the viewset before the default routes.

        Args:
            viewset: The ViewSet class whose routes are resolved.

        Returns:
            Combined list of ``Route`` objects for the viewset.
        """

        self.routes = DefaultRouter.routes

        if hasattr(viewset, "routes"):
            self.routes = viewset.routes + self.routes

        return super().get_routes(viewset)
