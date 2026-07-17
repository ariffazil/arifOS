"""CLI: python -m arifos.aaa cards"""

from __future__ import annotations

import json
import sys

from . import cards, gateway_card


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "cards"
    if cmd == "cards":
        roster = cards()
        ids = sorted(
            {
                str(a.get("id") or a.get("agent_id") or a.get("name"))
                for a in roster
                if isinstance(a, dict)
            }
        )
        print(json.dumps({"count": len(ids), "identities": ids}, indent=2))
        return 0 if ids else 1
    if cmd == "gateway":
        print(json.dumps(gateway_card(), indent=2)[:2000])
        return 0
    print(f"unknown command: {cmd} (try: cards | gateway)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
