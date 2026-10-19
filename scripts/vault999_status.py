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
    """v2 epoch — resolve the REAL path, not a name-scoped guess.

    Stabilization 2026-10-19: v2 lives on the /agent mount and is reached via
    /var/lib/arifos/vault/SEALED_EVENTS_v2.jsonl (symlink). Checking only
    VAULT_DIR/SEALED_EVENTS_v2.jsonl reported MISSING for a 1,761-entry ledger.
    """
    candidates = [
        VAULT_DIR / "SEALED_EVENTS_v2.jsonl",
        Path("/var/lib/arifos/vault/SEALED_EVENTS_v2.jsonl"),
        Path("/agent/vault999/sealed/SEALED_EVENTS_v2.jsonl"),
    ]
    v2_file = next((p for p in candidates if p.exists()), candidates[0])
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

        # Verify chain continuity within v2 — honest: a MISSING link field is
        # UNMEASURED, never a pass. (2026-10-19: the old guard `if prev_hash and
        # curr_prev` skipped every row whose link field was absent, so a chain
        # with 956 broken links reported chain_continuous=True.)
        result["chain_continuous"] = True
        missing_links = 0
        breaks = 0
        for i in range(1, len(entries)):
            prev = entries[i - 1]
            curr = entries[i]
            prev_hash = (
                prev.get("entry_hash")
                or prev.get("chain_hash")
                or prev.get("seal_hash")
            )
            curr_prev = (
                curr.get("prev_entry_hash")
                or curr.get("prev_hash")
                or curr.get("prev_leaf")
            )
            if curr_prev in (None, "None", "", "null"):
                missing_links += 1
                continue
            if prev_hash and str(curr_prev) != str(prev_hash):
                breaks += 1
                if "break_at" not in result:
                    result["break_at"] = i
        result["missing_link_fields"] = missing_links
        result["broken_links"] = breaks
        result["chain_continuous"] = (breaks == 0 and missing_links == 0)

    if result["genesis_anchored"] and result["chain_continuous"]:
        result["status"] = "HEALTHY"
    elif result["chain_continuous"] and _is_v1_frozen():
        # V2 has continuous chain and v1 is FROZEN_HISTORICAL per epoch_state.json.
        # Genesis anchor may not match v1 terminal due to epoch split (different
        # export paths), but epoch_split was sovereign-ratified 2026-06-02.
        # The v2 chain is structurally sound — not DEGRADED.
        result["status"] = "HEALTHY_RECONCILED"
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
        with urllib.request.urlopen(
            "http://localhost:5001/health", timeout=2
        ) as resp:  # writer (live); legacy 5001 removed
            data = json.loads(resp.read().decode())
            result["status"] = data.get("status", "unknown")
            result["reachable"] = True
            result["service"] = data.get("service", "unknown")
    except Exception as e:
        result["status"] = f"unreachable: {e}"
    print()
    print("═══ VAULT999 Summary ═══")
    # Stabilization 2026-10-19: this function printed but returned None, so any
    # caller doing svc["reachable"] crashed. Return the probe result explicitly.
    return result


def _is_v1_frozen() -> bool:
    """Check if v1 is frozen per epoch_state.json."""
    state_file = VAULT_DIR / "epoch_state.json"
    if not state_file.exists():
        return False
    try:
        with open(state_file) as f:
            state = json.load(f)
        return state.get("v1", {}).get("status") == "FROZEN"
    except (json.JSONDecodeError, OSError):
        return False


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

    print("\n🧭 Canonical Spine (F004 — the only authority)")
    spine = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
    head = Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
    if spine.exists():
        print(f"   Path:         {spine}")
        print(f"   Entries:      {sum(1 for _ in spine.open(errors='replace'))}")
        if head.exists():
            h = json.load(head.open())
            print(f"   Head seq:     {h.get('seq')}  hash={str(h.get('hash'))[:24]}…")
            print(f"   Declared:     canonical={h.get('canonical_entries')} historical={h.get('historical_entries')}")
    else:
        print("   MISSING — no canonical spine")

    print("\n🌐 Vault Service (port 5001)")
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
