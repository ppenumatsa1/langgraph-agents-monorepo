import asyncio

from app.domain.services.research_service import run_research
from app.langgraph.state import ResearchState


def test_end_to_end_flow_with_mocks(monkeypatch) -> None:
    from app.langgraph.nodes import researcher, reviewer, writer
    from app.langgraph.tools import web_search as web_search_tools

    def fake_search_web(query: str, max_results: int = 6, region: str = "us-en"):
        return [
            {
                "title": "Test Source",
                "url": "https://example.com",
                "snippet": "Snippet",
                "date": "2026-01-01",
                "source": "Example",
            }
        ]

    async def fake_chat_completion(
        system_prompt: str, user_prompt: str, config: dict | None = None
    ) -> str:
        if "review_notes" in user_prompt:
            return '{"review_notes": ["OK"], "summary": "Looks good."}'
        if "Research Summary" in user_prompt:
            return "Draft content."
        return "- Insight 1\n- Insight 2"

    monkeypatch.setattr(web_search_tools, "web_search", fake_search_web)
    monkeypatch.setattr(researcher, "chat_completion", fake_chat_completion)
    monkeypatch.setattr(writer, "chat_completion", fake_chat_completion)
    monkeypatch.setattr(reviewer, "chat_completion", fake_chat_completion)

    state = ResearchState(
        topic="Test topic",
        audience=None,
        tone=None,
        length=None,
        time_range=None,
    )

    result = asyncio.run(run_research(state))

    assert result.research_summary
    assert result.draft
    assert result.review_notes == ["OK"]
    assert result.summary == "Looks good."
