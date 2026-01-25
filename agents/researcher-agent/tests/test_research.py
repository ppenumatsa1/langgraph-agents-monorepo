from fastapi.testclient import TestClient

from app.langgraph.state import ResearchState
from app.main import create_app


def test_research() -> None:
    client = TestClient(create_app())
    response = client.post("/v1/research", json={"topic": "AI safety"})
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "AI safety"
    assert "summary" in body


def test_research_stream(monkeypatch) -> None:
    from app.domain.routes import research as research_routes

    def fake_stream(state: ResearchState):
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

    client = TestClient(create_app())
    with client.stream("POST", "/v1/research/stream", json={"topic": "AI safety"}) as response:
        assert response.status_code == 200
        data = "".join(response.iter_text())

    assert "event: update" in data
    assert "event: done" in data
