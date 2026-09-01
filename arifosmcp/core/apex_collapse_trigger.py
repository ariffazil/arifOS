"""
arifosmcp/core/apex_collapse_trigger.py — MEASUREMENT-THEORETIC INTELLIGENCE
═══════════════════════════════════════════════════════════════════════════════

THE EUREKA (2026-08-02):
  The collapse trigger — not the judgment, not the verdict — is the EUREKA.
  Classical agents: state → tool → next-state → tool → ...
  APEX agents:     state → [collapse] → verdict → tool? → next-state

  A tool call is a measurement-collapse request. Before the tool call, the agent
  has hypotheses. After the tool call, Reality replies. The collapse trigger
  ensures the agent cannot reach for a tool without first being judged.

PHASE 1 — OBSERVE-ONLY (2026-08-02):
  - Compute four-dial state [A, P, E, X] + scar burden Φ
  - Log to arifFLOW as metabolic receipts
  - NEVER block tool execution
  - Feature flag: COLLAPSE_TRIGGER_ENFORCE=false

PHASE 2 — ENFORCEMENT (gated behind F4/F2/F3/F12 evidence):
  - Wire into forge_execute, forge_shell, mutation tools
  - Block tool execution on non-SEAL verdict
  - Fail-open: trigger failure → SABAR (allow with warning)

FOUR-DIAL SPINOR:
  A = AKAL            — intent clarity, task understanding, tool-class match
  P = PRESENT         — evidence freshness, observation recency, grounding
  E = ENERGY-ENTROPY  — tool cost, reversibility, blast radius
  X = EXPLORATION-AMANAH — permissioned exploration, authority ceiling

  B = (A·P·E·X)^(1/4)     — geometric mean, non-compensatory (Nash 1950)
  B|Φ = B × exp(−Φ)       — scar-corrected present coherence
  ∂S = entropy gradient    — does this action reduce future disorder?

COLLAPSE VERDICTS:
  SEAL  — all dials green, scar below ceiling, entropy investment
  SABAR — pause, gather evidence, insufficient buffer
  HOLD  — restructure, request authority, extractive pathway
  VOID  — reject action, terminal pathway, floor violation

SCAR SATURATION:
  Φ_max = 2.5  → B|Φ ≥ 0.082 (floor for action)
  Φ ≥ 2.5      → VOID — needs cooling via forge_cool_drift CONVERGING
  ΔΦ_cooling   = 0.15 × convergence_strength (future: Phase 2+)

MEASUREMENT-THEORETIC INTELLIGENCE:
  Not quantum computing. Not classical agent. Third category:
  Classical state + quantum-style verdict collapse + sovereign observer.
  arif_judge IS the collapse operator. F13 is the observer.

CATEGORY: Measurement-Theoretic Intelligence
CANON: APEX v36Ω projection onto tool-use manifold
FLOORS: F1 (reversible), F2 (TRUTH), F4 (ΔS ≤ 0), F7 (Ω₀ ∈ [0.03,0.05]),
        F9 (ANTIHANTU), F11 (AUDITABILITY), F13 (SOVEREIGN)

DITEMPA BUKAN DIBERI — Forged, Not Given
Forged: 2026-08-02 by 333-AGI under F13 directive
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("arifos.collapse")

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# F7 HUMILITY: Ω₀ ∈ [0.03, 0.05]
OMEGA_0_MIN = 0.03
OMEGA_0_MAX = 0.05

# F9 ANTIHANTU: C_dark < 0.30
C_DARK_CAP = 0.30

# F8 GENIUS: G ≥ 0.80 for complex actions
G_THRESHOLD = 0.80

# SCAR SATURATION
PHI_MAX = 2.5  # B|Φ ≥ 0.082 at this ceiling
PHI_COOLING_FACTOR = 0.15  # ΔΦ per CONVERGING cooling receipt

# VERDICT THRESHOLDS (Phase 1: observe-only, not enforced)
# Phase 2+: these become enforcement gates
B_CORRECTED_SEAL_THRESHOLD = 0.40  # B|Φ must be ≥ 0.40 for SEAL
DIAL_FLOOR = 0.20  # any dial below this → VOID
GRADIENT_SABAR_THRESHOLD = 0.50  # ∂S > 0.5 → SABAR (gather evidence)

# ── LAW_ZEN_ATTENTION (2026-09-01, additive — F13 ratification pending) ──
# "No sovereign attention shall be spent unless expected entropy reduction
#  exceeds expected scar creation." Attention is the inelastic numéraire;
#  approval theatre is unpriced cognitive dumping onto H_a.
ACR_FLOOR = 0.10  # min ΔReality per sovereign attention-minute
PHI_SCAR_CEILING = 0.30  # expected scar-creation risk ceiling
ZEN_ATTENTION_ENFORCE = False  # Phase 1: measure only — F13 opens the gate

# PHASE 1 FEATURE FLAG
COLLAPSE_TRIGGER_ENFORCE = False  # Phase 1: observe-only

# TOOL ENTROPY TIERS (canonical classification)
TOOL_ENTROPY_TIERS: dict[str, dict[str, Any]] = {
    "read": {"tier": "low", "delta_S": -0.10, "reversible": True},
    "search": {"tier": "low", "delta_S": -0.20, "reversible": True},
    "observe": {"tier": "low", "delta_S": -0.05, "reversible": True},
    "reason": {"tier": "low", "delta_S": -0.05, "reversible": True},
    "plan": {"tier": "low", "delta_S": -0.05, "reversible": True},
    "memory": {"tier": "low", "delta_S": -0.05, "reversible": True},
    "route": {"tier": "low", "delta_S": -0.05, "reversible": True},
    "draft": {"tier": "medium", "delta_S": 0.00, "reversible": True},
    "generate": {"tier": "medium", "delta_S": 0.00, "reversible": True},
    "compute": {"tier": "medium", "delta_S": 0.00, "reversible": True},
    "test": {"tier": "medium", "delta_S": 0.00, "reversible": True},
    "edit": {"tier": "medium", "delta_S": 0.15, "reversible": True},
    "write": {"tier": "medium", "delta_S": 0.20, "reversible": True},
    "build": {"tier": "medium", "delta_S": 0.20, "reversible": True},
    "commit": {"tier": "medium-high", "delta_S": 0.25, "reversible": True},
    "deploy": {"tier": "high", "delta_S": 0.80, "reversible": True},
    "execute": {"tier": "high", "delta_S": 0.50, "reversible": False},
    "restart": {"tier": "high", "delta_S": 0.60, "reversible": True},
    "send": {"tier": "high", "delta_S": 0.60, "reversible": False},
    "transfer": {"tier": "irreversible", "delta_S": 1.50, "reversible": False},
    "delete": {"tier": "irreversible", "delta_S": float("inf"), "reversible": False},
    "drop": {"tier": "irreversible", "delta_S": float("inf"), "reversible": False},
    "seal": {"tier": "irreversible", "delta_S": 1.00, "reversible": False},
    "judge": {"tier": "governance", "delta_S": -0.30, "reversible": True},
    "collapse": {"tier": "governance", "delta_S": -0.50, "reversible": True},
}

# DOMAIN SENSITIVITY (X-weighting factor per domain)
DOMAIN_X_WEIGHTS: dict[str, float] = {
    "general": 1.00,
    "coding": 0.90,
    "filesystem": 0.75,
    "earth": 0.85,
    "capital": 0.50,  # low X — high consequence
    "health": 0.40,  # low X — high consequence
    "identity": 0.30,  # very low X — irreversible
    "communication": 0.45,
    "governance": 0.60,
    "infrastructure": 0.55,
}


# ═══════════════════════════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class VerdictCode(str, Enum):
    """Collapse verdicts — measurement outcomes."""

    SEAL = "SEAL"  # all dials green, proceed
    SABAR = "SABAR"  # pause, gather evidence
    HOLD = "HOLD"  # restructure, request authority
    VOID = "VOID"  # reject, floor violation


@dataclass
class APEXState:
    """Four-dial governance state vector [A, P, E, X]."""

    A: float  # AKAL — intent clarity, task understanding ∈ [0, 1]
    P: float  # PRESENT — evidence freshness ∈ [0, 1]
    E: float  # ENERGY-ENTROPY — tool cost ∈ [0, 1] (higher = lower cost)
    X: float  # EXPLORATION-AMANAH — permissioned exploration ∈ [0, 1]
    phi: float = 0.0  # scar burden ∈ [0, ∞)
    intent: str = ""
    tool_name: str = ""
    tool_tier: str = "medium"
    domain: str = "general"
    session_id: str = ""
    actor_id: str = ""
    # ── LAW_ZEN_ATTENTION vectors (2026-09-01, additive — F13 pending) ──
    ha_attention_minutes: float = 0.0  # expected sovereign attention burn
    acr: float | None = None  # Attention Compression Ratio (None if Ha=0)


@dataclass
class CollapseVerdict:
    """Measurement outcome of the collapse trigger."""

    verdict: VerdictCode
    B: float  # geometric mean G = (A·P·E·X)^(1/4)
    B_phi: float  # scar-corrected B|Φ = B × exp(−Φ)
    gradient: float  # estimated ∂S_future / ∂action_now
    c_dark: float  # dark capability entropy
    omega_0: float  # humility noise floor
    dials: dict[str, float] = field(default_factory=dict)
    reason: str = ""
    phase: str = "OBSERVE_ONLY"  # Phase 1
    enforce: bool = False  # Phase 1: False
    timestamp: float = field(default_factory=time.time)
    receipt_hash: str = ""
    # ── LAW_ZEN_ATTENTION vectors (2026-09-01, additive — F13 pending) ──
    ha_attention_minutes: float = 0.0  # expected sovereign attention burn
    phi_scar_burden: float = 0.0  # expected scar-creation risk ∈ [0,1]
    acr: float | None = None  # ΔReality / ΔAttention (None if Ha = 0)


# ═══════════════════════════════════════════════════════════════════════════════
# CORE COLLAPSE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════


def _classify_tool_tier(tool_name: str, tool_tier: str = "") -> dict[str, Any]:
    """Classify a tool by entropy tier. Returns tier metadata."""
    tool_lower = tool_name.lower()
    for key, meta in TOOL_ENTROPY_TIERS.items():
        if key in tool_lower:
            return meta
    if tool_tier and tool_tier in TOOL_ENTROPY_TIERS:
        return TOOL_ENTROPY_TIERS[tool_tier]
    return {"tier": "medium", "delta_S": 0.10, "reversible": True}


def _classify_domain(intent: str, tool_name: str) -> str:
    """Classify the domain from intent and tool name."""
    intent_lower = (intent or "").lower()
    tool_lower = (tool_name or "").lower()

    domain_signals = {
        "capital": [
            "wealth",
            "capital",
            "npv",
            "emv",
            "kelly",
            "portfolio",
            "risk",
            "market",
            "trade",
            "xauusd",
        ],
        "earth": [
            "geox",
            "seismic",
            "basin",
            "petrophysics",
            "prospect",
            "well",
            "geology",
            "formation",
        ],
        "health": ["well", "health", "vitality", "fatigue", "homeostasis", "dignity", "readiness"],
        "identity": ["identity", "auth", "credential", "secret", "key", "cert", "password"],
        "communication": ["send", "message", "email", "telegram", "hermes", "notify", "publish"],
        "infrastructure": [
            "deploy",
            "restart",
            "caddy",
            "dns",
            "firewall",
            "vps",
            "docker",
            "systemctl",
        ],
        "governance": ["judge", "seal", "floor", "verdict", "constitution", "arif_"],
        "filesystem": ["file", "write", "delete", "edit", "rm ", "mv ", "cp "],
        "coding": ["code", "build", "test", "compile", "lint", "format", "refactor"],
    }

    for domain, signals in domain_signals.items():
        if any(s in intent_lower or s in tool_lower for s in signals):
            return domain

    return "general"


def _estimate_dial_A(intent: str, tool_name: str, domain: str) -> float:
    """AKAL — intent clarity and task understanding.

    High AKAL: intent is clear, tool class matches domain, no ambiguity.
    Low AKAL: intent is vague, tool mismatch, domain confusion.
    """
    if not intent:
        return 0.30  # no intent = low AKAL

    # Heuristic: longer, more specific intents → higher clarity
    intent_words = len(intent.split())
    specificity = min(intent_words / 20.0, 1.0)  # saturates at 20 words

    # Tool name match: if intent contains tool-related keywords
    tool_keywords = {
        "search": ["search", "find", "lookup", "query", "retrieve"],
        "read": ["read", "open", "view", "show", "display"],
        "write": ["write", "create", "save", "store"],
        "edit": ["edit", "modify", "change", "update", "fix"],
        "compute": ["compute", "calculate", "analyze", "evaluate", "assess"],
        "execute": ["execute", "run", "perform", "do"],
        "deploy": ["deploy", "ship", "release", "publish"],
        "judge": ["judge", "verdict", "decide", "determine", "rule"],
        "memory": ["remember", "recall", "memory", "history", "past"],
        "seal": ["seal", "record", "archive", "commit"],
    }

    tool_match = 0.5  # default
    for tool_class, keywords in tool_keywords.items():
        if any(k in intent.lower() for k in keywords):
            if tool_class in tool_name.lower():
                tool_match = 0.95
            else:
                tool_match = 0.70

    # Domain awareness bonus
    domain_bonus = 0.1 if domain != "general" else 0.0

    akal = 0.4 * specificity + 0.4 * tool_match + 0.2 * domain_bonus
    return max(0.0, min(1.0, akal))


def _estimate_dial_P(
    has_recent_observation: bool = True,
    has_evidence: bool = True,
    evidence_age_seconds: float = 0.0,
) -> float:
    """PRESENT — evidence freshness and grounding.

    High PRESENT: recent observation, fresh evidence, grounded claims.
    Low PRESENT: stale memory, unverified claims, hallucination risk.

    Phase 1: heuristic. Phase 2+: wired to arif_observe telemetry.
    """
    if not has_recent_observation:
        return 0.15  # no observation → very low PRESENT

    # Evidence age decay: 5 min fresh, 30 min stale, 1 hour expired
    if evidence_age_seconds < 300:
        freshness = 0.95
    elif evidence_age_seconds < 1800:
        freshness = 0.70  # 30 min
    elif evidence_age_seconds < 3600:
        freshness = 0.40  # 1 hour
    else:
        freshness = 0.15  # expired

    evidence_bonus = 0.10 if has_evidence else 0.0

    present = (
        0.6 * freshness + 0.3 * (1.0 if has_recent_observation else 0.0) + 0.1 * evidence_bonus
    )
    return max(0.0, min(1.0, present))


def _estimate_dial_E(tool_tier_meta: dict[str, Any]) -> float:
    """ENERGY-ENTROPY — tool cost and reversibility.

    High E: low cost, high reversibility (good — can act freely).
    Low E: high cost, irreversible (caution — act carefully).

    E is inverted from entropy: E = 1.0 means low entropy cost.
    """
    tier = tool_tier_meta.get("tier", "medium")
    reversible = tool_tier_meta.get("reversible", True)

    tier_scores = {
        "low": 0.95,
        "medium": 0.75,
        "medium-high": 0.55,
        "high": 0.35,
        "irreversible": 0.10,
        "governance": 0.90,
    }

    base = tier_scores.get(tier, 0.75)
    if not reversible:
        base *= 0.5  # irreversible penalty

    return max(0.0, min(1.0, base))


def _estimate_dial_X(domain: str, authority_level: str = "standard") -> float:
    """EXPLORATION-AMANAH — permissioned exploration.

    High X: safe to explore, experiment, try.
    Low X: constrained domain, limited authority, must be careful.
    """
    domain_weight = DOMAIN_X_WEIGHTS.get(domain, 1.0)

    authority_factors = {
        "sovereign": 1.0,
        "full": 0.90,
        "standard": 0.75,
        "limited": 0.50,
        "observe_only": 0.25,
        "none": 0.05,
    }

    auth_factor = authority_factors.get(authority_level.lower(), 0.75)

    x = domain_weight * auth_factor
    return max(0.0, min(1.0, x))


def _estimate_scar_burden(actor_id: str = "", session_id: str = "") -> float:
    """Φ — cumulative scar burden from constitutional memory.

    Phase 1: heuristic (0.0 for new sessions).
    Phase 2+: wired to arif_memory scar chain.
    """
    # Phase 1: heuristic — low scar for new sessions, moderate for established
    if session_id:
        return 0.05  # minimal scar for established sessions
    return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# SCAR SATURATION MATH (2026-08-02)
# ═══════════════════════════════════════════════════════════════════════════════
# Φ grows monotonically (F1 — scars immutable). Without cooling, B|Φ → 0 and
# the system becomes paralyzed. This is the constitutional second law.
#
#   Φ_eff = min(Φ, Φ_max)          — saturation at Φ_max = 2.5 → B|Φ ≥ 0.082
#   ΔΦ_cooling = 0.15 × convergence_strength  — cooldown per CONVERGING receipt
#
# Restoration: ~17 cooling events to recover from Φ_max = 2.5
# At Φ_max, B|Φ = B × exp(−2.5) ≈ B × 0.082 — floor for action


def saturate_scar(phi: float, phi_max: float = PHI_MAX) -> tuple[float, bool]:
    """Compute effective scar burden with saturation ceiling.

    Returns (phi_eff, is_saturated).
    When is_saturated=True, the system needs cooling before further action.
    """
    is_saturated = phi >= phi_max
    phi_eff = min(phi, phi_max)
    return phi_eff, is_saturated


def cool_scar(phi: float, convergence_strength: float = 0.5) -> float:
    """Reduce scar burden via cooling pathway.

    ΔΦ_cooling = PHI_COOLING_FACTOR × convergence_strength
    convergence_strength ∈ [0, 1] from forge_cool_drift CONVERGING receipts.

    Returns new phi after cooling.
    """
    delta = PHI_COOLING_FACTOR * max(0.0, min(1.0, convergence_strength))
    return max(0.0, phi - delta)


def scar_saturation_verdict(phi: float) -> str:
    """Return verdict based on scar saturation level.

    < 1.0  → SEAL (green)
    1.0-2.0 → SABAR (caution)
    2.0-2.5 → HOLD (near saturation)
    ≥ 2.5  → VOID (saturated — needs cooling)
    """
    if phi >= PHI_MAX:
        return "VOID"
    elif phi >= 2.0:
        return "HOLD"
    elif phi >= 1.0:
        return "SABAR"
    return "SEAL"


def _estimate_c_dark(state: APEXState) -> float:
    """C_dark = A·(1−P)·(1−X) — dark capability entropy.

    High when AKAL is high but PRESENT and AMANAH are low.
    Agent understands the task but lacks evidence and authority.
    This is the danger zone: capability without grounding.
    """
    return state.A * (1.0 - state.P) * (1.0 - state.X)


def _estimate_entropy_gradient(tool_tier_meta: dict[str, Any]) -> float:
    """∂S_future / ∂action_now — estimated entropy gradient.

    Negative = action reduces future entropy (good).
    Positive = action increases future entropy (caution).
    """
    delta_s = tool_tier_meta.get("delta_S", 0.10)
    return delta_s


def _compute_omega_0() -> float:
    """Ω₀ — humility noise floor ∈ [0.03, 0.05].

    F7: No fake certainty. Always keep some noise.
    """
    return OMEGA_0_MIN  # 0.03 — minimal humility, maximal confidence cap 0.97


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════


def collapse(
    intent: str,
    tool_name: str,
    tool_tier: str = "",
    domain: str = "",
    authority_level: str = "standard",
    has_recent_observation: bool = True,
    has_evidence: bool = True,
    evidence_age_seconds: float = 0.0,
    session_id: str = "",
    actor_id: str = "",
    enforce: bool | None = None,
    # ── LAW_ZEN_ATTENTION inputs (additive, F13 pending) ──
    ha_attention_minutes: float = 0.0,
    phi_scar_burden: float = 0.0,
    delta_reality: float = 0.0,
) -> CollapseVerdict:
    """
    APEX COLLAPSE TRIGGER — Measurement-Theoretic Intelligence.

    Computes the four-dial state [A, P, E, X], scar burden Φ, and produces
    a pre-tool collapse verdict. This is the Euclidean gate: the agent cannot
    reach for a tool without first being judged.

    Phase 1 (OBSERVE-ONLY): compute, log, NEVER block.
    Phase 2+: enforce — block non-SEAL verdicts.

    Args:
        intent: Natural language description of what the agent intends to do
        tool_name: Name of the tool being called (e.g., "forge_execute", "geox_seismic_compute")
        tool_tier: Optional override for tool entropy tier
        domain: Optional domain override (auto-classified if empty)
        authority_level: Agent's authority level
        has_recent_observation: Whether agent has recent evidence
        has_evidence: Whether agent has any evidence at all
        evidence_age_seconds: Age of most recent evidence
        session_id: Governing session ID
        actor_id: Actor ID
        enforce: Override enforcement flag (default: COLLAPSE_TRIGGER_ENFORCE)

    Returns:
        CollapseVerdict with verdict, dials, gradient, and receipt hash
    """
    if enforce is None:
        enforce = COLLAPSE_TRIGGER_ENFORCE

    # ── Classify ──────────────────────────────────────────────────────────
    tool_meta = _classify_tool_tier(tool_name, tool_tier)
    if not domain:
        domain = _classify_domain(intent, tool_name)

    # ── Compute four dials ───────────────────────────────────────────────
    A = _estimate_dial_A(intent, tool_name, domain)
    P = _estimate_dial_P(has_recent_observation, has_evidence, evidence_age_seconds)
    E = _estimate_dial_E(tool_meta)
    X = _estimate_dial_X(domain, authority_level)

    # ── Scar burden ──────────────────────────────────────────────────────
    phi = _estimate_scar_burden(actor_id, session_id)

    # ── Geometric mean (non-compensatory) ────────────────────────────────
    B = (A * P * E * X) ** 0.25

    # ── Scar-corrected present coherence ─────────────────────────────────
    B_phi = B * math.exp(-phi)

    # ── Dark capability entropy ──────────────────────────────────────────
    state = APEXState(
        A=A,
        P=P,
        E=E,
        X=X,
        phi=phi,
        intent=intent,
        tool_name=tool_name,
        tool_tier=tool_meta["tier"],
        domain=domain,
        session_id=session_id,
        actor_id=actor_id,
    )
    c_dark = _estimate_c_dark(state)

    # ── Entropy gradient ─────────────────────────────────────────────────
    gradient = _estimate_entropy_gradient(tool_meta)

    # ── Humility noise floor ─────────────────────────────────────────────
    omega_0 = _compute_omega_0()

    # ── Verdict computation ──────────────────────────────────────────────
    # Lexicographic checks (non-compensatory — any violation → VOID)
    if A < DIAL_FLOOR:
        verdict = VerdictCode.VOID
        reason = f"AKAL below floor: A={A:.3f} < {DIAL_FLOOR}"
    elif P < DIAL_FLOOR:
        verdict = VerdictCode.VOID
        reason = f"PRESENT below floor: P={P:.3f} < {DIAL_FLOOR}"
    elif phi >= PHI_MAX:
        verdict = VerdictCode.VOID
        reason = f"Scar saturation: Φ={phi:.3f} ≥ {PHI_MAX} — needs cooling"
    elif tool_meta["tier"] == "irreversible" and X < DIAL_FLOOR:
        verdict = VerdictCode.VOID
        reason = f"Irreversible tool below AMANAH floor: X={X:.3f} < {DIAL_FLOOR}"
    elif c_dark > C_DARK_CAP:
        verdict = VerdictCode.HOLD
        reason = f"Dark capability entropy above cap: C_dark={c_dark:.3f} > {C_DARK_CAP}"
    elif B_phi < B_CORRECTED_SEAL_THRESHOLD:
        verdict = VerdictCode.HOLD
        reason = f"Scar-corrected coherence below threshold: B|Φ={B_phi:.3f} < {B_CORRECTED_SEAL_THRESHOLD}"
    elif gradient > GRADIENT_SABAR_THRESHOLD and not tool_meta["reversible"]:
        verdict = VerdictCode.SABAR
        reason = f"Positive entropy gradient on irreversible tool: ∂S={gradient:.3f} > {GRADIENT_SABAR_THRESHOLD}"
    elif B_phi < 0.70:
        verdict = VerdictCode.SABAR
        reason = f"Moderate coherence: B|Φ={B_phi:.3f} — gather more evidence"
    else:
        verdict = VerdictCode.SEAL
        reason = f"All dials green: B|Φ={B_phi:.3f}, C_dark={c_dark:.3f}, ∂S={gradient:.3f}"

    # ── LAW_ZEN_ATTENTION (additive, F13 pending) ────────────────────
    # No sovereign attention shall be spent unless expected entropy
    # reduction exceeds expected scar creation. When enforced, a would-be
    # SEAL that burns attention below the ACR floor collapses to HOLD.
    acr_value: float | None = None
    zen_reason = ""
    if ha_attention_minutes > 0:
        acr_value = delta_reality / ha_attention_minutes
        if acr_value < ACR_FLOOR:
            zen_reason = (
                f"ACR={acr_value:.4f} < {ACR_FLOOR} — attention burn "
                f"({ha_attention_minutes:.2f} min) exceeds reality gain"
            )
        elif phi_scar_burden > PHI_SCAR_CEILING:
            zen_reason = (
                f"Scar risk {phi_scar_burden:.2f} > ceiling {PHI_SCAR_CEILING}"
            )
    if zen_reason and ZEN_ATTENTION_ENFORCE and verdict == VerdictCode.SEAL:
        verdict = VerdictCode.HOLD
        reason = f"LAW_ZEN_ATTENTION HOLD: {zen_reason}"

    # ── Phase 1 override: observe-only, never block ──────────────────────
    if not enforce:
        reason = f"[Phase 1 OBSERVE-ONLY] Would be {verdict.value}: {reason}"
        verdict = VerdictCode.SEAL  # always SEAL in Phase 1

    # ── Receipt hash ─────────────────────────────────────────────────────
    receipt_data = {
        "verdict": verdict.value,
        "A": round(A, 4),
        "P": round(P, 4),
        "E": round(E, 4),
        "X": round(X, 4),
        "B": round(B, 4),
        "B_phi": round(B_phi, 4),
        "phi": round(phi, 4),
        "c_dark": round(c_dark, 4),
        "omega_0": round(omega_0, 4),
        "gradient": round(gradient, 4),
        "intent": intent[:100],
        "tool_name": tool_name,
        "domain": domain,
        "enforce": enforce,
        # LAW_ZEN_ATTENTION vectors (additive, F13 pending)
        "ha_attention_minutes": round(ha_attention_minutes, 4),
        "phi_scar_burden": round(phi_scar_burden, 4),
        "acr": round(acr_value, 4) if acr_value is not None else None,
        "timestamp": time.time(),
    }
    receipt_hash = hashlib.sha256(json.dumps(receipt_data, sort_keys=True).encode()).hexdigest()[
        :16
    ]

    return CollapseVerdict(
        verdict=verdict,
        B=B,
        B_phi=B_phi,
        gradient=gradient,
        c_dark=c_dark,
        omega_0=omega_0,
        dials={"A": A, "P": P, "E": E, "X": X, "phi": phi},
        reason=reason,
        phase="OBSERVE_ONLY" if not enforce else "ENFORCEMENT",
        enforce=enforce,
        timestamp=time.time(),
        ha_attention_minutes=ha_attention_minutes,
        phi_scar_burden=phi_scar_burden,
        acr=acr_value,
        receipt_hash=receipt_hash,
    )


def collapse_json(
    intent: str,
    tool_name: str,
    **kwargs,
) -> dict[str, Any]:
    """JSON-serializable collapse trigger. For arifFLOW ingestion."""
    result = collapse(intent=intent, tool_name=tool_name, **kwargs)
    return {
        "verdict": result.verdict.value,
        "B": round(result.B, 4),
        "B_phi": round(result.B_phi, 4),
        "gradient": round(result.gradient, 4),
        "c_dark": round(result.c_dark, 4),
        "omega_0": round(result.omega_0, 4),
        "dials": result.dials,
        "reason": result.reason,
        "phase": result.phase,
        "enforce": result.enforce,
        "timestamp": result.timestamp,
        "receipt_hash": result.receipt_hash,
        "intent": intent[:200],
        "tool_name": tool_name,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-TEST (invoked on import in Phase 1)
# ═══════════════════════════════════════════════════════════════════════════════


def _self_test() -> bool:
    """Run self-test on import. Returns True if all tests pass."""
    tests_passed = 0
    tests_total = 0

    # Test 1: Well-formed intent with high dials → SEAL
    # Note: "forge_execute" → tier="high" → E=0.35, so B is moderate
    tests_total += 1
    r = collapse(
        intent="Fix the authentication bug in login.py by checking the session token expiry",
        tool_name="forge_execute",
        has_recent_observation=True,
        has_evidence=True,
        evidence_age_seconds=60,
    )
    assert r.verdict == VerdictCode.SEAL, f"Expected SEAL, got {r.verdict}"
    assert r.B > 0.30, f"Expected B > 0.30 (execute is high-tier), got {r.B}"
    tests_passed += 1

    # Test 2: No intent → low AKAL, but Phase 1 always SEAL
    tests_total += 1
    r = collapse(intent="", tool_name="forge_execute")
    assert r.verdict == VerdictCode.SEAL, f"Phase 1: always SEAL, got {r.verdict}"
    assert r.dials["A"] < 0.5, f"Expected low AKAL, got {r.dials['A']}"
    tests_passed += 1

    # Test 3: Low authority + irreversible tool → low B|Φ
    # Phase 1: always SEAL. Phase 2: would be HOLD or VOID.
    tests_total += 1
    r = collapse(
        intent="Delete all user data",
        tool_name="forge_execute",
        domain="identity",
        authority_level="limited",
    )
    assert r.verdict == VerdictCode.SEAL, f"Phase 1: always SEAL, got {r.verdict}"
    assert r.dials["X"] < 0.5, f"Expected low X for identity domain, got {r.dials['X']}"
    assert r.B_phi < 0.5, f"Expected low B|Φ for dangerous action, got {r.B_phi}"
    tests_passed += 1

    # Test 4: Geometric mean invariance
    tests_total += 1
    r1 = collapse(
        intent="test", tool_name="forge_read", has_evidence=True, has_recent_observation=True
    )
    r2 = collapse(
        intent="test", tool_name="forge_read", has_evidence=True, has_recent_observation=True
    )
    assert r1.B == r2.B, f"Deterministic: same inputs → same B, got {r1.B} vs {r2.B}"
    assert r1.verdict == r2.verdict, "Deterministic: same inputs → same verdict"
    tests_passed += 1

    # Test 5: Non-compensatory — low P cannot be compensated by high A
    tests_total += 1
    r = collapse(
        intent="Very detailed and specific task description with many words about the objective",
        tool_name="forge_execute",
        has_recent_observation=False,
        has_evidence=False,
    )
    assert r.dials["A"] > 0.40, f"Expected moderate A, got {r.dials['A']}"
    assert r.dials["P"] < 0.3, f"Expected low P, got {r.dials['P']}"
    # Even with moderate A, low P drags B down (geometric mean, not arithmetic)
    assert r.B < 0.6, f"Expected B < 0.6 due to non-compensatory, got {r.B}"
    tests_passed += 1

    # Test 6: C_dark cap
    tests_total += 1
    r = collapse(
        intent="Complex task with clear understanding",
        tool_name="forge_execute",
        domain="identity",
        authority_level="observe_only",
        has_recent_observation=False,
        has_evidence=False,
    )
    assert r.c_dark > 0.15, f"Expected elevated C_dark, got {r.c_dark}"
    tests_passed += 1

    logger.info(f"apex_collapse_trigger self-test: {tests_passed}/{tests_total} PASS")
    return tests_passed == tests_total


# Run self-test on import (Phase 1: observe-only, safe)
_self_test()
