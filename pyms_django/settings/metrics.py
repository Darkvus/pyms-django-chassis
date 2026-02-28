"""OpenTelemetry metrics provider configuration for pyms-django-chassis."""
from __future__ import annotations

import logging
from typing import Final

logger = logging.getLogger(__name__)

LATENCY_BUCKETS: Final[list[float]] = [
    0, 50, 100, 250, 500, 750, 1000, 3000, 5000, 10000, 30000,
]


def configure_metrics_provider(
    service_name: str,
    artifact_version: str,
    collector_url: str = "http://localhost:4318/v1/metrics",
) -> None:
    """Configure the OpenTelemetry metrics provider with an OTLP HTTP exporter.

    Sets up a ``MeterProvider`` with a ``PeriodicExportingMetricReader`` and a
    histogram view with explicit latency buckets. Does nothing if the
    ``opentelemetry`` monitoring extras are not installed.

    Args:
        service_name: Name of the service reported to the collector.
        artifact_version: Version of the service reported to the collector.
        collector_url: OTLP HTTP endpoint for the metrics exporter.
    """
    try:
        from opentelemetry import metrics
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({
            "service.name": service_name,
            "service.version": artifact_version,
        })

        exporter = OTLPMetricExporter(endpoint=collector_url)

        reader = PeriodicExportingMetricReader(
            exporter,
            export_interval_millis=60000,
            export_timeout_millis=30000,
        )

        latency_view = View(
            instrument_name="microservice_http_request_latency",
            aggregation=ExplicitBucketHistogramAggregation(boundaries=LATENCY_BUCKETS),
        )

        provider = MeterProvider(
            resource=resource,
            metric_readers=[reader],
            views=[latency_view],
        )

        metrics.set_meter_provider(provider)
        logger.info("Metrics provider configured for %s v%s", service_name, artifact_version)

    except ImportError:
        logger.warning("OpenTelemetry monitoring extras not installed. Metrics disabled.")
    except Exception:
        logger.exception("Failed to configure metrics provider")
