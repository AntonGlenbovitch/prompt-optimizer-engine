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
