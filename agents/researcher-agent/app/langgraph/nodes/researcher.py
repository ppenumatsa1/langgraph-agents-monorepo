import json
import logging

from opentelemetry import trace

from app.core.llm import chat_completion
from app.domain.services.research_enrichment import enrich_with_research
from app.langgraph.prompts import RESEARCHER_PROMPT
from app.langgraph.state import ResearchState

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app.langgraph.nodes.researcher")


async def researcher_node(state: ResearchState, config: dict | None = None) -> ResearchState:
    with tracer.start_as_current_span("node.researcher") as span:
        span.set_attribute("app.topic", state.topic)
        logger.info("Researcher node started", extra={"topic": state.topic})
        enriched_state = state
        if not state.sources:
            enriched_state = await enrich_with_research(state, config=config)

        summary = await _summarize(enriched_state, config)
        span.set_attribute("app.sources.count", len(enriched_state.sources))
        logger.info(
            "Researcher node completed",
            extra={"topic": enriched_state.topic, "sources_count": len(enriched_state.sources)},
        )
        return ResearchState(
            topic=enriched_state.topic,
            audience=enriched_state.audience,
            tone=enriched_state.tone,
            length=enriched_state.length,
            time_range=enriched_state.time_range,
            sources=enriched_state.sources,
            research_summary=summary,
            draft=enriched_state.draft,
            review_notes=enriched_state.review_notes,
            summary=enriched_state.summary,
        )


async def _summarize(state: ResearchState, config: dict | None = None) -> str:
    with tracer.start_as_current_span("node.researcher.summarize"):
        logger.info("Researcher summarize started", extra={"topic": state.topic})
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
        logger.info("Researcher summarize completed", extra={"topic": state.topic})
        return response.strip() or ""
