"""AWS Secrets Manager integration for pyms-django-chassis."""
from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any, Final

from pyms_django.cloud.resources import SecretManagerResource

logger = logging.getLogger(__name__)

AWS_ERROR_CODES: Final[dict[str, str]] = {
    "ResourceNotFoundException": "The requested secret was not found",
    "InvalidRequestException": "The request was invalid",
    "InvalidParameterException": "The parameter is invalid",
    "DecryptionFailure": "The secret cannot be decrypted",
    "InternalServiceError": "An internal service error occurred",
}


class AwsSecretManager(SecretManagerResource):
    """Secrets Manager client that caches the secret bundle in memory.

    Reads ``AWS_REGION`` and ``AWS_SECRET_NAME`` from the environment.
    The boto3 client is created lazily on the first request.
    """

    def __init__(self) -> None:
        self._region: str = os.environ.get("AWS_REGION", "us-east-1")
        self._secret_name: str = os.environ.get("AWS_SECRET_NAME", "")
        self._client: Any = None
        self._cache: dict[str, dict[str, str]] = {}

    def _get_client(self) -> Any:  # noqa: ANN401
        """Return the boto3 Secrets Manager client, creating it if necessary.

        Returns:
            A boto3 ``secretsmanager`` client.
        """
        if self._client is None:
            import boto3
            self._client = boto3.client(
                service_name="secretsmanager",
                region_name=self._region,
            )
        return self._client

    def _fetch_secret_bundle(self) -> dict[str, str]:
        """Fetch the full secret bundle from AWS, caching the result.

        Returns:
            Dictionary mapping secret keys to their values.

        Raises:
            botocore.exceptions.ClientError: If the AWS request fails.
            ValueError: If the response contains neither ``SecretString`` nor ``SecretBinary``.
        """
        if self._secret_name in self._cache:
            return self._cache[self._secret_name]

        client = self._get_client()
        try:
            response = client.get_secret_value(SecretId=self._secret_name)
        except client.exceptions.ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = AWS_ERROR_CODES.get(error_code, f"Unknown error: {error_code}")
            logger.error("AWS Secrets Manager error: %s - %s", error_code, error_msg)
            raise

        if "SecretString" in response:
            secret_data: dict[str, str] = json.loads(response["SecretString"])
        elif "SecretBinary" in response:
            decoded = base64.b64decode(response["SecretBinary"]).decode("utf-8")
            secret_data = json.loads(decoded)
        else:
            msg = "Secret response contains neither SecretString nor SecretBinary"
            raise ValueError(msg)

        self._cache[self._secret_name] = secret_data
        return secret_data

    def get_secret(self, secret_key: str) -> str:
        """Retrieve a specific secret value from the bundle.

        Args:
            secret_key: Key within the secret JSON bundle.

        Returns:
            The plaintext value for *secret_key*.

        Raises:
            KeyError: If *secret_key* is absent from the secret bundle.
            botocore.exceptions.ClientError: If the AWS request fails.
        """
        secrets = self._fetch_secret_bundle()
        if secret_key not in secrets:
            msg = f"Secret key '{secret_key}' not found in secret '{self._secret_name}'"
            raise KeyError(msg)
        return secrets[secret_key]
