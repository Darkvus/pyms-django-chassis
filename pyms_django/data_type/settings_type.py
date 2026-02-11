"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from typing import TypedDict


class DisabledPayloadSettings(TypedDict, total=False):
    """Settings for disabling payload logging per endpoint."""
    # Key: endpoint path, Value: list of field names to mask


class DatabaseSettings(TypedDict, total=False):
    """Database connection settings."""
    ENGINE: str
    NAME: str
    USER: str
    PASSWORD: str
    HOST: str
    PORT: str


class MetricsSettings(TypedDict, total=False):
    """Metrics configuration settings."""
    collector_url: str
    export_interval_ms: int
    export_timeout_ms: int
