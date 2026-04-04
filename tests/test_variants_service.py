from app.services.variants import _append_sentence
from app.services.variants import _minimal_variant


def test_append_sentence_adds_missing_period() -> None:
    result = _append_sentence("Explain how this works", "Provide details.")

    assert result == "Explain how this works. Provide details."


def test_append_sentence_avoids_double_punctuation() -> None:
    result = _append_sentence("Explain how this works?", "Provide details.")

    assert result == "Explain how this works? Provide details."


def test_minimal_variant_preserves_acronyms_and_removes_what_are_pattern() -> None:
    prompt = "Can you please explain what RAG systems are and how they work?"

    assert _minimal_variant(prompt) == "Explain RAG systems and how they work"


def test_minimal_variant_removes_trailing_period_and_capitalizes() -> None:
    prompt = "please summarize retrieval augmented generation."

    assert _minimal_variant(prompt) == "Summarize retrieval augmented generation"
