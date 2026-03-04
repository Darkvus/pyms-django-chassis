"""Base FilterSet for pyms-django-chassis microservices."""

from __future__ import annotations

from django_filters import FilterSet


class BaseFilterSet(FilterSet):
    """Base FilterSet that all microservice filtersets should inherit from."""

    class Meta:
        abstract = True
