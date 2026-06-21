"""
_epistemic Response Envelope — Halal/Haram Boundary at Transport Level
═══════════════════════════════════════════════════════════════════════════

Every MCP response from any federation organ MUST carry an ``_epistemic``
field declaring the nature of the output. This dissolves the SYUBHAH problem:

  An AI-generated explanation cannot be mistaken for a deterministic verdict
  across a transport hop because the envelope labels it.

Four-field taxonomy ratified by Arif bin Fazil (F13 SOVEREIGN), 2026-06-21:

  output_class:     What kind of processing produced this
  ai_involvement:   Whether an LLM touched it
  authority_claim:  Can this be treated as authoritative?
  evidence_source:  Where the data came from

Halal/haram boundary:
  - AI may generate interpretation, NOT authority
  - AI may generate explanation, NOT evidence
  - AI may generate strategy, NOT audit truth
  - AI may recommend action, NOT self-approve action

DITEMPA BUKAN DIBERI — Every output carries its own epistemic label.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT CLASS — What kind of processing produced this output
# ═══════════════════════════════════════════════════════════════════════════════


class OutputClass(StrEnum):
    """Classification of the processing path that produced the output.

    DETERMINISTIC        — Pure rule engine / calculation / telemetry.
                           No AI involvement. Examples: constitution_hash,
                           tool_count_live, health probes, schema validation.

    GOVERNANCE_TEMPLATE  — Structured text generated from governance templates.
                           May include rule-based explanatory prose.
                           Examples: "Reversible operation verified",
                           "Constitutional floors passed".

    AI_ADVISORY          — Output produced or assisted by an AI/LLM path.
                           Always advisory, never authoritative on its own.
                           Examples: arif_mind_reason, arif_heart_critique,
                           arif_reply_compose, arif_evidence_fetch summaries.

    DOMAIN_COMPUTATION   — Domain-specific computation from an organ engine.
                           May mix deterministic calculation with heuristics.
                           Examples: GEOX petrophysics, WEALTH NPV, WELL vitality.
    """

    DETERMINISTIC = "DETERMINISTIC"
    GOVERNANCE_TEMPLATE = "GOVERNANCE_TEMPLATE"
    AI_ADVISORY = "AI_ADVISORY"
    DOMAIN_COMPUTATION = "DOMAIN_COMPUTATION"


# ═══════════════════════════════════════════════════════════════════════════════
# AI INVOLVEMENT — Whether an LLM touched this output
# ═══════════════════════════════════════════════════════════════════════════════


class AiInvolvement(StrEnum):
    """Degree of AI/LLM involvement in producing this output.

    NONE             — No LLM involvement. Pure deterministic or template.
    ASSISTED         — LLM assisted but final output is governed by determinism.
                       Example: LLM rephrased a deterministic result.
    GENERATED        — LLM generated the output content.
                       Example: arif_mind_reason reasoning trace.
    FALLBACK_SKIPPED — AI path was attempted but not completed; deterministic
                       fallback returned instead. Carries a degraded_reason field.
    """

    NONE = "NONE"
    ASSISTED = "ASSISTED"
    GENERATED = "GENERATED"
    FALLBACK_SKIPPED = "FALLBACK_SKIPPED"


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHORITY CLAIM — Whether this output can be treated as authoritative
# ═══════════════════════════════════════════════════════════════════════════════


class AuthorityClaim(StrEnum):
    """What authority this output carries.

    NONE       — No authority claim. Advisory only.
    ADVISORY   — May inform decisions but is not binding.
    EXECUTIVE  — Authoritative. Can be used for irreversible actions.
                 Haram for AI-generated content. Must be DETERMINISTIC +
                 NONE + COMPUTED or MEASURED.
    """

    NONE = "NONE"
    ADVISORY = "ADVISORY"
    EXECUTIVE = "EXECUTIVE"


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE SOURCE — Where the data came from
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceSource(StrEnum):
    """Origin of the evidence in this output.

    COMPUTED       — Derived from deterministic computation.
    MEASURED       - Observed from live system state (probes, telemetry).
    RETRIEVED     — Retrieved from storage (DB, vault, cache).
    AI_SYNTHESIZED — Generated or hallucinated by AI. Must never enter vault.
    """

    COMPUTED = "COMPUTED"
    MEASURED = "MEASURED"
    RETRIEVED = "RETRIEVED"
    AI_SYNTHESIZED = "AI_SYNTHESIZED"


# ═══════════════════════════════════════════════════════════════════════════════
# THE _EPISTEMIC ENVELOPE — Every response carries one
# ═══════════════════════════════════════════════════════════════════════════════


class EpistemicTag(BaseModel):
    """Four-field epistemic classification for every MCP response.

    This is the halal/haram boundary at the transport level.
    Every MCP endpoint from every federation organ MUST inject this
    into its response before returning.

    The receiver (kernel router, vault sealer, bridge, or downstream agent)
    MUST read this field to determine how to treat the output.
    """

    output_class: OutputClass = Field(
        ...,
        description=(
            "What kind of processing produced this output: "
            "DETERMINISTIC, GOVERNANCE_TEMPLATE, AI_ADVISORY, or DOMAIN_COMPUTATION"
        ),
    )
    ai_involvement: AiInvolvement = Field(
        ...,
        description="Whether an LLM touched this output: NONE, ASSISTED, GENERATED, FALLBACK_SKIPPED",
    )
    authority_claim: AuthorityClaim = Field(
        ...,
        description=(
            "Can this be treated as authoritative? "
            "NONE (advisory), ADVISORY (inform but not binding), "
            "EXECUTIVE (authoritative). Haram for AI-generated content."
        ),
    )
    evidence_source: EvidenceSource = Field(
        ...,
        description=(
            "Where the data came from: COMPUTED, MEASURED, RETRIEVED, "
            "AI_SYNTHESIZED. AI_SYNTHESIZED must never enter vault."
        ),
    )

    # Optional: human-readable reason for FALLBACK_SKIPPED or degraded paths
    degraded_reason: str | None = Field(
        None,
        description="If ai_involvement is FALLBACK_SKIPPED, explain why",
    )

    # Optional: audit chain — which node or hop added this epistemic tag
    tagged_by: str | None = Field(
        None,
        description="Which organ/node injected this epistemic tag (e.g. 'arifOS', 'geox', 'aforge')",
    )
    tagged_at: str | None = Field(
        None,
        description="ISO timestamp of when this tag was injected",
    )

    # ── Schema version for forward compat ──
    schema_version: str = "1.0.0"


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULTS — Quick presets for common tool classes
# ═══════════════════════════════════════════════════════════════════════════════


# Deterministic kernel/telemetry tools
EPISTEMIC_DETERMINISTIC = EpistemicTag(
    output_class=OutputClass.DETERMINISTIC,
    ai_involvement=AiInvolvement.NONE,
    authority_claim=AuthorityClaim.EXECUTIVE,
    evidence_source=EvidenceSource.COMPUTED,
)

# Governance template prose
EPISTEMIC_GOVERNANCE_TEMPLATE = EpistemicTag(
    output_class=OutputClass.GOVERNANCE_TEMPLATE,
    ai_involvement=AiInvolvement.NONE,
    authority_claim=AuthorityClaim.ADVISORY,
    evidence_source=EvidenceSource.COMPUTED,
)

# AI advisory / reasoning output (wajib AI-assisted)
EPISTEMIC_AI_ADVISORY = EpistemicTag(
    output_class=OutputClass.AI_ADVISORY,
    ai_involvement=AiInvolvement.GENERATED,
    authority_claim=AuthorityClaim.ADVISORY,
    evidence_source=EvidenceSource.AI_SYNTHESIZED,
)

# AI advisory that fell back to deterministic (degraded)
EPISTEMIC_AI_FALLBACK = EpistemicTag(
    output_class=OutputClass.AI_ADVISORY,
    ai_involvement=AiInvolvement.FALLBACK_SKIPPED,
    authority_claim=AuthorityClaim.ADVISORY,
    evidence_source=EvidenceSource.COMPUTED,
)

# Domain computation (e.g. GEOX petrophysics, WEALTH NPV)
EPISTEMIC_DOMAIN_COMPUTATION = EpistemicTag(
    output_class=OutputClass.DOMAIN_COMPUTATION,
    ai_involvement=AiInvolvement.NONE,
    authority_claim=AuthorityClaim.ADVISORY,
    evidence_source=EvidenceSource.COMPUTED,
)

# Domain computation with AI assistance
EPISTEMIC_DOMAIN_ASSISTED = EpistemicTag(
    output_class=OutputClass.DOMAIN_COMPUTATION,
    ai_involvement=AiInvolvement.ASSISTED,
    authority_claim=AuthorityClaim.ADVISORY,
    evidence_source=EvidenceSource.COMPUTED,
)

# Measured telemetry (health probes, live readings)
EPISTEMIC_MEASURED = EpistemicTag(
    output_class=OutputClass.DETERMINISTIC,
    ai_involvement=AiInvolvement.NONE,
    authority_claim=AuthorityClaim.EXECUTIVE,
    evidence_source=EvidenceSource.MEASURED,
)

# Retrieved from storage (vault reads, memory recall)
EPISTEMIC_RETRIEVED = EpistemicTag(
    output_class=OutputClass.DETERMINISTIC,
    ai_involvement=AiInvolvement.NONE,
    authority_claim=AuthorityClaim.EXECUTIVE,
    evidence_source=EvidenceSource.RETRIEVED,
)


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATORS — Cross-field rules
# ═══════════════════════════════════════════════════════════════════════════════


def validate_halal_haram(epistemic: EpistemicTag) -> list[str]:
    """Validate the epistemic tag against halal/haram rules.

    Returns a list of violations (empty = clean).
    """
    violations: list[str] = []

    # Rule 1: AI may not claim EXECUTIVE authority
    if epistemic.ai_involvement in (AiInvolvement.GENERATED, AiInvolvement.ASSISTED):
        if epistemic.authority_claim == AuthorityClaim.EXECUTIVE:
            violations.append(
                "HARAM: AI-generated/assisted output must not claim EXECUTIVE authority. "
                "AI may generate interpretation, not authority."
            )

    # Rule 2: AI_SYNTHESIZED evidence must not claim EXECUTIVE
    if epistemic.evidence_source == EvidenceSource.AI_SYNTHESIZED:
        if epistemic.authority_claim == AuthorityClaim.EXECUTIVE:
            violations.append(
                "HARAM: AI-synthesised evidence must not claim EXECUTIVE authority. "
                "AI may generate explanation, not evidence."
            )

    # Rule 3: DETERMINISTIC with NONE ai_involvement should claim evidence source properly
    if (
        epistemic.output_class == OutputClass.DETERMINISTIC
        and epistemic.ai_involvement == AiInvolvement.NONE
    ):
        if epistemic.evidence_source == EvidenceSource.AI_SYNTHESIZED:
            violations.append(
                "PARADOX: DETERMINISTIC output with NONE AI involvement "
                "cannot have AI_SYNTHESIZED evidence source."
            )

    # Rule 4: EXECUTIVE authority requires NONE AI involvement and COMPUTED/MEASURED evidence
    if epistemic.authority_claim == AuthorityClaim.EXECUTIVE:
        if epistemic.ai_involvement != AiInvolvement.NONE:
            violations.append(
                "HARAM: EXECUTIVE authority requires NONE AI involvement. "
                f"Got {epistemic.ai_involvement}."
            )
        if epistemic.evidence_source not in (EvidenceSource.COMPUTED, EvidenceSource.MEASURED, EvidenceSource.RETRIEVED):
            violations.append(
                "HARAM: EXECUTIVE authority requires COMPUTED or MEASURED evidence source. "
                f"Got {epistemic.evidence_source}."
            )

    return violations


def assert_tag_valid(epistemic: EpistemicTag) -> None:
    """Raise ValueError if epistemic tag violates halal/haram rules."""
    violations = validate_halal_haram(epistemic)
    if violations:
        raise ValueError(
            f"Epistemic tag violates halal/haram boundary:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )
