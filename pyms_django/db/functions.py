"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from django.db.models import FloatField, Func


class Latitude(Func):  # type: ignore[type-arg]
    """Extract latitude from a PostGIS point field."""
    function = "ST_Y"
    output_field = FloatField()


class Longitude(Func):  # type: ignore[type-arg]
    """Extract longitude from a PostGIS point field."""
    function = "ST_X"
    output_field = FloatField()
