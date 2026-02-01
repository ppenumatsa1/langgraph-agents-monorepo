import logging

from langgraph.graph import END, StateGraph

from app.langgraph.nodes.researcher import researcher_node
from app.langgraph.nodes.reviewer import reviewer_node
from app.langgraph.nodes.writer import writer_node
from app.langgraph.state import ResearchState

logger = logging.getLogger("app.langgraph.graph")


def build_graph():
    logger.info("Building LangGraph workflow")
    graph = StateGraph(ResearchState)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", END)

    compiled = graph.compile()
    logger.info("LangGraph workflow ready")
    return compiled
