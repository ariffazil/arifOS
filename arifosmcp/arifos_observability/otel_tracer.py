"""
OpenTelemetry Tracer — Init + span helpers for arifOS.

Phase 1: in-process tracing with console + OTLP exporter.
Phase 2: full agent-specific trace schema.

Constitutional binding:
- F11 AUDIT: Every tool call is a span
- F2 TRUTH: Spans carry input hash + output hash for reproducibility
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

_initialized = False


def init_tracer(
    service_name: str = "arifOS",
    service_version: str = "2026.06.14",
    otlp_endpoint: str | None = None,
    console_export: bool = False,
) -> trace.Tracer:
    """Initialize the OpenTelemetry tracer (idempotent)."""
    global _initialized
    if _initialized:
        return trace.get_tracer(service_name)

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "arifos.floors_active": 13,
            "arifos.constitution_hash": os.environ.get(
                "ARIFOS_CONSTITUTION_HASH",
                "sha256:dd4f41e75f55ed38df759a1c8db1fc4680ef0307a6b0e2793bccf6540bb21506",
            ),
        }
    )

    provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        except ImportError:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)

        provider.add_span_processor(
            BatchSpanProcessor(exporter)
        )

    if console_export:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _initialized = True
    return trace.get_tracer(service_name)


class OTelTracer:
    """High-level wrapper around OTel tracer for arifOS tool calls."""

    def __init__(self, service_name: str = "arifOS"):
        self.tracer = init_tracer(service_name=service_name)

    @contextmanager
    def span(self, name: str, attributes: dict[str, Any] | None = None):
        """Context-managed span with arifOS attribute schema."""
        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                for k, v in attributes.items():
                    span.set_attribute(
                        k, str(v) if not isinstance(v, (str, int, float, bool)) else v
                    )
            span.set_attribute("arifos.floor_compliance", "F11_AUDIT")
            span.set_attribute("arifos.epoch", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            try:
                yield span
            except Exception as e:
                span.set_attribute("arifos.error", str(e))
                span.record_exception(e)
                raise
