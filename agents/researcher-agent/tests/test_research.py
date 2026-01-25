from fastapi.testclient import TestClient

from app.main import create_app


def test_research() -> None:
    client = TestClient(create_app())
    response = client.post("/v1/research", json={"topic": "AI safety"})
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "AI safety"
    assert "summary" in body
