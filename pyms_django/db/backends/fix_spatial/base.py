"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from django.contrib.gis.db.backends.spatialite.base import DatabaseWrapper as SpatialiteDatabaseWrapper

    class DatabaseWrapper(SpatialiteDatabaseWrapper):
        """
        Fix for Spatialite v5.0+ compatibility.
        Handles the changed initialization function name.
        """

        def prepare_database(self) -> None:
            """Initialize Spatialite with compatibility for v5.0+."""
            super().prepare_database()
            try:
                with self.cursor() as cursor:
                    cursor.execute("SELECT InitSpatialMetaData(1);")
            except Exception:
                try:
                    with self.cursor() as cursor:
                        cursor.execute("SELECT InitSpatialMetaDataFull(1);")
                except Exception:
                    logger.debug("Spatialite metadata already initialized or not available")
except ImportError:
    pass
