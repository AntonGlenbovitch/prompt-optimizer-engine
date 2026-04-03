from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_returns_prompt_score_and_issues() -> None:
    prompt = "Summarize summarize this"
    response = client.post("/analyze", json={"prompt": prompt})

    assert response.status_code == 200
    payload = response.json()

    assert payload["prompt"] == prompt
    assert isinstance(payload["score"], int)
    assert isinstance(payload["issues"], list)
