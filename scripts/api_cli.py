from __future__ import annotations

"""
arifOS API CLI - Minimal client for the FastAPI server.

Usage (with API running on http://localhost:8000):

    python scripts/api_cli.py health
    python scripts/api_cli.py run "What is Amanah?"
    python scripts/api_cli.py recall demo-user "What did I ask before?"
"""

import argparse
import json
from typing import Any, Dict, Tuple
from urllib import parse, request


BASE_URL = "http://localhost:8000"


def _get(path: str, params: Dict[str, Any] | None = None) -> Tuple[int, Dict[str, Any]]:
  url = BASE_URL + path
  if params:
    url += "?" + parse.urlencode(params)
  with request.urlopen(url) as resp:  # type: ignore[no-untyped-call]
    return resp.status, json.loads(resp.read().decode("utf-8"))


def _post(path: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
  data = json.dumps(payload).encode("utf-8")
  req = request.Request(
    BASE_URL + path,
    data=data,
    headers={"Content-Type": "application/json"},
  )
  with request.urlopen(req) as resp:  # type: ignore[no-untyped-call]
    return resp.status, json.loads(resp.read().decode("utf-8"))


def main() -> None:
  parser = argparse.ArgumentParser(description="arifOS API CLI")
  subparsers = parser.add_subparsers(dest="command", required=True)

  subparsers.add_parser("health", help="Check /health endpoint")

  run_parser = subparsers.add_parser("run", help="Run query through pipeline")
  run_parser.add_argument("query", help="Query text to send to pipeline")

  recall_parser = subparsers.add_parser("recall", help="Recall L7 memories")
  recall_parser.add_argument("user_id", help="User ID for memory isolation")
  recall_parser.add_argument("prompt", help="Prompt for semantic recall")

  args = parser.parse_args()

  if args.command == "health":
    code, body = _get("/health")
  elif args.command == "run":
    code, body = _post("/pipeline/run", {"query": args.query})
  elif args.command == "recall":
    code, body = _get(
      "/memory/recall",
      {"user_id": args.user_id, "prompt": args.prompt},
    )
  else:
    parser.error(f"Unknown command: {args.command}")
    return

  print(code)
  print(json.dumps(body, indent=2))


if __name__ == "__main__":
  main()

