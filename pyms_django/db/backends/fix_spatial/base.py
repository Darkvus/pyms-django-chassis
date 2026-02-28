"""Spatialite backend compatibility fix for pyms-django-chassis."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from django.contrib.gis.db.backends.spatialite.base import DatabaseWrapper as SpatialiteDatabaseWrapper

    class DatabaseWrapper(SpatialiteDatabaseWrapper):
        """Spatialite database wrapper compatible with v5.0 and later.

        Overrides ``prepare_database`` to handle the renamed initialisation
        function introduced in Spatialite 5.0.
        """

        def prepare_database(self) -> None:
            """Initialise Spatialite metadata with v5.0+ compatibility.

            Tries ``InitSpatialMetaData(1)`` first, falling back to
            ``InitSpatialMetaDataFull(1)`` if that raises an error.
            """
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
