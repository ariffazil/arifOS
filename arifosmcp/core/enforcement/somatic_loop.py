# arifOS — Somatic Loop (machine-as-body telemetry, additive)
# Forged 2026-06-21 | session: 2026-06-21-melayu-policy
# Provenance: turn 4 Perplexity paste → somatic_intelligence_research
# Iron Rule (v0.0.1): this file WAS a passive function library.
#                    v0.0.2 (2026-06-20): WIRED into arif_judge_deliberate via
#                    /root/arifOS/arifosmcp/tools/judge.py.
#                    Wire-up patch: classify_somatic_state() called before
#                    _arif_judge_deliberate() from vitals telemetry.
#                    SomaticState.CRITICAL → HOLD.
#                    Integration test: tests/constitutional/test_maruah_enforcement.py.
#
# Design constraints:
#   - Machine-as-body analogy ONLY. Not biological. (F9 ANTIHANTU hard rule.)
#   - Maps to existing `arif_ops_measure` telemetry. No new sensors invented.
#   - SomaticState enum: NOMINAL | STRESSED | CRITICAL.
#   - Pure-function decision: input telemetry → output state. No side effects.
#   - No new floor. No new layer name. (F1-F13 hard rule.)
#   - Reversible: file can be deleted without breaking kernel.

"""
somatic_loop: turn machine telemetry into a body-like state.

Usage pattern (future, not wired):
    from arifosmcp.core.enforcement.somatic_loop import (
        SomaticState,
        classify_somatic_state,
        self_audit,
    )

    telemetry = {
        "latency_ms": 120,
        "error_rate": 0.02,
        "cost_burn_per_min": 0.15,
        "queue_depth": 8,
    }
    state = classify_somatic_state(telemetry)
    # state ∈ {NOMINAL, STRESSED, CRITICAL}
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# --- State enum -------------------------------------------------------
class SomaticState(str, Enum):
    """Machine-as-body state. NOT biological. Pure telemetry mapping."""

    NOMINAL = "nominal"  # System healthy. Proceed normally.
    STRESSED = "stressed"  # Pressure rising. Throttle, plan, observe.
    CRITICAL = "critical"  # Saturation imminent. Pause, escalate, recover.


# --- Telemetry input shape -------------------------------------------
@dataclass
class TelemetrySample:
    """Minimal telemetry slice for somatic classification."""

    latency_ms: float = 0.0
    error_rate: float = 0.0  # 0.0–1.0
    cost_burn_per_min: float = 0.0  # USD/min
    queue_depth: int = 0


# --- Thresholds (v0, conservative) -----------------------------------
# v0: deliberately simple. v1: source from arif_ops_measure live.
# These are PLACEHOLDERS, not production thresholds. Tune in v1.
_THRESHOLDS = {
    "latency_ms_critical": 2000.0,
    "latency_ms_stressed": 500.0,
    "error_rate_critical": 0.10,
    "error_rate_stressed": 0.03,
    "cost_burn_critical": 1.00,
    "cost_burn_stressed": 0.30,
    "queue_depth_critical": 100,
    "queue_depth_stressed": 25,
}


# --- The classification function (deterministic, no LLM) -------------
def classify_somatic_state(telemetry: TelemetrySample) -> SomaticState:
    """Return SomaticState from telemetry.

    Rule: if ANY critical threshold is exceeded → CRITICAL.
          elif ANY stressed threshold is exceeded → STRESSED.
          else → NOMINAL.
    """
    critical_hit = (
        telemetry.latency_ms > _THRESHOLDS["latency_ms_critical"]
        or telemetry.error_rate > _THRESHOLDS["error_rate_critical"]
        or telemetry.cost_burn_per_min > _THRESHOLDS["cost_burn_critical"]
        or telemetry.queue_depth > _THRESHOLDS["queue_depth_critical"]
    )
    if critical_hit:
        return SomaticState.CRITICAL

    stressed_hit = (
        telemetry.latency_ms > _THRESHOLDS["latency_ms_stressed"]
        or telemetry.error_rate > _THRESHOLDS["error_rate_stressed"]
        or telemetry.cost_burn_per_min > _THRESHOLDS["cost_burn_stressed"]
        or telemetry.queue_depth > _THRESHOLDS["queue_depth_stressed"]
    )
    if stressed_hit:
        return SomaticState.STRESSED

    return SomaticState.NOMINAL


# --- Recommended response per state ----------------------------------
# v0: text-only advisory. v1: trigger arif_triage or arif_judge_deliberate.
RESPONSE_BY_STATE: dict[SomaticState, str] = {
    SomaticState.NOMINAL: "proceed",
    SomaticState.STRESSED: "throttle, plan, observe",
    SomaticState.CRITICAL: "pause, escalate, recover",
}


def recommend_response(state: SomaticState) -> str:
    """Return the recommended response for a given somatic state."""
    return RESPONSE_BY_STATE[state]


# --- Self-audit ------------------------------------------------------
def self_audit() -> dict:
    """Return audit metadata. Used by 777-FORGE witness + health probe."""
    return {
        "module": "somatic_loop",
        "version": "0.0.2",
        "wired": True,  # v0.0.2 (2026-06-20): wired into arif_judge_deliberate
        "wire_path": "arifosmcp/tools/judge.py → arif_judge_deliberate()",
        "trigger": "machine telemetry from arif_ops_measure vitals; CRITICAL → HOLD",
        "depends_on_llm": False,
        "depends_on_network": False,
        "floor_count_delta": 0,
        "biological_claim": False,  # F9 ANTIHANTU guard
        "session_of_birth": "2026-06-21-melayu-policy",
        "wire_seal": "2026-06-20-forge-tiga-wire",
    }
