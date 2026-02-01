import logging
from dataclasses import asdict
from typing import Any, AsyncIterator

from opentelemetry import trace

from app.core.exceptions import ResearcherAgentError
from app.core.observability import get_langchain_tracer
from app.langgraph.graph import build_graph
from app.langgraph.state import ResearchState

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app.services.research")


async def run_research(state: ResearchState) -> ResearchState:
    with tracer.start_as_current_span("service.run_research") as span:
        span.set_attribute("app.topic", state.topic)
        logger.info("Service run_research started", extra={"topic": state.topic})
        graph = build_graph()
        config = _get_graph_config()
        graph_input = _to_input(state)
        try:
            if config is None:
                result: Any = await graph.ainvoke(graph_input)
            else:
                result = await graph.ainvoke(graph_input, config=config)
            logger.info("Service run_research completed", extra={"topic": state.topic})
            return _to_state(result)
        except ResearcherAgentError:
            raise
        except Exception as exc:
            raise ResearcherAgentError("Research flow failed", cause=exc) from exc


async def stream_research(state: ResearchState) -> AsyncIterator[ResearchState]:
    with tracer.start_as_current_span("service.stream_research") as span:
        span.set_attribute("app.topic", state.topic)
        logger.info("Service stream_research started", extra={"topic": state.topic})
        graph = build_graph()
        config = _get_graph_config()
        graph_input = _to_input(state)
        try:
            if config is None:
                stream = graph.astream(graph_input, stream_mode="values")
            else:
                stream = graph.astream(graph_input, stream_mode="values", config=config)
            async for value in stream:
                yield _to_state(value)
            logger.info("Service stream_research completed", extra={"topic": state.topic})
        except ResearcherAgentError:
            raise
        except Exception as exc:
            raise ResearcherAgentError("Research stream failed", cause=exc) from exc


def _to_state(result: Any) -> ResearchState:
    if isinstance(result, ResearchState):
        return result
    return ResearchState(**result)


def _to_input(state: ResearchState) -> dict:
    return asdict(state)


def _get_graph_config() -> dict | None:
    tracer = get_langchain_tracer()
    if tracer is None:
        return None
    config: dict[str, Any] = {"callbacks": [tracer]}

    span_context = trace.get_current_span().get_span_context()
    if span_context and span_context.is_valid:
        config["configurable"] = {"thread_id": format(span_context.trace_id, "032x")}

    return config
