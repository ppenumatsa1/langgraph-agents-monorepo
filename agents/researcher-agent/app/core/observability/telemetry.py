import logging
import os

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)
from langchain_azure_ai.callbacks.tracers import AzureAIOpenTelemetryTracer
from opentelemetry import _logs, metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanContext, TraceFlags

from app.core.middleware.correlation import get_correlation_id
from app.core.utils.config import get_settings

_telemetry_configured = False
_fastapi_instrumented = False
_langchain_tracer: AzureAIOpenTelemetryTracer | None = None


class _TelemetryNoiseFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        noisy_prefixes = (
            "azure.monitor.opentelemetry",
            "azure.core.pipeline",
            "azure.core.pipeline.policies.http_logging_policy",
        )
        return not record.name.startswith(noisy_prefixes)


class _SpanNoiseFilterProcessor(SpanProcessor):
    def on_start(self, span, parent_context):
        return

    def on_end(self, span):
        name = getattr(span, "name", "")
        attributes = getattr(span, "attributes", {}) or {}
        asgi_event = attributes.get("asgi.event.type")
        noisy_name_suffixes = (" http receive", " http send")

        if asgi_event in {"http.request", "http.response.start", "http.response.body"}:
            span._context = SpanContext(
                span.context.trace_id,
                span.context.span_id,
                span.context.is_remote,
                TraceFlags(TraceFlags.DEFAULT),
                span.context.trace_state,
            )
            return

        if name.endswith(noisy_name_suffixes):
            span._context = SpanContext(
                span.context.trace_id,
                span.context.span_id,
                span.context.is_remote,
                TraceFlags(TraceFlags.DEFAULT),
                span.context.trace_state,
            )


class _LogRecordEnrichmentFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        trace_id = get_current_trace_id()
        span_id = get_current_span_id()
        correlation_id = get_current_correlation_id()
        if trace_id and not hasattr(record, "trace_id"):
            setattr(record, "trace_id", trace_id)
        if span_id and not hasattr(record, "span_id"):
            setattr(record, "span_id", span_id)
        if correlation_id and not hasattr(record, "correlation_id"):
            setattr(record, "correlation_id", correlation_id)
        return True


def get_current_trace_id() -> str | None:
    span_context = trace.get_current_span().get_span_context()
    if span_context and span_context.is_valid:
        return format(span_context.trace_id, "032x")
    return None


def get_current_span_id() -> str | None:
    span_context = trace.get_current_span().get_span_context()
    if span_context and span_context.is_valid:
        return format(span_context.span_id, "016x")
    return None


def get_current_correlation_id() -> str | None:
    return get_correlation_id()


def configure_telemetry(app=None) -> None:
    global _telemetry_configured
    global _fastapi_instrumented

    settings = get_settings()
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logging.getLogger(__name__).warning(
            "Telemetry disabled: missing APPLICATIONINSIGHTS_CONNECTION_STRING"
        )
        return

    if not _telemetry_configured:
        resource = Resource.create(
            {
                "service.name": os.getenv("OTEL_SERVICE_NAME", settings.service_name),
                "service.version": settings.service_version,
            }
        )

        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(_SpanNoiseFilterProcessor())
        tracer_provider.add_span_processor(
            BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=connection_string))
        )
        trace.set_tracer_provider(tracer_provider)

        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(AzureMonitorLogExporter(connection_string=connection_string))
        )

        _logs.set_logger_provider(logger_provider)
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        handler.addFilter(_TelemetryNoiseFilter())
        handler.addFilter(_LogRecordEnrichmentFilter())
        logging.getLogger().addHandler(handler)
        LoggingInstrumentor().instrument(set_logging_format=True, logger_provider=logger_provider)

        metric_reader = PeriodicExportingMetricReader(
            AzureMonitorMetricExporter(connection_string=connection_string)
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)

        logging.getLogger("azure").setLevel(logging.ERROR)
        logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
        logging.getLogger("azure.monitor.opentelemetry").setLevel(logging.ERROR)

        RequestsInstrumentor().instrument()
        _telemetry_configured = True

    if app is not None and not _fastapi_instrumented:
        FastAPIInstrumentor.instrument_app(app)
        _fastapi_instrumented = True


def get_langchain_tracer() -> AzureAIOpenTelemetryTracer | None:
    global _langchain_tracer

    if _langchain_tracer is not None:
        return _langchain_tracer

    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        logging.getLogger(__name__).warning(
            "LangChain tracing disabled: missing APPLICATIONINSIGHTS_CONNECTION_STRING"
        )
        return None

    settings = get_settings()
    enable_content_recording = os.getenv("OTEL_RECORD_CONTENT", "true").lower() == "true"
    _langchain_tracer = AzureAIOpenTelemetryTracer(
        connection_string=connection_string,
        enable_content_recording=enable_content_recording,
        name=settings.service_name,
    )
    return _langchain_tracer
