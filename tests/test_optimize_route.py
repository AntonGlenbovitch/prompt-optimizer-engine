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


def test_variants_returns_original_and_generated_variants() -> None:
    prompt = "Summarize this article"
    response = client.post("/variants", json={"prompt": prompt})

    assert response.status_code == 200
    payload = response.json()

    assert payload["original"] == prompt
    assert len(payload["variants"]) == 3
    assert [variant["type"] for variant in payload["variants"]] == [
        "minimal",
        "balanced",
        "detailed",
    ]


def test_optimize_basic_removes_question_style_task_text() -> None:
    prompt = "Can you explain what RAG systems are and how they work?"
    response = client.post("/optimize-basic", json={"prompt": prompt})

    assert response.status_code == 200
    optimized = response.json()["optimized"]

    assert "Explain RAG systems and how they work" in optimized
    assert "?" not in optimized


def test_detailed_variant_scores_higher_than_balanced() -> None:
    prompt = "Explain what RAG systems are and how they work"
    response = client.post("/optimize", json={"prompt": prompt})

    assert response.status_code == 200
    variants = {variant["type"]: variant for variant in response.json()["variants"]}

    assert variants["detailed"]["score"] > variants["balanced"]["score"]
