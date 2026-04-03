"""Prompt variant generation service."""

from __future__ import annotations

from app.services.optimizer import optimize_prompt


def _without_constraints(optimized_prompt: str) -> str:
    """Drop the constraints section from an optimized prompt."""
    return optimized_prompt.split("\n\nConstraints:\n", maxsplit=1)[0].strip()


def generate_variants(text: str) -> list:
    """Generate minimal, balanced, and detailed prompt variants."""
    balanced = optimize_prompt(text)
    minimal = _without_constraints(balanced)
    detailed = (
        f"{balanced}\n"
        "- Include examples\n"
        "- Provide clear explanation\n"
        "- Structure response"
    )

    return [
        {"type": "minimal", "prompt": minimal},
        {"type": "balanced", "prompt": balanced},
        {"type": "detailed", "prompt": detailed},
    ]
