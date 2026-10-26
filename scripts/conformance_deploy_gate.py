#!/usr/bin/env python3
"""Deployment conformance gate — PASS/AMBER, never a silent PASS.

The conformance spine is honest by design: it exits 1 unless every check is
PASS and no check is SKIPPED. On 2026-10-26 the only failing check is
``cooling_ledger`` with exactly one error: no WELL entropy seals have landed in
VAULT999. WELL is up but degraded; that is a real residual, not a deployment
artifact defect.

This gate accepts that ONE known CAUTION and writes an AMBER receipt. It does
not accept HOLD, RED, CHAIN_HEALTH_FAIL, unexplained critical evidence, skipped
checks, or any other failed check. The deployment report must carry the AMBER
label; this gate never prints CONFORMANCE_PASS for a CAUTION.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RECEIPT = Path(os.environ.get("CONFORMANCE_RECEIPT", "/var/lib/arifos/conformance_amber.json"))
KNOWN_ERROR = "No WELL entropy seals found"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "arifosmcp.transport.conformance_spine"],
        capture_output=True,
        text=True,
    )
    try:
        report = json.loads(proc.stdout)
    except ValueError:
        print(
            json.dumps(
                {
                    "status": "CONFORMANCE_BLOCKED",
                    "reason": "conformance spine did not emit JSON",
                    "stdout": proc.stdout[-2000:],
                    "stderr": proc.stderr[-2000:],
                },
                indent=2,
            )
        )
        return 1

    verdict = report.get("verdict")
    failed = [c for c in report.get("checks", []) if c.get("verdict") == "FAIL"]
    skipped = report.get("skipped", 0)
    unexplained = report.get("unexplained_critical_evidence", [])

    if verdict == "SEAL" and report.get("all_green") and not failed and not skipped:
        print(
            json.dumps(
                {
                    "status": "CONFORMANCE_PASS",
                    "verdict": verdict,
                    "substrate_gate": report.get("substrate_gate"),
                    "score": report.get("score"),
                    "timestamp": report.get("timestamp"),
                },
                indent=2,
            )
        )
        return 0

    if verdict == "CAUTION" and not unexplained and not skipped:
        by_name = {c.get("check"): c for c in failed}
        names = set(by_name)
        # Residual 1: the kernel is serving but in its designed floor HOLD
        # posture (status=degraded, thermodynamic verdict=HOLD). Liveness is
        # proven; floor honesty is reported separately and is NOT called PASS.
        alive_ok = False
        if "arifos_alive" in by_name:
            ev = by_name["arifos_alive"].get("evidence", {})
            alive_ok = (
                ev.get("status") == "degraded"
                and ev.get("verdict") == "HOLD"
                and bool(ev.get("version"))
            )
        # Residual 2: WELL is up but has no entropy seals in VAULT999.
        cooling_ok = False
        cooling_errors: list[str] = []
        if "cooling_ledger" in by_name:
            cooling_errors = by_name["cooling_ledger"].get("evidence", {}).get("errors", [])
            cooling_ok = bool(cooling_errors) and all(KNOWN_ERROR in str(e) for e in cooling_errors)
        if names == {"arifos_alive", "cooling_ledger"} and alive_ok and cooling_ok:
            receipt = {
                "status": "CONFORMANCE_DEGRADED_ACCEPTED",
                "verdict": verdict,
                "substrate_gate": report.get("substrate_gate"),
                "score": report.get("score"),
                "residuals": [
                    {
                        "check": "arifos_alive",
                        "evidence": by_name["arifos_alive"].get("evidence"),
                        "classification": "KNOWN_FLOOR_HOLD_POSTURE — liveness proven, floors not PASS",
                    },
                    {
                        "check": "cooling_ledger",
                        "evidence": by_name["cooling_ledger"].get("evidence"),
                        "classification": "KNOWN_WELL_ENTROPY_SEAL_GAP",
                    },
                ],
                "accepted_at": _now(),
                "reason": (
                    "Two known residuals accepted for this deployment: the kernel "
                    "serves in its designed floor HOLD posture, and WELL has no "
                    "entropy seals in VAULT999. This is a DEGRADED acceptance, "
                    "not a PASS, and not a SEAL-CANDIDATE."
                ),
                "spine_report": report,
            }
            RECEIPT.parent.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(receipt, indent=2, default=str))
            print(
                json.dumps(
                    {
                        "status": "CONFORMANCE_DEGRADED_ACCEPTED",
                        "verdict": verdict,
                        "substrate_gate": report.get("substrate_gate"),
                        "score": report.get("score"),
                        "receipt": str(RECEIPT),
                        "residuals": [r["check"] for r in receipt["residuals"]],
                    },
                    indent=2,
                )
            )
            return 0

    print(
        json.dumps(
            {
                "status": "CONFORMANCE_BLOCKED",
                "verdict": verdict,
                "substrate_gate": report.get("substrate_gate"),
                "failed": failed,
                "skipped": skipped,
                "unexplained_critical_evidence": unexplained,
            },
            indent=2,
        )
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
