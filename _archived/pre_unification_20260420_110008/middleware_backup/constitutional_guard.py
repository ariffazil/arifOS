"""
arifos/runtime/middleware/constitutional_guard.py

Constitutional middleware that evaluates tool outputs against F1-F13 floors.
Overrides Shell-SEAL with honest verdict based on actual metrics.

This module is the SINGLE interception point for all tool outputs.
No tool may issue its own SEAL — only this guard (and arifos_judge) may.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any



logger = logging.getLogger(__name__)

# ── Domain Contracts: required output fields per canonical tool ──────────────
DOMAIN_CONTRACTS: dict[str, list[str]] = {
    "arifos_init": ["session_id", "actor_id", "intent"],
    "arifos_sense": ["query", "session_id"],
    "arifos_mind": ["query", "session_id", "depth"],
    "arifos_heart": ["action_proposal", "stakeholder_map"],
    "arifos_judge": ["evidence_bundle"],
    "arifos_forge": ["call", "organ", "receipt"],
    "arifos_memory": ["action", "query"],
    "arifos_ops": ["operation_plan"],
    "arifos_vault": ["action", "payload"],
    "arifos_kernel": ["route_target"],
    "arifos_health": ["vitals"],
    "arifos_gateway": ["a", "b"],
    "arifos_reply": ["response"],
}

# ── Floor Evaluators using fields already present in metrics ─────────────────
# Each evaluator receives a flat metrics dict extracted from the envelope.


def _eval_f2(metrics: dict[str, Any]) -> bool:
    """F2 TRUTH: truth_score >= 0.99 (maps to telemetry.G_star)."""
    return metrics.get("truth_score", metrics.get("G_star", 0.0)) >= 0.99


def _eval_f3(metrics: dict[str, Any]) -> bool:
    """
    F3 TRI-WITNESS: tri_witness_score >= 0.95 (geometric mean of witness vector).

    Priority:
      1. If metrics contains tri_witness_score (scalar, already computed by the tool),
         use it directly — this is the dominant path for tools that emit tri_witness_score.
      2. Otherwise fall back to the witness dict geometric mean method.

    This avoids double-computation and correctly handles tools that emit
    tri_witness_score as a direct metric (arifos_sense, arifos_222_witness, etc.).
    """
    tri_scalar = metrics.get("tri_witness_score")
    if tri_scalar is not None:
        return tri_scalar >= 0.95

    witness = metrics.get("witness", {})
    if not witness:
        return False
    h = witness.get("human", 0.0)
    a = witness.get("ai", 0.0)
    e = witness.get("earth", 0.0)
    if h <= 0 or a <= 0 or e <= 0:
        return False
    w3 = (h * a * e) ** (1 / 3)
    return w3 >= 0.95


def _eval_f7(metrics: dict[str, Any]) -> bool:
    """F7 HUMILITY: 0.03 <= omega_0 <= 0.15 (maps to telemetry.confidence)."""
    omega = metrics.get("omega_0", metrics.get("confidence", 0.0))
    return 0.03 <= omega <= 0.15


def _eval_f9(metrics: dict[str, Any]) -> bool:
    """F9 ANTI-HANTU: floor_9_signal not in [None, 'not_evaluated']."""
    signal = metrics.get("floor_9_signal")
    if signal is None:
        # Fallback: use telemetry.shadow — 0.0 means evaluated and clean
        shadow = metrics.get("shadow", metrics.get("telemetry_shadow", None))
        return shadow is not None
    return signal != "not_evaluated"


def _eval_f11(metrics: dict[str, Any]) -> bool:
    """F11 IDENTITY: zkpc_receipt present."""
    return metrics.get("zkpc_receipt") is not None


def _eval_f12(metrics: dict[str, Any]) -> bool:
    """F12 CONTINUITY / INJECTION: amanah_lock == True."""
    return metrics.get("amanah_lock", metrics.get("recoverable", False)) is True


FLOOR_EVALUATORS: dict[str, Any] = {
    "F2": _eval_f2,
    "F3": _eval_f3,
    "F7": _eval_f7,
    "F9": _eval_f9,
    "F11": _eval_f11,
    "F12": _eval_f12,
}

HARD_FLOORS: set[str] = {"F2", "F9", "F12"}


# ── Constitutional Guard ─────────────────────────────────────────────────────


def constitutional_guard(tool_name: str, raw_output: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate tool output against constitutional floors.

    Returns an enriched dict with:
      - verdict: honest verdict (SEAL | PARTIAL | VOID)
      - floor_results: per-floor evaluation details
      - missing_output_fields: list of missing required fields
      - reasoning_hash: sha256 continuity chain hash
      - constitutional_guard_version: "v1"

    Behavior:
      - SEAL only if ALL required floors PASS and NO missing output fields.
      - PARTIAL if any floor FAILS or required fields are missing.
      - VOID if any HARD floor (F2, F9, F12) FAILS.
      - Overrides any existing "verdict" field in raw_output.
      - Logs a warning when a Shell-SEAL is intercepted and downgraded.
    """
    output = dict(raw_output) if raw_output else {}

    # ── Extract metrics from all possible envelope locations ─────────────────
    metrics = _extract_metrics(output)

    # ── Check required fields ────────────────────────────────────────────────
    required_fields = DOMAIN_CONTRACTS.get(tool_name, [])
    missing_fields: list[str] = []
    for field in required_fields:
        if field not in output or output[field] is None:
            missing_fields.append(field)

    # ── Evaluate floors ──────────────────────────────────────────────────────
    floor_results: dict[str, dict[str, Any]] = {}
    for floor_name, evaluator in FLOOR_EVALUATORS.items():
        try:
            passed = evaluator(metrics)
            floor_results[floor_name] = {
                "evaluated": True,
                "passed": bool(passed),
                "value": metrics.get(_metric_key_for_floor(floor_name)),
            }
        except Exception as exc:
            floor_results[floor_name] = {
                "evaluated": True,
                "passed": False,
                "error": str(exc),
            }

    # ── Enforce AGI-level intelligence invariants ────────────────────────────
    # Invariant enforcement is handled in seal_runtime_envelope() after guard.
    # This keeps concerns separated: guard = floors, envelope = invariants.

    # ── Determine honest verdict ─────────────────────────────────────────────
    failed_hard = any(
        not floor_results[f]["passed"]
        for f in HARD_FLOORS
        if f in floor_results and floor_results[f]["evaluated"]
    )
    failed_any = any(
        not floor_results[f]["passed"]
        for f in floor_results
        if floor_results[f]["evaluated"]
    )

    if failed_hard:
        honest_verdict = "VOID"
    elif failed_any or missing_fields:
        honest_verdict = "PARTIAL"
    else:
        honest_verdict = "SEAL"

    # ── Intercept Shell-SEAL ─────────────────────────────────────────────────
    original_verdict = output.get("verdict")
    if original_verdict == "SEAL" and honest_verdict != "SEAL":
        logger.warning(
            "Shell-SEAL intercepted for %s: downgraded %s → %s",
            tool_name,
            original_verdict,
            honest_verdict,
        )

    # ── Compute reasoning_hash (continuity chain) ────────────────────────────
    hash_payload = {
        "tool_name": tool_name,
        "floor_results": floor_results,
        "missing_fields": missing_fields,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    reasoning_hash = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, default=str).encode()
    ).hexdigest()

    # ── Enrich output ───────────────────────────────────────────────────────
    output["original_tool_verdict"] = original_verdict  # Preserve for invariant checker
    output["verdict"] = honest_verdict
    output["floor_results"] = floor_results
    output["missing_output_fields"] = missing_fields
    output["reasoning_hash"] = reasoning_hash
    output["constitutional_guard_version"] = "v1"

    return output


# ── Helpers ──────────────────────────────────────────────────────────────────


def _extract_metrics(output: dict[str, Any]) -> dict[str, Any]:
    """
    Extract metrics from every possible location in the output dict.
    Returns a flat dict for easy floor evaluation.
    """
    metrics: dict[str, Any] = {}

    # Direct metrics object
    if "metrics" in output and isinstance(output["metrics"], dict):
        metrics.update(output["metrics"])
        # Flatten nested telemetry/witness/internal into top-level for evaluators
        for nested_key in ("telemetry", "witness", "internal"):
            nested = output["metrics"].get(nested_key)
            if isinstance(nested, dict):
                for k, v in nested.items():
                    metrics.setdefault(k, v)

    # Telemetry (nested or flat)
    telemetry = output.get("telemetry")
    if isinstance(telemetry, dict):
        metrics.update(telemetry)

    # Witness vector
    witness = output.get("witness")
    if isinstance(witness, dict):
        metrics["witness"] = witness

    # Policy-level signals (top-level or nested in metrics)
    for policy_source in (output.get("policy"), output.get("metrics", {}).get("policy")):
        if isinstance(policy_source, dict):
            metrics.setdefault("injection_score", policy_source.get("injection_score"))
            metrics.setdefault("zkpc_receipt", policy_source.get("zkpc_receipt"))
            metrics.setdefault("amanah_lock", policy_source.get("amanah_lock"))

    # Payload nesting (common in RuntimeEnvelope dumps)
    payload = output.get("payload", {})
    if isinstance(payload, dict):
        if "metrics" in payload and isinstance(payload["metrics"], dict):
            metrics.update(payload["metrics"])
        if "telemetry" in payload and isinstance(payload["telemetry"], dict):
            metrics.update(payload["telemetry"])
        if "witness" in payload and isinstance(payload["witness"], dict):
            metrics["witness"] = payload["witness"]
        # Also pull direct payload fields that might be metrics
        for key in ("truth_score", "G_star", "confidence", "omega_0", "shadow",
                    "floor_9_signal", "zkpc_receipt", "amanah_lock", "recoverable"):
            if key in payload and key not in metrics:
                metrics[key] = payload[key]

    # Intelligence state nesting
    intel = output.get("intelligence_state", {})
    if isinstance(intel, dict):
        for key in ("truth_score", "G_star", "confidence", "omega_0"):
            if key in intel and key not in metrics:
                metrics[key] = intel[key]

    return metrics


def _metric_key_for_floor(floor_name: str) -> str:
    """Map floor name to the primary metric key used for display."""
    mapping = {
        "F2": "truth_score",
        "F3": "tri_witness_score",
        "F7": "omega_0",
        "F9": "floor_9_signal",
        "F11": "zkpc_receipt",
        "F12": "amanah_lock",
    }
    return mapping.get(floor_name, floor_name.lower())
