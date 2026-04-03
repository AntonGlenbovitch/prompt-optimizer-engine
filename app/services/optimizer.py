"""Prompt optimization service."""

from __future__ import annotations


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
    cleaned = text
    for filler in _FILLER_PHRASES:
        cleaned = cleaned.replace(filler, " ")
    return " ".join(cleaned.split())


def _remove_duplicate_words(text: str) -> str:
    seen: set[str] = set()
    unique_words: list[str] = []

    for word in text.split():
        if word not in seen:
            unique_words.append(word)
            seen.add(word)

    return " ".join(unique_words)


def _detect_task(text: str) -> str:
    for keyword, task in _TASK_KEYWORDS.items():
        if keyword in text:
            return task
    return "Describe"


def _extract_subject(text: str) -> str:
    subject_words = [word for word in text.split() if word not in _KNOWN_VERBS]
    return " ".join(subject_words)


def optimize_prompt(text: str) -> str:
    """Normalize and restructure user text into an optimized prompt template."""
    normalized = text.strip().lower()
    without_fillers = _remove_fillers(normalized)
    deduplicated = _remove_duplicate_words(without_fillers)

    task = _detect_task(deduplicated)
    subject = _extract_subject(deduplicated)
    task_line = f"{task} {subject}".strip()

    return (
        "Role:\n"
        "You are an expert assistant.\n\n"
        "Task:\n"
        f"{task_line}\n\n"
        "Constraints:\n"
        "- Be concise\n"
        "- Avoid repetition"
    )
