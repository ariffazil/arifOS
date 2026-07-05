"""
APEX Runtime Governance Envelope — Canonical Python Implementation

APEX-MCP-001: Every MCP-visible output that can influence agent state
must carry an APEX envelope. Transport frames remain protocol-pure JSON-RPC.

10 Gates:
  [Cognitive] Amanah · Presence · Humility · Signal · Understanding · Energy
  [Kernel]    Authority · Reversibility · Proof · Sovereign

APEX-Law equation: g(t) = A(t) · P(t) · H(t) · √(S(t)·U(t)) · E(t)²
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

# ZEN Phase 1: ToAC + TPCP integration per APEX_STACK_Forge_2026-07-06_v1
# ToAC: AC_Risk = U_phys × D_transform × B_cog (from GEOX/040)
# TPCP: 4-phase (ΔP → ΩP → ΨP → Φ_P) + most restrictive verdict
# NOTE: TPCP run_tpcp_pipeline not present in paradox pkg (path was wrong too). ToAC fn local. Deferred.

def toac_contrast_score(evidence: dict | None = None, claim_strength: float = 0.5) -> float:
    """Mandatory ToAC contrast tag. Default 0.50 per brief if missing."""
    if not evidence:
        return 0.50
    u_phys = evidence.get('uncertainty_phys', 0.5)
    d_trans = evidence.get('distortion', 0.5)
    b_cog = evidence.get('bias_cog', 0.5)
    risk = min(1.0, u_phys * d_trans * b_cog)
    return risk


# ── Constants ──────────────────────────────────────────────────────────────

APEX_EQUATION = "g(t)=A(t)\u00b7P(t)\u00b7H(t)\u00b7\u221a(S(t)\u00b7U(t))\u00b7E(t)\u00b2"
APEX_VERSION = "v2026.06.20"
APEX_SPEC = "APEX-MCP-001"

BOUNDARIES = {"LIVE", "CACHED", "INFERRED"}
ACTION_CLASSES = {"READ", "MUTATE", "ATOMIC", "IRREVERSIBLE"}
PROOF_LEVELS = {"ZKPC_NONE", "ZKPC_OBSERVATION", "ZKPC_AUDIT", "ZKPC_CERTAINTY"}

VERDICT_VOID = "VOID"
VERDICT_HOLD = "HOLD"
VERDICT_SABAR = "SABAR"
VERDICT_SEAL = "SEAL"

# Verdict lattice: VOID > HOLD > SABAR > SEAL
_VERDICT_ORDER = {VERDICT_VOID: 0, VERDICT_HOLD: 1, VERDICT_SABAR: 2, VERDICT_SEAL: 3}


# ── Gate Verdict Factory ───────────────────────────────────────────────────


def gate(
    passed: bool,
    score: float,
    detail: str,
    **extra: Any,
) -> dict[str, Any]:
    """Create a single gate verdict."""
    v: dict[str, Any] = {
        "pass": passed,
        "score": round(max(0.0, min(1.0, score)), 4),
        "detail": detail,
    }
    v.update(extra)
    return v


# ── Individual Gate Builders ───────────────────────────────────────────────


def amanah_gate(
    confidence: float = 0.88,
    evidence_strength: float = 0.95,
) -> dict[str, Any]:
    """Gate 1: Is the claim no stronger than the evidence?"""
    c = max(0.0, min(1.0, confidence))
    e = max(0.0, min(1.0, evidence_strength))
    passed = c <= e + 0.05  # 5% tolerance
    score = min(1.0, e / max(c, 1e-6))
    return gate(
        passed=passed,
        score=score,
        detail=f"confidence {c:.2f} {'<=' if passed else '>'} evidence {e:.2f}",
    )


