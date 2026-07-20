"""
arif_smoke_truth_kernel.py — Phase 5 shadow deployment
═══════════════════════════════════════════════════════════════════════════════
Forged 2026-07-14 · F13 SOVEREIGN RATIFIED

PURPOSE
-------
Run the new truth_kernel.py alongside the legacy TruthVector and log
disagreement, WITHOUT changing production verdicts. This is the safest
path to migrate: observe first, change later.

The script accepts a JSON list of (claim, evidence) bundles, runs the
new engine, and (optionally) reconstructs the legacy TruthVector shape
for the same inputs. Disagreement is logged to JSONL.

USAGE
-----
    # Smoke run on the canonical PETRONAS example
    python3 -m arifosmcp.runtime.arif_smoke_truth_kernel

    # Programmatic
    from arifosmcp.runtime.arif_smoke_truth_kernel import run_shadow
    report = run_shadow([bundle1, bundle2])
    print(report["disagreements"])

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .truth_kernel import (
    Claim,
    ClaimKind,
    Evidence,
    RecordState,
    TruthEngine,
    legacy_truth_vector,
)

logger = logging.getLogger("arifosmcp.smoke_truth_kernel")

# Where to log the shadow run
SHADOW_LOG = Path("/root/A-FORGE/forge_work/2026-07-14/truth_kernel_shadow.jsonl")


# ── Canonical smoke bundle — the PETRONAS dividend-constraint example ─

PETRONAS_BUNDLE: dict[str, Any] = {
    "claim": {
        "claim_id": "petronas-dividend-constraint",
        "text": "Dividend extraction materially constrains PETRONAS reinvestment.",
        "kind": "causal_hypothesis",
        "prior_probability": 0.50,
        "falsifiers": [
            "Free cash flow remains sufficient after dividends and committed capex",
            "Comparable reinvestment is maintained despite dividend extraction",
        ],
    },
    "evidence": [
        {
            "evidence_id": "annual-report-cashflow",
            "description": "Audited cash-flow and dividend figures",
            "likelihood_if_claim": 0.80,
            "likelihood_if_not_claim": 0.30,
            "source_quality": 0.98,
            "independence": 1.0,
            "reproducibility": 1.0,
            "calibration": 0.90,
            "freshness": 0.95,
            "lineage_group": "petronas-audited-report",
            "provenance_uri": "vault://source/annual-report",
        },
        {
            "evidence_id": "capex-plan",
            "description": "Published committed capital programme",
            "likelihood_if_claim": 0.65,
            "likelihood_if_not_claim": 0.55,
            "source_quality": 0.90,
            "independence": 0.90,
            "reproducibility": 0.95,
            "calibration": 0.85,
            "freshness": 0.95,
            "lineage_group": "petronas-capex-disclosure",
            "provenance_uri": "vault://source/capex-plan",
        },
    ],
    "record_state": "attested",
}


# ── Bundle parsing ─────────────────────────────────────────────────────


def _parse_evidence(raw: dict[str, Any]) -> Evidence:
    return Evidence(
        evidence_id=raw["evidence_id"],
        description=raw.get("description", ""),
        likelihood_if_claim=float(raw["likelihood_if_claim"]),
        likelihood_if_not_claim=float(raw["likelihood_if_not_claim"]),
        source_quality=float(raw.get("source_quality", 1.0)),
        independence=float(raw.get("independence", 1.0)),
        reproducibility=float(raw.get("reproducibility", 1.0)),
        calibration=float(raw.get("calibration", 1.0)),
        freshness=float(raw.get("freshness", 1.0)),
        lineage_group=raw.get("lineage_group"),
        provenance_uri=raw.get("provenance_uri"),
    )


def _parse_claim(raw: dict[str, Any]) -> Claim:
    return Claim(
        claim_id=raw["claim_id"],
        text=raw.get("text", ""),
        kind=ClaimKind(raw["kind"]),
        prior_probability=float(raw.get("prior_probability", 0.5)),
        falsifiers=tuple(raw.get("falsifiers", ())),
        declared_frame=raw.get("declared_frame"),
        affected_humans=tuple(raw.get("affected_humans", ())),
    )


# ── Shadow runner ─────────────────────────────────────────────────────


def _assess_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    claim = _parse_claim(bundle["claim"])
    evidence = [_parse_evidence(e) for e in bundle.get("evidence", [])]
    record_state = RecordState(bundle.get("record_state", "transient"))
    assessment = TruthEngine().assess(claim, evidence, record_state=record_state)
    legacy = legacy_truth_vector(assessment)
    return {
        "claim_id": claim.claim_id,
        "new": assessment.to_dict(),
        "legacy": legacy,
    }


def _classify_disagreement(new: dict[str, Any], legacy: dict[str, Any]) -> str:
    """Lightweight disagreement classifier."""
    diffs: list[str] = []
    # truth_tau → warrant
    new_w = new["warrant"]
    old_t = legacy["truth_tau"]
    if abs(new_w - old_t) > 0.1:
        diffs.append(f"warrant={new_w:.3f} vs truth_tau={old_t:.3f}")
    # uncertainty_sigma → entropy_bits
    new_h = new["epistemic_entropy_bits"]
    old_s = legacy["uncertainty_sigma"]
    if abs(new_h - old_s) > 0.5:
        diffs.append(f"entropy_bits={new_h:.3f} vs uncertainty_sigma={old_s:.3f}")
    # coherence_c → 1 - c_conflict
    new_c = 1.0 - new["contradiction_index"]
    old_c = legacy["coherence_c"]
    if abs(new_c - old_c) > 0.1:
        diffs.append(f"coherence={new_c:.3f} vs coherence_c={old_c:.3f}")
    return "AGREE" if not diffs else "DIFFER: " + "; ".join(diffs)


def run_shadow(
    bundles: list[dict[str, Any]] | None = None,
    log_path: Path | None = None,
    *,
    write_log: bool = True,
) -> dict[str, Any]:
    """Run shadow assessment for each bundle and log disagreement.

    Returns a summary report.
    """
    if bundles is None:
        bundles = [PETRONAS_BUNDLE]
    out_path = log_path or SHADOW_LOG
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    n_agree = 0
    n_differ = 0
    for b in bundles:
        result = _assess_bundle(b)
        result["disagreement"] = _classify_disagreement(result["new"], result["legacy"])
        results.append(result)
        if result["disagreement"] == "AGREE":
            n_agree += 1
        else:
            n_differ += 1
        if write_log:
            with out_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, default=str) + "\n")

    return {
        "bundles": len(bundles),
        "agree": n_agree,
        "differ": n_differ,
        "results": results,
        "log_path": str(out_path),
    }


def main() -> int:
    """Entry point for `python -m arifosmcp.runtime.arif_smoke_truth_kernel`."""
    report = run_shadow()
    print(
        json.dumps(
            {
                "bundles": report["bundles"],
                "agree": report["agree"],
                "differ": report["differ"],
                "log_path": report["log_path"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
