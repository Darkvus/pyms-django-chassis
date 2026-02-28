"""Django app configuration for the pyms-django-chassis tenants module."""
from __future__ import annotations

from django.apps import AppConfig


class TenantAppConfig(AppConfig):
    """App configuration for the tenants module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pyms_django.tenants"
    verbose_name = "Tenants"
