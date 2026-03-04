"""Typed dict definitions for pyms-django-chassis configuration settings."""

from __future__ import annotations

from typing import TypedDict


class DisabledPayloadSettings(TypedDict, total=False):
    """Typed dict for disabling payload logging on specific endpoints.

    Keys are endpoint paths and values are lists of field names to mask.
    """

    # Key: endpoint path, Value: list of field names to mask


class DatabaseSettings(TypedDict, total=False):
    """Typed dict for Django database connection settings."""

    ENGINE: str
    NAME: str
    USER: str
    PASSWORD: str
    HOST: str
    PORT: str


class MetricsSettings(TypedDict, total=False):
    """Typed dict for OpenTelemetry metrics configuration."""

    collector_url: str
    export_interval_ms: int
    export_timeout_ms: int
