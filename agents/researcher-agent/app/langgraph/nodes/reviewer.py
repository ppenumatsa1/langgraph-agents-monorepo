import json
import logging

from opentelemetry import trace

from app.core.llm import chat_completion
from app.langgraph.prompts import REVIEWER_PROMPT
from app.langgraph.state import ResearchState

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app.langgraph.nodes.reviewer")


async def reviewer_node(state: ResearchState, config: dict | None = None) -> ResearchState:
    with tracer.start_as_current_span("node.reviewer") as span:
        span.set_attribute("app.topic", state.topic)
        logger.info("Reviewer node started", extra={"topic": state.topic})
        review_notes, summary = await _review(state, config)
        logger.info("Reviewer node completed", extra={"topic": state.topic})
        return ResearchState(
            topic=state.topic,
            audience=state.audience,
            tone=state.tone,
            length=state.length,
            time_range=state.time_range,
            sources=state.sources,
            research_summary=state.research_summary,
            draft=state.draft,
            review_notes=review_notes,
            summary=summary,
        )


async def _review(state: ResearchState, config: dict | None = None) -> tuple[list[str], str]:
    with tracer.start_as_current_span("node.reviewer.review"):
        logger.info("Reviewer review started", extra={"topic": state.topic})
        sources_payload = json.dumps(state.sources[:5], ensure_ascii=False)
        user_prompt = (
            f"Topic: {state.topic}\n"
            f"Draft: {state.draft}\n"
            f"Sources: {sources_payload}\n\n"
            "Return JSON with keys review_notes (list of strings) and summary (string)."
        )
        response = await chat_completion(REVIEWER_PROMPT, user_prompt, config=config)
        try:
            parsed = json.loads(response)
            notes = parsed.get("review_notes") or []
            summary = parsed.get("summary") or ""
            logger.info("Reviewer review completed", extra={"topic": state.topic})
            return list(notes), str(summary)
        except Exception:
            logger.info("Reviewer review completed", extra={"topic": state.topic})
            return ["Review completed."], response.strip()
