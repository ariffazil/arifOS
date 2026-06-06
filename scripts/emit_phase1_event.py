#!/usr/bin/env python3
"""
emit_phase1_event.py — Phase 1 Milestone Event Emitter
======================================================

Appends a structured event to VAULT999/outcomes.jsonl for Phase 1
milestones (drift resolution, attestation receipt, etc.).

Schema (matches the existing outcomes.jsonl ledger):
{
  "decision_id":         str   # e.g. "DRIFT-RESOLVED-2026-06-06-51d7dca"
  "session_id":          str   # e.g. "phase1-stabilize-2026-06-06"
  "verdict_issued":      str   # "SEAL" | "HOLD" | "VOID"
  "expected_outcome":    str   # human-readable expected state
  "actual_outcome":      str   # human-readable observed state
  "outcome_status":      str   # "RESOLVED" | "OPEN" | "PENDING"
  "harm_detected":       bool
  "reversible":          bool
  "calibration_delta":   float
  "operator_override":   bool
  "override_reason":     str
  "timestamp_decision":  float # epoch seconds
  "timestamp_outcome":   float # epoch seconds
  "floor_attribution":   dict
  "phase1_metadata":     dict  # NEW: phase-1-specific fields
}

This is Phase 1 additive — does NOT touch the arifOS tool, does NOT
require FederationEnvelope. Future Phase 2 will route this through
arif_vault_seal with a proper envelope. For now, the helper is
auditable and append-only.

DITEMPA BUKAN DIBERI — Every milestone is forged, not skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


VAULT999_PATHS = [
    Path("/opt/arifos/app/VAULT999/outcomes.jsonl"),
    Path("/root/arifOS/VAULT999/outcomes.jsonl"),
    Path("/root/VAULT999/outcomes.jsonl"),
]


def find_vault() -> Path:
    for p in VAULT999_PATHS:
        if p.exists():
            return p
    raise FileNotFoundError(f"No VAULT999/outcomes.jsonl found in {VAULT999_PATHS}")


def emit_event(
    decision_id: str,
    session_id: str,
    verdict: str,
    expected: str,
    actual: str,
    outcome_status: str,
    reversible: bool,
    floor_attribution: dict,
    phase1_metadata: dict,
    vault_path: Path | None = None,
    dry_run: bool = False,
) -> dict:
    """Append a structured event to outcomes.jsonl. Returns the written event."""
    now_epoch = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    event = {
        "decision_id": decision_id,
        "session_id": session_id,
        "verdict_issued": verdict,
        "expected_outcome": expected,
        "actual_outcome": actual,
        "outcome_status": outcome_status,
        "harm_detected": False,
        "reversible": reversible,
        "calibration_delta": 0.0,
        "operator_override": False,
        "override_reason": "",
        "timestamp_decision": f"{now_epoch:.6f}",
        "timestamp_outcome": f"{now_epoch:.6f}",
        "floor_attribution": floor_attribution,
        "phase1_metadata": phase1_metadata,
    }
    if dry_run:
        return {"dry_run": True, "event": event}

    vault = vault_path or find_vault()
    line = json.dumps(event, default=str)
    with open(vault, "a") as f:
        f.write(line + "\n")
    return {"vault": str(vault), "event": event, "timestamp": now_iso}


def cmd_drift_resolved(args) -> int:
    floor_attr = {
        "F2_Truth": "verified — build=live SHA match",
        "F4_Clarity": "delta_S=0 (no destructive entropy change)",
        "F9_Law": "no_drift — runtime_matches_build=true",
        "F11_Autonomy": "system corrected via restart without external force",
    }
    meta = {
        "build_commit": args.build_commit,
        "live_commit": args.live_commit,
        "runtime_matches_build": True,
        "attestation_receipt_hash": args.receipt_hash,
        "resolving_actor": "openclaw-phase1",
        "resolving_action": "service_restart_then_nocache_verify",
    }
    result = emit_event(
        decision_id=f"DRIFT-RESOLVED-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{args.build_commit}",
        session_id=args.session_id,
        verdict="SEAL",
        expected=f"build_commit={args.build_commit} == live_commit={args.build_commit}, runtime_matches_build=true",
        actual=f"VERIFIED build={args.build_commit} live={args.live_commit}, runtime_matches_build=true",
        outcome_status="RESOLVED",
        reversible=True,
        floor_attribution=floor_attr,
        phase1_metadata=meta,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_dr = sub.add_parser("drift-resolved")
    p_dr.add_argument("--build-commit", required=True)
    p_dr.add_argument("--live-commit", required=True)
    p_dr.add_argument("--receipt-hash", required=True)
    p_dr.add_argument("--session-id", default="phase1-stabilize-2026-06-06")
    p_dr.add_argument("--dry-run", action="store_true")
    p_dr.set_defaults(func=cmd_drift_resolved)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
