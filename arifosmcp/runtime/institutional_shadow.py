"""
arifosmcp/runtime/institutional_shadow.py
═══════════════════════════════════════════════════════════════════
Institutional Shadow Drift computation.

Implements GENESIS/006 at runtime: measures when a sovereign institution's
observed functions have diverged from its declared name, and produces a
cross-node contract (InstitutionalShadowDrift) that WEALTH/GEOX/AAA can consume.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from arifosmcp.schemas.institutional_shadow import (
    InstitutionalShadowDrift,
    ObservedFunction,
    ShadowDriftRequest,
    ShadowDriftResponse,
)


# Sovereign-institution keywords that signal the entity has moved beyond its name.
_SHADOW_ESCAPE_KEYWORDS: frozenset[str] = frozenset(
    {
        "compute",
        "ai",
        "sovereign",
        "intelligence",
        "data centre",
        "datacenter",
        "grid",
        "ccs",
        "carbon storage",
        "hydrogen",
        "semiconductor",
        "chips",
        "capital market",
        "sovereign wealth",
        "strategic reserve",
    }
)


def _compute_drift_score(declared_function: str, observed_functions: list[ObservedFunction]) -> float:
    """
    Drift score = fraction of observed function mass that is NOT covered by
    the declared function's semantic field.
    """
    if not observed_functions:
        return 0.0

    declared = declared_function.lower()
    total_mass = 0.0
    escaped_mass = 0.0

    for fn in observed_functions:
        mass = fn.confidence * (1.0 + math.log1p(fn.capital_exposure_myr / 1e9))
        total_mass += mass
        # If the observed domain is mentioned in the declared function, it's covered.
        domain = fn.domain.lower()
        if domain in declared:
            continue
        # If the observed function triggers shadow-escape keywords, it has escaped.
        if any(kw in domain for kw in _SHADOW_ESCAPE_KEYWORDS):
            escaped_mass += mass
            continue
        # Mild drift for functions not explicitly in the name.
        escaped_mass += mass * 0.3

    if total_mass == 0.0:
        return 0.0
    return min(1.0, escaped_mass / total_mass)


def _compute_sovereignty_score(observed_functions: list[ObservedFunction]) -> float:
    """
    Sovereignty score: higher when observed functions retain domestic control
    and lower when they depend on foreign substrate.
    """
    if not observed_functions:
        return 0.5

    total_confidence = sum(fn.confidence for fn in observed_functions)
    if total_confidence == 0.0:
        return 0.5

    weighted_score = 0.0
    for fn in observed_functions:
        meta = fn.metadata or {}
        foreign_dependency = float(meta.get("foreign_dependency", 0.0))
        domestic_control = float(meta.get("domestic_control", 1.0 - foreign_dependency))
        equity_share = float(meta.get("sovereign_equity_share", 1.0))
        weighted_score += fn.confidence * (
            0.5 + 0.5 * (domestic_control * 0.6 + equity_share * 0.4)
        )

    return max(0.0, min(1.0, weighted_score / total_confidence))


def _classify_risk(drift_score: float, capital_exposure_myr: float) -> str:
    """Blast-radius class from drift × exposure."""
    if drift_score < 0.3:
        return "LOW"
    if drift_score < 0.6 and capital_exposure_myr < 100e9:
        return "MEDIUM"
    if drift_score < 0.8 and capital_exposure_myr < 500e9:
        return "HIGH"
    return "CRITICAL"


def compute_institutional_shadow_drift(
    request: ShadowDriftRequest,
) -> ShadowDriftResponse:
    """
    Compute Institutional Shadow Drift for a sovereign institution.

    Returns a ShadowDriftResponse with cross-node routing hints.
    """
    observed = request.observed_functions or []
    capital_exposure = request.capital_exposure_myr or sum(
        fn.capital_exposure_myr for fn in observed
    )

    drift_score = _compute_drift_score(request.declared_function, observed)
    sovereignty_score = _compute_sovereignty_score(observed)
    risk_class = _classify_risk(drift_score, capital_exposure)

    hold_reasons: list[str] = []
    if drift_score >= 0.7:
        hold_reasons.append(
            "Institutional function has substantially outgrown its declared name."
        )
    if sovereignty_score < 0.5:
        hold_reasons.append(
            "Observed functions show low sovereign control / high foreign dependency."
        )
    if capital_exposure >= 100e9:
        hold_reasons.append(
            f"High capital exposure ({capital_exposure/1e9:.1f}B MYR) requires 888 review."
        )

    if hold_reasons:
        verdict = "HOLD"
    elif drift_score >= 0.4:
        verdict = "HOLD"
    else:
        verdict = "SEAL"

    last_update: datetime | None = None
    if request.last_shadow_update:
        try:
            last_update = datetime.fromisoformat(request.last_shadow_update.replace("Z", "+00:00"))
        except ValueError:
            last_update = None

    drift = InstitutionalShadowDrift(
        institution_name=request.institution_name,
        declared_function=request.declared_function,
        declared_function_keywords=request.declared_function_keywords,
        observed_functions=observed,
        last_shadow_update=last_update,
        total_capital_exposure_myr=capital_exposure,
        drift_score=drift_score,
        sovereignty_score=sovereignty_score,
        risk_class=risk_class,
        verdict=verdict,
        hold_reasons=hold_reasons,
    )

    routing: dict[str, str] = {
        "arifOS": verdict,
        "WEALTH": "score_sovereignty_risk" if capital_exposure > 0 else "noop",
        "GEOX": "verify_physical_substrate" if any(fn.domain in ("geology", "ccs", "reservoir") for fn in observed) else "noop",
        "AAA": "display_shadow_drift_card",
        "APEX": "888_JUDGE" if verdict == "HOLD" else "noop",
    }

    next_action = (
        "Route to 888_JUDGE before any irreversible deal involving this institution."
        if verdict == "HOLD"
        else "Shadow drift within tolerance; proceed with normal federation routing."
    )

    return ShadowDriftResponse(
        drift=drift,
        next_safe_action=next_action,
        federation_routing=routing,
    )


def arif_detect_institutional_shadow_drift(
    institution_name: str,
    declared_function: str,
    observed_functions: list[dict[str, Any]],
    declared_function_keywords: list[str] | None = None,
    last_shadow_update: str | None = None,
    capital_exposure_myr: float | None = None,
) -> dict[str, Any]:
    """
    Public MCP-style helper. Accepts plain dicts for observed_functions so it can
    be called from any node without importing the full Pydantic model.
    """
    observed_models = [ObservedFunction.model_validate(o) for o in observed_functions]
    request = ShadowDriftRequest(
        institution_name=institution_name,
        declared_function=declared_function,
        declared_function_keywords=declared_function_keywords or [],
        observed_functions=observed_models,
        last_shadow_update=last_shadow_update,
        capital_exposure_myr=capital_exposure_myr,
    )
    response = compute_institutional_shadow_drift(request)
    return response.model_dump(mode="json")
