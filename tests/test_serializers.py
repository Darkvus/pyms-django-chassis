"""
    pyms-django-chassis
    Tests for serializers.
"""
from __future__ import annotations

from pyms_django.serializers import (
    BadRequestDetailSerializer,
    BadRequestMessageSerializer,
    BadRequestResponseSerializer,
    PaginateResponseSerializer,
    ServerInternalErrorMessageSerializer,
    ServerInternalErrorResponseSerializer,
)


class TestBadRequestDetailSerializer:
    def test_valid_data(self) -> None:
        serializer = BadRequestDetailSerializer(data={
            "code": "required",
            "description": "This field is required.",
        })
        assert serializer.is_valid()

    def test_missing_code(self) -> None:
        serializer = BadRequestDetailSerializer(data={
            "description": "This field is required.",
        })
        assert not serializer.is_valid()


class TestBadRequestMessageSerializer:
    def test_valid_data_with_details(self) -> None:
        serializer = BadRequestMessageSerializer(data={
            "type": "INFO",
            "field": "name",
            "details": [{"code": "required", "description": "Required"}],
        })
        assert serializer.is_valid()

    def test_valid_data_with_code(self) -> None:
        serializer = BadRequestMessageSerializer(data={
            "type": "ERROR",
            "code": "not_found",
            "description": "Not found",
        })
        assert serializer.is_valid()


class TestBadRequestResponseSerializer:
    def test_valid_data(self) -> None:
        serializer = BadRequestResponseSerializer(data={
            "messages": [{"type": "ERROR", "code": "test", "description": "Test"}],
            "trace_id": "abc123",
        })
        assert serializer.is_valid()


class TestServerInternalErrorSerializer:
    def test_message_defaults(self) -> None:
        serializer = ServerInternalErrorMessageSerializer(data={})
        assert serializer.is_valid()

    def test_response_valid(self) -> None:
        serializer = ServerInternalErrorResponseSerializer(data={
            "messages": [{"type": "ERROR", "code": "unknown_error", "description": "Internal Server Error"}],
            "trace_id": "xyz789",
        })
        assert serializer.is_valid()


class TestPaginateResponseSerializer:
    def test_valid_data(self) -> None:
        serializer = PaginateResponseSerializer(data={
            "count": 100,
            "next": "http://example.com/api?offset=10",
            "previous": None,
            "results": [{"id": 1}],
        })
        assert serializer.is_valid()
