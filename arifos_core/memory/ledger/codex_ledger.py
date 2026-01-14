"""
Codex CLI ledger integration - v35Ω-compatible append-only logging.

Builds Metrics from floor audits and logs via log_cooling_entry with
non-breaking Codex metadata. Uses SHA3-256 hash chaining from the
existing Cooling Ledger writer.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from arifos_core.enforcement.metrics import (
    KAPPA_R_THRESHOLD,
    Metrics,
    OMEGA_0_MAX,
    OMEGA_0_MIN,
    PEACE_SQUARED_THRESHOLD,
    TRI_WITNESS_THRESHOLD,
    TRUTH_THRESHOLD,
)
from arifos_core.memory.cooling_ledger import DEFAULT_LEDGER_PATH, log_cooling_entry


def _coerce_float(value: Any, default: float) -> float:
    try:
        if value is None:
            raise ValueError
        return float(value)
    except Exception:
        return float(default)


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"pass", "ok", "true", "yes"}:
            return True
        if lowered in {"fail", "false", "no", "warn", "void"}:
            return False
    return bool(default)


def _build_codex_audit(
    floors: Dict[str, Any],
    risk_score: Optional[float],
    entropy_delta: Optional[float],
    reversible: Optional[bool],
    artifacts: Optional[List[str]],
) -> Dict[str, Any]:
    audit: Dict[str, Any] = {"floors": dict(floors) if isinstance(floors, dict) else {}}
    if risk_score is not None:
        audit["risk_score"] = risk_score
    if entropy_delta is not None:
        audit["entropy_delta"] = entropy_delta
    if reversible is not None:
        audit["reversible"] = reversible
    if artifacts is not None:
        audit["artifacts"] = artifacts
    return audit


def log_codex_cli_entry(
    *,
    floors: Dict[str, Any],
    verdict: str,
    task_type: Optional[str] = None,
    task_description: str = "",
    scope: Optional[str] = None,
    risk_score: Optional[float] = None,
    entropy_delta: Optional[float] = None,
    reversible: Optional[bool] = None,
    artifacts: Optional[List[str]] = None,
    query: Optional[str] = None,
    candidate_output: Optional[str] = None,
    context_summary: str = "Codex CLI task",
    pipeline_path: Optional[List[str]] = None,
    job_id: Optional[str] = None,
    stakes: str = "normal",
    high_stakes: Optional[bool] = None,
    ledger_path: Union[str, Path] = DEFAULT_LEDGER_PATH,
) -> Dict[str, Any]:
    """
    Log a Codex CLI task to the Cooling Ledger using v35Ω schema + Codex metadata.

    Args:
        floors: Floor audit mapping (expects F0-F9 keys).
        verdict: Verdict string (SEAL | PARTIAL | SABAR | VOID | HOLD_888).
        task_type: Task classification (e.g., code_gen, refactor).
        task_description: Human-readable description of the task.
        scope: Target file or scope string.
        risk_score: Optional risk score to capture.
        entropy_delta: Optional entropy delta (negative = entropy reduction).
        reversible: Whether the change set is reversible.
        artifacts: List of related artifacts (e.g., file names).
        query: Optional input/query text.
        candidate_output: Optional output text snippet.
        context_summary: Short summary for ledger context.
        pipeline_path: Pipeline stages; defaults to ["CODEX_CLI"].
        job_id: Optional stable job id; auto-generated UUID if omitted.
        stakes: Stakes class ("normal" or "high").
        high_stakes: Override for tri-witness enforcement if needed.
        ledger_path: Target ledger path (append-only JSONL).
    """

    omega_midpoint = (OMEGA_0_MIN + OMEGA_0_MAX) / 2.0

    metrics = Metrics(
        truth=_coerce_float(floors.get("F2_truth"), TRUTH_THRESHOLD),
        delta_s=_coerce_float(floors.get("F4_delta_s"), 0.0),
        peace_squared=_coerce_float(floors.get("F3_peace2"), PEACE_SQUARED_THRESHOLD),
        kappa_r=_coerce_float(floors.get("F5_kappa_r"), KAPPA_R_THRESHOLD),
        omega_0=_coerce_float(floors.get("F6_omega0"), omega_midpoint),
        amanah=_coerce_bool(floors.get("F1_amanah"), True),
        tri_witness=_coerce_float(floors.get("F8_tri_witness"), TRI_WITNESS_THRESHOLD),
        rasa=_coerce_bool(floors.get("F7_rasa"), True),
        anti_hantu=_coerce_bool(floors.get("F9_anti_hantu"), True),
    )

    codex_audit = _build_codex_audit(
        floors=floors,
        risk_score=risk_score,
        entropy_delta=entropy_delta,
        reversible=reversible,
        artifacts=artifacts,
    )

    entry = log_cooling_entry(
        job_id=job_id or str(uuid.uuid4()),
        verdict=verdict,
        metrics=metrics,
        query=query,
        candidate_output=candidate_output,
        stakes=stakes,
        pipeline_path=pipeline_path or ["CODEX_CLI"],
        context_summary=context_summary,
        ledger_path=ledger_path,
        high_stakes=high_stakes,
        source="CODEX_CLI",
        task_type=task_type,
        task_description=task_description,
        scope=scope,
        codex_audit=codex_audit,
    )

    return entry


__all__ = ["log_codex_cli_entry"]
