def estimate_tokens(text: str) -> int:
    """Estimate token count by multiplying stripped word count by 1.3.

    This uses a simple deterministic approximation where each whitespace-separated
    word contributes about 1.3 tokens.
    """
    normalized_text = text.strip()
    if not normalized_text:
        return 0

    return int(len(normalized_text.split()) * 1.3)
