"""Tests for pyms_django.handlers.errors."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.http import Http404
from rest_framework.exceptions import APIException, NotAuthenticated, ValidationError

from pyms_django.exceptions import DomainException, TypeException
from pyms_django.handlers.errors import (
    custom_exception_handler,
    get_messages,
    get_trace_id,
    handle_response,
    process_error_message,
    process_errors,
)


class TestGetTraceId:
    def test_returns_empty_when_otel_not_installed(self) -> None:
        with patch.dict("sys.modules", {"opentelemetry": None}):
            result = get_trace_id()
        assert result == ""

    def test_returns_string(self) -> None:
        assert isinstance(get_trace_id(), str)


class TestProcessErrorMessage:
    def test_list_of_string_errors(self) -> None:
        err = MagicMock()
        err.code = "required"
        err.__str__ = lambda _: "This field is required."
        result = process_error_message("name", [err])
        assert result["type"] == "INFO"
        assert result["field"] == "name"
        assert len(result["details"]) == 1

    def test_list_of_dict_errors(self) -> None:
        result = process_error_message("email", [{"code": "invalid", "description": "Invalid email"}])
        assert result["type"] == "INFO"
        assert result["details"][0]["code"] == "invalid"

    def test_non_list_error(self) -> None:
        result = process_error_message("name", "some error")
        assert result["type"] == "ERROR"
        assert result["code"] == "invalid"


class TestProcessErrors:
    def test_dict_errors(self) -> None:
        err = MagicMock()
        err.code = "required"
        err.__str__ = lambda _: "Required."
        result = process_errors({"name": [err]})
        assert len(result) == 1
        assert result[0]["field"] == "name"

    def test_list_errors(self) -> None:
        result = process_errors(["error one", "error two"])
        assert len(result) == 2

    def test_list_of_dict_errors(self) -> None:
        result = process_errors([{"type": "ERROR", "code": "x", "description": "y"}])
        assert result[0]["code"] == "x"

    def test_scalar_error(self) -> None:
        result = process_errors("something went wrong")
        assert result[0]["code"] == "unknown_error"

    def test_dict_with_non_list_field(self) -> None:
        result = process_errors({"field": "direct string error"})
        assert len(result) == 1


class TestGetMessages:
    def test_domain_validation(self) -> None:
        class ValErr(DomainException):
            type = TypeException.VALIDATION
        _, code = get_messages(ValErr(code="invalid"))
        assert code == 400

    def test_domain_business(self) -> None:
        class BizErr(DomainException):
            type = TypeException.BUSINESS
        _, code = get_messages(BizErr(code="conflict"))
        assert code == 400

    def test_domain_permission(self) -> None:
        class PermErr(DomainException):
            type = TypeException.PERMISSION
        _, code = get_messages(PermErr(code="forbidden"))
        assert code == 403

    def test_domain_technical(self) -> None:
        _, code = get_messages(DomainException(code="crash"))
        assert code == 500

    def test_validation_error_dict(self) -> None:
        _, code = get_messages(ValidationError({"name": ["This field is required."]}))
        assert code == 400

    def test_validation_error_list(self) -> None:
        _, code = get_messages(ValidationError(["error one"]))
        assert code == 400

    def test_http404(self) -> None:
        msgs, code = get_messages(Http404())
        assert code == 404
        assert msgs[0]["code"] == "not_found"

    def test_api_exception_string_detail(self) -> None:
        _, code = get_messages(APIException("something failed"))
        assert code == 500

    def test_api_exception_list_detail(self) -> None:
        _, code = get_messages(NotAuthenticated())
        assert code == 401

    def test_unknown_exception(self) -> None:
        msgs, code = get_messages(RuntimeError("crash"))
        assert code == 500
        assert msgs[0]["code"] == "unknown_error"

    def test_domain_description_hidden(self) -> None:
        exc = DomainException(code="secret", description="private detail")
        msgs, _ = get_messages(exc)
        assert msgs[0]["description"] == ""


class TestHandleResponse:
    def test_builds_response(self) -> None:
        response = handle_response([{"type": "ERROR", "code": "x", "description": "y"}], 400)
        assert response.status_code == 400
        assert "messages" in response.data  # type: ignore[attr-defined]
        assert "trace_id" in response.data  # type: ignore[attr-defined]


class TestCustomExceptionHandler:
    def setup_method(self) -> None:
        self.context: dict = {}

    def test_handles_domain_exception(self) -> None:
        response = custom_exception_handler(DomainException(code="test"), self.context)
        assert response is not None
        assert response.status_code == 500

    def test_handles_validation_error(self) -> None:
        response = custom_exception_handler(ValidationError({"field": ["required"]}), self.context)
        assert response is not None
        assert response.status_code == 400

    def test_handles_http404(self) -> None:
        response = custom_exception_handler(Http404(), self.context)
        assert response is not None
        assert response.status_code == 404

    def test_handles_runtime_error(self) -> None:
        response = custom_exception_handler(RuntimeError("boom"), self.context)
        assert response is not None
        assert response.status_code == 500
