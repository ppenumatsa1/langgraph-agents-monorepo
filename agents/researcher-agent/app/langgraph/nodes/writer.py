import json

from app.core.llm import chat_completion
from app.langgraph.prompts import WRITER_PROMPT
from app.langgraph.state import ResearchState


def writer_node(state: ResearchState) -> ResearchState:
    sources_payload = json.dumps(state.sources[:5], ensure_ascii=False)
    user_prompt = (
        f"Topic: {state.topic}\n"
        f"Audience: {state.audience or 'general'}\n"
        f"Tone: {state.tone or 'neutral'}\n"
        f"Length: {state.length or 'short'}\n"
        f"Research Summary: {state.research_summary}\n"
        f"Sources: {sources_payload}\n\n"
        "Write a concise markdown draft with citations [1], [2], [3] aligned to sources."
    )
    draft = chat_completion(WRITER_PROMPT, user_prompt).strip() or state.draft
    return ResearchState(
        topic=state.topic,
        audience=state.audience,
        tone=state.tone,
        length=state.length,
        time_range=state.time_range,
        sources=state.sources,
        research_summary=state.research_summary,
        draft=draft,
        review_notes=state.review_notes,
        summary=state.summary,
    )
