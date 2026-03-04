"""Base DRF serializers and error-response serializers for pyms-django-chassis."""

from __future__ import annotations

import logging
from typing import Any

from rest_framework import serializers

logger = logging.getLogger(__name__)


class BaseSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Base ``ModelSerializer`` with model-level validation and optimised updates.

    Includes a UUID ``id`` field, delegates validation to the model's
    ``clean()`` method, and saves only changed fields on update.
    """

    id = serializers.UUIDField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate data using the model's ``clean()`` method.

        Instantiates the model (or updates the existing instance) and calls
        ``clean()`` to run full model-level validation.

        Args:
            attrs: Dictionary of deserialized field values.

        Returns:
            Validated attribute dictionary.
        """
        attrs = super().validate(attrs)
        instance = self.instance
        if instance is None:
            instance = self.Meta.model(**attrs)
        else:
            for key, value in attrs.items():
                setattr(instance, key, value)
        instance.clean()
        return attrs

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:  # noqa: ANN401
        """Update the instance, saving only fields that have changed.

        Avoids overwriting concurrent modifications by limiting the
        ``UPDATE`` statement to fields whose values differ from the
        current instance.

        Args:
            instance: The model instance to update.
            validated_data: Dictionary of validated field values.

        Returns:
            The updated model instance.
        """
        update_fields: list[str] = ["updated_at"]
        for attr, value in validated_data.items():
            if getattr(instance, attr, None) != value:
                setattr(instance, attr, value)
                update_fields.append(attr)
        instance.save(update_fields=update_fields)
        return instance


class BadRequestDetailSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for error detail."""

    code = serializers.CharField()
    description = serializers.CharField()


class BadRequestMessageSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for error message."""

    type = serializers.CharField()
    field = serializers.CharField(required=False, default="")
    code = serializers.CharField(required=False, default="")
    description = serializers.CharField(required=False, default="")
    details = BadRequestDetailSerializer(many=True, required=False)


class BadRequestResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for 400 Bad Request responses."""

    messages = BadRequestMessageSerializer(many=True)
    trace_id = serializers.CharField()


class ServerInternalErrorMessageSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for 500 error message."""

    type = serializers.CharField(default="ERROR")
    code = serializers.CharField(default="unknown_error")
    description = serializers.CharField(default="Internal Server Error")


class ServerInternalErrorResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for 500 Internal Server Error responses."""

    messages = ServerInternalErrorMessageSerializer(many=True)
    trace_id = serializers.CharField()


class PaginateResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for paginated responses."""

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()


def dynamic_serializer(model_name: type, expand: bool = False) -> type:
    """Dynamically create a ``ModelSerializer`` class for the given model.

    If ``django-restql`` is installed, the serializer also inherits
    ``DynamicFieldsMixin`` for field filtering via query parameters.

    Args:
        model_name: The Django model class.
        expand: If ``True``, sets ``depth=1`` to expand related objects.

    Returns:
        A new serializer class with ``fields = "__all__"``.
    """
    bases: list[type] = []
    try:
        from django_restql.mixins import DynamicFieldsMixin

        bases.append(DynamicFieldsMixin)
    except ImportError:
        pass
    bases.append(BaseSerializer)

    meta_attrs: dict[str, Any] = {
        "model": model_name,
        "fields": "__all__",
    }
    if expand:
        meta_attrs["depth"] = 1

    meta = type("Meta", (), meta_attrs)
    return type(
        f"{model_name.__name__}DynamicSerializer",
        tuple(bases),
        {"Meta": meta},
    )


def serializer_ql(model_name: type) -> type:
    """Create a RestQL-enabled serializer for the given model.

    Args:
        model_name: The Django model class.

    Returns:
        A new serializer class with RestQL support if available.
    """
    return dynamic_serializer(model_name, expand=False)
