"""arifos_wiki_tools.physics — Discovery Physics Kernel.

Wraps existing arifOS physics primitives for the discovery tool:
- Evidence Level Ladder (L0-L6)
- Search Worthiness (W)
- Entropy Delta (ΔS)
- Omega-0 / Humility Band
- Witness Consensus (W₄)
- Contradiction Audit

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
CONFESSION: These are thin wrappers. The canonical formulas live in:
  arifosmcp.runtime.a_rif.models    (EvidenceLevel, ClaimState)
  arifosmcp.runtime.a_rif.engine    (calculate_search_worthiness, evaluate_entropy_delta)
  arifosmcp.runtime.a_rif.contradiction (audit_for_contradictions)
  core.shared.physics              (W_4, Omega_0, humility_band)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# ── Ensure arifOS core/ is on the import path ──────────────────────────────
_ARIFOS_ROOT = Path(__file__).resolve().parents[2]  # .../arifOS/
if not any(str(_ARIFOS_ROOT) == p for p in sys.path):
    sys.path.insert(0, str(_ARIFOS_ROOT))
if not any(str(_ARIFOS_ROOT / "core") == p for p in sys.path):
    sys.path.insert(0, str(_ARIFOS_ROOT / "core"))

try:
    from arifosmcp.runtime.a_rif.models import ClaimState, EvidenceLevel
    from arifosmcp.runtime.a_rif.engine import (
        calculate_search_worthiness,
        evaluate_entropy_delta,
    )
    from arifosmcp.runtime.a_rif.contradiction import (
        audit_for_contradictions,
        ContradictionReport,
    )
    from core.shared.physics import W_4, Omega_0, humility_band

    _PHYSICS_AVAILABLE = True
except ImportError as _e:
    _PHYSICS_AVAILABLE = False
    _IMPORT_ERROR = str(_e)

# ── Constants ────────────────────────────────────────────────────────────────

# Source authority rank → Evidence Level mapping (from source_rank.py)
_SOURCE_RANK_TO_LEVEL: dict[int, str] = {
    1: "L4",  # official / primary
    2: "L3",  # primary data / academic
    3: "L2",  # reputable institution
    4: "L2",  # reputable news
    5: "L1",  # blog / social
    7: "L0",  # blog / forum
    9: "L0",  # unknown / synthetic
}

# Discovery physics version
_VERSION = "0.1.0"


# ── Evidence Level ──────────────────────────────────────────────────────────


def evidence_level_from_sources(
    local_wiki_count: int,
    repo_index_count: int,
    web_count: int,
    source_rank: int | None = None,
) -> str:
    """
    Map layer counts to an Evidence Level (L0-L6).

    L0 = no usable evidence / contaminated
    L1 = search snippets only
    L2 = one fetched source inspected
    L3 = multiple independent sources agree
    L4 = primary / official source inspected
    L5 = primary + corroborated + archived
    L6 = reproducible data / direct measurement
    """
    total = local_wiki_count + repo_index_count + web_count

    if source_rank is not None:
        rank_level = _SOURCE_RANK_TO_LEVEL.get(source_rank)
        if rank_level:
            return rank_level

    if total == 0:
        return "L0"
    if web_count >= 2 and (local_wiki_count + repo_index_count) >= 1:
        return "L3"  # multiple independent sources agree
    if web_count >= 1 or (local_wiki_count + repo_index_count) >= 2:
        return "L2"  # one or more sources inspected
    if total >= 1:
        return "L1"  # search snippets only
    return "L0"


# ── Search Worthiness ───────────────────────────────────────────────────────


def compute_search_w(
    uncertainty: float = 0.5,
    importance: float = 0.5,
    freshness: float = 0.5,
    noise: float = 0.2,
    injection: float = 0.1,
    cost: float = 0.1,
    background_confidence: float = 0.0,
) -> dict[str, Any]:
    """
    Compute search worthiness: W = ((1-B)*I*F)/(N*P*C)

    Returns dict with W score and recommendation.
    W < 1.0 → skip search (not worth it)
    W >= 1.0 → proceed with search
    """
    if not _PHYSICS_AVAILABLE:
        return {
            "W": None,
            "worthwhile": None,
            "recommendation": "skip",
            "_error": "arifOS physics modules unavailable",
        }

    W = calculate_search_worthiness(
        uncertainty=uncertainty,
        importance=importance,
        freshness=freshness,
        noise=noise,
        injection=injection,
        cost=cost,
        background_confidence=background_confidence,
    )
    # Cap W at 10.0 for operational scoring — raw values can be explosive
    # (e.g., W=62.5 with default cost=0.1, injection=0.1).
    # Cap is transparent: raw W is not hidden, but capped W is used for threshold.
    W_capped = min(W, 10.0)
    return {
        "W": W,
        "W_capped": W_capped,
        "worthwhile": W_capped >= 1.0,
        "recommendation": "search" if W_capped >= 1.0 else "skip",
    }


# ── Entropy Delta ──────────────────────────────────────────────────────────


def compute_entropy_delta(
    entropy_before: float,
    entropy_after: float,
) -> dict[str, Any]:
    """
    Compute ΔS = entropy_after - entropy_before.

    ΔS > 0    → search increased uncertainty → void/hold
    |ΔS| < 0.01 → plateau → stop
    ΔS < -0.01 → uncertainty reduced → continue / useful
    """
    if not _PHYSICS_AVAILABLE:
        return {
            "delta_s": None,
            "recommendation": "unknown",
            "_error": "arifOS physics modules unavailable",
        }

    delta_s = evaluate_entropy_delta(entropy_before, entropy_after)
    if delta_s > 0:
        recommendation = "void"
    elif abs(delta_s) < 0.01:
        recommendation = "stop"
    else:
        recommendation = "continue"
    return {
        "before": entropy_before,
        "after": entropy_after,
        "delta_s": delta_s,
        "recommendation": recommendation,
    }


# ── Omega-0 Humility ──────────────────────────────────────────────────────


def compute_omega(confidence: float) -> dict[str, Any]:
    """
    Compute Ω₀ from confidence.

    Ω₀ in [0.03, 0.05] = healthy humility band
    < 0.03 = overconfident
    > 0.05 = too uncertain
    """
    if not _PHYSICS_AVAILABLE:
        return {
            "omega_0": None,
            "in_band": None,
            "_error": "arifOS physics modules unavailable",
        }

    band = Omega_0(confidence)
    omega_val = float(band.omega_0)  # UncertaintyBand.omega_0 is a float field
    return {
        "omega_0": round(omega_val, 4),
        "in_band": 0.03 <= omega_val <= 0.05,
        "diagnosis": (
            "overconfident"
            if omega_val < 0.03
            else "too_uncertain"
            if omega_val > 0.05
            else "humility_band"
        ),
    }


# ── Witness Consensus W₄ ─────────────────────────────────────────────────


def compute_w4(
    human: float = 0.0,
    ai: float = 0.0,
    evidence: float = 0.0,
    verifier: float = 0.0,
) -> dict[str, Any]:
    """
    Compute W₄ = (H × A × E × V)^(1/4).

    W₄ >= 0.75 → enough witness consensus
    W₄ < 0.75  → HOLD / insufficient witness
    """
    if not _PHYSICS_AVAILABLE:
        return {
            "W4": None,
            "consensus": None,
            "recommendation": "HOLD",
            "_error": "arifOS physics modules unavailable",
        }

    W4 = W_4(human, ai, evidence, verifier)
    return {
        "human": human,
        "ai": ai,
        "evidence": evidence,
        "verifier": verifier,
        "W4": round(W4, 4),
        "consensus": W4 >= 0.75,
        "recommendation": "proceed" if W4 >= 0.75 else "HOLD",
    }


# ── Contradiction Audit ──────────────────────────────────────────────────


def audit_claims(claims: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Audit claims for contradictions.

    Returns ContradictionReport with status:
      CONFLICT → HOLD
      CONSISTENT → still conservative
      VOID → no claims to audit
    """
    if not _PHYSICS_AVAILABLE:
        return {
            "status": "UNKNOWN",
            "conflicts": [],
            "recommendation": "HOLD",
            "_error": "arifOS physics modules unavailable",
        }

    report: ContradictionReport = audit_for_contradictions(claims)
    return {
        "status": report.status,
        "conflicts": [
            {"a": c.get("a"), "b": c.get("b"), "type": c.get("type")}
            for c in (getattr(report, "conflicts", []) or [])
        ],
        "recommendation": report.recommendation,
    }


# ── Claim State ───────────────────────────────────────────────────────────


def claim_state_from_evidence(
    evidence_level: str,
    w4: float | None,
    contradictions_found: bool,
) -> str:
    """
    Map evidence level + witness + contradictions to a ClaimState.

    Returns: unknown | hypothesis | supported | verified | void
    """
    if evidence_level == "L0":
        return "void"
    if contradictions_found:
        return "hypothesis"  # contradictions downgrades to hypothesis
    if w4 is not None and w4 < 0.75:
        return "hypothesis"  # insufficient witness consensus
    if evidence_level in ("L5", "L6"):
        return "verified"
    if evidence_level in ("L3", "L4"):
        return "supported"
    return "hypothesis"


# ── Unified Discovery Score ───────────────────────────────────────────────


def score_discovery(
    local_wiki_count: int,
    repo_index_count: int,
    web_count: int,
    query: str,
    entropy_before: float = 0.5,
    background_confidence: float = 0.0,
    human_witness: float = 0.0,
    claims: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Compute the full Discovery Physics Kernel score.

    Returns a dict with all physics primitives and the honest claim_state.

    Args:
        local_wiki_count: Number of local wiki hits
        repo_index_count: Number of repo index hits
        web_count: Number of web hits
        query: The search query (used for search worthiness)
        entropy_before: Prior uncertainty estimate [0, 1]
        background_confidence: How confident we were before searching [0, 1]
        human_witness: Human/local authority witness score [0, 1]
        claims: Optional list of claim dicts for contradiction audit
    """
    claims = claims or []

    total = local_wiki_count + repo_index_count + web_count

    # Evidence Level
    ev_level = evidence_level_from_sources(local_wiki_count, repo_index_count, web_count)

    # Omega-0
    # confidence proxy = proportion of layers that found something
    confidence_proxy = min(total / 3.0, 1.0)
    omega_result = compute_omega(confidence_proxy)

    # W4 Witness Consensus
    # Evidence witness scales with layers that found something
    ai_witness = min((repo_index_count + local_wiki_count) / 3.0, 1.0) if total > 0 else 0.0
    ev_witness = min(web_count / 3.0, 1.0) if web_count > 0 else 0.0
    # No verifier in v0 discovery (that's adversarial testing)
    w4_result = compute_w4(
        human=human_witness,
        ai=ai_witness,
        evidence=ev_witness,
        verifier=0.0,
    )

    # Entropy Delta
    # entropy_after: lower when more results found
    entropy_after = max(0.0, entropy_before - (total * 0.05))
    entropy_result = compute_entropy_delta(entropy_before, entropy_after)

    # Contradiction Audit
    contradiction_result = audit_claims(claims)

    # Claim State
    claim_state = claim_state_from_evidence(
        evidence_level=ev_level,
        w4=w4_result.get("W4"),
        contradictions_found=contradiction_result["status"] == "CONFLICT",
    )

    return {
        "physics_version": _VERSION,
        "evidence_level": ev_level,
        "claim_state": claim_state,
        "entropy": entropy_result,
        "omega_0": omega_result,
        "witness": w4_result,
        "contradictions": contradiction_result,
        "search_worthiness": compute_search_w(
            uncertainty=entropy_before,
            importance=0.5,
            freshness=0.5,
            background_confidence=background_confidence,
        ),
    }
