from __future__ import annotations

from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    return _correlation_id_ctx.get()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get("x-correlation-id")
        correlation_id = incoming or str(uuid4())
        token = _correlation_id_ctx.set(correlation_id)
        request.state.correlation_id = correlation_id

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

        if correlation_id:
            response.headers["x-correlation-id"] = correlation_id

        _correlation_id_ctx.reset(token)

        return response
