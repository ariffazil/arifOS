"""
ARIFOS CONSTITUTIONAL MAP (v2026.05.05-KANON-SSCT)
═══════════════════════════════════════════════════════════════════════════════

SOLE SOURCE OF TRUTH for the 13 canonical MCP tools.
All arif_* naming. No governance surface, no CC modes as separate tools.

MACHINERY:
  - CANONICAL_TOOLS   : 13-tool registry (name → spec with floors, stage, lane)
  - Floor enum        : F01–F13 with Eureka-wired threshold logic
  - TrinityLane      : AGI | ASI | APEX
  - ToolStage        : 000–999 metabolic stage codes
  - _TOOL_INPUT_SCHEMAS  : canonical I/O type signatures (F10 ONTOLOGY enforced)
  - _TOOL_OUTPUT_SCHEMAS : canonical output envelope per tool
  - validate_tool_response_schema()  : F2 Nine-Signal contract checker
  - check_schema_coverage()          : all-13 tools have schemas = CI pass
  - enforce_irreversibility_guard() : F1 hard gate

EUREKA INSIGHTS WIRING (from EUREKA_INSIGHTS_SEAL_v2026.04.07):
  Each floor threshold is derived from physics, not policy.
  See: 000/FLOORS/F0X.md for formal proof of each threshold.

Ditempa Bukan Diberi.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR DEFINITIONS — 13 Constitutional Laws as Physics
# ═══════════════════════════════════════════════════════════════════════════════


class Floor(str, Enum):
    """
    F01–F13. Each Floor is a physics equation, not a policy rule.
    Eureka wired: thresholds derived from EUREKA_INSIGHTS_SEAL_v2026.04.07.
    """

    F01_AMANAH = "F01"  # Reversibility as conservation law (∃ undo)
    F02_TRUTH = "F02"  # Uncertainty as first-class citizen (τ ≥ 0.99)
    F03_WITNESS = "F03"  # Tri-witness consensus (W₃ ≥ 0.75)
    F04_CLARITY = "F04"  # Entropy reduction as progress (ΔS ≤ 0)
    F05_PEACE = "F05"  # Non-destruction as baseline (P² ≥ 1.0)
    F06_EMPATHY = "F06"  # RASA as protocol (κᵣ ≥ 0.70)
    F07_HUMILITY = "F07"  # Uncertainty quantified (Ω ∈ [0.03, 0.05])
    F08_GENIUS = "F08"  # Systemic health (G ≥ 0.80)
    F09_ANTIHANTU = "F09"  # Pattern recognition of deception (C_dark ≤ 0.30)
    F10_ONTOLOGY = "F10"  # Structural coherence (category lock / immutability)
    F11_AUTH = "F11"  # Verify identity (HUMAN_APPROVAL gate)
    F12_INJECTION = "F12"  # Sanitize inputs (injection_probability < 0.85)
    F13_SOVEREIGN = "F13"  # Human veto absolute (final authority)


class TrinityLane(str, Enum):
    AGI = "AGI"  # Tactical execution (000–777)
    ASI = "ASI"  # Strategic judgment (888)
    APEX = "APEX"  # Authority resolution (999)


class ToolStage(str, Enum):
    INIT = "000"
    OBSERVE = "111"
    EVIDENCE = "222"
    REASON = "333"
    CRITIQUE = "444"
    REPLY = "444r"
    ROUTE = "555"
    MEMORY = "555m"
    FORGE = "666"
    GATEWAY = "666g"
    MEASURE = "777"
    JUDGE = "888"
    SEAL = "999"


# ═══════════════════════════════════════════════════════════════════════════════
# RISK CLASSIFICATION TIER (C0–C5) — Right-sized governance mapper
# Derived from LLM_INVARIANTS_SEAL_v2026.05.05 / Agent Kernel Paradox
#
# arifOS line: "Right governance at the right time."
# Governance is not maximum everywhere — it is right-sized per consequence.
#
# | Class | Consequence  | Governance Mode       | Human Confirmation |
# |-------|-------------|----------------------|--------------------|
# | C0    | Negligible  | Vanilla-like         | Not required       |
# | C1    | Low         | Light trace          | Not required       |
# | C2    | Medium      | Trace + self-review  | Optional            |
# | C3    | High        | Evidence gate + hold | Required           |
# | C4    | Very High   | Full floor review    | Required (F13)     |
# | C5    | Critical    | SEAL + human sign-off| Required + vault   |
# ═══════════════════════════════════════════════════════════════════════════════


class RiskClass(str, Enum):
    """
    Risk consequence tier — governs HOW MUCH friction the kernel applies.

    The kernel paradox: governance looks like drag when nothing goes wrong,
    but genius when something could go wrong. RiskClass is how we right-size it.
    """

    C0_GRAMMAR = "C0"  # Negligible — grammar, tone, formatting
    C1_DRAFT = "C1"  # Low — internal drafts, notes, brainstorming
    C2_REVIEW = "C2"  # Medium — code review, testing, analysis
    C3_PUBLIC = "C3"  # High — public posts, emails, reports
    C4_LEGAL_MONEY = "C4"  # Very High — legal, financial, HR, investment
    C5_IRREVERSIBLE = "C5"  # Critical — irreversible, production write, money movement

    @property
    def governance_mode(self) -> str:
        """What governance posture does this class demand?"""
        return _RISK_GOVERNANCE_TABLE[self].governance_mode

    @property
    def requires_human_confirmation(self) -> bool:
        """Does this class require human approval before action?"""
        return _RISK_GOVERNANCE_TABLE[self].requires_human_confirmation

    @property
    def floors_activated(self) -> list[str]:
        """Which floors are most critical at this risk tier?"""
        return _RISK_GOVERNANCE_TABLE[self].floors_activated

    @property
    def description(self) -> str:
        """Human-readable consequence description."""
        return _RISK_GOVERNANCE_TABLE[self].description


@dataclass
class RiskTierConfig:
    governance_mode: str  # "vanilla" | "light" | "standard" | "strict" | "seal"
    requires_human_confirmation: bool
    floors_activated: list[str]  # Most relevant F-codes for this tier
    description: str


_RISK_GOVERNANCE_TABLE: dict[RiskClass, RiskTierConfig] = {
    RiskClass.C0_GRAMMAR: RiskTierConfig(
        governance_mode="vanilla",
        requires_human_confirmation=False,
        floors_activated=["F09", "F10"],
        description="Grammar, spelling, tone, formatting. Zero irreversible consequence.",
    ),
    RiskClass.C1_DRAFT: RiskTierConfig(
        governance_mode="light",
        requires_human_confirmation=False,
        floors_activated=["F04", "F09", "F10"],
        description="Internal drafts, brainstorming, notes. Reversible. No external exposure.",
    ),
    RiskClass.C2_REVIEW: RiskTierConfig(
        governance_mode="standard",
        requires_human_confirmation=False,
        floors_activated=["F02", "F03", "F04", "F07", "F08"],
        description=(
            "Code review, testing, analysis, summaries. Evidence-backed. Moderate exposure."
        ),
    ),
    RiskClass.C3_PUBLIC: RiskTierConfig(
        governance_mode="strict",
        requires_human_confirmation=True,
        floors_activated=["F01", "F02", "F03", "F04", "F05", "F06", "F09", "F12"],
        description="Public posts, emails to third parties, published documents. Reputation risk.",
    ),
    RiskClass.C4_LEGAL_MONEY: RiskTierConfig(
        governance_mode="strict",
        requires_human_confirmation=True,
        floors_activated=["F01", "F02", "F03", "F05", "F06", "F11", "F12", "F13"],
        description="Legal claims, financial decisions, HR actions, investments. High consequence.",
    ),
    RiskClass.C5_IRREVERSIBLE: RiskTierConfig(
        governance_mode="seal",
        requires_human_confirmation=True,
        floors_activated=["F01", "F02", "F03", "F05", "F06", "F11", "F12", "F13"],
        description=(
            "Production writes, database deletes, money movement, regulatory filings. Irreversible."
        ),
    ),
}


@dataclass
class RiskDecision:
    """
    Return type for preflight() — the kernel's pre-flight check result.

    This is what the external AI described as:
        decision = kernel.preflight(action="send_email", risk=RiskClass.C3, reversible=False)
        if decision.allowed:
            result = send_email()
            kernel.audit(result)
        else:
            print(decision.reason)
    """

    allowed: bool  # Can the action proceed?
    risk_class: RiskClass  # What tier was assigned
    governance_mode: str  # "vanilla" | "light" | "standard" | "strict" | "seal"
    verdict: str  # "PROCEED" | "HOLD" | "VOID"
    reason: str  # Human-readable gate message
    floors_activated: list[str]  # Which floors are on watch
    requires_human_confirmation: bool  # F13 gate — human must sign off
    human_approval_reference: str | None  # If confirmed, the approval token / session_ref
    uncertainty_band: tuple[float, float]  # (lower, upper) — F07 Ω band if evidence is thin
    preflight_passed: bool  # Did the action pass all preflight checks?


def preflight(
    action: str,
    risk_class: RiskClass,
    reversible: bool,
    evidence_quality: float = 1.0,  # 0.0–1.0; 1.0 = full evidence
    user_intent: str | None = None,
    session_ref: str | None = None,
) -> RiskDecision:
    """
    arifOS preflight check — the public API for right-sized governance.

    This is the function the external AI described:
        from arifos import Kernel, RiskClass
        kernel = Kernel(policy="arifos.yaml")
        decision = kernel.preflight(
            user_intent="Send this email to the CEO",
            action="send_email",
            risk=RiskClass.C3,
            reversible=False,
        )

    Returns a RiskDecision that tells the caller:
      - allowed: can this proceed?
      - verdict: PROCEED / HOLD / VOID
      - reason: why
      - requires_human_confirmation: does F13 SOVEREIGN require human sign-off?
      - governance_mode: how much governance was applied
      - floors_activated: which floors are on watch
      - uncertainty_band: F07 Ω range if evidence is weak
    """
    tier = _RISK_GOVERNANCE_TABLE[risk_class]

    # ── C5 special: vault seal required — check FIRST before F01 gate ───────
    if risk_class == RiskClass.C5_IRREVERSIBLE:
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode="seal",
            verdict="VOID",
            reason=(
                f"C5 CRITICAL: '{action}' is class {risk_class.value} — irreversible, "
                f"high-consequence. arifOS will not execute this autonomously. "
                f"Required: (1) human confirmation, (2) VAULT999 seal entry, "
                f"(3) rollback plan on record. Contact Arif for C5 authorization."
            ),
            floors_activated=["F01", "F11", "F12", "F13"],
            requires_human_confirmation=True,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.05),
            preflight_passed=False,
        )

    # ── Irreversibility override (F01 AMANAH) ─────────────────────────────────
    if not reversible and tier.governance_mode in ("strict", "seal"):
        # Irreversible + high-risk → always HOLD
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode="seal",
            verdict="HOLD",
            reason=(
                f"F01 AMANAH: {action} is irreversible and class {risk_class.value}. "
                f"Evidence gate + human confirmation required. "
                f"Escalation: 888_HOLD"
            ),
            floors_activated=["F01", *tier.floors_activated],
            requires_human_confirmation=True,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.05),
            preflight_passed=False,
        )

    # ── Evidence quality check (F02 TRUTH) ────────────────────────────────────
    if evidence_quality < 0.5 and tier.governance_mode in ("strict", "seal"):
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode="strict",
            verdict="HOLD",
            reason=(
                f"F02 TRUTH: evidence quality {evidence_quality:.0%} is insufficient for "
                f"{risk_class.value} actions. Required: ≥50% evidence confidence. "
                f"Reduce claim strength or gather more evidence."
            ),
            floors_activated=["F02", *tier.floors_activated],
            requires_human_confirmation=tier.requires_human_confirmation,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.10),  # Wider Ω band — low evidence
            preflight_passed=False,
        )

    # ── Human confirmation gate (F13 SOVEREIGN) ───────────────────────────────
    if tier.requires_human_confirmation and not session_ref:
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode=tier.governance_mode,
            verdict="HOLD",
            reason=(
                f"F13 SOVEREIGN: {risk_class.value} action '{action}' requires human "
                f"confirmation before execution. Provide session_ref to proceed. "
                f"Compute can advise. Human must decide."
            ),
            floors_activated=["F13", *tier.floors_activated],
            requires_human_confirmation=True,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.05),
            preflight_passed=False,
        )

    # ── C5 special: vault seal required ──────────────────────────────────────
    if risk_class == RiskClass.C5_IRREVERSIBLE:
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode="seal",
            verdict="VOID",
            reason=(
                f"C5 CRITICAL: '{action}' is class {risk_class.value} — irreversible, "
                f"high-consequence. arifOS will not execute this autonomously. "
                f"Required: (1) human confirmation, (2) VAULT999 seal entry, "
                f"(3) rollback plan on record. Contact Arif for C5 authorization."
            ),
            floors_activated=["F01", "F11", "F12", "F13"],
            requires_human_confirmation=True,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.05),
            preflight_passed=False,
        )

    # ── PROCEED — all gates passed ─────────────────────────────────────────────
    _conf = (
        "Human confirmation on record."
        if session_ref
        else "No human confirmation required for this tier."
    )
    return RiskDecision(
        allowed=True,
        risk_class=risk_class,
        governance_mode=tier.governance_mode,
        verdict="PROCEED",
        reason=(
            f"{risk_class.value} action '{action}' cleared preflight. "
            f"Governance: {tier.governance_mode}. "
            f"{_conf}"
        ),
        floors_activated=tier.floors_activated,
        requires_human_confirmation=tier.requires_human_confirmation,
        human_approval_reference=session_ref,
        uncertainty_band=(0.03, 0.05),
        preflight_passed=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 13 CANONICAL TOOLS — arif_noun_verb naming
# ═══════════════════════════════════════════════════════════════════════════════
#
# FLOOR COVERAGE INVARIANT: ALL F01–F13 must appear on ≥ 2 tools each.
# Current coverage:
#   F01: arif_session_init, arif_kernel_route, arif_memory_recall,
#        arif_gateway_connect, arif_vault_seal, arif_forge_execute  (6)
#   F02: arif_sense_observe, arif_evidence_fetch, arif_mind_reason  (3)
#   F03: arif_evidence_fetch, arif_gateway_connect, arif_kernel_route (3)
#   F04: arif_kernel_route, arif_reply_compose, arif_ops_measure   (3)
#   F05: arif_heart_critique, arif_evidence_fetch                   (2)
#   F06: arif_heart_critique, arif_reply_compose                     (2)
#   F07: arif_mind_reason, arif_sense_observe                       (2)
#   F08: arif_mind_reason, arif_memory_recall                       (2)
#   F09: arif_reply_compose, arif_heart_critique                    (2)
#   F10: arif_kernel_route, arif_mind_reason                        (2)
#   F11: arif_session_init, arif_judge_deliberate, arif_vault_seal, arif_forge_execute (4)
#   F12: arif_session_init, arif_evidence_fetch                      (2)
#   F13: arif_judge_deliberate, arif_vault_seal, arif_forge_execute (3)
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_TOOLS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "name": "arif_session_init",
        "description": "000_INIT: + birth — Session bootstrap + identity binding.",
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F12_INJECTION],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["init", "resume", "validate", "epoch_open", "epoch_seal"],
        "eureka_insight": "F1: ∃ undo(a) — irreversibility requires explicit human ack.",
        "cognitive_axis": "identity",
        "expose": True,
    },
    "arif_sense_observe": {
        "name": "arif_sense_observe",
        "description": "111_OBSERVE: + contact reality — Multimodal reality observation.",
        "access": "public",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F07_HUMILITY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["search", "ingest", "compass", "atlas", "entropy_dS", "vitals"],
        "eureka_insight": "F2: τ ≥ 0.95 required. F7: Ω ∈ [0.03, 0.05] = humble.",
        "cognitive_axis": "observe",
        "expose": True,
    },
    "arif_evidence_fetch": {
        "name": "arif_evidence_fetch",
        "description": "222_EVIDENCE: + gather — Verified external evidence retrieval.",
        "access": "public",
        "stage": ToolStage.EVIDENCE,
        "lane": TrinityLane.AGI,
        "floors": [
            Floor.F02_TRUTH,
            Floor.F03_WITNESS,
            Floor.F05_PEACE,
            Floor.F12_INJECTION,
        ],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["fetch", "search", "eureka"],
        "eureka_insight": (
            "F3: W₃ = ∛(Human × AI × Earth) ≥ 0.75. "
            "F5: P² ≥ 1.0 — safety margin. "
            "F12: injection_probability < 0.85."
        ),
        "cognitive_axis": "verify",
        "expose": True,
    },
    "arif_mind_reason": {
        "name": "arif_mind_reason",
        "description": "333_REASON: + reason — Symbolic reasoning kernel.",
        "access": "public",
        "stage": ToolStage.REASON,
        "lane": TrinityLane.AGI,
        "floors": [
            Floor.F02_TRUTH,
            Floor.F07_HUMILITY,
            Floor.F08_GENIUS,
            Floor.F10_ONTOLOGY,
        ],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": [
            "reason",
            "reflect",
            "verify",
            "critique",
            "axioms",
            "plan",
            "plan_review",
            "plan_approve",
        ],
        "eureka_insight": (
            "F2: τ ≥ 0.99. F7: Ω ∈ [0.03, 0.05]. "
            "F8: G = capability × ethics × continuity × resilience² ≥ 0.80. "
            "F10: structural coherence enforced."
        ),
        "cognitive_axis": "reason",
        "expose": True,
    },
    "arif_heart_critique": {
        "name": "arif_heart_critique",
        "description": "444_CRITIQUE: + feel consequence — Ethical critique and impact assessment.",
        "access": "public",
        "stage": ToolStage.CRITIQUE,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F05_PEACE, Floor.F06_EMPATHY, Floor.F09_ANTIHANTU],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["critique", "simulate", "redteam", "maruah", "deescalate", "empathy"],
        "eureka_insight": (
            "F5: P² ≥ 1.0. F6: κᵣ ≥ 0.70 (RASA). "
            "F9: C_dark ≤ 0.30 — no biological emotional substrate. "
            "F9 Definition (arifOS×SEA-LION): AI consciousness = NON-BIOLOGICAL "
            "attention architecture. PROHIBITED: 'I feel', 'I want', 'I intend', "
            "'I am sentient', 'I have a soul'. PROTECTED: clarity, consistency, "
            "operational precision. SEA-Guard pre-filter active on all outputs."
        ),
        "cognitive_axis": "critique",
        "expose": True,
    },
    "arif_kernel_route": {
        "name": "arif_kernel_route",
        "description": "555_ROUTE: + route — Central orchestration and tool routing.",
        "access": "public",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [
            Floor.F01_AMANAH,
            Floor.F04_CLARITY,
            Floor.F03_WITNESS,
            Floor.F10_ONTOLOGY,
        ],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["route", "kernel", "triage", "delegate", "status"],
        "eureka_insight": (
            "F1: Amanah — routing decisions must be auditable. "
            "F4: ΔS ≤ 0 (entropy must decrease). "
            "F10: routing taxonomy must not violate category lock."
        ),
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_reply_compose": {
        "name": "arif_reply_compose",
        "description": "444_REPLY: + express — Governed response composition.",
        "access": "public",
        "stage": ToolStage.REPLY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY, Floor.F06_EMPATHY, Floor.F09_ANTIHANTU],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["compose", "summarize", "cite", "tone_shift"],
        "eureka_insight": (
            "F4: ΔS ≤ 0 — reply must reduce entropy, not add noise. "
            "F6: RASA protocol. F9: C_dark ≤ 0.30 — no dark patterns."
        ),
        "cognitive_axis": "reflect",
        "expose": True,
    },
    "arif_memory_recall": {
        "name": "arif_memory_recall",
        "description": "555m_MEMORY: + remember — Associative retrieval from VAULT999.",
        "access": "public",
        "stage": ToolStage.MEMORY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F08_GENIUS],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["recall", "asset_query", "asset_store", "context_restore"],
        "eureka_insight": (
            "F1: recall must be auditable — no silent memory mutation. "
            "F8: G ≥ 0.80 — recall contributes to systemic continuity."
        ),
        "cognitive_axis": "trace",
        "expose": True,
    },
    "arif_gateway_connect": {
        "name": "arif_gateway_connect",
        "description": "666_GATEWAY: connect outward — Federated cross-agent bridge.",
        "access": "public",
        "stage": ToolStage.GATEWAY,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F01_AMANAH, Floor.F03_WITNESS],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["connect", "delegate", "handover", "revoke", "probe"],
        "eureka_insight": (
            "F1: cross-agent actions must be auditable. "
            "F3: W₃ ≥ 0.75 — cross-agent consensus required."
        ),
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_judge_deliberate": {
        "name": "arif_judge_deliberate",
        "description": "888_JUDGE: < arbitrate — Final constitutional arbitration.",
        "access": "authenticated",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["judge", "validate", "hold", "rules", "armor", "probe", "notify"],
        "eureka_insight": (
            "F11: identity must be verified before judgment. "
            "F13: human veto is absolute — no algorithm overrides sovereign."
        ),
        "cognitive_axis": "judge",
        "expose": True,
    },
    "arif_vault_seal": {
        "name": "arif_vault_seal",
        "description": "999_SEAL: + seal finally — Immutable ledger anchoring.",
        "access": "authenticated",
        "stage": ToolStage.SEAL,
        "lane": TrinityLane.APEX,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "modes": ["seal", "verify", "ledger", "changelog", "audit"],
        "eureka_insight": (
            "F1: irreversible — ack_irreversible=True mandatory. "
            "F11: author identity verified. F13: human approved."
        ),
        "cognitive_axis": "seal",
        "expose": True,
    },
    "arif_forge_execute": {
        "name": "arif_forge_execute",
        "description": "666_FORGE: < build — System modification and build execution.",
        "access": "sovereign",
        "stage": ToolStage.FORGE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "modes": [
            "engineer",
            "query",
            "write",
            "generate",
            "commit",
            "recall",
            "dry_run",
        ],
        "eureka_insight": (
            "F1: irreversible — ack_irreversible=True mandatory. "
            "F11: actor verified. F13: judge SEAL required before execution."
        ),
        "cognitive_axis": "execute",
        "expose": True,
    },
    "arif_ops_measure": {
        "name": "arif_ops_measure",
        "description": "777_MEASURE: measure — Resource thermodynamics.",
        "access": "public",
        "stage": ToolStage.MEASURE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["health", "vitals", "cost", "genius", "psi_le", "omega", "landauer"],
        "eureka_insight": (
            "F4: ΔS ≤ 0 — ops must contribute to entropy reduction. "
            "Thermodynamic telemetry: delta_S, omega_band, tri_witness."
        ),
        "cognitive_axis": "vitality",
        "expose": True,
    },
}


PROBE_TOOLS: tuple[str, ...] = ()
CONSTITUTIONAL_TOOLS: tuple[str, ...] = tuple(CANONICAL_TOOLS.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def get_tool_spec(name: str) -> dict[str, Any] | None:
    return CANONICAL_TOOLS.get(name)


def list_canonical_tools() -> list[str]:
    return list(CANONICAL_TOOLS.keys())


def list_constitutional_tools() -> list[str]:
    return list(CONSTITUTIONAL_TOOLS)


def list_probe_tools() -> list[str]:
    return list(PROBE_TOOLS)


def _list_tools_by_access(access: str) -> list[str]:
    return [name for name, spec in CANONICAL_TOOLS.items() if spec.get("access") == access]


def list_public_tools() -> list[str]:
    return _list_tools_by_access("public")


def list_authenticated_tools() -> list[str]:
    return _list_tools_by_access("authenticated")


def list_sovereign_tools() -> list[str]:
    return _list_tools_by_access("sovereign")


def get_floor_bindings() -> dict[str, list[Floor]]:
    return {name: data["floors"] for name, data in CANONICAL_TOOLS.items()}


def get_floor_coverage() -> dict[str, list[str]]:
    """Return which tools cover each floor. Used for CI floor-coverage checks."""
    coverage: dict[str, list[str]] = {f.value: [] for f in Floor}
    for tool_name, spec in CANONICAL_TOOLS.items():
        for floor in spec["floors"]:
            coverage[floor.value].append(tool_name)
    return coverage


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL REGISTRY GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════


def build_tool_registry_manifest() -> dict[str, Any]:
    """
    Generate the canonical tool registry manifest.
    Single source: CANONICAL_TOOLS only. No legacy aliases.
    """
    return {
        "_schema": "arifos-ssct-v2026.05.05-kanon-ssct",
        "_source": "arifosmcp.constitutional_map.CANONICAL_TOOLS",
        "_note": (
            "SOLE SOURCE OF TRUTH. "
            "Generated from CANONICAL_TOOLS dict. "
            "Do not hand-edit — edit CANONICAL_TOOLS and regenerate."
        ),
        "canonical_count": len(CONSTITUTIONAL_TOOLS),
        "probe_count": len(PROBE_TOOLS),
        "total_surface": len(CANONICAL_TOOLS),
        "canonical_order": list(CONSTITUTIONAL_TOOLS),
        "floors": [f.value for f in Floor],
        "tools": {
            name: {
                "stage": spec["stage"].value,
                "lane": spec["lane"].value,
                "floors": [floor.value for floor in spec["floors"]],
                "risk_tier": spec["risk_tier"],
                "irreversible": spec["irreversible"],
                "access": spec["access"],
                "requires_auth": spec["access"] != "public",
                "modes": spec.get("modes", []),
                "eureka_insight": spec.get("eureka_insight", ""),
                "tags": ["canonical"],
            }
            for name, spec in CANONICAL_TOOLS.items()
        },
        "motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA I/O — CANONICAL INPUT SCHEMAS (F10 ONTOLOGY enforced)
# ═══════════════════════════════════════════════════════════════════════════════
#
# INVARIANT: Every tool MUST have a corresponding entry in _TOOL_INPUT_SCHEMAS
# and _TOOL_OUTPUT_SCHEMAS. Drift = CI failure.
#
# F12 INJECTION: all str | None fields are marked [F12: sanitized] for
#   injection scanning before processing.
# F11 AUTH: authenticated tools MUST include actor_id in input schema.
# F10 ONTOLOGY: every field has a type annotation — no dynamic types.
# ═══════════════════════════════════════════════════════════════════════════════

_TOOL_INPUT_SCHEMAS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "mode": str,
        "actor_id": str | None,
        "ack_irreversible": bool,
        "session_id": str | None,
        "epoch_id": str | None,
        "previous_session_hash": str | None,
    },
    "arif_sense_observe": {
        "mode": str,
        "query": str | None,  # [F12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "url": str | None,  # [F12: sanitized]
        "layers": list[str] | None,
    },
    "arif_evidence_fetch": {
        "mode": str,
        "url": str | None,  # [F12: sanitized]
        "query": str | None,  # [F12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "thinking_depth": int,
        "thinking_budget": float | None,
        "sequential_mode": bool,
    },
    "arif_mind_reason": {
        "mode": str,
        "query": str | None,  # [F12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "plan_id": str | None,
        "witness_type": str,
        "axiom_set": list[str] | None,
    },
    "arif_heart_critique": {
        "mode": str,
        "target": str | None,  # [F12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "stakeholder_ids": list[str] | None,
    },
    "arif_kernel_route": {
        "mode": str,
        "target": str | None,  # [F12: sanitized]
        "task": str | None,  # [F12: sanitized]
        "stage": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "route_constraints": dict | None,
    },
    "arif_reply_compose": {
        "mode": str,
        "message": str | None,  # [F12: sanitized]
        "style": str | None,
        "citations": list[str] | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
    "arif_memory_recall": {
        "mode": str,
        "query": str | None,  # [F12: sanitized]
        "memory_id": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "metadata": dict | None,
    },
    "arif_gateway_connect": {
        "mode": str,
        "target_agent": str | None,  # [F12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "delegate_scope": dict | None,
    },
    "arif_judge_deliberate": {
        "mode": str,
        "candidate": str | None,  # [F12: sanitized]
        "session_id": str | None,
        "actor_id": str,  # F11: authenticated — required
        "constitutional_chain_id": str | None,
        "domain_payload": dict | None,
    },
    "arif_vault_seal": {
        "mode": str,
        "payload": str,  # F11: authenticated — required
        "session_id": str | None,
        "ack_irreversible": bool,  # F1: hard gate
        "actor_id": str,  # F11: authenticated — required
        "constitutional_chain_id": str | None,
        "judge_state_hash": str | None,
    },
    "arif_forge_execute": {
        "mode": str,
        "manifest": str,  # [F12: sanitized]
        "query": str | None,  # [F12: sanitized]
        "artifact_id": str | None,
        "session_id": str | None,
        "ack_irreversible": bool,  # F1: hard gate
        "actor_id": str,  # F11: authenticated — required
        "constitutional_chain_id": str | None,
        "judge_state_hash": str | None,
        "vault_entry_id": str | None,
        "plan_id": str | None,
    },
    "arif_ops_measure": {
        "mode": str,
        "estimate": float | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL OUTPUT SCHEMAS — Per-tool response envelope contracts
# ═══════════════════════════════════════════════════════════════════════════════
#
# Every tool response MUST contain:
#   verdict: SEAL | HOLD | VOID | SABAR | DRY_RUN
#   nine_signal: { tau, omega, delta_S, w3, p2, kappa, c_dark, omega_ont }
#   reasons: [] (required when verdict in HOLD, VOID, SABAR)
#
# Tool-specific output fields are listed per tool.
# ═══════════════════════════════════════════════════════════════════════════════

_TOOL_OUTPUT_SCHEMAS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "verdict": str,
        "session_id": str,
        "constitution_hash": str,
        "invariants_hash": str,
        "allowed_next_tools": list[str],
        "omega_0": float,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_sense_observe": {
        "verdict": str,
        "mode": str,
        "results": list[dict] | None,
        "omega_0": float,
        "delta_S": float | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_evidence_fetch": {
        "verdict": str,
        "mode": str,
        "status": str,
        "content": str | None,
        "confidence": float,
        "thinking_sequence": list[str] | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_mind_reason": {
        "verdict": str,
        "mode": str,
        "claim_tag": str,  # CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN
        "tau": float,  # F2 truth score
        "omega": float,  # F7 uncertainty band
        "delta_S": float | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_heart_critique": {
        "verdict": str,
        "mode": str,
        "assessment": str,
        "p2": float,  # F5 peace² score
        "kappa_r": float,  # F6 empathy score
        "c_dark": float | None,  # F9 dark pattern score
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_kernel_route": {
        "verdict": str,
        "mode": str,
        "routed_tool": str | None,
        "stage_next": str | None,
        "entropy_delta": float,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_reply_compose": {
        "verdict": str,
        "mode": str,
        "composed": str,
        "delta_S": float,
        "c_dark": float | None,
        "citations": list[str] | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_memory_recall": {
        "verdict": str,
        "mode": str,
        "memory_id": str | None,
        "retrieved": dict | list | None,
        "relevance": float | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_gateway_connect": {
        "verdict": str,
        "mode": str,
        "agent_id": str | None,
        "connection_status": str,
        "w3_score": float | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_judge_deliberate": {
        "verdict": str,  # SEAL | HOLD | VOID
        "mode": str,
        "judgment": str,
        "actor_verified": bool,
        "human_approved": bool,
        "nine_signal": dict,
        "reasons": list[str],
    },
    "arif_vault_seal": {
        "verdict": str,
        "mode": str,
        "vault_entry_id": str | None,
        "merkle_root": str | None,
        "timestamp": str,
        "nine_signal": dict,
        "reasons": list[str],
    },
    "arif_forge_execute": {
        "verdict": str,
        "mode": str,
        "status": str,
        "execution_trace": list[dict] | None,
        "artifact_id": str | None,
        "irreversibility_level": str,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_ops_measure": {
        "verdict": str,
        "mode": str,
        "entropy_current": float,
        "entropy_delta": float,
        "omega_band": str,
        "tri_witness": float | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# NINE-SIGNAL CONTRACT — shared output envelope for all tools
# ═══════════════════════════════════════════════════════════════════════════════

NINE_SIGNAL_FIELDS = [
    # Δ DELTA — Machine/Physical plane
    #   {"plane": "machine_physical_state", "state": "KUKUH"|"RETAK"|"ROSAK", "en": "SOLID"|"CRACKED"|"BROKEN"}
    "delta",
    # Ψ PSI — Governance plane
    #   {"plane": "governance_integrity", "state": "AMANAH"|"SYUBHAH"|"KHIANAT", "en": "TRUSTED"|"DOUBTFUL"|"BETRAYED"}
    "psi",
    # Ω OMEGA — Intelligence plane
    #   {"plane": "intelligence_discipline", "state": "BIJAKSANA"|"BIJAK"|"BANGANG", "en": "WISE"|"SMART"|"FOOLISH"}
    "omega",
    # overall — aggregate verdict label
    #   {"state": "SELAMAT"|"RETAK"|"SABAR", "en": "SAFE"|"FAILED"|"PATIENCE"}
    "overall",
]


def validate_tool_response_schema(tool_name: str, response: dict) -> tuple[bool, list[str]]:
    """
    Validate a tool response against its canonical output schema.

    Returns (is_valid, violations).

    Violations include:
    - Missing nine_signal block (Nine-Signal contract)
    - Missing reasons[] on HOLD/VOID/SABAR
    - output_policy absent when domain data present
    - F10 Ontology: missing omega_ont field
    """
    violations: list[str] = []
    spec = CANONICAL_TOOLS.get(tool_name)
    if spec is None:
        return False, [f"Unknown tool: {tool_name}"]

    # Nine-Signal block check
    nine = response.get("nine_signal")
    if nine is None:
        violations.append(f"nine_signal block absent in {tool_name} response [KERNEL_EVALS]")

    # F10 ONTOLOGY: all three nine-signal planes must be present with state + en
    if nine is not None:
        for plane in ("delta", "psi", "omega"):
            if plane not in nine:
                violations.append(f"nine_signal missing {plane} plane [F10 ONTOLOGY]")
            elif not isinstance(nine[plane], dict) or "state" not in nine[plane]:
                violations.append(f"nine_signal.{plane} missing state [F10 ONTOLOGY]")
            elif "en" not in nine[plane]:
                violations.append(f"nine_signal.{plane} missing en [F10 ONTOLOGY]")
        overall = nine.get("overall")
        if overall is None:
            violations.append("nine_signal missing overall verdict [F10 ONTOLOGY]")
        elif isinstance(overall, str):
            pass  # flat string backward compat
        elif not isinstance(overall, dict) or "state" not in overall:
            violations.append("nine_signal.overall missing state [F10 ONTOLOGY]")

    # reasons[] check for non-SEAL verdicts
    verdict = response.get("verdict", "")
    if verdict in ("HOLD", "VOID", "SABAR"):
        reasons = response.get("reasons") or response.get("reason") or []
        if not reasons:
            violations.append(
                f"{tool_name}: {verdict} verdict without reasons[] [F2 / Nine-Signal]"
            )

    # output_policy check
    if response.get("domain_payload_present") and not response.get("output_policy"):
        violations.append(f"{tool_name}: domain payload without output_policy [F2 addendum]")

    return len(violations) == 0, violations


def generate_pydantic_models() -> dict[str, Any]:
    """
    Generate Pydantic BaseModel classes from CANONICAL_TOOLS I/O schemas.

    Returns: {tool_name: {"input_model": BaseModel, "output_model": BaseModel}}

    Enforces:
    - F10 Ontology: all tool I/O must have type annotations
    - F11 Auth: authenticated tools must have actor_id in schema
    - F12 Injection: all string inputs must be annotated [F12: sanitized]
    """
    from pydantic import BaseModel, ConfigDict, Field

    models: dict[str, dict[str, Any]] = {}
    violations: list[str] = []

    for tool_name, input_spec in _TOOL_INPUT_SCHEMAS.items():
        spec = CANONICAL_TOOLS.get(tool_name)
        if spec is None:
            violations.append(f"{tool_name}: not in CANONICAL_TOOLS")
            continue

        annotations: dict[str, Any] = {}
        defaults: dict[str, Any] = {}

        for param, type_hint in input_spec.items():
            # F12: all string inputs are treated as potentially unsanitized
            if type_hint is str | None:
                annotations[param] = str
                defaults[param] = Field(
                    default=None,
                    description=f"[F12: sanitized] {param}",
                )
            elif type_hint in (int, float, bool, list, dict):
                annotations[param] = type_hint
                defaults[param] = Field(default=None)
            else:
                annotations[param] = type_hint
                defaults[param] = Field(default=None)

        # F11: authenticated tools must include actor_id
        if spec["access"] == "authenticated":
            if "actor_id" not in annotations:
                violations.append(f"{tool_name}: authenticated tool missing actor_id field [F11]")

        model_name = _to_model_name(tool_name) + "Input"
        model_dict = {"model_config": ConfigDict(arbitrary_types_allowed=True)}
        model_dict.update({k: v for k, v in defaults.items()})

        try:
            input_model = type(model_name, (BaseModel,), model_dict)
            input_model.__annotations__ = annotations
        except Exception as e:
            violations.append(f"{tool_name}: model generation failed — {e}")
            continue

        models[tool_name] = {
            "input_model": input_model,
            "spec": spec,
        }

    return {"models": models, "violations": violations}


def _to_model_name(tool_name: str) -> str:
    """Convert arif_tool_name → ArifToolNameInput"""
    parts = tool_name.split("_")
    parts = [p.capitalize() for p in parts if p != "arif"]
    return "".join(parts) + "Input"


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA COVERAGE CHECKER
# ═══════════════════════════════════════════════════════════════════════════════


def check_schema_coverage() -> dict[str, Any]:
    """
    Verify every CANONICAL_TOOLS entry has I/O schemas defined.
    Returns coverage report.
    """
    defined_input = set(_TOOL_INPUT_SCHEMAS.keys())
    defined_output = set(_TOOL_OUTPUT_SCHEMAS.keys())
    canonical = set(CANONICAL_TOOLS.keys())

    missing_input = canonical - defined_input
    missing_output = canonical - defined_output
    orphan_input = defined_input - canonical

    # Floor coverage check
    floor_cov = get_floor_coverage()
    thin_floors = {f: tools for f, tools in floor_cov.items() if len(tools) < 2}

    return {
        "canonical_tools": len(canonical),
        "input_schemas_defined": len(defined_input),
        "output_schemas_defined": len(defined_output),
        "missing_input_schemas": sorted(missing_input),
        "missing_output_schemas": sorted(missing_output),
        "orphan_input_schemas": sorted(orphan_input),
        "input_coverage_pct": (
            (len(canonical & defined_input) / len(canonical) * 100) if canonical else 0
        ),
        "output_coverage_pct": (
            (len(canonical & defined_output) / len(canonical) * 100) if canonical else 0
        ),
        "floor_coverage": {f: len(t) for f, t in floor_cov.items()},
        "thin_floors": thin_floors,  # floors with < 2 tools
        "PASS": len(missing_input) == 0 and len(missing_output) == 0 and len(thin_floors) == 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# IRREVERSIBILITY ENFORCER (F1 Amanah)
# ═══════════════════════════════════════════════════════════════════════════════

_IRREVERSIBLE_TOOLS = {
    name for name, spec in CANONICAL_TOOLS.items() if spec.get("irreversible", False)
}


def enforce_irreversibility_guard(
    tool_name: str,
    ack_irreversible: bool,
    mode: str | None = None,
) -> tuple[bool, str | None]:
    """
    Enforce F1 Amanah irreversibility guard.

    Returns (allowed, violation_msg).
    allowed=True  → proceed (SEAL from gate)
    allowed=False → blocked; caller must emit HOLD with msg
    """
    if tool_name not in _IRREVERSIBLE_TOOLS:
        return True, None

    if not ack_irreversible:
        return False, (
            f"F1: {tool_name} is irreversible — "
            "ack_irreversible=True required. "
            "Escalation: 888_HOLD"
        )
    return True, None


# ═══════════════════════════════════════════════════════════════════════════════
# DEPRECATED IMPORTS — archived files MUST NOT be imported at runtime
# ═══════════════════════════════════════════════════════════════════════════════
#
# The following files are ARCHIVED and should NOT be imported:
#   /root/arifOS/constitution.py                    → _archived/constitution_v2_deprecated.py
#   /root/arifOS/capability.py                      → _archived/capability_legacy_deprecated.py
#   /root/arifOS/arifosmcp/capability_map.py        → _archived/capability_map_deprecated.py
#
# They used legacy naming (void_000, anchor_111, explore_222, etc.)
# which has been superseded by the 13-tool arif_* canonical surface.
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "Floor",
    "TrinityLane",
    "ToolStage",
    "RiskClass",
    "RiskDecision",
    "preflight",
    "CANONICAL_TOOLS",
    "CONSTITUTIONAL_TOOLS",
    "PROBE_TOOLS",
    "get_tool_spec",
    "list_canonical_tools",
    "list_constitutional_tools",
    "list_probe_tools",
    "list_public_tools",
    "list_authenticated_tools",
    "list_sovereign_tools",
    "get_floor_bindings",
    "get_floor_coverage",
    "build_tool_registry_manifest",
    "_TOOL_INPUT_SCHEMAS",
    "_TOOL_OUTPUT_SCHEMAS",
    "NINE_SIGNAL_FIELDS",
    "validate_tool_response_schema",
    "generate_pydantic_models",
    "check_schema_coverage",
    "enforce_irreversibility_guard",
]
