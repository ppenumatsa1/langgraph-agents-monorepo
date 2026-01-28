from __future__ import annotations

from fastapi import Request
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get("x-correlation-id")
        response = await call_next(request)

        span_context = trace.get_current_span().get_span_context()
        if span_context and span_context.is_valid:
            trace_flags = format(int(span_context.trace_flags), "02x")
            traceparent = (
                "00-"
                f"{format(span_context.trace_id, '032x')}-"
                f"{format(span_context.span_id, '016x')}-"
                f"{trace_flags}"
            )
            response.headers["traceparent"] = traceparent

        correlation_id = incoming or (format(span_context.trace_id, "032x") if span_context else "")
        if correlation_id:
            response.headers["x-correlation-id"] = correlation_id

        return response
