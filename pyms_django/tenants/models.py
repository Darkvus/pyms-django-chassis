"""Multi-tenant Django models for pyms-django-chassis."""

from __future__ import annotations

from django.db import models

from pyms_django.models import BaseModel

try:
    from django_tenants.models import DomainMixin, TenantMixin

    class Tenant(TenantMixin, BaseModel):  # type: ignore[misc]
        """Tenant model that maps to a dedicated PostgreSQL schema."""

        name = models.CharField(max_length=100)
        description = models.TextField(blank=True, default="")
        auto_create_schema = True
        auto_drop_schema = False

        class Meta:
            ordering = ["name"]

        def __str__(self) -> str:
            return str(self.name)

    class Domain(DomainMixin, BaseModel):  # type: ignore[misc]
        """Domain name model used to route requests to a tenant."""

        class Meta:
            ordering = ["domain"]

        def __str__(self) -> str:
            return str(self.domain)

except ImportError:
    pass
