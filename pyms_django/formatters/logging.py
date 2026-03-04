"""JSON log formatter with OpenTelemetry trace context for pyms-django-chassis."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import logging

from django.conf import settings
from pythonjsonlogger.json import JsonFormatter


class CustomJsonFormatter(JsonFormatter):
    """JSON log formatter that enriches records with service metadata and trace context.

    Adds ``timestamp``, ``severity``, ``service``, ``version``, and optionally
    ``trace``, ``span``, and ``parent`` fields from the active OpenTelemetry span.
    """

    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        """Enrich the log record with service and trace metadata.

        Args:
            log_record: Mutable dict that will be serialised as the JSON log entry.
            record: The original ``logging.LogRecord``.
            message_dict: Pre-formatted message fields from the base formatter.
        """
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = datetime.now(UTC).isoformat()
        log_record["severity"] = record.levelname
        log_record["service"] = getattr(settings, "SERVICE_NAME", "unknown")
        log_record["version"] = getattr(settings, "ARTIFACT_VERSION", "unknown")

        # Add OpenTelemetry trace context
        try:
            from opentelemetry import trace

            span = trace.get_current_span()
            span_context = span.get_span_context()
            if span_context.trace_id:
                log_record["trace"] = f"{span_context.trace_id:032x}"
                log_record["span"] = f"{span_context.span_id:016x}"

            parent_span = getattr(span, "parent", None)
            if parent_span and hasattr(parent_span, "span_id"):
                log_record["parent"] = f"{parent_span.span_id:016x}"
        except ImportError:
            # OTel not installed — fall back to context vars populated by TracingMiddleware
            from pyms_django.trace_context import span_id_var, trace_id_var

            tid = trace_id_var.get()
            if tid:
                log_record["trace"] = tid
                log_record["span"] = span_id_var.get()
        except Exception:
            pass
