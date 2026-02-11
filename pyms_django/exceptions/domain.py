"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TypeException(str, Enum):
    """Tipo de excepcion de dominio."""
    VALIDATION = "VALIDATION"
    BUSINESS = "BUSINESS"
    PERMISSION = "PERMISSION"
    TECHNICAL = "TECHNICAL"


class LogLevel(str, Enum):
    """Nivel de log para la excepcion."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    EXCEPTION = "exception"


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    """Detalle de un error de validacion."""
    code: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class ErrorMessage:
    """Mensaje de error de dominio."""
    type: str = "ERROR"
    code: str = ""
    description: str = ""
    field: str = ""
    details: list[ErrorDetail] = field(default_factory=list)


class DomainException(Exception):
    """
    Excepcion base de dominio. Los microservicios heredan de esta clase
    para definir sus excepciones de negocio.

    Ejemplo:
        class BookingNotFoundError(DomainException):
            code = "booking_not_found"
            description = "The requested booking does not exist"
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
        """Retorna la lista de mensajes de error formateados."""
        if self.details:
            return [ErrorMessage(
                type="ERROR", field=self.field, details=self.details
            )]
        return [ErrorMessage(
            type="ERROR", code=self.code, description=self.description
        )]
