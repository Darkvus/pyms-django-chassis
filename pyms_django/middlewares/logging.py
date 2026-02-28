"""Request logging and OpenTelemetry metrics middleware for pyms-django-chassis."""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from collections.abc import Callable
from typing import Any, Final

from django.conf import settings
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

EXCLUDED_PATHS: Final[list[str]] = [
    "health-check",
    "version",
    "redoc",
    "static",
    "dependencies",
]


def _get_counter() -> Any:
    """Create an OpenTelemetry HTTP response status counter, or return ``None``.

    Returns:
        An OpenTelemetry ``Counter`` instrument, or ``None`` if the SDK is not installed.
    """
    try:
        from opentelemetry import metrics
        meter = metrics.get_meter(__name__)
        return meter.create_counter(
            name="microservice_http_response_status",
            description="HTTP response status counter",
        )
    except ImportError:
        return None


def _get_histogram() -> Any:
    """Create an OpenTelemetry HTTP request latency histogram, or return ``None``.

    Returns:
        An OpenTelemetry ``Histogram`` instrument, or ``None`` if the SDK is not installed.
    """
    try:
        from opentelemetry import metrics
        meter = metrics.get_meter(__name__)
        return meter.create_histogram(
            name="microservice_http_request_latency",
            description="HTTP request latency in milliseconds",
            unit="ms",
        )
    except ImportError:
        return None


class RequestLoggingMiddleware:
    """Middleware that logs requests/responses and records OpenTelemetry metrics."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self._counter = _get_counter()
        self._histogram = _get_histogram()

    def _should_skip(self, path: str) -> bool:
        """Return ``True`` if the request path should be excluded from logging.

        Args:
            path: The request path to check.

        Returns:
            ``True`` when *path* contains any of the ``EXCLUDED_PATHS`` segments.
        """
        return any(excluded in path for excluded in EXCLUDED_PATHS)

    def _get_request_payload(self, request: HttpRequest) -> dict[str, Any] | str:
        """Extract the request body, masking fields listed in ``DISABLED_PAYLOAD_LOGGING``.

        Args:
            request: The incoming HTTP request.

        Returns:
            Parsed JSON payload dict with sensitive fields masked, or an empty string.
        """
        disabled_logging: dict[str, list[str]] = getattr(settings, "DISABLED_PAYLOAD_LOGGING", {})
        endpoint = request.path
        disabled_fields = disabled_logging.get(endpoint, [])

        try:
            body = request.body.decode("utf-8")
            if body:
                payload = json.loads(body)
                if isinstance(payload, dict) and disabled_fields:
                    for field_name in disabled_fields:
                        if field_name in payload:
                            payload[field_name] = "***"
                return payload
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ""
        return ""

    def _get_request_headers(self, request: HttpRequest) -> dict[str, str]:
        """Extract HTTP headers from the request META dict.

        Args:
            request: The incoming HTTP request.

        Returns:
            Dictionary of header names to their values.
        """
        headers: dict[str, str] = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
            elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                headers[key.replace("_", "-").title()] = value
        return headers

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._should_skip(request.path):
            return self.get_response(request)

        start_time = time.monotonic()

        # Log REQUEST
        logger.info(
            "REQUEST",
            extra={
                "url": request.build_absolute_uri(),
                "method": request.method,
                "headers": self._get_request_headers(request),
                "payload": self._get_request_payload(request),
            },
        )

        response = self.get_response(request)

        # Calculate response time
        elapsed_ms = (time.monotonic() - start_time) * 1000

        # Log RESPONSE
        log_data: dict[str, Any] = {
            "url": request.build_absolute_uri(),
            "method": request.method,
            "status_code": response.status_code,
            "response_time_ms": round(elapsed_ms, 2),
        }

        if response.status_code >= 500:
            logger.error("RESPONSE", extra=log_data)
        else:
            logger.info("RESPONSE", extra=log_data)

        # Record metrics
        metric_attrs = {
            "endpoint": request.path,
            "method": request.method or "",
            "status": str(response.status_code),
            "worker_id": str(os.getpid()),
            "thread_id": str(threading.current_thread().ident),
        }

        if self._counter:
            try:
                self._counter.add(1, metric_attrs)
            except Exception:
                pass

        if self._histogram:
            try:
                self._histogram.record(elapsed_ms, metric_attrs)
            except Exception:
                pass

        return response
