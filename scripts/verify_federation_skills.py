#!/usr/bin/env python3
"""
Post-deploy verification for Phase 2 Federation Skills over MCP (skill://).

Usage (after deploy):
  python scripts/verify_federation_skills.py
  python scripts/verify_federation_skills.py --url https://arifos.arif-fazil.com/mcp
  python scripts/verify_federation_skills.py --url http://localhost:8088/mcp --expect 49

It performs:
- initialize
- resources/list (with session)
- spot-check 7 core SKILL.md + read
- report counts + success/fail

Exit 0 on success (cores present + reasonable counts), non-zero on failure.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import urllib.error
import urllib.request
from typing import Any

CORE_SKILLS = [
    "federation-router",
    "arifos-kernel-operator",
    "aaa-doctrine-loader",
    "aforge-execution-governor",
    "vault999-audit-sealer",
    "auditor-validator-kutip-sampah",
    "mcp-fastmcp-builder",
]

DEFAULT_URL = "http://127.0.0.1:8088/mcp"


def _rpc(url: str, method: str, params: dict[str, Any] | None = None, session_id: str | None = None, req_id: int = 1) -> dict[str, Any]:
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params:
        body["params"] = params
    data = json.dumps(body).encode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            txt = resp.read().decode()
            new_sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
            return {"ok": True, "status": resp.status, "text": txt, "session_id": new_sid or session_id}
    except urllib.error.HTTPError as e:
        err_txt = e.read().decode()[:800]
        return {"ok": False, "status": e.code, "text": err_txt, "session_id": session_id}
    except Exception as e:
        return {"ok": False, "error": str(e), "session_id": session_id}


def _parse_json(txt: str) -> dict[str, Any]:
    try:
        return json.loads(txt)
    except Exception:
        return {"raw": txt}


async def verify(url: str, expect_skill_mds: int | None = None) -> int:
    print(f"Verifying federation skills at: {url}")

    # 1. initialize
    r1 = _rpc(url, "initialize", {
        "protocolVersion": "2025-11-25",
        "clientInfo": {"name": "verify_federation_skills", "version": "1"},
        "capabilities": {"resources": {}, "tools": {}},
    })
    if not r1.get("ok"):
        print("FAIL: initialize failed:", r1)
        return 2

    init = _parse_json(r1["text"])
    sid = r1.get("session_id") or init.get("result", {}).get("sessionId")
    print(f"  initialize: OK (session={sid[:8] if sid else 'none'}...)")

    if not sid:
        # Some implementations may not return header; try to continue
        sid = None

    # 2. resources/list
    r2 = _rpc(url, "resources/list", {}, session_id=sid)
    if not r2.get("ok"):
        print("FAIL: resources/list failed:", r2.get("text", r2)[:300])
        return 3

    body2 = _parse_json(r2["text"])
    resources = body2.get("result", {}).get("resources", [])
    skill_resources = [r for r in resources if str(r.get("uri", "")).startswith("skill://")]
    skill_mds = [r for r in skill_resources if "SKILL.md" in str(r.get("uri", ""))]

    print(f"  resources/list: total={len(resources)}, skill:// total={len(skill_resources)}, SKILL.md={len(skill_mds)}")

    if expect_skill_mds is not None and len(skill_mds) < expect_skill_mds:
        print(f"  WARN: expected at least {expect_skill_mds} SKILL.md, got {len(skill_mds)}")

    # 3. Spot-check cores + read
    missing = []
    for name in CORE_SKILLS:
        uri = f"skill://{name}/SKILL.md"
        found = any(str(r.get("uri")) == uri for r in resources)
        if not found:
            missing.append(name)
            print(f"  MISSING core: {uri}")
            continue

        # read
        rread = _rpc(url, "resources/read", {"uri": uri}, session_id=sid)
        if not rread.get("ok"):
            print(f"  READ FAIL {uri}: {rread.get('text', rread)[:200]}")
            missing.append(name)
            continue

        read_body = _parse_json(rread["text"])
        contents = read_body.get("result", {}).get("contents", [])
        text = ""
        if contents:
            text = contents[0].get("text", "") if isinstance(contents[0], dict) else str(contents[0])
        if not text or len(text) < 200:
            print(f"  READ EMPTY/SHORT {uri}")
            missing.append(name)
            continue

        if "# " not in text[:100] and "federation" not in text.lower()[:200]:
            print(f"  READ suspicious content for {uri}")
            missing.append(name)
        else:
            print(f"  OK {uri} (len={len(text)})")

    if missing:
        print(f"\nFAIL: {len(missing)} core skill(s) missing or unreadable: {missing}")
        return 4

    print("\nPASS: All 7 core federation SKILL.md are discoverable and readable via MCP resources.")
    print("Phase 2 wire verification successful against live endpoint.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL, help="MCP endpoint URL")
    parser.add_argument("--expect", type=int, default=None, help="Expected minimum SKILL.md count")
    args = parser.parse_args()

    code = asyncio.run(verify(args.url, args.expect))
    sys.exit(code)


if __name__ == "__main__":
    main()
