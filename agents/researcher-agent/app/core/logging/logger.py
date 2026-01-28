import json
import logging
from datetime import datetime, timezone

from opentelemetry import trace


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        try:
            span_context = trace.get_current_span().get_span_context()
            if span_context and span_context.is_valid:
                trace_id = format(span_context.trace_id, "032x")
                span_id = format(span_context.span_id, "016x")
                payload["trace_id"] = trace_id
                payload["span_id"] = span_id
                payload["correlation_id"] = trace_id
        except Exception:
            pass
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)
