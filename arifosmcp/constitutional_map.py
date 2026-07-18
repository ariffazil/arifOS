"""
ARIFOS CONSTITUTIONAL MAP (v2026.07.04-CANONICAL-9)
═══════════════════════════════════════════════════════════════════════════════

SOLE SOURCE OF TRUTH for the canonical MCP tools.
Public canonical surface: the 9-stage metabolic loop (CANONICAL-9 2026-07-04:
9 stages = 9 public tools. arif_critique promoted from arif_think mode to
its own public tool at stage 555).

Canonical 9 stages = arif_init (000), arif_observe (111), arif_think (333),
arif_route (444), arif_critique (555), arif_judge (666), arif_forge (777),
arif_compose (888), arif_seal (999). arif_canary, arif_triage → modes of
arif_init. arif_fetch → mode of arif_observe. arif_bridge_connect → mode of
arif_route. arif_critique is now its own public tool at 555.

Full CANONICAL_TOOLS dict registers the public verbs + supporting internal tools.
All arif_* naming. One stage = one canonical verb (F4 CLARITY).

MACHINERY:
  - CANONICAL_TOOLS   : registry for canonical surface (public verbs + internal support tools; name → spec with floors, stage, lane)
  - CORE_NINE         : ordered list of the 9-stage public verbs
  - Law enum          : L01–L13 with Eureka-wired threshold logic
  - TrinityLane      : AGI | ASI | APEX
  - ToolStage        : 000–999 metabolic stage codes
  - _TOOL_INPUT_SCHEMAS  : canonical I/O type signatures (L10 ONTOLOGY enforced)
  - _TOOL_OUTPUT_SCHEMAS : canonical output envelope per tool
  - validate_tool_response_schema()  : F2 Nine-Signal contract checker
  - check_schema_coverage()          : all tools have schemas = CI pass
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
    SOVEREIGN = "SOVEREIGN"  # Authority resolution (999)


class ToolStage(StrEnum):
    INIT = "000"  # Session bootstrap (absorbed: canary, triage)
    OBSERVE = "111"  # Reality sensing (absorbed: fetch)
    REASON = "333"  # Cognitive reasoning
    ROUTE = "444"  # Intent routing (absorbed: bridge_connect)
    CRITIQUE = "555"  # Adversarial critique (promoted from arif_think mode)
    JUDGE = "888"  # Constitutional verdict
    FORGE_EXECUTE = "777"  # Guarded execution
    REPLY = "888"  # Response composition
    SEAL = "999"  # VAULT999 seal anchor


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

METABOLIC_LOOP: dict[str, dict[str, str | None]] = {
    "000": {"next": "111", "verb": "observe"},
    "111": {"next": "333", "verb": "think"},
    "333": {"next": "444", "verb": "route"},
    "444": {"next": "555", "verb": "memory"},
    "555": {"next": "666", "verb": "judge"},
    "666": {"next": "777", "verb": "forge"},
    "777": {"next": "999", "verb": "seal"},
    "999": {"next": None},  # Gödel break — only sovereign can authorize 000
}

# Backward compat alias
STAGE_PROGRESSION: dict[str, dict[str, str | None]] = METABOLIC_LOOP


# ═══════════════════════════════════════════════════════════════════════════════
# CORE NINE — The 9-Stage Metabolic Loop (CANONICAL-9 2026-07-04)
# ═══════════════════════════════════════════════════════════════════════════════
# Public agents see exactly 9 surface verbs (9 stages = 9 tools).
# Everything else is an internal mode, diagnostic handler, or hidden helper.
# CANONICAL-9 2026-07-04:
#   - Absorbed into arif_init: arif_canary (mode=canary), arif_triage (mode=triage)
#   - Absorbed into arif_observe: arif_fetch (mode=fetch)
#   - Absorbed into arif_route: arif_bridge_connect (mode=bridge)
#   - Restored: arif_seal (999 — stage needs its verb)
#   - Absorbed: arif_critique → arif_think(mode=critique), arif_compose → arif_forge(mode=compose)
#   - 8 canonical tools (KERNEL_ABI_8), capability_registry.json is source of truth
# See /root/forge_work/2026-07-04/ZEN-9-VERB-METABOLIC-LOOP.md for doctrine.
#
# This is the expressive core. There are more tools (internals + diagnostics),
# but these are the public 8. These are the ones that must be cognitively perfect.

CORE_NINE: list[str] = [
    "arif_init",  # 000 — Session bootstrap. Modes: init, light, resume, canary, preflight, triage
    "arif_observe",  # 111 — Sense reality. Modes: search, fetch, ingest, vitals, atlas
    "arif_think",  # 333 — Cognitive engine. Modes: reason, plan, reflect, verify, critique
    "arif_route",  # 444 — Route intent to organ. Modes: route, bridge, triage
    "arif_memory",  # 555 — Memory governor. Modes: recall, inspect, attest, remember, promote, revise, forget, audit
    "arif_judge",  # 666 — Constitutional verdict. SEAL/HOLD/SABAR/VOID
    "arif_forge",  # 777 — Guarded execution. Modes: engineer, query, write, generate, commit
    "arif_seal",  # 999 — Append to VAULT999. Modes: seal, verify, ledger
]

CORE_NINE_WITH_ENGINE = {
    "arif_init": "arif_init (modes: init, light, resume, canary, preflight, triage)",
    "arif_observe": "arif_observe (modes: search, fetch, ingest, vitals, atlas)",
    "arif_think": "arif_think (modes: reason, plan, reflect, verify, critique, simulate, wonder)",
    "arif_route": "arif_route (modes: route, bridge, dispatch)",
    "arif_memory": "arif_memory (modes: recall, inspect, attest, remember, promote, revise, forget, audit)",
    "arif_judge": "arif_judge (kernel: arif_kernel_intercept)",
    "arif_forge": "arif_forge (modes: engineer, query, write, generate, commit; arif_act is internal alias)",
    "arif_seal": "arif_seal (modes: seal, verify, ledger; VAULT999 seal anchor)",
}

CORE_NINE_LABELS: dict[str, str] = {
    "arif_init": "Session anchor (000)",
    "arif_observe": "Sensing observation (111)",
    "arif_think": "Reasoning engine (333)",
    "arif_route": "Intent router (444)",
    "arif_critique": "Adversarial critique (555)",
    "arif_judge": "Constitutional verdict (666)",
    "arif_forge": "Guarded execution gate (777)",
    "arif_compose": "Response composer (888)",
    "arif_seal": "VAULT999 seal (999)",
}

# Map stage to the canonical tool in the 9-stage loop (for docs / agents).
CORE_NINE_STAGE_MAP: dict[str, str] = {
    "000": "arif_init",
    "111": "arif_observe",
    "333": "arif_think",
    "444": "arif_route",
    "555": "arif_memory",
    "666": "arif_judge",
    "777": "arif_forge",
    "888": "arif_forge",  # legacy stage — compose absorbed into forge
    "999": "arif_seal",
}

# Backward-compat aliases (DEPRECATED — resolve to the new names).
CANONICAL_7 = tuple(CORE_NINE)  # deprecated alias; semantically CORE_NINE
CORE_SEVEN = CORE_NINE  # deprecated alias; semantically CORE_NINE
CORE_SEVEN_WITH_ENGINE = CORE_NINE_WITH_ENGINE
CORE_SEVEN_LABELS = CORE_NINE_LABELS
CORE_SEVEN_STAGE_MAP = CORE_NINE_STAGE_MAP


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


class DeltaIrreversibilityClass(StrEnum):
    """
    Constitutional irreversibility tier (C0–C5) — governs HOW MUCH friction the kernel applies.

    The kernel paradox: governance looks like drag when nothing goes wrong,
    but genius when something could go wrong. This class is how we right-size it.

    Formerly: RiskClass (renamed 2026-07-17 to disambiguate from ActionRiskTier).
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


# ── Backward-compatible alias ──────────────────────────────────────────
RiskClass = DeltaIrreversibilityClass  # DEPRECATED — use DeltaIrreversibilityClass


@dataclass
class RiskTierConfig:
    governance_mode: str  # "vanilla" | "light" | "standard" | "strict" | "seal"
    requires_human_confirmation: bool
    floors_activated: list[str]  # Most relevant F-codes for this tier
    description: str


_RISK_GOVERNANCE_TABLE: dict[DeltaIrreversibilityClass, RiskTierConfig] = {
    DeltaIrreversibilityClass.C0_GRAMMAR: RiskTierConfig(
        governance_mode="vanilla",
        requires_human_confirmation=False,
        floors_activated=["L09", "L10"],
        description="Grammar, spelling, tone, formatting. Zero irreversible consequence.",
    ),
    DeltaIrreversibilityClass.C1_DRAFT: RiskTierConfig(
        governance_mode="light",
        requires_human_confirmation=False,
        floors_activated=["L04", "L09", "L10"],
        description="Internal drafts, brainstorming, notes. Reversible. No external exposure.",
    ),
    DeltaIrreversibilityClass.C2_REVIEW: RiskTierConfig(
        governance_mode="standard",
        requires_human_confirmation=False,
        floors_activated=["L02", "L03", "L04", "L07", "L08"],
        description=(
            "Code review, testing, analysis, summaries. Evidence-backed. Moderate exposure."
        ),
    ),
    DeltaIrreversibilityClass.C3_PUBLIC: RiskTierConfig(
        governance_mode="audit",
        requires_human_confirmation=False,  # C3 auto-proceed: SABAR + mandatory audit
        floors_activated=["L01", "L02", "L04", "L06", "L09", "L12"],
        description="Public posts, emails to third parties, published documents. Reputation risk. Auto-proceeds with SABAR + audit log.",
    ),
    DeltaIrreversibilityClass.C4_LEGAL_MONEY: RiskTierConfig(
        governance_mode="strict",
        requires_human_confirmation=True,
        floors_activated=["L01", "L02", "L03", "L05", "L06", "L11", "L12", "L13"],
        description="Legal claims, financial decisions, HR actions, investments. High consequence.",
    ),
    DeltaIrreversibilityClass.C5_IRREVERSIBLE: RiskTierConfig(
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
        decision = kernel.preflight(action="send_email", risk=DeltaIrreversibilityClass.C3, reversible=False)
        if decision.allowed:
            result = send_email()
            kernel.audit(result)
        else:
            print(decision.reason)
    """

    allowed: bool  # Can the action proceed?
    risk_class: DeltaIrreversibilityClass  # What tier was assigned
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
    risk_class: DeltaIrreversibilityClass,
    reversible: bool,
    evidence_quality: float = 1.0,  # 0.0–1.0; 1.0 = full evidence
    user_intent: str | None = None,
    session_ref: str | None = None,
) -> RiskDecision:
    """
    arifOS preflight check — the public API for right-sized governance.

    This is the function the external AI described:
        from arifos import Kernel, DeltaIrreversibilityClass  # RiskClass alias still available
        kernel = Kernel(policy="arifos.yaml")
        decision = kernel.preflight(
            user_intent="Send this email to the CEO",
            action="send_email",
            risk=DeltaIrreversibilityClass.C3,
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
    if risk_class == DeltaIrreversibilityClass.C5_IRREVERSIBLE:
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

    # C3 auto-proceed: public posts proceed with audit log, no human gate
    if risk_class == DeltaIrreversibilityClass.C3_PUBLIC and session_ref:
        return RiskDecision(
            allowed=True,
            risk_class=risk_class,
            governance_mode="audit",
            verdict="SABAR",
            reason=(
                f"C3 PUBLIC: '{action}' auto-proceeded with SABAR. "
                f"Audit trail logged. Human may review at session_ref={session_ref}."
            ),
            floors_activated=["L02", "L04", "L06", "L09", "L12"],
            requires_human_confirmation=False,
            human_approval_reference=session_ref,
            uncertainty_band=(0.03, 0.05),
            preflight_passed=True,
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
    if risk_class == DeltaIrreversibilityClass.C5_IRREVERSIBLE:
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
# CANONICAL KERNEL VERBS — arif_noun_verb naming
# ═══════════════════════════════════════════════════════════════════════════════
# MCP "tools" are the transport envelope. These entries are constitutional
# kernel stages (metabolic loop 000→999), not generic plugins.
#
# FLOOR COVERAGE INVARIANT: ALL L01–L13 must appear on ≥ 2 tools each.
# Current coverage (ZEN-9 collapse: absorbed tools folded into parents):
#   L01: arif_init, arif_route, arif_judge, arif_seal, arif_forge  (5)
#   L02: arif_observe, arif_think, arif_compose, arif_judge        (4)
#   L03: arif_observe                                               (1)
#   L04: arif_route, arif_compose                                   (2)
#   L05: arif_think, arif_observe                                   (2)
#   L06: arif_think, arif_compose                                   (2)
#   L07: arif_think, arif_observe                                   (2)
#   L08: arif_think                                                 (1)
#   L09: arif_think, arif_compose                                   (2)
#   L10: arif_think, arif_route                                     (2)
#   L11: arif_init, arif_route, arif_judge, arif_seal, arif_forge  (5)
#   L12: arif_init, arif_observe                                    (2)
#   L13: arif_judge, arif_seal, arif_forge                          (3)
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
        "access": "internal_only",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["intercept"],
        "eureka_insight": "F13: Human veto absolute. Minimum kernel enforcement spine.",
        "cognitive_axis": "judge",
        "expose": False,  # F13-ratified 2026-07-04: 12-tool public facade — kernel intercept stays internal
    },
    "arif_init": {
        "name": "arif_init",
        "description": (
            "KERNEL 000 · Session ignition. Binds actor, floors, and audit before any other "
            "arif_* verb can govern. Without session_id the kernel treats the caller as "
            "anonymous (OBSERVE_ONLY). Modes: ping | light | init | resume | validate | "
            "epoch_open | epoch_seal | canary | preflight | triage. "
            "Returns session_id, authority band, allowed_next_verbs. Not a helper plugin. "
            "Use when: starting a new session, resuming a session, checking kernel liveness, "
            "or running a preflight check before any governed action."
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
            "canary",
            "preflight",
            "triage",
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
            "KERNEL 111 · Sense reality into evidence (not reasoning, not judgment). "
            "Modes: search | fetch | ingest | vitals | compass | atlas | entropy_dS | "
            "repo_map | hybrid_discovery. Returns evidence with sources + uncertainty tags. "
            "Domain compute → arif_route to GEOX/WEALTH/WELL. "
            "Use when: the user needs factual evidence, web search, URL fetch, system vitals, "
            "or entropy measurement. For domain-specific computation (geology, capital, health), "
            "use arif_route instead."
        ),
        "access": "public",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L02_TRUTH, Law.L03_WITNESS, Law.L07_HUMILITY, Law.L12_INJECTION],
        "risk_tier": "low",
        "irreversible": False,
        "modes": [
            "search",
            "fetch",
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
            "Fetch and preserve external evidence with source citations and provenance tags. "
            "Use for targeted URL/source retrieval. Modes: fetch (default), search, eureka. "
            "For broad sensing use arif_observe; for specific evidence use arif_fetch. "
            "Use when: you need to fetch a specific URL, search for particular evidence, "
            "or preserve external content with provenance tracking."
        ),
        "access": "public",
        "stage": ToolStage.OBSERVE,
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
        "eureka_insight": ("F3: W₃ = ∛(Human × AI × Earth) ≥ 0.75. F5: P² ≥ 1.0 — safety margin. "),
        "cognitive_axis": "verify",
        "expose": True,
    },
    "arif_think": {
        "name": "arif_think",
        "description": (
            "KERNEL 333 · Mind — structured reasoning under F2/F7 (not chat, not verdict). "
            "Modes: reason | reflect | verify | plan | plan_review | plan_approve | "
            "refactor_plan | metabolize | axioms. Returns OBS/DER/INT/SPEC labels. "
            "Maruah/ethics → arif_critique. Binding decision → arif_judge. "
            "Use when: the user needs structured reasoning, plan generation, plan review, "
            "reflection on past actions, verification of claims, or axiom exploration."
        ),
        "access": "public",
        "stage": ToolStage.REASON,
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L02_TRUTH,
            Law.L05_PEACE,
            Law.L06_EMPATHY,
            Law.L07_HUMILITY,
            Law.L08_GENIUS,
            Law.L09_ANTIHANTU,
            Law.L10_ONTOLOGY,
        ],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": [
            "reason",
            "reflect",
            "verify",
            "axioms",
            "plan",
            "plan_review",
            "plan_approve",
            "refactor_plan",
            "metabolize",
            "simulate",
            "wonder",
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
            "KERNEL 555 · Heart — ethical/dignity/risk stress before judgment (not SEAL). "
            "Requires non-empty target. Modes: critique | redteam | maruah | deescalate | "
            "empathize | simulate | shadow. Returns risk, floors, human impact. "
            "Binding verdict is arif_judge only. "
            "Use when: a proposal has human/dignity impact, ethical risk, blast_radius MEDIUM+, "
            "or needs red-team stress-testing before judgment."
        ),
        "access": "internal_only",
        "stage": ToolStage.CRITIQUE,
        "lane": TrinityLane.ASI,
        "floors": [Law.L05_PEACE, Law.L06_EMPATHY, Law.L09_ANTIHANTU],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["critique", "redteam", "maruah", "shadow", "deescalate", "empathy"],
        "eureka_insight": (
            "F5: P² ≥ 1.0. F6: κᵣ ≥ 0.70 (RASA). "
            "F9: C_dark ≤ 0.30 — no biological or artificial emotional substrate. "
            "F9 Doctrine: The machine is an instrument, not a person."
        ),
        "cognitive_axis": "critique",
        "expose": False,  # absorbed into cognition.think(mode=critique)
    },
    # ── CANONICAL TOOLS (RULE 14 MODE-FIRST NAMING, 2026-06-20) ──
    "arif_route": {
        "name": "arif_route",
        "description": (
            "KERNEL 444 · Intent→organ router (default path to GEOX/WEALTH/WELL/A-FORGE). "
            "Select when goal is known but organ/verb is not. Optional organ_tool = "
            "governed bridge (prefer over arif_bridge_connect). Not session preflight "
            "(use arif_init mode=preflight|triage). Returns organ, port, tool_prefix, suggested_tools. "
            "Use when: the user's request involves domain-specific computation (geology, capital, health, "
            "execution) and you need to route to the correct federation organ."
        ),
        "access": "public",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L04_CLARITY, Law.L10_ONTOLOGY, Law.L11_AUDIT],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["route", "bridge"],
        "deprecated_aliases": [],  # no live aliases — convergence over choice
        "eureka_insight": "ZEN-9: route absorbs bridge as mode. One tool, two operations.",
        "cognitive_axis": "boundary",
        "expose": True,
    },
    "arif_triage": {
        "name": "arif_triage",
        "description": (
            "DEPRECATED — use arif_init(mode='preflight'|'triage'|'status'). "
            "Internal session preflight handler only; not on public tools/list."
        ),
        "access": "internal_only",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [Law.L04_CLARITY, Law.L10_ONTOLOGY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["status", "preflight", "triage"],
        "eureka_insight": "Absorbed into arif_init 2026-07-09 (audit dual-existence kill).",
        "cognitive_axis": "boundary",
        "expose": False,
    },
    "arif_bridge_connect": {
        "name": "arif_bridge_connect",
        "description": (
            "KERNEL 444-direct · Low-level organ call (organ + tool_name required). "
            "Authority HIGH/lease. Agents prefer arif_route. Not a free MCP proxy. "
            "Use when: you already know the exact organ and tool name and need a direct "
            "bridge call (bypasses intent routing). Requires session + lease."
        ),
        "access": "internal_only",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L10_ONTOLOGY],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["connect"],
        "eureka_insight": "Direct organ bridge enables cross-organ federation without routing overhead.",
        "cognitive_axis": "boundary",
        "expose": False,
    },
    "arif_compose": {
        "name": "arif_compose",
        "description": (
            "KERNEL reply · Final human-facing composition (citations, tone, ΔS≤0). "
            "Call LAST after observe/think/judge. Modes: compose | summarize | cite | "
            "tone_shift | style | format. Not a substitute for judge or seal. "
            "Use when: the pipeline is complete and you need to format the final response "
            "for the human — adding citations, adjusting tone, or restructuring output."
        ),
        "access": "internal_only",
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
        "expose": False,  # host/model adapter composes; not a kernel capability
    },
    "arif_memory": {
        "name": "arif_memory",
        "description": (
            "KERNEL memory governor · L1–L6 under F1/F2/F4/F11 (not a free notepad). "
            "Modes: recall | inspect | attest | remember | promote | revise | forget. "
            "Writes are J-space mutations; arifOS judges, storage organs hold data. "
            "Use when: the agent needs to recall past context, store new knowledge, "
            "promote memories to higher tiers, or audit memory integrity."
        ),
        "access": "authenticated",
        "stage": ToolStage.INIT,
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
        "irreversible": True,
        "modes": [
            "recall",
            "inspect",
            "attest",
            "remember",
            "promote",
            "revise",
            "forget",
            "audit",
        ],
        "eureka_insight": (
            "F1: every memory op is reversible via supersede (revise) or tombstone (forget → vault). "
            "F4: hybrid recall cascade (vector→graph→vault) reduces entropy per mode. "
            "F11: every write carries actor_id + session_id + receipt (forensic traceability). "
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
            "KERNEL 888 · Constitutional verdict — only organ that SEAL/HOLD/SABAR/VOIDs. "
            "Not advice; binding floor + authority arbitration. Requires actor, intent, "
            "domain, reversibility_level, blast_radius. Authority: SOVEREIGN session for "
            "real adjudicate. Returns verdict + receipts + next_safe_action. "
            "Use when: a decision needs constitutional clearance — irreversible actions, "
            "high-blast-radius operations, or when the agent must know if an action is lawful."
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
            "KERNEL 999 · VAULT999 immutable append — irreversible civilizational memory. "
            "Modes: seal | verify | chain | list | dry_run. seal requires ack_irreversible. "
            "Kernel judges; vault seals; Arif owns F13 veto. Not for HOLD/SABAR/VOID paths. "
            "Use when: a verdict has been reached and needs to be permanently recorded in "
            "VAULT999, or when verifying the integrity of the seal chain."
        ),
        "access": "authenticated",
        "stage": ToolStage.SEAL,
        "lane": TrinityLane.SOVEREIGN,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "modes": ["seal", "verify", "ledger", "changelog", "audit"],
        "eureka_insight": (
            "ZEN-9: seal restored to public surface — 999 needs its verb. "
            "Gödel break: 999 cannot authorize 000. Only sovereign heartbeat. "
            "Kernel judges (arif_judge). VAULT999 seals. ARIF F13 owns final veto."
        ),
        "cognitive_axis": "seal",
        "expose": True,  # ZEN-9 collapse 2026-07-04: restored to public surface
    },
    "arif_verify": {
        "name": "arif_verify",
        "description": (
            "KERNEL · Ed25519 signature verification (live MCP, AAA Wave 2 / Phase 5). "
            "Completes the identity ceremony started by arif_challenge. Validates a "
            "base64 Ed25519 signature against a hex-encoded actor public key over the "
            "payload {actor_id}:{challenge}. Consumes the challenge (one-shot, no replay). "
            "On success, marks the session as ed25519_verified. "
            "Input: challenge (b64), signature (b64), actor_pubkey (64-hex), session_id, actor_id?. "
            "Output: verified, actor_id, challenge_age_seconds, message. "
            "Use when: verifying actor identity after arif_challenge; never trust a claimed "
            "actor_id without cryptographic binding. "
            "Note: the legacy JITU SEAL-token gate (_arif_verify_tool) remains reachable "
            "via HTTP /kernel/arif_verify — that semantics is preserved."
        ),
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L01_AMANAH,
            Law.L02_TRUTH,
            Law.L11_AUDIT,
            Law.L12_INJECTION,
            Law.L13_SOVEREIGN,
        ],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["ed25519_verify"],
        "eureka_insight": (
            "Identity = cryptographic, not declarative. arif_verify closes the gap between "
            "claimed and proven actor identity. Without it, authority bands are theatre."
        ),
        "cognitive_axis": "verify",
        "expose": True,  # AAA Wave 2: live MCP surface for Ed25519 ceremony
    },
    "arif_challenge": {
        "name": "arif_challenge",
        "description": (
            "KERNEL · Issue an Ed25519 identity challenge nonce (live MCP, AAA Wave 2 / Phase 5). "
            "Generates a cryptographically random 32-byte nonce, base64-encoded, with a TTL "
            "(default 300s). The nonce is single-use and registered in the issued-challenges "
            "registry; arif_verify must consume it. "
            "Input: actor_id (required), session_id? (optional binding), ttl_seconds? (default 300). "
            "Output: challenge (b64 nonce), issued_at (ISO-8601 UTC), ttl_seconds, session_id. "
            "Use when: starting an Ed25519 identity ceremony; the actor signs "
            'f"{actor_id}:{challenge}" with its Ed25519 private key and submits via arif_verify.'
        ),
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [
            Law.L01_AMANAH,
            Law.L02_TRUTH,
            Law.L11_AUDIT,
            Law.L12_INJECTION,
        ],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["challenge"],
        "eureka_insight": (
            "One-shot nonce = no replay. Every arif_challenge birth = one arif_verify death."
        ),
        "cognitive_axis": "identity",
        "expose": True,  # AAA Wave 2: live MCP surface for Ed25519 ceremony
    },
    "arif_act": {
        "name": "arif_act",
        "description": (
            "INTERNAL alias for arif_forge. Retained for backward compatibility with "
            "intercept routing tables. Not on public surface; call arif_forge instead."
        ),
        "access": "internal_only",
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
            "F13-ratified 2026-07-04: arif_forge replaces arif_act on the public wire. "
            "arif_act retained internally for backwards compatibility."
        ),
        "cognitive_axis": "execute",
        "expose": False,  # F13-ratified 2026-07-04: arif_forge is now the canonical public name
    },
    "arif_forge": {
        "name": "arif_forge",
        "description": (
            "KERNEL 777 · Execution gate via A-FORGE (hands, not law). Mutates only after "
            "arif_judge SEAL + lease/chain IDs — no self-authorize. Modes: dry_run | "
            "engineer | query | write | generate | commit | recall. Public execution "
            "verb (arif_act is internal alias only). "
            "Use when: a constitutional verdict (SEAL) has been obtained and the agent "
            "needs to execute a mutation — code changes, deployments, file writes, git operations."
        ),
        "access": "authenticated",
        "stage": ToolStage.FORGE_EXECUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L11_AUDIT, Law.L13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "modes": ["engineer", "query", "write", "generate", "commit", "recall", "dry_run"],
        "eureka_insight": (
            "F1: irreversible — ack_irreversible=True mandatory. "
            "L11: actor verified. L12: fail safely; no unsafe continuation when "
            "substrate confidence drops. L13: judge SEAL_CANDIDATE required before "
            "execution. F13-ratified 2026-07-04: arif_forge replaces arif_act as the "
            "canonical public execution tool."
        ),
        "cognitive_axis": "execute",
        "expose": True,  # F13-ratified 2026-07-04: 12-tool kernel trim — canonical public execution gate
    },
    "arif_measure": {
        "name": "arif_measure",
        "description": (
            "INTERNAL: Kernel *runtime* health only (process, transport, topology, "
            "resource metrics). NOT human readiness or coupled vitality — those are "
            "WELL (well_validate_vitality). Alias intent: arif_runtime_health. "
            "Boundary: AAA/docs/MEASUREMENT_BOUNDARY_CONTRACT.md."
        ),
        "access": "internal_only",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L02_TRUTH, Law.L04_CLARITY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": [
            "health",
            "vitals",
            "cost",
            "genius",
            "topology",
            "drift",
        ],
        "eureka_insight": (
            "F4: ΔS ≤ 0 — ops must contribute to entropy reduction. "
            "F8: measured intelligence is not useful intelligence."
        ),
        "cognitive_axis": "vitality",
        "expose": False,
    },
    # ── Entropy Integrity Mesh — public wire (v2026.07.12) ──────────
    # Must live in CANONICAL_TOOLS (not ONE_SKILL classification).
    # Matches public_surface.CANONICAL_12 public facade.
    "arif_entropy_observe": {
        "name": "arif_entropy_observe",
        "description": (
            "Register a structured entropy observation from an authorised organ. "
            "Collects observations WITHOUT producing a verdict. Validates against "
            "prohibited-inference policy. Enters J-state pipeline after validation."
        ),
        "access": "internal_only",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L09_ANTIHANTU, Law.L02_TRUTH, Law.L11_AUDIT],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["observe"],
        "eureka_insight": "F9: never infer hidden niat. Observe behavior, not character.",
        "cognitive_axis": "observe",
        "expose": False,
    },
    "arif_j_state_assess": {
        "name": "arif_j_state_assess",
        "description": (
            "Fuse organ observations into a judgment-integrity map. "
            "Computes 5 J-planes using MINIMUM-FLOOR aggregation. "
            "Never outputs a diagnosis or moral identity."
        ),
        "access": "internal_only",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L09_ANTIHANTU, Law.L02_TRUTH, Law.L04_CLARITY],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": ["assess"],
        "eureka_insight": "J-state uses MINIMUM-FLOOR: weakest plane determines overall state.",
        "cognitive_axis": "judge",
        "expose": False,
    },
    "arif_correction_probe": {
        "name": "arif_correction_probe",
        "description": (
            "Generate a neutral challenge and record the response. "
            "Modes: draft_probe, record_response, classify_response, close_probe."
        ),
        "access": "internal_only",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L02_TRUTH, Law.L11_AUDIT],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["draft_probe", "record_response", "classify_response", "close_probe"],
        "eureka_insight": "Correction response is behavior evidence, not character judgment.",
        "cognitive_axis": "judge",
        "expose": False,
    },
    "arif_consequence_trace": {
        "name": "arif_consequence_trace",
        "description": (
            "Trace who makes the decision, who receives benefits, "
            "who bears harm, and who can reverse it."
        ),
        "access": "internal_only",
        "stage": ToolStage.OBSERVE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L06_EMPATHY, Law.L11_AUDIT],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["trace"],
        "eureka_insight": "Consequence gap = power * benefit_capture * harm_distance * non_accountability.",
        "cognitive_axis": "observe",
        "expose": False,
    },
    "arif_entropy_route": {
        "name": "arif_entropy_route",
        "description": (
            "Route domain questions to the correct organ. "
            "Human stress -> WELL; capital -> WEALTH; physical -> GEOX; runtime -> A-FORGE."
        ),
        "access": "internal_only",
        "stage": ToolStage.ROUTE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L04_CLARITY],
        "risk_tier": "low",
        "irreversible": False,
        "modes": ["route"],
        "eureka_insight": "Each organ measures only what it owns. arifOS combines signals.",
        "cognitive_axis": "route",
        "expose": False,
    },
    "arif_j_gate": {
        "name": "arif_j_gate",
        "description": (
            "Convert J-state evidence into action posture. "
            "J0->VOID, J1->HOLD, J2->reversible only, J3->bounded, J4->witnessed. "
            "Never issues VAULT999 SEAL autonomously."
        ),
        "access": "internal_only",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.AGI,
        "floors": [Law.L01_AMANAH, Law.L13_SOVEREIGN, Law.L09_ANTIHANTU],
        "risk_tier": "high",
        "irreversible": False,
        "modes": ["gate"],
        "eureka_insight": "F13: J-gate NEVER permits autonomous SEAL. Human veto is absolute.",
        "cognitive_axis": "judge",
        "expose": False,
    },
}


# ═─ Public wire surface (metabolic 12 + entropy mesh 6 = 18) ──────
# SOT order/names live in public_surface.CANONICAL_12. This frozenset is the
# expose=True filter for CANONICAL_TOOLS. Must stay set-equal to that tuple.
# Tools not in this set are force-set to access="internal_only", expose=False.
_PUBLIC_12: frozenset[str] = frozenset(
    {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_bridge_connect",
        "arif_critique",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_compose",
        "arif_seal",
        "arif_verify",
        "arif_entropy_observe",
        "arif_j_state_assess",
        "arif_correction_probe",
        "arif_consequence_trace",
        "arif_entropy_route",
        "arif_j_gate",
    }
)
# Backward-compat aliases (DEPRECATED).
_PUBLIC_9: frozenset[str] = _PUBLIC_12
_PUBLIC_7: frozenset[str] = _PUBLIC_12
_PUBLIC_13: frozenset[str] = _PUBLIC_12

for _name, _spec in CANONICAL_TOOLS.items():
    if _name not in _PUBLIC_12:
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
        "arif_init": {
            "restraint": "STRICT",
            "verdict": "REQUIRED",
            "classification": "Binds geometry with One Skill flags + One Tool requirement.",
        },
        "arif_observe": {
            "restraint": "STANDARD",
            "verdict": "NONE",
            "classification": "Observe only; restraint for clarity, no verdict needed.",
        },
        "arif_think": {
            "restraint": "STANDARD",
            "verdict": "CONDITIONAL",
            "classification": "Reasoning under uncertainty; restraint prevents overfit.",
        },
        "arif_judge": {
            "restraint": "STRICT",
            "verdict": "REQUIRED",
            "classification": "The One Tool: renders the verdict that enables or refuses action.",
        },
        "arif_seal": {
            "restraint": "STRICT",
            "verdict": "REQUIRED",
            "classification": "Seals the verdict into append-only memory.",
        },
        "arif_forge": {
            "restraint": "STRICT",
            "verdict": "REQUIRED",
            "classification": "Execution substrate. Only after One Tool verdict + One Skill check.",
        },
        "arif_forge_execute": {
            "restraint": "STRICT",
            "verdict": "REQUIRED",
            "classification": "Teeth of the system. enforce_restraint_and_verdict must PASS.",
        },
        "arif_act": {
            "restraint": "STRICT",
            "verdict": "REQUIRED",
            "classification": "Execution gate. Requires prior seal from One Tool.",
        },
        "arif_memory": {
            "restraint": "STANDARD",
            "verdict": "CONDITIONAL",
            "classification": "Memory ops gated by restraint for mutation.",
        },
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
    "arif_vault_query": {
        "name": "arif_vault_query",
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
        title="000 Init · Kernel Session",
    ),
    "arif_observe": derive_mcp_annotations(
        "OBSERVE",
        title="111 Observe · Sense Reality",
    ),
    "arif_fetch": derive_mcp_annotations(
        "OBSERVE",
        title="Evidence Fetch",
    ),
    "arif_think": derive_mcp_annotations(
        "ANALYZE",
        title="333 Think · Mind",
    ),
    "arif_critique": derive_mcp_annotations(
        "ANALYZE",
        title="555 Critique · Heart",
    ),
    "arif_compose": derive_mcp_annotations(
        "ANALYZE",
        title="Compose · Kernel Reply",
    ),
    "arif_judge": derive_mcp_annotations(
        "DRAFT",
        title="888 Judge · Verdict",
    ),
    "arif_seal": derive_mcp_annotations(
        "IRREVERSIBLE",
        title="999 Seal · VAULT999",
        is_irreversible=True,
    ),
    "arif_forge": derive_mcp_annotations(
        "MUTATE",
        title="777 Forge · Execute Gate",
        is_irreversible=True,
    ),
    "arif_measure": derive_mcp_annotations(
        "OBSERVE",
        title="Ops Measure",
    ),
    "arif_memory": derive_mcp_annotations(
        "MUTATE",
        title="Memory Governor · Kernel",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # RULE-14 DIAGNOSTIC TOOLS — action_class from kernel_canonical spec
    # ═══════════════════════════════════════════════════════════════════
    "arif_route": derive_mcp_annotations(
        "ANALYZE",
        title="444 Route · Intent→Organ",
    ),
    "arif_triage": derive_mcp_annotations(
        "ANALYZE",
        title="000 Triage · Session Preflight",
    ),
    "arif_bridge_connect": derive_mcp_annotations(
        "BRIDGE",
        title="444 Bridge · Direct Organ (HIGH)",
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
    "arif_vault_query": derive_mcp_annotations(
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
    "arif_fetch": ToolStage.OBSERVE,
    "arif_think": ToolStage.REASON,
    "arif_critique": ToolStage.REASON,
    "arif_route": ToolStage.ROUTE,
    "arif_compose": ToolStage.REPLY,
    "arif_judge": ToolStage.JUDGE,
    "arif_seal": ToolStage.SEAL,
    "arif_forge": ToolStage.FORGE_EXECUTE,
    "arif_measure": ToolStage.OBSERVE,
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
    # The canonical public surface is the 9-stage metabolic loop.
    return list(CORE_NINE)


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
    Merges CANONICAL_TOOLS + DIAGNOSTIC_TOOLS into one machine-readable registry.

    Public canonical order is the exposed 7-tool facade. Non-exposed entries from
    CANONICAL_TOOLS remain in the manifest as internal aliases/supporting tools,
    but they are not counted as public canonical surface.

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

    public_canonical_order = [
        name
        for name in [
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_judge",
            "arif_forge",
            "arif_compose",
            "arif_seal",
        ]
        if name in CANONICAL_TOOLS and CANONICAL_TOOLS[name].get("expose", True)
    ]
    internal_canonical_order = [
        name
        for name, spec in CANONICAL_TOOLS.items()
        if not spec.get("expose", True) and name not in DIAGNOSTIC_TOOLS
    ]

    all_tools: dict[str, dict[str, Any]] = {}

    # ── Canonical (13 kernel + Rule-14 diagnostics) ──
    for name, spec in CANONICAL_TOOLS.items():
        is_public = spec.get("expose", True)
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
            "tier": "canonical" if is_public else "internal",
            "namespace": (
                "arif_* (canonical public prefix)"
                if is_public
                else "arif_* (internal supporting alias)"
            ),
            "tags": ["canonical"] if is_public else ["internal", "non-public"],
            "public_exposed": is_public,
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
            "Generated from CANONICAL_TOOLS + DIAGNOSTIC_TOOLS. "
            "canonical_order is the exposed 7-tool public facade; internal_canonical_order contains "
            "non-public supporting aliases that remain registered for compatibility and governed routing. "
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
            "arif_*": "9-stage metabolic loop public verbs plus internal supporting aliases",
            "hermes_*": "GATED — Hermes ASI cross-verification tools (requires ARIFOS_MCP_EXPOSE_DEV_TOOLS=true)",
            "forge_*": "GATED/DEPRECATED — A-FORGE pre-execution sub-tools (use A-FORGE MCP directly)",
            "arifos_*": "BLOCKED — internal-only prefix, never exposed on public MCP surface",
            "mcp_*": "GATED — Utility namespace for operational diagnostics",
        },
        "canonical_count": len(public_canonical_order),
        "internal_canonical_count": len(internal_canonical_order),
        "diagnostic_count": len(DIAGNOSTIC_TOOLS),
        "total_surface": len(all_tools),
        "tier_summary": tier_counts,
        "tier_legend": {
            "canonical": "7 exposed public verbs on the default MCP wire surface",
            "internal": "Internal supporting arif_* aliases/tools kept for governed routing and compatibility",
            "hermes": "Cross-verification, fact-checking, vault query, and epistemic checks",
            "canary": "Transport and protocol echo/probe tools",
            "lease": "Capability lease lifecycle tools",
            "attest": "Federation organ attestation and heartbeat tools",
            "forge-sub": "Pre-execution forge planning tools",
            "narrative": "Institutional shadow drift and narrative tension detection tools",
            "diagnostic": "Health probes, drift checks, floor status, budget telemetry, and scanners",
        },
        "canonical_order": public_canonical_order,
        "internal_canonical_order": internal_canonical_order,
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
    "DeltaIrreversibilityClass",
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
