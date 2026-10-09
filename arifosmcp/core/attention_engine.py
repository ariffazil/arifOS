"""
ATTENTION_ENGINE_v1 — Constitutional Attention Allocator
══════════════════════════════════════════════════════════

Replaces low-signal keyword filtering with governance-aware attention allocation.

Not a safety filter. Not an execution blocker. Not a keyword scanner.
It is a PRIORITIZATION LAYER that computes which aspects of an input
deserve governance resources.

ATTENTION ENGINE IS:
  A constitutional primitive that computes attention profiles.

ATTENTION ENGINE IS NOT:
  A safety filter, execution blocker, keyword scanner, or enforcement layer.

Six attention dimensions:
  A1 IDENTITY    — Who is acting? (anonymous → sovereign)
  A2 SOVEREIGNTY — Does this touch governance/state?
  A3 IRREVERSIBILITY — Can this change reality without undo?
  A4 WITNESS     — Is evidence/receipt available?
  A5 NOVELTY     — Is this new or repeated?
  A6 CONFIDENCE  — How certain is the current state?

Output: AttentionProfile — a typed dict with scores 0.0–1.0 per dimension.
         The consumer (judge, law, executor) decides what threshold to apply.

Ditempa Bukan Diberi — Forged, Not Given.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AttentionProfile:
    """
    Constitutional attention profile for a single action/input.

    Each dimension is 0.0–1.0:
      0.0 = no attention needed (routine, reversible, witnessed, repeated)
      1.0 = maximum attention required (sovereign, irreversible, unwitnessed, novel)

    The profile itself does NOT decide. It informs the Judge what deserves
    governance resources.
    """

    identity: float = 0.0          # A1: actor binding quality
    sovereignty: float = 0.0       # A2: touches governance/constitutional state
    irreversibility: float = 0.0   # A3: reality mutation without undo
    witness: float = 0.0           # A4: evidence/receipt availability (high = NEEDS witness)
    novelty: float = 0.0           # A5: new vs repeated pattern
    confidence: float = 1.0        # A6: inverse of uncertainty (1.0 = certain, 0.0 = unknown)

    # Metadata — never affects verdict, only traceability
    actor_id: str | None = None
    session_id: str | None = None
    action_type: str | None = None
    action_risk_tier: str | None = None  # "public" | "standard" | "critical" | "sovereign"

    @property
    def total_attention(self) -> float:
        """Sum of all attention dimensions. Rough gauge of governance load."""
        return (
            self.identity
            + self.sovereignty
            + self.irreversibility
            + self.witness
            + self.novelty
            + (1.0 - self.confidence)
        )

    @property
    def max_dimension(self) -> tuple[str, float]:
        """Which single dimension demands most attention?"""
        dims = {
            "identity": self.identity,
            "sovereignty": self.sovereignty,
            "irreversibility": self.irreversibility,
            "witness": self.witness,
            "novelty": self.novelty,
            "uncertainty": 1.0 - self.confidence,
        }
        return max(dims.items(), key=lambda x: x[1])

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["total_attention"] = self.total_attention
        d["max_dimension"] = self.max_dimension
        return d

    def __str__(self) -> str:
        dims = [
            f"id={self.identity:.2f}",
            f"sov={self.sovereignty:.2f}",
            f"irr={self.irreversibility:.2f}",
            f"wit={self.witness:.2f}",
            f"nov={self.novelty:.2f}",
            f"conf={self.confidence:.2f}",
        ]
        return f"AttentionProfile({', '.join(dims)})"


# ── Tier baselines ──────────────────────────────────────────────────────
# Pre-computed attention profiles for known risk tiers.
# These are STARTING POINTS — the caller can override individual dimensions.

_TIER_BASELINES: dict[str, AttentionProfile] = {
    "public": AttentionProfile(
        identity=0.1,
        sovereignty=0.0,
        irreversibility=0.0,
        witness=0.0,
        novelty=0.1,
        confidence=1.0,
    ),
    "standard": AttentionProfile(
        identity=0.3,
        sovereignty=0.0,
        irreversibility=0.2,
        witness=0.3,
        novelty=0.2,
        confidence=0.9,
    ),
    "critical": AttentionProfile(
        identity=0.7,
        sovereignty=0.3,
        irreversibility=0.6,
        witness=0.7,
        novelty=0.3,
        confidence=0.7,
    ),
    "sovereign": AttentionProfile(
        identity=1.0,
        sovereignty=1.0,
        irreversibility=1.0,
        witness=0.9,
        novelty=0.5,
        confidence=0.8,
    ),
}


def compute_attention(
    tool_name: str = "",
    params: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    risk_tier: str | None = None,
    is_reversible: bool = True,
    has_evidence: bool = False,
    is_novel: bool = False,
    confidence: float = 1.0,
    sovereign_domain: bool = False,
) -> AttentionProfile:
    """
    Compute an AttentionProfile for a given action.

    This is a PURE FUNCTION — it does not block, filter, or enforce.
    It only allocates attention scores. The consumer decides thresholds.

    Parameters
    ----------
    tool_name : str
        The canonical tool name (e.g., "arif_forge", "arif_read").
    params : dict | None
        Tool call parameters.
    actor_id : str | None
        Actor identifier. None = anonymous → raises identity attention.
    session_id : str | None
        Session binding. None = unbound → raises identity attention.
    risk_tier : str | None
        "public" | "standard" | "critical" | "sovereign". Sets baseline.
    is_reversible : bool
        False → raises irreversibility attention.
    has_evidence : bool
        False → raises witness attention (needs evidence).
    is_novel : bool
        True → raises novelty attention.
    confidence : float
        0.0–1.0. Inverted for attention (low confidence = high attention).
    sovereign_domain : bool
        Touches kernel, law, governance state → raises sovereignty attention.

    Returns
    -------
    AttentionProfile
    """
    params = params or {}

    # Resolve risk tier from params if not explicit
    if risk_tier is None:
        risk_tier = params.get("risk_tier", "standard")

    # Start from tier baseline
    profile = AttentionProfile()
    baseline = _TIER_BASELINES.get(risk_tier or "standard", _TIER_BASELINES["standard"])

    # Apply baseline values where the caller hasn't overridden
    profile.identity = baseline.identity
    profile.sovereignty = baseline.sovereignty
    profile.irreversibility = baseline.irreversibility
    profile.witness = baseline.witness
    profile.novelty = baseline.novelty
    profile.confidence = baseline.confidence

    # ── A1: Identity Attention ──────────────────────────────────────
    # Anonymous or unbound actors demand full identity scrutiny
    if actor_id is None and session_id is None:
        profile.identity = 1.0
    elif actor_id is None:
        profile.identity = max(profile.identity, 0.5)

    # ── A2: Sovereign Attention ─────────────────────────────────────
    if sovereign_domain:
        profile.sovereignty = 1.0

    # Sovereign-tier tools always touch governance
    if risk_tier == "sovereign":
        profile.sovereignty = max(profile.sovereignty, 0.9)

    # ── A3: Irreversibility Attention ───────────────────────────────
    if not is_reversible:
        profile.irreversibility = 1.0

    # ── A4: Witness Attention ───────────────────────────────────────
    # High score = needs witness (evidence not yet present)
    if not has_evidence:
        profile.witness = max(profile.witness, 0.7)
    else:
        profile.witness = max(0.0, profile.witness - 0.3)

    # ── A5: Novelty Attention ──────────────────────────────────────
    if is_novel:
        profile.novelty = 1.0

    # ── A6: Confidence ──────────────────────────────────────────────
    # This is the INVERSE: low confidence = high attention demand
    profile.confidence = max(0.0, min(1.0, confidence))

    # ── Metadata ────────────────────────────────────────────────────
    profile.actor_id = actor_id
    profile.session_id = session_id
    profile.action_type = tool_name
    profile.action_risk_tier = risk_tier

    logger.debug(f"ATTENTION computed for {tool_name}: {profile}")
    return profile


def attention_verdict(profile: AttentionProfile) -> dict[str, Any]:
    """
    Translate an AttentionProfile into governance recommendations.

    This is the bridge between attention allocation and judgment.
    It does NOT enforce — it only recommends what ceremony is appropriate.

    Returns
    -------
    dict with keys:
      "recommended_ceremony" : "none" | "witness" | "judge" | "sovereign"
      "requires_reversibility_check" : bool
      "requires_witness" : bool
      "attention_summary" : str
    """
    ceremony = "none"
    requires_witness = False
    requires_reversibility = False

    # High irreversibility → needs reversibility check
    if profile.irreversibility >= 0.7:
        requires_reversibility = True
        ceremony = "judge"

    # High witness demand → needs evidence ceremony
    if profile.witness >= 0.7:
        requires_witness = True
        if ceremony == "none":
            ceremony = "witness"

    # High sovereignty → sovereign ceremony
    if profile.sovereignty >= 0.8:
        ceremony = "sovereign"

    # Low confidence → escalate ceremony
    if profile.confidence < 0.5:
        ceremony = "judge" if ceremony == "none" else ceremony

    # Total attention gauge
    total = profile.total_attention
    if total >= 4.0 and ceremony == "none":
        ceremony = "judge"
    elif total >= 2.5 and ceremony == "none":
        ceremony = "witness"

    return {
        "recommended_ceremony": ceremony,
        "requires_reversibility_check": requires_reversibility,
        "requires_witness": requires_witness,
        "attention_summary": str(profile),
    }


def attention_delta(old: AttentionProfile, new: AttentionProfile) -> AttentionProfile:
    """
    Compute the attention delta between two profiles.
    Useful for detecting shifts in governance requirements over time.
    """
    return AttentionProfile(
        identity=new.identity - old.identity,
        sovereignty=new.sovereignty - old.sovereignty,
        irreversibility=new.irreversibility - old.irreversibility,
        witness=new.witness - old.witness,
        novelty=new.novelty - old.novelty,
        confidence=new.confidence - old.confidence,
        actor_id=new.actor_id or old.actor_id,
        session_id=new.session_id or old.session_id,
        action_type=new.action_type or old.action_type,
        action_risk_tier=new.action_risk_tier or old.action_risk_tier,
    )


# ── Quick attention probe (for CLI / health checks) ───────────────────

def quick_attention(
    actor_id: str | None = None,
    risk_tier: str = "standard",
    is_reversible: bool = True,
) -> AttentionProfile:
    """
    Minimal attention computation for health checks and diagnostics.
    Uses defaults for everything except the three key parameters.
    """
    return compute_attention(
        tool_name="quick_probe",
        actor_id=actor_id,
        risk_tier=risk_tier,
        is_reversible=is_reversible,
        has_evidence=True,
        is_novel=False,
        confidence=0.9,
    )
