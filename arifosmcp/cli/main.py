"""arifOS CLI entry point and subcommand dispatch."""

from __future__ import annotations

import argparse
import sys
from typing import Callable

from arifosmcp.cli.check import run_check
from arifosmcp.cli.judge import run_judge
from arifosmcp.cli.seal import run_seal


COMMANDS: dict[str, Callable[[list[str]], int]] = {
    "check": run_check,
    "judge": run_judge,
    "seal": run_seal,
}


def main(argv: list[str] | None = None) -> int:
    """Entry point for `arifos <subcommand>`."""
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="arifos",
        description="arifOS — Constitutional kernel CLI. Use `arifos serve` to boot the MCP server.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=[*COMMANDS.keys(), "serve", "help"],
        help="Subcommand to run.",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments passed to the subcommand.",
    )

    # If no command given, show help.
    if not argv:
        parser.print_help()
        return 0

    parsed = parser.parse_args([argv[0]])
    command = parsed.command

    if command == "serve":
        # Hand back to server main (caller responsibility).
        return -1
    if command == "help":
        parser.print_help()
        return 0
    if command in COMMANDS:
        return COMMANDS[command](argv[1:])

    parser.print_help()
    return 1
