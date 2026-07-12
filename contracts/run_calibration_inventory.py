#!/usr/bin/env python3
"""Inventory recovery receipts → execution-class empirical rates (seed calibration)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

RECEIPT_DIR = Path("/root/WELL/loop/receipts")
OUT = Path("/root/A-FORGE/forge_work/falsification/calibration_inventory.json")


def main() -> None:
    files = sorted(RECEIPT_DIR.glob("recovery_*.json"))
    seal = hold = void = other = mut_total = 0
    for p in files:
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        v = d.get("final_verdict") or d.get("verdict") or "OTHER"
        if v == "SEAL":
            seal += 1
        elif v == "HOLD":
            hold += 1
        elif v == "VOID":
            void += 1
        else:
            other += 1
        mut_total += int(d.get("mutation_count") or 0)

    n = seal + hold + void + other
    success_rate = seal / n if n else None
    inv = {
        "claim_class": "agent_execution_allowlisted_recovery",
        "kind": "frequentist_rate",
        "target": "well-heartbeat.recovery_success",
        "n_receipts": n,
        "seal": seal,
        "hold": hold,
        "void": void,
        "other": other,
        "mutations_total": mut_total,
        "success_rate_seal": success_rate,
        "calibration_status": "SEED_ONLY" if (n or 0) < 20 else "MVP_THRESHOLD_MET",
        "min_n_for_mvp": 20,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "Not domain posterior calibration. Execution class only.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(inv, indent=2))
    print(json.dumps(inv, indent=2))


if __name__ == "__main__":
    main()
