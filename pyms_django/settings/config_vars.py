"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

import os
from typing import Any, Final

SECRET_MANAGER_PREFIX: Final[str] = "ENC_"


class ConfigVars:
    """
    Configuration variable resolver.
    Variables prefixed with ENC_ are fetched from the cloud secret manager.
    Others are fetched from environment variables.
    """

    def __getattr__(self, name: str) -> str:
        if name.startswith(SECRET_MANAGER_PREFIX):
            return self._get_from_secret_manager(name)
        value = os.environ.get(name)
        if value is None:
            msg = f"Environment variable '{name}' not found"
            raise AttributeError(msg)
        return value

    def _get_from_secret_manager(self, name: str) -> str:
        """Fetch a secret from the configured cloud secret manager."""
        provider = os.environ.get("SECRET_MANAGER_PROVIDER", "AWS").upper()
        if provider == "AWS":
            from pyms_django.cloud.aws.secret_manager import AwsSecretManager
            manager = AwsSecretManager()
            secret_key = name[len(SECRET_MANAGER_PREFIX):]
            return manager.get_secret(secret_key)
        msg = f"Unsupported secret manager provider: {provider}"
        raise ValueError(msg)


config: Final[ConfigVars] = ConfigVars()
