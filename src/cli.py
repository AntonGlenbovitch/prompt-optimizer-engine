"""CLI module for prompt_optimizer."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Create and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="prompt_optimizer",
        description="A simple CLI that reads and echoes a prompt.",
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="Prompt text to display back to the user.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = build_parser()
    return parser.parse_args(argv)
