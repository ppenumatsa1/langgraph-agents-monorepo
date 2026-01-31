import json
from typing import Any

from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from opentelemetry import trace

from app.core.exceptions import ExternalServiceError
from app.langgraph.state import ResearchState
from app.langgraph.tools.web_search import web_search_tool

_tool_node = ToolNode([web_search_tool], name="web_search")
tracer = trace.get_tracer(__name__)


async def enrich_with_research(state: ResearchState, config: dict | None = None) -> ResearchState:
    try:
        with tracer.start_as_current_span("service.enrich_with_research") as span:
            span.set_attribute("app.topic", state.topic)
            tool_calls = [
                {
                    "id": "web_search-1",
                    "name": "web_search",
                    "type": "tool_call",
                    "args": {
                        "query": state.topic,
                        "max_results": 6,
                        "region": "us-en",
                    },
                }
            ]
            ai_message = AIMessage(content="", tool_calls=tool_calls)
            if config is None:
                result = await _tool_node.ainvoke({"messages": [ai_message]})
            else:
                result = await _tool_node.ainvoke({"messages": [ai_message]}, config=config)

            messages = result.get("messages", []) if isinstance(result, dict) else result
            sources = _extract_sources(messages)
            span.set_attribute("app.sources.count", len(sources))
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


def _extract_sources(messages: list[Any]) -> list[dict[str, str]]:
    if not messages:
        return []

    content = getattr(messages[0], "content", None)
    if isinstance(content, list):
        return content
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []
    return []
