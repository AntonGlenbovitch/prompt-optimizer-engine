"""Prompt optimization service."""

from __future__ import annotations

import re


_FILLER_PHRASES = ["please", "maybe", "can you", "i think", "could you"]
_TASK_KEYWORDS = {
    "explain": "Explain",
    "summarize": "Summarize",
    "list": "List",
}
_KNOWN_VERBS = {
    "explain",
    "summarize",
    "list",
    "describe",
    "analyze",
    "write",
    "tell",
    "show",
    "give",
    "create",
    "make",
}


def _remove_fillers(text: str) -> str:
    words = text.split()
    filler_patterns = [filler.split() for filler in _FILLER_PHRASES]

    cleaned_words: list[str] = []
    i = 0
    while i < len(words):
        matched_pattern_length = 0
        for pattern in filler_patterns:
            pattern_length = len(pattern)
            segment = words[i : i + pattern_length]
            segment_lower = [word.lower() for word in segment]
            if segment_lower == pattern:
                matched_pattern_length = pattern_length
                break

        if matched_pattern_length:
            i += matched_pattern_length
            continue

        cleaned_words.append(words[i])
        i += 1

    return " ".join(cleaned_words)


def _remove_duplicate_words(text: str) -> str:
    seen: set[str] = set()
    unique_words: list[str] = []

    for word in text.split():
        word_lower = word.lower()
        if word_lower not in seen:
            unique_words.append(word)
            seen.add(word_lower)

    return " ".join(unique_words)


def _detect_task(text: str) -> str:
    text_lower = text.lower()
    for keyword, task in _TASK_KEYWORDS.items():
        if keyword in text_lower:
            return task
    return "Describe"


def _extract_subject(text: str) -> str:
    subject_words = [word for word in text.split() if word.lower() not in _KNOWN_VERBS]
    return " ".join(subject_words)


def _normalize_task_phrase(text: str) -> str:
    """Keep task text concise and statement-like."""
    normalized = re.sub(
        r"\bwhat\s+(.+?)\s+(?:are|is|were|was)\b",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(r"\?+", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized.rstrip(".").strip()


def optimize_prompt(text: str) -> str:
    """Normalize and restructure user text into an optimized prompt template."""
    normalized = text.strip()
    without_fillers = _remove_fillers(normalized)
    deduplicated = _remove_duplicate_words(without_fillers)

    task = _detect_task(deduplicated)
    subject = _extract_subject(deduplicated)
    task_line = _normalize_task_phrase(f"{task} {subject}".strip())

    return (
        "Role:\n"
        "You are an expert assistant.\n\n"
        "Task:\n"
        f"{task_line}\n\n"
        "Constraints:\n"
        "- Be concise\n"
        "- Avoid repetition"
    )
