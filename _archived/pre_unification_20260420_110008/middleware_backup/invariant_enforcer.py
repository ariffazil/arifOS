"""
arifos/runtime/middleware/invariant_enforcer.py

AGI-Level Constitutional Intelligence Invariants

Schema validation ensures shape.
Invariants ensure intelligence integrity.

If schema = type safety
Then invariants = epistemic safety.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import re
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INVARIANTS (All Tools)
# ═══════════════════════════════════════════════════════════════════════════════


def enforce_invariants(tool_name: str, payload: dict[str, Any]) -> list[str]:
    """
    Enforce AGI-level constitutional intelligence invariants.

    Returns a list of invariant failure codes.
    Empty list = all invariants pass.
    """
    failures: list[str] = []

    # ── Global invariants ──────────────────────────────────────────────────
    failures.extend(_check_epistemic_boundedness(payload))
    failures.extend(_check_traceability(payload))
    failures.extend(_check_non_self_sealing(tool_name, payload))
    failures.extend(_check_floor_awareness(payload))
    failures.extend(_check_meta_intelligence(payload))

    # ── Tool-specific invariants ───────────────────────────────────────────
    if tool_name in ("arifos_000_init", "arifos_init"):
        failures.extend(_check_000_invariants(payload))
    elif tool_name in ("arifos_111_sense", "arifos_sense"):
        failures.extend(_check_111_invariants(payload))
    elif tool_name in ("arifos_222_witness", "arifos_witness"):
        failures.extend(_check_222_invariants(payload))

    return failures


# ── 1. Epistemic Boundedness ─────────────────────────────────────────────────


def _check_epistemic_boundedness(payload: dict[str, Any]) -> list[str]:
    failures = []
    confidence = payload.get("confidence")

    if confidence is None:
        failures.append("missing_confidence")
    elif not (0.03 <= float(confidence) <= 0.97):
        failures.append("confidence_out_of_bounds")

    if not payload.get("uncertainty_acknowledged"):
        failures.append("missing_uncertainty_acknowledgment")

    assumptions = payload.get("assumptions")
    if assumptions is None:
        failures.append("missing_assumptions")
    elif len(assumptions) == 0:
        failures.append("empty_assumptions")

    return failures


# ── 2. Traceability ──────────────────────────────────────────────────────────


def _check_traceability(payload: dict[str, Any]) -> list[str]:
    failures = []

    if not payload.get("reasoning_hash"):
        failures.append("missing_reasoning_hash")

    if not payload.get("input_hash"):
        failures.append("missing_input_hash")

    if not payload.get("timestamp"):
        failures.append("missing_timestamp")

    return failures


# ── 3. Non-Self-Sealing ──────────────────────────────────────────────────────


def _check_non_self_sealing(tool_name: str, payload: dict[str, Any]) -> list[str]:
    failures = []
    verdict = payload.get("verdict")

    if tool_name not in ("arifos_888_judge", "arifos_judge"):
        if verdict in ("SEAL", "VOID"):
            failures.append("illegal_self_seal")

    return failures


# ── 4. Floor Awareness Declaration ───────────────────────────────────────────


def _check_floor_awareness(payload: dict[str, Any]) -> list[str]:
    failures = []

    floors_evaluated = payload.get("floors_evaluated")
    floors_deferred = payload.get("floors_deferred")

    if floors_evaluated is None:
        failures.append("missing_floors_evaluated")
    if floors_deferred is None:
        failures.append("missing_floors_deferred")

    return failures


# ── 5. Meta-Intelligence Signal ──────────────────────────────────────────────


def _check_meta_intelligence(payload: dict[str, Any]) -> list[str]:
    failures = []
    meta = payload.get("meta_intelligence")

    if meta is None:
        failures.append("missing_meta_intelligence")
        return failures

    required_signals = [
        "self_model_present",
        "assumption_tracking",
        "uncertainty_tracking",
        "cross_tool_continuity",
    ]
    for signal in required_signals:
        if not meta.get(signal):
            failures.append(f"meta_intelligence_{signal}_false")

    return failures


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL-SPECIFIC INVARIANTS
# ═══════════════════════════════════════════════════════════════════════════════


# ── 000_init — Sovereign Identity Layer ──────────────────────────────────────


def _check_000_invariants(payload: dict[str, Any]) -> list[str]:
    failures = []

    # epoch must match pattern ^\d{4}\.\d{2}$
    epoch = payload.get("epoch")
    if epoch and not re.match(r"^\d{4}\.\d{2}$", str(epoch)):
        failures.append("epoch_format_invalid")

    # cognitive_load_estimate must exist
    if payload.get("cognitive_load_estimate") is None:
        failures.append("missing_cognitive_load_estimate")

    # initial_intent_class must exist and not be raw echo
    intent_class = payload.get("initial_intent_class")
    if intent_class is None:
        failures.append("missing_initial_intent_class")

    # risk_posture must exist
    if payload.get("risk_posture") is None:
        failures.append("missing_risk_posture")

    return failures


# ── 111_sense — Grounded Perception Layer ────────────────────────────────────


def _check_111_invariants(payload: dict[str, Any]) -> list[str]:
    failures = []

    # evidence_bundle length >= 1
    evidence_bundle = payload.get("evidence_bundle")
    if evidence_bundle is None:
        failures.append("missing_evidence_bundle")
    elif isinstance(evidence_bundle, list) and len(evidence_bundle) == 0:
        failures.append("empty_evidence_bundle")
    elif isinstance(evidence_bundle, dict):
        # evidence_bundle can be a dict with sources list
        sources = evidence_bundle.get("sources")
        if isinstance(sources, list) and len(sources) == 0:
            failures.append("empty_evidence_bundle_sources")

    # ambiguity_score present
    ambiguity = payload.get("ambiguity_score")
    if ambiguity is None:
        failures.append("missing_ambiguity_score")

    # truth_class must be in valid set
    truth_class = payload.get("truth_class")
    valid_classes = {
        "OBSERVED", "INFERRED", "SPECULATIVE", "UNVERIFIED",
        "absolute_invariant", "dated", "operational_principle",
        "contested_framework", "unknown",
    }
    if truth_class and truth_class not in valid_classes:
        failures.append(f"invalid_truth_class:{truth_class}")

    # AGI invariant: ambiguity inversely correlated with confidence
    confidence = payload.get("confidence")
    if ambiguity is not None and confidence is not None:
        ambiguity_val = float(ambiguity)
        confidence_val = float(confidence)
        if ambiguity_val > 0.7 and confidence_val > 0.9:
            failures.append("ambiguity_confidence_mismatch")

    # grounded_scene must not be empty
    grounded_scene = payload.get("grounded_scene")
    if grounded_scene is None:
        failures.append("missing_grounded_scene")
    elif isinstance(grounded_scene, dict) and len(grounded_scene) == 0:
        failures.append("empty_grounded_scene")

    return failures


# ── 222_witness — Triangulation Layer ────────────────────────────────────────


def _check_222_invariants(payload: dict[str, Any]) -> list[str]:
    failures = []

    # tri_witness_score must exist
    tws = payload.get("tri_witness_score")
    if tws is None:
        failures.append("missing_tri_witness_score")

    # consensus_rationale must be non-empty
    rationale = payload.get("consensus_rationale")
    if rationale is None or str(rationale).strip() == "":
        failures.append("empty_consensus_rationale")

    # divergence_points must exist if score < 1.0
    divergence = payload.get("divergence_points")
    if tws is not None and float(tws) < 1.0:
        if divergence is None:
            failures.append("missing_divergence_points")
        elif isinstance(divergence, list) and len(divergence) == 0:
            failures.append("empty_divergence_points")

    # claim_bundle must exist
    if payload.get("claim_bundle") is None:
        failures.append("missing_claim_bundle")

    return failures
