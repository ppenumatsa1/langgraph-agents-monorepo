import os

import httpx
import pytest


@pytest.mark.skipif(not os.getenv("SMOKE_BASE_URL"), reason="SMOKE_BASE_URL not set")
def test_live_health() -> None:
    base_url = os.environ["SMOKE_BASE_URL"].rstrip("/")
    response = httpx.get(f"{base_url}/health", timeout=10)
    assert response.status_code == 200


@pytest.mark.skipif(not os.getenv("SMOKE_BASE_URL"), reason="SMOKE_BASE_URL not set")
def test_live_research() -> None:
    base_url = os.environ["SMOKE_BASE_URL"].rstrip("/")
    response = httpx.post(
        f"{base_url}/v1/research",
        json={"topic": "AI safety"},
        timeout=60,
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("topic") == "AI safety"
