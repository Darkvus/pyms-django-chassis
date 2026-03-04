"""Tests for pyms_django.middlewares.tracing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from pyms_django.middlewares.tracing import TracingMiddleware
from pyms_django.trace_context import span_id_var, trace_id_var


@pytest.fixture
def rf() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def ok_response() -> HttpResponse:
    return HttpResponse("OK", status=200)


class TestTracingMiddleware:
    def test_passes_through_without_otel(self, rf: RequestFactory, ok_response: HttpResponse) -> None:
        mw = TracingMiddleware(MagicMock(return_value=ok_response))
        assert mw(rf.get("/api/test/")).status_code == 200

    def test_b3_headers_set_context_vars(self, rf: RequestFactory, ok_response: HttpResponse) -> None:
        captured: dict[str, str] = {}

        def capturing(_req: HttpRequest) -> HttpResponse:
            captured["trace"] = trace_id_var.get()
            captured["span"] = span_id_var.get()
            return ok_response

        mw = TracingMiddleware(capturing)
        mw(rf.get("/api/resource/", HTTP_X_B3_TRACEID="aabbccdd11223344", HTTP_X_B3_SPANID="deadbeef"))
        assert captured["trace"] == "aabbccdd11223344"
        assert captured["span"] == "deadbeef"

    def test_no_b3_headers_leaves_context_vars_empty(self, rf: RequestFactory, ok_response: HttpResponse) -> None:
        trace_id_var.set("")
        span_id_var.set("")
        captured: dict[str, str] = {}

        def capturing(_req: HttpRequest) -> HttpResponse:
            captured["trace"] = trace_id_var.get()
            return ok_response

        TracingMiddleware(capturing)(rf.get("/api/resource/"))
        assert captured["trace"] == ""

    def test_handles_import_error_gracefully(self, rf: RequestFactory, ok_response: HttpResponse) -> None:
        mw = TracingMiddleware(MagicMock(return_value=ok_response))
        with patch.dict("sys.modules", {"opentelemetry": None, "opentelemetry.trace": None}):
            assert mw(rf.get("/api/test/")).status_code == 200


class TestTraceContextVar:
    def test_default_values(self) -> None:
        trace_id_var.set("")
        span_id_var.set("")
        assert trace_id_var.get() == ""
        assert span_id_var.get() == ""

    def test_set_and_get(self) -> None:
        token_t = trace_id_var.set("deadbeef01234567")
        token_s = span_id_var.set("cafebabe")
        assert trace_id_var.get() == "deadbeef01234567"
        assert span_id_var.get() == "cafebabe"
        trace_id_var.reset(token_t)
        span_id_var.reset(token_s)
