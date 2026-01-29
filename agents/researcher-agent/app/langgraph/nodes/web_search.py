from __future__ import annotations

import json
from typing import Any

from langgraph.prebuilt import ToolNode

from app.langgraph.state import ResearchState
from app.langgraph.tools.web_search import web_search_tool

_tool_node = ToolNode([web_search_tool], name="web_search")


async def web_search_node(state: ResearchState, config: dict | None = None) -> ResearchState:
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

    if config is None:
        result = await _tool_node.ainvoke(tool_calls)
    else:
        result = await _tool_node.ainvoke(tool_calls, config=config)

    messages = result if isinstance(result, list) else result.get("messages", [])
    sources = _extract_sources(messages)

    return ResearchState(
        topic=state.topic,
        audience=state.audience,
        tone=state.tone,
        length=state.length,
        time_range=state.time_range,
        sources=sources,
        research_summary=state.research_summary,
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
