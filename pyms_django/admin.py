"""Django admin mixins and utilities for pyms-django-chassis."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet

logger = logging.getLogger(__name__)


class MigrateModelAdminMixin:
    """Admin mixin that adds a bulk tenant-migration action."""

    def migrate_data_to_other_tenant(
        self,
        request: HttpRequest,
        queryset: QuerySet[Any],
    ) -> HttpResponse | TemplateResponse:
        """Bulk admin action to copy selected records to another tenant schema.

        Displays a confirmation template on GET; on POST with ``apply``,
        copies the selected records to the target schema and resets the connection.

        Args:
            request: The current HTTP request.
            queryset: The queryset of selected objects.

        Returns:
            A ``TemplateResponse`` for the confirmation form, or an ``HttpResponse``
            redirect after migration.
        """
        if request.POST.get("apply"):
            target_schema = request.POST.get("target_schema", "")
            if target_schema:
                try:
                    from pyms_django.db.set_tenant_utils import set_tenant_schema
                    count = queryset.count()
                    objects = list(queryset)
                    set_tenant_schema(target_schema)
                    for obj in objects:
                        obj.pk = None
                        obj.save()
                    from pyms_django.db.set_tenant_utils import set_public_schema
                    set_public_schema()
                    self.message_user(request, f"Successfully migrated {count} records to {target_schema}")  # type: ignore[attr-defined]
                except Exception:
                    logger.exception("Failed to migrate data")
                    self.message_user(request, "Migration failed. Check logs.", level="error")  # type: ignore[attr-defined]
            return HttpResponse(status=302, headers={"Location": request.get_full_path()})
        return TemplateResponse(
            request,
            "admin/migrate_data_to_other_tenant.html",
            {"queryset": queryset, "action_name": "migrate_data_to_other_tenant"},
        )

    migrate_data_to_other_tenant.short_description = "Migrate data to other tenant"  # type: ignore[attr-defined]


try:
    from import_export.admin import ExportActionMixin, ImportMixin
    from import_export.resources import ModelResource

    class ImportExportActionMixin(ImportMixin, ExportActionMixin):  # type: ignore[misc]
        """Combined import/export admin mixin with bulk support."""
        pass

    def modelresource_factory(model: type[Model], **kwargs: object) -> type[ModelResource]:
        """Create a ``ModelResource`` subclass with bulk operations enabled.

        Args:
            model: The Django model class to create a resource for.
            **kwargs: Additional ``Meta`` attributes to set on the resource.

        Returns:
            A new ``ModelResource`` subclass with ``use_bulk=True``.
        """
        meta_attrs: dict[str, object] = {
            "model": model,
            "use_bulk": True,
            **kwargs,
        }
        meta = type("Meta", (), meta_attrs)
        return type(
            f"{model.__name__}Resource",
            (ModelResource,),
            {"Meta": meta},
        )

except ImportError:
    class ImportExportActionMixin:  # type: ignore[no-redef]
        """Fallback when django-import-export is not installed."""
        pass

    def modelresource_factory(_model: type[Model], **_kwargs: object) -> type:  # type: ignore[misc]
        """Raise ``ImportError`` because ``django-import-export`` is not installed.

        Args:
            _model: The Django model class.
            **_kwargs: Ignored.

        Raises:
            ImportError: Always, with installation instructions.
        """
        msg = "django-import-export is required. Install with: pip install pyms-django-chassis[import-export]"
        raise ImportError(msg)
