"""Domain exception primitives for pyms-django-chassis microservices.

Provides ``TypeException``, ``LogLevel``, ``ErrorDetail``, ``ErrorMessage``,
and ``DomainException`` as building blocks for business-rule exceptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from enum import Enum


class TypeException(str, Enum):
    """Enum of domain exception categories."""
    VALIDATION = "VALIDATION"
    BUSINESS = "BUSINESS"
    PERMISSION = "PERMISSION"
    TECHNICAL = "TECHNICAL"


class LogLevel(str, Enum):
    """Enum of log levels used when a ``DomainException`` is logged."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    EXCEPTION = "exception"


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    """Immutable detail entry for a single validation error.

    Attributes:
        code: Machine-readable error code.
        description: Human-readable explanation.
    """

    code: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class ErrorMessage:
    """Immutable error message included in a ``DomainException`` response.

    Attributes:
        type: Message category (e.g. ``"ERROR"``, ``"INFO"``).
        code: Machine-readable error code.
        description: Human-readable explanation.
        field: Field name associated with the error, if any.
        details: List of nested ``ErrorDetail`` entries.
    """

    type: str = "ERROR"
    code: str = ""
    description: str = ""
    field: str = ""
    details: list[ErrorDetail] = dc_field(default_factory=list)


class DomainException(Exception):
    """Base class for domain-specific exceptions.

    Subclass to define business-rule exceptions with a fixed code, description,
    type, and log level. Override class attributes to customise the defaults.

    Attributes:
        code: Machine-readable error identifier.
        description: Default human-readable description.
        type: Category that controls the HTTP status code returned.
        log_level: Severity used when logging the exception.

    Example:
        ::

            class ResourceNotFoundError(DomainException):
                code = "resource_not_found"
                description = "The requested resource does not exist"
                type = TypeException.BUSINESS
                log_level = LogLevel.WARNING
    """
    code: str = "domain_error"
    description: str = ""
    type: TypeException = TypeException.TECHNICAL
    log_level: LogLevel = LogLevel.EXCEPTION

    def __init__(
        self,
        code: str | None = None,
        description: str | None = None,
        field: str = "",
        details: list[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(description or self.description)
        if code:
            self.code = code
        if description:
            self.description = description
        self.field = field
        self.details = details

    @property
    def messages(self) -> list[ErrorMessage]:
        """List of formatted error messages for the HTTP response.

        Returns:
            List of ``ErrorMessage`` instances describing the exception.
        """
        if self.details:
            return [ErrorMessage(
                type="ERROR", field=self.field, details=self.details
            )]
        return [ErrorMessage(
            type="ERROR", code=self.code, description=self.description
        )]
