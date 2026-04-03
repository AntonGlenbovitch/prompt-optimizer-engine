"""Prompt analysis service."""

from __future__ import annotations


def analyze_prompt(text: str) -> dict:
    """Analyze a prompt and return score with detected issues."""
    cleaned_text = text.strip()
    analysis_text = cleaned_text.lower()
    words = analysis_text.split()
    issues: list[str] = []
    score = 50
    action_verbs = {"explain", "summarize", "list", "describe", "analyze"}

    word_count = len(words)
    if word_count < 5:
        issues.append("too short")
        score -= 25
    elif word_count > 40:
        issues.append("too verbose")
        score -= 15

    if len(set(words)) != len(words):
        issues.append("repetitive wording")
        score -= 20

    has_action_verb = any(word in action_verbs for word in words)
    if has_action_verb:
        score += 10
    else:
        issues.append("unclear instruction")
        score -= 25

    if "role:" in analysis_text and "task:" in analysis_text:
        score += 20

    if "constraints:" in analysis_text:
        score += 15

    sentence_count = sum(analysis_text.count(char) for char in ".!?")
    if sentence_count >= 2:
        score += 10

    score = max(0, min(100, score))
    return {"score": score, "issues": issues}
