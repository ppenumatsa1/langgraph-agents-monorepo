from langgraph.graph import END, StateGraph

from app.langgraph.nodes.researcher import researcher_node
from app.langgraph.nodes.reviewer import reviewer_node
from app.langgraph.nodes.web_search import web_search_node
from app.langgraph.nodes.writer import writer_node
from app.langgraph.state import ResearchState


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("web_search", web_search_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)

    graph.set_entry_point("web_search")
    graph.add_edge("web_search", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", END)

    return graph.compile()
