"""Application entry point for prompt_optimizer."""

from __future__ import annotations

from cli import parse_args


def run(raw_prompt: str) -> None:
    """Run the core app logic.

    For now, this simply prints the raw prompt unchanged.
    """
    print(raw_prompt)


def main() -> None:
    """Parse CLI arguments and execute the application."""
    args = parse_args()
    run(args.prompt)


if __name__ == "__main__":
    main()
