#!/usr/bin/env python3
"""
sot_cron.py — Federation SOT/Drift Cron (Vault Bridge tick)

Architecture (Continuous World Model):
  Phase 1 — READ STATE    tail VAULT999 outcomes.jsonl, recover prior
                           payload_hash + unresolved_drift for actor=sot-cron.
  Phase 2 — MODULATE      focus-on prior drift if any, else full sweep.
  Phase 3 — CHECK         diff ESTATE_MANIFEST vs live workspace; build payload.
  Phase 4 — SEAL          delegate to federation_ritual.py seal (canonical
                           sovereign path) — this is the Vault Bridge.

F13 SOVEREIGN: the seal call uses federation_ritual.py which authenticates
as the sovereign actor via HMAC rootkey. The cron is a delegate.

Doctrine: DITEMPA BUKAN DIBERI — Forged, Not Given.
T3 grant 2026-08-07 by 888 SOVEREIGN.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VAULT_PATH = Path("/root/arifOS/VAULT999/outcomes.jsonl")
ENVELOPE_PATH = Path("/root/.arifos/federation-session.json")
ACTOR = "arif"  # sovereign — HMAC rootkey path via federation_ritual
KERNEL_URL = "http://127.0.0.1:8088"
ORGANS = ["arifOS", "A-FORGE", "AAA", "GEOX", "WEALTH", "WELL", "arifFlow"]


def read_prev_state(vault: Path, actor: str) -> dict:
    """Phase 1 — read prior vault state for our actor."""
    if not vault.exists():
        return {"prev_payload_hash": "0" * 16, "prev_drift": [],
                "is_first_run": True, "anchor_kind": "vault_missing"}
    last_match = None
    last_any = None
    with vault.open("rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - 65536))
        chunk = f.read().decode("utf-8", errors="replace")
    for line in reversed(chunk.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if last_any is None:
            last_any = e
        if e.get("actor") == actor:
            last_match = e
            break
    if last_match is None:
        anchor = last_any or {}
        return {"prev_payload_hash": anchor.get("payload_hash", "0" * 16),
                "prev_drift": [], "is_first_run": True,
                "anchor_kind": "any_actor"}
    payload = last_match.get("payload", {}) or {}
    return {"prev_payload_hash": last_match.get("payload_hash", "0" * 16),
            "prev_drift": payload.get("unresolved_drift", []),
            "is_first_run": False, "anchor_kind": "self"}


def modulate(prev_state: dict) -> dict:
    """Phase 2 — decide focus-or-full strategy."""
    carried = prev_state.get("prev_drift", [])
    return {"strategy": "focused" if carried else "full",
            "focus_on": carried,
            "carried_from_prev_payload_hash": prev_state.get("prev_payload_hash", "0" * 16)}


def check_workspace(modulation: dict) -> dict:
    """Phase 3 — diff manifest vs live workspace, build payload."""
    drift_flags: list[str] = []
    git_ahead: dict[str, int] = {}
    for org in ORGANS:
        repo = Path("/root") / org
        if not (repo / ".git").exists():
            drift_flags.append(f"git_not_a_repo:{org}")
            continue
        try:
            out = subprocess.check_output(
                ["git", "-C", str(repo), "rev-list", "--count", "@{u}..HEAD"],
                stderr=subprocess.DEVNULL, text=True, timeout=5,
            ).strip()
            n = int(out) if out.isdigit() else 0
            git_ahead[org] = n
            if n > 0:
                drift_flags.append(f"git_unpushed:{org}={n}")
        except Exception:
            git_ahead[org] = -1
            drift_flags.append(f"git_no_upstream:{org}")
    new_unresolved = [
        f for f in drift_flags
        if not any(r["flag"] == f and r["resolved"]
                   for r in [])
    ]
    return {
        "intent": "continuous-world-model-sot-check",
        "modulation": modulation,
        "git_ahead": git_ahead,
        "drift_flags_new": [f for f in drift_flags if f not in modulation["focus_on"]],
        "unresolved_drift": new_unresolved,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "tick_seq": int(time.time()),
    }


from datetime import timezone  # late import to avoid circular

def seal_via_federation_ritual(summary: str, payload: dict) -> tuple[bool, str]:
    """Phase 4 — delegate to canonical sovereign seal path."""
    # Init sovereign session
    init = subprocess.run(
        ["python3", "/root/scripts/federation_ritual.py", "init",
         "--actor", ACTOR, "--intent", summary],
        capture_output=True, text=True, timeout=30,
    )
    if init.returncode != 0:
        return False, f"init failed: {init.stderr[-200:]}"
    # Seal
    seal = subprocess.run(
        ["python3", "/root/scripts/federation_ritual.py", "seal",
         "--summary", summary,
         "--entry-content", json.dumps(payload)],
        capture_output=True, text=True, timeout=30,
    )
    return seal.returncode == 0, seal.stdout[-300:] + " | " + seal.stderr[-200:]


def main() -> int:
    started = time.time()
    try:
        prev = read_prev_state(VAULT_PATH, ACTOR)
        modulation = modulate(prev)
        payload = check_workspace(modulation)
        ok, msg = seal_via_federation_ritual(
            f"sotcron tick #{payload.get('tick_seq', '?')}",
            payload,
        )
        elapsed = time.time() - started
        sys.stderr.write(
            f"[sotcron] ok={ok} elapsed={elapsed:.1f}s "
            f"drift_new={len(payload['drift_flags_new'])} "
            f"unresolved={len(payload['unresolved_drift'])}\n"
        )
        if not ok:
            sys.stderr.write(f"[sotcron] seal_failed: {msg}\n")
        return 0 if ok else 1
    except Exception as e:
        sys.stderr.write(f"[sotcron] HOLD: {type(e).__name__}: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
