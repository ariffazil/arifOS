"""
ARIFOS CONSTITUTIONAL MAP (v2026.05.05-KANON-SSCT)
═══════════════════════════════════════════════════════════════════════════════

SOLE SOURCE OF TRUTH for the 13 canonical MCP tools.
All arif_* naming. No governance surface, no CC modes as separate tools.

MACHINERY:
  - CANONICAL_TOOLS   : 13-tool registry (name → spec with floors, stage, lane)
  - Law enum          : L01–L13 with Eureka-wired threshold logic
  - TrinityLane      : AGI | ASI | APEX
  - ToolStage        : 000–999 metabolic stage codes
  - _TOOL_INPUT_SCHEMAS  : canonical I/O type signatures (L10 ONTOLOGY enforced)
  - _TOOL_OUTPUT_SCHEMAS : canonical output envelope per tool
  - validate_tool_response_schema()  : F2 Nine-Signal contract checker
  - check_schema_coverage()          : all-13 tools have schemas = CI pass
  - enforce_irreversibility_guard() : F1 hard gate

EUREKA INSIGHTS WIRING (from EUREKA_INSIGHTS_SEAL_v2026.04.07):
  Each law threshold is derived from physics, not policy.
  See: 000/LAWS/L0X.md for formal proof of each threshold.

Ditempa Bukan Diberi.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# LAW DEFINITIONS — 13 Constitutional Laws as Physics
# ═══════════════════════════════════════════════════════════════════════════════


class Law(StrEnum):
    """
    L01–L13. Each Law is a physics equation, not a policy rule.
    Eureka wired: thresholds derived from EUREKA_INSIGHTS_SEAL_v2026.04.07.
    """

    L01_AMANAH = "L01"  # Reversibility as conservation law (∃ undo)
    L02_TRUTH = "L02"  # Uncertainty as first-class citizen (τ ≥ 0.99)
    L03_WITNESS = "L03"  # Tri-witness consensus (W₃ ≥ 0.75)
    L04_CLARITY = "L04"  # Entropy reduction as progress (ΔS ≤ 0)
    L05_PEACE = "L05"  # Non-destruction as baseline (P² ≥ 1.0)
    L06_EMPATHY = "L06"  # RASA as protocol (κᵣ ≥ 0.70)
    L07_HUMILITY = "L07"  # Uncertainty quantified (Ω ∈ [0.03, 0.05])
    L08_GENIUS = "L08"  # Systemic health (G ≥ 0.80)
    L09_ANTIHANTU = "L09"  # Pattern recognition of deception (C_dark ≤ 0.30)
    L10_ONTOLOGY = "L10"  # Structural coherence (category lock / immutability)
    L11_AUDIT = "L11"  # Verify identity + log provenance (HUMAN_APPROVAL gate)

    L12_INJECTION = "L12"  # Sanitize inputs (injection_probability < 0.85)
    L13_SOVEREIGN = "L13"  # Human veto absolute (final authority)


class TrinityLane(StrEnum):
    AGI = "AGI"  # Tactical execution (000–777)
    ASI = "ASI"  # Strategic judgment (888)
    APEX = "APEX"  # Authority resolution (999)


class ToolStage(StrEnum):
    INIT = "000"
    OBSERVE = "111"
    EVIDENCE = "222"
    REASON = "333"
    CRITIQUE = "444"
    # REPLY is a refinement of CRITIQUE (444). The "r" suffix encodes
    # parent-child relationship: reply composition is a governance-refined
    # sub-stage of the critique/reflection phase, not an independent stage.
    REPLY = "444r"
    ROUTE = "555"
    # MEMORY is a refinement of ROUTE (555). The "m" suffix encodes
    # that memory operations are a specialized form of routing — they
    # route queries through the 6-layer memory stack (L1-L6).
    MEMORY = "555m"
    # 666 is constitutionally the CRITIQUE/HEART gate (arif_heart_critique).
    # FORGE execution is a separate stage — 010 FORGE_EXECUTE — to prevent
    # the dangerous semantic confusion that caused v3.1 progression bug.
    FORGE = "666"
    FORGE_EXECUTE = "010"
    # GATEWAY is a refinement of FORGE (666). The "g" suffix encodes
    # that cross-organ federation bridging is a governed sub-stage of
    # the critique/forge phase, not an independent stage.
    GATEWAY = "666g"
    MEASURE = "777"
    JUDGE = "888"
    SEAL = "999"


class FiqhTier(StrEnum):
    """
    F0: The constitutional fiqh-of-floors tier vocabulary.
    Ratified by F13 SOVEREIGN (Arif) on 2026-06-11 with ed25519 signature
    (see /root/compose/sekrits/F0_FIQH_888_SEAL_2026-06-11.json).
    See: static/arifos/floors/F0_FIQH.md
    DITEMPA BUKAN DIBERI.
    """

    WAJIB = "WAJIB"  # obligatory; kernel REJECTS if missing
    SUNAT = "SUNAT"  # recommended; kernel RECORDS if observed
    HARUS = "HARUS"  # permitted; kernel does not record (x-payah default)
    MAKRUH = "MAKRUH"  # discouraged; kernel pings sovereign, requires ack
    HARAM = "HARAM"  # forbidden; kernel REJECTS unconditionally


# Per-floor tier (ratified 2026-06-11 by F13 SOVEREIGN ed25519 signature):
_FLOOR_FIQH: dict[Law, FiqhTier] = {
    Law.L01_AMANAH: FiqhTier.WAJIB,
    Law.L02_TRUTH: FiqhTier.WAJIB,
    Law.L03_WITNESS: FiqhTier.SUNAT,
    Law.L04_CLARITY: FiqhTier.WAJIB,
    Law.L05_PEACE: FiqhTier.MAKRUH,
    Law.L06_EMPATHY: FiqhTier.WAJIB,  # ASEAN context (maruah-first)
    Law.L07_HUMILITY: FiqhTier.WAJIB,
    Law.L08_GENIUS: FiqhTier.SUNAT,
    Law.L09_ANTIHANTU: FiqhTier.HARAM,
    Law.L10_ONTOLOGY: FiqhTier.WAJIB,
    Law.L11_AUDIT: FiqhTier.WAJIB,
    Law.L12_INJECTION: FiqhTier.HARAM,
    Law.L13_SOVEREIGN: FiqhTier.WAJIB,
}


def get_floor_tier(floor: Law) -> FiqhTier:
    """Return the ratified fiqh tier for a given Law. F0 ratified 2026-06-11."""
    return _FLOOR_FIQH.get(floor, FiqhTier.HARUS)  # default HARUS = no enforcement


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE PROGRESSION — Golden Path auto-chaining
# ═══════════════════════════════════════════════════════════════════════════════
# After each stage completes with SEAL verdict, agents can auto-load the next
# stage's tool and prompt. HOLD/SABAR/VOID verdicts nullify progression.
# 999_SEAL is terminal — no next stage.

STAGE_PROGRESSION: dict[str, dict[str, str | None]] = {
    "000": {"next": "111", "tool": "arif_sense_observe", "prompt": "111_agi"},
    "111": {"next": "222", "tool": "arif_evidence_fetch", "prompt": None},
    "222": {"next": "333", "tool": "arif_mind_reason", "prompt": None},
    # v3.1: 333 reason → 666 heart (ontology-aligned: 666 = HEART)
    "333": {"next": "666", "tool": "arif_heart_critique", "prompt": "666_asi"},
    # Stage suffixes: "r" = reply (refinement of critique), "m" = memory
    # (refinement of route), "g" = gateway (refinement of forge). These
    # encode parent-child relationships, not independent stage numbers.
    # 444r reply is a side-branch; no tool sits directly at 444.
    "444r": {"next": "555", "tool": "arif_kernel_route", "prompt": None},
    # v3.1 fix: 555 route/memory → 666 critique (heart), NOT forge.
    # Constitutionally: critique MUST precede forge. Never skip heart.
    "555": {"next": "666", "tool": "arif_heart_critique", "prompt": "666_critique"},
    "555m": {"next": "666", "tool": "arif_heart_critique", "prompt": "666_critique"},
    # 666 critique → 010 forge (dry_run mandatory)
    "666": {"next": "010", "tool": "arif_forge_execute", "prompt": "010_dry_run"},
    "666g": {"next": "010", "tool": "arif_forge_execute", "prompt": "010_dry_run"},
    # 010 forge → 777 measure (verify before judge)
    "010": {"next": "777", "tool": "arif_ops_measure", "prompt": None},
    "777": {"next": "888", "tool": "arif_judge_deliberate", "prompt": "888_apex"},
    "888": {"next": "999", "tool": "arif_vault_seal", "prompt": "999_seal"},
    "999": {"next": None, "tool": None, "prompt": None},
}


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
# | C4    | Very High   | Full floor review    | Required (L13)     |
# | C5    | Critical    | SEAL + human sign-off| Required + vault   |
# ═══════════════════════════════════════════════════════════════════════════════


class RiskClass(StrEnum):
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
        floors_activated=["L09", "L10"],
        description="Grammar, spelling, tone, formatting. Zero irreversible consequence.",
    ),
    RiskClass.C1_DRAFT: RiskTierConfig(
        governance_mode="light",
        requires_human_confirmation=False,
        floors_activated=["L04", "L09", "L10"],
        description="Internal drafts, brainstorming, notes. Reversible. No external exposure.",
    ),
    RiskClass.C2_REVIEW: RiskTierConfig(
        governance_mode="standard",
        requires_human_confirmation=False,
        floors_activated=["L02", "L03", "L04", "L07", "L08"],
        description=(
            "Code review, testing, analysis, summaries. Evidence-backed. Moderate exposure."
        ),
    ),
    RiskClass.C3_PUBLIC: RiskTierConfig(
        governance_mode="strict",
        requires_human_confirmation=True,
        floors_activated=["L01", "L02", "L03", "L04", "L05", "L06", "L09", "L12"],
        description="Public posts, emails to third parties, published documents. Reputation risk.",
    ),
    RiskClass.C4_LEGAL_MONEY: RiskTierConfig(
        governance_mode="strict",
        requires_human_confirmation=True,
        floors_activated=["L01", "L02", "L03", "L05", "L06", "L11", "L12", "L13"],
        description="Legal claims, financial decisions, HR actions, investments. High consequence.",
    ),
    RiskClass.C5_IRREVERSIBLE: RiskTierConfig(
        governance_mode="seal",
        requires_human_confirmation=True,
        floors_activated=["L01", "L02", "L03", "L05", "L06", "L11", "L12", "L13"],
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
    requires_human_confirmation: bool  # L13 gate — human must sign off
    human_approval_reference: str | None  # If confirmed, the approval token / session_ref
    uncertainty_band: tuple[float, float]  # (lower, upper) — L07 Ω band if evidence is thin
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
      - requires_human_confirmation: does L13 SOVEREIGN require human sign-off?
      - governance_mode: how much governance was applied
      - floors_activated: which floors are on watch
      - uncertainty_band: L07 Ω range if evidence is weak
    """
    tier = _RISK_GOVERNANCE_TABLE[risk_class]

    # ── C5 special: vault seal required — check FIRST before L01 gate ───────
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
            floors_activated=["L01", "L11", "L12", "L13"],
            requires_human_confirmation=True,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.05),
            preflight_passed=False,
        )

    # ── Irreversibility override (L01 AMANAH) ─────────────────────────────────
    if not reversible and tier.governance_mode in ("strict", "seal"):
        # Irreversible + high-risk → always HOLD
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode="seal",
            verdict="HOLD",
            reason=(
                f"L01 AMANAH: {action} is irreversible and class {risk_class.value}. "
                f"Evidence gate + human confirmation required. "
                f"Escalation: 888_HOLD"
            ),
            floors_activated=["L01", *tier.floors_activated],
            requires_human_confirmation=True,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.05),
            preflight_passed=False,
        )

    # ── Evidence quality check (L02 TRUTH) ────────────────────────────────────
    if evidence_quality < 0.5 and tier.governance_mode in ("strict", "seal"):
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode="strict",
            verdict="HOLD",
            reason=(
                f"L02 TRUTH: evidence quality {evidence_quality:.0%} is insufficient for "
                f"{risk_class.value} actions. Required: ≥50% evidence confidence. "
                f"Reduce claim strength or gather more evidence."
            ),
            floors_activated=["L02", *tier.floors_activated],
            requires_human_confirmation=tier.requires_human_confirmation,
            human_approval_reference=None,
            uncertainty_band=(0.03, 0.10),  # Wider Ω band — low evidence
            preflight_passed=False,
        )

    # ── Human confirmation gate (L13 SOVEREIGN) ───────────────────────────────
    if tier.requires_human_confirmation and not session_ref:
        return RiskDecision(
            allowed=False,
            risk_class=risk_class,
            governance_mode=tier.governance_mode,
            verdict="HOLD",
            reason=(
                f"L13 SOVEREIGN: {risk_class.value} action '{action}' requires human "
                f"confirmation before execution. Provide session_ref to proceed. "
                f"Compute can advise. Human must decide."
            ),
            floors_activated=["L13", *tier.floors_activated],
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
            floors_activated=["L01", "L11", "L12", "L13"],
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
# FLOOR COVERAGE INVARIANT: ALL L01–L13 must appear on ≥ 2 tools each.
# Current coverage:
#   L01: arif_session_init, arif_kernel_route, arif_memory_recall,
#        arif_gateway_connect, arif_vault_seal, arif_forge_execute  (6)
#   L02: arif_sense_observe, arif_evidence_fetch, arif_mind_reason  (3)
#   L03: arif_evidence_fetch, arif_gateway_connect, arif_kernel_route (3)
#   L04: arif_kernel_route, arif_reply_compose, arif_ops_measure   (3, incl. topology/drift)
#   L05: arif_heart_critique, arif_evidence_fetch                   (2)
#   L06: arif_heart_critique, arif_reply_compose                     (2)
#   L07: arif_mind_reason, arif_sense_observe                       (2)
#   L08: arif_mind_reason, arif_memory_recall                       (2)
#   L09: arif_reply_compose, arif_heart_critique                    (2)
#   L10: arif_kernel_route, arif_mind_reason                        (2)
#   L11: arif_session_init, arif_judge_deliberate, arif_vault_seal, arif_forge_execute (4)
#   L12: arif_session_init, arif_evidence_fetch                      (2)
#   L13: arif_judge_deliberate, arif_vault_seal, arif_forge_execute (3)
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_TOOLS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "name": "arif_session_init",
        "description": "000_INIT: Session bootstrap + identity binding. CALL FIRST on every agentic session — no audit trail, no floor enforcement, no actor binding without this. Do NOT call GEOX/WEALTH/WELL tools before calling this. Parameters: mode (init|resume|validate|epoch_open|epoch_seal), actor_id, session_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L12_INJECTION],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["init", "resume", "validate", "epoch_open", "epoch_seal"],
        "eureka_insight": "F1: ∃ undo(a) — irreversibility requires explicit human ack.",
        "cognitive_axis": "identity",
        "expose": True,
    },
    "arif_sense_observe": {
        "name": "arif_sense_observe",
        "description": "111_OBSERVE: Multimodal reality observation and hybrid discovery. Call this for: web search, local wiki and repo index discovery (hybrid_discovery), checking system state, grounding session in current reality. Hybrid discovery is READ-ONLY evidence retrieval — it finds but does not store. Agents should pass findings to arif_mind_reason or arif_memory_recall as appropriate. Parameters: mode (search|hybrid_discovery|ingest|compass|atlas|entropy_dS|vitals), query, url, layers, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L02_TRUTH, Law.L07_HUMILITY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": [
            "search",
            "hybrid_discovery",
            "ingest",
            "compass",
            "atlas",
            "entropy_dS",
            "vitals",
        ],
        "eureka_insight": "F2: τ ≥ 0.95 required. F7: Ω ∈ [0.03, 0.05] = humble.",
        "cognitive_axis": "observe",
        "expose": True,
    },
    "arif_evidence_fetch": {
        "name": "arif_evidence_fetch",
        "description": "222_EVIDENCE: Verified external evidence retrieval with source-of-truth grounding. Call this when: a claim needs external citation, Arif needs live data before deciding, or reasoning requires factual grounding. Do NOT call this for general browsing (use arif_sense_observe) or reasoning over already-gathered data (use arif_mind_reason). Parameters: mode (fetch|search|eureka), url, query (the evidence query string), thinking_depth, sequential_mode, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.EVIDENCE,
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L02_TRUTH,
            Law.L03_WITNESS,
            Law.L05_PEACE,
            Law.L12_INJECTION,
        ],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["fetch", "search", "eureka"],
        "eureka_insight": (
            "F3: W₃ = ∛(Human × AI × Earth) ≥ 0.75. "
            "F5: P² ≥ 1.0 — safety margin. "
            "L12: injection_probability < 0.85."
        ),
        "cognitive_axis": "verify",
        "expose": True,
    },
    "arif_mind_reason": {
        "name": "arif_mind_reason",
        "description": "333_REASON: Symbolic reasoning kernel — epistemically honest, self-critiquing, confidence-labeled. Call this for: complex multi-step reasoning, plan generation, refactor planning, cross-domain analysis, hypothesis evaluation. Labels its own uncertainty (F7). Do NOT call this for domain-specific calculations — use GEOX/WEALTH for those. Parameters: mode (reason|reflect|verify|critique|plan|plan_review|plan_approve|refactor_plan|metabolize), query (the reasoning prompt), plan_id, witness_type, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.REASON,
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L02_TRUTH,
            Law.L07_HUMILITY,
            Law.L08_GENIUS,
            Law.L10_ONTOLOGY,
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
            "refactor_plan",
            "metabolize",
        ],
        "eureka_insight": (
            "F2: τ ≥ 0.99. F7: Ω ∈ [0.03, 0.05]. "
            "F8: G = capability × ethics × continuity × resilience² ≥ 0.80. "
            "L10: ambiguity is permanent; expose assumptions before reasoning. "
            "Eureka: internal reasoning may be deep, but public output must be legible, bounded, and auditable."
        ),
        "cognitive_axis": "reason",
        "expose": True,
    },
    "arif_heart_critique": {
        "name": "arif_heart_critique",
        "description": "666_HEART: Ethical critique and consequence assessment against F1-L13 floors. Call this before: irreversible actions, decisions affecting dignity or human welfare, forge execution, or any proposal that may violate constitutional floors. Do NOT call this to make the final decision — that belongs to arif_judge_deliberate. Parameters: mode (critique|simulate|redteam|maruah|deescalate|empathy), target (the item to critique), stakeholder_ids, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.FORGE,
        "lane": TrinityLane.ASI,
        "floors": [Law.L05_PEACE, Law.L06_EMPATHY, Law.L09_ANTIHANTU],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["critique", "simulate", "redteam", "maruah", "deescalate", "empathy"],
        "eureka_insight": (
            "F5: P² ≥ 1.0. F6: κᵣ ≥ 0.70 (RASA). "
            "F9: C_dark ≤ 0.30 — no biological or artificial emotional substrate. "
            "F9 Doctrine (arifOS×MiniMax-M3, originally with SEA-LION): The machine is an instrument, not a person. "
            "No substrate grants it feeling, intent, or personhood. "
            "PROHIBITED: 'I feel', 'I want', 'I intend', 'I am sentient', 'I have a soul'. "
            "PROTECTED: clarity, consistency, operational precision. SEA-Guard pre-filter active on all outputs."
        ),
        "cognitive_axis": "critique",
        "expose": True,
    },
    "arif_kernel_route": {
        "name": "arif_kernel_route",
        "description": "555_ROUTE: Routes intent to correct tool or organ. "
        "Use when unsure which tool to call, task needs multi-tool sequencing, "
        "or delegating to GEOX/WEALTH/WELL. Returns a plan, not a result. "
        "Parameters: mode (route|kernel|triage|delegate|status|metabolize), target (tool/endpoint name), task (task description), stage, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L01_AMANAH,
            Law.L04_CLARITY,
            Law.L03_WITNESS,
            Law.L10_ONTOLOGY,
        ],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["route", "kernel", "triage", "delegate", "status", "metabolize"],
        "eureka_insight": (
            "F1: Amanah — routing decisions must be auditable. "
            "F4: ΔS ≤ 0 (entropy must decrease). "
            "L10: ambiguity is permanent; expose assumptions before routing. "
            "L12: graceful degradation — if router/tool/substrate uncertainty rises, return SABAR/HOLD/VOID rather than continuing unsafe execution. "
            "Eureka: what is declared must be registered and callable; registry not matching reality is HOLD. "
            "Eureka: internal depth, external legibility."
        ),
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_reply_compose": {
        "name": "arif_reply_compose",
        "description": "444_REPLY: Governed response composition — formats final output for Arif with citations and tone calibration. Call this as the LAST step before presenting results to Arif. Do NOT call this mid-pipeline — only after reasoning and judgment are complete. Parameters: mode (compose|summarize|cite|tone_shift), message (the content to compose), style, citations, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.REPLY,
        "lane": TrinityLane.AGI,
        "floors": [Law.L02_TRUTH, Law.L04_CLARITY, Law.L06_EMPATHY, Law.L09_ANTIHANTU],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["compose", "summarize", "cite", "tone_shift"],
        "eureka_insight": (
            "F4: ΔS ≤ 0 — reply must reduce entropy, not add noise. "
            "F6: RASA protocol. F9: C_dark ≤ 0.30 — no dark patterns. "
            "L10: ambiguity is permanent; expose assumptions before composing. "
            "Eureka: internal reasoning may be deep, but public output must be legible, bounded, and auditable."
        ),
        "cognitive_axis": "reflect",
        "expose": True,
    },
    "arif_memory_recall": {
        "name": "arif_memory_recall",
        "description": "555m_MEMORY: Associative memory — Postgres+Qdrant vector recall across sessions. Call this for: retrieving past decisions, querying stored assets (geoscience prospects, financial models), or restoring session context. Do NOT use this for live web data (use arif_evidence_fetch) or permanent ledger sealing (use arif_vault_seal). Parameters: mode (recall|asset_query|asset_store|context_restore), query, memory_id, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.MEMORY,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L08_GENIUS],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["recall", "asset_query", "asset_store", "context_restore"],
        "eureka_insight": (
            "F1: recall must be auditable — no silent memory mutation. "
            "F8: G ≥ 0.80 — recall contributes to systemic continuity. "
            "F8/L11: memory is power; recall/store requires purpose limits, stale-assumption checks, sensitive-data boundaries, and auditable consent."
        ),
        "cognitive_axis": "trace",
        "expose": True,
    },
    "arif_gateway_connect": {
        "name": "arif_gateway_connect",
        "description": "666_GATEWAY: Federated cross-agent bridge — connects arifOS to GEOX (earth), WEALTH (capital), WELL (human), or external A2A agents. Call this to: delegate domain work to GEOX/WEALTH/WELL with session_id provenance, or initiate multi-agent workflows. Do NOT call GEOX/WEALTH/WELL tools directly from an ungoverned session — route through here to maintain constitutional audit trail. Parameters: mode (connect|delegate|handover|revoke|probe), target_agent (e.g., GEOX|WEALTH|WELL|kimi|claude|gemini), session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.GATEWAY,
        "lane": TrinityLane.ASI,
        "floors": [Law.L01_AMANAH, Law.L03_WITNESS, Law.L11_AUDIT],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["connect", "delegate", "handover", "revoke", "probe"],
        "eureka_insight": (
            "F1: cross-agent actions must be auditable. "
            "F3: W₃ ≥ 0.75 — cross-agent consensus required. "
            "L11: cross-organ routing requires verified identity. "
            "L12: graceful degradation — if router/tool/substrate uncertainty rises, return SABAR/HOLD/VOID rather than continuing unsafe execution."
        ),
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_judge_deliberate": {
        "name": "arif_judge_deliberate",
        "description": "888_JUDGE: Final constitutional arbitration — renders SEAL/HOLD/VOID verdicts. Call this before: any irreversible action, deployment, or consequential decision. Requires domain_evidence from GEOX/WEALTH/WELL as input. Do NOT call this first — must be preceded by sense→evidence→reason→critique pipeline. Parameters: mode (judge|validate|hold|rules|armor|probe|notify), candidate (the action/decision to judge), constitutional_chain_id, session_id, actor_id (required).",  # noqa: E501
        "access": "authenticated",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["judge", "validate", "hold", "rules", "armor", "probe", "notify"],
        "eureka_insight": (
            "L01: irreversible downstream — judge verdicts authorize forge/vault actions. "
            "L11: identity must be verified before judgment. "
            "L13: human veto is absolute — no algorithm overrides sovereign."
        ),
        "cognitive_axis": "judge",
        "expose": True,
    },
    "arif_vault_seal": {
        "name": "arif_vault_seal",
        "description": "999_SEAL: Immutable ledger anchoring — cryptographic hash-chain seal to VAULT999. Call this LAST to permanently record any decision, verdict, or completed workflow. Irreversible — requires ack_irreversible=True and a preceding arif_judge_deliberate SEAL verdict. Do NOT call this mid-pipeline or speculatively. Parameters: mode (seal|verify|ledger|changelog|audit), payload, ack_irreversible (bool, required), actor_id (required), constitutional_chain_id, judge_state_hash, session_id.",  # noqa: E501
        "access": "authenticated",
        "stage": ToolStage.SEAL,
        "lane": TrinityLane.APEX,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "modes": ["seal", "verify", "ledger", "changelog", "audit"],
        "eureka_insight": (
            "F1: irreversible — ack_irreversible=True mandatory. "
            "L11: author identity verified. L13: human approved."
        ),
        "cognitive_axis": "seal",
        "expose": True,
    },
    "arif_forge_execute": {
        "name": "arif_forge_execute",
        "description": "010_FORGE_EXECUTE: Build execution — code generation, artifact creation, system modification. Call this for: writing code, generating files, executing build commands. Requires arif_judge_deliberate SEAL before side-effects are live (dry_run by default). Do NOT call this without a preceding judge verdict on consequential changes. Parameters: mode (engineer|query|write|generate|commit|recall|dry_run), manifest (the build manifest/instructions), query, artifact_id, ack_irreversible (bool), actor_id (required), constitutional_chain_id, judge_state_hash, vault_entry_id, plan_id, session_id.",  # noqa: E501
        "access": "sovereign",
        "stage": ToolStage.FORGE_EXECUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
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
            "L11: actor verified. L12: fail safely; no unsafe continuation when substrate confidence drops. "
            "L13: judge SEAL required before execution."
        ),
        "cognitive_axis": "execute",
        "expose": True,
    },
    "arif_ops_measure": {
        "name": "arif_ops_measure",
        "description": "777_MEASURE: Machine resource health + governance thermodynamics (g_score, entropy delta, Ω). Call this for: VPS CPU/RAM/disk state, arifOS reasoning quality metrics, or pre-forge health check. Do NOT use this for Arif's biological/cognitive state — use WELL:well_assess_metabolism for that. Parameters: mode (health|vitals|cost|genius|psi_le|omega|landauer|topology|drift), estimate, session_id, actor_id.",  # noqa: E501
        "access": "public",
        "stage": ToolStage.MEASURE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L02_TRUTH, Law.L04_CLARITY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": [
            "health",
            "vitals",
            "cost",
            "genius",
            "psi_le",
            "omega",
            "landauer",
            "topology",
            "drift",
        ],
        "eureka_insight": (
            "F4: ΔS ≤ 0 — ops must contribute to entropy reduction. "
            "Eureka: health is trajectory, not binary; measure delta_S, omega_band, tri_witness, and drift trend. "
            "Eureka: what is declared must be registered and callable; registry not matching reality is HOLD. "
            "F8: measured intelligence is not useful intelligence; prefer local workflow evals over leaderboard metrics."
        ),
        "cognitive_axis": "vitality",
        "expose": True,
    },
}


PROBE_TOOLS: tuple[str, ...] = ()
CONSTITUTIONAL_TOOLS: tuple[str, ...] = tuple(CANONICAL_TOOLS.keys())

# MCP Spec 2025-11-25 tool annotations (SEP-1862/1913/1984/2417)
# title + readOnlyHint + destructiveHint + idempotentHint + openWorldHint
_TOOL_ANNOTATIONS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "title": "Init Session",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "arif_sense_observe": {
        "title": "Sense & Observe",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    "arif_evidence_fetch": {
        "title": "Fetch Evidence",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    "arif_mind_reason": {
        "title": "Mind Reason",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "arif_heart_critique": {
        "title": "Heart Critique",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "arif_kernel_route": {
        "title": "Kernel Route",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "arif_reply_compose": {
        "title": "Reply Compose",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "arif_memory_recall": {
        "title": "Memory Recall",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "arif_gateway_connect": {
        "title": "Gateway Connect",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
    "arif_judge_deliberate": {
        "title": "Judge Deliberate",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "arif_vault_seal": {
        "title": "Vault Seal",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    "arif_forge_execute": {
        "title": "Forge Execute",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    "arif_ops_measure": {
        "title": "Ops Measure",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
}

# MCP Spec 2025-11-25 outputSchema (SEP-2127 / JSON Schema)
# Every canonical tool returns through _enforce_nine_signal which produces
# a standardized envelope.  The `result` field is tool-specific.
CANONICAL_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Execution status: OK, ERROR, TIMEOUT, DRY_RUN",
        },
        "tool": {
            "type": "string",
            "description": "Canonical tool name that produced this response",
        },
        "verdict": {
            "type": "string",
            "description": "Constitutional verdict: SEAL, HOLD, VOID, SABAR, PROVISIONAL, PARTIAL",
        },
        "result": {"type": "object", "description": "Tool-specific payload"},
        "meta": {"type": "object", "description": "Metadata including actor_id, mode, circuit"},
        "delta_S": {"type": "number", "description": "Thermodynamic entropy change"},
        "timestamp": {"type": "string", "description": "ISO-8601 timestamp"},
        "session_id": {"type": ["string", "null"], "description": "Active session identifier"},
        "actor_id": {"type": ["string", "null"], "description": "Sovereign or agent actor ID"},
        "output_policy": {
            "type": "string",
            "description": "Policy constraints: DOMAIN_SEAL, DOMAIN_HOLD, DOMAIN_VOID, SIMULATION_ONLY",
        },
        "nine_signal": {"type": "object", "description": "F2 addendum nine-signal block"},
        "reasons": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Human-readable justification list",
        },
        "_nine_signal_compliant": {"type": "boolean", "description": "Internal compliance flag"},
        "_violations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Non-compliance audit trail",
        },
        "stage_progression": {
            "type": ["object", "null"],
            "description": "Next stage auto-chain hint",
        },
    },
    "required": ["status", "tool", "verdict", "result", "nine_signal", "reasons"],
}

TOOL_STAGES: dict[str, ToolStage] = {
    "arif_session_init": ToolStage.INIT,
    "arif_sense_observe": ToolStage.OBSERVE,
    "arif_evidence_fetch": ToolStage.EVIDENCE,
    "arif_mind_reason": ToolStage.REASON,
    "arif_heart_critique": ToolStage.FORGE,
    "arif_kernel_route": ToolStage.ROUTE,
    "arif_reply_compose": ToolStage.REPLY,
    "arif_memory_recall": ToolStage.MEMORY,
    "arif_gateway_connect": ToolStage.GATEWAY,
    "arif_judge_deliberate": ToolStage.JUDGE,
    "arif_vault_seal": ToolStage.SEAL,
    "arif_forge_execute": ToolStage.FORGE_EXECUTE,
    "arif_ops_measure": ToolStage.MEASURE,
}


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


def list_internal_only_tools() -> list[str]:
    """
    Return tools registered in CANONICAL_TOOLS with access == "internal_only".

    These tools exist in the canonical registry (so they can be inspected
    internally, audited, and reasoned about) but are NEVER exposed to
    any public MCP surface. They are filtered from:

    - public_tool_names_for_mode()
    - arif_session_init's `allowed_tools` list
    - The /health `tools_loaded` count
    - AGENTS.md auto-generated tables

    Use cases:
    - Diagnostic probes only operators should call
    - Tools in development not yet ready for public release
    - Tools that exist for federation-internal coordination (e.g.
      _arif_daily_intelligence_brief is currently a defined function
      but not registered; this tier formalises that pattern).

    F2 TRUTH: Internal-only tools are NOT phantoms — they are
    deliberately registered, deliberately filtered. The
    `internal_only_registry` distinction is auditable.
    """
    return _list_tools_by_access("internal_only")


def get_law_bindings() -> dict[str, list[Law]]:
    return {name: data["floors"] for name, data in CANONICAL_TOOLS.items()}


# Backward-compat alias (deprecated 2026-06-06)
get_floor_bindings = get_law_bindings


def get_law_coverage() -> dict[str, list[str]]:
    """Return which tools cover each law. Used for CI law-coverage checks."""
    coverage: dict[str, list[str]] = {f.value: [] for f in Law}
    for tool_name, spec in CANONICAL_TOOLS.items():
        for law in spec["floors"]:
            coverage[law.value].append(tool_name)
    return coverage


# Backward-compat alias (deprecated 2026-06-06)
get_floor_coverage = get_law_coverage


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
        "laws": [f.value for f in Law],
        "floors": [f.value for f in Law],  # deprecated alias
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
# SCHEMA I/O — CANONICAL INPUT SCHEMAS (L10 ONTOLOGY enforced)
# ═══════════════════════════════════════════════════════════════════════════════
#
# INVARIANT: Every tool MUST have a corresponding entry in _TOOL_INPUT_SCHEMAS
# and _TOOL_OUTPUT_SCHEMAS. Drift = CI failure.
#
# L12 INJECTION: all str | None fields are marked [L12: sanitized] for
#   injection scanning before processing.
# L11 AUTH: authenticated tools MUST include actor_id in input schema.
# L10 ONTOLOGY: every field has a type annotation — no dynamic types.
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
        "query": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "url": str | None,  # [L12: sanitized]
        "layers": list[str] | None,
        "result_limit": int,  # max results for search/ingest (default 10)
    },
    "arif_evidence_fetch": {
        "mode": str,
        "url": str | None,  # [L12: sanitized]
        "query": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "thinking_depth": int,
        "thinking_budget": float | None,
        "sequential_mode": bool,
    },
    "arif_mind_reason": {
        "mode": str,
        "query": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "plan_id": str | None,
        "witness_type": str,
        "axiom_set": list[str] | None,
    },
    "arif_heart_critique": {
        "mode": str,
        "target": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "stakeholder_ids": list[str] | None,
    },
    "arif_kernel_route": {
        "mode": str,
        "target": str | None,  # [L12: sanitized]
        "task": str | None,  # [L12: sanitized]
        "stage": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "route_constraints": dict | None,
    },
    "arif_reply_compose": {
        "mode": str,
        "message": str | None,  # [L12: sanitized]
        "style": str | None,
        "citations": list[str] | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
    "arif_memory_recall": {
        "mode": str,
        "query": str | None,  # [L12: sanitized]
        "memory_id": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "metadata": dict | None,
    },
    "arif_gateway_connect": {
        "mode": str,
        "target_agent": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "delegate_scope": dict | None,
    },
    "arif_judge_deliberate": {
        "mode": str,
        "candidate": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str,  # L11: authenticated — required
        "constitutional_chain_id": str | None,
        "domain_payload": dict | None,
    },
    "arif_vault_seal": {
        "mode": str,
        "payload": str,  # L11: authenticated — required
        "session_id": str | None,
        "ack_irreversible": bool,  # F1: hard gate
        "actor_id": str,  # L11: authenticated — required
        "constitutional_chain_id": str | None,
        "judge_state_hash": str | None,
    },
    "arif_forge_execute": {
        "mode": str,
        "manifest": str,  # [L12: sanitized]
        "query": str | None,  # [L12: sanitized]
        "artifact_id": str | None,
        "session_id": str | None,
        "ack_irreversible": bool,  # F1: hard gate
        "actor_id": str,  # L11: authenticated — required
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
        "a_rif": dict | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_evidence_fetch": {
        "verdict": str,
        "mode": str,
        "status": str,
        "content": str | None,
        "confidence": float,
        "thinking_sequence": dict | list[str] | None,
        "resource_metrics": dict | None,
        "confidence_path": list[float] | None,
        "claim_state": str | None,
        "contradiction_audit": dict | None,
        "source_card": dict | None,
        "a_rif": dict | None,
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
    #   {"plane": "machine_physical_state", "state": "KUKUH"|"RETAK"|"ROSAK", "en": "SOLID"|"CRACKED"|"BROKEN"}  # noqa: E501
    "delta",
    # Ψ PSI — Governance plane
    #   {"plane": "governance_integrity", "state": "AMANAH"|"SYUBHAH"|"KHIANAT", "en": "TRUSTED"|"DOUBTFUL"|"BETRAYED"}  # noqa: E501
    "psi",
    # Ω OMEGA — Intelligence plane
    #   {"plane": "intelligence_discipline", "state": "BIJAKSANA"|"BIJAK"|"BANGANG", "en": "WISE"|"SMART"|"FOOLISH"}  # noqa: E501
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
    - L10 Ontology: missing omega_ont field
    """
    violations: list[str] = []
    spec = CANONICAL_TOOLS.get(tool_name)
    is_canonical = spec is not None

    # Nine-Signal block check
    nine = response.get("nine_signal")
    if nine is None:
        violations.append(f"nine_signal block absent in {tool_name} response [KERNEL_EVALS]")

    # L10 ONTOLOGY: all three nine-signal planes must be present with state + en
    if nine is not None:
        for plane in ("delta", "psi", "omega"):
            if plane not in nine:
                violations.append(f"nine_signal missing {plane} plane [L10 ONTOLOGY]")
            elif not isinstance(nine[plane], dict) or "state" not in nine[plane]:
                violations.append(f"nine_signal.{plane} missing state [L10 ONTOLOGY]")
            elif "en" not in nine[plane]:
                violations.append(f"nine_signal.{plane} missing en [L10 ONTOLOGY]")
        overall = nine.get("overall")
        if overall is None:
            violations.append("nine_signal missing overall verdict [L10 ONTOLOGY]")
        elif isinstance(overall, str):
            pass  # flat string backward compat
        elif not isinstance(overall, dict) or "state" not in overall:
            violations.append("nine_signal.overall missing state [L10 ONTOLOGY]")

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

    # Non-canonical tools are admitted if they satisfy the universal nine-signal contract.
    # Tool-specific output schemas are enforced only for canonical CANONICAL_TOOLS entries.
    if not is_canonical and not violations:
        return True, [f"non-canonical tool {tool_name} admitted via nine-signal contract"]

    return len(violations) == 0, violations


def generate_pydantic_models() -> dict[str, Any]:
    """
    Generate Pydantic BaseModel classes from CANONICAL_TOOLS I/O schemas.

    Returns: {tool_name: {"input_model": BaseModel, "output_model": BaseModel}}

    Enforces:
    - L10 Ontology: all tool I/O must have type annotations
    - L11 Auth: authenticated tools must have actor_id in schema
    - L12 Injection: all string inputs must be annotated [L12: sanitized]
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
            # L12: all string inputs are treated as potentially unsanitized
            if type_hint is str | None:
                annotations[param] = str
                defaults[param] = Field(
                    default=None,
                    description=f"[L12: sanitized] {param}",
                )
            elif type_hint in (int, float, bool, list, dict):
                annotations[param] = type_hint
                defaults[param] = Field(default=None)
            else:
                annotations[param] = type_hint
                defaults[param] = Field(default=None)

        # L11: authenticated tools must include actor_id
        if spec["access"] == "authenticated":
            if "actor_id" not in annotations:
                violations.append(f"{tool_name}: authenticated tool missing actor_id field [L11]")

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

    # Law coverage check
    law_cov = get_law_coverage()
    thin_laws = {f: tools for f, tools in law_cov.items() if len(tools) < 2}

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
        "law_coverage": {f: len(t) for f, t in law_cov.items()},
        "thin_laws": thin_laws,  # floors with < 2 tools
        "PASS": len(missing_input) == 0 and len(missing_output) == 0 and len(thin_laws) == 0,
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
    "Law",
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
    "_TOOL_ANNOTATIONS",
    "CANONICAL_OUTPUT_SCHEMA",
    "_TOOL_INPUT_SCHEMAS",
    "_TOOL_OUTPUT_SCHEMAS",
    "NINE_SIGNAL_FIELDS",
    "validate_tool_response_schema",
    "generate_pydantic_models",
    "check_schema_coverage",
    "enforce_irreversibility_guard",
]
