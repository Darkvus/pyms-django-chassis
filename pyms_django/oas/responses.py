"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from typing import Any, Final

BAD_REQUEST_RESPONSE: Final[dict[str, Any]] = {
    "description": "Bad Request",
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "field": {"type": "string"},
                                "code": {"type": "string"},
                                "description": {"type": "string"},
                                "details": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "code": {"type": "string"},
                                            "description": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "trace_id": {"type": "string"},
                },
            },
        },
    },
}

INTERNAL_SERVER_ERROR_RESPONSE: Final[dict[str, Any]] = {
    "description": "Internal Server Error",
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "default": "ERROR"},
                                "code": {"type": "string", "default": "unknown_error"},
                                "description": {"type": "string", "default": "Internal Server Error"},
                            },
                        },
                    },
                    "trace_id": {"type": "string"},
                },
            },
        },
    },
}
