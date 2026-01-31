from __future__ import annotations

from typing import Any

from ddgs import DDGS
from langchain.tools import tool
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def web_search(query: str, max_results: int = 6, region: str = "us-en") -> list[dict[str, str]]:
    with tracer.start_as_current_span("tool.web_search") as span:
        span.set_attribute("app.query", query)
        span.set_attribute("app.max_results", max_results)
        span.set_attribute("app.region", region)
        results: list[dict[str, str]] = []
        with DDGS() as ddgs:
            try:
                for item in ddgs.news(query, region=region, max_results=max_results):
                    results.append(_normalize_result(item))
            except Exception:
                pass

            if not results:
                for item in ddgs.text(query, region=region, max_results=max_results):
                    results.append(_normalize_result(item))

        filtered = [r for r in results if r.get("url")]
        span.set_attribute("app.results.count", len(filtered))
        return filtered


@tool("web_search")
def web_search_tool(
    query: str, max_results: int = 6, region: str = "us-en"
) -> list[dict[str, str]]:
    """Search the web for relevant sources."""
    return web_search(query=query, max_results=max_results, region=region)


def _normalize_result(item: dict[str, Any]) -> dict[str, str]:
    return {
        "title": str(item.get("title") or item.get("source") or "").strip(),
        "url": str(item.get("url") or item.get("link") or item.get("href") or "").strip(),
        "snippet": str(
            item.get("snippet") or item.get("body") or item.get("excerpt") or ""
        ).strip(),
        "date": str(item.get("date") or item.get("published") or "").strip(),
        "source": str(item.get("source") or item.get("publisher") or "").strip(),
    }
