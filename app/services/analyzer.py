"""Prompt analysis service."""

from __future__ import annotations


def analyze_prompt(text: str) -> dict:
    """Analyze a prompt and return score with detected issues."""
    cleaned_text = text.strip()
    words = cleaned_text.lower().split()
    issues: list[str] = []
    score = 100

    word_count = len(words)
    if word_count < 5:
        issues.append("too short")
        score -= 20
    elif word_count > 30:
        issues.append("too verbose")
        score -= 15

    if len(set(words)) != len(words):
        issues.append("repetitive wording")
        score -= 20

    action_verbs = {"explain", "summarize", "list", "describe", "analyze"}
    if not any(word in action_verbs for word in words):
        issues.append("unclear instruction")
        score -= 25

    score = max(score, 0)
    return {"score": score, "issues": issues}
