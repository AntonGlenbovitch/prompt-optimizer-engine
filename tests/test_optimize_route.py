from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_optimize_returns_mock_response() -> None:
    response = client.post("/optimize", json={"prompt": "Make this better"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["original_prompt"] == "Make this better"
    assert len(payload["variants"]) == 3
    assert [variant["type"] for variant in payload["variants"]] == [
        "minimal",
        "balanced",
        "detailed",
    ]


def test_optimize_basic_returns_original_and_optimized() -> None:
    prompt = "Please summarize summarize this article"
    response = client.post("/optimize-basic", json={"prompt": prompt})

    assert response.status_code == 200
    payload = response.json()

    assert payload["original"] == prompt
    assert payload["optimized"].startswith("Role:\nYou are an expert assistant.")
