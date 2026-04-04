"""Prompt variant generation service."""

from __future__ import annotations

import re

from app.services.optimizer import optimize_prompt
from app.services.optimizer import _FILLER_PHRASES


def _remove_fillers_preserve_case(text: str) -> str:
    """Remove known filler phrases without lowercasing the whole input."""
    cleaned = text
    for filler in _FILLER_PHRASES:
        pattern = re.compile(rf"\b{re.escape(filler)}\b", flags=re.IGNORECASE)
        cleaned = pattern.sub(" ", cleaned)
    return " ".join(cleaned.split())


def _remove_duplicate_words_preserve_case(text: str) -> str:
    """Remove duplicate words while preserving original capitalization."""
    seen: set[str] = set()
    unique_words: list[str] = []

    for word in text.split():
        key = word.casefold()
        if key not in seen:
            unique_words.append(word)
            seen.add(key)

    return " ".join(unique_words)


def _remove_what_are_pattern(text: str) -> str:
    """Collapse 'what ... are/is' phrasing into a direct subject phrase."""
    return re.sub(
        r"\bwhat\s+(.+?)\s+(?:are|is|were|was)\b",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )


def _strip_trailing_punctuation(text: str) -> str:
    """Remove trailing '?' and '.' punctuation marks."""
    return re.sub(r"[?.]+\s*$", "", text).strip()


def _capitalize_first_letter(text: str) -> str:
    """Capitalize only the first character, preserving the rest."""
    if not text:
        return text
    return text[0].upper() + text[1:]


def _minimal_variant(text: str) -> str:
    stripped = text.strip()
    without_fillers = _remove_fillers_preserve_case(stripped)
    normalized_question_pattern = _remove_what_are_pattern(without_fillers)
    deduplicated = _remove_duplicate_words_preserve_case(normalized_question_pattern)
    without_trailing_punctuation = _strip_trailing_punctuation(deduplicated)
    return _capitalize_first_letter(without_trailing_punctuation)


def _extract_task_line(balanced: str) -> str:
    if "\n\nTask:\n" not in balanced:
        return balanced.strip()
    task_block = balanced.split("\n\nTask:\n", maxsplit=1)[1]
    return task_block.split("\n\nConstraints:\n", maxsplit=1)[0].strip()


def _append_sentence(base_text: str, sentence: str) -> str:
    """Append a sentence while preventing double punctuation."""
    normalized_base = base_text.strip()
    if not normalized_base:
        return sentence.strip()
    if normalized_base[-1] not in ".!?":
        normalized_base = f"{normalized_base}."
    return f"{normalized_base} {sentence.strip()}"


def _task_mentions(task_text: str, pattern: str) -> bool:
    """Return whether the task already includes an instruction pattern."""
    return re.search(pattern, task_text, flags=re.IGNORECASE) is not None


def _detailed_variant(balanced: str) -> str:
    task_line = _extract_task_line(balanced)
    expanded_task = _append_sentence(
        task_line,
        "Provide a step-by-step explanation, include concrete examples, and break down "
        "the key components.",
    )
    constraints = [
        "- Use a clear structure",
        "- Keep the response concise where possible",
    ]

    if not _task_mentions(expanded_task, r"\bstep(?:\s*-\s*|\s+)by(?:\s*-\s*|\s+)step\b"):
        constraints.append("- Explain step-by-step")
    if not _task_mentions(expanded_task, r"\bexample(?:s)?\b"):
        constraints.append("- Include examples")
    if not _task_mentions(expanded_task, r"\bbreak\s+down\b|\bbreakdown\b"):
        constraints.append("- Break down key components")

    return (
        "Role:\n"
        "You are an expert assistant.\n\n"
        "Task:\n"
        f"{expanded_task}\n\n"
        "Constraints:\n"
        f"{'\n'.join(constraints)}"
    )


def generate_variants(text: str) -> list:
    """Generate minimal, balanced, and detailed prompt variants."""
    balanced = optimize_prompt(text)
    minimal = _minimal_variant(text)
    detailed = _detailed_variant(balanced)

    return [
        {"type": "minimal", "prompt": minimal},
        {"type": "balanced", "prompt": balanced},
        {"type": "detailed", "prompt": detailed},
    ]
