from app.langgraph.tools.web_search import web_search


def search_web(query: str, max_results: int = 6, region: str = "us-en") -> list[dict[str, str]]:
    return web_search(query=query, max_results=max_results, region=region)
