"""
arifOS APEX PRIME (Ψ) — Stage 888 Judge (v53.0-HARDENED)

APEX PRIME is the sole authority for constitutional verdict decisions.
It strictly enforces the Trinity of Verdicts:
1. SABAR (Wait/Block) - Hypervisor or Tri-Witness issues
2. VOID (Stop) - Hard Constitutional Violations
3. SEAL (Proceed) - Approved (Clean or Conditional)

Public API (stability contract):
- `APEXPrime.judge_output(...)` for tool-level judgments.
- `APEXPrime.check(metrics, ...)` for metrics-only evaluation.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

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

APEX_VERSION = "v53.0-HARDENED-TRINITY"
APEX_EPOCH = 53


def normalize_verdict_code(verdict_str: str) -> str:
    """Normalize verdict strings to canonical 3-state form."""
    if not verdict_str:
        return "VOID"

    v_upper = verdict_str.upper().strip()
    
    # Map legacy -> New Trinity
    if v_upper in ("SEAL", "SEALED", "PARTIAL"):
        return "SEAL"
    if v_upper in ("SABAR", "888_HOLD", "HOLD_888", "HOLD"):
        return "SABAR"
    if v_upper in ("VOID", "VOIDED", "SUNSET"):
        return "VOID"
        
    return "VOID"  # Default safe fallback


def _floor_scalar(value: Any) -> float:
    """Extract a numeric scalar from mixed floor/result shapes."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
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
    if verdict == Verdict.SEAL:
        if genius_index >= 0.85:
            return {"tier": "L5_ETERNAL", "hold_hours": 0}
        return {"tier": "L4_MONTHLY", "hold_hours": 0}
        
    if verdict == Verdict.SABAR:
        return {"tier": "L3_WEEKLY", "hold_hours": 24 * 7}
        
    # VOID
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
        """Compute p(truth) per canonical exponential form."""
        entropy_gain = max(0.0, -float(delta_s))
        x = max(0.0, float(alpha) * float(evidence_ratio) * entropy_gain * float(tri_witness))
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
                "Empathy",
                KAPPA_R_THRESHOLD,
                float(metrics.kappa_r),
                float(metrics.kappa_r) >= KAPPA_R_THRESHOLD,
                is_hard=False,
            ),
            FloorCheckResult(
                "F5",
                "Humility",
                OMEGA_0_MIN,
                float(metrics.omega_0),
                OMEGA_0_MIN <= float(metrics.omega_0) <= OMEGA_0_MAX,
                is_hard=True,
            ),
            FloorCheckResult(
                "F6",
                "Clarity",
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

        # Hard Floors
        if float(metrics.truth) < truth_threshold:
            failed.append("F2(truth)")
        if not metrics.amanah:
            failed.append("F1(amanah)")
        if float(metrics.delta_s) > DELTA_S_THRESHOLD:
            failed.append("F6(clarity)")
        if not (OMEGA_0_MIN <= float(metrics.omega_0) <= OMEGA_0_MAX):
            failed.append("F5(humility)")
        if not metrics.anti_hantu:
            failed.append("F9(anti-hantu)")
        if not metrics.rasa:
            failed.append("F7(rasa)")

        # High Stakes -> Hard if failed
        tri_ok = float(metrics.tri_witness) >= self.tri_witness_threshold
        if self.high_stakes and not tri_ok:
            failed.append("F8(tri_witness)")
        elif not tri_ok:
            warnings.append("F8(tri_witness)")

        # Soft Floors
        if float(metrics.peace_squared) < PEACE_SQUARED_THRESHOLD:
            warnings.append("F3(peace)")
        if float(metrics.kappa_r) < KAPPA_R_THRESHOLD:
            warnings.append("F4(empathy)")

        all_pass = len(failed) == 0 and len(warnings) == 0
        
        # 3-State Verdict Map
        if failed:
            verdict = "VOID"
        elif all_pass:
            verdict = "SEAL"
        else:
            verdict = "SEAL"  # Conditional pass for warnings in metrics check

        return FloorsVerdict(
            verdict=verdict,
            passed_floors=["F1"], # Simplified, caller relies on failed list
            failed_floors=failed,
            reason=f"Failed: {failed}, Warnings: {warnings}" if failed or warnings else "All Pass"
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
        """Issue an ApexVerdict (3-State) from Metrics."""
        floors = self.check(metrics, lane=lane)
        
        sub_verdict = None
        
        # 1. Check Blocking Conditions
        if eye_blocking:
            verdict = Verdict.SABAR  # Re-classified as Block from VOID
            sub_verdict = "EYE_BLOCK"
            reason = "SABAR: @EYE blocking issue"
        
        # 2. Check Hard Failures
        elif floors.verdict == "VOID":
            verdict = Verdict.VOID
            sub_verdict = "HARD_FAIL"
            reason = f"VOID: {floors.reason}"
            
        # 3. Check p(truth) -> SABAR if low
        else:
            evidence_ratio = float((context or {}).get("evidence_ratio", 1.0))
            p_truth = self.compute_p_truth(
                truth=float(metrics.truth),
                delta_s=float(metrics.delta_s),
                tri_witness=float(metrics.tri_witness),
                evidence_ratio=evidence_ratio,
                alpha=self.p_truth_alpha,
            )
            
            if p_truth < self.p_truth_min:
                verdict = Verdict.SABAR
                sub_verdict = "LOW_CONFIDENCE"
                reason = f"SABAR: p(truth)={p_truth:.3f}<{self.p_truth_min}"
            else:
                verdict = Verdict.SEAL
                if "Warning" in floors.reason:
                    sub_verdict = "CONDITIONAL"
                    reason = f"SEAL (Conditional): {floors.reason}"
                else:
                    reason = "SEAL: All Pass"

        return self._build_verdict(
            verdict, query, response, user_id, metrics, reason, sub_verdict, sub_verdict == "LOW_CONFIDENCE"
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
        """Stage 888: 3-State Verdict Logic (SEAL, SABAR, VOID)."""
        ctx: Dict[str, Any] = dict(context or {})
        
        # 1. Metrics & Hard/Soft Checks
        metrics = self._metrics_from_floor_results(agi_results, asi_results)
        floors = self.check(metrics, lane=str(ctx.get("lane", "SOFT")))
        
        # 2. Hypervisor Checks (F10-F13)
        v10 = validate_f10_ontology(f"{query}\n{response}")
        v12 = validate_f12_injection_defense(query)
        v13 = validate_f13_curiosity(query, {"response": response})
        
        hypervisor_block = False
        hypervisor_reasons = []
        
        if not v10["pass"]:
            hypervisor_block = True
            hypervisor_reasons.append("F10(Ontology)")
        if not v12["pass"]:
            hypervisor_block = True
            hypervisor_reasons.append(f"F12(Injection:{v12.get('score')})")

        # 3. Decision Logic
        verdict = Verdict.VOID
        sub_verdict = None
        reason = ""
        
        # A. SABAR: Hypervisor Block
        if hypervisor_block:
            verdict = Verdict.SABAR
            sub_verdict = "HYPERVISOR_BLOCK"
            reason = f"SABAR: Hypervisor Block ({', '.join(hypervisor_reasons)})"

        # B. VOID: Hard Floor Failure
        elif floors.verdict == "VOID":
            verdict = Verdict.VOID
            sub_verdict = "CONSTITUTIONAL_VIOLATION"
            reason = f"VOID: {floors.reason}"

        # C. SABAR: Tri-Witness / High Stakes
        elif self.high_stakes and float(metrics.tri_witness) < self.tri_witness_threshold:
            verdict = Verdict.SABAR
            sub_verdict = "WITNESS_HOLD"
            reason = f"SABAR: Tri-Witness {metrics.tri_witness:.2f}<{self.tri_witness_threshold}"

        # D. SABAR: Low p(truth)
        else:
            evidence_ratio = float(ctx.get("evidence_ratio", 1.0))
            p_truth = self.compute_p_truth(
                truth=float(metrics.truth),
                delta_s=float(metrics.delta_s),
                tri_witness=float(metrics.tri_witness),
                evidence_ratio=evidence_ratio,
                alpha=self.p_truth_alpha,
            )
            
            if p_truth < self.p_truth_min:
                verdict = Verdict.SABAR
                sub_verdict = "LOW_CONFIDENCE"
                reason = f"SABAR: p(truth)={p_truth:.3f}<{self.p_truth_min}"
            
            # E. SEAL: Conditional or Clean
            else:
                verdict = Verdict.SEAL
                if "Warning" in (floors.reason or ""):
                    sub_verdict = "CONDITIONAL"
                    reason = f"SEAL (Conditional): {floors.reason}"
                else:
                    reason = "SEAL: All Pass"

        return self._build_verdict(
            verdict, query, response, user_id, metrics, reason, sub_verdict, False
        )

    def _build_verdict(
        self,
        verdict: Verdict,
        query: str,
        response: str,
        user_id: Optional[str],
        metrics: Metrics,
        reason: str,
        sub_verdict: Optional[str],
        is_p_truth_fail: bool
    ) -> ApexVerdict:
        """Helper to construct ApexVerdict."""
        genius_index = float(metrics.truth)
        cooling = _phoenix_tier_for(verdict, genius_index)
        
        p_truth = 1.0 # default
        if is_p_truth_fail:
             # re-calc or just pass 0 for simplicity in this helper context
             p_truth = 0.0 

        proof_hash = _sha256_hex(
            json.dumps(
                {
                    "query": query,
                    "response": response,
                    "verdict": verdict.value,
                    "sub": sub_verdict,
                    "v": APEX_VERSION
                },
                default=str,
                sort_keys=True
            ).encode("utf-8")
        )

        return ApexVerdict(
            verdict=verdict,
            pulse=float(metrics.psi) if metrics.psi else 1.0,
            reason=reason,
            violated_floors=[], # Populated by caller if needed, omitted for speed here
            compass_alignment={},
            genius_stats={"truth": float(metrics.truth)},
            proof_hash=proof_hash,
            cooling_metadata=cooling,
            sub_verdict=sub_verdict
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

