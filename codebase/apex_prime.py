"""
arifOS APEX PRIME (Ψ) — Stage 888 Judge (v52.1 APEX-ROOM)

APEX PRIME is the sole authority for constitutional verdict decisions.

Public API (stability contract):
- `APEXPrime.judge_output(...)` for tool-level judgments (AGI/ASI floor bundles).
- `APEXPrime.check(metrics, ...)` + `check_floors(metrics, ...)` for metrics-only evaluation.
- `apex_review(...)` legacy convenience wrapper.

This module is intentionally conservative:
- Hard floor failure => VOID
- p(truth) below threshold => SABAR
- Soft floor failure => PARTIAL
- Tri-witness dissent (high-stakes) => 888_HOLD
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

from codebase.enforcement import (
    validate_f10_ontology,
    validate_f12_injection_defense,
    validate_f13_curiosity,
)
from codebase.constants import (
    DELTA_S_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MAX,
    OMEGA_0_MIN,
    PEACE_SQUARED_THRESHOLD,
    TRI_WITNESS_THRESHOLD,
    TRUTH_THRESHOLD,
    FloorsVerdict,
    get_lane_truth_threshold,
)

from .types import ApexVerdict, FloorCheckResult, Metrics, Verdict

APEX_VERSION = "v52.1-APEX888"
APEX_EPOCH = 52


def normalize_verdict_code(verdict_str: str) -> str:
    """Normalize verdict strings to canonical form."""
    if not verdict_str:
        return "VOID"

    verdict_upper = verdict_str.upper().strip()
    verdict_map = {
        "SEAL": "SEAL",
        "SEALED": "SEAL",
        "SABAR": "SABAR",
        "VOID": "VOID",
        "VOIDED": "VOID",
        "PARTIAL": "PARTIAL",
        "888_HOLD": "888_HOLD",
        "888-HOLD": "888_HOLD",
        "HOLD_888": "888_HOLD",
        "HOLD-888": "888_HOLD",
        "HOLD": "888_HOLD",
        "SUNSET": "SUNSET",
    }
    return verdict_map.get(verdict_upper, verdict_upper)


def _floor_scalar(value: Any) -> float:
    """Extract a numeric scalar from mixed floor/result shapes."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    # Support both dataclass variants in the repo:
    # - system.types.FloorCheckResult(value=...)
    # - enforcement.metrics.FloorCheckResult(actual=...)
    for attr in ("value", "actual", "score"):
        if hasattr(value, attr):
            v = getattr(value, attr)
            if isinstance(v, (int, float)):
                return float(v)
    return 0.0


def _floor_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    for attr in ("passed", "ok"):
        if hasattr(value, attr):
            v = getattr(value, attr)
            if isinstance(v, bool):
                return v
    return default


def _sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _phoenix_tier_for(verdict: Verdict, genius_index: float) -> Dict[str, Any]:
    """Assign Phoenix-72 cooling tier (L0-L5) as metadata."""
    if verdict == Verdict.SEAL and genius_index >= 0.85:
        return {"tier": "L5_ETERNAL", "hold_hours": 0}
    if verdict == Verdict.SEAL:
        return {"tier": "L4_MONTHLY", "hold_hours": 0}
    if verdict == Verdict.PARTIAL:
        return {"tier": "L4_MONTHLY", "hold_hours": 24 * 30}
    if verdict == Verdict.SABAR:
        return {"tier": "L3_WEEKLY", "hold_hours": 24 * 7}
    if verdict == Verdict.HOLD_888:
        return {"tier": "L2_PHOENIX", "hold_hours": 72}
    return {"tier": "L2_PHOENIX", "hold_hours": 72}


class APEXPrime:
    """APEX PRIME — constitutional judge (Stage 888)."""

    def __init__(
        self,
        high_stakes: bool = False,
        tri_witness_threshold: float = TRI_WITNESS_THRESHOLD,
        p_truth_alpha: float = 25.0,
        p_truth_min: float = 0.99,
    ) -> None:
        self.high_stakes = high_stakes
        self.tri_witness_threshold = tri_witness_threshold
        self.p_truth_alpha = p_truth_alpha
        self.p_truth_min = p_truth_min

    @staticmethod
    def compute_p_truth(
        *,
        truth: float,
        delta_s: float,
        tri_witness: float,
        evidence_ratio: float = 1.0,
        alpha: float = 25.0,
        epsilon: float = 1.0e-9,
    ) -> float:
        """Compute p(truth) per canonical exponential form.

        p(truth) = 1 - exp(-α * (E/E) * (-ΔS) * TW)

        Notes:
        - This implementation treats ΔS<=0 as "entropy non-increasing" (good).
        - If ΔS is positive, (-ΔS) becomes negative and p(truth) is clamped at 0.
        """
        entropy_gain = max(0.0, -float(delta_s))
        x = max(0.0, float(alpha) * float(evidence_ratio) * entropy_gain * float(tri_witness))
        # 1 - exp(-x) is stable for small x; clamp to [0,1].
        p = 1.0 - math.exp(-max(epsilon, x))
        return max(0.0, min(1.0, p))

    def _metrics_from_floor_results(
        self,
        agi_results: Iterable[Any],
        asi_results: Iterable[Any],
    ) -> Metrics:
        """Derive Metrics from floor results (best-effort)."""
        truth = 1.0
        delta_s = 0.0
        peace_squared = 1.0
        kappa_r = 1.0
        omega_0 = 0.04
        amanah = True
        tri_witness = 0.95
        rasa = True
        anti_hantu = True

        for f in list(agi_results) + list(asi_results):
            fid = getattr(f, "floor_id", "")
            if fid == "F2":
                truth = _floor_scalar(f)
            elif fid == "F6":
                delta_s = _floor_scalar(f)
            elif fid == "F3":
                peace_squared = _floor_scalar(f)
            elif fid == "F4":
                kappa_r = _floor_scalar(f)
            elif fid == "F5":
                omega_0 = _floor_scalar(f)
            elif fid == "F1":
                amanah = _floor_bool(f)
            elif fid == "F8":
                tri_witness = _floor_scalar(f)
            elif fid == "F7":
                rasa = _floor_bool(f)
            elif fid == "F9":
                anti_hantu = _floor_bool(f)

        return Metrics(
            truth=truth,
            delta_s=delta_s,
            peace_squared=peace_squared,
            kappa_r=kappa_r,
            omega_0=omega_0,
            amanah=amanah,
            tri_witness=tri_witness,
            rasa=rasa,
            anti_hantu=anti_hantu,
        )

    def _floor_results_from_metrics(self, metrics: Metrics, lane: str) -> List[FloorCheckResult]:
        truth_threshold = get_lane_truth_threshold(lane)
        return [
            FloorCheckResult("F1", "Amanah", 1.0, 1.0 if metrics.amanah else 0.0, metrics.amanah, is_hard=True),
            FloorCheckResult(
                "F2",
                "Truth",
                truth_threshold,
                float(metrics.truth),
                float(metrics.truth) >= truth_threshold,
                is_hard=True,
            ),
            FloorCheckResult(
                "F3",
                "Peace²",
                PEACE_SQUARED_THRESHOLD,
                float(metrics.peace_squared),
                float(metrics.peace_squared) >= PEACE_SQUARED_THRESHOLD,
                is_hard=False,
            ),
            FloorCheckResult(
                "F4",
                "Empathy (κᵣ)",
                KAPPA_R_THRESHOLD,
                float(metrics.kappa_r),
                float(metrics.kappa_r) >= KAPPA_R_THRESHOLD,
                is_hard=False,
            ),
            FloorCheckResult(
                "F5",
                "Humility (Ω₀)",
                OMEGA_0_MIN,
                float(metrics.omega_0),
                OMEGA_0_MIN <= float(metrics.omega_0) <= OMEGA_0_MAX,
                is_hard=True,
            ),
            FloorCheckResult(
                "F6",
                "Clarity (ΔS)",
                DELTA_S_THRESHOLD,
                float(metrics.delta_s),
                float(metrics.delta_s) <= DELTA_S_THRESHOLD,
                is_hard=True,
            ),
            FloorCheckResult("F7", "RASA", 1.0, 1.0 if metrics.rasa else 0.0, bool(metrics.rasa), is_hard=True),
            FloorCheckResult(
                "F8",
                "Tri-Witness",
                self.tri_witness_threshold,
                float(metrics.tri_witness),
                float(metrics.tri_witness) >= self.tri_witness_threshold,
                is_hard=self.high_stakes,
            ),
            FloorCheckResult(
                "F9",
                "Anti-Hantu",
                1.0,
                1.0 if metrics.anti_hantu else 0.0,
                bool(metrics.anti_hantu),
                is_hard=True,
            ),
        ]

    def check(self, metrics: Metrics, lane: str = "SOFT") -> FloorsVerdict:
        """Evaluate floor pass/fail from a Metrics object."""
        truth_threshold = get_lane_truth_threshold(lane)

        failed: List[str] = []
        warnings: List[str] = []

        truth_ok = float(metrics.truth) >= truth_threshold
        if not truth_ok:
            failed.append(f"F2(truth={metrics.truth:.3f}<{truth_threshold:.2f})")

        amanah_ok = bool(metrics.amanah)
        if not amanah_ok:
            failed.append("F1(amanah)")

        delta_s_ok = float(metrics.delta_s) <= DELTA_S_THRESHOLD
        if not delta_s_ok:
            failed.append(f"F6(delta_s={metrics.delta_s:.3f}>{DELTA_S_THRESHOLD:.2f})")

        omega_ok = OMEGA_0_MIN <= float(metrics.omega_0) <= OMEGA_0_MAX
        if not omega_ok:
            failed.append(f"F5(omega_0={metrics.omega_0:.3f} not in [{OMEGA_0_MIN:.2f},{OMEGA_0_MAX:.2f}])")

        anti_hantu_ok = bool(metrics.anti_hantu)
        if not anti_hantu_ok:
            failed.append("F9(anti_hantu)")

        rasa_ok = bool(metrics.rasa)
        if not rasa_ok:
            failed.append("F7(rasa)")

        tri_ok = float(metrics.tri_witness) >= self.tri_witness_threshold
        if self.high_stakes and not tri_ok:
            failed.append(f"F8(tri_witness={metrics.tri_witness:.3f}<{self.tri_witness_threshold:.2f})")

        peace_ok = float(metrics.peace_squared) >= PEACE_SQUARED_THRESHOLD
        if not peace_ok:
            warnings.append(f"F3(peace_squared={metrics.peace_squared:.3f}<{PEACE_SQUARED_THRESHOLD:.2f})")

        kappa_ok = float(metrics.kappa_r) >= KAPPA_R_THRESHOLD
        if not kappa_ok:
            warnings.append(f"F4(kappa_r={metrics.kappa_r:.3f}<{KAPPA_R_THRESHOLD:.2f})")

        all_pass = len(failed) == 0 and len(warnings) == 0 and (tri_ok or not self.high_stakes)
        verdict = "SEAL" if all_pass else ("VOID" if len(failed) else "PARTIAL")
        return FloorsVerdict(
            all_pass=all_pass,
            failed_floors=failed,
            warnings=warnings,
            metrics=metrics,
            lane=lane,
            verdict=verdict,
        )

    def judge(
        self,
        metrics: Metrics,
        *,
        lane: str = "SOFT",
        query: str = "",
        response: str = "",
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        eye_blocking: bool = False,
    ) -> ApexVerdict:
        """Issue an ApexVerdict from a Metrics-only input (legacy-compatible)."""
        floors = self.check(metrics, lane=lane)
        violated_floors = [f.split("(", 1)[0] for f in floors.failed_floors] + [
            f.split("(", 1)[0] for f in floors.warnings
        ]

        if eye_blocking:
            verdict = Verdict.VOID
            reason = "VOID: @EYE blocking issue"
        elif not floors.hard_ok:
            verdict = Verdict.VOID
            reason = f"VOID: Hard floor violations ({', '.join(floors.failed_floors)})"
        elif floors.warnings:
            verdict = Verdict.PARTIAL
            reason = f"PARTIAL: Soft floor warnings ({', '.join(floors.warnings)})"
        else:
            verdict = Verdict.SEAL
            reason = "SEAL: Metrics pass"

        evidence_ratio = float((context or {}).get("evidence_ratio", 1.0))
        p_truth = self.compute_p_truth(
            truth=float(metrics.truth),
            delta_s=float(metrics.delta_s),
            tri_witness=float(metrics.tri_witness),
            evidence_ratio=evidence_ratio,
            alpha=self.p_truth_alpha,
        )

        if verdict == Verdict.SEAL and p_truth < self.p_truth_min:
            verdict = Verdict.SABAR
            reason = f"SABAR: p(truth)={p_truth:.3f}<{self.p_truth_min:.2f}"

        genius_index = float(metrics.truth)  # minimal, deterministic proxy
        cooling = _phoenix_tier_for(verdict, genius_index)

        proof_hash = _sha256_hex(
            json.dumps(
                {
                    "query": query,
                    "response": response,
                    "user_id": user_id,
                    "metrics": asdict(metrics),
                    "verdict": verdict.value,
                    "p_truth": p_truth,
                },
                sort_keys=True,
                default=str,
            ).encode("utf-8")
        )

        return ApexVerdict(
            verdict=verdict,
            pulse=float(metrics.psi) if metrics.psi is not None else 1.0,
            reason=reason,
            violated_floors=violated_floors,
            compass_alignment={},
            genius_stats={
                "p_truth": p_truth,
                "truth": float(metrics.truth),
                "delta_s": float(metrics.delta_s),
                "peace_squared": float(metrics.peace_squared),
                "kappa_r": float(metrics.kappa_r),
                "omega_0": float(metrics.omega_0),
                "tri_witness": float(metrics.tri_witness),
            },
            proof_hash=proof_hash,
            cooling_metadata=cooling,
        )

    def judge_output(
        self,
        query: str,
        response: str,
        agi_results: List[Any],
        asi_results: List[Any],
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ApexVerdict:
        """Stage 888: issue verdict from AGI+ASI floor bundles."""
        ctx: Dict[str, Any] = dict(context or {})
        ctx.setdefault("user_id", user_id)
        ctx.setdefault("response", response)

        # Derive core metrics from floor results first.
        metrics = self._metrics_from_floor_results(agi_results, asi_results)

        # Add hypervisor-style checks (F10-F13 family).
        extra_floors: List[FloorCheckResult] = []

        # F10 Ontology (HARD)
        v10 = validate_f10_ontology(f"{query}\n{response}")
        extra_floors.append(
            FloorCheckResult("F10", "Ontology", 1.0, 1.0 if v10["pass"] else 0.0, bool(v10["pass"]), is_hard=True)
        )

        # F12 Injection Defense (HARD)
        v12 = validate_f12_injection_defense(query)
        extra_floors.append(
            FloorCheckResult(
                "F12",
                "Injection Defense",
                0.85,
                float(v12.get("score", 1.0)),
                bool(v12["pass"]),
                is_hard=True,
                reason=v12.get("reason", ""),
            )
        )

        # F13 Curiosity (SOFT)
        v13 = validate_f13_curiosity(query, {"response": response})
        extra_floors.append(
            FloorCheckResult(
                "F13",
                "Curiosity",
                0.85,
                float(v13.get("score", 0.0)),
                bool(v13["pass"]),
                is_hard=False,
                reason=v13.get("reason", ""),
            )
        )

        lane = str(ctx.get("lane", "SOFT"))
        floors = self._floor_results_from_metrics(metrics, lane=lane)
        all_floor_results: List[FloorCheckResult] = [*floors, *extra_floors]

        hard_failed = [f for f in all_floor_results if f.is_hard and not f.passed]
        soft_failed = [f for f in all_floor_results if (not f.is_hard) and not f.passed]

        p_truth = self.compute_p_truth(
            truth=float(metrics.truth),
            delta_s=float(metrics.delta_s),
            tri_witness=float(metrics.tri_witness),
            evidence_ratio=float(ctx.get("evidence_ratio", 1.0)),
            alpha=self.p_truth_alpha,
        )

        if hard_failed:
            verdict = Verdict.VOID
            reason = f"VOID: Hard floor failure ({', '.join(f.floor_id for f in hard_failed)})"
        elif self.high_stakes and float(metrics.tri_witness) < self.tri_witness_threshold:
            verdict = Verdict.HOLD_888
            reason = f"888_HOLD: Tri-Witness {metrics.tri_witness:.3f}<{self.tri_witness_threshold:.2f}"
        elif p_truth < self.p_truth_min:
            verdict = Verdict.SABAR
            reason = f"SABAR: p(truth)={p_truth:.3f}<{self.p_truth_min:.2f}"
        elif soft_failed:
            verdict = Verdict.PARTIAL
            reason = f"PARTIAL: Soft floor failure ({', '.join(f.floor_id for f in soft_failed)})"
        else:
            verdict = Verdict.SEAL
            reason = "SEAL: All floors pass"

        genius_index = float(metrics.truth)
        cooling = _phoenix_tier_for(verdict, genius_index)

        proof_hash = _sha256_hex(
            json.dumps(
                {
                    "query": query,
                    "response": response,
                    "user_id": user_id,
                    "floors": [asdict(f) for f in all_floor_results],
                    "verdict": verdict.value,
                    "p_truth": p_truth,
                    "apex_version": APEX_VERSION,
                },
                sort_keys=True,
                default=str,
            ).encode("utf-8")
        )

        compass_alignment = {f.floor_id: f.passed for f in all_floor_results if f.floor_id.startswith("F")}
        violated_floors = [f.floor_id for f in all_floor_results if not f.passed]

        return ApexVerdict(
            verdict=verdict,
            pulse=float(metrics.psi) if metrics.psi is not None else 1.0,
            reason=reason,
            violated_floors=violated_floors,
            compass_alignment=compass_alignment,
            genius_stats={
                "p_truth": p_truth,
                "truth": float(metrics.truth),
                "delta_s": float(metrics.delta_s),
                "peace_squared": float(metrics.peace_squared),
                "kappa_r": float(metrics.kappa_r),
                "omega_0": float(metrics.omega_0),
                "tri_witness": float(metrics.tri_witness),
            },
            proof_hash=proof_hash,
            cooling_metadata=cooling,
        )


def check_floors(metrics: Metrics, *, lane: str = "SOFT", high_stakes: bool = False) -> FloorsVerdict:
    """Standalone floor check (legacy import path)."""
    prime = APEXPrime(high_stakes=high_stakes)
    return prime.check(metrics, lane=lane)


def apex_review(
    *,
    query: str,
    response: str,
    lane: str = "SOFT",
    user_id: Optional[str] = None,
    metrics: Metrics,
    context: Optional[Dict[str, Any]] = None,
    eye_blocking: bool = False,
    high_stakes: Optional[bool] = None,
) -> ApexVerdict:
    """Legacy wrapper: judge a response using Metrics (v52-compatible signature)."""
    hs = bool(high_stakes) if high_stakes is not None else (lane.upper() == "HARD")
    prime = APEXPrime(high_stakes=hs)
    return prime.judge(
        metrics,
        lane=lane,
        query=query,
        response=response,
        user_id=user_id,
        context=context,
        eye_blocking=eye_blocking,
    )


__all__ = [
    "APEXPrime",
    "ApexVerdict",
    "Verdict",
    "Metrics",
    "FloorCheckResult",
    "FloorsVerdict",
    "APEX_VERSION",
    "APEX_EPOCH",
    "normalize_verdict_code",
    "check_floors",
    "apex_review",
]

