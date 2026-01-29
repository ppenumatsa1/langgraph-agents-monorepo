import json

from app.core.llm import chat_completion
from app.langgraph.prompts import RESEARCHER_PROMPT
from app.langgraph.state import ResearchState


async def researcher_node(state: ResearchState, config: dict | None = None) -> ResearchState:
    summary = await _summarize(state, config)
    return ResearchState(
        topic=state.topic,
        audience=state.audience,
        tone=state.tone,
        length=state.length,
        time_range=state.time_range,
        sources=state.sources,
        research_summary=summary,
        draft=state.draft,
        review_notes=state.review_notes,
        summary=state.summary,
    )


async def _summarize(state: ResearchState, config: dict | None = None) -> str:
    sources_payload = json.dumps(state.sources[:5], ensure_ascii=False)
    user_prompt = (
        f"Topic: {state.topic}\n"
        f"Audience: {state.audience or 'general'}\n"
        f"Tone: {state.tone or 'neutral'}\n"
        f"Length: {state.length or 'short'}\n"
        f"Sources: {sources_payload}\n\n"
        "Return 4-6 concise bullet points summarizing the key insights."
    )
    response = await chat_completion(RESEARCHER_PROMPT, user_prompt, config=config)
    return response.strip() or ""
