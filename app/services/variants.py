"""Prompt variant generation service."""

from __future__ import annotations

import re

from app.services.optimizer import _FILLER_PHRASES
from app.services.optimizer import _normalize_task_phrase
from app.services.optimizer import optimize_prompt


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
    normalized_statement = _normalize_task_phrase(without_trailing_punctuation)
    return _capitalize_first_letter(normalized_statement)


def _extract_task_line(balanced: str) -> str:
    if "\n\nTask:\n" not in balanced:
        return balanced.strip()
    task_block = balanced.split("\n\nTask:\n", maxsplit=1)[1]
    return task_block.split("\n\nConstraints:\n", maxsplit=1)[0].strip()


def _to_sentence(text: str) -> str:
    """Normalize a sentence and ensure it ends with a period."""
    sentence = _normalize_task_phrase(text)
    if not sentence:
        return sentence
    if sentence[-1] not in ".!":
        sentence = f"{sentence}."
    return sentence


def _append_sentence(base_text: str, sentence: str) -> str:
    """Append sentence-level text while preserving clean punctuation."""
    base_sentence = _to_sentence(base_text)
    extra_sentence = _to_sentence(sentence)
    if not base_sentence:
        return extra_sentence
    if not extra_sentence:
        return base_sentence
    return f"{base_sentence} {extra_sentence}"


def _task_mentions(task_text: str, pattern: str) -> bool:
    """Return whether the task already includes an instruction pattern."""
    return re.search(pattern, task_text, flags=re.IGNORECASE) is not None


def _detailed_variant(balanced: str) -> str:
    task_line = _normalize_task_phrase(_extract_task_line(balanced))
    task_sentences = [
        _to_sentence(task_line),
        _to_sentence(
            "Provide a step-by-step explanation with concrete examples and a breakdown "
            "of key components"
        ),
    ]
    expanded_task = "\n".join(sentence for sentence in task_sentences if sentence)
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
