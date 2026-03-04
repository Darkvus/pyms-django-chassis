"""Tests for pyms_django.oas.parameters."""
from __future__ import annotations

from pyms_django.oas.parameters import HEADER_USER_ID_PARAM


class TestHeaderUserIdParam:
    def test_name(self) -> None:
        assert HEADER_USER_ID_PARAM["name"] == "User-Id"

    def test_in_header(self) -> None:
        assert HEADER_USER_ID_PARAM["in"] == "header"

    def test_not_required(self) -> None:
        assert HEADER_USER_ID_PARAM["required"] is False

    def test_schema_type_uuid(self) -> None:
        assert HEADER_USER_ID_PARAM["schema"]["type"] == "string"
        assert HEADER_USER_ID_PARAM["schema"]["format"] == "uuid"
