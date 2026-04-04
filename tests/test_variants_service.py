from app.services.variants import _append_sentence
from app.services.variants import _detailed_variant
from app.services.variants import _minimal_variant


def test_append_sentence_adds_missing_period() -> None:
    result = _append_sentence("Explain how this works", "Provide details.")

    assert result == "Explain how this works. Provide details."


def test_append_sentence_avoids_double_punctuation() -> None:
    result = _append_sentence("Explain how this works?", "Provide details.")

    assert result == "Explain how this works. Provide details."


def test_minimal_variant_preserves_acronyms_and_removes_what_are_pattern() -> None:
    prompt = "Can you please explain what RAG systems are and how they work?"

    assert _minimal_variant(prompt) == "Explain RAG systems and how they work"


def test_minimal_variant_removes_trailing_period_and_capitalizes() -> None:
    prompt = "please summarize retrieval augmented generation."

    assert _minimal_variant(prompt) == "Summarize retrieval augmented generation"


def test_detailed_variant_uses_multi_sentence_task_block() -> None:
    balanced = (
        "Role:\n"
        "You are an expert assistant.\n\n"
        "Task:\n"
        "Explain what RAG systems are and how they work?\n\n"
        "Constraints:\n"
        "- Be concise"
    )

    detailed = _detailed_variant(balanced)

    assert "Task:\nExplain RAG systems and how they work.\nProvide a step-by-step" in detailed
    assert "work?" not in detailed
