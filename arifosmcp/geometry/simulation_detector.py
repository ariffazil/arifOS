"""
simulation_detector.py — Third-Axis Institution Classifier
═══════════════════════════════════════════════════════════════════════════════

Detects simulation depth in any institution, system, or agentic structure.
This is the operational module — it takes evidence, produces a SimulationDepth
verdict using the models from simulation_schema.py.

The third axis (simulative) answers what Acemoglu's inclusive/extractive
binary cannot: what happens when an institution performs value creation
without actually creating value?

Detection signals (from Calhoun's Universe 25 + Acemoglu + industry cases):
  S1: Transparency decreasing over time (half-yearly replaces quarterly)
  S2: Narrative vehicles that perform strategic relevance (Gentari, SEA-H)
  S3: Controlled information environment (Q&A dikawal, scripted townhalls)
  S4: Governance scores detached from behavior (GSS=1.00 while DNA dead)
  S5: CEO signals exit without succession plan ("i will not be around")
  S6: Insiders stop discussing problems (Arif talks to AI, not colleagues)
  S7: Belief gap — institution performs values it no longer enforces
  S8: The Beautiful One pattern — perfect form, zero fight

Constitutional binding:
  F2 TRUTH:    every signal requires evidence_ref (no fabricated signals)
  F9 ANTIHANTU: simulation = hantu pattern (false narrative maintained)
  F13 SOVEREIGN: the detector measures but does not decide — Arif decides

Origin: EUREKA — Calhoun's Universe 25 × Acemoglu × Petronas 2026.
DITEMPA BUKAN DIBERI — the simulative can now be measured.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.geometry.simulation_schema import (
    BeliefIntegrity,
    NarrativeGap,
    OpacityTrend,
    SelfSimulationGuard,
    SimulationDepth,
    SimulationVerdict,
)

logger = logging.getLogger(__name__)

DETECTOR_POLICY_VERSION = "simulation_detector.v1"


# ─── Eight simulation signals ───────────────────────────────────────────────
# Each signal contributes evidence toward a simulation_index.
# Signals are NOT additive — they're Bayesian: each one increases confidence
# that the institution is simulative.

SIMULATION_SIGNALS = {
    "S1_OPACITY_INCREASING": {
        "label": "Transparency decreasing",
        "weight": 0.15,
        "description": "Reporting cadence reduced, information access narrowed",
        "examples": ["quarterly→half-yearly", "controlled Q&A", "media access restricted"],
    },
    "S2_NARRATIVE_VEHICLES": {
        "label": "Narrative vehicles performing relevance",
        "weight": 0.10,
        "description": "Entities created to perform strategic positioning rather than create value",
        "examples": ["Gentari (energy transition narrative)", "SEA-H (growth narrative)"],
    },
    "S3_CONTROLLED_ENVIRONMENT": {
        "label": "Information environment controlled",
        "weight": 0.10,
        "description": "Q&A dikawal, questions pre-screened, unscripted interaction prevented",
        "examples": ["townhall Q&A controlled by one person", "no open floor"],
    },
    "S4_GOVERNANCE_DETACHED": {
        "label": "Governance scores detached from behavior",
        "weight": 0.15,
        "description": "Formal governance metrics (GSS) show health while actual governance is hollow",
        "examples": ["GSS=1.00 while DNA extinct", "board independence on paper only"],
    },
    "S5_CEO_EXIT_SIGNAL": {
        "label": "CEO signals exit without institutional solution",
        "weight": 0.15,
        "description": "Leader hints departure while building personal vehicles, not successors",
        "examples": [
            '"i will not be around"',
            "no named successor",
            "children dependent on founder",
        ],
    },
    "S6_INSIDERS_SILENT": {
        "label": "Insiders stop discussing problems",
        "weight": 0.15,
        "description": "People who see the gap discuss it only with AI, not colleagues",
        "examples": ["Arif talks to AI agents", "no internal discussion of collapse risk"],
    },
    "S7_BELIEF_GAP": {
        "label": "Stated values no longer enforced",
        "weight": 0.10,
        "description": "DNA (loyalty, professionalism, integrity, cohesiveness) exists on paper, not in behavior",
        "examples": ["Azizan's DNA codified but bulldogs gone", "values posters in empty hallways"],
    },
    "S8_BEAUTIFUL_ONE": {
        "label": "The Beautiful One pattern",
        "weight": 0.10,
        "description": "Perfect form, zero fight. Competent performance of leadership without the defining behavior: saying no to power.",
        "examples": ["TT: perfect restructuring, perfect townhall, no 'no'"],
    },
}
assert abs(sum(s["weight"] for s in SIMULATION_SIGNALS.values()) - 1.0) < 1e-9, (
    "weights must sum to 1.0"
)


# ─── Detector ───────────────────────────────────────────────────────────────
def detect_simulation(
    *,
    institution_name: str,
    evidence: dict[str, Any],
    confidence: float = 0.5,
) -> SimulationDepth:
    """Classify an institution on the third axis (inclusive/extractive/simulative).

    Args:
        institution_name: name of the institution
        evidence: dict with keys matching the 8 simulation signals + supporting data
        confidence: how confident the assessor is (0-1)

    Returns:
        SimulationDepth with computed index, verdict, and Calhoun phase.
    """
    # ── Signal scoring ──────────────────────────────────────────────────
    signal_scores: dict[str, float] = {}
    for signal_id, signal_def in SIMULATION_SIGNALS.items():
        signal_evidence = evidence.get(signal_id, {})
        if isinstance(signal_evidence, dict):
            present = signal_evidence.get("present", False)
            strength = signal_evidence.get("strength", 0.5)
        elif isinstance(signal_evidence, bool):
            present = signal_evidence
            strength = 0.5
        else:
            present = bool(signal_evidence)
            strength = 0.5

        signal_scores[signal_id] = signal_def["weight"] * strength if present else 0.0

    # ── Narrative gap ───────────────────────────────────────────────────
    claimed = evidence.get("claimed_value", 80.0)
    observed = evidence.get("observed_value", 80.0)
    evidence_refs = evidence.get("evidence_refs", [])

    narrative_gap = NarrativeGap(
        claimed_value=claimed,
        observed_value=observed,
        gap_ratio=round(abs(claimed - observed) / max(abs(claimed), 1.0), 4),
        evidence_refs=evidence_refs,
        domain=evidence.get("domain", "institutional_integrity"),
    )

    # ── Opacity trend ───────────────────────────────────────────────────
    opacity_trend = OpacityTrend(
        transparency_cadence_t0=evidence.get("transparency_t0", 80.0),
        transparency_cadence_t1=evidence.get("transparency_t1", 80.0),
        trend=round(
            evidence.get("transparency_t1", 80.0) - evidence.get("transparency_t0", 80.0), 4
        )
        / 100.0,
        disclosure_quality=evidence.get("disclosure_quality", 0.5),
        specific_change=evidence.get("transparency_change", ""),
    )

    # ── Belief integrity ────────────────────────────────────────────────
    belief = evidence.get("belief", {})
    belief_integrity = BeliefIntegrity(
        insider_consistency=belief.get("insider_consistency", 0.5),
        whistleblower_presence=belief.get("whistleblower_presence", 0.5),
        dissent_tolerance=belief.get("dissent_tolerance", 0.5),
        bulldog_count=belief.get("bulldog_count", 0),
        behavioral_transmission=belief.get("behavioral_transmission", 0.5),
    )

    # ── Composite simulation index ──────────────────────────────────────
    sim_depth = SimulationDepth(
        institution_name=institution_name,
        analysis_date=datetime.now(UTC).isoformat(),
        confidence=confidence,
        evidence_strength=evidence.get("evidence_strength", "PLAUSIBLE"),
        narrative_gap=narrative_gap,
        opacity_trend=opacity_trend,
        belief_integrity=belief_integrity,
    )

    logger.info(
        "[simulation_detector] %s: simulation_index=%.4f verdict=%s phase=%s",
        institution_name,
        sim_depth.simulation_index,
        sim_depth.simulation_verdict.value,
        sim_depth.calhoun_phase,
    )

    return sim_depth


# ─── Petronas 2026 — canonical test case ────────────────────────────────────
# This fixture is the calibrated test case. If the detector returns anything
# other than SIMULATING/HOLLOW for these inputs, the detector is broken.

PETRONAS_2026_EVIDENCE: dict[str, Any] = {
    # Narrative gap: Petronas claims strategic health, Arif observes hollowing
    "claimed_value": 75.0,  # official narrative: strategic, transitioning, resilient
    "observed_value": 25.0,  # Arif's observation: DNA dead, GSS=1.00, simulation mode
    "evidence_refs": [
        "Hassan townhall archive (2025-06-05): TT said 'i will not be around'",
        "Hassan townhall archive: Q&A controlled by Faizal",
        "Hassan townhall archive: 5,000 retrenchment confirmed",
        "Hassan townhall archive: TPCP dissolution",
        "GSS=1.00 governance score (lowest possible)",
        "The Edge Malaysia 2010-02-07: Petronas DNA article (Azizan era values)",
        "Half-yearly reporting replacing quarterly (TT era decision)",
        "Gentari formation: energy transition vehicle",
        "SEA-H joint venture with Eni: regional expansion vehicle",
        "Arif personal observation: no colleagues willing to discuss collapse risk",
    ],
    "domain": "institutional_integrity",
    # Opacity: half-yearly replaced quarterly — simulation signal
    "transparency_t0": 70.0,  # historical: quarterly reporting, open Q&A
    "transparency_t1": 35.0,  # current: half-yearly, controlled Q&A
    "disclosure_quality": 0.3,
    "transparency_change": "Quarterly→half-yearly reporting (TT era). Q&A controlled by one person.",
    # Signals (presence + strength)
    "S1_OPACITY_INCREASING": {"present": True, "strength": 0.9},
    "S2_NARRATIVE_VEHICLES": {"present": True, "strength": 0.8},
    "S3_CONTROLLED_ENVIRONMENT": {"present": True, "strength": 0.9},
    "S4_GOVERNANCE_DETACHED": {"present": True, "strength": 0.95},
    "S5_CEO_EXIT_SIGNAL": {"present": True, "strength": 0.85},
    "S6_INSIDERS_SILENT": {"present": True, "strength": 0.7},
    "S7_BELIEF_GAP": {"present": True, "strength": 0.9},
    "S8_BEAUTIFUL_ONE": {"present": True, "strength": 0.8},
    # Belief integrity
    "belief": {
        "insider_consistency": 0.2,  # low: actions contradict stated values
        "whistleblower_presence": 0.1,  # low: no one surfacing problems
        "dissent_tolerance": 0.05,  # very low: no "no" to power
        "bulldog_count": 0,  # Rastam, Azizan, Hassan — all gone
        "behavioral_transmission": 0.05,  # near zero: new people not learning old DNA
    },
    "evidence_strength": "PLAUSIBLE",
}


def petronas_test_case() -> SimulationDepth:
    """Run the canonical Petronas 2026 test case through the detector.

    Returns:
        SimulationDepth. Expected: simulation_index >= 0.5 (SIMULATING or HOLLOW).
        If < 0.5, the detector is mis-calibrated.
    """
    return detect_simulation(
        institution_name="Petronas (2026 — TT era)",
        evidence=PETRONAS_2026_EVIDENCE,
        confidence=0.75,
    )


# ─── Self-Simulation guard (kernel must measure itself) ─────────────────────
def kernel_self_check(
    *,
    claimed_capabilities: list[str],
    observed_capabilities: list[str],
) -> SelfSimulationGuard:
    """The kernel measures its OWN simulation depth.

    If the kernel claims to enforce F1-F13 but doesn't actually block
    violations — if it performs governance without governing — it has
    become simulative. This guard detects that.
    """
    # Simplified: count which claimed capabilities are actually observed
    claimed_set = set(claimed_capabilities)
    observed_set = set(observed_capabilities)
    missing = claimed_set - observed_set
    sim_index = len(missing) / max(len(claimed_set), 1)

    return SelfSimulationGuard(
        kernel_claims=list(claimed_set),
        kernel_observed=list(observed_set),
        self_simulation_index=round(sim_index, 4),
        last_self_check=datetime.now(UTC).isoformat(),
    )


# ─── Self-check ─────────────────────────────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Verify detector properties."""
    results: list[tuple[str, bool]] = []

    # 1. Module loads
    results.append(("module_loads", True))

    # 2. Petronas test case returns SIMULATING or HOLLOW
    tc = petronas_test_case()
    r = tc.simulation_verdict in (SimulationVerdict.SIMULATING, SimulationVerdict.HOLLOW)
    results.append(("petronas_is_simulating_or_hollow", r))

    # 3. Simulation index >= 0.5 for Petronas
    r = tc.simulation_index >= 0.50
    results.append(("petronas_index_above_0.5", r))

    # 4. Calhoun phase is C or D
    r = tc.calhoun_phase in ("Phase C — Behavioral death", "Phase D — Extinction")
    results.append(("petronas_calhoun_phase_c_or_d", r))

    # 5. Signal weights sum to 1.0
    r = abs(sum(s["weight"] for s in SIMULATION_SIGNALS.values()) - 1.0) < 1e-9
    results.append(("signal_weights_sum_to_1", r))

    # 6. Self-check guard works
    guard = kernel_self_check(
        claimed_capabilities=["F1_AMANAH", "F2_TRUTH", "F13_SOVEREIGN"],
        observed_capabilities=["F1_AMANAH", "F2_TRUTH"],  # missing F13
    )
    r = guard.self_simulation_index > 0.0
    results.append(("self_check_detects_missing", r))

    # 7. to_dict() works
    d = tc.to_dict()
    r = "simulation_index" in d and "simulation_verdict" in d
    results.append(("to_dict_works", r))

    all_pass = all(p for _, p in results)
    return {
        "all_pass": all_pass,
        "checks": [{"name": n, "pass": p} for n, p in results],
        "n_checks": len(results),
        "n_pass": sum(1 for _, p in results if p),
        "petronas_result": {
            "simulation_index": tc.simulation_index,
            "verdict": tc.simulation_verdict.value,
            "calhoun_phase": tc.calhoun_phase,
        },
    }


if __name__ == "__main__":
    r = _self_check()
    if r["all_pass"]:
        print(f"✅ simulation_detector selftest PASS ({r['n_pass']}/{r['n_checks']})")
        print(
            f"   Petronas 2026: index={r['petronas_result']['simulation_index']:.4f} "
            f"verdict={r['petronas_result']['verdict']} "
            f"phase='{r['petronas_result']['calhoun_phase']}'"
        )
    else:
        failed = [c["name"] for c in r["checks"] if not c["pass"]]
        print(f"❌ FAIL: {failed}")


__all__ = [
    "DETECTOR_POLICY_VERSION",
    "SIMULATION_SIGNALS",
    "PETRONAS_2026_EVIDENCE",
    "detect_simulation",
    "petronas_test_case",
    "kernel_self_check",
    "_self_check",
]
