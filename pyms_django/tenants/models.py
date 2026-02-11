"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from django.db import models

from pyms_django.models import BaseModel

try:
    from django_tenants.models import DomainMixin, TenantMixin

    class Tenant(TenantMixin, BaseModel):  # type: ignore[misc]
        """Multi-tenant model using PostgreSQL schemas."""

        name = models.CharField(max_length=100)
        description = models.TextField(blank=True, default="")
        auto_create_schema = True
        auto_drop_schema = False

        class Meta:
            ordering = ["name"]

        def __str__(self) -> str:
            return str(self.name)

    class Domain(DomainMixin, BaseModel):  # type: ignore[misc]
        """Domain model for tenant routing."""

        class Meta:
            ordering = ["domain"]

        def __str__(self) -> str:
            return str(self.domain)

except ImportError:
    pass
