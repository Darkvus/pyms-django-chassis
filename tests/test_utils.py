"""Tests for pyms_django utilities."""

from __future__ import annotations

import pytest
from django.test import RequestFactory, override_settings

from pyms_django.utils import get_app_id_from_request, get_user_id_from_request


@pytest.fixture
def rf() -> RequestFactory:
    return RequestFactory()


class TestGetUserIdFromRequest:
    def test_returns_user_id_from_header(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_USER_ID="abc-123")
        assert get_user_id_from_request(request) == "abc-123"

    def test_returns_none_when_header_absent(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        assert get_user_id_from_request(request) is None

    def test_object_without_meta(self) -> None:
        assert get_user_id_from_request(object()) is None

    @override_settings(HEADER_USER_ID="X-Custom-User")
    def test_uses_custom_header_from_settings(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_X_CUSTOM_USER="custom-id")
        assert get_user_id_from_request(request) == "custom-id"


class TestGetAppIdFromRequest:
    def test_returns_app_id_from_header(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_APP_ID="app-456")
        assert get_app_id_from_request(request) == "app-456"

    def test_returns_none_when_header_absent(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        assert get_app_id_from_request(request) is None

    def test_object_without_meta(self) -> None:
        assert get_app_id_from_request(object()) is None

    @override_settings(HEADER_APP_ID="X-App")
    def test_uses_custom_header_from_settings(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_X_APP="my-app")
        assert get_app_id_from_request(request) == "my-app"
