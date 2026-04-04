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


def _minimal_variant(text: str) -> str:
    stripped = text.strip()
    without_fillers = _remove_fillers_preserve_case(stripped)
    deduplicated = _remove_duplicate_words_preserve_case(without_fillers)
    return deduplicated


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


def _detailed_variant(balanced: str) -> str:
    task_line = _extract_task_line(balanced)
    expanded_task = _append_sentence(
        task_line,
        "Provide a step-by-step explanation, include concrete examples, and break down "
        "the key components.",
    )

    return (
        "Role:\n"
        "You are an expert assistant.\n\n"
        "Task:\n"
        f"{expanded_task}\n\n"
        "Constraints:\n"
        "- Include examples\n"
        "- Explain step-by-step\n"
        "- Break down key components\n"
        "- Use clear structure"
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
