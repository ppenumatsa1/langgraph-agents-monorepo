from typing import Any, Iterable

from app.langgraph.graph import build_graph
from app.langgraph.state import ResearchState


def run_research(state: ResearchState) -> ResearchState:
    graph = build_graph()
    result: Any = graph.invoke(state)
    return _to_state(result)


def stream_research(state: ResearchState) -> Iterable[ResearchState]:
    graph = build_graph()
    for value in graph.stream(state, stream_mode="values"):
        yield _to_state(value)


def _to_state(result: Any) -> ResearchState:
    if isinstance(result, ResearchState):
        return result
    return ResearchState(**result)
