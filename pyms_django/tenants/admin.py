"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from django.contrib import admin

try:
    from pyms_django.tenants.models import Domain, Tenant

    @admin.register(Tenant)
    class TenantAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
        """Admin for Tenant model."""

        list_display = ("name", "schema_name", "created_at", "active")
        list_filter = ("active",)
        search_fields = ("name", "schema_name")

    @admin.register(Domain)
    class DomainAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
        """Admin for Domain model."""

        list_display = ("domain", "tenant", "is_primary", "created_at")
        list_filter = ("is_primary",)
        search_fields = ("domain",)

except ImportError:
    pass
