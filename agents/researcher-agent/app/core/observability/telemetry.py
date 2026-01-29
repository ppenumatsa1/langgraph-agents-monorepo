import logging
import os

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter, AzureMonitorTraceExporter
from langchain_azure_ai.callbacks.tracers import AzureAIOpenTelemetryTracer
from opentelemetry import _logs, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.utils.config import get_settings

_telemetry_configured = False
_fastapi_instrumented = False
_langchain_tracer: AzureAIOpenTelemetryTracer | None = None


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
        tracer_provider.add_span_processor(
            BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=connection_string))
        )
        trace.set_tracer_provider(tracer_provider)

        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(AzureMonitorLogExporter(connection_string=connection_string))
        )

        _logs.set_logger_provider(logger_provider)
        logging.getLogger().addHandler(
            LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        )
        LoggingInstrumentor().instrument(set_logging_format=True, logger_provider=logger_provider)
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
