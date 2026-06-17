"""OpenTelemetry setup for VerityGate.

Initializes tracing + logging when OTEL_ENABLED=true. Instruments FastAPI,
SQLAlchemy, httpx, and Redis automatically. Does nothing when disabled, so
local development runs unchanged.
"""
from __future__ import annotations

import logging

from .config import get_settings

logger = logging.getLogger(__name__)


def setup_telemetry(app=None, engine=None):
    """Call during app lifespan. No-op when OTEL_ENABLED=false."""
    settings = get_settings()
    if not settings.otel_enabled:
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Instrument FastAPI
    if app is not None:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)

    # Instrument SQLAlchemy
    if engine is not None:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument(engine=engine)

    # Instrument httpx (provider calls)
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    HTTPXClientInstrumentor().instrument()

    # Instrument Redis
    if settings.redis_url:
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        RedisInstrumentor().instrument()

    logger.info(
        "OpenTelemetry initialized — exporting to %s",
        settings.otel_exporter_endpoint,
    )
