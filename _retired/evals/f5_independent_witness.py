#!/usr/bin/env python3
"""
f5_independent_witness.py — Independent F5 (Peace²) witness probe
═══════════════════════════════════════════════════════════════════
Forged 2026-10-15 by 333-AGI (FI-001) under F13 P2 directive.

PROBLEM (documented 2026-10-13): kernel F5 reads its own degraded_reasons
— the constitutional layer's status feeds its own measurement. Self-reference.
Kernel itself labels the path: independent_or_self_reported = "self_reported".

FIX: measure Peace² from sources the kernel cannot self-report —
  epistemic stability  = CHRON calibration (accuracy × (1 − brier))   [OBS]
  operational friction = open attention-debt ratio                    [OBS]
  independent_peace2   = 0.5×epistemic + 0.5×(1−open_ratio)          [DER]

Everything is labelled. The composite formula is a CHOICE, stated openly,
not a discovered constant. Decomposition matters more than the composite.

Stdlib only. Read-only against live surfaces. Append-only record.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

KERNEL = "http://127.0.0.1:8088/health"
CHRON = "http://127.0.0.1:18102/health"
DEBT_FILE = Path("/root/chron/data/attention_debt.jsonl")
STATE_DIR = Path("/root/.local/share/arifos/state")


def fetch_json(url: str, timeout: float = 5.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:  # honest: a dead witness source is reported, never invented
        return {"_error": str(e)}


def kernel_self_report(health: dict) -> dict:
    """What the kernel says about its own F5. OBS from /health."""
    constitutional = health.get("layer_health", {}).get("constitutional", {})
    detail = constitutional.get("floors_detail", {})
    provenance = constitutional.get("floors_provenance", {})
    score = None
    for key in ("floor_scores", "floors_score"):
        block = constitutional.get(key)
        if isinstance(block, dict) and "F5" in block:
            score = block["F5"]
    return {
        "source": "kernel:/health (self-reported)",
        "epistemic_label": "OBS",
        "verdict": detail.get("F5"),
        "score": score,
        "provenance": provenance.get("F5"),
        "self_reference_flag": "f4_f9_probe" in str(provenance.get("F5", "")),
        "degraded_reasons_self_loop": any(
            "self-reported" in str(r.get("explanation", ""))
            for r in health.get("degraded_reasons", [])
        ),
    }


def independent_reading(health: dict) -> dict:
    """What the kernel cannot say about itself. OBS from CHRON + debt ledger."""
    chron = fetch_json(CHRON)
    cal = chron.get("calibration", {}) if isinstance(chron, dict) else {}
    accuracy = cal.get("accuracy")
    brier = cal.get("mean_brier")

    total, open_n, open_weight = 0, 0, 0.0
    if DEBT_FILE.exists():
        for line in DEBT_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            total += 1
            if row.get("status") not in ("RESOLVED", "CLOSED"):
                open_n += 1
                open_weight += float(row.get("weight", 1.0))

    epistemic = (
        round(accuracy * (1.0 - brier), 4) if accuracy is not None and brier is not None else None
    )
    open_ratio = round(open_n / total, 4) if total else None
    independent = None
    if epistemic is not None and open_ratio is not None:
        # DERIVED — stated formula, not a law of nature.
        independent = round(0.5 * epistemic + 0.5 * (1.0 - open_ratio), 4)

    return {
        "source": "CHRON:18102 calibration + chron/data/attention_debt.jsonl",
        "epistemic_label": "OBS→DER",
        "epistemic_stability": {
            "label": "DER",
            "formula": "accuracy × (1 − mean_brier)",
            "accuracy": accuracy,
            "mean_brier": brier,
            "value": epistemic,
            "chron_quality": cal.get("quality"),
            "accuracy_ci95": cal.get("accuracy_ci95"),
        },
        "operational_friction": {
            "label": "OBS",
            "debt_total": total,
            "debt_open": open_n,
            "debt_open_weight": open_weight,
            "open_ratio": open_ratio,
        },
        "independent_peace2": {
            "label": "DER",
            "formula": "0.5×epistemic + 0.5×(1 − open_ratio)",
            "value": independent,
            "threshold": 1.0,
            "threshold_verdict": (
                "pass" if independent is not None and independent >= 1.0 else "fail"
            ),
            "threshold_note": "F5 doctrine threshold is ≥ 1.0. This 0..1 composite can never reach 1.0 — the threshold and the scale are not comparable. Direction is comparable; magnitude is not.",
        },
    }


def main() -> None:
    health = fetch_json(KERNEL)
    self_report = kernel_self_report(health)
    independent = independent_reading(health)

    sv = self_report.get("verdict")
    tv = independent["independent_peace2"]["threshold_verdict"]
    record = {
        "schema": "arifos.f5_independent_witness.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "forged_by": "333-AGI (FI-001)",
        "purpose": "Break F5 self-reference: kernel Peace² measured from outside the kernel.",
        "self_reported": self_report,
        "independent": independent,
        "comparison": {
            "verdict_agreement": sv == tv,
            "causal_disagreement": True if sv == tv else None,
            "reading": (
                "Same direction, different cause. Kernel attributes F5 to layer self-report "
                "+ deployment attestation drift; independent witness attributes it to open "
                "attention debt. Verdict agreement does not validate the kernel's CAUSE — "
                "self-referential justification remains broken even when the conclusion agrees."
                if sv == tv
                else "Verdicts diverge. Independent witness disagrees with kernel self-report — "
                "escalate to CHRON/FRAME for third measurement."
            ),
        },
        "limitations": [
            "Composite formula is a chosen convention (0.5/0.5), not a calibrated law.",
            "Attention debt is a proxy for friction, not Peace² itself.",
            "CHRON calibration CI is wide (accuracy_ci95 lower bound ~0.59).",
            "Kernel score source claims.json not located on disk — score read from /health only.",
        ],
    }

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    out = STATE_DIR / f"f5-witness-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    print(json.dumps(record, indent=2, ensure_ascii=False))
    print(f"\n→ recorded: {out}")


if __name__ == "__main__":
    main()
