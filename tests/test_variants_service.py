from app.services.variants import _append_sentence


def test_append_sentence_adds_missing_period() -> None:
    result = _append_sentence("Explain how this works", "Provide details.")

    assert result == "Explain how this works. Provide details."


def test_append_sentence_avoids_double_punctuation() -> None:
    result = _append_sentence("Explain how this works?", "Provide details.")

    assert result == "Explain how this works? Provide details."
