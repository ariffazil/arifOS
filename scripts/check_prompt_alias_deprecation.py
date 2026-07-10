#!/usr/bin/env python3
"""
check_prompt_alias_deprecation.py — enforce 666_judge removal deadline

Deadline: 2026-07-17 (see docs/PROMPT_666_JUDGE_DEPRECATION.md)

Exit codes:
  0 — compliant
  1 — past deadline and alias still live
  2 — cannot probe MCP
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date

DEADLINE = date(2026, 7, 17)
ALIAS = "666_judge"
CANON = "888_judge"
MCP_URL = "http://127.0.0.1:8088/mcp"


def mcp(method: str, params: dict | None = None, sid: str | None = None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-11-25",
    }
    if sid:
        headers["Mcp-Session-Id"] = sid
    body: dict = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params
    req = urllib.request.Request(
        MCP_URL, data=json.dumps(body).encode(), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode()
        sid_out = r.headers.get("Mcp-Session-Id")
        if "data:" in raw:
            for line in raw.splitlines():
                if line.startswith("data:"):
                    return json.loads(line[5:].strip()), sid_out
        return json.loads(raw), sid_out


def main() -> int:
    today = date.today()
    try:
        _, sid = mcp(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "alias-deprecation-check", "version": "1"},
            },
        )
        try:
            mcp("notifications/initialized", {}, sid)
        except Exception:
            pass
        pl, _ = mcp("prompts/list", {}, sid)
        prompts = (pl.get("result") or {}).get("prompts") or []
        names = {p.get("name") for p in prompts}
    except Exception as e:
        print(f"PROBE_FAIL: {e}", file=sys.stderr)
        return 2

    has_alias = ALIAS in names
    has_canon = CANON in names
    print(f"date={today.isoformat()} deadline={DEADLINE.isoformat()}")
    print(f"has_{CANON}={has_canon} has_{ALIAS}={has_alias}")
    print(f"names={sorted(n for n in names if n)}")

    if not has_canon:
        print("FAIL: canonical 888_judge missing from live prompts/list")
        return 1

    if today < DEADLINE:
        if has_alias:
            print("OK: alias still present within deprecation window")
        else:
            print("OK: alias already removed early (fine)")
        return 0

    # On or after deadline
    if has_alias:
        print(
            f"FAIL: {ALIAS} still live on/after {DEADLINE.isoformat()} — remove alias now"
        )
        return 1
    print(f"OK: {ALIAS} gone; {CANON} sole judge prompt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
