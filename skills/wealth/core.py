"""
WEALTH Core — Stage 999: THE ECONOMIST
═══════════════════════════════════════

Sovereign Valuation Kernel. High-precision financial evaluation
and capital allocation math, mapped to fundamental physical dimensions.

Post-AGI extension: verification-first capital governance.
EconomicEnvelope now carries optional verification state:
  - VerificationSurface
  - AuditEntropy (delta_m, svs, entropy_band)
  - WealthScore
  - truth_band (F2: declare confidence band, not just score it)

All existing functions remain backward-compatible.
New code paths are additive and non-mutating.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

EPSILON = 1e-9
INVALID_FLAGS = {
    "INVALID_INITIAL_INVESTMENT",
    "INVALID_CASHFLOW_SERIES",
    "INVALID_DISCOUNT_RATE",
    "INVALID_FINANCE_RATE",
    "INVALID_REINVESTMENT_RATE",
    "INVALID_SCENARIOS",
    "PROBABILITY_MASS_INVALID",
    "INVALID_DEBT_SERVICE",
}
HOLD_FLAGS = {
    "LEVERAGE_CRITICAL",
    "LEVERAGE_DEFAULT",
    "SOVEREIGN_DIGNITY_LOW",
    "MULTIPLE_IRR_POSSIBLE",
}
QUALIFY_FLAGS = {
    "NON_NORMAL_FLOWS",
    "IRR_NOT_FOUND",
    "NOT_RECOVERED",
    "EBITDA_PROXY_USED",
}

# ── New verification governance flags ─────────────────────────────────────────
VERIFICATION_HOLD_FLAGS = {
    "LOW_VERIFIABLE_SHARE",  # svs < 0.30
    "EXTREME_ENTROPY_BAND",  # entropy_band == "EXTREME"
    "DELTA_M_EXCEEDS_THRESHOLD",  # delta_m > 0.80
    "NO_LIABILITY_OWNER",  # liability_owner absent → automatic HOLD
    "MISSING_JUNIOR_LOOP",  # CRITICAL junior loop degradation
}
VERIFICATION_VOID_FLAGS = {
    "F9_ANTI_HANTU_FAIL",
    "L13_SOVEREIGN_VETO",
    "FLOORS_FAILED",
}


# ═══════════════════════════════════════════════════════════════════════════════
# TRUTH BAND — F2 Declaration
# ═══════════════════════════════════════════════════════════════════════════════

TruthBand = Literal["CERTAIN", "HIGH_CONFIDENCE", "PLAUSIBLE", "SPECULATIVE", "UNKNOWN"]


def truth_band_from_score(confidence_score: float) -> TruthBand:
    """Map numeric confidence to F2 truth band declaration."""
    if confidence_score >= 0.95:
        return "CERTAIN"
    elif confidence_score >= 0.80:
        return "HIGH_CONFIDENCE"
    elif confidence_score >= 0.50:
        return "PLAUSIBLE"
    elif confidence_score >= 0.20:
        return "SPECULATIVE"
    return "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# ECONOMIC ENVELOPE — Extended with Verification State
# ═══════════════════════════════════════════════════════════════════════════════


class EconomicEnvelope(BaseModel):
    """
    Sovereign capital allocation envelope.

    Extended post-AGI:
      - verification_surface: canonical claim + evidence + verifier info
      - audit_entropy: delta_m, svs, entropy_band (from wealth_verify)
      - wealth_score: multi-axis constitutional score (from wealth_score_kernel)
      - truth_band: F2 declaration — the band, not just the score

    When verification state is present, verdict derivation uses it as
    the dominant recommendation layer, not NPV/IRR alone.
    """

    tool: str
    dimension: str
    verdict: str
    allocation_signal: str
    primary_result: dict[str, Any]
    secondary_metrics: dict[str, Any] = Field(default_factory=dict)
    thermodynamics: dict[str, float] = Field(
        default={
            "g_score": 0.85,
            "delta_s": -0.12,
            "psi": 1.10,
            "omega": 0.04,
        }
    )
    integrity_flags: list[str] = Field(default_factory=list)
    confidence: str
    epistemic: str
    epoch_id: str = Field(default=None, description="Constitutional epoch timestamp")
    # ── Verification-first governance (optional — backward compatible) ────
    verification_surface: Optional[dict[str, Any]] = None
    audit_entropy: Optional[dict[str, Any]] = None
    wealth_score: Optional[dict[str, Any]] = None
    truth_band: Optional[TruthBand] = None
    confidence_note: Optional[str] = None  # F2: human-readable band declaration


# ═══════════════════════════════════════════════════════════════════════════════
# EXISTING FUNCTIONS — Unchanged, backward-compatible
# ═══════════════════════════════════════════════════════════════════════════════


def round_value(value: float | None, digits: int = 6) -> float | None:
    if value is None or not math.isfinite(value):
        return value
    return round(value, digits)


def count_sign_changes(values: list[float]) -> int:
    prev = 0
    changes = 0
    for v in values:
        if abs(v) <= EPSILON:
            continue
        sign = 1 if v > 0 else -1
        if prev != 0 and sign != prev:
            changes += 1
        prev = sign
    return changes


def build_cashflow_series(initial: float, flows: list[float], terminal: float = 0) -> list[float]:
    series = [-abs(initial), *flows]
    if terminal and len(series) > 1:
        series[-1] += terminal
    return series


def npv_from_series(series: list[float], rate: float) -> float:
    total = 0.0
    for i, cf in enumerate(series):
        total += cf / pow(1 + rate, i)
    return total


def derive_verdict(flags: list[str]) -> str:
    if any(f in INVALID_FLAGS for f in flags):
        return "VOID"
    if any(f in HOLD_FLAGS for f in flags):
        return "888-HOLD"
    if any(f in QUALIFY_FLAGS for f in flags):
        return "QUALIFY"
    return "SEAL"


def derive_allocation_signal(tool: str, primary: dict[str, Any], flags: list[str]) -> str:
    if any(f in INVALID_FLAGS for f in flags):
        return "INSUFFICIENT_DATA"
    if tool == "wealth_npv_reward":
        val = primary.get("npv")
        return "ACCEPT" if val and val > 0 else "REJECT" if val and val < 0 else "MARGINAL"
    return "MARGINAL"


def create_envelope(
    tool: str,
    dimension: str,
    primary: dict[str, Any],
    secondary: dict[str, Any],
    flags: list[str],
    epistemic: str = "CLAIM",
) -> EconomicEnvelope:
    verdict = derive_verdict(flags)
    return EconomicEnvelope(
        tool=tool,
        dimension=dimension,
        verdict=verdict,
        allocation_signal=derive_allocation_signal(tool, primary, flags),
        primary_result=primary,
        secondary_metrics=secondary,
        integrity_flags=flags,
        confidence="HIGH" if verdict == "SEAL" else "LOW",
        epistemic=epistemic,
        epoch_id=datetime.now(timezone.utc).isoformat(),
    )


def calculate_npv(
    initial: float, flows: list[float], rate: float, terminal: float = 0
) -> dict[str, Any]:
    series = build_cashflow_series(initial, flows, terminal)
    npv = npv_from_series(series, rate)
    return {
        "npv": round_value(npv),
        "flags": [] if math.isfinite(npv) else ["INVALID_NPV"],
    }


def calculate_irr(initial: float, flows: list[float]) -> dict[str, Any]:
    series = build_cashflow_series(initial, flows)

    def f(r):
        return npv_from_series(series, r)

    low, high = -0.9, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if f(mid) > 0:
            low = mid
        else:
            high = mid
    return {"irr": round_value(mid), "flags": []}


def calculate_dscr(ebitda: float, debt_service: float) -> dict[str, Any]:
    dscr = ebitda / debt_service if debt_service > 0 else None
    flags = ["LEVERAGE_DEFAULT"] if dscr and dscr < 1.0 else []
    return {"dscr": round_value(dscr), "flags": flags}


def wealth_npv_reward(
    initial_investment: float,
    cash_flows: list[float],
    discount_rate: float,
    terminal_value: float = 0,
    epistemic: str = "CLAIM",
) -> EconomicEnvelope:
    m = calculate_npv(initial_investment, cash_flows, discount_rate, terminal_value)
    return create_envelope(
        "wealth_npv_reward",
        "Reward",
        {"npv": m["npv"]},
        {"terminal_value": terminal_value},
        m["flags"],
        epistemic,
    )


def wealth_irr_yield(initial_investment: float, cash_flows: list[float]) -> EconomicEnvelope:
    m = calculate_irr(initial_investment, cash_flows)
    return create_envelope("wealth_irr_yield", "Energy", {"irr": m["irr"]}, {}, m["flags"])


def wealth_dscr_leverage(ebitda: float, debt_service: float) -> EconomicEnvelope:
    m = calculate_dscr(ebitda, debt_service)
    return create_envelope("wealth_dscr_leverage", "Survival", {"dscr": m["dscr"]}, {}, m["flags"])


# ═══════════════════════════════════════════════════════════════════════════════
# NEW: VERIFICATION-AWARE ENVELOPE CREATION
# ═══════════════════════════════════════════════════════════════════════════════


def _derive_verdict_from_verification(
    flags: list[str],
    audit_entropy: dict[str, Any] | None,
    wealth_score: dict[str, Any] | None,
) -> str:
    """
    Override or inform verdict using verification state.

    Priority:
      1. Verification VOID flags (F9, F13, FLOORS_FAILED) → VOID
      2. Verification HOLD flags (Δm, svs, liability) → 888-HOLD
      3. wealth_score recommendation if present → dominant
      4. Fall back to classic flag-based verdict

    This replaces the old logic where NPV/IRR alone determined the verdict.
    """
    all_flags = set(flags)

    # Collect verification flags
    if audit_entropy:
        band = audit_entropy.get("entropy_band", "LOW")
        svs = audit_entropy.get("svs", 1.0)
        delta_m = audit_entropy.get("delta_m", 0.0)
        if band == "EXTREME":
            all_flags.add("EXTREME_ENTROPY_BAND")
        if svs < 0.30:
            all_flags.add("LOW_VERIFIABLE_SHARE")
        if delta_m > 0.80:
            all_flags.add("DELTA_M_EXCEEDS_THRESHOLD")
        for b in audit_entropy.get("bottlenecks", []):
            all_flags.add(f"BOTTLENECK: {b}")

    if wealth_score:
        rec = wealth_score.get("recommendation", "HOLD_CANDIDATE")
        ws_flags = wealth_score.get("floor_flags", [])
        ws_blocks = wealth_score.get("hard_blocks", [])
        all_flags.update(ws_flags)
        all_flags.update(ws_blocks)

    # VOID priority
    if any(f in VERIFICATION_VOID_FLAGS for f in all_flags):
        return "VOID"
    if any(f in INVALID_FLAGS for f in all_flags):
        return "VOID"

    # HOLD priority
    if any(f in VERIFICATION_HOLD_FLAGS for f in all_flags):
        return "888-HOLD"
    if any(f in HOLD_FLAGS for f in all_flags):
        return "888-HOLD"

    # wealth_score recommendation as dominant signal
    if wealth_score:
        rec = wealth_score.get("recommendation", "HOLD_CANDIDATE")
        if rec == "VOID_CANDIDATE":
            return "VOID"
        if rec == "HOLD_CANDIDATE":
            return "888-HOLD"
        if rec == "SEAL_CANDIDATE":
            return "SEAL"

    if any(f in QUALIFY_FLAGS for f in all_flags):
        return "QUALIFY"
    return "SEAL"


def _derive_truth_band(
    audit_entropy: dict[str, Any] | None,
    wealth_score: dict[str, Any] | None,
    fallback_confidence: float = 0.5,
) -> tuple[TruthBand, str]:
    """
    F2 Truth band declaration — the band, not just the score.

    Returns (truth_band, confidence_note) for F2 compliance.
    """
    if wealth_score:
        fs = wealth_score.get("final_score", 0.0)
        band = truth_band_from_score(abs(fs))
        if fs < 0:
            note = f"Negative score ({fs:.2f}) — speculative band"
        elif wealth_score.get("hard_blocks"):
            note = f"Hard blocks present — {wealth_score['hard_blocks'][0]}"
        else:
            note = f"Constitutional score {fs:.2f} — {band.lower()} confidence"
        return band, note

    if audit_entropy:
        band = audit_entropy.get("entropy_band", "LOW")
        delta_m = audit_entropy.get("delta_m", 0.0)
        if band == "EXTREME":
            return "SPECULATIVE", f"Δm={delta_m:.2f} — extreme entropy, speculative"
        if band == "HIGH":
            return "PLAUSIBLE", f"Δm={delta_m:.2f} — high entropy, plausible"
        return "HIGH_CONFIDENCE", f"Δm={delta_m:.2f} — low entropy"

    band = truth_band_from_score(fallback_confidence)
    return band, f"Fallback confidence {fallback_confidence:.2f} — {band.lower()}"


def create_governed_envelope(
    tool: str,
    dimension: str,
    primary: dict[str, Any],
    secondary: dict[str, Any],
    flags: list[str],
    epistemic: str = "CLAIM",
    # ── Verification state (optional) ──────────────────────────────────────
    verification_surface: dict[str, Any] | None = None,
    audit_entropy: dict[str, Any] | None = None,
    wealth_score: dict[str, Any] | None = None,
    fallback_confidence: float = 0.5,
) -> EconomicEnvelope:
    """
    Create an EconomicEnvelope with verification-first governance.

    When audit_entropy or wealth_score is present, verdict derivation uses
    them as the dominant recommendation layer — not NPV/IRR alone.

    F2 truth band is always declared (even if only from fallback).
    """
    verdict = _derive_verdict_from_verification(flags, audit_entropy, wealth_score)
    truth_band, confidence_note = _derive_truth_band(
        audit_entropy, wealth_score, fallback_confidence
    )

    # Override allocation_signal if wealth_score present
    if wealth_score:
        rec = wealth_score.get("recommendation", "HOLD_CANDIDATE")
        if rec == "SEAL_CANDIDATE":
            allocation = "ACCEPT"
        elif rec == "HOLD_CANDIDATE":
            allocation = "MARGINAL"
        else:
            allocation = "INSUFFICIENT_DATA"
    else:
        allocation = derive_allocation_signal(tool, primary, flags)

    return EconomicEnvelope(
        tool=tool,
        dimension=dimension,
        verdict=verdict,
        allocation_signal=allocation,
        primary_result=primary,
        secondary_metrics=secondary,
        integrity_flags=flags,
        confidence="HIGH" if verdict == "SEAL" else "LOW",
        epistemic=epistemic,
        epoch_id=datetime.now(timezone.utc).isoformat(),
        verification_surface=verification_surface,
        audit_entropy=audit_entropy,
        wealth_score=wealth_score,
        truth_band=truth_band,
        confidence_note=confidence_note,
    )


def wrap_with_verification(
    envelope: EconomicEnvelope,
    audit_entropy: dict[str, Any] | None = None,
    wealth_score: dict[str, Any] | None = None,
    verification_surface: dict[str, Any] | None = None,
) -> EconomicEnvelope:
    """
    Wrap an existing envelope with verification state.

    Does NOT mutate the original envelope (immutability preserved).
    Returns a new envelope with verification fields populated and
    verdict re-derived from verification state if present.
    """
    if audit_entropy is None and wealth_score is None and verification_surface is None:
        return envelope  # nothing to wrap

    # Re-derive verdict if verification state present
    new_verdict = _derive_verdict_from_verification(
        envelope.integrity_flags, audit_entropy, wealth_score
    )
    truth_band, confidence_note = _derive_truth_band(
        audit_entropy,
        wealth_score,
        fallback_confidence=0.5 if envelope.confidence == "HIGH" else 0.3,
    )

    return EconomicEnvelope(
        tool=envelope.tool,
        dimension=envelope.dimension,
        verdict=new_verdict,
        allocation_signal=envelope.allocation_signal,
        primary_result=envelope.primary_result,
        secondary_metrics=envelope.secondary_metrics,
        thermodynamics=envelope.thermodynamics,
        integrity_flags=envelope.integrity_flags,
        confidence=envelope.confidence,
        epistemic=envelope.epistemic,
        epoch_id=datetime.now(timezone.utc).isoformat(),
        verification_surface=verification_surface or envelope.verification_surface,
        audit_entropy=audit_entropy or envelope.audit_entropy,
        wealth_score=wealth_score or envelope.wealth_score,
        truth_band=truth_band,
        confidence_note=confidence_note,
    )
