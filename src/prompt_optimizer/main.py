"""Application entry point for prompt_optimizer."""

from __future__ import annotations

import re
from collections import Counter


CLARITY_VERBS = {"explain", "summarize", "describe", "clarify", "outline"}


def _load_parse_args():
    """Load parse_args for package and direct-script execution modes."""
    if __package__:
        from .cli import parse_args

        return parse_args

    from pathlib import Path
    import sys

    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

    from prompt_optimizer.cli import parse_args

    return parse_args


def estimate_tokens(text: str) -> int:
    """Estimate token count using a simple words-based approximation."""
    word_count = len(text.split())
    return round(word_count * 1.3)


def _classify_length(word_count: int) -> str:
    """Classify prompt length by word count."""
    if word_count < 10:
        return "short"
    if word_count <= 40:
        return "medium"
    return "long"


def _detect_redundancy(words: list[str]) -> list[str]:
    """Find repeated single words and adjacent two-word phrases."""
    issues: list[str] = []

    word_counts = Counter(words)
    repeated_words = sorted(word for word, count in word_counts.items() if count > 2)
    if repeated_words:
        shown = ", ".join(repeated_words[:4])
        issues.append(f"Repetitive wording (words repeated often: {shown})")

    bigrams = [f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)]
    bigram_counts = Counter(bigrams)
    repeated_bigrams = sorted(phrase for phrase, count in bigram_counts.items() if count > 1)
    if repeated_bigrams:
        shown = ", ".join(repeated_bigrams[:3])
        issues.append(f"Repeated phrases detected: {shown}")

    return issues


def analyze_prompt(raw_prompt: str) -> tuple[int, str, list[str]]:
    """Analyze prompt quality and return score, length label, and issues."""
    words = re.findall(r"[a-zA-Z']+", raw_prompt.lower())
    word_count = len(words)
    length_label = _classify_length(word_count)

    issues: list[str] = []
    score = 100

    if length_label == "short":
        issues.append("Too short; may lack context")
        score -= 20
    elif length_label == "long":
        issues.append("Too verbose")
        score -= 15

    redundancy_issues = _detect_redundancy(words)
    if redundancy_issues:
        issues.extend(redundancy_issues)
        score -= min(25, 10 * len(redundancy_issues))

    if not any(verb in words for verb in CLARITY_VERBS):
        issues.append("Lacks clear instruction")
        score -= 20

    if not issues:
        issues.append("No major issues detected")

    score = max(0, min(100, score))
    return score, length_label, issues


def run(raw_prompt: str) -> None:
    """Run the core app logic and print prompt analysis results."""
    token_count = estimate_tokens(raw_prompt)
    score, length_label, issues = analyze_prompt(raw_prompt)

    print(f"Prompt: {raw_prompt}")
    print(f"Tokens (estimated): {token_count}")
    print(f"Length: {length_label}")
    print(f"Quality Score: {score}")
    print("Issues:")
    for issue in issues:
        print(f"- {issue}")


def main() -> None:
    """Parse CLI arguments and execute the application."""
    parse_args = _load_parse_args()
    args = parse_args()
    run(args.prompt)


if __name__ == "__main__":
    main()
