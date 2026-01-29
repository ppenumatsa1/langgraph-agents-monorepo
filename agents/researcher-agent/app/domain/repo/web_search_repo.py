from app.langgraph.tools.web_search import web_search, web_search_tool


def search_web(
    query: str,
    max_results: int = 6,
    region: str = "us-en",
    config: dict | None = None,
) -> list[dict[str, str]]:
    if config is None:
        return web_search(query=query, max_results=max_results, region=region)
    return web_search_tool.invoke(
        {"query": query, "max_results": max_results, "region": region}, config=config
    )
