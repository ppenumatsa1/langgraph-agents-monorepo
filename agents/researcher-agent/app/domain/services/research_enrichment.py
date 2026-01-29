import asyncio

from app.core.exceptions import ExternalServiceError
from app.domain.repo.web_search_repo import search_web
from app.langgraph.state import ResearchState


async def enrich_with_research(state: ResearchState, config: dict | None = None) -> ResearchState:
    try:
        sources = await asyncio.to_thread(search_web, state.topic, config=config)
    except Exception as exc:
        raise ExternalServiceError("Web search failed", cause=exc) from exc
    return ResearchState(
        topic=state.topic,
        audience=state.audience,
        tone=state.tone,
        length=state.length,
        time_range=state.time_range,
        sources=sources,
        draft=state.draft,
        review_notes=state.review_notes,
        summary=state.summary,
    )
