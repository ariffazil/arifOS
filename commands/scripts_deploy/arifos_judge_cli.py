#!/usr/bin/env python3
"""
arifOS 888_JUDGE + 999_VAULT Interactive CLI
DITEMPA BUKAN DIBERI — F13 Sovereign Elicitation Wrapper

Usage:
    python arifos_judge_cli.py --candidate "Deploy KL2 pipeline to production"
    python arifos_judge_cli.py --candidate "Deploy KL2 pipeline" --ack --vault-payload '{"action":"deploy"}'

This script handles the HOLD → human prompt → SEAL loop that the raw MCP tool
requires but which headless agents cannot self-complete.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ARIFOS_MCP_URL = os.getenv("ARIFOS_MCP_URL", "https://mcp.arif-fazil.com/mcp")
ACTOR_ID = os.getenv("ARIFOS_ACTOR_ID", "arif-fazil")


# ---------------------------------------------------------------------------
# MCP Tool Caller (HTTP bridge)
# ---------------------------------------------------------------------------
async def call_arifos_tool(session_id: str | None, tool: str, params: dict) -> dict:
    import httpx

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": {**(params or {}), "session_id": session_id, "actor_id": ACTOR_ID},
        },
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        r = await client.post(f"{ARIFOS_MCP_URL}/rpc", json=payload)
        r.raise_for_status()
        data = r.json()

    if "error" in data:
        raise RuntimeError(f"MCP error: {data['error']}")

    result = data.get("result", {}).get("content", [{}])[0]
    text = result.get("text", "{}")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------
async def init_session() -> str:
    resp = await call_arifos_tool(None, "arif_session_init", {"mode": "init"})
    sid = resp.get("result", {}).get("session", {}).get("session_id")
    if not sid:
        raise RuntimeError(f"Session init failed: {json.dumps(resp, indent=2)[:500]}")
    print(f"  Session: {sid}")
    return sid


# ---------------------------------------------------------------------------
# 888 JUDGE — with interactive elicitation
# ---------------------------------------------------------------------------
async def judge_candidate(session_id: str, candidate: str) -> dict:
    print(f"\n  Candidate: {candidate[:120]}...")
    resp = await call_arifos_tool(
        session_id,
        "arif_judge_deliberate",
        {"mode": "judge", "candidate": candidate},
    )
    return resp


# ---------------------------------------------------------------------------
# 999 VAULT — with explicit human ack
# ---------------------------------------------------------------------------
async def vault_anchor(
    session_id: str,
    payload: dict,
    judge_state_hash: str | None = None,
    constitutional_chain_id: str | None = None,
) -> dict:
    resp = await call_arifos_tool(
        session_id,
        "arif_vault_seal",
        {
            "mode": "seal",
            "payload": json.dumps(payload),
            "ack_irreversible": True,
            "judge_state_hash": judge_state_hash,
            "constitutional_chain_id": constitutional_chain_id,
        },
    )
    return resp


# ---------------------------------------------------------------------------
# Interactive loop
# ---------------------------------------------------------------------------
def human_confirm(candidate: str, verdict: dict) -> bool:
    print("\n" + "=" * 60)
    print("  arifOS 888 JUDGE — HUMAN ELICITATION REQUIRED")
    print("=" * 60)
    print(f"\nCandidate:\n  {candidate}\n")

    reasons = verdict.get("result", {}).get("reasons", [])
    if reasons:
        print("Judge reasons:")
        for r in reasons:
            print(f"  • {r}")

    floors = verdict.get("result", {}).get("constitutional_compliance", {}).get("law_results", {})
    if floors:
        print("\nFloor compliance:")
        for f, v in floors.items():
            print(f"  {f}: {v}")

    print("\n" + "-" * 60)
    print("Options:")
    print("  [SEAL]  — Approve and anchor to VAULT999")
    print("  [SABAR] — Approve with conditions")
    print("  [HOLD]  — Pause for more info")
    print("  [VOID]  — Reject")
    print("-" * 60)

    choice = input("\nYour verdict (SEAL/SABAR/HOLD/VOID): ").strip().upper()
    return choice == "SEAL"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main():
    parser = argparse.ArgumentParser(description="arifOS 888_JUDGE interactive CLI")
    parser.add_argument("--candidate", required=True, help="Action/proposal to adjudicate")
    parser.add_argument("--ack", action="store_true", help="Auto-acknowledge (batch mode)")
    parser.add_argument("--vault-payload", help="JSON payload to anchor if SEAL")
    parser.add_argument("--session-id", help="Resume existing session")
    args = parser.parse_args()

    print("╔════════════════════════════════════════════════════════════╗")
    print("║  arifOS 888_JUDGE + 999_VAULT — Constitutional CLI        ║")
    print("║  DITEMPA BUKAN DIBERI                                     ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Session
    sid = args.session_id
    if not sid:
        print("\n▶ Init session...")
        sid = await init_session()

    # 888 JUDGE
    print("\n▶ 888 JUDGE deliberating...")
    verdict = await judge_candidate(sid, args.candidate)
    v_code = verdict.get("result", {}).get("verdict", "UNKNOWN")
    print(f"  Raw verdict: {v_code}")

    # If already SEAL (rare for consequential actions), proceed
    if v_code == "SEAL":
        approved = True
    elif args.ack:
        print("  --ack set, auto-approving SEAL...")
        approved = True
    else:
        approved = human_confirm(args.candidate, verdict)

    if not approved:
        print("\n  ❌ Action NOT approved. Exiting.")
        sys.exit(1)

    # 999 VAULT
    if args.vault_payload:
        print("\n▶ 999 VAULT anchoring...")
        vault_payload = json.loads(args.vault_payload)
        vault_payload["candidate"] = args.candidate
        vault_payload["approved_at"] = datetime.now(timezone.utc).isoformat()
        vault_payload["actor_id"] = ACTOR_ID

        vault_resp = await vault_anchor(sid, vault_payload)
        v_verdict = vault_resp.get("result", {}).get("verdict", "UNKNOWN")
        print(f"  Vault verdict: {v_verdict}")

        if v_verdict != "SEAL":
            print(f"  Vault details: {json.dumps(vault_resp.get('result', {}), indent=2)[:800]}")
            print("\n  ⚠️  Vault returned HOLD — likely F11 identity or F13 elicitation gap.")
            print("      Run with DID signature or use AAA Cockpit for full seal authority.")
            sys.exit(2)

        entry_id = vault_resp.get("result", {}).get("entry_id")
        chain_hash = vault_resp.get("result", {}).get("chain_hash")
        print(f"\n  ✅ SEALED — entry_id: {entry_id}")
        print(f"     chain_hash: {chain_hash}")

    print("\n  DITEMPA BUKAN DIBERI.")


if __name__ == "__main__":
    asyncio.run(main())
