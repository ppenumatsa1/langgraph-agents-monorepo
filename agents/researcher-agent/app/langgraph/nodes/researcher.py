import json

from app.core.llm import chat_completion
from app.domain.services.research_enrichment import enrich_with_research
from app.langgraph.prompts import RESEARCHER_PROMPT
from app.langgraph.state import ResearchState


async def researcher_node(state: ResearchState) -> ResearchState:
    enriched = await enrich_with_research(state)
    summary = await _summarize(enriched)
    return ResearchState(
        topic=enriched.topic,
        audience=enriched.audience,
        tone=enriched.tone,
        length=enriched.length,
        time_range=enriched.time_range,
        sources=enriched.sources,
        research_summary=summary,
        draft=enriched.draft,
        review_notes=enriched.review_notes,
        summary=enriched.summary,
    )


async def _summarize(state: ResearchState) -> str:
    sources_payload = json.dumps(state.sources[:5], ensure_ascii=False)
    user_prompt = (
        f"Topic: {state.topic}\n"
        f"Audience: {state.audience or 'general'}\n"
        f"Tone: {state.tone or 'neutral'}\n"
        f"Length: {state.length or 'short'}\n"
        f"Sources: {sources_payload}\n\n"
        "Return 4-6 concise bullet points summarizing the key insights."
    )
    response = await chat_completion(RESEARCHER_PROMPT, user_prompt)
    return response.strip() or ""
