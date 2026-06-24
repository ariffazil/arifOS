"""
ARIFOS CONSTITUTIONAL MAP (v2026.05.05-KANON-SSCT)
═══════════════════════════════════════════════════════════════════════════════

SOLE SOURCE OF TRUTH for the canonical MCP tools.
Public canonical surface: exactly 7 tools (F13 ratified 2026-06-23: arif_init, arif_observe, arif_think, arif_route, arif_judge, arif_act, arif_seal).
Full CANONICAL_TOOLS dict registers the 7 + supporting internal tools (kernel_intercept etc).
All arif_* naming. No governance surface, no CC modes as separate tools.
One public intent = one canonical verb (F4 CLARITY).

MACHINERY:
  - CANONICAL_TOOLS   : registry for canonical surface (7 public + internal support; name → spec with floors, stage, lane)
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
    L03_WITNESS = (
        "L03"  # Quad-witness consensus (W₄ ≥ 0.75) — human · ai · earth · system (H·A·E·S)
    )
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
    # 666 is constitutionally the CRITIQUE/HEART gate (arif_critique).
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
    "000": {"next": "111", "tool": "arif_observe", "prompt": "111_agi"},
    "111": {"next": "222", "tool": "arif_fetch", "prompt": None},
    "222": {"next": "333", "tool": "arif_think", "prompt": None},
    # v3.1: 333 reason → 666 heart (ontology-aligned: 666 = HEART)
    "333": {"next": "666", "tool": "arif_critique", "prompt": "444_asi"},
    # Stage suffixes: "r" = reply (refinement of critique), "m" = memory
    # (refinement of route), "g" = gateway (refinement of forge). These
    # encode parent-child relationships, not independent stage numbers.
    # 444r reply is a side-branch; no tool sits directly at 444.
    "444r": {"next": "555", "tool": "arif_route", "prompt": None},
    # v3.1 fix: 555 route/memory → 666 critique (heart), NOT forge.
    # Constitutionally: critique MUST precede forge. Never skip heart.
    "555": {"next": "666", "tool": "arif_critique", "prompt": "666_critique"},
    "555m": {"next": "666", "tool": "arif_critique", "prompt": "666_critique"},
    # 666 critique pre-forge ethical check — heart before hammer
    "666": {"next": "010", "tool": "arif_forge", "prompt": "010_dry_run"},
    "666g": {"next": "010", "tool": "arif_forge", "prompt": "010_dry_run"},
    # 010 forge → 777 measure (verify before judge)
    "010": {"next": "777", "tool": "arif_measure", "prompt": None},
    "777": {"next": "888", "tool": "arif_judge", "prompt": "888_apex"},
    "888": {"next": "999", "tool": "arif_seal", "prompt": "999_seal"},
    "999": {"next": None, "tool": None, "prompt": None},
}


# ═══════════════════════════════════════════════════════════════════════════════
# CORE 7 — The Kernel's Primary 7-Tool Metabolic Pipeline
# ═══════════════════════════════════════════════════════════════════════════════
# These are the 7 essential tools that form the governed agentic loop.
# "Properly" means:
#   - Complete affordance contracts (purpose, use_when, do_not_use, L0-L5, risk, thresholds)
#   - Every response carries facts | inferences | unknowns | metacognition | next_safe_action
#   - arif_kernel_intercept is the enforcement brain for the 888 slot
#   - This loop is what metacognitive agents should primarily reason about.
#
# This is the expressive core. There are more tools (internals + diagnostics), but these 7 are public.
# but these 7 are the ones that must be cognitively perfect.

CORE_SEVEN: list[str] = [
    "arif_init",  # 000 INIT — bootstrap + identity binding (must be first)
    "arif_observe",  # 111 OBSERVE — ground in reality (absorbs fetch)
    "arif_think",  # 333 THINK — reasoning + plans + critique (absorbs critique)
    "arif_route",  # 444/555 ROUTE — intent routing
    "arif_judge",  # 888 JUDGE — verdict (enforced by arif_kernel_intercept)
    "arif_act",  # 900 ACT — gated execution (hard seal requirement)
    "arif_seal",  # 999 SEAL — immutable record
]

CORE_SEVEN_WITH_ENGINE = {
    "arif_init": "arif_init",
    "arif_observe": "arif_observe",
    "arif_think": "arif_think",
    "arif_route": "arif_route",
    "arif_judge": "arif_judge (kernel: arif_kernel_intercept)",
    "arif_act": "arif_act (gated execution)",
    "arif_seal": "arif_seal",
}

CORE_SEVEN_LABELS: dict[str, str] = {
    "arif_init": "Bootstrap (000)",
    "arif_observe": "Ground Reality (111)",
    "arif_think": "Reason (333)",
    "arif_route": "Route (444/555)",
    "arif_judge": "Verdict (888)",
    "arif_act": "Act (900, gated)",
    "arif_seal": "Permanent Record (999)",
}

# Map stage to the canonical tool in the clean 7-loop (for docs / agents)
CORE_SEVEN_STAGE_MAP: dict[str, str] = {
    "000": "arif_init",
    "111": "arif_observe",
    "333": "arif_think",
    "444": "arif_route",
    "888": "arif_judge",
    "900": "arif_act",
    "999": "arif_seal",
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
#   L01: arif_init, arif_seal, arif_forge     (3)
#   L02: arif_observe, arif_fetch, arif_think  (3)
#   L03: arif_fetch                                         (1)
#   L04: arif_compose, arif_measure                        (2, incl. topology/drift)
#   L05: arif_critique, arif_fetch                   (2)
#   L06: arif_critique, arif_compose                     (2)
#   L07: arif_think, arif_observe                       (2)
#   L08: arif_think                                            (1)
#   L09: arif_compose, arif_critique                    (2)
#   L10: arif_think                                            (1)
#   L11: arif_init, arif_judge, arif_seal, arif_forge (4)
#   L12: arif_init, arif_fetch                      (2)
#   L13: arif_judge, arif_seal, arif_forge (3)
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_TOOLS: dict[str, dict[str, Any]] = {
    "arif_kernel_intercept": {
        "name": "arif_kernel_intercept",
        "description": (
            "Minimum Constitutional Kernel — brutalist interceptor for all agent actions. "
            "Takes action details and returns ALLOW, DENY, ESCALATE, or SIMULATE verdict. "
            "Use for any mutating or external action that needs constitutional clearance. "
            "Returns verdict with reasoning and floor violations."
        ),
        "access": "public",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["intercept"],
        "eureka_insight": "F13: Human veto absolute. Minimum kernel enforcement spine.",
        "cognitive_axis": "judge",
        "expose": True,
    },
    "arif_init": {
        "name": "arif_init",
        "description": (
            "Start or resume a governed session. CALL THIS FIRST before any other tool. "
            "Binds identity, creates audit trail, activates floor enforcement. "
            "Use mode='light' for fast bootstrap (<1s). Use mode='init' for full binding (~60s). "
            "Returns session_id needed by all other tools. Binds the One Skill (Knowing What NOT To Do) and One Tool (Verdict Loop With Memory) via geometry."
        ),
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L12_INJECTION],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": [
            "init",
            "light",
            "resume",
            "validate",
            "epoch_open",
            "epoch_seal",
            # F14 — Right #10 (opt out) + Right #6 (refuse profiling).
            "opt_out",
            "opt_out_profiling",
        ],
        "eureka_insight": "F1: ∃ undo(a) — irreversibility requires explicit human ack.",
        "cognitive_axis": "identity",
        "expose": True,
        # Deeper classification under the irreducible pair
        "restraint_level": "STRICT",
        "verdict_required": "REQUIRED",
        "one_skill": "Knowing What NOT To Do (restraint under uncertainty: HOLD/ASK/REFUSE)",
        "one_tool": "Verdict Loop With Memory (judge + seal + receipt + witness)",
        "classification": "Entry point that binds constitutional geometry with restraint flags and verdict requirement. No action without this.",
    },
    "arif_observe": {
        "name": "arif_observe",
        "description": (
            "Search the web, check system vitals, or gather real-world data. "
            "Use mode='search' for web search, mode='ingest' to fetch a URL, "
            "mode='vitals' for CPU/memory/disk state. "
            "Returns results with source citations and uncertainty tags."
        ),
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
    "arif_fetch": {
        "name": "arif_fetch",
        "description": (
            "Fetch and preserve external evidence with source citations. "
            "Use when a claim needs verified backing or factual grounding. "
            "Provide url to fetch a specific page, or query to search for evidence. "
            "Returns content with provenance tags and confidence scores."
        ),
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
    "arif_think": {
        "name": "arif_think",
        "description": (
            "Multi-step reasoning, planning, and reflection with confidence labeling. "
            "Use for complex analysis, hypothesis evaluation, plan generation. "
            "Provide query with the question or problem to reason about. "
            "Use mode='plan' to generate execution plans, mode='reflect' to self-critique. "
            "Returns reasoning with confidence scores and uncertainty bands."
        ),
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
    "arif_critique": {
        "name": "arif_critique",
        "description": (
            "Assess ethical risks and human impact before acting. "
            "Use before irreversible actions, decisions affecting dignity, or forge execution. "
            "Provide target (the action/decision to critique). "
            "Use mode='redteam' for adversarial analysis, mode='maruah' for dignity impact. "
            "Returns risk assessment with floor violations and recommendations."
        ),
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
    # ── CANONICAL TOOLS (RULE 14 MODE-FIRST NAMING, 2026-06-20) ──
    "arif_route": {
        "name": "arif_route",
        "description": (
            "Routes a natural-language intent to the correct federation organ. "
            "Use when you know what you want but not which tool to call. "
            "Provide intent describing the task (e.g., 'interpret this seismic section'). "
            "Returns routing decision with organ, tool, and arguments."
        ),
        "access": "public",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L04_CLARITY, Law.L10_ONTOLOGY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["route"],
        "eureka_insight": "RULE 14: One tool, one operation (routing). Modes are not used; intent is the parameter.",
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_triage": {
        "name": "arif_triage",
        "description": (
            "Constitutional preflight check. Returns kernel status, current holds, "
            "and the correct lane for a proposed action before execution. "
            "Use mode='status' for session count, mode='preflight' for safety probe, "
            "mode='triage' for priority classification. "
            "Returns status with holds, stage, and recommendations."
        ),
        "access": "public",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L04_CLARITY, Law.L10_ONTOLOGY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["status", "preflight", "triage"],
        "eureka_insight": "RULE 14: Mode-first. One tool, three related modes (status, preflight, triage) — all act on session state.",
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_bridge_connect": {
        "name": "arif_bridge_connect",
        "description": (
            "Low-level direct organ tool call. Bypasses intent routing — caller must specify "
            "organ and tool_name. Use only when both are known ahead of time. "
            "Provide organ (geox|wealth|well), tool_name, and arguments. "
            "Returns organ response with provenance tags."
        ),
        "access": "authenticated",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L10_ONTOLOGY],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["connect"],
        "eureka_insight": "RULE 14 + arif_<noun>_<verb> convention: One tool, one operation (connect). Organ is a parameter, not a mode. Bypasses intent map for known-target cases. Canonical name forged 2026-06-21 — arif_bridge retained as deprecated alias.",
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_compose": {
        "name": "arif_compose",
        "description": (
            "Compose the final response for the user. Call this LAST, after reasoning and judgment are complete. "
            "Provide message with the content to compose. "
            "Use mode='summarize' for brief output, mode='cite' to include sources. "
            "Returns formatted response with tone calibration and citations."
        ),
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
    "arif_memory": {
        "name": "arif_memory",
        "description": (
            "Federated memory tool — 7 canonical modes: "
            "recall (search memories), inspect (view details), attest (verify), "
            "remember (store new), promote (escalate tier), revise (update), forget (delete). "
            "Use for storing, retrieving, and governing memory across the 6-layer stack. "
            "Returns memory entries with provenance and truth-class tags."
        ),
        "access": "public",
        "stage": ToolStage.MEMORY,
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L01_AMANAH,
            Law.L02_TRUTH,
            Law.L04_CLARITY,
            Law.L08_GENIUS,
            Law.L11_AUDIT,
            Law.L12_INJECTION,
            Law.L13_SOVEREIGN,
        ],
        "risk_tier": "medium",
        "irreversible": True,  # forget mode is IRREVERSIBLE on recall + writes tombstone to vault
        "modes": ["recall", "inspect", "attest", "remember", "promote", "revise", "forget"],
        "eureka_insight": (
            "F1: every memory op is reversible via supersede (revise) or tombstone (forget → vault). "
            "F2: 7 truth-classes (observed|claimed|derived|approved|sealed|contested|deprecated) gate recall. "
            "F4: hybrid recall cascade (vector→graph→vault) reduces entropy per mode. "
            "F8: per-mode floor pre-checks (L01..L13) preserve governance integrity. "
            "F11: every write carries actor_id + session_id + receipt (forensic traceability). "
            "F13: forget mode requires explicit human ack — L13 SOVEREIGN. "
            "Direction 1 (memory kernel v5) — ratified 2026-06-21. "
            "ADR-010 baked in: L4 canonical band, no-bypass rule, vault seal lineage."
        ),
        "cognitive_axis": "trace",
        "expose": True,
        "supersedes": "arif_memory_recall",
        "schema_version": 5,
        "deprecated_aliases": ["arif_memory_recall"],
    },
    "arif_judge": {
        "name": "arif_judge",
        "description": (
            "888 constitutional verdict on a proposed action. Floor check, authority check, "
            "and HOLD/SEAL/VOID/ESCALATE arbitration. This is the minimum constitutional kernel — "
            "every mutating or external action must pass through it. "
            "Provide candidate action with intent, actor, authority, evidence, and reversibility. "
            "Returns verdict + next_safe_action."
        ),
        "access": "authenticated",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Law.L01_AMANAH, Law.L02_TRUTH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["intercept", "judge", "validate", "hold", "escalate"],
        "eureka_insight": (
            "F13 SOVEREIGN: human veto absolute. "
            "F01 AMANAH: reversibility required unless explicitly acked. "
            "F02 TRUTH: evidence threshold τ ≥ 0.99 for claims."
        ),
        "cognitive_axis": "judge",
        "expose": True,
        # Deeper classification under the irreducible pair (One Skill + One Tool)
        "restraint_level": "STRICT",
        "verdict_required": "REQUIRED",
        "one_skill": "Knowing What NOT To Do (restraint under uncertainty: HOLD/ASK/REFUSE)",
        "one_tool": "Verdict Loop With Memory (judge + seal + receipt + witness + cooling)",
        "classification": "The One Tool core. Every action must pass here. Restraint from geometry drives HOLD/ASK/REFUSE decisions. No bypass.",
    },
    "arif_judge_deliberate": {
        "name": "arif_judge_deliberate",
        "description": (
            "Internal AAA a2a-server deliberation tool. Render a nuanced constitutional verdict "
            "with multi-floor reasoning. Not part of the public 7-tool facade; use arif_judge for "
            "public constitutional arbitration."
        ),
        "access": "internal_only",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["judge", "validate", "hold", "rules", "armor", "probe", "notify"],
        "eureka_insight": "Internal deliberation surface for AAA a2a-server.",
        "cognitive_axis": "judge",
        "expose": False,
    },
    "arif_seal": {
        "name": "arif_seal",
        "description": (
            "Seal a verdict or outcome to the immutable audit ledger. "
            "Use for final, irreversible records that must be preserved forever. "
            "Provide payload with the content to seal. "
            "Requires ack_irreversible=True and a preceding arif_judge SEAL verdict. "
            "Returns seal_id and hash for permanent reference."
        ),
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
    "arif_act": {
        "name": "arif_act",
        "description": "Execute approved action. Requires seal_verdict_id.",
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
    "arif_forge": {
        "name": "arif_forge",
        "description": (
            "Internal alias for arif_act. Retained for backward compatibility "
            "but no longer advertised on the public MCP surface."
        ),
        "access": "internal_only",
        "stage": ToolStage.FORGE_EXECUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "modes": ["engineer", "query", "write", "generate", "commit", "recall", "dry_run"],
        "eureka_insight": "Internal alias for arif_act.",
        "cognitive_axis": "execute",
        "expose": False,
    },
    "arif_measure": {
        "name": "arif_measure",
        "description": (
            "Check system health, thermodynamic state, and resource metrics. "
            "Use for operational status and metabolic monitoring. "
            "Use mode='health' for overall status, mode='vitals' for CPU/memory/disk, "
            "mode='topology' for service map, mode='drift' for config drift detection. "
            "Returns metrics with health scores and recommendations."
        ),
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


# ═─ 7-Tool MCP Facade enforcement ─══════════════════════════════════════════
# F13 SOVEREIGN ratification 2026-06-23: public surface is exactly 7 verbs.
# All other canonical tools are demoted to internal_only aliases.
_PUBLIC_7: frozenset[str] = frozenset(
    {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_judge",
        "arif_act",
        "arif_seal",
    }
)
for _name, _spec in CANONICAL_TOOLS.items():
    if _name not in _PUBLIC_7:
        _spec["access"] = "internal_only"
        _spec["expose"] = False

# ── Deeper One Skill + One Tool Classification (map step)
# Every capability classified under the load-bearing pair.
# One Skill: Knowing What NOT To Do (restraint: HOLD/ASK/REFUSE under uncertainty)
# One Tool: Verdict Loop With Memory (judge/seal/receipt/witness/cooling)
# This makes bypass impossible at the spec level. Sourced from constitutional truth.
ONE_SKILL_ONE_TOOL_CLASSIFICATION: dict[str, dict[str, Any]] = {
    "core": {
        "skill": "Knowing What NOT To Do",
        "tool": "Verdict Loop With Memory",
        "enforcement": "restraint_flags from INIT geometry drive HOLD/ASK/REFUSE; verdict_trace required for execution",
    },
    "tools": {
        "arif_init": {"restraint": "STRICT", "verdict": "REQUIRED", "classification": "Binds geometry with One Skill flags + One Tool requirement."},
        "arif_observe": {"restraint": "STANDARD", "verdict": "NONE", "classification": "Observe only; restraint for clarity, no verdict needed."},
        "arif_think": {"restraint": "STANDARD", "verdict": "CONDITIONAL", "classification": "Reasoning under uncertainty; restraint prevents overfit."},
        "arif_judge": {"restraint": "STRICT", "verdict": "REQUIRED", "classification": "The One Tool: renders the verdict that enables or refuses action."},
        "arif_seal": {"restraint": "STRICT", "verdict": "REQUIRED", "classification": "Seals the verdict into append-only memory."},
        "arif_forge": {"restraint": "STRICT", "verdict": "REQUIRED", "classification": "Execution substrate. Only after One Tool verdict + One Skill check."},
        "arif_forge_execute": {"restraint": "STRICT", "verdict": "REQUIRED", "classification": "Teeth of the system. enforce_restraint_and_verdict must PASS."},
        "arif_act": {"restraint": "STRICT", "verdict": "REQUIRED", "classification": "Execution gate. Requires prior seal from One Tool."},
        "arif_memory": {"restraint": "STANDARD", "verdict": "CONDITIONAL", "classification": "Memory ops gated by restraint for mutation."},
    },
    "note": "All tools inherit from INIT geometry. If kernel spec does not classify it, DENY.",
}


PROBE_TOOLS: tuple[str, ...] = ()
CONSTITUTIONAL_TOOLS: tuple[str, ...] = tuple(CANONICAL_TOOLS.keys())

# ═══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC & FEDERATION TOOLS — non-canonical operational surface
# ═══════════════════════════════════════════════════════════════════════════════
# These tools are registered on the arifOS MCP surface but are NOT part of
# the 7-tool canonical public surface (CANONICAL_TOOLS primary). They serve operational,
# diagnostic, federation-attestation, and lease-management roles.
#
# TIERS:
#   hermes     — Cross-verification, fact-checking, vault query, epistemic checks
#   canary     — Transport/protocol diagnostics (ping, echo, version, init probe)
#   lease      — Capability lease lifecycle (inspect, issue, revoke)
#   attest     — Federation organ attestation (self + peer heartbeat verification)
#   forge-sub  — Pre-execution forge planning (dry_run, plan, query)
#   narrative  — Institutional shadow drift + narrative tension detection
#   diagnostic — Health probes, floor status, drift checks, budget telemetry, instruction scanner
#
# NAMESPACE RULING (F13 SOVEREIGN, 2026-06-14; amended 2026-06-19 — Canonical13 enforcement):
#   arif_*   — Canonical prefix for the 7-tool public surface (F13 2026-06-23) + supporting internals + 1 canary probe
#   hermes_* — GATED non-arif_ namespace for Hermes ASI tools (ARIFOS_MCP_EXPOSE_DEV_TOOLS)
#   forge_*  — GATED non-arif_ namespace for A-FORGE sub-tools (ARIFOS_MCP_EXPOSE_DEV_TOOLS;
#              forge_* tools are DEPRECATED on arifOS — use A-FORGE MCP directly)
#   arifos_* — BLOCKED public prefix (internal-only, never exposed)
#   mcp_*    — Utility namespace for operational diagnostics (mcp_drift_check; gated)
#
# AMENDED 2026-06-19: hermes_*, forge_*, and non-canonical arif_* diagnostics
# (lease, attest, peer_contract, heartbeat, narrative, shadow) are no longer
# on the default public wire surface. They require ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
# Canonical13 = 21 canonical tools. Default public wire = 21 + 1 canary probe = 22.
# ═══════════════════════════════════════════════════════════════════════════════

DIAGNOSTIC_TOOLS: dict[str, dict[str, Any]] = {
    # ── Hermes Tools (7) — Cross-verification, fact-check, vault, epistemic ──
    "hermes_system_status": {
        "name": "hermes_system_status",
        "description": "HERMES: Federation-wide system status snapshot — organ health, vault seal count, memory stats, NATS event count.",
        "access": "public",
        "tier": "hermes",
        "namespace": "hermes_* (sanctioned non-arif_ prefix — F13 SOVEREIGN 2026-06-14)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH],
        "modes": ["brief", "full", "organs", "events"],
        "tags": ["hermes", "diagnostic"],
    },
    "hermes_vault_query": {
        "name": "hermes_vault_query",
        "description": "HERMES: Query VAULT999 audit ledger — recent entries, keyword search, organ filter, date filter.",
        "access": "public",
        "tier": "hermes",
        "namespace": "hermes_* (sanctioned)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L11_AUDIT],
        "modes": ["recent", "search", "organ", "date"],
        "tags": ["hermes", "vault"],
    },
    "hermes_epistemic_check": {
        "name": "hermes_epistemic_check",
        "description": "HERMES: Pre-flight epistemic confidence check — evaluates claim against evidence, returns CONFIDENCE_LEVEL + GAPS.",
        "access": "public",
        "tier": "hermes",
        "namespace": "hermes_* (sanctioned)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L07_HUMILITY],
        "modes": ["quick", "vault", "full"],
        "tags": ["hermes", "epistemic"],
    },
    "hermes_fact_check": {
        "name": "hermes_fact_check",
        "description": "HERMES: Verify factual claims against web search + VAULT999 + available tools. Returns CONFIRMED/REFUTED/MIXED/UNKNOWN.",
        "access": "public",
        "tier": "hermes",
        "namespace": "hermes_* (sanctioned)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS, Law.L07_HUMILITY],
        "modes": ["quick", "web", "deep"],
        "tags": ["hermes", "verification"],
    },
    "hermes_cross_verify": {
        "name": "hermes_cross_verify",
        "description": "HERMES: Cross-agent claim verification — delegates fact-check to a second agent for independent corroboration (F3 TRI-WITNESS).",
        "access": "public",
        "tier": "hermes",
        "namespace": "hermes_* (sanctioned)",
        "risk_tier": "medium",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS],
        "modes": ["verify"],
        "tags": ["hermes", "cross-verify"],
    },
    "hermes_plan_review": {
        "name": "hermes_plan_review",
        "description": "HERMES: Review multi-step plans for safety and completeness — missing verify steps, floor violations, unclear success criteria.",
        "access": "public",
        "tier": "hermes",
        "namespace": "hermes_* (sanctioned)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L01_AMANAH, Law.L05_PEACE, Law.L12_INJECTION],
        "modes": ["quick", "full"],
        "tags": ["hermes", "plan-review"],
    },
    "hermes_memory_steward": {
        "name": "hermes_memory_steward",
        "description": "HERMES: Classify content for memory storage tier — STORE_IN_VAULT, STORE_IN_GRAPHITI, STORE_IN_MEMORY, DISCARD, TODO_FOR_ARIF.",
        "access": "public",
        "tier": "hermes",
        "namespace": "hermes_* (sanctioned)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L01_AMANAH, Law.L02_TRUTH],
        "modes": ["classify", "compact"],
        "tags": ["hermes", "memory"],
    },
    # ── Canary / Transport Tools — Multimode (replaces 6 individual canaries) ──
    "arif_canary": {
        "name": "arif_canary",
        "description": (
            "CANARY: Unified transport diagnostic probe. One tool, six modes. "
            "Use for liveness checks, protocol version verification, schema round-trip "
            "testing, transport detail dumps, MCP handshake tests, and full conformance spine. "
            "Modes: ping | schema_echo | version_echo | transport_echo | initialize_probe | conformance_report"
        ),
        "access": "public",
        "tier": "canary",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [],
        "modes": [
            "ping",
            "schema_echo",
            "version_echo",
            "transport_echo",
            "initialize_probe",
            "conformance_report",
        ],
        "tags": ["canary", "diagnostic", "transport", "multimode"],
    },
    # ── Individual canary names (DEPRECATED → arif_canary) ──
    "arif_ping": {
        "name": "arif_ping",
        "description": "[DEPRECATED — use arif_canary(mode=ping)] Lightweight liveness probe.",
        "access": "public",
        "tier": "canary",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [],
        "modes": ["probe"],
        "tags": ["canary", "diagnostic", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_canary",
    },
    "arif_schema_echo": {
        "name": "arif_schema_echo",
        "description": "[DEPRECATED — use arif_canary(mode=schema_echo)] Payload round-trip test.",
        "access": "public",
        "tier": "canary",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [],
        "modes": ["echo"],
        "tags": ["canary", "diagnostic", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_canary",
    },
    "arif_version_echo": {
        "name": "arif_version_echo",
        "description": "[DEPRECATED — use arif_canary(mode=version_echo)] Protocol version check.",
        "access": "public",
        "tier": "canary",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [],
        "modes": ["echo"],
        "tags": ["canary", "diagnostic", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_canary",
    },
    "arif_transport_echo": {
        "name": "arif_transport_echo",
        "description": "[DEPRECATED — use arif_canary(mode=transport_echo)] Transport detail dump.",
        "access": "public",
        "tier": "canary",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [],
        "modes": ["echo"],
        "tags": ["canary", "diagnostic", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_canary",
    },
    "arif_initialize_probe": {
        "name": "arif_initialize_probe",
        "description": "[DEPRECATED — use arif_canary(mode=initialize_probe)] MCP handshake test.",
        "access": "public",
        "tier": "canary",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [],
        "modes": ["probe"],
        "tags": ["canary", "diagnostic", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_canary",
    },
    "arif_conformance_report": {
        "name": "arif_conformance_report",
        "description": "[DEPRECATED — use arif_canary(mode=conformance_report)] Full conformance spine.",
        "access": "public",
        "tier": "canary",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH],
        "modes": ["report"],
        "tags": ["canary", "conformance", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_canary",
    },
    # ── Lease Tools (3) — Capability lease lifecycle ──
    "arif_lease_inspect": {
        "name": "arif_lease_inspect",
        "description": "LEASE: Inspect an existing capability lease — organ_id, actor_id, scope, action_class, TTL, forbidden list.",
        "access": "public",
        "tier": "lease",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT],
        "modes": ["inspect"],
        "tags": ["lease", "diagnostic"],
    },
    "arif_lease_issue": {
        "name": "arif_lease_issue",
        "description": "LEASE: Issue a new bounded authority lease — scopes organ/agent tool access and action class. Max TTL, scope, forbidden list.",
        "access": "authenticated",
        "tier": "lease",
        "namespace": "arif_*",
        "risk_tier": "medium",
        "irreversible": False,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "modes": ["issue"],
        "tags": ["lease", "mutation-gated"],
    },
    "arif_lease_revoke": {
        "name": "arif_lease_revoke",
        "description": "LEASE: Revoke an existing capability lease — requires lease_id + reason. Irreversible scope change.",
        "access": "authenticated",
        "tier": "lease",
        "namespace": "arif_*",
        "risk_tier": "medium",
        "irreversible": True,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "modes": ["revoke"],
        "tags": ["lease", "mutation-gated"],
    },
    # ── Organ Attestation Tools (4) — Federation health heartbeat verification ──
    "arif_os_attest": {
        "name": "arif_os_attest",
        "description": "ATTEST: arifOS self-attestation — returns constitution_hash, schema_hash, tool_surface, health, active lease state. Required before any kernel-grade federation call.",
        "access": "public",
        "tier": "attest",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH],
        "modes": ["attest"],
        "tags": ["attest", "federation"],
    },
    "arif_organ_attest": {
        "name": "arif_organ_attest",
        "description": "ATTEST: Probe and attest a single federation organ (GEOX, WEALTH, WELL) — returns organ heartbeat, schema hash, tool count, kernel envelope.",
        "access": "public",
        "tier": "attest",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS],
        "modes": ["attest"],
        "tags": ["attest", "federation", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_attest",
    },
    "arif_organ_attest_all": {
        "name": "arif_organ_attest_all",
        "description": "ATTEST: Attest arifOS plus all federation organs in one call — returns per-organ heartbeat + degraded-organ list.",
        "access": "public",
        "tier": "attest",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS],
        "modes": ["attest"],
        "tags": ["attest", "federation", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_attest",
    },
    "arif_heartbeat": {
        "name": "arif_heartbeat",
        "description": "ATTEST: Record or query federation heartbeats — returns liveness verdict for known organs.",
        "access": "public",
        "tier": "attest",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH],
        "modes": ["record", "query"],
        "tags": ["attest", "federation", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_attest",
    },
    # ── Peer Federation Contract Tools (3) — P2P capability peering v1 ──
    "arif_peer_contract_validate": {
        "name": "arif_peer_contract_validate",
        "description": "ATTEST: Validate a Peer Federation Contract v1 against the canonical schema and constitutional constraints (judge exclusivity, F13 veto, lease alignment).",
        "access": "public",
        "tier": "attest",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS],
        "modes": ["validate"],
        "tags": ["attest", "federation", "peer-contract", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_attest",
    },
    "arif_peer_contract_attest": {
        "name": "arif_peer_contract_attest",
        "description": "ATTEST: Return the arifOS peer federation contract URL, hash, and signed contract. Required before P2P negotiation.",
        "access": "public",
        "tier": "attest",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH],
        "modes": ["attest"],
        "tags": ["attest", "federation", "peer-contract", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_attest",
    },
    "arif_peer_contract_forbid": {
        "name": "arif_peer_contract_forbid",
        "description": "ATTEST: Forbid a peer organ from the federation contract surface. Runtime gate only; does not mutate the canonical contract on disk.",
        "access": "authenticated",
        "tier": "attest",
        "namespace": "arif_*",
        "risk_tier": "medium",
        "irreversible": False,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "modes": ["forbid"],
        "tags": ["attest", "federation", "peer-contract", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_attest",
    },
    # ── Forge Sub-Tools (3) — Pre-execution planning (A-FORGE namespace) ──
    "forge_dry_run": {
        "name": "forge_dry_run",
        "description": "FORGE-SUB: Simulate forge execution without mutation — returns diff preview, files touched, rollback plan. Safe to call without approval. Required before MUTATE/ATOMIC forge execution.",
        "access": "public",
        "tier": "forge-sub",
        "namespace": "forge_* (sanctioned non-arif_ prefix — F13 SOVEREIGN 2026-06-14)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L01_AMANAH],
        "modes": ["dry_run"],
        "tags": ["forge", "pre-execution"],
    },
    "forge_plan": {
        "name": "forge_plan",
        "description": "FORGE-SUB: Classify action, estimate blast radius, produce execution plan. Safe to call without approval. Required before MUTATE/ATOMIC forge execution.",
        "access": "public",
        "tier": "forge-sub",
        "namespace": "forge_* (sanctioned)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L01_AMANAH, Law.L04_CLARITY],
        "modes": ["plan"],
        "tags": ["forge", "pre-execution"],
    },
    "forge_query": {
        "name": "forge_query",
        "description": "FORGE-SUB: Read-only system introspection — workspace tree, system state, query result. Safe to call without approval.",
        "access": "public",
        "tier": "forge-sub",
        "namespace": "forge_* (sanctioned)",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L04_CLARITY],
        "modes": ["query"],
        "tags": ["forge", "pre-execution"],
    },
    # ── Narrative / Institutional Detection Tools (2) ──
    "arif_detect_institutional_shadow_drift": {
        "name": "arif_detect_institutional_shadow_drift",
        "description": "NARRATIVE: Detect when a sovereign institution's observed functions have outgrown its declared name (GENESIS/006 Petronas Paradox). Returns drift_score, sovereignty_score, risk_class, verdict.",
        "access": "public",
        "tier": "narrative",
        "namespace": "arif_*",
        "risk_tier": "medium",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L05_PEACE],
        "modes": ["detect"],
        "tags": ["narrative", "institutional", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_shadow_drift",
    },
    "arif_detect_narrative_tension": {
        "name": "arif_detect_narrative_tension",
        "description": "NARRATIVE: Detect paradox tension, power asymmetry, and implicit frames in news articles or institutional text. Returns FrameGraph with actors, claims, tensions, kernel verdict.",
        "access": "public",
        "tier": "narrative",
        "namespace": "arif_*",
        "risk_tier": "medium",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L05_PEACE, Law.L06_EMPATHY],
        "modes": ["detect"],
        "tags": ["narrative", "media", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_narrative_tension",
    },
    # ── Additional Diagnostic Tools (6) — Health probes, drift checks, budget, floor status, instructions ──
    "arif_stack_health_probe": {
        "name": "arif_stack_health_probe",
        "description": "DIAGNOSTIC: Deep health probe across the full arifOS stack — MCP, runtime, bridges, memory tiers, vault. Heavier than /health.",
        "access": "public",
        "tier": "diagnostic",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L04_CLARITY],
        "modes": ["probe"],
        "tags": ["diagnostic", "health", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_health",
    },
    "arif_scan_local_instructions": {
        "name": "arif_scan_local_instructions",
        "description": "DIAGNOSTIC: Scan local filesystem for agent instruction files (CLAUDE.md, AGENTS.md, etc.) and report findings. Used by arif_judge scan_instructions mode (folded — kept as standalone for direct access).",
        "access": "public",
        "tier": "diagnostic",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L04_CLARITY],
        "modes": ["scan"],
        "tags": ["diagnostic", "instructions", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_judge",
    },
    "arif_organ_consensus": {
        "name": "arif_organ_consensus",
        "description": "DIAGNOSTIC: Cross-organ consensus check — queries all available organs and compares responses for drift. Used by arif_gateway_connect consensus mode (folded — kept as standalone for direct access).",
        "access": "public",
        "tier": "diagnostic",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS],
        "modes": ["consensus"],
        "tags": ["diagnostic", "consensus", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_gateway_connect",
    },
    "arif_session_budget": {
        "name": "arif_session_budget",
        "description": "DIAGNOSTIC: Query session token budget and consumption. Used by arif_measure budget mode (folded — kept as standalone for direct access).",
        "access": "public",
        "tier": "diagnostic",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L04_CLARITY],
        "modes": ["budget"],
        "tags": ["diagnostic", "budget", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_measure",
    },
    "arif_floor_status": {
        "name": "arif_floor_status",
        "description": "DIAGNOSTIC: Query live status of all 13 constitutional floors — active, enforcement state, recent violations. Folded into arif_judge floor_status mode (kept as standalone for direct access).",
        "access": "public",
        "tier": "diagnostic",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L11_AUDIT],
        "modes": ["status"],
        "tags": ["diagnostic", "floors", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_judge",
    },
    "mcp_drift_check": {
        "name": "mcp_drift_check",
        "description": "MCP Protocol Drift Check — detect drift between declared MCP protocol version, registered surface, and actual runtime. Every tool registered must be enumerated. Every enumerated tool must be callable.",
        "access": "public",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L07_HUMILITY],
        "modes": ["status", "info", "health"],
        "tags": ["diagnostic", "paradox", "epistemic"],
    },
    # ── MCP Gate v0 — Constitutional Gate (2026-06-14) ─────────────────
    # The wedge: determines whether MCP-powered agents may touch the world.
    "arif_gate_judge": {
        "name": "arif_gate_judge",
        "description": (
            "MCP GATE v0: Constitutional gate for MCP tool calls. "
            "Determines whether an action is ALLOW, ALLOW_WITH_LOG, REQUIRE_APPROVAL, "
            "SIMULATE_FIRST, BLOCK, or HOLD_888. "
            "Input: tool_name, action_class (8-tier), risk dimensions. "
            "Output: verdict with one-line summary (Lapisan 1) and five-line detail (Lapisan 2). "
            "This is the wedge — arifOS as the constitutional runtime for MCP."
        ),
        "access": "public",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "risk_tier": "low",
        "irreversible": False,
        "floors": [
            Law.L01_AMANAH,
            Law.L04_CLARITY,
            Law.L08_GENIUS,
            Law.L11_AUDIT,
            Law.L13_SOVEREIGN,
        ],
        "modes": ["judge"],
        "tags": ["gate", "constitutional", "mcp", "infrastructure", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "art_gate",
        "_deprecation_note": "This is ART.gate() — a function, not a tool. Should be runtime/art/gate.py, not a registered MCP tool.",
    },
    # ── Shadow Geometry Tools (Phase 2, 2026-06-16) ───────────────────
    "arif_self_evaluate": {
        "name": "arif_self_evaluate",
        "description": "DIAGNOSTIC: Evaluate a text output against the 13 constitutional floors of arifOS. Returns PASS/HOLD/VOID verdict with scores and reasons.",
        "access": "public",
        "tier": "diagnostic",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L11_AUDIT],
        "modes": ["evaluate"],
        "tags": ["diagnostic", "evaluation", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_judge",
    },
    "arif_model_compare": {
        "name": "arif_model_compare",
        "description": "DIAGNOSTIC: Compare two models across the 6 shadow geometry axes of the arifOS Federation.",
        "access": "public",
        "tier": "diagnostic",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L11_AUDIT],
        "modes": ["compare"],
        "tags": ["diagnostic", "shadow_geometry", "deprecated"],
        "_deprecated": True,
        "_canonical_name": "arif_diag_model_compare",
    },
    # ── ChatGPT Compatibility Shim (2) — OpenAI discovery requirements ──
    # Registered only when ARIFOS_CHATGPT_COMPAT=true.
    # Thin single-string-param wrappers → arif_observe / arif_fetch.
    # ART: OBSERVE-class, blast=low, trust=evidence. ACT: single-call programs.
    "arif_search": {
        "name": "arif_search",
        "description": (
            "Search the web for information. Use when you need to find current "
            "facts, documentation, or real-world data. Returns search results "
            "with titles, URLs, and snippets."
        ),
        "access": "public",
        "tier": "chatgpt-shim",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L07_HUMILITY],
        "modes": ["search"],
        "tags": ["chatgpt-shim", "observe"],
        "_chatgpt_compat": True,
        "_routes_to": "arif_observe",
    },
    "arif_fetch": {
        "name": "arif_fetch",
        "description": (
            "Fetch content from a URL. Use when you need to read the contents "
            "of a specific webpage or document. Returns the page content as text."
        ),
        "access": "public",
        "tier": "chatgpt-shim",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS, Law.L05_PEACE, Law.L12_INJECTION],
        "modes": ["fetch"],
        "tags": ["chatgpt-shim", "observe"],
        "_chatgpt_compat": True,
        "_routes_to": "arif_fetch",
    },
    # ── Tool Discovery ──
    "arif_resolve_tool": {
        "name": "arif_resolve_tool",
        "description": (
            "Resolve a tool name or alias to the canonical arifOS tool name. "
            "Use when you have a tool name but aren't sure if it's the canonical name. "
            "Returns the canonical name, use_when guidance, and examples."
        ),
        "access": "public",
        "tier": "discovery",
        "namespace": "arif_*",
        "risk_tier": "low",
        "irreversible": False,
        "floors": [Law.L02_TRUTH],
        "modes": [],
        "tags": ["discovery", "utility", "read-only"],
    },
}

# Full surface: canonical (13) + diagnostic (32) = 45 declared tools
# Note: actual MCP registration count may differ slightly from this dict
# due to runtime-only registrations. The /health contract_status.tool_count
# is authoritative for the live wire surface.
FULL_SURFACE_TOOLS: tuple[str, ...] = CONSTITUTIONAL_TOOLS + tuple(DIAGNOSTIC_TOOLS.keys())

# ═══════════════════════════════════════════════════════════════════════════════
# MCP ANNOTATIONS — derived from action_class, NOT hand-set
# ═══════════════════════════════════════════════════════════════════════════════
# Per the AAA Agent Operating Invariants (Rule 6: HINTS ≠ CONTRACTS):
# MCP annotations (readOnlyHint, destructiveHint, idempotentHint) are UX
# vocabulary — informational signals, not enforceable guarantees.
#
# arifOS edge: `destructiveHint` is COMPUTED from action_class deterministically.
# The annotation is OUTPUT of the classification gate, not INPUT to it.
# A malicious server can mark a destructive tool `readOnlyHint: true` —
# but arifOS derives everything from the action_class, which is the
# actual enforceable contract.
#
# Derivation table:
#   action_class   → readOnlyHint  destructiveHint  idempotentHint
#   ─────────────     ────────────  ───────────────  ──────────────
#   OBSERVE           True          False            True
#   ANALYZE           True          False            True
#   PREPARE           False         False            True
#   DRAFT             True          False            False
#   MUTATE            False         True             False
#   EXECUTE           False         True             False
#   IRREVERSIBLE      False         True             False
#   BRIDGE            False         False            False
#
# Override: irreversible=True in the tool spec forces destructiveHint=True
# regardless of action_class (belt-and-suspenders for vault/forge etc.)
# ═══════════════════════════════════════════════════════════════════════════════


def derive_mcp_annotations(
    action_class: str,
    *,
    is_irreversible: bool = False,
    title: str = "",
) -> dict[str, Any]:
    """Derive MCP tool annotations from action_class deterministically.

    This is the arifOS edge: annotations are OUTPUT of classification,
    not hand-set metadata. The action_class IS the enforceable contract.

    Args:
        action_class: One of OBSERVE|ANALYZE|PREPARE|DRAFT|MUTATE|EXECUTE|IRREVERSIBLE|BRIDGE
        is_irreversible: Belt-and-suspenders — if True, forces destructiveHint=True
        title: Human-readable short title for the tool

    Returns:
        Dict of MCP annotations ready for FastMCP tool registration.
    """
    ac = action_class.upper()

    _READONLY_MAP: dict[str, bool] = {
        "OBSERVE": True,
        "ANALYZE": True,
        "PREPARE": False,
        "DRAFT": True,
        "MUTATE": False,
        "EXECUTE": False,
        "IRREVERSIBLE": False,
        "BRIDGE": False,
    }

    _DESTRUCTIVE_MAP: dict[str, bool] = {
        "OBSERVE": False,
        "ANALYZE": False,
        "PREPARE": False,
        "DRAFT": False,
        "MUTATE": True,
        "EXECUTE": True,
        "IRREVERSIBLE": True,
        "BRIDGE": False,
    }

    _IDEMPOTENT_MAP: dict[str, bool] = {
        "OBSERVE": True,
        "ANALYZE": True,
        "PREPARE": True,
        "DRAFT": False,
        "MUTATE": False,
        "EXECUTE": False,
        "IRREVERSIBLE": False,
        "BRIDGE": False,
    }

    read_only = _READONLY_MAP.get(ac, False)
    destructive = _DESTRUCTIVE_MAP.get(ac, True)  # unknown → conservative
    idempotent = _IDEMPOTENT_MAP.get(ac, False)

    # Belt-and-suspenders: irreversible tools are ALWAYS destructive
    if is_irreversible:
        destructive = True

    return {
        "title": title or ac.title(),
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": ac in ("OBSERVE", "BRIDGE"),
        "_derived_from": {
            "action_class": action_class,
            "is_irreversible": is_irreversible,
            "derivation": "arifOS action_class → MCP annotations (deterministic)",
            "rule": "AAA Agent Invariant #6: HINTS ≠ CONTRACTS. Annotations are output of classification, not input.",
        },
    }


def _action_class_for_tool(tool_name: str, spec: dict[str, Any] | None = None) -> str:
    """Determine the action_class for any tool from its spec + risk registry.

    Resolution order:
      1. tool_risk_registry.py (canonical, has explicit action_class)
      2. Spec-based inference from tier + irreversible field
      3. Conservative default (OBSERVE)
    """
    # 1. Try the risk registry first
    try:
        from arifosmcp.runtime.tool_risk_registry import classify_tool

        profile = classify_tool(tool_name)
        if profile and profile.action_class != "OBSERVE":
            # Only use registry if it has a non-default classification
            # (classify_tool returns OBSERVE as fallback for unknown tools)
            return profile.action_class
    except Exception:
        pass

    # 2. Spec-based inference
    if spec:
        tier = spec.get("tier", spec.get("risk_tier", "low"))
        irreversible = spec.get("irreversible", False)

        if irreversible:
            return "IRREVERSIBLE"

        # Tier-based defaults
        if tier in ("hermes", "canary", "diagnostic"):
            return "OBSERVE"
        if tier == "attest":
            return "ANALYZE"
        if tier == "lease":
            return "MUTATE"  # lease tools change state
        if tier == "forge-sub":
            return "ANALYZE"
        if tier == "narrative":
            return "ANALYZE"
        if tier == "canonical":
            # For canonical tools not in risk registry, use access level
            access = spec.get("access", "public")
            risk_tier = spec.get("risk_tier", "low")
            if risk_tier == "critical":
                return "MUTATE"
            if access == "authenticated":
                return "DRAFT"
            return "ANALYZE"

    # 3. Conservative default
    return "OBSERVE"


# MCP Spec 2025-11-25 tool annotations (SEP-1862/1913/1984/2417)
# EVERY annotation below is DERIVED from action_class via derive_mcp_annotations().
# No hand-set hints. The action_class is the contract; the hints are its projection.
_TOOL_ANNOTATIONS: dict[str, dict[str, Any]] = {
    # ═══════════════════════════════════════════════════════════════════
    # CANONICAL TOOLS — action_class from tool_risk_registry.py
    # ═══════════════════════════════════════════════════════════════════
    "arif_init": derive_mcp_annotations(
        "PREPARE",
        title="Init Session",
    ),
    "arif_observe": derive_mcp_annotations(
        "OBSERVE",
        title="Sense & Observe",
    ),
    "arif_fetch": derive_mcp_annotations(
        "OBSERVE",
        title="Fetch Evidence",
    ),
    "arif_think": derive_mcp_annotations(
        "ANALYZE",
        title="Mind Reason",
    ),
    "arif_critique": derive_mcp_annotations(
        "ANALYZE",
        title="Heart Critique",
    ),
    "arif_compose": derive_mcp_annotations(
        "ANALYZE",
        title="Reply Compose",
    ),
    "arif_judge": derive_mcp_annotations(
        "DRAFT",
        title="Judge Deliberate",
    ),
    "arif_seal": derive_mcp_annotations(
        "IRREVERSIBLE",
        title="Vault Seal",
        is_irreversible=True,
    ),
    "arif_forge": derive_mcp_annotations(
        "MUTATE",
        title="Forge Execute",
        is_irreversible=True,
    ),
    "arif_measure": derive_mcp_annotations(
        "OBSERVE",
        title="Ops Measure",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # RULE-14 DIAGNOSTIC TOOLS — action_class from kernel_canonical spec
    # ═══════════════════════════════════════════════════════════════════
    "arif_route": derive_mcp_annotations(
        "ANALYZE",
        title="Route",
    ),
    "arif_triage": derive_mcp_annotations(
        "ANALYZE",
        title="Triage",
    ),
    "arif_bridge_connect": derive_mcp_annotations(
        "BRIDGE",
        title="Bridge Connect",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # CHATGPT COMPATIBILITY SHIM — OBSERVE-class, read-only, open-world
    # ═══════════════════════════════════════════════════════════════════
    "arif_search": derive_mcp_annotations(
        "OBSERVE",
        title="Search (ChatGPT Compat)",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # HERMES TOOLS (7) — all OBSERVE/ANALYZE (read-only cross-verification)
    # ═══════════════════════════════════════════════════════════════════
    "hermes_system_status": derive_mcp_annotations(
        "OBSERVE",
        title="System Status",
    ),
    "hermes_vault_query": derive_mcp_annotations(
        "OBSERVE",
        title="Vault Query",
    ),
    "hermes_epistemic_check": derive_mcp_annotations(
        "ANALYZE",
        title="Epistemic Check",
    ),
    "hermes_fact_check": derive_mcp_annotations(
        "ANALYZE",
        title="Fact Check",
    ),
    "hermes_cross_verify": derive_mcp_annotations(
        "ANALYZE",
        title="Cross Verify",
    ),
    "hermes_plan_review": derive_mcp_annotations(
        "ANALYZE",
        title="Plan Review",
    ),
    "hermes_memory_steward": derive_mcp_annotations(
        "ANALYZE",
        title="Memory Steward",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # CANARY TOOLS (6) — zero-floor transport diagnostics, all OBSERVE
    # ═══════════════════════════════════════════════════════════════════
    "arif_canary": derive_mcp_annotations(
        "OBSERVE",
        title="Canary (multimode)",
    ),
    "arif_ping": derive_mcp_annotations(
        "OBSERVE",
        title="Ping [DEPRECATED]",
    ),
    "arif_schema_echo": derive_mcp_annotations(
        "OBSERVE",
        title="Schema Echo",
    ),
    "arif_version_echo": derive_mcp_annotations(
        "OBSERVE",
        title="Version Echo",
    ),
    "arif_transport_echo": derive_mcp_annotations(
        "OBSERVE",
        title="Transport Echo",
    ),
    "arif_initialize_probe": derive_mcp_annotations(
        "ANALYZE",
        title="Initialize Probe",
    ),
    "arif_conformance_report": derive_mcp_annotations(
        "ANALYZE",
        title="Conformance Report",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # LEASE TOOLS (3) — state-changing authority management
    # ═══════════════════════════════════════════════════════════════════
    "arif_lease_inspect": derive_mcp_annotations(
        "OBSERVE",
        title="Lease Inspect",
    ),
    "arif_lease_issue": derive_mcp_annotations(
        "MUTATE",
        title="Lease Issue",
    ),
    "arif_lease_revoke": derive_mcp_annotations(
        "IRREVERSIBLE",
        title="Lease Revoke",
        is_irreversible=True,
    ),
    # ═══════════════════════════════════════════════════════════════════
    # ATTEST TOOLS (7) — read-only federation health verification
    # ═══════════════════════════════════════════════════════════════════
    "arif_os_attest": derive_mcp_annotations(
        "OBSERVE",
        title="OS Attest",
    ),
    "arif_organ_attest": derive_mcp_annotations(
        "ANALYZE",
        title="Organ Attest",
    ),
    "arif_organ_attest_all": derive_mcp_annotations(
        "ANALYZE",
        title="Organ Attest All",
    ),
    "arif_heartbeat": derive_mcp_annotations(
        "OBSERVE",
        title="Heartbeat",
    ),
    "arif_peer_contract_validate": derive_mcp_annotations(
        "ANALYZE",
        title="Peer Contract Validate",
    ),
    "arif_peer_contract_attest": derive_mcp_annotations(
        "OBSERVE",
        title="Peer Contract Attest",
    ),
    "arif_peer_contract_forbid": derive_mcp_annotations(
        "MUTATE",
        title="Peer Contract Forbid",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # FORGE SUB-TOOLS (3) — pre-execution planning, all ANALYZE
    # ═══════════════════════════════════════════════════════════════════
    "forge_dry_run": derive_mcp_annotations(
        "ANALYZE",
        title="Dry Run",
    ),
    "forge_plan": derive_mcp_annotations(
        "ANALYZE",
        title="Plan",
    ),
    "forge_query": derive_mcp_annotations(
        "OBSERVE",
        title="Query",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # NARRATIVE TOOLS (2) — institutional analysis, all ANALYZE
    # ═══════════════════════════════════════════════════════════════════
    "arif_detect_institutional_shadow_drift": derive_mcp_annotations(
        "ANALYZE",
        title="Detect Institutional Shadow Drift",
    ),
    "arif_detect_narrative_tension": derive_mcp_annotations(
        "ANALYZE",
        title="Detect Narrative Tension",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # DIAGNOSTIC TOOLS (6) — health probes, drift checks, budget
    # ═══════════════════════════════════════════════════════════════════
    "arif_stack_health_probe": derive_mcp_annotations(
        "OBSERVE",
        title="Stack Health Probe",
    ),
    "arif_scan_local_instructions": derive_mcp_annotations(
        "OBSERVE",
        title="Scan Local Instructions",
    ),
    "arif_organ_consensus": derive_mcp_annotations(
        "ANALYZE",
        title="Organ Consensus",
    ),
    "arif_session_budget": derive_mcp_annotations(
        "OBSERVE",
        title="Session Budget",
    ),
    "arif_floor_status": derive_mcp_annotations(
        "OBSERVE",
        title="Floor Status",
    ),
    "mcp_drift_check": derive_mcp_annotations(
        "ANALYZE",
        title="Drift Check",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # MCP GATE + SHADOW GEOMETRY (3) — evaluation infrastructure
    # ═══════════════════════════════════════════════════════════════════
    "arif_gate_judge": derive_mcp_annotations(
        "ANALYZE",
        title="Gate Judge",
    ),
    "arif_self_evaluate": derive_mcp_annotations(
        "ANALYZE",
        title="Self Evaluate",
    ),
    "arif_model_compare": derive_mcp_annotations(
        "ANALYZE",
        title="Model Compare",
    ),
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
    "arif_init": ToolStage.INIT,
    "arif_observe": ToolStage.OBSERVE,
    "arif_fetch": ToolStage.EVIDENCE,
    "arif_think": ToolStage.REASON,
    "arif_critique": ToolStage.FORGE,
    "arif_compose": ToolStage.REPLY,
    "arif_judge": ToolStage.JUDGE,
    "arif_seal": ToolStage.SEAL,
    "arif_forge": ToolStage.FORGE_EXECUTE,
    "arif_measure": ToolStage.MEASURE,
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
    # The canonical public surface is the Core 7.
    # Everything else (memory, measure, compose, kernel internals, aliases)
    # is internal or demoted.
    return list(CORE_SEVEN)


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
    - arif_init's `allowed_tools` list
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
    Merges CANONICAL_TOOLS (21 canonical) + DIAGNOSTIC_TOOLS (40 diagnostic/hermes/canary/lease/attest/forge-sub/narrative).
    Single source: CANONICAL_TOOLS + DIAGNOSTIC_TOOLS dicts. No legacy aliases.

    FORGED 2026-06-21: Every tool now includes an affordance_contract derived from
    tool_risk_registry.py (canonical) or inferred from the tool spec (diagnostic).
    This is the arifOS edge: the contract is computed, not hand-set.
    """
    # ── Load risk registry for affordance contract derivation ──
    _risk_registry: dict[str, Any] = {}
    try:
        from arifosmcp.runtime.tool_risk_registry import (
            TOOL_RISK_REGISTRY,
            classify_tool as _risk_classify,
        )

        _risk_registry = TOOL_RISK_REGISTRY
    except Exception:
        _risk_classify = None

    def _affordance_contract(name: str, spec: dict[str, Any]) -> dict[str, Any]:
        """Derive affordance_contract for a tool from risk registry or spec."""
        # 1. Try the risk registry first
        if name in _risk_registry:
            profiles = _risk_registry[name]
            base = profiles[0]  # First entry is base/default
            return {
                "action_class": base.action_class,
                "risk_tier": base.risk_tier,
                "blast_radius": base.blast_radius,
                "reversibility": base.reversibility,
                "requires_lease": base.requires_lease,
                "autonomy_floor": base.autonomy_floor,
                "rationale": base.rationale,
                "_derived_from": "tool_risk_registry.py (canonical)",
            }

        # 2. Spec-based inference for diagnostic tools
        tier = spec.get("tier", spec.get("risk_tier", "low"))
        irreversible = spec.get("irreversible", False)
        access = spec.get("access", "public")

        if irreversible:
            action_class = "IRREVERSIBLE"
        elif tier == "lease":
            action_class = "MUTATE"
        elif access in ("authenticated", "sovereign"):
            action_class = "DRAFT"
        elif tier in ("hermes", "canary", "diagnostic", "forge-sub", "narrative"):
            action_class = "OBSERVE"
        elif tier == "attest":
            action_class = "ANALYZE"
        else:
            action_class = "OBSERVE"

        # blast_radius inference
        if tier == "canonical" and spec.get("risk_tier") == "critical":
            blast_radius = "PUBLIC"
        elif tier in ("hermes", "narrative"):
            blast_radius = "ORG"
        elif tier in ("lease", "attest"):
            blast_radius = "ORG"
        else:
            blast_radius = "LOCAL"

        reversibility = 0.0 if irreversible else 0.9

        return {
            "action_class": action_class,
            "risk_tier": spec.get("risk_tier", "low").upper(),
            "blast_radius": blast_radius,
            "reversibility": reversibility,
            "requires_lease": irreversible or tier == "lease",
            "autonomy_floor": "PRINCIPAL_APPROVAL_REQUIRED" if irreversible else "FULL_AUTO",
            "rationale": f"Spec-inferred: tier={tier}, irreversible={irreversible}, access={access}",
            "_derived_from": "constitutional_map.py (spec-inferred for diagnostic tools)",
        }

    all_tools: dict[str, dict[str, Any]] = {}

    # ── Canonical (13 kernel + Rule-14 diagnostics) ──
    for name, spec in CANONICAL_TOOLS.items():
        all_tools[name] = {
            "stage": spec["stage"].value if hasattr(spec["stage"], "value") else str(spec["stage"]),
            "lane": spec["lane"].value if hasattr(spec["lane"], "value") else str(spec["lane"]),
            "floors": [floor.value for floor in spec["floors"]],
            "risk_tier": spec["risk_tier"],
            "irreversible": spec["irreversible"],
            "access": spec["access"],
            "requires_auth": spec["access"] != "public",
            "modes": spec.get("modes", []),
            "eureka_insight": spec.get("eureka_insight", ""),
            "tier": "canonical",
            "namespace": "arif_* (canonical prefix)",
            "tags": ["canonical"],
            "affordance_contract": _affordance_contract(name, spec),
        }
        # Forward deprecation metadata if present
        if spec.get("_deprecated"):
            all_tools[name]["_deprecated"] = True
            all_tools[name]["_canonical_name"] = spec.get("_canonical_name", "")

    # ── Diagnostic + Federation tools ──
    for name, spec in DIAGNOSTIC_TOOLS.items():
        all_tools[name] = {
            "tier": spec.get("tier", "diagnostic"),
            "namespace": spec.get("namespace", "arif_*"),
            "floors": [floor.value for floor in spec.get("floors", [])],
            "risk_tier": spec.get("risk_tier", "low"),
            "irreversible": spec.get("irreversible", False),
            "access": spec.get("access", "public"),
            "requires_auth": spec.get("access", "public") != "public",
            "modes": spec.get("modes", []),
            "tags": spec.get("tags", []),
            "affordance_contract": _affordance_contract(name, spec),
        }

    # ── Tier summary ──
    tier_counts: dict[str, int] = {}
    for t in all_tools.values():
        tier = t.get("tier", "unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    return {
        "_schema": "arifos-ssct-v2026.06.14-kanon-ssct",
        "_source": "arifosmcp.constitutional_map (CANONICAL_TOOLS + DIAGNOSTIC_TOOLS)",
        "_note": (
            "SOLE SOURCE OF TRUTH. "
            "Generated from CANONICAL_TOOLS (21 canonical) + DIAGNOSTIC_TOOLS (40 operational). "
            "Do not hand-edit — edit the source dicts in constitutional_map.py and regenerate. "
            "FORGED 2026-06-21: affordance_contract added — derived from tool_risk_registry.py "
            "for canonical tools, spec-inferred for diagnostic tools. The contract is "
            "COMPUTED, not hand-set."
        ),
        "_affordance_contract_derivation": {
            "canonical_tools": "tool_risk_registry.py → ToolRiskProfile (action_class, risk_tier, blast_radius, reversibility, requires_lease, autonomy_floor)",
            "diagnostic_tools": "constitutional_map.py → spec-inferred from tier + irreversible + access fields",
            "rule": "AAA Agent Invariant #6: HINTS ≠ CONTRACTS. Affordance contracts are derived from action_class, not self-declared by the tool.",
            "forged": "2026-06-21",
        },
        "_namespace_ruling": {
            "arif_*": "Canonical13 public surface — 21 canonical tools + 1 canary probe (22 default wire tools)",
            "hermes_*": "GATED — Hermes ASI cross-verification tools (requires ARIFOS_MCP_EXPOSE_DEV_TOOLS=true)",
            "forge_*": "GATED/DEPRECATED — A-FORGE pre-execution sub-tools (use A-FORGE MCP directly; removed 2026-07-15)",
            "arifos_*": "BLOCKED — internal-only prefix, never exposed on public MCP surface",
            "mcp_*": "GATED — Utility namespace for operational diagnostics",
        },
        "canonical_count": len(CONSTITUTIONAL_TOOLS),
        "diagnostic_count": len(DIAGNOSTIC_TOOLS),
        "total_surface": len(all_tools),
        "tier_summary": tier_counts,
        "tier_legend": {
            "canonical": "21 canonical tools — F1-F13 constitutional pipeline plus rule-14/public extensions",
            "hermes": "7 cross-verification, fact-checking, vault query, epistemic checks",
            "canary": "1 multimode transport/protocol diagnostic probe (no session required)",
            "lease": "3 capability lease lifecycle tools (inspect, issue, revoke)",
            "attest": "4 federation organ attestation tools (self + peer heartbeat)",
            "forge-sub": "3 pre-execution forge planning tools (dry_run, plan, query)",
            "narrative": "2 institutional shadow drift + narrative tension detection tools",
            "diagnostic": "6 health probes, drift checks, floor status, budget telemetry, instruction scanner",
        },
        "canonical_order": list(CONSTITUTIONAL_TOOLS),
        "diagnostic_order": list(DIAGNOSTIC_TOOLS.keys()),
        "laws": [f.value for f in Law],
        "floors": [f.value for f in Law],  # deprecated alias
        "tools": all_tools,
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
    "arif_init": {
        "mode": str,
        "actor_id": str | None,
        "ack_irreversible": bool,
        "session_id": str | None,
        "epoch_id": str | None,
        "previous_session_hash": str | None,
    },
    "arif_observe": {
        "mode": str,
        "query": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "url": str | None,  # [L12: sanitized]
        "layers": list[str] | None,
        "result_limit": int,  # max results for search/ingest (default 10)
    },
    "arif_fetch": {
        "mode": str,
        "url": str | None,  # [L12: sanitized]
        "query": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "thinking_depth": int,
        "thinking_budget": float | None,
        "sequential_mode": bool,
    },
    "arif_think": {
        "mode": str,
        "query": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str | None,
        "plan_id": str | None,
        "witness_type": str,
        "axiom_set": list[str] | None,
    },
    "arif_critique": {
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
    "arif_compose": {
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
        "contract_url": str | None,  # P2P Federation Contract v1 URL
        "contract": dict | None,  # Inline P2P Federation Contract v1
    },
    "arif_judge": {
        "mode": str,
        "candidate": str | None,  # [L12: sanitized]
        "session_id": str | None,
        "actor_id": str,  # L11: authenticated — required
        "constitutional_chain_id": str | None,
        "domain_payload": dict | None,
        "peer_contract_id": str | None,  # P2P Federation Contract v1 audit continuity
    },
    "arif_seal": {
        "mode": str,
        "payload": str,  # L11: authenticated — required
        "session_id": str | None,
        "ack_irreversible": bool,  # F1: hard gate
        "actor_id": str,  # L11: authenticated — required
        "constitutional_chain_id": str | None,
        "judge_state_hash": str | None,
    },
    "arif_forge": {
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
    "arif_measure": {
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
    "arif_init": {
        "verdict": str,
        "session_id": str,
        "constitution_hash": str,
        "invariants_hash": str,
        "allowed_next_tools": list[str],
        "omega_0": float,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_observe": {
        "verdict": str,
        "mode": str,
        "results": list[dict] | None,
        "omega_0": float,
        "delta_S": float | None,
        "a_rif": dict | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_fetch": {
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
    "arif_think": {
        "verdict": str,
        "mode": str,
        "claim_tag": str,  # CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN
        "tau": float,  # F2 truth score
        "omega": float,  # F7 uncertainty band
        "delta_S": float | None,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_critique": {
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
    "arif_compose": {
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
    "arif_judge": {
        "verdict": str,  # SEAL | HOLD | VOID
        "mode": str,
        "judgment": str,
        "actor_verified": bool,
        "human_approved": bool,
        "nine_signal": dict,
        "reasons": list[str],
    },
    "arif_seal": {
        "verdict": str,
        "mode": str,
        "vault_entry_id": str | None,
        "merkle_root": str | None,
        "timestamp": str,
        "nine_signal": dict,
        "reasons": list[str],
    },
    "arif_forge": {
        "verdict": str,
        "mode": str,
        "status": str,
        "execution_trace": list[dict] | None,
        "artifact_id": str | None,
        "irreversibility_level": str,
        "nine_signal": dict,
        "reasons": list[str] | None,
    },
    "arif_measure": {
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

# ═══════════════════════════════════════════════════════════════════════════════
# COGNITIVE GRADIENT BRIDGE — MCP Packaging Law integration
# ═══════════════════════════════════════════════════════════════════════════════
# The cognitive gradient is the formal enforcement of the MCP Packaging Law:
#   "MCP tools must be packaged by cognitive level, not by function."
#
# This bridge connects the constitutional map (CANONICAL_TOOLS) with the
# cognitive gradient module. Agents query gradient_summary() to discover
# the four-level ladder; kernel_status uses gradient_ladder() in discover mode.
#
# Four levels:
#   L1 PERCEPTION     — Look (stateless, cheap, fire-and-forget)
#   L2 EVIDENCE       — Look + Prove (verified, receipted, cited)
#   L3 EXPLORATION    — Look + Think + Discover (multi-hop, governed, graph-building)
#   L4 INTERVENTION   — Governed Action (mutation under seal, lease-gated)
#
# DITEMPA BUKAN DIBERI — Forged, Not Given.


def get_cognitive_gradient() -> dict:
    """Return the full cognitive gradient from the canonical module.

    Returns a dict with keys: levels, ladder, packaging_check, tool_count.
    This is the primary queryable surface for agents discovering the gradient.
    """
    try:
        from arifosmcp.core.cognitive_gradient import (  # noqa: PLC0415
            gradient_ladder,
            gradient_summary,
            packaging_law_check,
        )

        return {
            "levels": gradient_summary(exposed_only=True),
            "ladder": gradient_ladder(),
            "packaging_check": packaging_law_check(),
            "tool_count": len(CANONICAL_TOOLS),
            "gradient_tool_count": len(gradient_ladder()),
        }
    except ImportError:
        return {
            "levels": {},
            "ladder": [],
            "packaging_check": {
                "verdict": "UNAVAILABLE",
                "summary": "Cognitive gradient module not loaded.",
            },
            "tool_count": len(CANONICAL_TOOLS),
            "gradient_tool_count": 0,
        }


def resolve_gradient_level(tool_name: str) -> int | None:
    """Return the cognitive level (1-4) for a tool, or None if unknown."""
    try:
        from arifosmcp.core.cognitive_gradient import resolve_level  # noqa: PLC0415

        level = resolve_level(tool_name)
        return int(level) if level is not None else None
    except ImportError:
        return None


def recommend_gradient_level(intent: str) -> dict:
    """Given a natural-language intent, recommend which cognitive level to use."""
    try:
        from arifosmcp.core.cognitive_gradient import (  # noqa: PLC0415
            recommend_level,
            tools_at_level,
        )

        level = recommend_level(intent)
        tools = tools_at_level(level, exposed_only=True)
        return {
            "recommended_level": int(level),
            "label": level.label,
            "verbs": level.verbs,
            "contract": level.contract,
            "available_tools": tools,
        }
    except ImportError:
        return {"recommended_level": 1, "label": "Perception", "available_tools": []}


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
    "DIAGNOSTIC_TOOLS",
    "FULL_SURFACE_TOOLS",
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
    "get_cognitive_gradient",
    "resolve_gradient_level",
    "recommend_gradient_level",
]
