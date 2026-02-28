"""Custom PostGIS database functions for pyms-django-chassis."""
from __future__ import annotations

from django.db.models import FloatField, Func


class Latitude(Func):  # type: ignore[type-arg]
    """Database function that extracts the latitude from a PostGIS point.

    Maps to the PostGIS ``ST_Y`` function.
    """
    function = "ST_Y"
    output_field = FloatField()


class Longitude(Func):  # type: ignore[type-arg]
    """Database function that extracts the longitude from a PostGIS point.

    Maps to the PostGIS ``ST_X`` function.
    """
    function = "ST_X"
    output_field = FloatField()
