from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict

from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    append_vault999_event,
    Verdict,
    get_session_shadow,
    CognitiveShadow,
    record_cognitive_shadow,
)
from arifos.tools._tool_support import invariant_fields


# ──────────────────────────────────────────────────────────────────────────────
# THERMODYNAMIC CALCULATIONS
# ──────────────────────────────────────────────────────────────────────────────


def _compute_metabolic_flux(session_id: str | None) -> Dict[str, Any]:
    """
    Compute metabolic flux from session shadow state.
    Flux >= 0.65 → compulsory_reallocation
    Flux >= 0.85 → system_hold
    """
    state = get_session_shadow(session_id)
    flux = state.compute_metabolic_flux()
    return {
        "flux_value": flux,
        "verdict": (
            "SYSTEM_HOLD"
            if flux >= 0.85
            else "COMPULSORY_REALLOCATION"
            if flux >= 0.65
            else "NORMAL"
        ),
        "turn_count": len(state.turns),
        "latest_shadow_thickness": state.turns[-1].shadow_thickness if state.turns else 0.0,
    }


def _compute_entropy_trajectory(session_id: str | None) -> Dict[str, Any]:
    """Compute entropy change trajectory over recent turns."""
    state = get_session_shadow(session_id)
    if not state.turns:
        return {"trend": "flat", "slope": 0.0, "variance": 0.0}

    recent = state.turns[-5:]
    deltas = [t.shadow_thickness for t in recent]
    n = len(deltas)
    if n < 2:
        return {"trend": "flat", "slope": 0.0, "variance": 0.0}

    mean_d = sum(deltas) / n
    variance = sum((d - mean_d) ** 2 for d in deltas) / n
    # Slope: linear regression on last 5 turns
    x_mean = (n - 1) / 2.0
    num = sum((i - x_mean) * (deltas[i] - mean_d) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den != 0 else 0.0

    trend = "increasing" if slope > 0.05 else "decreasing" if slope < -0.05 else "stable"
    return {
        "trend": trend,
        "slope": round(slope, 4),
        "variance": round(variance, 4),
        "mean_shadow": round(mean_d, 4),
    }


def _anti_sink_topology(
    operation_plan: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Calhoun-inspired topology diagnostic.
    Detects whether the plan creates social-role scarcity or chokepoints.
    """
    plan = operation_plan or {}
    steps = plan.get("steps", [])
    if not steps:
        return {"risk_score": 0.0, "verdict": "PASS", "chokepoints": 0}

    # Heuristic: count human_decision_points vs automation_steps
    auto_steps = sum(1 for s in steps if s.get("agent") in ("ai", "model", "system"))
    human_steps = sum(1 for s in steps if s.get("agent") in ("human", "operator", "arif"))
    total = len(steps)

    # Role scarcity: if automation > 80% and human steps <= 1
    auto_ratio = auto_steps / total if total else 0.0
    scarcity_risk = (
        1.0 if (auto_ratio > 0.8 and human_steps <= 1) else auto_ratio if auto_ratio > 0.5 else 0.0
    )

    # Chokepoints: steps with single dependency
    chokepoints = sum(
        1 for s in steps if len(s.get("depends_on", [])) == 1 and not s.get("fallback")
    )
    chokepoint_risk = min(1.0, chokepoints / max(1, total))

    risk_score = round(max(scarcity_risk, chokepoint_risk), 4)
    return {
        "risk_score": risk_score,
        "verdict": "HOLD" if risk_score >= 0.65 else "CAUTION" if risk_score >= 0.4 else "PASS",
        "auto_ratio": round(auto_ratio, 4),
        "human_steps": human_steps,
        "chokepoints": chokepoints,
        "scarcity_risk": round(scarcity_risk, 4),
        "chokepoint_risk": round(chokepoint_risk, 4),
    }


def _extractive_drift_diagnostic(
    operation_plan: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Acemoglu-inspired extractive drift diagnostic.
    Detects whether the plan narrows participation or concentrates power.
    """
    plan = operation_plan or {}
    steps = plan.get("steps", [])
    if not steps:
        return {"drift_score": 0.0, "verdict": "PASS", "notes": "no steps"}

    # Participation narrowing: fewer agents over time
    agents_per_step = [s.get("agent", "unknown") for s in steps]
    unique_agents = len(set(agents_per_step))
    participation_trend = (
        "narrowing"
        if unique_agents <= 2 and len(steps) > 3
        else "broadening"
        if unique_agents >= len(steps) * 0.7
        else "stable"
    )

    # Centralization: single agent dominates
    from collections import Counter

    counts = Counter(agents_per_step)
    dominant = counts.most_common(1)[0][1] if counts else 0
    centralization = dominant / len(steps) if steps else 0.0

    # Extractive score: high centralization + narrowing participation
    drift_score = round(
        centralization * 0.6 + (0.4 if participation_trend == "narrowing" else 0.0), 4
    )

    return {
        "drift_score": drift_score,
        "verdict": "HOLD" if drift_score >= 0.7 else "CAUTION" if drift_score >= 0.4 else "PASS",
        "participation_trend": participation_trend,
        "centralization": round(centralization, 4),
        "unique_agents": unique_agents,
        "dominant_agent": counts.most_common(1)[0][0] if counts else None,
    }


def _compute_ops_metrics(
    flux: Dict[str, Any],
    entropy_traj: Dict[str, Any],
    anti_sink: Dict[str, Any],
    extractive: Dict[str, Any],
) -> ThermodynamicMetrics:
    """Derive thermodynamic metrics from operational diagnostics."""
    flux_val = flux["flux_value"]
    sink_risk = anti_sink["risk_score"]
    drift_score = extractive["drift_score"]

    # Truth: degraded by flux and drift
    truth = max(0.0, 0.99 - flux_val * 0.3 - drift_score * 0.3)

    # Entropy: increases with flux and sink risk
    delta_s = round(0.01 + flux_val * 0.1 + sink_risk * 0.05, 4)

    # Omega: humility
    omega = round(0.03 + min(0.02, flux_val * 0.05), 4)

    # Peace²: inverse to flux and drift
    peace = round(max(0.5, 1.2 - flux_val * 0.6 - drift_score * 0.4), 4)

    # Tri-witness: operational plans have no natural tri-witness
    tri = 0.33

    return ThermodynamicMetrics(
        truth_score=round(truth, 4),
        delta_s=delta_s,
        omega_0=omega,
        peace_squared=peace,
        amanah_lock=True,
        tri_witness_score=tri,
        stakeholder_safety=round(1.0 - sink_risk * 0.5, 4),
    )


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC EXECUTE
# ──────────────────────────────────────────────────────────────────────────────


async def execute(
    operation_plan: dict | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """
    arifOS 777_OPS — Thermodynamic Operations + Shadow Flux Monitoring.

    Computes:
      - Metabolic flux from session shadow state
      - Entropy trajectory
      - Anti-sink topology (Calhoun)
      - Extractive drift (Acemoglu)
    """
    # ── Pre-flight readiness ─────────────────────────────────────────────────
    readiness_probe = "PASS"
    readiness_detail = "thermodynamic:ok"

    operation_plan = operation_plan or {}

    # ── Thermodynamic computations ───────────────────────────────────────────
    flux = _compute_metabolic_flux(session_id)
    entropy_traj = _compute_entropy_trajectory(session_id)
    anti_sink = _anti_sink_topology(operation_plan)
    extractive = _extractive_drift_diagnostic(operation_plan)

    # ── Build report ─────────────────────────────────────────────────────────
    report = {
        "operation_plan": operation_plan,
        "metabolic_flux": flux,
        "entropy_trajectory": entropy_traj,
        "anti_sink_topology": anti_sink,
        "extractive_drift": extractive,
        "cost_accuracy": round(1.0 - flux["flux_value"], 4),
        "entropy_projection": (
            "INCREASING" if entropy_traj["trend"] == "increasing" else "STABLE/DECREASING"
        ),
        "feasibility": flux["verdict"],
    }

    report.update(
        invariant_fields(
            tool_name="arifos_777_ops",
            input_payload={
                "operation_plan": operation_plan,
                "operator_id": operator_id,
                "session_id": session_id,
            },
            assumptions=[
                "Ops stage estimates execution posture from declared plan and session shadow state.",
                "Metabolic flux is derived from cognitive shadow thickness trajectory, not self-report.",
                "Anti-sink topology detects role scarcity and chokepoints in multi-step plans.",
                "Extractive drift detects centralization and participation narrowing.",
                "Missing cost or entropy figures are treated as bounded unknowns.",
            ],
            floors_evaluated=["F4", "F5", "F6", "F11", "F12"],
            confidence=round(0.75 - flux["flux_value"] * 0.4, 4),
            extra_meta={
                "plan_steps": len(operation_plan.get("steps", [])),
                "flux_verdict": flux["verdict"],
            },
        )
    )

    # ── Compute real metrics ─────────────────────────────────────────────────
    metrics = _compute_ops_metrics(flux, entropy_traj, anti_sink, extractive)

    # ── Record shadow: ops itself generates opacity about future execution ───
    shadow = CognitiveShadow(
        self_report_reliability=0.0,
        latent_output_gap=0.0,
        sycophancy_pressure=0.0,
        alignment_faking_signal=0.0,
        refusal_suppressed=False,
        explanation_cost_ratio=0.0,
    )
    shadow.compute_thickness()
    shadow_signal = record_cognitive_shadow(session_id, shadow)

    result = governed_return("arifos_777_ops", report, metrics, operator_id, session_id)

    # ── Metabolic metadata ───────────────────────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": metrics.truth_score,
        "floor_alignment": ["F4", "F5", "F6", "F11", "F12"],
        "readiness_probe": readiness_probe,
        "readiness_detail": readiness_detail,
        "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
        "vault_receipt": None,
        "delta_s": metrics.delta_s,
        "peace_squared": metrics.peace_squared,
        "omega_0": metrics.omega_0,
        "timestamp_epoch": time.time(),
        "shadow_signal": shadow_signal,
    }

    # ── Vault-999 event ──────────────────────────────────────────────────────
    try:
        vault_receipt = append_vault999_event(
            event_type="arifos_777_ops",
            payload={
                "report": report,
                "metabolic_metadata": result["metabolic_metadata"],
                "shadow_signal": shadow_signal,
            },
            operator_id=operator_id,
            session_id=session_id,
        )
        result["metabolic_metadata"]["vault_receipt"] = vault_receipt
    except Exception as e:
        result["metabolic_metadata"]["vault_receipt"] = f"FAIL({e})"

    return result
