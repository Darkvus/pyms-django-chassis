"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

import logging
from typing import Any

from django.contrib import admin
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)


class MigrateModelAdminMixin:
    """Admin mixin for migrating data between tenants."""

    def migrate_data_to_other_tenant(
        self,
        request: HttpRequest,
        queryset: QuerySet[Any],
    ) -> HttpResponse | TemplateResponse:
        """Admin action to migrate selected records to another tenant."""
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

    def modelresource_factory(model: type[Model], **kwargs: Any) -> type[ModelResource]:
        """Factory to create ModelResource with use_bulk=True."""
        meta_attrs: dict[str, Any] = {
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

    def modelresource_factory(model: type[Model], **kwargs: Any) -> type:  # type: ignore[misc]
        """Fallback factory when django-import-export is not installed."""
        msg = "django-import-export is required. Install with: pip install pyms-django-chassis[import-export]"
        raise ImportError(msg)
