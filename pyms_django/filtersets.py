"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from django_filters import FilterSet


class BaseFilterSet(FilterSet):
    """Base FilterSet that all microservice filtersets should inherit from."""

    class Meta:
        abstract = True
