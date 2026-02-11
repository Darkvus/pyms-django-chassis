"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, create_model


def create_dynamic_model(
    model_name: str,
    fields: dict[str, tuple[type, Any]],
) -> type[BaseModel]:
    """
    Dynamically create a Pydantic model.

    Args:
        model_name: Name of the model class.
        fields: Dictionary of field_name -> (type, default_value).
                Use ... (Ellipsis) for required fields.

    Returns:
        A new Pydantic model class.

    Example:
        UserModel = create_dynamic_model("User", {
            "name": (str, ...),
            "age": (int, 0),
        })
    """
    return create_model(model_name, **fields)
