"""Tests for pyms_django.middlewares.logging."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from pyms_django.middlewares.logging import EXCLUDED_PATHS, RequestLoggingMiddleware


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def mock_get_response() -> MagicMock:
    return MagicMock(return_value=HttpResponse("OK", status=200))


@pytest.fixture
def middleware(mock_get_response: MagicMock) -> RequestLoggingMiddleware:
    return RequestLoggingMiddleware(mock_get_response)


class TestRequestLoggingMiddleware:
    def test_normal_request(self, middleware: RequestLoggingMiddleware, request_factory: RequestFactory) -> None:
        response = middleware(request_factory.get("/api/test/"))
        assert response.status_code == 200

    def test_excluded_health_check(self, middleware: RequestLoggingMiddleware, request_factory: RequestFactory) -> None:
        response = middleware(request_factory.get("/health-check/"))
        assert response.status_code == 200

    def test_excluded_version(self, middleware: RequestLoggingMiddleware, request_factory: RequestFactory) -> None:
        response = middleware(request_factory.get("/version/"))
        assert response.status_code == 200

    def test_should_skip_excluded_paths(self, middleware: RequestLoggingMiddleware) -> None:
        for path in EXCLUDED_PATHS:
            assert middleware._should_skip(f"/{path}/") is True

    def test_should_not_skip_normal_paths(self, middleware: RequestLoggingMiddleware) -> None:
        assert middleware._should_skip("/api/bookings/") is False

    def test_5xx_response(self, request_factory: RequestFactory) -> None:
        mw = RequestLoggingMiddleware(MagicMock(return_value=HttpResponse("Error", status=500)))
        response = mw(request_factory.get("/api/test/"))
        assert response.status_code == 500
