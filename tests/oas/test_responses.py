"""Tests for pyms_django.oas.responses."""

from __future__ import annotations

from pyms_django.oas.responses import BAD_REQUEST_RESPONSE, INTERNAL_SERVER_ERROR_RESPONSE


class TestBadRequestResponse:
    def test_description(self) -> None:
        assert BAD_REQUEST_RESPONSE["description"] == "Bad Request"

    def test_has_messages_property(self) -> None:
        schema = BAD_REQUEST_RESPONSE["content"]["application/json"]["schema"]
        assert "messages" in schema["properties"]

    def test_has_trace_id_property(self) -> None:
        schema = BAD_REQUEST_RESPONSE["content"]["application/json"]["schema"]
        assert "trace_id" in schema["properties"]


class TestInternalServerErrorResponse:
    def test_description(self) -> None:
        assert INTERNAL_SERVER_ERROR_RESPONSE["description"] == "Internal Server Error"

    def test_has_messages_property(self) -> None:
        schema = INTERNAL_SERVER_ERROR_RESPONSE["content"]["application/json"]["schema"]
        assert "messages" in schema["properties"]

    def test_default_code(self) -> None:
        schema = INTERNAL_SERVER_ERROR_RESPONSE["content"]["application/json"]["schema"]
        items = schema["properties"]["messages"]["items"]
        assert items["properties"]["code"]["default"] == "unknown_error"
