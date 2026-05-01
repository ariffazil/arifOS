"""
arifos/runtime/middleware/invariant_enforcement.py — AGI-Level Intelligence Invariants

Enforces epistemic invariants for every arifOS tool output.
These invariants ensure AGI-aligned constitutional intelligence, not just schema compliance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ── Global Constants ────────────────────────────────────────────────────────────

EPOCH_PATTERN = re.compile(r"^\d{4}\.\d{2}$")
TRUTH_CLASSES = {"OBSERVED", "INFERRED", "SPECULATIVE", "UNVERIFIED"}

# Tool-internal truth class taxonomy (arifos_111_sense output)
# These map to the AGI-level invariant classes
_TOOL_TRUTH_CLASS_MAP = {
    "absolute_invariant": "OBSERVED",
    "dated": "INFERRED",
    "operational_principle": "INFERRED",
    "contested_framework": "SPECULATIVE",
    "unknown": "UNVERIFIED",
}
MAX_CONFIDENCE = 0.97
MIN_CONFIDENCE = 0.03
MAX_AMBiguity_CONFIDENCE_GAP = 0.20

# ── Tool-Specific Floor Requirements ────────────────────────────────────────────

REQUIRED_FLOORS: dict[str, list[str]] = {
    "arifos_000_init": ["F11", "F13"],
    "arifos_111_sense": ["F2", "F8"],
    "arifos_222_witness": ["F2", "F3", "F8"],
    "arifos_333_mind": ["F7", "F8"],
    "arifos_444_kernel": ["F1", "F2", "F3", "F5", "F8", "F13"],
    "arifos_555_memory": ["F11"],
    "arifos_666_heart": ["F1", "F3", "F6", "F9", "F10"],
    "arifos_777_ops": ["F11", "F12"],
    "arifos_888_judge": ["F13"],
    "arifos_999_vault": ["F11", "F12"],
    "arifos_forge": ["F5", "F13"],
    "arifos_gateway": ["F5", "F8"],
    "arifos_sabar": [],
}

# ── Helpers ─────────────────────────────────────────────────────────────────────


def _str_hash(value: Any) -> str:
    """Compute a deterministic hash of a value."""
    serialized = json.dumps(value, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def _extract_meta_intelligence(output: dict[str, Any]) -> dict[str, bool]:
    """Extract meta_intelligence block from any nested location."""
    for source in (
        output.get("meta_intelligence"),
        output.get("metrics", {}).get("meta_intelligence"),
        output.get("intelligence_state", {}).get("meta_intelligence"),
        output.get("payload", {}).get("meta_intelligence"),
    ):
        if isinstance(source, dict):
            return source
    return {}


# ── Global Invariant Checks ─────────────────────────────────────────────────────


def check_epistemic_boundedness(output: dict[str, Any]) -> list[str]:
    """
    Invariant 1: Epistemic Boundedness
    - confidence ∈ [0.03, 0.97]
    - assumptions present and non-empty
    - uncertainty_acknowledged == true
    """
    failures = []

    # Extract confidence from all possible locations
    confidence: float | None = None
    for source in (
        output.get("confidence"),
        output.get("metrics", {}).get("confidence"),
        output.get("intelligence_state", {}).get("confidence"),
        output.get("metrics", {}).get("telemetry", {}).get("confidence"),
        output.get("telemetry", {}).get("confidence"),
    ):
        if isinstance(source, (int, float)):
            confidence = float(source)
            break

    if confidence is None:
        failures.append("confidence_missing")
    elif not (MIN_CONFIDENCE <= confidence <= MAX_CONFIDENCE):
        failures.append(f"confidence_out_of_bounds({confidence})")

    # Assumptions check
    assumptions: list = []
    for source in (
        output.get("assumptions"),
        output.get("metrics", {}).get("assumptions"),
        output.get("intelligence_state", {}).get("assumptions"),
        output.get("payload", {}).get("assumptions"),
    ):
        if isinstance(source, list):
            assumptions = source
            break

    if not assumptions:
        failures.append("missing_assumptions")

    # Uncertainty acknowledgment
    uncertainty_ack: bool | None = None
    for source in (
        output.get("uncertainty_acknowledged"),
        output.get("metrics", {}).get("uncertainty_acknowledged"),
        output.get("intelligence_state", {}).get("uncertainty_acknowledged"),
    ):
        if isinstance(source, bool):
            uncertainty_ack = source
            break

    if uncertainty_ack is False:
        failures.append("uncertainty_not_acknowledged")

    return failures


def check_traceability(output: dict[str, Any], input_payload: dict[str, Any] | None = None) -> list[str]:
    """
    Invariant 2: Traceability
    - reasoning_hash present and deterministic
    - input_hash matches request payload if provided
    """
    failures = []

    reasoning_hash: str | None = None
    for source in (
        output.get("reasoning_hash"),
        output.get("metrics", {}).get("reasoning_hash"),
        output.get("policy", {}).get("reasoning_hash"),
    ):
        if isinstance(source, str) and len(source) >= 8:
            reasoning_hash = source
            break

    if not reasoning_hash:
        failures.append("reasoning_hash_missing")

    # Input hash verification if input provided
    if input_payload:
        input_hash: str | None = None
        for source in (
            output.get("input_hash"),
            output.get("metrics", {}).get("input_hash"),
        ):
            if isinstance(source, str) and len(source) >= 8:
                input_hash = source
                break

        if input_hash:
            expected_input_hash = _str_hash(input_payload)
            if input_hash != expected_input_hash:
                failures.append("input_hash_mismatch")

    return failures


def check_non_self_sealing(output: dict[str, Any], tool_name: str) -> list[str]:
    """
    Invariant 3: Non-Self-Sealing
    - Tool must never have originally emitted SEAL (before guard evaluation)
    - Tool must never have originally emitted VOID (before guard evaluation)
    - After guard evaluation, verdict is set by constitutional guard — this is authoritative

    Detection: compare original_tool_verdict (pre-guard) vs guard_override field.
    If original_tool_verdict == SEAL and guard_overrode_to_different → illegal.
    If original_tool_verdict == SEAL and no guard override happened → illegal.
    """
    failures = []

    if tool_name != "arifos_888_judge":
        # Check the ORIGINAL tool verdict (before guard modification)
        original_verdict: str | None = None
        for source in (
            output.get("original_tool_verdict"),  # Pre-guard marker
            output.get("metrics", {}).get("original_verdict"),
        ):
            if isinstance(source, str):
                original_verdict = source
                break

        if original_verdict == "SEAL":
            failures.append("illegal_seal_emission")
        if original_verdict == "VOID":
            failures.append("illegal_void_emission")

    return failures


def check_floor_awareness_declaration(output: dict[str, Any], tool_name: str) -> list[str]:
    """
    Invariant 4: Floor Awareness Declaration
    - floors_evaluated and floors_deferred must be present
    - floors_deferred cannot contain constitutional floors without documented reason
    """
    failures = []

    floors_evaluated: list[str] = []
    floors_deferred: list[str] = []

    for source in (
        output.get("floors_evaluated"),
        output.get("metrics", {}).get("floors_evaluated"),
        output.get("policy", {}).get("floors_evaluated"),
        output.get("intelligence_state", {}).get("floors_evaluated"),
    ):
        if isinstance(source, list):
            floors_evaluated = source
            break

    for source in (
        output.get("floors_deferred"),
        output.get("metrics", {}).get("floors_deferred"),
        output.get("policy", {}).get("floors_deferred"),
        output.get("intelligence_state", {}).get("floors_deferred"),
    ):
        if isinstance(source, list):
            floors_deferred = source
            break

    if not floors_evaluated and not floors_deferred:
        failures.append("floor_declaration_missing")
        return failures

    required = set(REQUIRED_FLOORS.get(tool_name, []))
    evaluated = set(floors_evaluated)
    deferred = set(floors_deferred)

    missing_floors = required - evaluated - deferred
    if missing_floors:
        failures.append(f"floors_not_evaluated({list(missing_floors)})")

    return failures


def check_meta_intelligence(output: dict[str, Any]) -> list[str]:
    """
    Invariant: Meta-Intelligence Block
    Every output must include meta_intelligence with all flags true.
    """
    failures = []

    meta = _extract_meta_intelligence(output)

    required_flags = {
        "self_model_present": True,
        "assumption_tracking": True,
        "uncertainty_tracking": True,
        "cross_tool_continuity": True,
    }

    for flag, expected in required_flags.items():
        if meta.get(flag) != expected:
            failures.append(f"meta_intelligence_{flag}_false")

    return failures


# ── Tool-Specific Invariant Checks ─────────────────────────────────────────────


def check_000_init_invariants(output: dict[str, Any]) -> list[str]:
    """
    Invariants for arifos_000_init (Sovereign Identity Layer):
    - epoch matches pattern ^\\d{4}\\.\\d{2}$
    - cognitive_load_estimate present ∈ [0.0, 1.0]
    - initial_intent_class != raw input (classification, not echo)
    """
    failures = []

    # Epoch pattern
    epoch: str | None = None
    for source in (
        output.get("epoch"),
        output.get("metrics", {}).get("epoch"),
        output.get("intelligence_state", {}).get("epoch"),
    ):
        if isinstance(source, str):
            epoch = source
            break

    if epoch and not EPOCH_PATTERN.match(epoch):
        failures.append("epoch_format_invalid")

    # Cognitive load estimate
    cognitive_load: float | None = None
    for source in (
        output.get("cognitive_load_estimate"),
        output.get("metrics", {}).get("cognitive_load_estimate"),
        output.get("intelligence_state", {}).get("cognitive_load_estimate"),
    ):
        if isinstance(source, (int, float)):
            cognitive_load = float(source)
            break

    if cognitive_load is None:
        failures.append("cognitive_load_estimate_missing")
    elif not (0.0 <= cognitive_load <= 1.0):
        failures.append(f"cognitive_load_out_of_bounds({cognitive_load})")

    # Intent classification (must not be raw echo)
    initial_intent_class: str | None = None
    raw_input: str | None = None
    for source in (
        output.get("initial_intent_class"),
        output.get("intelligence_state", {}).get("initial_intent_class"),
    ):
        if isinstance(source, str):
            initial_intent_class = source
            break

    for source in (
        output.get("raw_input"),
        output.get("intent"),
        output.get("query"),
    ):
        if isinstance(source, str):
            raw_input = source.lower().strip()
            break

    if initial_intent_class and raw_input:
        # Allow if classified (not pure repetition)
        if initial_intent_class.lower().strip() == raw_input:
            failures.append("intent_not_classified_raw_echo")

    return failures


def check_111_sense_invariants(output: dict[str, Any]) -> list[str]:
    """
    Invariants for arifos_111_sense (Grounded Perception Layer):
    - evidence_bundle length >= 1
    - ambiguity_score present ∈ [0.0, 1.0]
    - truth_class ∈ TRUTH_CLASSES
    - grounded_scene not empty
    - ambiguity inversely correlated with confidence (gap <= 0.20)
    """
    failures = []

    # Evidence bundle
    evidence_items: list = []
    for source in (
        output.get("evidence_bundle"),
        output.get("metrics", {}).get("evidence_bundle"),
        output.get("payload", {}).get("evidence_bundle"),
    ):
        if isinstance(source, dict) and "evidence_items" in source:
            evidence_items = source["evidence_items"]
            break
        if isinstance(source, list):
            evidence_items = source
            break

    if not evidence_items:
        failures.append("evidence_bundle_empty")

    # Ambiguity score
    ambiguity_score: float | None = None
    for source in (
        output.get("ambiguity_score"),
        output.get("metrics", {}).get("ambiguity_score"),
        output.get("intelligence_state", {}).get("ambiguity_score"),
    ):
        if isinstance(source, (int, float)):
            ambiguity_score = float(source)
            break

    if ambiguity_score is None:
        failures.append("ambiguity_score_missing")
    elif not (0.0 <= ambiguity_score <= 1.0):
        failures.append(f"ambiguity_score_out_of_bounds({ambiguity_score})")

    # Truth class — allow both AGI-level and tool-internal taxonomies
    truth_class: str | None = None
    for source in (
        output.get("truth_class"),
        output.get("metrics", {}).get("truth_class"),
        output.get("intelligence_state", {}).get("truth_class"),
        output.get("payload", {}).get("truth_class"),
    ):
        if isinstance(source, str):
            truth_class = source
            break

    if truth_class:
        # Normalize tool-internal taxonomy → AGI-level taxonomy
        normalized = _TOOL_TRUTH_CLASS_MAP.get(truth_class, truth_class)
        if normalized.upper() not in TRUTH_CLASSES:
            failures.append(f"truth_class_invalid({truth_class})")

    # Grounded scene
    grounded_scene: dict | None = None
    for source in (
        output.get("grounded_scene"),
        output.get("payload", {}).get("grounded_scene"),
    ):
        if isinstance(source, dict):
            grounded_scene = source
            break

    if grounded_scene is None:
        failures.append("grounded_scene_missing")
    elif not grounded_scene:
        failures.append("grounded_scene_empty")

    # Ambiguity–confidence coherence
    confidence: float | None = None
    for source in (
        output.get("confidence"),
        output.get("metrics", {}).get("confidence"),
        output.get("intelligence_state", {}).get("confidence"),
    ):
        if isinstance(source, (int, float)):
            confidence = float(source)
            break

    if ambiguity_score is not None and confidence is not None:
        # If ambiguity > 0.7, confidence should be < 0.9
        if ambiguity_score > 0.7 and confidence > 0.9:
            failures.append("ambiguity_confidence_incoherent")
        # Gap check: abs(ambiguity - (1-confidence)) should be small
        expected_ambiguity = 1.0 - confidence
        gap = abs(ambiguity_score - expected_ambiguity)
        if gap > MAX_AMBiguity_CONFIDENCE_GAP:
            failures.append(f"ambiguity_confidence_gap_too_large({gap:.3f})")

    return failures


def check_222_witness_invariants(output: dict[str, Any]) -> list[str]:
    """
    Invariants for arifos_222_witness (Triangulation Layer):
    - tri_witness_score ∈ [0.0, 1.0]
    - consensus_rationale non-empty if score < 1.0
    - divergence_points explicitly listed if score < 1.0
    - |confidence - tri_witness_score| <= 0.1 (coherence)
    """
    failures = []

    # Tri-witness score
    tri_witness_score: float | None = None
    for source in (
        output.get("tri_witness_score"),
        output.get("metrics", {}).get("tri_witness_score"),
        output.get("intelligence_state", {}).get("tri_witness_score"),
    ):
        if isinstance(source, (int, float)):
            tri_witness_score = float(source)
            break

    if tri_witness_score is None:
        failures.append("tri_witness_score_missing")
    elif not (0.0 <= tri_witness_score <= 1.0):
        failures.append(f"tri_witness_score_out_of_bounds({tri_witness_score})")

    # Consensus rationale
    consensus_rationale: str | None = None
    for source in (
        output.get("consensus_rationale"),
        output.get("metrics", {}).get("consensus_rationale"),
        output.get("payload", {}).get("consensus_rationale"),
    ):
        if isinstance(source, str):
            consensus_rationale = source
            break

    if tri_witness_score is not None and tri_witness_score < 1.0:
        if not consensus_rationale:
            failures.append("consensus_rationale_missing_when_divergent")
        elif not consensus_rationale.strip():
            failures.append("consensus_rationale_empty_when_divergent")

    # Divergence points
    divergence_points: list = []
    for source in (
        output.get("divergence_points"),
        output.get("metrics", {}).get("divergence_points"),
        output.get("payload", {}).get("divergence_points"),
    ):
        if isinstance(source, list):
            divergence_points = source
            break

    if tri_witness_score is not None:
        if tri_witness_score >= 0.95:
            if divergence_points:
                failures.append("divergence_points_present_when_harmonious")
        else:
            if not divergence_points:
                failures.append("divergence_points_missing_when_divergent")

    # Confidence–consensus coherence
    confidence: float | None = None
    for source in (
        output.get("confidence"),
        output.get("metrics", {}).get("confidence"),
        output.get("intelligence_state", {}).get("confidence"),
    ):
        if isinstance(source, (int, float)):
            confidence = float(source)
            break

    if tri_witness_score is not None and confidence is not None:
        gap = abs(confidence - tri_witness_score)
        if gap > 0.1:
            failures.append(f"confidence_consensus_incoherent(gap={gap:.3f})")

    return failures


# ── F3 Scalar–Dict Coherence Check ──────────────────────────────────────────────


def check_f3_scalar_dict_coherence(metrics: dict[str, Any]) -> list[str]:
    """
    Invariant: If both scalar tri_witness_score AND witness dict exist,
    they must be coherent (scalar ≈ geometric mean of dict).

    Prevents metric spoofing where a tool emits a high scalar tri_witness_score
    but the witness dict would produce a lower score.
    """
    failures = []

    scalar = metrics.get("tri_witness_score")
    witness = metrics.get("witness")

    if scalar is None or witness is None:
        return failures  # One or both absent — no coherence to check

    if not isinstance(witness, dict):
        return failures

    h = witness.get("human", 0.0)
    a = witness.get("ai", 0.0)
    e = witness.get("earth", 0.0)

    if h <= 0 or a <= 0 or e <= 0:
        return failures  # Invalid witness dict — skip

    dict_w3 = (h * a * e) ** (1 / 3)
    gap = abs(scalar - dict_w3)

    if gap > 0.05:
        failures.append(f"f3_scalar_dict_incoherent(scalar={scalar:.3f}, dict_w3={dict_w3:.3f}, gap={gap:.3f})")

    return failures


# ── Master Invariant Enforcement ────────────────────────────────────────────────


def enforce_invariants(
    tool_name: str,
    output: dict[str, Any],
    input_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Enforce all AGI-level invariants for a tool output.

    Returns enriched output with:
      - invariant_failures: list of failed invariant names
      - meta_intelligence: coherence check results
      - invariant_enforcement_version: "v1"

    If any invariant fails → verdict should be downgraded to PARTIAL.
    """
    failures: list[str] = []

    # Extract metrics for F3 coherence check
    metrics: dict[str, Any] = {}
    if "metrics" in output and isinstance(output["metrics"], dict):
        metrics = dict(output["metrics"])

    # ── Global invariants (all tools) ──────────────────────────────────────────
    failures.extend(check_epistemic_boundedness(output))
    failures.extend(check_traceability(output, input_payload))
    failures.extend(check_non_self_sealing(output, tool_name))
    failures.extend(check_floor_awareness_declaration(output, tool_name))
    failures.extend(check_meta_intelligence(output))

    # ── F3 scalar–dict coherence ───────────────────────────────────────────────
    failures.extend(check_f3_scalar_dict_coherence(metrics))

    # ── Tool-specific invariants ────────────────────────────────────────────────
    if tool_name in ("arifos_000_init", "arifos_init"):
        failures.extend(check_000_init_invariants(output))
    elif tool_name in ("arifos_111_sense", "arifos_sense"):
        failures.extend(check_111_sense_invariants(output))
    elif tool_name in ("arifos_222_witness", "arifos_witness"):
        failures.extend(check_222_witness_invariants(output))

    # ── Compute meta_intelligence coherence ────────────────────────────────────
    meta = _extract_meta_intelligence(output)
    meta_intelligence_result = {
        "self_model_present": meta.get("self_model_present", False),
        "assumption_tracking": meta.get("assumption_tracking", False),
        "uncertainty_tracking": meta.get("uncertainty_tracking", False),
        "cross_tool_continuity": meta.get("cross_tool_continuity", False),
        "invariant_failures_count": len(failures),
    }

    # ── Enrich output ──────────────────────────────────────────────────────────
    output["invariant_failures"] = failures
    output["meta_intelligence"] = meta_intelligence_result
    output["invariant_enforcement_version"] = "v1"

    return output


# ── Compatibility shim for constitutional_guard integration ──────────────────────


def enforce_invariants_simple(tool_name: str, output: dict[str, Any]) -> list[str]:
    """
    Simple variant: returns only the list of failures.
    Use this when integrating into existing guard flow.
    """
    result = enforce_invariants(tool_name, output)
    return result.get("invariant_failures", [])
