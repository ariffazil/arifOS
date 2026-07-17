"""CLI: python -m arifos.forge probe"""

from __future__ import annotations

import json
import sys

from . import ForgeClient, DEFAULT_URL


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "probe"
    if cmd == "probe":
        with ForgeClient(DEFAULT_URL) as client:
            tools = client.list_tools()
        print(
            json.dumps(
                {
                    "url": DEFAULT_URL,
                    "tool_count": len(tools),
                    "tools": [t.get("name") for t in tools[:20]],
                },
                indent=2,
            )
        )
        return 0 if tools else 1
    print(f"unknown command: {cmd} (try: probe)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
