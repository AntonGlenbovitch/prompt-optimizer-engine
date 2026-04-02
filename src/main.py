"""Application entry point for prompt_optimizer."""

from __future__ import annotations

from cli import parse_args


def estimate_tokens(text: str) -> int:
    """Estimate token count using a simple words-based approximation."""
    word_count = len(text.split())
    return round(word_count * 1.3)


def run(raw_prompt: str) -> None:
    """Run the core app logic and print prompt/token estimate."""
    token_count = estimate_tokens(raw_prompt)
    print(f"Prompt: {raw_prompt}")
    print(f"Tokens (estimated): {token_count}")


def main() -> None:
    """Parse CLI arguments and execute the application."""
    args = parse_args()
    run(args.prompt)


if __name__ == "__main__":
    main()
