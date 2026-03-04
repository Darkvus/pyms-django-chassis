"""OpenTelemetry tracing middleware for pyms-django-chassis."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from pyms_django.trace_context import span_id_var, trace_id_var

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class TracingMiddleware:
    """Middleware that creates OpenTelemetry spans with B3 propagation."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        carrier: dict[str, Any] = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].lower().replace("_", "-")
                carrier[header_name] = value

        # Propagate B3 trace headers into context vars for log enrichment
        b3_trace = carrier.get("x-b3-traceid", "")
        b3_span = carrier.get("x-b3-spanid", "")
        if b3_trace:
            trace_id_var.set(b3_trace)
        if b3_span:
            span_id_var.set(b3_span)

        try:
            from opentelemetry import context, propagate, trace
            from opentelemetry.trace import SpanKind

            tracer = trace.get_tracer(__name__)
            ctx = propagate.extract(carrier)
            token = context.attach(ctx)
            try:
                with tracer.start_as_current_span(
                    name=f"{request.method} {request.path}",
                    kind=SpanKind.SERVER,
                    attributes={
                        "http.method": request.method,
                        "http.url": request.build_absolute_uri(),
                        "http.host": request.get_host(),
                        "HTTP_HOST": request.get_host(),
                    },
                ) as span:
                    sc = span.get_span_context()
                    if sc.trace_id:
                        trace_id_var.set(f"{sc.trace_id:032x}")
                        span_id_var.set(f"{sc.span_id:016x}")
                    response = self.get_response(request)
                    span.set_attribute("http.status_code", response.status_code)
                    return response
            finally:
                context.detach(token)
        except ImportError:
            logger.debug("OpenTelemetry not installed, skipping tracing")
            return self.get_response(request)
