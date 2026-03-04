"""Tests for pyms_django.exceptions.domain."""
from __future__ import annotations

import pytest

from pyms_django.exceptions import (
    DomainException,
    ErrorDetail,
    ErrorMessage,
    LogLevel,
    TypeException,
)
from pyms_django.handlers.errors import get_messages


class TestTypeException:
    def test_validation_value(self) -> None:
        assert TypeException.VALIDATION == "VALIDATION"

    def test_business_value(self) -> None:
        assert TypeException.BUSINESS == "BUSINESS"

    def test_permission_value(self) -> None:
        assert TypeException.PERMISSION == "PERMISSION"

    def test_technical_value(self) -> None:
        assert TypeException.TECHNICAL == "TECHNICAL"


class TestLogLevel:
    def test_debug_value(self) -> None:
        assert LogLevel.DEBUG == "debug"

    def test_info_value(self) -> None:
        assert LogLevel.INFO == "info"

    def test_warning_value(self) -> None:
        assert LogLevel.WARNING == "warning"

    def test_exception_value(self) -> None:
        assert LogLevel.EXCEPTION == "exception"


class TestErrorDetail:
    def test_create_error_detail(self) -> None:
        detail = ErrorDetail(code="required", description="This field is required.")
        assert detail.code == "required"
        assert detail.description == "This field is required."

    def test_error_detail_is_frozen(self) -> None:
        detail = ErrorDetail(code="required")
        with pytest.raises(AttributeError):
            detail.code = "changed"  # type: ignore[misc]


class TestErrorMessage:
    def test_default_values(self) -> None:
        msg = ErrorMessage()
        assert msg.type == "ERROR"
        assert msg.code == ""
        assert msg.description == ""
        assert msg.field == ""
        assert msg.details == []

    def test_custom_values(self) -> None:
        detail = ErrorDetail(code="min_length", description="Too short")
        msg = ErrorMessage(type="INFO", field="name", details=[detail])
        assert msg.type == "INFO"
        assert msg.field == "name"
        assert len(msg.details) == 1


class TestDomainException:
    def test_default_exception(self) -> None:
        exc = DomainException()
        assert exc.code == "domain_error"
        assert exc.type == TypeException.TECHNICAL
        assert exc.log_level == LogLevel.EXCEPTION

    def test_custom_exception(self) -> None:
        exc = DomainException(code="custom_error", description="Something went wrong")
        assert exc.code == "custom_error"
        assert exc.description == "Something went wrong"

    def test_subclass_exception(self) -> None:
        class BookingNotFound(DomainException):
            code = "booking_not_found"
            description = "Booking not found"
            type = TypeException.BUSINESS
            log_level = LogLevel.WARNING

        exc = BookingNotFound()
        assert exc.code == "booking_not_found"
        assert exc.type == TypeException.BUSINESS
        assert exc.log_level == LogLevel.WARNING

    def test_messages_without_details(self) -> None:
        exc = DomainException(code="test_error", description="Test")
        messages = exc.messages
        assert len(messages) == 1
        assert messages[0].code == "test_error"

    def test_messages_with_details(self) -> None:
        details = [ErrorDetail(code="required", description="Required field")]
        exc = DomainException(field="name", details=details)
        messages = exc.messages
        assert len(messages) == 1
        assert messages[0].field == "name"
        assert len(messages[0].details) == 1

    def test_get_messages_validation(self) -> None:
        class ValidationErr(DomainException):
            type = TypeException.VALIDATION

        exc = ValidationErr(code="invalid")
        msgs, status_code = get_messages(exc)
        assert status_code == 400

    def test_get_messages_permission(self) -> None:
        class PermErr(DomainException):
            type = TypeException.PERMISSION

        exc = PermErr(code="forbidden")
        msgs, status_code = get_messages(exc)
        assert status_code == 403

    def test_get_messages_technical(self) -> None:
        exc = DomainException(code="technical")
        msgs, status_code = get_messages(exc)
        assert status_code == 500
