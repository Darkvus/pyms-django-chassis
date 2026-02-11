"""
    pyms-django-chassis
    Open-source Django microservice chassis
"""
from __future__ import annotations

import logging
from typing import Any

from rest_framework import serializers

logger = logging.getLogger(__name__)


class BaseSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """
    Base serializer with UUID id, model validation via clean(),
    and optimized update that only saves changed fields.
    """

    id = serializers.UUIDField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate by instantiating the model and calling clean()."""
        attrs = super().validate(attrs)
        instance = self.instance
        if instance is None:
            instance = self.Meta.model(**attrs)
        else:
            for key, value in attrs.items():
                setattr(instance, key, value)
        instance.clean()
        return attrs

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:
        """Update only changed fields to avoid race conditions."""
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
    """Create a dynamic serializer, optionally with DynamicFieldsMixin from django-restql."""
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
    serializer_class = type(
        f"{model_name.__name__}DynamicSerializer",
        tuple(bases),
        {"Meta": meta},
    )
    return serializer_class


def serializer_ql(model_name: type) -> type:
    """Create a RestQL-enabled serializer."""
    return dynamic_serializer(model_name, expand=False)
