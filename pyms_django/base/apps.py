"""Django app configuration for the pyms-django-chassis base module."""

from __future__ import annotations

from django.apps import AppConfig


class BaseAppConfig(AppConfig):
    """App configuration for the base chassis module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pyms_django.base"
    verbose_name = "PyMS Django Base"
