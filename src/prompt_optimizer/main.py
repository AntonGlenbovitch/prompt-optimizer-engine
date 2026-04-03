"""Application entry point for prompt_optimizer."""

from __future__ import annotations

import re

FILLER_PATTERNS = [
    r"\bplease\b",
    r"\bi think\b",
    r"\bmaybe\b",
]

ROLE_PATTERN = re.compile(r"\b(?:act as|as)\s+(an?\s+[^,.!\n]+)", re.IGNORECASE)


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


def remove_filler_words(text: str) -> str:
    """Remove known filler words and phrases from the prompt."""
    cleaned = text
    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    return cleaned.strip()


def remove_duplicate_phrases(text: str) -> str:
    """Remove duplicate clauses while preserving original order."""
    parts = [part.strip() for part in re.split(r"[\n.;]+", text) if part.strip()]

    seen: set[str] = set()
    unique_parts: list[str] = []
    for part in parts:
        normalized = re.sub(r"\s+", " ", part).lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_parts.append(part)

    return ". ".join(unique_parts).strip()


def _extract_role(text: str) -> tuple[str, str]:
    """Extract a role phrase when the prompt includes one."""
    match = ROLE_PATTERN.search(text)
    if not match:
        return "Not specified", text

    role = match.group(1).strip()
    updated_text = (text[: match.start()] + text[match.end() :]).strip(" ,.-")
    return role, updated_text


def _to_clauses(text: str) -> list[str]:
    """Break text into simple clauses for task/constraints extraction."""
    clauses = [clause.strip(" ,-") for clause in re.split(r"[\n.!?]+", text) if clause.strip()]
    return clauses


def structure_prompt(text: str) -> str:
    """Convert plain prompt text into a simple Role/Task/Constraints format."""
    role, without_role = _extract_role(text)
    clauses = _to_clauses(without_role)

    task = clauses[0] if clauses else "Not specified"
    constraints = "; ".join(clauses[1:]) if len(clauses) > 1 else "None"

    return f"Role: {role}\nTask: {task}\nConstraints: {constraints}"


def optimize_prompt(raw_prompt: str) -> str:
    """Apply rule-based prompt optimization steps."""
    no_filler = remove_filler_words(raw_prompt)
    deduplicated = remove_duplicate_phrases(no_filler)
    return structure_prompt(deduplicated)


def _extract_prompt_parts(raw_prompt: str) -> tuple[str, str, str]:
    """Extract normalized role, task, and constraints from the raw prompt."""
    no_filler = remove_filler_words(raw_prompt)
    deduplicated = remove_duplicate_phrases(no_filler)
    role, without_role = _extract_role(deduplicated)
    clauses = _to_clauses(without_role)

    task = clauses[0] if clauses else "Not specified"
    constraints = "; ".join(clauses[1:]) if len(clauses) > 1 else "None"
    return role, task, constraints


def generate_variants(raw_prompt: str) -> dict[str, str]:
    """Generate three intent-preserving prompt variants with different styles."""
    role, task, constraints = _extract_prompt_parts(raw_prompt)
    role_line = f"As {role}, " if role != "Not specified" else ""
    constraint_text = f" Constraints: {constraints}." if constraints != "None" else ""

    variant_a = f"{role_line}{task}.{constraint_text}".strip()

    variant_b_lines = [
        f"Role: {role}",
        f"Task: {task}",
        f"Constraints: {constraints}",
    ]
    variant_b = "\n".join(variant_b_lines)

    variant_c_lines = [
        "Objective:",
        f"- {task}",
        "",
        "Context:",
        f"- Role: {role}",
        "",
        "Requirements:",
        f"- Follow these constraints: {constraints}",
        "- Keep the response clear, complete, and aligned with the objective.",
        "- If information is missing, state assumptions before proceeding.",
    ]
    variant_c = "\n".join(variant_c_lines)

    return {
        "A": variant_a,
        "B": variant_b,
        "C": variant_c,
    }


def estimate_tokens(text: str) -> int:
    """Estimate token count using a lightweight character-based heuristic."""
    return max(1, round(len(text) / 4))


def score_variant_quality(variant: str, role: str, task: str, constraints: str) -> int:
    """Score prompt quality from 0-100 using simple structure/completeness signals."""
    score = 40

    lower_variant = variant.lower()
    if role != "Not specified" and "role" in lower_variant:
        score += 15
    if task != "Not specified" and task.lower() in lower_variant:
        score += 20
    if constraints != "None" and constraints.lower() in lower_variant:
        score += 15

    # Reward clear structure markers.
    marker_count = sum(marker in variant for marker in ("Role:", "Task:", "Constraints:", "Objective:", "Requirements:"))
    score += min(marker_count * 3, 10)

    # Soft penalty for overly short or verbose prompts.
    length = len(variant)
    if length < 40:
        score -= 10
    elif length > 500:
        score -= 5

    return max(0, min(100, score))


def build_comparison_rows(raw_prompt: str, variants: dict[str, str]) -> list[dict[str, str | int]]:
    """Build comparison metrics for each variant."""
    role, task, constraints = _extract_prompt_parts(raw_prompt)
    rows: list[dict[str, str | int]] = []
    for name, text in variants.items():
        rows.append(
            {
                "variant": name,
                "tokens": estimate_tokens(text),
                "quality": score_variant_quality(text, role, task, constraints),
                "length": len(text),
            }
        )
    return rows


def _render_table(rows: list[dict[str, str | int]]) -> str:
    """Render a simple fixed-width comparison table."""
    headers = ("Variant", "Token Estimate", "Quality Score", "Length (chars)")
    widths = [len(header) for header in headers]

    str_rows = []
    for row in rows:
        display_row = (
            str(row["variant"]),
            str(row["tokens"]),
            f'{row["quality"]}/100',
            str(row["length"]),
        )
        str_rows.append(display_row)
        widths = [max(width, len(value)) for width, value in zip(widths, display_row)]

    def format_row(values: tuple[str, ...]) -> str:
        return "| " + " | ".join(value.ljust(width) for value, width in zip(values, widths)) + " |"

    separator = "|-" + "-|-".join("-" * width for width in widths) + "-|"
    lines = [format_row(headers), separator]
    lines.extend(format_row(row) for row in str_rows)
    return "\n".join(lines)


def run(raw_prompt: str) -> None:
    """Run optimization and print result."""
    variants = generate_variants(raw_prompt)
    print("--- Variant A ---")
    print(variants["A"])
    print("--- Variant B ---")
    print(variants["B"])
    print("--- Variant C ---")
    print(variants["C"])
    print("--- Comparison ---")
    comparison_rows = build_comparison_rows(raw_prompt, variants)
    print(_render_table(comparison_rows))


def main() -> None:
    """Parse CLI arguments and execute the application."""
    parse_args = _load_parse_args()
    args = parse_args()
    run(args.prompt)


if __name__ == "__main__":
    main()
