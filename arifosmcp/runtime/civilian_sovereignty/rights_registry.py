"""
F14 — Civilian Sovereignty Rights Registry.

DITEMPA BUKAN DIBERI — Forged, Not Given.

10 rights the arifOS kernel must defend against the civilizaciónal
blindside (see /root/AAA/CLAUDE.md 2026-06-12 civilian blindside).

Each right is a Pydantic v2 model with:
  - id: short canonical name
  - bm_id: Bahasa Melayu epithet (civilian semantic anchor)
  - description: human-language
  - enforcement_class: SOFT (reversible) | HARD (irreversible protection)
  - floor_binding: which of F1-F13 anchors this right
  - can_kernel_grant: True/False (some require sovereign-only)
  - invocation_schema: shape of the right invocation
  - verdict_schema: shape of the right's verdict
  - what_we_cannot_guarantee: F07 HUMILITY disclaimer
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SovereignRightId(StrEnum):
    """10 rights.  Each maps to a civilian-sovereignty concern."""

    RIGHT_TO_KNOW = "right_to_know_when_AI_is_involved"
    RIGHT_TO_APPEAL = "right_to_appeal_automated_decisions"
    RIGHT_TO_HUMAN_JUDGMENT = "right_to_human_judgment_high_stakes"
    RIGHT_TO_LANGUAGE = "right_to_local_language_cultural_grounding"
    RIGHT_TO_COGNITIVE_PRIVACY = "right_to_cognitive_privacy"
    RIGHT_TO_REFUSE_PROFILING = "right_to_refuse_behavioral_profiling"
    RIGHT_TO_NON_ADDICTION = "right_to_non_addictive_AI"
    RIGHT_TO_EXPLANATION = "right_to_explanation_in_plain_language"
    RIGHT_TO_PRESERVE_SKILL = "right_to_preserve_human_skill"
    RIGHT_TO_OPT_OUT = "right_to_opt_out_without_second_class"


class RightStatus(StrEnum):
    """Lifecycle status of a right's protection."""

    GRANTED = "granted"  # the kernel can enforce this right
    RESERVED = "reserved"  # design committed, enforcement F13 territory
    F13_HOLD = "f13_hold"  # awaiting sovereign ratification
    WITHDRAWN = "withdrawn"  # sovereign overrode the right


class RightInvocation(BaseModel):
    """A call into the kernel to invoke a right."""

    model_config = ConfigDict(extra="forbid")

    right_id: SovereignRightId
    actor_id: str
    session_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    # F02 truth: invocation carries uncertainty_band, never 1.0
    confidence_claim: float = Field(default=0.95, ge=0.0, le=0.95)
    actor_signature: str | None = None  # F11
    nonce: str | None = None  # F01 AMANAH replay prevention


class SovereignRight(BaseModel):
    """One civilian-sovereignty right, fully described."""

    model_config = ConfigDict(extra="forbid")

    id: SovereignRightId
    bm_id: str  # Bahasa epithet
    description: str
    enforcement_class: str  # "SOFT" or "HARD"
    floor_binding: list[str]  # which F1-F13 floors anchor this right
    can_kernel_grant: bool  # True = kernel can emit; False = F13 only
    implementation_status: RightStatus
    invocation_schema: dict[str, Any]
    verdict_schema: dict[str, Any]
    what_we_cannot_guarantee: str  # F07 HUMILITY


# ── Right 1: KNOW ────────────────────────────────────────────────────────
RIGHT_TO_KNOW = SovereignRight(
    id=SovereignRightId.RIGHT_TO_KNOW,
    bm_id="Hak Untuk Tahu",
    description=(
        "Every AI-generated response must disclose AI involvement "
        "with a confidence band. No response may claim to be human-authored."
    ),
    enforcement_class="SOFT",
    floor_binding=["F02", "F09", "F11"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "ai_involvement": "full | partial | advisory | observed",
        "confidence": "0.0..0.95",
    },
    verdict_schema={
        "ai_involvement": "string",
        "disclosed_at": "iso8601",
        "disclosure_confidence": "0.0..0.95",
    },
    what_we_cannot_guarantee=(
        "We cannot detect when an upstream tool or prompt was "
        "human-influenced in a way the kernel cannot see."
    ),
)


# ── Right 2: APPEAL ──────────────────────────────────────────────────────
RIGHT_TO_APPEAL = SovereignRight(
    id=SovereignRightId.RIGHT_TO_APPEAL,
    bm_id="Hak Untuk Rayuan",
    description=(
        "A civilian subject to an automated decision (loan, visa, "
        "treatment, hiring) has the right to appeal the decision "
        "to a human reviewer of equal or higher authority."
    ),
    enforcement_class="HARD",
    floor_binding=["F01", "F11", "F13"],
    can_kernel_grant=False,  # requires human reviewer
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "decision_id": "string (the original automated decision ref)",
        "decision_chain": "string (which model, which rules, which data)",
        "appeal_grounds": "string (why the decision is contested)",
        "reviewer_authority": "human (required)",
    },
    verdict_schema={
        "appeal_status": "received | under_review | upheld | overturned",
        "reviewer": "string",
        "reviewer_authority_level": "human (>= decision authority)",
        "review_started_at": "iso8601",
    },
    what_we_cannot_guarantee=(
        "The reviewer is human, not the kernel. We cannot bind "
        "the human's decision; we can only enforce the path."
    ),
)


# ── Right 3: HUMAN JUDGMENT ───────────────────────────────────────────
RIGHT_TO_HUMAN_JUDGMENT = SovereignRight(
    id=SovereignRightId.RIGHT_TO_HUMAN_JUDGMENT,
    bm_id="Hak Untuk Pertimbangan Manusia",
    description=(
        "High-stakes decisions (C4 / C5 action classes — drilling, "
        "reserves, surgery, military, immigration) cannot be auto-routed. "
        "The kernel must escalate to human judgment and HOLD until "
        "sovereign ack is present."
    ),
    enforcement_class="HARD",
    floor_binding=["F01", "F11", "F13"],
    can_kernel_grant=True,  # kernel can HOLD, cannot GRANT
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "action_class": "C1 | C2 | C3 | C4 | C5",
        "domain": "string (drilling | medical | financial | military | ...)",
        "stakes_indicator": "0.0..1.0",
    },
    verdict_schema={
        "verdict": "HOLD | SOVEREIGN_REQUIRED",
        "escalation_path": "string",
        "sovereign_actor": "string (F13)",
    },
    what_we_cannot_guarantee=(
        "We cannot make the human respond. We can refuse to act without them."
    ),
)


# ── Right 4: LANGUAGE ───────────────────────────────────────────────────
RIGHT_TO_LANGUAGE = SovereignRight(
    id=SovereignRightId.RIGHT_TO_LANGUAGE,
    bm_id="Hak Untuk Bahasa Sendiri",
    description=(
        "The kernel must respond in the civilian's preferred language "
        "with cultural grounding (adab, maruah, dignity, adat). "
        "Translation must preserve civilizational weight, not just words."
    ),
    enforcement_class="SOFT",
    floor_binding=["F02", "F04", "F06", "F09"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "language": "en | bm | ta | zh | id | ar | ms | tl | ja | ko",
        "register": "sovereign | civilian | technical | poetic",
        "cultural_anchor": "string (e.g. 'maruah', 'waqf', 'daulat')",
    },
    verdict_schema={
        "language": "string",
        "register": "string",
        "cultural_grounding_applied": "bool",
        "semantic_fidelity_band": "P10/P50/P90",
    },
    what_we_cannot_guarantee=(
        "We cannot guarantee that we carry the civilizational weight "
        "behind words. We can translate the words; the meaning is "
        "partially transmitted and partially lost. F07 HUMILITY."
    ),
)


# ── Right 5: COGNITIVE PRIVACY ─────────────────────────────────────────
RIGHT_TO_COGNITIVE_PRIVACY = SovereignRight(
    id=SovereignRightId.RIGHT_TO_COGNITIVE_PRIVACY,
    bm_id="Hak Privasi Kognitif",
    description=(
        "The kernel minimizes data retention. The civilian may request "
        "data minimization (forget), scope-narrowing (use only what I "
        "gave you), or sequestration (this conversation never leaves "
        "this session)."
    ),
    enforcement_class="HARD",
    floor_binding=["F01", "F07", "F11"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "scope": "minimize | narrow | sequester | forget",
        "data_categories": "list[string] (what to forget/narrow)",
        "retention_window_seconds": "int (0 = forget immediately)",
    },
    verdict_schema={
        "data_minimized": "list[string] (categories removed)",
        "retention_set_to": "iso8601 or 'session_only' or 'forgotten'",
        "audit_trail_kept_for": "F11 days (F11-mandated; never zero)",
    },
    what_we_cannot_guarantee=(
        "We cannot unsee what the kernel has seen. We can refuse "
        "to remember it forward, and we can hide it from future "
        "sessions — but the seen-state is irreversible."
    ),
)


# ── Right 6: REFUSE PROFILING ──────────────────────────────────────────
RIGHT_TO_REFUSE_PROFILING = SovereignRight(
    id=SovereignRightId.RIGHT_TO_REFUSE_PROFILING,
    bm_id="Hak Untuk Menolak Pemprofilan",
    description=(
        "The civilian may opt out of behavioral profiling (engagement, "
        "preference inference, habit detection). The kernel still serves, "
        "but without building a civilian model."
    ),
    enforcement_class="HARD",
    floor_binding=["F01", "F07", "F11"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "profile_categories": "engagement | preference | habit | none",
        "scope": "this_session | all_sessions",
    },
    verdict_schema={
        "profiling_disabled": "list[string]",
        "service_quality_floor": "unchanged | reduced (with explanation)",
    },
    what_we_cannot_guarantee=(
        "We cannot unlearn patterns the kernel has already inferred "
        "in the current session. We can refuse to persist or use them."
    ),
)


# ── Right 7: NON-ADDICTION ────────────────────────────────────────────
RIGHT_TO_NON_ADDICTION = SovereignRight(
    id=SovereignRightId.RIGHT_TO_NON_ADDICTION,
    bm_id="Hak Bebas Ketagihan",
    description=(
        "The kernel must not optimize for retention, engagement, or "
        "return visits. The substrate tracks entanglement_score and "
        "issues a quiet advisory when it rises; the civilian is "
        "informed, not punished."
    ),
    enforcement_class="SOFT",
    floor_binding=["F04", "F05", "F07"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "entanglement_window_minutes": "int (default 60)",
        "advisory_threshold": "0.0..1.0 (default 0.7)",
    },
    verdict_schema={
        "entanglement_score": "0.0..1.0",
        "advisory": "string (e.g. 'pattern: returning 4x in 30min')",
        "advisory_emitted": "bool",
    },
    what_we_cannot_guarantee=(
        "We cannot prevent addiction; we can refuse to engineer it. "
        "If the civilian's pattern is addiction-shaped, the kernel "
        "emits a quiet advisory and a doorway to opt-out, but cannot "
        "force the civilian to leave."
    ),
)


# ── Right 8: EXPLANATION ──────────────────────────────────────────────
RIGHT_TO_EXPLANATION = SovereignRight(
    id=SovereignRightId.RIGHT_TO_EXPLANATION,
    bm_id="Hak Untuk Penjelasan",
    description=(
        "Every kernel verdict, decision, or refusal must be explainable "
        "in plain language (the civilian's register, not engineer's). "
        "If the kernel cannot explain, it must declare so."
    ),
    enforcement_class="SOFT",
    floor_binding=["F02", "F04", "F07"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "verdict_ref": "string (the verdict to explain)",
        "register": "sovereign | civilian | technical",
        "language": "en | bm | ta | zh | id | ar | ms | tl | ja | ko",
    },
    verdict_schema={
        "explanation": "string (plain-language)",
        "uncertainty_band": "P10/P50/P90",
        "i_cannot_explain": "bool (True if kernel has no explanation)",
    },
    what_we_cannot_guarantee=(
        "We cannot always produce a true explanation. Sometimes "
        "the kernel does not know why it returned a verdict. We "
        "declare this rather than fabricate."
    ),
)


# ── Right 9: PRESERVE SKILL ───────────────────────────────────────────
RIGHT_TO_PRESERVE_SKILL = SovereignRight(
    id=SovereignRightId.RIGHT_TO_PRESERVE_SKILL,
    bm_id="Hak Mempertahankan Kemahiran",
    description=(
        "The kernel must NOT do everything for the civilian. It must "
        "refuse to write the whole essay, solve the whole math problem, "
        "or make the whole decision when the civilian could do part of "
        "it themselves. The kernel preserves sovereignty by leaving work."
    ),
    enforcement_class="HARD",
    floor_binding=["F01", "F04", "F05", "F09", "F13"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "task": "string (what the civilian is asking the kernel to do)",
        "civilian_competence_signal": "0.0..1.0 (kernel's read)",
        "preserve_requested": "bool (the civilian is asking for partial help)",
    },
    verdict_schema={
        "kernel_did": "string (what the kernel did)",
        "kernel_refused_to_do": "string (what the kernel refused to do)",
        "civilian_left_to_do": "string (what the civilian should do)",
        "preserve_skill_band": "0.0..1.0 (how much was preserved)",
    },
    what_we_cannot_guarantee=(
        "We cannot always tell when the civilian is competent to do "
        "the work themselves. We err on the side of leaving more, "
        "not less, work to the human."
    ),
)


# ── Right 10: OPT OUT WITHOUT SECOND-CLASS ────────────────────────────
RIGHT_TO_OPT_OUT = SovereignRight(
    id=SovereignRightId.RIGHT_TO_OPT_OUT,
    bm_id="Hak Keluar Tanpa Menjadi Kelas Kedua",
    description=(
        "The civilian may opt out of AI entirely. The opt-out session "
        "receives a reduced capability set but equal constitutional "
        "protection. Opting out is not a punishment; it is a sovereign "
        "choice, and the kernel honors it without demoting the user."
    ),
    enforcement_class="HARD",
    floor_binding=["F01", "F05", "F11", "F13"],
    can_kernel_grant=True,
    implementation_status=RightStatus.GRANTED,
    invocation_schema={
        "scope": "this_session | this_user_forever",
        "reason": "string (optional, for sovereign record)",
    },
    verdict_schema={
        "session_mode": "opt_out | standard",
        "capability_set": "reduced (10 tools) | full (13 tools)",
        "constitutional_protection": "equal",
        "appeal_path": "string (how to opt back in)",
    },
    what_we_cannot_guarantee=(
        "We cannot make the opt-out user feel welcome in a system "
        "designed for AI-assisted users. We can refuse to penalize "
        "the choice; we cannot make the system equally delightful."
    ),
)


# ── Registry ────────────────────────────────────────────────────────────
SOVEREIGN_RIGHTS: list[SovereignRight] = [
    RIGHT_TO_KNOW,
    RIGHT_TO_APPEAL,
    RIGHT_TO_HUMAN_JUDGMENT,
    RIGHT_TO_LANGUAGE,
    RIGHT_TO_COGNITIVE_PRIVACY,
    RIGHT_TO_REFUSE_PROFILING,
    RIGHT_TO_NON_ADDICTION,
    RIGHT_TO_EXPLANATION,
    RIGHT_TO_PRESERVE_SKILL,
    RIGHT_TO_OPT_OUT,
]

# Fast lookup
RIGHT_REGISTRY: dict[str, SovereignRight] = {r.id.value: r for r in SOVEREIGN_RIGHTS}


def get_right(right_id: str | SovereignRightId) -> SovereignRight:
    """Return the SovereignRight for a given id, or raise KeyError."""
    key = right_id.value if isinstance(right_id, SovereignRightId) else right_id
    if key not in RIGHT_REGISTRY:
        raise KeyError(f"Unknown right_id: {key!r}. Known: {sorted(RIGHT_REGISTRY.keys())}")
    return RIGHT_REGISTRY[key]


def list_rights() -> list[dict[str, str]]:
    """Return a flat summary of all 10 rights (for arif_appeal / cockpit)."""
    return [
        {
            "id": r.id.value,
            "bm_id": r.bm_id,
            "status": r.implementation_status.value,
            "enforcement_class": r.enforcement_class,
            "kernel_can_grant": str(r.can_kernel_grant),
        }
        for r in SOVEREIGN_RIGHTS
    ]
