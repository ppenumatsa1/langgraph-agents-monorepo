import json
import logging
from datetime import datetime, timezone

from app.core.observability.telemetry import (
    get_current_correlation_id,
    get_current_span_id,
    get_current_trace_id,
)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        correlation_id = get_current_correlation_id()
        if correlation_id and not hasattr(record, "correlation_id"):
            setattr(record, "correlation_id", correlation_id)
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        trace_id = getattr(record, "trace_id", None) or get_current_trace_id()
        span_id = getattr(record, "span_id", None) or get_current_span_id()
        correlation_id = getattr(record, "correlation_id", None) or get_current_correlation_id()
        if trace_id:
            payload["trace_id"] = trace_id
        if span_id:
            payload["span_id"] = span_id
        if correlation_id:
            payload["correlation_id"] = correlation_id
        payload.update(self._extra_fields(record))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _extra_fields(record: logging.LogRecord) -> dict:
        reserved = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "message",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }
        extras: dict = {}
        for key, value in record.__dict__.items():
            if key in reserved or key.startswith("_"):
                continue
            try:
                json.dumps(value, ensure_ascii=False)
                extras[key] = value
            except TypeError:
                extras[key] = str(value)
        return extras


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addFilter(CorrelationIdFilter())
    root.addHandler(handler)
