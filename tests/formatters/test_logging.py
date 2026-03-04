"""Tests for pyms_django.formatters.logging."""

from __future__ import annotations

import logging
from unittest.mock import patch

from pyms_django.formatters.logging import CustomJsonFormatter
from pyms_django.trace_context import span_id_var, trace_id_var


def _make_record(msg: str = "test", level: int = logging.INFO) -> logging.LogRecord:
    return logging.LogRecord(
        name="test",
        level=level,
        pathname="",
        lineno=0,
        msg=msg,
        args=(),
        exc_info=None,
    )


class TestCustomJsonFormatter:
    def setup_method(self) -> None:
        self.formatter = CustomJsonFormatter()

    def test_adds_timestamp(self) -> None:
        log_record: dict = {}
        self.formatter.add_fields(log_record, _make_record(), {})
        assert "timestamp" in log_record

    def test_adds_severity(self) -> None:
        log_record: dict = {}
        self.formatter.add_fields(log_record, _make_record(), {})
        assert log_record["severity"] == "INFO"

    def test_adds_service(self) -> None:
        log_record: dict = {}
        self.formatter.add_fields(log_record, _make_record(), {})
        assert log_record["service"] == "test-service"

    def test_adds_version(self) -> None:
        log_record: dict = {}
        self.formatter.add_fields(log_record, _make_record(), {})
        assert log_record["version"] == "0.0.1-test"

    def test_severity_warning(self) -> None:
        log_record: dict = {}
        self.formatter.add_fields(log_record, _make_record(level=logging.WARNING), {})
        assert log_record["severity"] == "WARNING"

    def test_trace_from_context_var_when_no_otel(self) -> None:
        token_t = trace_id_var.set("aabbccdd00112233aabbccdd00112233")
        token_s = span_id_var.set("cafebabe12345678")
        try:
            log_record: dict = {}
            with patch.dict("sys.modules", {"opentelemetry": None, "opentelemetry.trace": None}):
                self.formatter.add_fields(log_record, _make_record(), {})
            assert log_record.get("trace") == "aabbccdd00112233aabbccdd00112233"
            assert log_record.get("span") == "cafebabe12345678"
        finally:
            trace_id_var.reset(token_t)
            span_id_var.reset(token_s)

    def test_no_trace_when_context_var_empty_and_no_otel(self) -> None:
        token_t = trace_id_var.set("")
        token_s = span_id_var.set("")
        try:
            log_record: dict = {}
            with patch.dict("sys.modules", {"opentelemetry": None, "opentelemetry.trace": None}):
                self.formatter.add_fields(log_record, _make_record(), {})
            assert "trace" not in log_record
        finally:
            trace_id_var.reset(token_t)
            span_id_var.reset(token_s)
