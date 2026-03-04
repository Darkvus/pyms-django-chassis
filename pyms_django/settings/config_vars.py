"""Environment and cloud secret manager variable resolver for pyms-django-chassis."""
from __future__ import annotations

import os
from typing import Final

SECRET_MANAGER_PREFIX: Final[str] = "ENC_"


class ConfigVars:
    """Resolver for environment and cloud secret manager variables.

    Attributes starting with ``ENC_`` are fetched from the cloud secret
    manager; all other attributes are read from environment variables.
    """

    def __getattr__(self, name: str) -> str:
        """Resolve a configuration variable by name.

        Args:
            name: Variable name. Prefix with ``ENC_`` to fetch from the secret manager.

        Returns:
            The resolved string value.

        Raises:
            AttributeError: If a non-prefixed variable is absent from the environment.
        """
        if name.startswith(SECRET_MANAGER_PREFIX):
            return self._get_from_secret_manager(name)
        value = os.environ.get(name)
        if value is None:
            msg = f"Environment variable '{name}' not found"
            raise AttributeError(msg)
        return value

    def _get_from_secret_manager(self, name: str) -> str:
        """Fetch a secret from the configured cloud provider.

        Args:
            name: Full variable name including the ``ENC_`` prefix.

        Returns:
            The plaintext secret value.

        Raises:
            ValueError: If ``SECRET_MANAGER_PROVIDER`` is set to an unsupported value.
        """
        provider = os.environ.get("SECRET_MANAGER_PROVIDER", "AWS").upper()
        if provider == "AWS":
            from pyms_django.cloud.aws.secret_manager import AwsSecretManager
            manager = AwsSecretManager()
            secret_key = name[len(SECRET_MANAGER_PREFIX):]
            return manager.get_secret(secret_key)
        msg = f"Unsupported secret manager provider: {provider}"
        raise ValueError(msg)


config: Final[ConfigVars] = ConfigVars()
