"""JSON log formatter with OpenTelemetry trace context for pyms-django-chassis."""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

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
                log_record["trace"] = hex(span_context.trace_id)[2:]
                log_record["span"] = hex(span_context.span_id)[2:]

            parent_span = getattr(span, "parent", None)
            if parent_span and hasattr(parent_span, "span_id"):
                log_record["parent"] = hex(parent_span.span_id)[2:]
        except ImportError:
            pass
        except Exception:
            pass
