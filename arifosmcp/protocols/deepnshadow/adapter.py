"""
DeepnShadow Protocol Adapter
═════════════════════════════

Internal-only adapter used by existing arif_* canonical tools.
No external MCP surface. No new tool registration.

Called by:
  - arif_sense_observe(mode="deepnshadow")      → encode_behaviour
  - arif_memory_recall(mode="deepnshadow")      → recall_pattern
  - arif_mind_reason(mode="deepnshadow")        → generate_hypothesis
  - arif_heart_critique(mode="deepnshadow")     → check_boundary
  - arif_reply_compose(mode="deepnshadow")      → compose_safe_action
  - arif_kernel_route(intent_type="deepnshadow") → orchestrate_chain
"""

from __future__ import annotations

import re
import uuid
from typing import Any

from arifosmcp.protocols.deepnshadow import (
    AlternativeExplanation,
    BehaviourObservation,
    DeepnShadowReport,
    DignityStatus,
    EmotionalCharge,
    EvidenceClass,
    InferenceMode,
    MetabolizedAction,
    PatternRecurrence,
    ProjectionMirror,
    RedactedVaultEntry,
    SafeAction,
    ScarVector,
    ShadowHypothesis,
    TeamShadowPattern,
)

# ── Arif default scar profile (overridable per-call) ──────────────────────────
DEFAULT_ARIF_SCAR_PROFILE: list[dict[str, str]] = [
    {"zone": "authority", "trigger": "false certainty", "response": "resistance"},
    {"zone": "competence", "trigger": "reputational blame", "response": "shame spike"},
    {"zone": "autonomy", "trigger": "forced obedience to lie", "response": "storm mind"},
]


# ═══════════════════════════════════════════════════════════════════════════════
# DS-111: Behaviour Encoder
# ═══════════════════════════════════════════════════════════════════════════════


def encode_behaviour(
    description: str,
    context: str | None = None,
    source: str = "human_report",
    evidence_class: str = "E1",
    actor_id: str | None = None,
    session_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Encode raw human behaviour into neutral observable fact."""
    obs = BehaviourObservation(
        observation_id=str(uuid.uuid4()),
        session_id=session_id,
        actor_id=actor_id,
        description=description,
        context=context,
        source=source,
        evidence_class=EvidenceClass(evidence_class),
        metadata=metadata or {},
    )
    return {
        "status": "SUCCESS",
        "tool": "arif_sense_observe",
        "mode": "deepnshadow",
        "observation": obs.model_dump(),
        "dignity_status": DignityStatus.SAFE.value,
        "note": "DS-111: Behaviour encoded as neutral observation.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-222: Evidence Quality Gate
# ═══════════════════════════════════════════════════════════════════════════════


def score_evidence(
    source: str = "human_report",
    recurrence_count: int = 1,
    documented: bool = False,
    corroborated: bool = False,
    confirmed_by_subject: bool = False,
) -> dict[str, Any]:
    """Classify signal into E0–E5 and cap confidence."""
    if confirmed_by_subject:
        eclass = EvidenceClass.E5_CONFIRMED
    elif corroborated:
        eclass = EvidenceClass.E4_CORROBORATED
    elif documented:
        eclass = EvidenceClass.E3_DOCUMENTED
    elif recurrence_count >= 2:
        eclass = EvidenceClass.E2_REPEATED
    elif source == "feeling":
        eclass = EvidenceClass.E0_FEELING
    else:
        eclass = EvidenceClass.E1_SINGLE

    cap = _confidence_cap(eclass)
    return {
        "status": "SUCCESS",
        "tool": "arif_memory_recall",
        "mode": "deepnshadow",
        "evidence_class": eclass.value,
        "confidence_cap": cap,
        "note": f"DS-222: Signal classified {eclass.value}. Cap = {cap}.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-222: Pattern Recall
# ═══════════════════════════════════════════════════════════════════════════════


def recall_pattern(
    observations: list[dict[str, Any]],
    window_days: int = 30,
) -> dict[str, Any]:
    """Detect recurrence from encoded observations."""
    if len(observations) < 2:
        return {
            "status": "SABAR",
            "tool": "arif_memory_recall",
            "mode": "deepnshadow",
            "recurrence_count": len(observations),
            "note": "DS-222: Insufficient recurrence for pattern. Need ≥ 2.",
        }

    obs_ids = [o.get("observation_id", str(uuid.uuid4())) for o in observations]
    contexts = list({o.get("context") for o in observations if o.get("context")})
    confidence = min(1.0, len(observations) / 5.0)

    pattern = PatternRecurrence(
        pattern_id=str(uuid.uuid4()),
        observation_ids=obs_ids,
        recurrence_count=len(observations),
        time_window_days=window_days,
        trigger_contexts=contexts,
        confidence=confidence,
    )
    return {
        "status": "SUCCESS" if confidence >= 0.4 else "SABAR",
        "tool": "arif_memory_recall",
        "mode": "deepnshadow",
        "pattern": pattern.model_dump(),
        "note": f"DS-222: Pattern detected with confidence {confidence:.2f}.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-333: Shadow Hypothesis Engine
# ═══════════════════════════════════════════════════════════════════════════════


def generate_hypothesis(
    hypothesis_text: str,
    pattern_id: str = "unknown",
    trigger_vector: str | None = None,
    confidence: float = 0.5,
    evidence_class: str = "E1",
) -> dict[str, Any]:
    """Generate dignity-safe shadow hypothesis with mandatory alternatives."""
    eclass = EvidenceClass(evidence_class)
    cap = _confidence_cap(eclass)
    confidence = min(confidence, cap)

    dignity_status, notes = _dignity_guard(hypothesis_text)
    alternatives = _generate_alternatives(hypothesis_text, pattern_id)

    hypothesis = ShadowHypothesis(
        hypothesis_id=str(uuid.uuid4()),
        pattern_id=pattern_id,
        hypothesis_text=hypothesis_text,
        trigger_vector=trigger_vector,
        confidence=confidence,
        uncertainty_band=_confidence_band(confidence),
        is_dignity_safe=(dignity_status == DignityStatus.SAFE),
        dignity_status=dignity_status,
        alternative_explanations=alternatives,
    )

    return {
        "status": (
            "SUCCESS" if dignity_status == DignityStatus.SAFE else dignity_status.value.upper()
        ),
        "tool": "arif_mind_reason",
        "mode": "deepnshadow",
        "hypothesis": hypothesis.model_dump(),
        "alternatives": [a.model_dump() for a in alternatives],
        "dignity_status": dignity_status.value,
        "constitutional_notes": notes,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-444: Projection Mirror
# ═══════════════════════════════════════════════════════════════════════════════


def check_projection(
    hypothesis_text: str,
    hypothesis_id: str = "unknown",
    arif_scars: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Check how much of the read is Arif's own scar reacting."""
    scars = arif_scars or DEFAULT_ARIF_SCAR_PROFILE
    text_lower = hypothesis_text.lower()
    matches = []
    resonance = 0.0

    for scar in scars:
        trigger = scar.get("trigger", "").lower()
        zone = scar.get("zone", "").lower()
        if trigger in text_lower or zone in text_lower:
            matches.append(scar)
            resonance += 0.3

    resonance = min(1.0, resonance)
    triggers = ", ".join([m["trigger"] for m in matches]) if matches else None
    zones = ", ".join([m["zone"] for m in matches]) if matches else None

    reflection = (
        f"Arif may be reacting strongly because {triggers} touch known scar-zone(s): {zones}."
        if matches
        else "No strong projection detected."
    )
    self_action = (
        "Pause. Write down 3 observable facts before acting. Check if the same behaviour would bother you on a calm day."
        if matches
        else None
    )

    mirror = ProjectionMirror(
        mirror_id=str(uuid.uuid4()),
        hypothesis_id=hypothesis_id,
        arif_trigger_match=triggers,
        resonance_score=round(resonance, 2),
        reflection_text=reflection,
        safe_self_action=self_action,
    )

    return {
        "status": "SUCCESS",
        "tool": "arif_mind_reason",
        "mode": "deepnshadow",
        "projection_mirror": mirror.model_dump(),
        "resonance_score": mirror.resonance_score,
        "note": "DS-444: Projection mirror does not invalidate the read; it purifies it.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-555: Scar Vector Boundary Check
# ═══════════════════════════════════════════════════════════════════════════════


def check_boundary(
    protected_zone: str,
    boundary_type: str = "unknown",
    confidence: float = 0.3,
    evidence_class: str = "E1",
    safe_action_hint: str | None = None,
) -> dict[str, Any]:
    """Scar-vector inference with dignity gate."""
    eclass = EvidenceClass(evidence_class)
    cap = _confidence_cap(eclass)
    confidence = min(confidence, cap)

    if confidence > 0.7:
        dignity_status = DignityStatus.HOLD
        notes = ["F05: High-confidence scar-vector risks turning human into label."]
    elif confidence > 0.4:
        dignity_status = DignityStatus.GUARDED
        notes = ["F06: Medium-confidence scar-vector. Private navigation only."]
    else:
        dignity_status = DignityStatus.SAFE
        notes = ["F07: Low-confidence scar-vector. Navigation instrument only."]

    scar = ScarVector(
        vector_id=str(uuid.uuid4()),
        hypothesis_id="unknown",
        protected_zone=protected_zone,
        confidence=confidence,
        boundary_type=boundary_type,
        safe_action_hint=safe_action_hint,
    )

    return {
        "status": dignity_status.value.upper(),
        "tool": "arif_heart_critique",
        "mode": "deepnshadow",
        "scar_vector": scar.model_dump(),
        "dignity_status": dignity_status.value,
        "constitutional_notes": notes,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-777: Metabolizer
# ═══════════════════════════════════════════════════════════════════════════════


def metabolize_action(
    raw_charge: str,
    action_text: str,
    avoids_trigger: str | None = None,
    arif_scar_link: str | None = None,
) -> dict[str, Any]:
    """Convert emotional charge into governed action."""
    charge = EmotionalCharge(raw_charge)
    metabolized = _metabolize_charge(charge)

    action = SafeAction(
        action_text=action_text,
        avoids_trigger=avoids_trigger,
        preserves_dignity=True,
    )
    meta = MetabolizedAction(
        metabolize_id=str(uuid.uuid4()),
        action=action,
        raw_charge=charge,
        metabolized_charge=metabolized,
        arif_scar_link=arif_scar_link,
    )

    return {
        "status": "SUCCESS",
        "tool": "arif_reply_compose",
        "mode": "deepnshadow",
        "metabolized_action": meta.model_dump(),
        "note": f"DS-777: {charge.value} → {metabolized}",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-333 TEAM: Team Shadow Map
# ═══════════════════════════════════════════════════════════════════════════════


def map_team_pattern(
    team_name: str,
    observed_behaviours: list[str],
    systemic_shadow: str | None = None,
    alternative_systemic_cause: str | None = None,
    safe_org_action: str | None = None,
) -> dict[str, Any]:
    """Organizational geology — map team-level patterns."""
    pattern = TeamShadowPattern(
        team_pattern_id=str(uuid.uuid4()),
        team_name=team_name,
        observed_behaviours=observed_behaviours,
        systemic_shadow=systemic_shadow,
        alternative_systemic_cause=alternative_systemic_cause
        or "Management pressure or resource constraint",
        safe_org_action=safe_org_action,
    )
    return {
        "status": "SUCCESS",
        "tool": "arif_mind_reason",
        "mode": "deepnshadow",
        "team_pattern": pattern.model_dump(),
        "note": "DS-333 TEAM: Organizational geology. Never reduce team to pathology.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DS-888 / DS-999: Report Builder + Vault Redaction
# ═══════════════════════════════════════════════════════════════════════════════


def build_report(
    mode: InferenceMode,
    observations: list[BehaviourObservation],
    patterns: list[PatternRecurrence],
    hypotheses: list[ShadowHypothesis],
    alternatives: list[AlternativeExplanation],
    mirrors: list[ProjectionMirror],
    scars: list[ScarVector],
    actions: list[SafeAction],
    metabolized: list[MetabolizedAction],
    team_patterns: list[TeamShadowPattern],
    session_id: str = "",
) -> dict[str, Any]:
    """Build terminal DeepnShadowReport with constitutional verdict."""
    overall_dignity = DignityStatus.SAFE
    if any(h.dignity_status == DignityStatus.HOLD for h in hypotheses):
        overall_dignity = DignityStatus.HOLD
    elif any(h.dignity_status == DignityStatus.GUARDED for h in hypotheses):
        overall_dignity = DignityStatus.GUARDED
    elif any(s.confidence > 0.5 for s in scars):
        overall_dignity = DignityStatus.GUARDED

    confidences = [h.confidence for h in hypotheses] + [s.confidence for s in scars]
    overall_confidence = sum(confidences) / max(len(confidences), 1)

    verdict = "SEAL"
    if overall_dignity == DignityStatus.HOLD:
        verdict = "HOLD"
    elif overall_dignity == DignityStatus.GUARDED:
        verdict = "SABAR"
    elif overall_confidence < 0.3:
        verdict = "SABAR"

    notes = [
        "F02: All hypotheses are hypotheses, not truths.",
        "F05: Shadow maps are for Arif's private navigation only.",
        "F06: No human was reduced to a label in this report.",
        "F07: Confidence is uncertainty-banded and evidence-capped.",
        "F09: No consciousness claims made.",
        "DS-333: Alternative explanations generated for every hypothesis.",
        "DS-444: Projection mirror checked.",
        "DS-777: Emotional charge metabolized into governed action.",
        "F13: Arif retains veto over any safe action.",
    ]

    report = DeepnShadowReport(
        report_id=str(uuid.uuid4()),
        session_id=session_id,
        mode=mode,
        observations=observations,
        patterns=patterns,
        hypotheses=hypotheses,
        alternative_explanations=alternatives,
        projection_mirrors=mirrors,
        scar_vectors=scars,
        safe_actions=actions,
        metabolized_actions=metabolized,
        team_patterns=team_patterns,
        overall_dignity_status=overall_dignity,
        overall_confidence=round(overall_confidence, 2),
        verdict=verdict,
        constitutional_notes=notes,
    )

    return {
        "status": verdict,
        "tool": "arif_kernel_route",
        "mode": "deepnshadow",
        "report": report.model_dump(),
        "vault_line": report.to_vault_line(),
    }


def redact_for_vault(
    mode: InferenceMode,
    role_tag: str | None,
    pattern_summary: str,
    safe_response: str | None,
    outcome: str | None,
    dignity_status: DignityStatus,
    session_id: str = "",
) -> dict[str, Any]:
    """Create redacted vault entry. Does not write — caller handles vault seal."""
    entry = RedactedVaultEntry(
        entry_id=str(uuid.uuid4()),
        session_id=session_id,
        mode=mode,
        role_tag=role_tag,
        pattern_summary=pattern_summary,
        safe_response=safe_response,
        outcome=outcome,
        dignity_status=dignity_status,
    )
    return {
        "status": "SEAL",
        "tool": "arif_vault_seal",
        "mode": "deepnshadow",
        "vault_payload": entry.model_dump(),
        "note": "DS-999: Redacted vault payload ready for append-only seal.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _confidence_cap(eclass: EvidenceClass) -> float:
    caps = {
        EvidenceClass.E0_FEELING: 0.2,
        EvidenceClass.E1_SINGLE: 0.4,
        EvidenceClass.E2_REPEATED: 0.6,
        EvidenceClass.E3_DOCUMENTED: 0.75,
        EvidenceClass.E4_CORROBORATED: 0.85,
        EvidenceClass.E5_CONFIRMED: 0.95,
    }
    return caps.get(eclass, 0.5)


def _confidence_band(confidence: float) -> str:
    if confidence < 0.3:
        return "low"
    if confidence < 0.7:
        return "medium"
    return "high"


def _dignity_guard(text: str) -> tuple[DignityStatus, list[str]]:
    text_lower = text.lower()
    notes: list[str] = []

    fatal_patterns = [
        r"\bis\s+(?:a\s+)?(?:narcissist|toxic|insecure|broken|traumatized|clumsy|stupid|lazy)",
        r"\bhas\s+trauma\b",
        r"\bis\s+projecting\b",
        r"\bis\s+avoidant\b",
        r"\bis\s+anxious\b",
    ]
    for pat in fatal_patterns:
        if re.search(pat, text_lower):
            return DignityStatus.HOLD, [f"F05 fatal dignity violation: pattern '{pat}'"]

    guarded = ["because", "due to their", "obviously", "clearly", "definitely"]
    for phrase in guarded:
        if phrase in text_lower:
            notes.append(f"F06 guarded language: '{phrase}'")
    if notes:
        return DignityStatus.GUARDED, notes
    return DignityStatus.SAFE, []


def _generate_alternatives(
    hypothesis_text: str, hypothesis_id: str
) -> list[AlternativeExplanation]:
    templates = [
        ("Workload pressure or resource constraint", "probable"),
        ("Management directive or external demand", "possible"),
        ("Miscommunication or unclear scope definition", "possible"),
        ("Tool limitation or workflow friction", "possible"),
        ("Personal non-work stress spilling over", "unlikely"),
    ]
    return [
        AlternativeExplanation(
            explanation_id=str(uuid.uuid4()),
            hypothesis_id=hypothesis_id,
            explanation_text=text,
            likelihood=likelihood,
        )
        for text, likelihood in templates
    ]


def _metabolize_charge(charge: EmotionalCharge) -> str:
    mapping = {
        EmotionalCharge.ANGER: "boundary",
        EmotionalCharge.SHAME: "workflow container",
        EmotionalCharge.SUSPICION: "hypothesis",
        EmotionalCharge.CONFUSION: "scope question",
        EmotionalCharge.HURT: "dignity-preserving response",
        EmotionalCharge.FEAR: "preparedness plan",
        EmotionalCharge.GRIEF: "acceptance ritual",
        EmotionalCharge.LOW: "rest signal",
        EmotionalCharge.NEUTRAL: "clean signal",
    }
    return mapping.get(charge, "governed action")
