"""
    pyms-django-chassis
    Open-source Django microservice chassis
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
    """Get the trace ID from the current OpenTelemetry span."""
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


def process_error_message(field: str, errors: Any) -> dict[str, Any]:
    """Process a single error field into standardized format."""
    if isinstance(errors, list):
        details = []
        for error in errors:
            if isinstance(error, dict):
                details.append(error)
            else:
                details.append({"code": str(error.code) if hasattr(error, "code") else "invalid", "description": str(error)})
        return {"type": "INFO", "field": field, "details": details}
    return {"type": "ERROR", "code": "invalid", "description": str(errors)}


def process_errors(errors: Any) -> list[dict[str, Any]]:
    """Process DRF validation errors into standardized message format."""
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
    """Extract messages and status code from an exception."""
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

    return [{"type": "ERROR", "code": "unknown_error", "description": "Internal Server Error"}], status.HTTP_500_INTERNAL_SERVER_ERROR


def _log_exception(exc: Exception) -> None:
    """Log the exception using the appropriate log level."""
    if isinstance(exc, DomainException):
        log_level = exc.log_level.value
        log_fn = getattr(logger, log_level, logger.exception)
        log_fn("DomainException: %s - %s", exc.code, exc.description, exc_info=exc)
    else:
        logger.exception("Unhandled exception: %s", exc)


def handle_response(messages: list[dict[str, Any]], http_status: int) -> Response:
    """Format and return a standardized error response."""
    trace_id = get_trace_id()
    return Response(
        {"messages": messages, "trace_id": trace_id},
        status=http_status,
    )


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """
    Custom exception handler for DRF.
    Handles DomainException, DRF exceptions, and generic exceptions.
    """
    _log_exception(exc)

    # Let DRF handle its own exceptions first for standard processing
    response = exception_handler(exc, context)

    messages, http_status = get_messages(exc)
    return handle_response(messages, http_status)
