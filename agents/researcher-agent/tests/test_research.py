import httpx
import pytest

from app.langgraph.state import ResearchState
from app.main import create_app


@pytest.mark.asyncio
async def test_research(monkeypatch) -> None:
    from app.domain.routes import research as research_routes

    async def fake_run(state: ResearchState) -> ResearchState:
        return ResearchState(
            topic=state.topic,
            audience=state.audience,
            tone=state.tone,
            length=state.length,
            time_range=state.time_range,
            sources=[],
            research_summary="Summary",
            draft="Draft",
            review_notes=["Note"],
            summary="Final",
        )

    monkeypatch.setattr(research_routes, "run_research", fake_run)

    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/research", json={"topic": "AI safety"})
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "AI safety"
    assert "summary" in body


@pytest.mark.asyncio
async def test_research_stream(monkeypatch) -> None:
    from app.domain.routes import research as research_routes

    async def fake_stream(state: ResearchState):
        yield ResearchState(
            topic=state.topic,
            audience=state.audience,
            tone=state.tone,
            length=state.length,
            time_range=state.time_range,
            sources=[{"title": "T", "url": "https://example.com"}],
            research_summary="Summary",
            draft="Draft",
            review_notes=["Note"],
            summary="Final",
        )

    monkeypatch.setattr(research_routes, "stream_research", fake_stream)

    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream(
            "POST", "/v1/research/stream", json={"topic": "AI safety"}
        ) as response:
            assert response.status_code == 200
            chunks = [chunk async for chunk in response.aiter_text()]
            data = "".join(chunks)

    assert "event: update" in data
    assert "event: done" in data
