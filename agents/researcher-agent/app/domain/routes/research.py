from fastapi import APIRouter

from app.domain.schemas.research import ResearchRequest, ResearchResponse
from app.domain.services.research_service import run_research
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
