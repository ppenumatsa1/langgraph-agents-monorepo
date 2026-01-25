from app.domain.repo.web_search_repo import search_web
from app.langgraph.state import ResearchState


def enrich_with_research(state: ResearchState) -> ResearchState:
    sources = search_web(state.topic)
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
