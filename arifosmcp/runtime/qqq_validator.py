"""
arifosmcp/runtime/qqq_validator.py
════════════════════════════════════
Gate 5b: QQQ Recommendation Discipline

Validates recommendation envelopes against the QQQ Doctrine v1.0.
Operational expression of F2 TRUTH + F4 CLARITY + F7 HUMILITY.

Gate 5 structure:
  Gate 5a: Floor Compliance (F1-F13) — existing
  Gate 5b: QQQ Discipline (this module) — new

QQQ triggers ONLY on: RECOMMENDATION, DECISION, VERDICT intent classes.
QQQ does NOT trigger on: OBSERVATION, STATUS_REPORT, QUESTION.

INADMISSIBLE label, never suppression. Recommendations always reach Arif.
Weak ones carry a scar. The scar teaches.

Doctrine: /root/AAA/governance/QQQ_RECOMMENDATION_PROTOCOL.md
FLOOR BIND: F2 TRUTH, F4 CLARITY, F7 HUMILITY, F11 AUDITABILITY, F13 SOVEREIGN

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger("arifosmcp.qqq_validator")


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT — QQQ compliance state
# ═══════════════════════════════════════════════════════════════════════════════


class QQQVerdict(StrEnum):
    """Verdict from QQQ validation.

    COMPLETE          — All three Q layers present and valid.
    INADMISSIBLE_Q1   — Option space incomplete.
    INADMISSIBLE_Q2   — Quantitative metrics missing.
    INADMISSIBLE_Q3   — Quantum analysis missing.
    NOT_REQUIRED      — Intent class does not require QQQ.
    ENVELOPE_MISSING  — QQQ required but no envelope provided.
    """

    COMPLETE = "COMPLETE"
    INADMISSIBLE_Q1 = "INADMISSIBLE-Q1"
    INADMISSIBLE_Q2 = "INADMISSIBLE-Q2"
    INADMISSIBLE_Q3 = "INADMISSIBLE-Q3"
    NOT_REQUIRED = "NOT_REQUIRED"
    ENVELOPE_MISSING = "ENVELOPE_MISSING"


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT — structured validation output
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class QQQCheck:
    """Result of QQQ envelope validation."""

    verdict: QQQVerdict
    qqq_required: bool = False
    reasons: list[str] = field(default_factory=list)
    paths_count: int = 0
    has_null: bool = False
    has_inverse: bool = False
    quantum_complete: bool = False
    metrics_complete: bool = False
    recommended_path_valid: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# INTENT GATING — when does QQQ trigger?
# ═══════════════════════════════════════════════════════════════════════════════

# Import canonical enums (single source of truth)
try:
    from arifosmcp.schemas.federation_enums import (
        IntentClass,
        QQQCompliance,
    )
    from arifosmcp.schemas.federation_enums import (
        requires_qqq as _requires_qqq,
    )
except ImportError:
    # Fallback if federation_enums not available
    class IntentClass:  # type: ignore[no-redef]
        OBSERVATION = "OBSERVATION"
        STATUS_REPORT = "STATUS_REPORT"
        QUESTION = "QUESTION"
        RECOMMENDATION = "RECOMMENDATION"
        DECISION = "DECISION"
        VERDICT = "VERDICT"

    def _requires_qqq(intent: str) -> bool:  # type: ignore[misc]
        return intent in {"RECOMMENDATION", "DECISION", "VERDICT"}


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION — the three Q layers
# ═══════════════════════════════════════════════════════════════════════════════


def _validate_q1(paths: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Q1 QUALITATIVE: option space mapping.

    Rules:
    - Minimum 5 paths
    - NULL category must be present (do-nothing option)
    - INVERSE category must be present (do-opposite option)
    """
    reasons: list[str] = []

    if len(paths) < 5:
        reasons.append(f"Q1: Only {len(paths)} paths, need ≥5")

    categories = {p.get("category", "").upper() for p in paths}

    if "NULL" not in categories:
        reasons.append("Q1: NULL path missing (do-nothing option)")

    if "INVERSE" not in categories:
        reasons.append("Q1: INVERSE path missing (do-opposite option)")

    return len(reasons) == 0, reasons


def _validate_q2(paths: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Q2 QUANTITATIVE: measured trade-offs.

    Rules:
    - Every path must have: blast_radius, reversibility, confidence, prior_art
    - Confidence must be 0.0-1.0
    - blast_radius must be 0-5
    - reversibility must be 0-5
    """
    reasons: list[str] = []
    required_fields = {"blast_radius", "reversibility", "confidence", "prior_art"}

    for p in paths:
        path_id = p.get("path_id", "?")
        missing = required_fields - set(p.keys())
        if missing:
            reasons.append(f"Q2: Path '{path_id}' missing fields: {missing}")
            continue

        conf = p.get("confidence", -1)
        if not (0.0 <= conf <= 1.0):
            reasons.append(f"Q2: Path '{path_id}' confidence={conf} outside [0.0, 1.0]")

        br = p.get("blast_radius", -1)
        if not (0 <= br <= 5):
            reasons.append(f"Q2: Path '{path_id}' blast_radius={br} outside [0, 5]")

        rev = p.get("reversibility", -1)
        if not (0 <= rev <= 5):
            reasons.append(f"Q2: Path '{path_id}' reversibility={rev} outside [0, 5]")

    return len(reasons) == 0, reasons


def _validate_q3(quantum: dict[str, Any] | None) -> tuple[bool, list[str]]:
    """Q3 QUANTUM: second-order effects.

    Rules:
    - All four quantum questions must be answered:
      precedent_effect, interference_effect, superposition_effect, observer_effect
    - Answers must be non-empty strings
    """
    reasons: list[str] = []

    if not quantum:
        reasons.append("Q3: quantum_analysis missing entirely")
        return False, reasons

    required = [
        "precedent_effect",
        "interference_effect",
        "superposition_effect",
        "observer_effect",
    ]
    for field_name in required:
        value = quantum.get(field_name, "")
        if not value or not isinstance(value, str) or len(value.strip()) < 5:
            reasons.append(f"Q3: {field_name} missing or too short")

    return len(reasons) == 0, reasons


def _validate_recommended_path(
    paths: list[dict[str, Any]], recommended_path_id: str
) -> tuple[bool, list[str]]:
    """Verdict: recommended_path_id must reference a valid path."""
    reasons: list[str] = []

    path_ids = {p.get("path_id") for p in paths}
    if recommended_path_id not in path_ids:
        reasons.append(
            f"Verdict: recommended_path_id '{recommended_path_id}' not in path_ids: {path_ids}"
        )

    return len(reasons) == 0, reasons


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN VALIDATOR — entry point
# ═══════════════════════════════════════════════════════════════════════════════


def validate_qqq(
    envelope: dict[str, Any] | None,
    intent_class: str = "RECOMMENDATION",
) -> QQQCheck:
    """Validate a QQQ recommendation envelope.

    Args:
        envelope: The RecommendationEnvelope dict, or None if not provided.
        intent_class: The intent class of the agent output.

    Returns:
        QQQCheck with verdict, reasons, and diagnostic fields.

    The validator is fail-honest, not fail-hidden:
    - Missing envelope → ENVELOPE_MISSING (not suppression)
    - Incomplete envelope → INADMISSIBLE-Q* (with specific reasons)
    - Complete envelope → COMPLETE
    - Non-QQQ intent → NOT_REQUIRED
    """
    # ── Intent gate ────────────────────────────────────────────────────────
    if not _requires_qqq(intent_class):
        return QQQCheck(
            verdict=QQQVerdict.NOT_REQUIRED,
            qqq_required=False,
            metadata={"intent_class": intent_class},
        )

    # ── Envelope presence ──────────────────────────────────────────────────
    if not envelope:
        return QQQCheck(
            verdict=QQQVerdict.ENVELOPE_MISSING,
            qqq_required=True,
            reasons=[f"QQQ required for intent '{intent_class}' but no envelope provided"],
            metadata={"intent_class": intent_class},
        )

    # ── Extract envelope fields ────────────────────────────────────────────
    paths = envelope.get("paths", [])
    quantum = envelope.get("quantum")
    recommended_path_id = envelope.get("recommended_path_id", "")

    check = QQQCheck(
        verdict=QQQVerdict.COMPLETE,  # optimistic, will downgrade
        qqq_required=True,
        paths_count=len(paths),
        has_null=any(p.get("category", "").upper() == "NULL" for p in paths),
        has_inverse=any(p.get("category", "").upper() == "INVERSE" for p in paths),
        metadata={"intent_class": intent_class},
    )

    all_reasons: list[str] = []

    # ── Q1: Qualitative ────────────────────────────────────────────────────
    q1_ok, q1_reasons = _validate_q1(paths)
    all_reasons.extend(q1_reasons)
    if not q1_ok:
        check.verdict = QQQVerdict.INADMISSIBLE_Q1

    # ── Q2: Quantitative ───────────────────────────────────────────────────
    q2_ok, q2_reasons = _validate_q2(paths)
    all_reasons.extend(q2_reasons)
    check.metrics_complete = q2_ok
    if not q2_ok and check.verdict == QQQVerdict.COMPLETE:
        check.verdict = QQQVerdict.INADMISSIBLE_Q2

    # ── Q3: Quantum ────────────────────────────────────────────────────────
    q3_ok, q3_reasons = _validate_q3(quantum)
    all_reasons.extend(q3_reasons)
    check.quantum_complete = q3_ok
    if not q3_ok and check.verdict == QQQVerdict.COMPLETE:
        check.verdict = QQQVerdict.INADMISSIBLE_Q3

    # ── Verdict: recommended_path_id ───────────────────────────────────────
    path_ok, path_reasons = _validate_recommended_path(paths, recommended_path_id)
    all_reasons.extend(path_reasons)
    check.recommended_path_valid = path_ok
    if not path_ok and check.verdict == QQQVerdict.COMPLETE:
        check.verdict = QQQVerdict.INADMISSIBLE_Q1  # path reference is Q1 concern

    # ── Finalize ───────────────────────────────────────────────────────────
    check.reasons = all_reasons

    if check.verdict == QQQVerdict.COMPLETE:
        logger.info(
            "QQQ COMPLETE: %d paths, recommended=%s",
            len(paths),
            recommended_path_id,
        )
    else:
        logger.warning(
            "QQQ %s: %s",
            check.verdict.value,
            "; ".join(all_reasons),
        )

    return check


# ═══════════════════════════════════════════════════════════════════════════════
# GATE — integration point for governance pipeline
# ═══════════════════════════════════════════════════════════════════════════════


def gate_qqq(
    envelope: dict[str, Any] | None,
    intent_class: str = "RECOMMENDATION",
) -> QQQCheck:
    """Gate 5b: QQQ discipline check.

    This is the integration point for the governance pipeline.
    Call after Gate 5a (Floor Compliance) and before Gate 6 (Drift Detection).

    Returns QQQCheck with verdict. The caller decides what to do:
    - COMPLETE → proceed
    - INADMISSIBLE-Q* → label and surface (never suppress)
    - NOT_REQUIRED → proceed (intent doesn't need QQQ)
    - ENVELOPE_MISSING → label and surface

    The gate does NOT block. It labels. The sovereign decides.
    """
    check = validate_qqq(envelope, intent_class)

    # Enrich with compliance mapping for downstream consumers
    compliance_map = {
        QQQVerdict.COMPLETE: "COMPLETE",
        QQQVerdict.INADMISSIBLE_Q1: "INADMISSIBLE-Q1",
        QQQVerdict.INADMISSIBLE_Q2: "INADMISSIBLE-Q2",
        QQQVerdict.INADMISSIBLE_Q3: "INADMISSIBLE-Q3",
        QQQVerdict.NOT_REQUIRED: "NOT_REQUIRED",
        QQQVerdict.ENVELOPE_MISSING: "INADMISSIBLE-Q1",
    }
    check.metadata["qqq_compliance"] = compliance_map.get(check.verdict, "INADMISSIBLE-Q1")

    return check
