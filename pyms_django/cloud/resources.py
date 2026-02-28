"""Abstract cloud resource interfaces for pyms-django-chassis."""
from __future__ import annotations

from abc import ABC, abstractmethod


class SecretManagerResource(ABC):
    """Abstract base class for secret manager implementations."""

    @abstractmethod
    def get_secret(self, secret_key: str) -> str:
        """Retrieve a secret value by key.

        Args:
            secret_key: The identifier of the secret to retrieve.

        Returns:
            The plaintext secret value.

        Raises:
            KeyError: If the secret key does not exist.
        """
        ...
