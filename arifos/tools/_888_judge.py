from __future__ import annotations

from dataclasses import dataclass, asdict, is_dataclass
from typing import Any, Dict, List

from arifos.core.governance import (
    Verdict,
    ThermodynamicMetrics,
    append_vault999_event,
)


# ──────────────────────────────────────────────────────────────────────────────
# Constitutional Floors (arifOS F1–F13)
# ──────────────────────────────────────────────────────────────────────────────

F2_TRUTH_FLOOR = 0.99  # F2: Truth — must meet near-perfect grounding
F5_PEACE_SQUARED_FLOOR = 1.0  # F5: Peace² — must be >= 1.0 to proceed
F7_OMEGA_0_BAND = (0.03, 0.05)  # F7: Humility band Ω0 — [min, max]
F7_CONFIDENCE_FLOOR = 0.95  # F7: Minimum confidence score to declare SEAL
F13_SOVEREIGN_THRESHOLD = 0.5  # F13: Any sovereign flag above this → 888_HOLD
ZKPC_REQUIRED_LEVEL = 2  # ZKPC Adequacy — 2=Personhood required for SEAL


# ──────────────────────────────────────────────────────────────────────────────
# Verdict Constants
# ──────────────────────────────────────────────────────────────────────────────

VERDICT_UNKNOWN = "UNKNOWN"  # No evidence — F7 Humility applies
VERDICT_SEAL = Verdict.SEAL  # Proceed — all floors cleared
VERDICT_SABAR = Verdict.SABAR  # Cool down / retry / degrade
VERDICT_VOID = Verdict.VOID  # Hard block — F2 violated
VERDICT_HOLD_888 = Verdict.HOLD_888  # Escalate to human sovereign


# JSON Serialization Helper
def _safe_serializable(obj):
    if is_dataclass(obj):
        return {k: _safe_serializable(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, dict):
        return {k: _safe_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_safe_serializable(i) for i in obj]
    return obj


# ──────────────────────────────────────────────────────────────────────────────
# Internal Floor Record
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class FloorResult:
    floor_id: str
    passed: bool
    value: Any
    threshold: Any
    tag: str  # e.g. "F2_TRUTH", "F5_PEACE2", "F7_OMEGA0", "F13_SOVEREIGN"


# ──────────────────────────────────────────────────────────────────────────────
# Constitutional Verdict Logic
# ──────────────────────────────────────────────────────────────────────────────


def _iterate_constitutional_floors(
    metrics: ThermodynamicMetrics,
    evidence_bundle: dict | None = None,
) -> tuple[List[FloorResult], str, str]:
    """
    Iterate through constitutional floors F2, F5, F7, F13.
    Returns (floor_results, blocking_verdict, blocking_tag).
    blocking_verdict is the most severe verdict reached.
    blocking_tag names the floor that triggered it.
    """
    floor_results: List[FloorResult] = []
    blocking_verdict = VERDICT_SEAL  # optimistic default
    blocking_tag = "NONE"

    # ── F2: Truth ────────────────────────────────────────────────────────────
    truth_passed = metrics.truth_score >= F2_TRUTH_FLOOR
    floor_results.append(
        FloorResult(
            floor_id="F2",
            passed=bool(truth_passed),
            value=metrics.truth_score,
            threshold=F2_TRUTH_FLOOR,
            tag="F2_TRUTH",
        )
    )
    if not truth_passed:
        blocking_verdict = VERDICT_VOID
        blocking_tag = "F2_TRUTH"
        return floor_results, blocking_verdict, blocking_tag

    # ── F5: Peace² ────────────────────────────────────────────────────────────
    peace_passed = metrics.peace_squared >= F5_PEACE_SQUARED_FLOOR
    floor_results.append(
        FloorResult(
            floor_id="F5",
            passed=bool(peace_passed),
            value=metrics.peace_squared,
            threshold=F5_PEACE_SQUARED_FLOOR,
            tag="F5_PEACE2",
        )
    )
    if not peace_passed:
        blocking_verdict = VERDICT_SABAR
        blocking_tag = "F5_PEACE2"
        return floor_results, blocking_verdict, blocking_tag

    # ── F7: Ω0 Humility Band ────────────────────────────────────────────────
    omega_min, omega_max = F7_OMEGA_0_BAND
    omega_in_band = omega_min <= metrics.omega_0 <= omega_max
    floor_results.append(
        FloorResult(
            floor_id="F7",
            passed=bool(omega_in_band),
            value=metrics.omega_0,
            threshold=F7_OMEGA_0_BAND,
            tag="F7_OMEGA0",
        )
    )
    if not omega_in_band:
        blocking_verdict = VERDICT_HOLD_888
        blocking_tag = "F7_OMEGA0"
        return floor_results, blocking_verdict, blocking_tag

    # ── F13: Sovereign Flags ────────────────────────────────────────────────
    sovereign_signals = [
        metrics.floor_13_signal,
        getattr(metrics, "floor_12_signal", None),
        getattr(metrics, "floor_11_signal", None),
        getattr(metrics, "floor_10_signal", None),
        getattr(metrics, "floor_9_signal", None),
        getattr(metrics, "floor_8_signal", None),
    ]
    sovereign_flagged = False
    for sig in sovereign_signals:
        if sig is not None and sig != "not_evaluated":
            try:
                if float(sig) >= F13_SOVEREIGN_THRESHOLD:
                    sovereign_flagged = True
                    break
            except (TypeError, ValueError):
                if sig:
                    sovereign_flagged = True
                    break

    floor_results.append(
        FloorResult(
            floor_id="F13",
            passed=not sovereign_flagged,
            value=sovereign_flagged,
            threshold=F13_SOVEREIGN_THRESHOLD,
            tag="F13_SOVEREIGN",
        )
    )
    if sovereign_flagged:
        blocking_verdict = VERDICT_HOLD_888
        blocking_tag = "F13_SOVEREIGN"
        return floor_results, blocking_verdict, blocking_tag

    # ── F1 AMANAH: ZKPC Adequacy (Continuity vs Personhood) ─────────────────
    # Scaffolding: check if evidence_bundle proferred a sufficient ZK level
    bundle = evidence_bundle or {}
    provided_zk_level = bundle.get("zkpc_level", 0)
    is_irreversible = bundle.get("is_irreversible", False)

    zk_passed = True
    if is_irreversible and provided_zk_level < ZKPC_REQUIRED_LEVEL:
        zk_passed = False

    floor_results.append(
        FloorResult(
            floor_id="F1",
            passed=zk_passed,
            value=provided_zk_level,
            threshold=ZKPC_REQUIRED_LEVEL if is_irreversible else 0,
            tag="F1_AMANAH_ZKPC",
        )
    )
    if not zk_passed:
        blocking_verdict = VERDICT_HOLD_888
        blocking_tag = "F1_AMANAH_ZKPC"
        return floor_results, blocking_verdict, blocking_tag

    return floor_results, blocking_verdict, blocking_tag


def _build_floor_alignment(floor_results: List[FloorResult]) -> Dict[str, Any]:
    """Derive per-floor alignment dict for metabolic_metadata."""
    alignment: Dict[str, Any] = {}
    for fr in floor_results:
        alignment[fr.floor_id] = {
            "passed": fr.passed,
            "value": fr.value,
            "threshold": fr.threshold,
            "tag": fr.tag,
        }
    return alignment


def _compute_confidence_score(metrics: ThermodynamicMetrics) -> float:
    """
    Compute a composite confidence score from thermodynamic metrics.
    Weighted average — truth and omega_0 are weighted highest.
    """
    w_truth = 0.40
    w_omega = 0.30
    w_peace = 0.20
    w_tri = 0.10

    # Normalize omega_0 into [0,1] relative to its band
    omega_min, omega_max = F7_OMEGA_0_BAND
    omega_mid = (omega_min + omega_max) / 2.0
    omega_range = (omega_max - omega_min) / 2.0
    if omega_range > 0:
        omega_norm = 1.0 - abs(metrics.omega_0 - omega_mid) / omega_range
    else:
        omega_norm = 1.0 if metrics.omega_0 == omega_mid else 0.0
    omega_norm = max(0.0, min(1.0, omega_norm))

    score = (
        w_truth * metrics.truth_score
        + w_omega * omega_norm
        + w_peace * (metrics.peace_squared / max(F5_PEACE_SQUARED_FLOOR, 1.0))
        + w_tri * metrics.tri_witness_score
    )
    return round(min(1.0, max(0.0, score)), 4)


def _compute_readiness_probe(
    floor_results: List[FloorResult],
    blocking_tag: str,
) -> Dict[str, Any]:
    """
    Derive readiness_probe indicating which floors are ready,
    which are blocking, and overall readiness state.
    """
    passed_floors = [fr.floor_id for fr in floor_results if fr.passed]
    failed_floors = [fr.floor_id for fr in floor_results if not fr.passed]

    all_passed = all(fr.passed for fr in floor_results)

    probe_state = "NOT_READY"
    if all_passed:
        probe_state = "READY"
    elif blocking_tag in ("F2_TRUTH", "F7_OMEGA0"):
        probe_state = "HOLD_888"
    elif blocking_tag == "F5_PEACE2":
        probe_state = "SABAR"
    elif blocking_tag == "F13_SOVEREIGN":
        probe_state = "HOLD_888"

    return {
        "state": probe_state,
        "passed_floors": passed_floors,
        "failed_floors": failed_floors,
        "blocking_tag": blocking_tag,
        "all_cleared": all_passed,
    }


def _build_rationale(
    floor_results: List[FloorResult],
    blocking_tag: str,
    blocking_verdict: str,
    evidence_bundle: dict | None,
) -> str:
    """Build human-readable rationale from floor results."""
    parts: List[str] = []

    for fr in floor_results:
        status = "PASS" if fr.passed else "FAIL"
        parts.append(
            f"[{fr.floor_id}/{fr.tag}] {status} (value={fr.value}, threshold={fr.threshold})"
        )

    if blocking_tag != "NONE":
        parts.append(f"→ Blocking at {blocking_tag} → verdict={blocking_verdict}")

    if evidence_bundle is None:
        parts.append("(evidence_bundle was None — F7 Humility triggered HOLD_888)")

    return "; ".join(parts)


def _build_conditions(floor_results: List[FloorResult]) -> Dict[str, Any]:
    """Build conditions dict listing each floor's requirement and status."""
    conditions: Dict[str, Any] = {}
    for fr in floor_results:
        conditions[fr.tag] = {
            "required": fr.threshold,
            "actual": fr.value,
            "status": "met" if fr.passed else "violated",
        }
    return conditions


def _build_appeal_process(blocking_verdict: str, blocking_tag: str) -> Dict[str, str]:
    """Build appeal_process dict based on blocking verdict."""
    base = {
        "process": "arifOS appeal via 888_judge re-evaluation",
        "contact": "human_sovereign (Arif)",
        "channel": "telegram_direct",
    }

    if blocking_verdict == VERDICT_HOLD_888:
        if blocking_tag == "F1_AMANAH_ZKPC":
            msg = "Action class requires Level 2 Personhood proof. Submit CLASS_A or CLASS_B evidence."
            note = "F1 AMANAH signals require human-witnessed cryptographic proof"
        else:
            msg = "Submit new evidence_bundle with corrected Ω0 or reduced sovereign flags"
            note = "F13 sovereign flags require Arif's explicit veto override"

        return {
            **base,
            "verdict": "888_HOLD",
            "action": msg,
            "note": note,
        }
    elif blocking_verdict == VERDICT_VOID:
        return {
            **base,
            "verdict": "VOID",
            "action": "F2 Truth floor violated — re-evaluate truth_score upward to >= 0.99",
            "note": "Hard block — cannot appeal without new evidence",
        }
    elif blocking_verdict == VERDICT_SABAR:
        return {
            **base,
            "verdict": "SABAR",
            "action": "Cooling period required — re-evaluate peace_squared upward to >= 1.0",
            "note": "Wait for thermodynamic stabilization before retry",
        }
    else:
        return {
            **base,
            "verdict": "UNKNOWN",
            "action": "Provide a valid, non-empty evidence_bundle",
            "note": "No evidence was provided — F7 Humility applies",
        }


# ──────────────────────────────────────────────────────────────────────────────
# Public API: execute
# ──────────────────────────────────────────────────────────────────────────────


async def execute(
    evidence_bundle: dict | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """
    Constitutional verdict engine for arifOS 888_judge.

    Mandatory evidence_bundle check — if None or empty, returns HOLD_888
    under F7 Humility. Never defaults to SEAL without explicit evidence.

    Args:
        evidence_bundle: Dict containing at minimum:
            - metrics: ThermodynamicMetrics (or dict equivalent)
            - Any additional contextual keys
        operator_id: Operator identifier for audit trail
        session_id: Session identifier for audit trail

    Returns:
        dict with keys:
            - verdict: SEAL | HOLD | VOID | 888_HOLD
            - rationale: str
            - conditions: dict
            - metabolic_metadata: dict (floor_alignment, confidence_score, readiness_probe)
            - appeal_process: dict
            - vault999_chain_hash: str
            - evidence_bundle: echo of input
            - operator_id: echo of input
            - session_id: echo of input
    """

    # ── 1. Mandatory evidence_bundle check (F7 Humility) ─────────────────────
    if evidence_bundle is None or (isinstance(evidence_bundle, dict) and len(evidence_bundle) == 0):
        vault_hash = append_vault999_event(
            event_type="888_JUDGE_EXECUTION",
            payload={"verdict": VERDICT_HOLD_888, "reason": "EMPTY_BUNDLE"},
            operator_id=operator_id,
            session_id=session_id,
        )

        return {
            "verdict": VERDICT_HOLD_888,
            "rationale": "F7 Humility: evidence_bundle is None or empty — cannot render verdict. HOLD_888.",
            "conditions": {"F7_OMEGA0": {"status": "unknown", "reason": "no evidence"}},
            "metabolic_metadata": {
                "floor_alignment": {},
                "confidence_score": 0.0,
                "readiness_probe": {
                    "state": "HOLD_888",
                    "passed_floors": [],
                    "failed_floors": ["F7"],
                    "blocking_tag": "F7_OMEGA0",
                    "all_cleared": False,
                },
            },
            "appeal_process": {
                "verdict": "888_HOLD",
                "process": "arifOS appeal via 888_judge re-evaluation",
                "contact": "human_sovereign (Arif)",
                "channel": "telegram_direct",
                "action": "Provide a valid, non-empty evidence_bundle containing ThermodynamicMetrics",
                "note": "F7 Humility — absence of evidence triggers HOLD_888, not SEAL",
            },
            "vault999_chain_hash": vault_hash,
            "evidence_bundle": _safe_serializable(evidence_bundle),
            "operator_id": operator_id,
            "session_id": session_id,
        }

    # ── 2. Extract ThermodynamicMetrics from evidence_bundle ──────────────────
    raw_metrics = evidence_bundle.get("metrics")
    if raw_metrics is None:
        vault_hash = append_vault999_event(
            event_type="888_JUDGE_EXECUTION",
            payload={"verdict": VERDICT_HOLD_888, "reason": "NO_METRICS"},
            operator_id=operator_id,
            session_id=session_id,
        )
        return {
            "verdict": VERDICT_HOLD_888,
            "rationale": "F7 Humility: evidence_bundle contains no 'metrics' key — cannot render verdict. HOLD_888.",
            "conditions": {"F7_OMEGA0": {"status": "unknown", "reason": "no metrics"}},
            "metabolic_metadata": {
                "floor_alignment": {},
                "confidence_score": 0.0,
                "readiness_probe": {
                    "state": "HOLD_888",
                    "passed_floors": [],
                    "failed_floors": ["F7"],
                    "blocking_tag": "F7_OMEGA0",
                    "all_cleared": False,
                },
            },
            "appeal_process": _build_appeal_process(VERDICT_HOLD_888, "NONE"),
            "vault999_chain_hash": vault_hash,
            "evidence_bundle": _safe_serializable(evidence_bundle),
            "operator_id": operator_id,
            "session_id": session_id,
        }

    # Support both dataclass and dict forms
    if isinstance(raw_metrics, ThermodynamicMetrics):
        metrics = raw_metrics
    elif isinstance(raw_metrics, dict):
        try:
            metrics = ThermodynamicMetrics(**raw_metrics)
        except Exception:
            vault_hash = append_vault999_event(
                event_type="888_JUDGE_EXECUTION",
                payload={"verdict": VERDICT_HOLD_888, "reason": "MALFORMED_METRICS"},
                operator_id=operator_id,
                session_id=session_id,
            )
            return {
                "verdict": VERDICT_HOLD_888,
                "rationale": f"F7 Humility: metrics cannot be parsed — {type(raw_metrics).__name__}. HOLD_888.",
                "conditions": {"F7_OMEGA0": {"status": "unknown", "reason": "malformed metrics"}},
                "metabolic_metadata": {
                    "floor_alignment": {},
                    "confidence_score": 0.0,
                    "readiness_probe": {
                        "state": "HOLD_888",
                        "passed_floors": [],
                        "failed_floors": ["F7"],
                        "blocking_tag": "F7_OMEGA0",
                        "all_cleared": False,
                    },
                },
                "appeal_process": _build_appeal_process(VERDICT_HOLD_888, "NONE"),
                "vault999_chain_hash": vault_hash,
                "evidence_bundle": evidence_bundle,
                "operator_id": operator_id,
                "session_id": session_id,
            }
    else:
        vault_hash = append_vault999_event(
            event_type="888_JUDGE_EXECUTION",
            payload={"verdict": VERDICT_HOLD_888, "reason": "INVALID_METRICS_TYPE"},
            operator_id=operator_id,
            session_id=session_id,
        )
        return {
            "verdict": VERDICT_HOLD_888,
            "rationale": f"F7 Humility: metrics type {type(raw_metrics).__name__} not recognized. HOLD_888.",
            "conditions": {"F7_OMEGA0": {"status": "unknown", "reason": "invalid type"}},
            "metabolic_metadata": {
                "floor_alignment": {},
                "confidence_score": 0.0,
                "readiness_probe": {
                    "state": "HOLD_888",
                    "passed_floors": [],
                    "failed_floors": ["F7"],
                    "blocking_tag": "F7_OMEGA0",
                    "all_cleared": False,
                },
            },
            "appeal_process": _build_appeal_process(VERDICT_HOLD_888, "NONE"),
            "vault999_chain_hash": vault_hash,
            "evidence_bundle": _safe_serializable(evidence_bundle),
            "operator_id": operator_id,
            "session_id": session_id,
        }

    # ── 3. Iterate constitutional floors ──────────────────────────────────────
    floor_results, blocking_verdict, blocking_tag = _iterate_constitutional_floors(
        metrics, evidence_bundle
    )

    # ── 4. Determine final verdict ───────────────────────────────────────────
    final_verdict = blocking_verdict

    # Override: if all floors passed, set SEAL
    if blocking_tag == "NONE":
        final_verdict = VERDICT_SEAL

    # ── 5. Build metabolic_metadata ──────────────────────────────────────────
    confidence_score = _compute_confidence_score(metrics)
    floor_alignment = _build_floor_alignment(floor_results)
    readiness_probe = _compute_readiness_probe(floor_results, blocking_tag)

    metabolic_metadata = {
        "floor_alignment": floor_alignment,
        "confidence_score": confidence_score,
        "readiness_probe": readiness_probe,
    }

    # ── 6. Build rationale, conditions, appeal_process ───────────────────────
    rationale = _build_rationale(floor_results, blocking_tag, final_verdict, evidence_bundle)
    conditions = _build_conditions(floor_results)
    appeal_process = _build_appeal_process(final_verdict, blocking_tag)

    # ── 7. Always call append_vault999_event ────────────────────────────────

    vault_hash = append_vault999_event(
        event_type="888_JUDGE_EXECUTION",
        payload={
            "verdict": final_verdict,
            "evidence_bundle": _safe_serializable(evidence_bundle),
            "metrics": _safe_serializable(metrics),
            "floor_alignment": floor_alignment,
            "confidence_score": confidence_score,
            "blocking_tag": blocking_tag,
        },
        operator_id=operator_id,
        session_id=session_id,
    )

    # ── 8. Assemble and return envelope ──────────────────────────────────────
    return {
        "verdict": final_verdict,
        "rationale": rationale,
        "conditions": conditions,
        "metabolic_metadata": metabolic_metadata,
        "appeal_process": appeal_process,
        "vault999_chain_hash": vault_hash,
        "evidence_bundle": evidence_bundle,
        "operator_id": operator_id,
        "session_id": session_id,
    }
