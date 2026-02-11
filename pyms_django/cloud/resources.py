"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class SecretManagerResource(ABC):
    """Abstract base class for secret manager implementations."""

    @abstractmethod
    def get_secret(self, secret_key: str) -> str:
        """Retrieve a secret value by its key."""
        ...
