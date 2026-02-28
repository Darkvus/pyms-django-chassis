"""Dynamic Pydantic model factory for pyms-django-chassis."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, create_model


def create_dynamic_model(
    model_name: str,
    fields: dict[str, tuple[type, Any]],
) -> type[BaseModel]:
    """Dynamically create a Pydantic model class.

    Args:
        model_name: Name of the generated model class.
        fields: Mapping of field names to ``(type, default)`` tuples.
            Use ``...`` (``Ellipsis``) as the default for required fields.

    Returns:
        A new Pydantic model class with the given fields.

    Example:
        ::

            UserModel = create_dynamic_model("User", {
                "name": (str, ...),
                "age": (int, 0),
            })
    """
    return create_model(model_name, **fields)
