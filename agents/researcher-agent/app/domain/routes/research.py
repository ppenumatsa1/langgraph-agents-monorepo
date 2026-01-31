import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from opentelemetry import context as otel_context
from opentelemetry import trace

from app.domain.schemas.research import ResearchRequest, ResearchResponse
from app.domain.services.research_service import run_research, stream_research
from app.langgraph.state import ResearchState

router = APIRouter()
logger = logging.getLogger("app.routes.research")
tracer = trace.get_tracer(__name__)


@router.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest) -> ResearchResponse:
    with tracer.start_as_current_span("router.research") as span:
        span.set_attribute("app.topic", request.topic)
        logger.info("Research request received", extra={"topic": request.topic})
        state = ResearchState(
            topic=request.topic,
            audience=request.audience,
            tone=request.tone,
            length=request.length,
            time_range=request.time_range,
            sources=[],
            research_summary="",
            draft="",
            review_notes=[],
            summary="",
        )
        result = await run_research(state)
        logger.info("Research request completed", extra={"topic": request.topic})
        return ResearchResponse(
            topic=result.topic,
            draft=result.draft,
            review_notes=result.review_notes,
            summary=result.summary,
        )


@router.post("/research/stream")
async def research_stream(request: ResearchRequest) -> StreamingResponse:
    logger.info("Research stream request received", extra={"topic": request.topic})
    state = ResearchState(
        topic=request.topic,
        audience=request.audience,
        tone=request.tone,
        length=request.length,
        time_range=request.time_range,
        sources=[],
        research_summary="",
        draft="",
        review_notes=[],
        summary="",
    )

    stream_context = otel_context.get_current()

    async def event_stream():
        token = otel_context.attach(stream_context)
        try:
            with tracer.start_as_current_span("router.research_stream") as span:
                span.set_attribute("app.topic", request.topic)
                async for snapshot in stream_research(state):
                    payload = {
                        "topic": snapshot.topic,
                        "sources": snapshot.sources,
                        "research_summary": snapshot.research_summary,
                        "draft": snapshot.draft,
                        "review_notes": snapshot.review_notes,
                        "summary": snapshot.summary,
                    }
                    yield _sse("update", payload)
                logger.info("Research stream request completed", extra={"topic": request.topic})
                yield _sse("done", {"status": "complete"})
        finally:
            otel_context.detach(token)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
