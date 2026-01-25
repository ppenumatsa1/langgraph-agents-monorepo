import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.domain.schemas.research import ResearchRequest, ResearchResponse
from app.domain.services.research_service import run_research, stream_research
from app.langgraph.state import ResearchState

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
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
    result = run_research(state)
    return ResearchResponse(
        topic=result.topic,
        draft=result.draft,
        review_notes=result.review_notes,
        summary=result.summary,
    )


@router.post("/research/stream")
def research_stream(request: ResearchRequest) -> StreamingResponse:
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

    def event_stream():
        for snapshot in stream_research(state):
            payload = {
                "topic": snapshot.topic,
                "sources": snapshot.sources,
                "research_summary": snapshot.research_summary,
                "draft": snapshot.draft,
                "review_notes": snapshot.review_notes,
                "summary": snapshot.summary,
            }
            yield _sse("update", payload)
        yield _sse("done", {"status": "complete"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
