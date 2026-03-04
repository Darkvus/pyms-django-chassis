"""Custom DRF exception handler for pyms-django-chassis.

Converts ``DomainException``, DRF exceptions, and unexpected errors into a
standardised JSON error response with an optional OpenTelemetry trace ID.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from pyms_django.exceptions import DomainException, TypeException

logger = logging.getLogger(__name__)

STATUS_MAP: dict[TypeException, int] = {
    TypeException.VALIDATION: status.HTTP_400_BAD_REQUEST,
    TypeException.BUSINESS: status.HTTP_400_BAD_REQUEST,
    TypeException.PERMISSION: status.HTTP_403_FORBIDDEN,
    TypeException.TECHNICAL: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def get_trace_id() -> str:
    """Return the current OpenTelemetry trace ID as a hex string.

    Returns:
        Trace ID hex string, or an empty string if tracing is unavailable.
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        span_context = span.get_span_context()
        if span_context.trace_id:
            return hex(span_context.trace_id)[2:]
    except ImportError:
        pass
    except Exception:
        pass
    return ""


def process_error_message(field: str, errors: object) -> dict[str, Any]:
    """Convert a single field's validation errors into a standardised dict.

    Args:
        field: Name of the field that failed validation.
        errors: Error value(s) for the field.

    Returns:
        Standardised error dict with ``type``, ``field``, and ``details`` keys.
    """
    if isinstance(errors, list):
        details = []
        for error in errors:
            if isinstance(error, dict):
                details.append(error)
            else:
                details.append(
                    {
                        "code": str(error.code) if hasattr(error, "code") else "invalid",  # type: ignore[union-attr]
                        "description": str(error),
                    }
                )
        return {"type": "INFO", "field": field, "details": details}
    return {"type": "ERROR", "code": "invalid", "description": str(errors)}


def process_errors(errors: object) -> list[dict[str, Any]]:
    """Convert DRF validation error detail into a list of standardised dicts.

    Args:
        errors: DRF ``ValidationError.detail`` value (dict, list, or scalar).

    Returns:
        List of standardised error message dicts.
    """
    messages: list[dict[str, Any]] = []
    if isinstance(errors, dict):
        for field_name, field_errors in errors.items():
            if isinstance(field_errors, list):
                details = []
                for error in field_errors:
                    if isinstance(error, dict):
                        details.append(error)
                    else:
                        code = getattr(error, "code", "invalid") if hasattr(error, "code") else "invalid"
                        details.append({"code": str(code), "description": str(error)})
                messages.append({"type": "INFO", "field": field_name, "details": details})
            else:
                messages.append(process_error_message(field_name, field_errors))
    elif isinstance(errors, list):
        for error in errors:
            if isinstance(error, dict):
                messages.append(error)
            else:
                messages.append({"type": "ERROR", "code": "invalid", "description": str(error)})
    else:
        messages.append({"type": "ERROR", "code": "unknown_error", "description": str(errors)})
    return messages


def get_messages(exc: Exception) -> tuple[list[dict[str, Any]], int]:
    """Extract a list of error messages and an HTTP status code from an exception.

    Args:
        exc: The exception to inspect.

    Returns:
        Tuple of ``(list of error message dicts, HTTP status code)``.
    """
    if isinstance(exc, DomainException):
        http_status = STATUS_MAP.get(exc.type, status.HTTP_500_INTERNAL_SERVER_ERROR)
        messages = [asdict(msg) for msg in exc.messages]
        # Do not expose description for domain exceptions
        for msg in messages:
            if not msg.get("details"):
                msg["description"] = ""
        return messages, http_status

    if isinstance(exc, ValidationError):
        return process_errors(exc.detail), status.HTTP_400_BAD_REQUEST

    if isinstance(exc, Http404):
        return [{"type": "ERROR", "code": "not_found", "description": "Not found."}], status.HTTP_404_NOT_FOUND

    if isinstance(exc, APIException):
        if isinstance(exc.detail, list):
            messages = [{"type": "ERROR", "code": exc.default_code, "description": str(d)} for d in exc.detail]
        elif isinstance(exc.detail, dict):
            messages = process_errors(exc.detail)
        else:
            messages = [{"type": "ERROR", "code": exc.default_code, "description": str(exc.detail)}]
        return messages, exc.status_code

    return (
        [{"type": "ERROR", "code": "unknown_error", "description": "Internal Server Error"}],
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _log_exception(exc: Exception) -> None:
    """Log the exception at the appropriate level.

    Uses the ``log_level`` from ``DomainException`` instances, or
    ``logger.exception`` for all other exception types.

    Args:
        exc: The exception to log.
    """
    if isinstance(exc, DomainException):
        log_level = exc.log_level.value
        log_fn = getattr(logger, log_level, logger.exception)
        log_fn("DomainException: %s - %s", exc.code, exc.description, exc_info=exc)
    else:
        logger.exception("Unhandled exception: %s", exc)


def handle_response(messages: list[dict[str, Any]], http_status: int) -> Response:
    """Build a standardised DRF ``Response`` for an error.

    Args:
        messages: List of standardised error message dicts.
        http_status: HTTP status code for the response.

    Returns:
        DRF ``Response`` containing ``messages`` and the current ``trace_id``.
    """
    trace_id = get_trace_id()
    return Response(
        {"messages": messages, "trace_id": trace_id},
        status=http_status,
    )


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """DRF exception handler that returns a standardised error response.

    Handles ``DomainException``, DRF ``APIException`` subclasses,
    ``Http404``, and unexpected exceptions.

    Args:
        exc: The raised exception.
        context: DRF handler context dict.

    Returns:
        DRF ``Response`` with a standardised error payload.
    """
    _log_exception(exc)

    # Let DRF handle its own exceptions first for standard processing
    exception_handler(exc, context)

    messages, http_status = get_messages(exc)
    return handle_response(messages, http_status)
