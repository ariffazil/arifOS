#!/usr/bin/env python3
"""
VAULT999 Status Verification — Epoch Split v2
═══════════════════════════════════════════════════════════════

Verifies the current state of VAULT999 after the 2026-06-02 epoch split.
Run this after any vault-related maintenance to confirm integrity.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

VAULT_DIR = Path("/root/arifOS/VAULT999")


def load_jsonl(path: Path) -> list[dict]:
    entries = []
    if not path.exists():
        return entries
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Parse error in {path.name}: {e}")
    return entries


def verify_v1_frozen() -> dict:
    """v1 is frozen — verify it exists and is not being written to."""
    v1_file = VAULT_DIR / "SEALED_EVENTS.jsonl"
    state_file = VAULT_DIR / "epoch_state.json"

    result = {
        "status": "unknown",
        "entries": 0,
        "lineage_breaks": None,
        "frozen": False,
    }

    if not v1_file.exists():
        result["status"] = "MISSING"
        return result

    entries = load_jsonl(v1_file)
    result["entries"] = len(entries)

    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        v1_state = state.get("v1", {})
        result["frozen"] = v1_state.get("status") == "FROZEN"
        result["lineage_breaks"] = v1_state.get("lineage_breaks")

    if result["frozen"]:
        result["status"] = "FROZEN_HISTORICAL"
    else:
        result["status"] = "UNEXPECTEDLY_ACTIVE"

    return result


def verify_v2_active() -> dict:
    """v2 is active — verify genesis anchor and chain continuity."""
    v2_file = VAULT_DIR / "SEALED_EVENTS_v2.jsonl"
    state_file = VAULT_DIR / "epoch_state.json"
    result = {
        "status": "unknown",
        "entries": 0,
        "genesis_anchored": False,
        "chain_continuous": False,
    }

    if not v2_file.exists():
        result["status"] = "MISSING"
        return result

    entries = load_jsonl(v2_file)
    result["entries"] = len(entries)

    if not entries:
        result["status"] = "EMPTY"
        return result

    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        v2_state = state.get("v2", {})
        v1_state = state.get("v1", {})

        # Verify genesis hash anchors to v1 terminal
        entries[0]
        genesis_hash = v2_state.get("genesis_hash")
        v1_terminal = v1_state.get("terminal_hash")
        result["genesis_anchored"] = genesis_hash == v1_terminal

        # Verify chain continuity within v2
        result["chain_continuous"] = True
        for i in range(1, len(entries)):
            prev = entries[i - 1]
            curr = entries[i]
            prev_hash = prev.get("entry_hash") or prev.get("chain_hash")
            curr_prev = curr.get("prev_entry_hash") or curr.get("prev_hash")
            if prev_hash and curr_prev and prev_hash != curr_prev:
                result["chain_continuous"] = False
                result["break_at"] = i
                break

    if result["genesis_anchored"] and result["chain_continuous"]:
        result["status"] = "HEALTHY"
    else:
        result["status"] = "DEGRADED"

    return result


def verify_live_vault() -> dict:
    """Canonical live vault (vault999.jsonl) — verify it parses."""
    live_file = VAULT_DIR / "vault999.jsonl"
    result = {
        "status": "unknown",
        "entries": 0,
        "last_entry_hash": None,
    }

    if not live_file.exists():
        result["status"] = "MISSING"
        return result

    entries = load_jsonl(live_file)
    result["entries"] = len(entries)

    if entries:
        last = entries[-1]
        chain = last.get("chain", {})
        result["last_entry_hash"] = chain.get("entry_hash")
        result["status"] = "HEALTHY"
    else:
        result["status"] = "EMPTY"

    return result


def verify_service_health() -> dict:
    """Check vault999-writer service health."""
    import urllib.request

    result = {"status": "unknown", "reachable": False}
    try:
        with urllib.request.urlopen("http://localhost:8100/health", timeout=2) as resp:
            data = json.loads(resp.read().decode())
            result["status"] = data.get("status", "unknown")
            result["reachable"] = True
            result["service"] = data.get("service", "unknown")
    except Exception as e:
        result["status"] = f"unreachable: {e}"

    return result


def main() -> int:
    print("═" * 60)
    print("  VAULT999 Epoch Split Verification")
    print("  Ratified: 2026-06-02 | Authority: F13 SOVEREIGN")
    print("═" * 60)

    print("\n📜 v1 Ledger (Historical — FROZEN)")
    v1 = verify_v1_frozen()
    print(f"   Status:       {v1['status']}")
    print(f"   Entries:      {v1['entries']}")
    print(f"   Lineage breaks: {v1['lineage_breaks']}")
    print(f"   Frozen:       {v1['frozen']}")

    print("\n🔗 v2 Ledger (Active)")
    v2 = verify_v2_active()
    print(f"   Status:       {v2['status']}")
    print(f"   Entries:      {v2['entries']}")
    print(f"   Genesis anchored: {v2['genesis_anchored']}")
    print(f"   Chain continuous: {v2['chain_continuous']}")

    print("\n📦 Canonical Live Vault (vault999.jsonl)")
    live = verify_live_vault()
    print(f"   Status:       {live['status']}")
    print(f"   Entries:      {live['entries']}")
    print(
        f"   Last hash:    {live['last_entry_hash'][:16] if live['last_entry_hash'] else 'N/A'}..."
    )

    print("\n🌐 Vault Service (port 8100)")
    svc = verify_service_health()
    print(f"   Reachable:    {svc['reachable']}")
    print(f"   Status:       {svc['status']}")
    print(f"   Service:      {svc.get('service', 'N/A')}")

    # Overall verdict
    print("\n" + "═" * 60)
    healthy = (
        v1["frozen"] is True
        and v2["status"] == "HEALTHY"
        and live["status"] == "HEALTHY"
        and svc["reachable"] is True
    )
    if healthy:
        print("  ✅ VAULT999: HEALTHY (v2 active, v1 frozen, service up)")
    else:
        print("  ⚠️  VAULT999: DEGRADED — inspect details above")
    print("═" * 60)

    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
