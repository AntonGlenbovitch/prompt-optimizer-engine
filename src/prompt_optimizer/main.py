"""Application entry point for prompt_optimizer."""

from __future__ import annotations


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


def run(raw_prompt: str) -> None:
    """Run the core app logic and print prompt/token estimate."""
    token_count = estimate_tokens(raw_prompt)
    print(f"Prompt: {raw_prompt}")
    print(f"Tokens (estimated): {token_count}")


def main() -> None:
    """Parse CLI arguments and execute the application."""
    parse_args = _load_parse_args()
    args = parse_args()
    run(args.prompt)


if __name__ == "__main__":
    main()
