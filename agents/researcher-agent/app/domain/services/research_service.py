from typing import Any

from app.langgraph.graph import build_graph
from app.langgraph.state import ResearchState


def run_research(state: ResearchState) -> ResearchState:
    graph = build_graph()
    result: Any = graph.invoke(state)
    return _to_state(result)


def _to_state(result: Any) -> ResearchState:
    if isinstance(result, ResearchState):
        return result
    return ResearchState(**result)
