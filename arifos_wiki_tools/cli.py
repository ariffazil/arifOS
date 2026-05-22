"""arifos_wiki_tools.cli — Command-line interface for arif-wiki."""

from __future__ import annotations

import argparse
import json
import sys

from arifos_wiki_tools.indexer import ingest_repo
from arifos_wiki_tools.search import search_index
from arifos_wiki_tools.synthesis import ask_repo, map_repo


def _print_json(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arif-wiki",
        description="arifOS Wiki Tools Forge — Local-first repo comprehension",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── ingest ────────────────────────────────────────────────────────────────
    p_ingest = sub.add_parser("ingest", help="Index a repository and generate wiki pages.")
    p_ingest.add_argument("repo_path", help="Path to the repository to index.")
    p_ingest.add_argument(
        "--scope",
        default="arifOS",
        help="Scope name written into the manifest (default: arifOS)",
    )
    p_ingest.add_argument(
        "--no-write-wiki",
        action="store_true",
        help="Skip generating wiki markdown pages.",
    )

    # ── map ─────────────────────────────────────────────────────────────────
    p_map = sub.add_parser("map", help="Show repository map from the local wiki index.")
    p_map.add_argument("repo_path", help="Path to the repository.")
    p_map.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="Maximum directory tree depth (default: 4)",
    )

    # ── search ──────────────────────────────────────────────────────────────
    p_search = sub.add_parser(
        "search",
        help="Search the local wiki index for evidence chunks.",
    )
    p_search.add_argument("repo_path", help="Path to the repository.")
    p_search.add_argument("query", help="Search query string.")
    p_search.add_argument(
        "--top-k",
        type=int,
        default=8,
        help="Maximum number of results to return (default: 8)",
    )

    # ── ask ──────────────────────────────────────────────────────────────────
    p_ask = sub.add_parser(
        "ask",
        help="Answer a question grounded in the local wiki index.",
    )
    p_ask.add_argument("repo_path", help="Path to the repository.")
    p_ask.add_argument("question", help="Natural-language question.")
    p_ask.add_argument(
        "--top-k",
        type=int,
        default=8,
        help="Maximum evidence chunks to retrieve (default: 8)",
    )

    args = parser.parse_args(argv)

    try:
        if args.cmd == "ingest":
            result = ingest_repo(
                args.repo_path,
                scope_name=args.scope,
                write_wiki=not args.no_write_wiki,
            )
            _print_json(result)
            return 0

        if args.cmd == "map":
            _print_json(map_repo(args.repo_path, max_depth=args.max_depth))
            return 0

        if args.cmd == "search":
            _print_json(search_index(args.repo_path, args.query, top_k=args.top_k))
            return 0

        if args.cmd == "ask":
            _print_json(ask_repo(args.repo_path, args.question, top_k=args.top_k))
            return 0

        parser.error("unknown command")
        return 2

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
