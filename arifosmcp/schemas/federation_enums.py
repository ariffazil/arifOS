"""
Federation-Wide Canonical Enums — Single Source of Truth
═══════════════════════════════════════════════════════════

F13 SOVEREIGN RATIFIED: 2026-07-14 (Arif bin Fazil)
CANONICAL SOURCE: All federation organs MUST import from here.
DO NOT define duplicates in individual organs.

If import is not possible (separate package), copy with header:
    "# CANONICAL SOURCE: arifOS/arifosmcp/schemas/federation_enums.py"
    "# VALUES MUST MATCH canonical exactly — CI gate enforces this."

14 enum families covering every cross-organ contract:
  1.  Verdict              — Constitutional outcomes
  2.  EpistemicTag         — Type of knowledge claim
  3.  EvidenceQuality      — Reliability of evidence
  4.  ConfidenceLevel      — Certainty assessment
  5.  OutputClass          — Processing path classification
  6.  SessionState         — Session authority bands
  7.  GovernanceLane       — Routing lanes for organ dispatch
  8.  ReceiptState         — Receipt lifecycle stages
  9.  ToolAffordanceState  — Tool surface status
  10. EvidenceSourceRank   — Source priority ranking
  11. IntentClass          — Agent output shape (QQQ gating)
  12. PathCategory         — QQQ path classification
  13. PriorArt             — QQQ prior-art availability
  14. QQQCompliance        — QQQ envelope completeness state

DITEMPA BUKAN DIBERI — One schema to govern them all.
"""

from __future__ import annotations

from enum import StrEnum

# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERDICT — Constitutional outcomes
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: stage_packets.VerdictType + transition_receipt.VerdictCode
# + APEX evaluation gates. These 6 cover all constitutional decision paths.


class Verdict(StrEnum):
    """Constitutional verdict — the only 6 outcomes an arif_judge may emit.

    SEAL     — Action is lawful, evidence meets threshold. Execute and record.
    HOLD     — Action is blocked pending human sovereign decision (F13).
    SABAR    — Action deferred. Not blocked but not yet ready. Re-evaluate.
    VOID     — Action is unlawful or impossible. Never execute.
    OBSERVE  — Action is observation-only. No mutation, no seal required.
    PARTIAL  — Action partially approved. Conditions apply before full SEAL.
    """

    SEAL = "SEAL"
    HOLD = "HOLD"
    SABAR = "SABAR"
    VOID = "VOID"
    OBSERVE = "OBSERVE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"  # fail-closed: unknown verdict = HOLD


# Mapping: which verdicts allow execution?
VERDICT_EXECUTION_MAP = {
    Verdict.SEAL: True,
    Verdict.PARTIAL: True,  # with conditions
    Verdict.OBSERVE: True,
    Verdict.HOLD: False,
    Verdict.SABAR: False,
    Verdict.VOID: False,
    Verdict.UNKNOWN: False,
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. EPISTEMIC TAG — What type of knowledge claim is this?
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: WEALTH epistemic.EpistemicTag, WELL federation_safety.EpistemicLayer,
# evidence.CertaintyCap, GEOX implicit tags.
# Full names ONLY — short codes (OBS/DER/INT/SPEC) are legacy.
# Short→full mapping provided for backward compat.


class EpistemicTag(StrEnum):
    """Label every knowledge claim with its epistemic strength.

    Ordered weakest → strongest:
      ASSUMED < SPECULATED < INTERPRETED < DERIVED < OBSERVED

    OBSERVED     — Direct measurement (sensor, well log, market price, probe).
    DERIVED      — Computed from observed data (NPV, porosity, synthetic).
    INTERPRETED  — Inferred from patterns by expert or model (facies, trend).
    SPECULATED   — Hypothesis without sufficient evidence (wildcat prospect).
    ASSUMED      — Input parameter, not verified against ground truth.
    """

    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INTERPRETED = "INTERPRETED"
    SPECULATED = "SPECULATED"
    ASSUMED = "ASSUMED"


# Built-in ordering (index 0 = weakest)
EPISTEMIC_ORDER = [
    EpistemicTag.ASSUMED,
    EpistemicTag.SPECULATED,
    EpistemicTag.INTERPRETED,
    EpistemicTag.DERIVED,
    EpistemicTag.OBSERVED,
]

# Short-code compatibility (WELL legacy → canonical)
EPISTEMIC_SHORT_TO_FULL = {
    "OBS": EpistemicTag.OBSERVED,
    "DER": EpistemicTag.DERIVED,
    "INT": EpistemicTag.INTERPRETED,
    "SPEC": EpistemicTag.SPECULATED,
    "CLAIM": EpistemicTag.OBSERVED,  # Bursa/WEALTH compat
    "PLAUSIBLE": EpistemicTag.DERIVED,
    "ESTIMATE": EpistemicTag.INTERPRETED,
    "HYPOTHESIS": EpistemicTag.SPECULATED,
    "UNKNOWN": EpistemicTag.ASSUMED,
}

# Full→short mapping (for organs that still emit short codes)
EPISTEMIC_FULL_TO_SHORT = {
    EpistemicTag.OBSERVED: "OBS",
    EpistemicTag.DERIVED: "DER",
    EpistemicTag.INTERPRETED: "INT",
    EpistemicTag.SPECULATED: "SPEC",
    EpistemicTag.ASSUMED: "ASM",
}


def normalize_epistemic(tag: str) -> EpistemicTag:
    """Normalize any epistemic tag variant to canonical form.

    Accepts: OBS, DER, INT, SPEC, ASM, CLAIM, PLAUSIBLE,
             OBSERVED, DERIVED, INTERPRETED, SPECULATED, ASSUMED
    """
    upper = tag.upper().strip()
    if upper in EPISTEMIC_SHORT_TO_FULL:
        return EPISTEMIC_SHORT_TO_FULL[upper]
    for member in EpistemicTag:
        if member.value == upper:
            return member
    return EpistemicTag.ASSUMED  # fail-weakest


# ═══════════════════════════════════════════════════════════════════════════════
# 3. EVIDENCE QUALITY — How reliable is the evidence?
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: WEALTH epistemic.EvidenceQuality, GEOX implicit quality.
# Replaces legacy STRONG/MODERATE/WEAK/MISSING/CONFLICTED with
# canonical OBSERVED/DERIVED/INTERPRETED/SPECULATED/ASSUMED.


class EvidenceQuality(StrEnum):
    """Quality of evidence supporting a claim or computation.

    OBSERVED     — Direct measurement (sensor, well log, market price).
    DERIVED      — Computed from observed data (NPV, porosity, seismic attr).
    INTERPRETED  — Inferred from patterns (facies, depositional environment).
    SPECULATED   — Hypothesis without sufficient evidence (prospect).
    ASSUMED      — Input parameter, not verified.
    """

    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INTERPRETED = "INTERPRETED"
    SPECULATED = "SPECULATED"
    ASSUMED = "ASSUMED"


EVIDENCE_QUALITY_ORDER = [
    EvidenceQuality.ASSUMED,
    EvidenceQuality.SPECULATED,
    EvidenceQuality.INTERPRETED,
    EvidenceQuality.DERIVED,
    EvidenceQuality.OBSERVED,
]

# Legacy WEALTH mapping
EVIDENCE_QUALITY_LEGACY_MAP = {
    "STRONG": EvidenceQuality.OBSERVED,
    "MODERATE": EvidenceQuality.DERIVED,
    "WEAK": EvidenceQuality.INTERPRETED,
    "MISSING": EvidenceQuality.SPECULATED,
    "CONFLICTED": EvidenceQuality.SPECULATED,
}


def normalize_evidence_quality(value: str) -> EvidenceQuality:
    """Normalize evidence quality from any legacy format."""
    upper = value.upper().strip()
    if upper in EVIDENCE_QUALITY_LEGACY_MAP:
        return EVIDENCE_QUALITY_LEGACY_MAP[upper]
    if upper in EPISTEMIC_SHORT_TO_FULL:
        return EvidenceQuality(upper.replace("OBSERVED", "OBSERVED"))
    for member in EvidenceQuality:
        if member.value == upper:
            return member
    return EvidenceQuality.ASSUMED


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CONFIDENCE LEVEL — How certain are we?
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: WELL metabolic.ConfidenceLevel.
# This is already shared across WELL and referenced by arifOS.


class ConfidenceLevel(StrEnum):
    """Shared confidence language across all organs.

    UNKNOWN    — No evidence assessed. Default state before evaluation.
    LOW        — Weak evidence, high uncertainty, single source.
    MODERATE   — Some evidence, plausible but not independently verified.
    HIGH       — Strong evidence, multiple independent sources, cross-referenced.
    VERIFIED   — Independently confirmed by external witness or measurement.
    SEALED     — Immutable record in VAULT999. Irreversible. Highest confidence.
    """

    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERIFIED = "VERIFIED"
    SEALED = "SEALED"


CONFIDENCE_ORDER = [
    ConfidenceLevel.UNKNOWN,
    ConfidenceLevel.LOW,
    ConfidenceLevel.MODERATE,
    ConfidenceLevel.HIGH,
    ConfidenceLevel.VERIFIED,
    ConfidenceLevel.SEALED,
]


# ═══════════════════════════════════════════════════════════════════════════════
# 5. OUTPUT CLASS — What kind of processing produced this output?
# ═══════════════════════════════════════════════════════════════════════════════

# Canonical source: epistemic_tag.py in this same schemas directory.
# Re-exported here for single-import convenience.


class OutputClass(StrEnum):
    """Classification of the processing path that produced the output.

    DETERMINISTIC        — Pure rule engine / calculation / telemetry.
                           No AI involvement.
    GOVERNANCE_TEMPLATE  — Structured text from governance templates.
    AI_ADVISORY          — Output produced or assisted by AI/LLM.
    DOMAIN_COMPUTATION   — Domain computation (petrophysics, NPV, vitality).
    """

    DETERMINISTIC = "DETERMINISTIC"
    GOVERNANCE_TEMPLATE = "GOVERNANCE_TEMPLATE"
    AI_ADVISORY = "AI_ADVISORY"
    DOMAIN_COMPUTATION = "DOMAIN_COMPUTATION"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SESSION STATE — Authority bands for active agent sessions
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: arif_init authority bands (OBSERVE_ONLY, LIMITED_MUTATE, FULL)
# + session state machine. Every session token carries one of these.


class SessionState(StrEnum):
    """Authority band for an active agent session.

    OBSERVE_ONLY   — Read-only. No mutations, no seals.
    LIMITED_MUTATE — Reversible mutations allowed. No seals, no irreversible.
    FULL           — Full authority up to configured ceiling. Seals allowed.
    SABAR          — Session degraded or blocked. Escalate before action.
    ANONYMOUS      — No session bound. OBSERVE only, no identity.
    """

    OBSERVE_ONLY = "OBSERVE_ONLY"
    LIMITED_MUTATE = "LIMITED_MUTATE"
    FULL = "FULL"
    SABAR = "SABAR"
    ANONYMOUS = "ANONYMOUS"
    UNKNOWN = "UNKNOWN"


SESSION_STATE_ORDER = [
    SessionState.ANONYMOUS,
    SessionState.OBSERVE_ONLY,
    SessionState.LIMITED_MUTATE,
    SessionState.FULL,
]


# ═══════════════════════════════════════════════════════════════════════════════
# 7. GOVERNANCE LANE — Routing lanes for organ dispatch
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: arif_route routing logic + GEOX judgment lane blocking.
# Every MCP tool in the federation belongs to exactly one lane.


class GovernanceLane(StrEnum):
    """Governance lane for organ routing and authority enforcement.

    OBSERVE     — Read-only evidence gathering. Lowest gate.
    REASONING   — Computation, inference, analysis. Medium gate.
    JUDGMENT    — Constitutional verdict. Requires arifOS kernel.
    EXECUTION   — Mutation, deployment, irreversible act. Requires A-FORGE lease.
    COCKPIT     — Display, routing, registry, state. No mutation.
    """

    OBSERVE = "OBSERVE"
    REASONING = "REASONING"
    JUDGMENT = "JUDGMENT"
    EXECUTION = "EXECUTION"
    COCKPIT = "COCKPIT"
    UNKNOWN = "UNKNOWN"


# Lane → minimum session state mapping
LANE_MINIMUM_SESSION = {
    GovernanceLane.OBSERVE: SessionState.ANONYMOUS,
    GovernanceLane.REASONING: SessionState.OBSERVE_ONLY,
    GovernanceLane.COCKPIT: SessionState.OBSERVE_ONLY,
    GovernanceLane.EXECUTION: SessionState.LIMITED_MUTATE,
    GovernanceLane.JUDGMENT: SessionState.FULL,
    GovernanceLane.UNKNOWN: SessionState.OBSERVE_ONLY,  # fail-safe
}


# ═══════════════════════════════════════════════════════════════════════════════
# 8. RECEIPT STATE — Lifecycle stage of a receipt through the audit pipeline
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: action_profile.ReceiptClass + vault_outbox receipt states
# + seal_chain states. Every action produces a receipt through this lifecycle.


class ReceiptState(StrEnum):
    """Where is this receipt in the audit lifecycle?

    DRAFTED     — Receipt created but not yet submitted.
    ROUTINE     — Standard operation receipt (OBSERVE, ANALYZE).
    SEALED      — Appended to VAULT999. Immutable.
    CONTESTED   — Receipt flagged for review. Under investigation.
    VOID        — Receipt invalidated. Action undone.
    SOVEREIGN   — F13-ratified decision. Special authority level.
    """

    DRAFTED = "DRAFTED"
    ROUTINE = "ROUTINE"
    SEALED = "SEALED"
    CONTESTED = "CONTESTED"
    VOID = "VOID"
    SOVEREIGN = "SOVEREIGN"
    UNKNOWN = "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# 9. TOOL AFFORDANCE STATE — Tool surface status
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: A-FORGE affordances.yaml drift detection + MCP surface audit.
# Every registered tool has exactly one affordance state.


class ToolAffordanceState(StrEnum):
    """Status of a tool in the affordance registry.

    ACTIVE      — Registered, callable, tested.
    DISABLED    — Registered but not currently callable (missing credentials, down).
    DEPRECATED  — Scheduled for removal. Still callable but warns.
    PHANTOM     — Listed in affordances but NOT in live registry. Needs cleanup.
    BLOCKED     — Blocked by governance policy. Requires 888_HOLD to unblock.
    HIDDEN      — Exists in registry but excluded from tools/list (internal use).
    """

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DEPRECATED = "DEPRECATED"
    PHANTOM = "PHANTOM"
    BLOCKED = "BLOCKED"
    HIDDEN = "HIDDEN"
    UNKNOWN = "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# 10. EVIDENCE SOURCE RANK — Priority ranking for evidence source types
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated from: epistemic_tag.EvidenceSource + WEALTH source ranking.
# Higher rank = more authoritative. Used for conflict resolution.


class EvidenceSourceRank(StrEnum):
    """Priority ranking for evidence sources.

    MEASURED         — Live probe, sensor, direct observation. HIGHEST.
    COMPUTED         — Derived from deterministic computation (NPV, volume).
    RETRIEVED        — From storage (database, vault, cache). Trust depends on write path.
    EXTERNAL_API     — From third-party API. Moderate trust.
    AI_SYNTHESIZED   — Generated by AI/LLM. LOWEST. Never enters vault.
    HUMAN_REPORTED   — Self-reported by human. Moderate trust.
    UNKNOWN          — No source identified. Treat as LOWEST.
    """

    MEASURED = "MEASURED"
    COMPUTED = "COMPUTED"
    RETRIEVED = "RETRIEVED"
    EXTERNAL_API = "EXTERNAL_API"
    HUMAN_REPORTED = "HUMAN_REPORTED"
    AI_SYNTHESIZED = "AI_SYNTHESIZED"
    UNKNOWN = "UNKNOWN"


EVIDENCE_SOURCE_RANK_ORDER = [
    EvidenceSourceRank.UNKNOWN,
    EvidenceSourceRank.AI_SYNTHESIZED,
    EvidenceSourceRank.EXTERNAL_API,
    EvidenceSourceRank.HUMAN_REPORTED,
    EvidenceSourceRank.RETRIEVED,
    EvidenceSourceRank.COMPUTED,
    EvidenceSourceRank.MEASURED,
]


# ═══════════════════════════════════════════════════════════════════════════════
# 11. INTENT CLASS — What shape is this agent output?
# ═══════════════════════════════════════════════════════════════════════════════

# QQQ Recommendation Doctrine v1.0 (2026-07-14).
# Gates when QQQ discipline triggers. Only RECOMMENDATION, DECISION, VERDICT
# require QQQ envelope. OBSERVATION, STATUS_REPORT, QUESTION do not.


class IntentClass(StrEnum):
    """Classification of agent output shape for QQQ gating.

    QQQ triggers ONLY on: RECOMMENDATION, DECISION, VERDICT.
    QQQ does NOT trigger on: OBSERVATION, STATUS_REPORT, QUESTION.

    This is the gate that prevents QQQ from becoming noise on every message.
    """

    OBSERVATION = "OBSERVATION"  # no QQQ — pure observation
    STATUS_REPORT = "STATUS_REPORT"  # no QQQ — state update
    QUESTION = "QUESTION"  # no QQQ — inquiry, not recommendation
    RECOMMENDATION = "RECOMMENDATION"  # QQQ mandatory
    DECISION = "DECISION"  # QQQ mandatory
    VERDICT = "VERDICT"  # QQQ mandatory
    UNKNOWN = "UNKNOWN"  # fail-closed: unknown = no QQQ (but flagged)


# QQQ-required intents
QQQ_REQUIRED_INTENTS = {
    IntentClass.RECOMMENDATION,
    IntentClass.DECISION,
    IntentClass.VERDICT,
}


def requires_qqq(intent: IntentClass) -> bool:
    """Does this intent class require QQQ discipline?"""
    return intent in QQQ_REQUIRED_INTENTS


# ═══════════════════════════════════════════════════════════════════════════════
# 12. QQQ PATH CATEGORY — Classification of recommendation paths
# ═══════════════════════════════════════════════════════════════════════════════

# QQQ Recommendation Doctrine v1.0, Q1 layer.
# Every path in a QQQ envelope must carry exactly one category.


class PathCategory(StrEnum):
    """Category of a recommendation path in QQQ Q1 enumeration.

    CONSERVATIVE — Safe, proven, slow. Low blast radius.
    AGGRESSIVE   — Fast, bold, higher risk. Higher blast radius.
    NULL         — Do nothing. ALWAYS required. Tests action bias.
    INVERSE      — Do the opposite. ALWAYS required. Tests pattern lock-in.
    LATERAL      — Creative, unexpected, orthogonal. Surfaces hidden options.
    """

    CONSERVATIVE = "CONSERVATIVE"
    AGGRESSIVE = "AGGRESSIVE"
    NULL = "NULL"
    INVERSE = "INVERSE"
    LATERAL = "LATERAL"


# Mandatory categories — Q1 requires NULL and INVERSE
QQQ_MANDATORY_CATEGORIES = {PathCategory.NULL, PathCategory.INVERSE}


# ═══════════════════════════════════════════════════════════════════════════════
# 13. QQQ PRIOR ART — Availability of prior precedent
# ═══════════════════════════════════════════════════════════════════════════════

# QQQ Recommendation Doctrine v1.0, Q2 layer.
# Per-path metric indicating whether prior precedent exists.


class PriorArt(StrEnum):
    """Prior-art availability for a QQQ recommendation path.

    STRONG — This path has been taken before with documented outcomes.
    WEAK   — Similar paths exist but not exact match.
    NONE   — No precedent. First-time path. Higher uncertainty.
    """

    STRONG = "STRONG"
    WEAK = "WEAK"
    NONE = "NONE"


# ═══════════════════════════════════════════════════════════════════════════════
# 14. QQQ COMPLIANCE — Envelope completeness state
# ═══════════════════════════════════════════════════════════════════════════════

# QQQ Recommendation Doctrine v1.0, Section 5.
# INADMISSIBLE labels never suppress — they surface with a scar.


class QQQCompliance(StrEnum):
    """QQQ envelope compliance state.

    COMPLETE          — All three Q layers present and valid. Admissible.
    INADMISSIBLE_Q1   — Option space incomplete (< 5 paths, or NULL/INVERSE missing).
    INADMISSIBLE_Q2   — Quantitative metrics missing or unmeasured.
    INADMISSIBLE_Q3   — Quantum analysis missing or incomplete.
    NOT_REQUIRED      — Intent class does not require QQQ (OBSERVATION, STATUS_REPORT, QUESTION).
    """

    COMPLETE = "COMPLETE"
    INADMISSIBLE_Q1 = "INADMISSIBLE-Q1"
    INADMISSIBLE_Q2 = "INADMISSIBLE-Q2"
    INADMISSIBLE_Q3 = "INADMISSIBLE-Q3"
    NOT_REQUIRED = "NOT_REQUIRED"


def is_admissible(compliance: QQQCompliance) -> bool:
    """Is this QQQ envelope admissible for recommendation?"""
    return compliance == QQQCompliance.COMPLETE


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE HELPERS — Validation functions combining multiple enums
# ═══════════════════════════════════════════════════════════════════════════════


def validate_verdict_executable(verdict: Verdict) -> bool:
    """Can this verdict proceed to execution?"""
    return VERDICT_EXECUTION_MAP.get(verdict, False)


def validate_session_for_lane(session_state: SessionState, lane: GovernanceLane) -> bool:
    """Does the session authority meet the lane's minimum requirement?"""
    required = LANE_MINIMUM_SESSION.get(lane, SessionState.OBSERVE_ONLY)
    try:
        return SESSION_STATE_ORDER.index(session_state) >= SESSION_STATE_ORDER.index(required)
    except ValueError:
        return False


def confidence_from_epistemic(tag: EpistemicTag) -> ConfidenceLevel:
    """Derive default confidence level from epistemic tag.

    OBSERVED    → HIGH
    DERIVED     → MODERATE
    INTERPRETED → LOW
    SPECULATED  → LOW
    ASSUMED     → UNKNOWN
    """
    mapping = {
        EpistemicTag.OBSERVED: ConfidenceLevel.HIGH,
        EpistemicTag.DERIVED: ConfidenceLevel.MODERATE,
        EpistemicTag.INTERPRETED: ConfidenceLevel.LOW,
        EpistemicTag.SPECULATED: ConfidenceLevel.LOW,
        EpistemicTag.ASSUMED: ConfidenceLevel.UNKNOWN,
    }
    return mapping.get(tag, ConfidenceLevel.UNKNOWN)


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA VERSION — Bump this on any breaking change to enum values
# ═══════════════════════════════════════════════════════════════════════════════

FEDERATION_ENUMS_SCHEMA_VERSION = "2.0.0"
FEDERATION_ENUMS_LAST_UPDATED = "2026-07-14"
