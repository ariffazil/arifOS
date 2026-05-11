"""
skills/wealth/score_kernel.py — Constitutional Wealth Score Kernel
═════════════════════════════════════════════════════════════════

Post-AGI capital allocation: verification-first scoring replacing single-axis NPV.

Score formula:
    final_score =
        a * reward_score
      - b * risk_score
      + c * verifiability_score
      + d * liability_clarity_score
      + e * reversibility_bonus
      - f * audit_entropy_penalty
      - g * junior_loop_damage_penalty

Hard rules (coded, not soft):
    if (!floors_passed || entropy_band === "EXTREME"):
        recommendation = "HOLD_CANDIDATE"
    if (anti_hantu_fail || sovereign_veto):
        recommendation = "VOID_CANDIDATE"

Source: arifOS WEALTH + Catalini, Hui & Wu (MIT/WashU/UCLA, February 2026)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Score weights — configurable per deployment class
_A = 0.30  # reward
_B = 0.25  # risk (negative contribution)
_C = 0.20  # verifiability (positive contribution)
_D = 0.15  # liability clarity
_E = 0.05  # reversibility bonus
_F = 0.20  # audit entropy penalty
_G = 0.15  # junior loop damage penalty

# Hard floor thresholds
_MIN_SVS = 0.30  # below this svs → automatic HOLD
_MAX_DELTA_M = 0.80  # above this delta_m → automatic HOLD
_MIN_LIABILITY_SCORE = 0.20  # no liability owner → score = 0 on this axis


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class WealthScore:
    """
    Constitutional capital allocation score — multi-axis, floor-enforced.

    Replaces single-axis NPV with verification-first governance.
    All scores normalized 0-1 unless noted.
    """

    reward_score: float
    risk_score: float
    verifiability_score: float  # svs-derived
    floor_score: float  # 0-1, F1-F13 compliance
    liability_clarity_score: float  # 0-1, liability owner present and solvent
    human_capacity_score: float  # 0-1, apprenticeship pipeline health
    audit_entropy_penalty: float  # delta_m-derived penalty (0-1)
    junior_loop_damage_penalty: float  # (0-1)
    final_score: float
    recommendation: str  # "SEAL_CANDIDATE" | "HOLD_CANDIDATE" | "VOID_CANDIDATE"
    entropy_band: str  # "LOW" | "MEDIUM" | "HIGH" | "EXTREME"
    floor_flags: list[str] = field(default_factory=list)
    hard_blocks: list[str] = field(default_factory=list)
    delta_m: float = 0.0
    svs: float = 1.0
    npv_estimate: float | None = None
    emv_estimate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "reward_score": round(self.reward_score, 4),
            "risk_score": round(self.risk_score, 4),
            "verifiability_score": round(self.verifiability_score, 4),
            "floor_score": round(self.floor_score, 4),
            "liability_clarity_score": round(self.liability_clarity_score, 4),
            "human_capacity_score": round(self.human_capacity_score, 4),
            "audit_entropy_penalty": round(self.audit_entropy_penalty, 4),
            "junior_loop_damage_penalty": round(self.junior_loop_damage_penalty, 4),
            "final_score": round(self.final_score, 4),
            "recommendation": self.recommendation,
            "entropy_band": self.entropy_band,
            "floor_flags": self.floor_flags,
            "hard_blocks": self.hard_blocks,
            "delta_m": round(self.delta_m, 4),
            "svs": round(self.svs, 4),
            "npv_estimate": self.npv_estimate,
            "emv_estimate": self.emv_estimate,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SCORE KERNEL
# ═══════════════════════════════════════════════════════════════════════════════


def wealth_score_kernel(
    reward_score: float | None = None,
    risk_score: float | None = None,
    npv_estimate: float | None = None,
    emv_estimate: float | None = None,
    verifiability_score: float | None = None,  # svs — 0-1
    delta_m: float = 0.0,
    entropy_band: str = "LOW",
    floors_passed: bool = True,
    floor_flags: list[str] | None = None,
    anti_hantu_fail: bool = False,
    sovereign_veto: bool = False,
    liability_owner_present: bool = True,
    liability_score: float = 0.5,
    reversibility_score: float = 0.5,
    junior_loop_status: str = "SAFE",
    human_capacity_score: float = 0.8,
    # Raw audit entropy components (optional — compute from these if verifiability_score not given)
    novelty: float | None = None,
    proxy_distance: float | None = None,
    verifier_scarcity: float | None = None,
    latency_to_ground_truth: float | None = None,
    model_opacity: float | None = None,
    provenance_score: float | None = None,
) -> WealthScore:
    """
    Constitutional score kernel for post-AGI capital allocation.

    Hard gates (coded, not soft):
      1. Floors failed → HOLD
      2. entropy_band == "EXTREME" → HOLD
      3. svs < _MIN_SVS → HOLD
      4. delta_m > _MAX_DELTA_M → HOLD
      5. anti_hantu_fail → VOID
      6. sovereign_veto → VOID

    High reward can NEVER override failed floors or extreme Δm.
    This is the difference between a calculator and a governor.
    """
    # Defaults
    r = max(0.0, min(1.0, reward_score if reward_score is not None else 0.5))
    risk = max(0.0, min(1.0, risk_score if risk_score is not None else 0.5))
    flags = floor_flags or []
    svs = max(
        0.0, min(1.0, verifiability_score if verifiability_score is not None else 1.0)
    )

    # ── Derive audit entropy penalty from Δm ──────────────────────────────────
    entropy_penalty = min(1.0, delta_m)

    # ── Junior loop damage penalty ───────────────────────────────────────────
    if junior_loop_status == "CRITICAL":
        jl_penalty = 0.8
        flags.append("MISSING_JUNIOR_LOOP")
    elif junior_loop_status == "DEGRADING":
        jl_penalty = 0.4
        flags.append("JUNIOR_LOOP_DEGRADING")
    else:
        jl_penalty = 0.0

    # ── Liability clarity score ──────────────────────────────────────────────
    liab = liability_score if liability_score is not None else 0.5
    if not liability_owner_present:
        liab = 0.0
        flags.append("NO_LIABILITY_OWNER")

    # ── Hard block checks ─────────────────────────────────────────────────────
    hard_blocks: list[str] = []

    if anti_hantu_fail:
        hard_blocks.append("F9_ANTI_HANTU_FAIL")
    if sovereign_veto:
        hard_blocks.append("F13_SOVEREIGN_VETO")

    # Δm / svs gates
    if entropy_band == "EXTREME":
        hard_blocks.append("EXTREME_DELTA_M")
    if delta_m > _MAX_DELTA_M:
        hard_blocks.append(f"DELTA_M_EXCEEDS_{_MAX_DELTA_M}")
    if svs < _MIN_SVS:
        hard_blocks.append(f"SVS_BELOW_{_MIN_SVS}")

    if not floors_passed:
        hard_blocks.append("FLOORS_FAILED")

    # ── Determine recommendation ─────────────────────────────────────────────
    if anti_hantu_fail or sovereign_veto:
        recommendation = "VOID_CANDIDATE"
    elif hard_blocks:
        recommendation = "HOLD_CANDIDATE"
    else:
        # Soft compute — only reached if no hard blocks
        rev_bonus = reversibility_score * _E

        final = (
            _A * r
            - _B * risk
            + _C * svs
            + _D * liab
            + _E * rev_bonus
            - _F * entropy_penalty
            - _G * jl_penalty
        )
        final = max(-1.0, min(1.0, final))

        recommendation = (
            "SEAL_CANDIDATE"
            if final > 0.1
            else "HOLD_CANDIDATE" if final > -0.1 else "HOLD_CANDIDATE"
        )

    # Floor score
    floor_score = 1.0 if floors_passed else 0.0

    return WealthScore(
        reward_score=r,
        risk_score=risk,
        verifiability_score=svs,
        floor_score=floor_score,
        liability_clarity_score=liab,
        human_capacity_score=human_capacity_score,
        audit_entropy_penalty=entropy_penalty,
        junior_loop_damage_penalty=jl_penalty,
        final_score=round(
            (
                -999.0
                if hard_blocks
                else max(
                    -1.0,
                    min(
                        1.0,
                        _A * r
                        - _B * risk
                        + _C * svs
                        + _D * liab
                        + _E * rev_bonus
                        - _F * entropy_penalty
                        - _G * jl_penalty,
                    ),
                )
            ),
            4,
        ),
        recommendation=recommendation,
        entropy_band=entropy_band,
        floor_flags=flags,
        hard_blocks=hard_blocks,
        delta_m=delta_m,
        svs=svs,
        npv_estimate=npv_estimate,
        emv_estimate=emv_estimate,
    )


def wealth_decision_packet(
    title: str,
    domain: str,
    claims: list[str],
    expected_reward: dict[str, Any] | None = None,
    known_risks: dict[str, Any] | None = None,
    evidence: list[str] | None = None,
    deployment_plan: dict[str, Any] | None = None,
    npv_estimate: float | None = None,
    emv_estimate: float | None = None,
    liability_owner: str | None = None,
    entropy_band: str = "LOW",
    delta_m: float = 0.0,
    svs: float = 1.0,
    floors_passed: bool = True,
    floor_flags: list[str] | None = None,
    junior_loop_status: str = "SAFE",
    human_capacity_score: float = 0.8,
    anti_hantu_fail: bool = False,
    sovereign_veto: bool = False,
) -> dict[str, Any]:
    """
    Compile a canonical decision packet for 888_JUDGE.

    This is the canonical input that arifos.judge / 888_JUDGE receives.
    Wraps: reward/risk, verification surface, Δm, junior loop impact,
    liability route, score kernel, verdict recommendation.
    """
    # Compute score
    score = wealth_score_kernel(
        reward_score=expected_reward.get("score") if expected_reward else None,
        risk_score=known_risks.get("score") if known_risks else None,
        npv_estimate=npv_estimate,
        emv_estimate=emv_estimate,
        verifiability_score=svs,
        delta_m=delta_m,
        entropy_band=entropy_band,
        floors_passed=floors_passed,
        floor_flags=floor_flags,
        anti_hantu_fail=anti_hantu_fail,
        sovereign_veto=sovereign_veto,
        liability_owner_present=liability_owner is not None,
        reversibility_score=1.0,  # default
        junior_loop_status=junior_loop_status,
        human_capacity_score=human_capacity_score,
    )

    return {
        "packet_type": "WEALTH_DECISION_PACKET",
        "title": title,
        "domain": domain,
        "claims": claims,
        "evidence": evidence or [],
        "deployment_plan": deployment_plan or {},
        "score": score.to_dict(),
        "verification": {
            "delta_m": round(delta_m, 4),
            "svs": round(svs, 4),
            "entropy_band": entropy_band,
        },
        "liability": {
            "owner": liability_owner,
            "owner_type": None,
        },
        "for_judge": {
            "candidate": title,
            "score_summary": {
                "final_score": score.final_score,
                "recommendation": score.recommendation,
                "entropy_band": score.entropy_band,
                "hard_blocks": score.hard_blocks,
                "floor_flags": score.floor_flags,
            },
            "verdict_trigger": (
                "SEAL"
                if score.recommendation == "SEAL_CANDIDATE"
                else "HOLD" if score.recommendation == "HOLD_CANDIDATE" else "VOID"
            ),
        },
    }
