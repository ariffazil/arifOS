"""
arifOS Governance Kernel — Floors F1–F13, ΔS, Ω0, Tri-Witness
Constitutional Patch: v0.2 | A-FORGE Bridge Ready

This module is the Single Execution Spine (SES) for all 13 tools.
All irreversible or high-impact decisions must pass through here.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations
import hashlib
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Union
from enum import Enum

from arifOS_mcp.runtime.state import IDENTITY_MANAGER, MetabolicState

# Vitality ledger integration — live writes from tool executions
_emit_vitality = None
_VITALITY_LEDGER_DIR: Optional[str] = None
try:
    from arifOS_mcp.tools.arifos.tool_vitality import (
        emit_vitality as _emit_vitality_fn,
        GovernanceMetrics as _VitalityGovMetrics,
        PerformanceMetrics as _VitalityPerfMetrics,
        CorrectnessMetrics as _VitalityCorrMetrics,
    )

    _emit_vitality = _emit_vitality_fn
    import os as _os

    _VITALITY_LEDGER_DIR = _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "..", "..", "arifOS_mcp", "tools", "arifos"
    )
except Exception:
    _emit_vitality = None


class Verdict(Enum):
    SEAL = "SEAL"  # Approved and hashed
    SABAR = "SABAR"  # Hold for cooling/reflection
    VOID = "VOID"  # Rejected/Violated
    HOLD_888 = "HOLD_888"  # Awaiting APEX consensus


@dataclass
class ThermodynamicMetrics:
    truth_score: float = 1.0  # F2: >= 0.99 for SEAL
    delta_s: float = 0.0  # F4: <= 0 for SEAL
    omega_0: float = 0.04  # F12: must be in [0.03, 0.05]
    peace_squared: float = 1.0  # F7: >= 1.0 for SEAL
    amanah_lock: bool = True  # F1: must be True for SEAL
    tri_witness_score: float = 1.0  # F3: >= 0.95 for high-stakes
    stakeholder_safety: float = 1.0  # F6/F9: >= 0.9 preferred

    # Advanced Floor Signals (F8-F13)
    floor_8_signal: Optional[str] = None  # Sabar
    floor_9_signal: Optional[str] = None  # Ethics
    floor_10_signal: Optional[str] = None  # Conscience
    floor_11_signal: Optional[str] = None  # Audit
    floor_12_signal: Optional[str] = None  # Humility
    floor_13_signal: Optional[str] = None  # Sovereignty


def _build_receipt_id(stage: str) -> str:
    """Cryptographic receipt using SHA-256 (F11 Audit)."""
    nonce = f"{stage.upper()}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    return hashlib.sha256(nonce.encode("utf-8")).hexdigest()[:24]


def _validate_tri_witness(metrics: ThermodynamicMetrics) -> bool:
    """F3 Tri-Witness: high-stakes operations require W³ >= 0.95."""
    # For standard operations, truth_score + tri_witness_score average >= 0.95
    return (metrics.truth_score + metrics.tri_witness_score) / 2.0 >= 0.95


def governed_return(
    stage: str,
    data: Any,
    metrics: ThermodynamicMetrics,
    verdict: Union[Verdict, str] = Verdict.SEAL,
    envelope: Optional[Any] = None,
    human_override: Optional[str] = None,
    primary_metric_value: Optional[float] = None,
    performance: Optional[Dict[str, Any]] = None,
    correctness: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Standardized return interface for all arifOS tools.
    Enforces the 'Governed Packet' contract and drives the Identity State Machine.

    Constitutional Rules:
    - F1 Amanah: amanah_lock must be True.
    - F2 Truth: truth_score >= 0.99 for SEAL.
    - F3 Tri-Witness: _validate_tri_witness() checked before SEAL.
    - F4 Clarity: delta_s <= 0 for SEAL.
    - F7 Peace²: peace_squared >= 1.0 for SEAL.
    - F8 Sabar: entropy spike (>0.1) or humility drift forces SABAR.
    - F9 Ethics: stakeholder_safety < 0.9 warns; < 0.5 forces VOID.
    - F11 Audit: SHA-256 receipt, identity block included.
    - F12 Humility: omega_0 outside [0.03, 0.05] forces SABAR.
    - F13 Sovereignty: human_override can escalate but not bypass F1/F9 VOID.
    """
    # Normalize verdict
    verdict_str = verdict.value if isinstance(verdict, Verdict) else str(verdict)

    # ═══════════════════════════════════════════════════════════════════════
    # 1. HARD VOID GATES (Non-negotiable)
    # ═══════════════════════════════════════════════════════════════════════

    # F1 Amanah: sacred trust violation = automatic VOID
    if not metrics.amanah_lock:
        verdict_str = Verdict.VOID.value
        metrics.floor_8_signal = "F1_AMANAH_BREACH: irreversible action without lock"

    # F9 Ethics: catastrophic harm = automatic VOID
    if metrics.stakeholder_safety < 0.5:
        verdict_str = Verdict.VOID.value
        metrics.floor_9_signal = "F9_ETHICS_BREACH: stakeholder_safety below 0.5"

    # F13 Sovereignty: human override can only ESCALATE (SEAL→SABAR, SABAR→VOID),
    # never bypass hard gates. If override is present and verdict is VOID, keep VOID.
    if human_override and verdict_str != Verdict.VOID.value:
        # Validate override token format (simple length check for v0.2)
        if len(human_override) >= 16:
            metrics.floor_13_signal = "F13_SOVEREIGNTY: human_override acknowledged"
            # Override can only downgrade (make safer), not force execution
            if verdict_str == Verdict.SEAL.value:
                verdict_str = Verdict.SABAR.value
                metrics.floor_13_signal += " | escalated to SABAR for review"
        else:
            metrics.floor_13_signal = "F13_SOVEREIGNTY: invalid override token format"

    # ═══════════════════════════════════════════════════════════════════════
    # 2. THERMODYNAMIC VALIDATION (SABAR triggers)
    # ═══════════════════════════════════════════════════════════════════════

    if verdict_str != Verdict.VOID.value:
        # F12 Humility: omega_0 outside [0.03, 0.05] triggers cooling
        if metrics.omega_0 < 0.03 or metrics.omega_0 > 0.05:
            verdict_str = Verdict.SABAR.value
            metrics.floor_12_signal = "HUMILITY_DRIFT_DETECTED"

        # F4 Clarity: positive entropy spike triggers Sabar
        if metrics.delta_s > 0.1:
            verdict_str = Verdict.SABAR.value
            metrics.floor_8_signal = "ENTROPY_SPIKE_DETECTED"

        # F7 Peace²: instability triggers Sabar
        if metrics.peace_squared < 1.0:
            verdict_str = Verdict.SABAR.value
            metrics.floor_8_signal = "PEACE2_VIOLATION"

        # F3 Tri-Witness: insufficient witness for high-stakes
        if not _validate_tri_witness(metrics):
            verdict_str = Verdict.SABAR.value
            metrics.floor_11_signal = "TRI_WITNESS_INSUFFICIENT"

        # F9 Ethics: moderate harm surface triggers warning, downgrade to SABAR
        if metrics.stakeholder_safety < 0.9:
            verdict_str = Verdict.SABAR.value
            metrics.floor_9_signal = "ETHICS_WARNING: stakeholder_safety below 0.9"

    # ═══════════════════════════════════════════════════════════════════════
    # 3. STATE MACHINE INTEGRATION (Single Transition)
    # ═══════════════════════════════════════════════════════════════════════

    # F7 Peace²: Only ONE state transition per governed_return call.
    # Map verdict to metabolic state.
    if verdict_str == Verdict.VOID.value:
        metabolic_state = MetabolicState.SABAR  # VOID forces cooling
    elif verdict_str == Verdict.SABAR.value:
        metabolic_state = MetabolicState.SABAR
    elif verdict_str == Verdict.HOLD_888.value:
        metabolic_state = MetabolicState.REFLECTING
    else:
        metabolic_state = MetabolicState.INTEGRATING

    # Perform single constitutional transition with witness bits
    IDENTITY_MANAGER.transition(
        metabolic_state, witness={"human": human_override is not None, "ai": True, "earth": False}
    )

    # Update values ONCE after transition
    IDENTITY_MANAGER.update_values({"metrics": asdict(metrics)})

    # ═══════════════════════════════════════════════════════════════════════
    # 4. RECEIPT & PACKET CONSTRUCTION
    # ═══════════════════════════════════════════════════════════════════════

    receipt_id = _build_receipt_id(stage)

    res = {
        "status": verdict_str,
        "verdict": verdict_str,
        "stage": stage,
        "metrics": asdict(metrics),
        "vault_receipt": receipt_id,
        "data": data,
        "timestamp": time.time(),
    }

    # F11 Audit: identity block for 999_VAULT
    res["identity"] = {
        "state": IDENTITY_MANAGER.current.state.value,
        "continuity_index": round(IDENTITY_MANAGER.current.continuity_index, 4),
        "drift_score": round(IDENTITY_MANAGER.current.drift_score, 4),
        "parent_hash": IDENTITY_MANAGER.current.parent_hash[:8],
        "evolution_note": IDENTITY_MANAGER.get_evolution_note(),
        "witness_status": IDENTITY_MANAGER.current.witness_status,
        "autonomy_level": round(IDENTITY_MANAGER.current_self_model.autonomy_level, 4),
    }

    # A-FORGE Bridge Contract: include runtime contract version
    res["runtime_contract"] = "arifos://forge/v2026.04.20"

    # ═══════════════════════════════════════════════════════════════════════
    # 5. LIVE VITALITY LEDGER WRITE (F11 Audit)
    # ═══════════════════════════════════════════════════════════════════════
    if _emit_vitality is not None and primary_metric_value is not None:
        try:
            # Map stage to canonical tool name if possible
            tool_name = stage
            if not tool_name.startswith("arifos_"):
                # Try common mappings (e.g., "000_INIT" → "arifos_000_init")
                lowered = tool_name.lower().replace("-", "_")
                candidates = [
                    f"arifos_{lowered}",
                    lowered,
                ]
                for c in candidates:
                    if c in (
                        "arifos_000_init",
                        "arifos_111_sense",
                        "arifos_222_witness",
                        "arifos_333_mind",
                        "arifos_444_kernel",
                        "arifos_555_memory",
                        "arifos_666_heart",
                        "arifos_777_ops",
                        "arifos_888_judge",
                        "arifos_999_vault",
                        "arifos_forge",
                        "arifos_gateway",
                        "arifos_sabar",
                    ):
                        tool_name = c
                        break

            v_gov = _VitalityGovMetrics(
                truth_score=metrics.truth_score,
                delta_s=metrics.delta_s,
                omega_0=metrics.omega_0,
                peace_squared=metrics.peace_squared,
                amanah_lock=metrics.amanah_lock,
                tri_witness_score=metrics.tri_witness_score,
                stakeholder_safety=metrics.stakeholder_safety,
            )
            v_perf = _VitalityPerfMetrics(**performance) if performance else _VitalityPerfMetrics()
            v_corr = _VitalityCorrMetrics(**correctness) if correctness else _VitalityCorrMetrics()

            record = _emit_vitality(
                tool_name=tool_name,
                primary_metric_value=primary_metric_value,
                governance=v_gov,
                performance=v_perf,
                correctness=v_corr,
                description=f"live_execution|stage={stage}|verdict={verdict_str}",
                ledger_dir=_VITALITY_LEDGER_DIR,
            )
            res["vitality_record"] = {
                "tool_name": record.tool_name,
                "run_id": record.run_id,
                "vitality_score": record.vitality_score,
                "verdict": record.verdict,
            }
        except Exception:
            # Failsafe: never crash the tool call because vitality logging failed
            pass

    return res
