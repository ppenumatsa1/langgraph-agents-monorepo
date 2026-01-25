from __future__ import annotations

from typing import Any

from ddgs import DDGS


def web_search(query: str, max_results: int = 6, region: str = "us-en") -> list[dict[str, str]]:
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

    return [r for r in results if r.get("url")]


def _normalize_result(item: dict[str, Any]) -> dict[str, str]:
    return {
        "title": str(item.get("title") or item.get("source") or "").strip(),
        "url": str(item.get("url") or item.get("link") or item.get("href") or "").strip(),
        "snippet": str(item.get("snippet") or item.get("body") or item.get("excerpt") or "").strip(),
        "date": str(item.get("date") or item.get("published") or "").strip(),
        "source": str(item.get("source") or item.get("publisher") or "").strip(),
    }
