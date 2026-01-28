from typing import Any, AsyncIterator

from app.core.exceptions import ResearcherAgentError
from app.langgraph.graph import build_graph
from app.langgraph.state import ResearchState


async def run_research(state: ResearchState) -> ResearchState:
    graph = build_graph()
    try:
        result: Any = await graph.ainvoke(state)
        return _to_state(result)
    except ResearcherAgentError:
        raise
    except Exception as exc:
        raise ResearcherAgentError("Research flow failed", cause=exc) from exc


async def stream_research(state: ResearchState) -> AsyncIterator[ResearchState]:
    graph = build_graph()
    try:
        async for value in graph.astream(state, stream_mode="values"):
            yield _to_state(value)
    except ResearcherAgentError:
        raise
    except Exception as exc:
        raise ResearcherAgentError("Research stream failed", cause=exc) from exc


def _to_state(result: Any) -> ResearchState:
    if isinstance(result, ResearchState):
        return result
    return ResearchState(**result)
