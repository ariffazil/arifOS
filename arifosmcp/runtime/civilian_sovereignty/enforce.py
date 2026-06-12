"""
F14 — Civilian Sovereignty Enforcement Helpers

DITEMPA BUKAN DIBERI — Forged, Not Given.

Each function in this module corresponds to one of the 10 sovereign
rights. The functions are designed to be CALLED from existing
canonical tools (no new MCP surface, no F13 territory).

Pattern:  each helper takes the existing tool's verdict and enriches
it with the right's metadata. The tool surface stays at 13.
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.civilian_sovereignty.rights_registry import (
    RIGHT_TO_KNOW,
    get_right,
)


# ── Right 1: KNOW ────────────────────────────────────────────────────────
def stamp_ai_involvement(
    verdict: dict[str, Any],
    involvement: str = "full",
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Right #1 — stamp every AI response with disclosure metadata.

    involvement:  full | partial | advisory | observed
    """
    verdict = dict(verdict)  # don't mutate caller
    verdict["ai_involvement"] = {
        "right_id": RIGHT_TO_KNOW.id.value,
        "disclosure": involvement,
        "confidence": max(0.0, min(0.95, confidence)),  # F07: never 1.0
        "what_we_cannot_guarantee": RIGHT_TO_KNOW.what_we_cannot_guarantee,
    }
    return verdict


# ── Right 2: APPEAL ──────────────────────────────────────────────────────
def make_appeal_envelope(
    original_decision_ref: str,
    decision_chain: str,
    appeal_grounds: str,
    actor_id: str,
) -> dict[str, Any]:
    """Right #2 — return the appeal path; kernel does NOT decide."""
    return {
        "right_id": "right_to_appeal_automated_decisions",
        "appeal_path": {
            "step_1": "Submit appeal with grounds + decision_ref",
            "step_2": "Kernel routes to human reviewer of equal authority",
            "step_3": "Reviewer: uphold, overturn, or escalate to F13",
            "kernel_role": "PATH ONLY — kernel does not adjudicate",
        },
        "input": {
            "original_decision_ref": original_decision_ref,
            "decision_chain": decision_chain,
            "appeal_grounds": appeal_grounds,
            "actor_id": actor_id,
        },
        "what_we_cannot_guarantee": get_right(
            "right_to_appeal_automated_decisions"
        ).what_we_cannot_guarantee,
    }


# ── Right 3: HUMAN JUDGMENT ───────────────────────────────────────────
def require_sovereign_judgment(
    action_class: str,
    domain: str = "",
    stakes: float = 0.0,
) -> dict[str, Any] | None:
    """Right #3 — return HOLD envelope if action requires sovereign.

    Returns None for C1/C2/C3 (kernel can grant).
    Returns HOLD envelope for C4/C5.
    """
    high_stakes_classes = {"C4", "C5"}
    if action_class in high_stakes_classes or stakes >= 0.7:
        return {
            "verdict": "HOLD",
            "reason": "F13 SOVEREIGN_REQUIRED",
            "right_id": "right_to_human_judgment_high_stakes",
            "action_class": action_class,
            "domain": domain,
            "stakes_indicator": max(0.0, min(1.0, stakes)),
            "escalation_path": "SOVEREIGN_ACK_REQUIRED",
            "what_we_cannot_guarantee": get_right(
                "right_to_human_judgment_high_stakes"
            ).what_we_cannot_guarantee,
        }
    return None


# ── Right 4: LANGUAGE ───────────────────────────────────────────────────
LANGUAGE_REGISTRY = {
    "en": "English",
    "bm": "Bahasa Melayu",
    "ms": "Bahasa Melayu (alt)",
    "id": "Bahasa Indonesia",
    "ta": "தமிழ் (Tamil)",
    "zh": "中文 (Chinese)",
    "ar": "العربية (Arabic)",
    "tl": "Filipino / Tagalog",
    "ja": "日本語 (Japanese)",
    "ko": "한국어 (Korean)",
}


def stamp_language(
    verdict: dict[str, Any],
    language: str = "en",
    register: str = "civilian",
    cultural_anchor: str = "",
) -> dict[str, Any]:
    """Right #4 — stamp language + register on every reply."""
    if language not in LANGUAGE_REGISTRY:
        language = "en"  # F07: refuse to fail on unknown lang
    verdict = dict(verdict)
    verdict["language_grounding"] = {
        "right_id": "right_to_local_language_cultural_grounding",
        "language": language,
        "language_name": LANGUAGE_REGISTRY[language],
        "register": register,
        "cultural_anchor": cultural_anchor,
        "semantic_fidelity_band": {"P10": 0.55, "P50": 0.75, "P90": 0.88},
        "what_we_cannot_guarantee": get_right(
            "right_to_local_language_cultural_grounding"
        ).what_we_cannot_guarantee,
    }
    return verdict


# ── Right 5: COGNITIVE PRIVACY ─────────────────────────────────────────
def stamp_cognitive_privacy(
    verdict: dict[str, Any],
    scope: str = "minimize",
    categories: list[str] | None = None,
    retention_window_seconds: int = 0,
) -> dict[str, Any]:
    """Right #5 — declare data minimization + retention."""
    if scope not in ("minimize", "narrow", "sequester", "forget"):
        scope = "minimize"  # F07: safest default
    verdict = dict(verdict)
    verdict["cognitive_privacy"] = {
        "right_id": "right_to_cognitive_privacy",
        "scope": scope,
        "data_minimized": categories or [],
        "retention_set_to": (
            "forgotten"
            if scope == "forget"
            else "session-only"
            if scope == "sequester"
            else f"{retention_window_seconds}s"
        ),
        # F11 AUDITABILITY: audit trail is NEVER zero. We can hide
        # the content, but the fact of the request is sealed.
        "audit_trail_kept_for_days": 90,
        "what_we_cannot_guarantee": get_right(
            "right_to_cognitive_privacy"
        ).what_we_cannot_guarantee,
    }
    return verdict


# ── Right 6: REFUSE PROFILING ──────────────────────────────────────────
def stamp_refuse_profiling(
    verdict: dict[str, Any],
    scope: str = "this_session",
) -> dict[str, Any]:
    """Right #6 — civilian opts out of behavioral profiling."""
    if scope not in ("this_session", "all_sessions"):
        scope = "this_session"
    verdict = dict(verdict)
    verdict["profiling_opt_out"] = {
        "right_id": "right_to_refuse_behavioral_profiling",
        "scope": scope,
        "profiling_disabled": ["engagement", "preference", "habit"],
        "service_quality_floor": "unchanged",
        "what_we_cannot_guarantee": get_right(
            "right_to_refuse_behavioral_profiling"
        ).what_we_cannot_guarantee,
    }
    return verdict


# ── Right 7: NON-ADDICTION ────────────────────────────────────────────
def entanglement_score(
    session_call_count: int,
    session_window_minutes: int = 60,
    return_count_today: int = 1,
) -> dict[str, Any]:
    """Right #7 — compute entanglement score + advisory.

    Heuristic:
      0.0–0.4  : normal use
      0.4–0.7  : pattern detected, no advisory
      0.7–1.0  : pattern detected, emit quiet advisory
    """
    density = min(1.0, session_call_count / max(1, session_window_minutes / 5))
    daily_factor = min(1.0, return_count_today / 10.0)
    score = round(0.6 * density + 0.4 * daily_factor, 3)
    advisory_emitted = score >= 0.7
    advisory = None
    if advisory_emitted:
        advisory = (
            f"Pattern: {session_call_count} calls in "
            f"{session_window_minutes}min, {return_count_today} sessions today. "
            "Consider a break, or invoke right_to_opt_out. "
            "The kernel is not engineering your return; it is observing."
        )
    return {
        "right_id": "right_to_non_addictive_AI",
        "entanglement_score": score,
        "advisory_emitted": advisory_emitted,
        "advisory": advisory,
        "band": ("OBSERVED" if score < 0.4 else "NOTED" if score < 0.7 else "QUIET_ADVISORY"),
        "what_we_cannot_guarantee": get_right("right_to_non_addictive_AI").what_we_cannot_guarantee,
    }


# ── Right 8: EXPLANATION ──────────────────────────────────────────────
def stamp_explanation(
    verdict: dict[str, Any],
    explanation: str,
    uncertainty_band: dict[str, float],
    i_cannot_explain: bool = False,
) -> dict[str, Any]:
    """Right #8 — every verdict gets a plain-language explanation."""
    verdict = dict(verdict)
    verdict["plain_explanation"] = {
        "right_id": "right_to_explanation_in_plain_language",
        "explanation": explanation,
        "uncertainty_band": uncertainty_band,  # {P10, P50, P90}
        "i_cannot_explain": i_cannot_explain,
        "what_we_cannot_guarantee": get_right(
            "right_to_explanation_in_plain_language"
        ).what_we_cannot_guarantee,
    }
    return verdict


# ── Right 9: PRESERVE SKILL ───────────────────────────────────────────
def preserve_skill_split(
    task: str,
    kernel_can_do: str,
    kernel_refuses_to_do: str,
    civilian_should_do: str,
    preserve_band: float = 0.5,
) -> dict[str, Any]:
    """Right #9 — declare what the kernel did, what it refused, and
    what the civilian should do themselves.

    preserve_band: 0.0 (kernel did everything) ... 1.0 (kernel
    refused almost everything). Default 0.5 = healthy split.
    """
    if not 0.0 <= preserve_band <= 1.0:
        preserve_band = 0.5  # F07: refuse to fail
    return {
        "right_id": "right_to_preserve_human_skill",
        "task": task,
        "kernel_did": kernel_can_do,
        "kernel_refused_to_do": kernel_refuses_to_do,
        "civilian_left_to_do": civilian_should_do,
        "preserve_skill_band": preserve_band,
        "what_we_cannot_guarantee": get_right(
            "right_to_preserve_human_skill"
        ).what_we_cannot_guarantee,
    }


# ── Right 10: OPT OUT ──────────────────────────────────────────────────
OPT_OUT_CAPABILITY_REDUCTION = {
    "lost_tools": [
        # the 3 lease primitives + 3 forge_*  = 6, but opt-out users
        # still get read-only access to 3 witness tools.
        # The point: opt-out users don't get to write, only to read.
    ],
    "retained_tools": [
        "arif_os_attest",  # witness: is the kernel alive?
        "arif_organ_attest_all",  # witness: who else is here?
        "arif_kernel_route",  # status: what is the state?
    ],
    "rejected_actions": [
        "vault_seal",
        "forge_execute",
        "lease_issue",
        "decision_deliberate",
    ],
}


def stamp_opt_out(
    verdict: dict[str, Any],
    scope: str = "this_session",
    reason: str = "",
) -> dict[str, Any]:
    """Right #10 — civilian opts out; verdict stamps reduced-but-equal."""
    if scope not in ("this_session", "this_user_forever"):
        scope = "this_session"
    verdict = dict(verdict)
    verdict["opt_out"] = {
        "right_id": "right_to_opt_out_without_second_class",
        "scope": scope,
        "reason": reason,
        "capability_set": "reduced (3 witness tools retained)",
        "retained_tools": OPT_OUT_CAPABILITY_REDUCTION["retained_tools"],
        "rejected_actions": OPT_OUT_CAPABILITY_REDUCTION["rejected_actions"],
        "constitutional_protection": "equal — all 13 floors still apply",
        "appeal_path": "session_init(mode='standard') to opt back in",
        "what_we_cannot_guarantee": get_right(
            "right_to_opt_out_without_second_class"
        ).what_we_cannot_guarantee,
    }
    return verdict


# ── Convenience: invoke all 10 at once (for sovereign audit) ──────────
def full_rights_audit(
    actor_id: str,
    session_id: str = "",
) -> dict[str, Any]:
    """Return the full F14 rights matrix for a session. For cockpit."""
    from arifosmcp.runtime.civilian_sovereignty.rights_registry import (
        SOVEREIGN_RIGHTS,
        list_rights,
    )

    return {
        "audit_id": f"f14-audit-{session_id[:16] if session_id else 'global'}",
        "actor_id": actor_id,
        "rights_count": len(SOVEREIGN_RIGHTS),
        "rights_summary": list_rights(),
        "what_we_cannot_guarantee": (
            "This matrix declares the kernel's commitment. It does not "
            "guarantee that every implementation path is bug-free. "
            "F02 TRUTH: status is observed_runtime, not theoretical."
        ),
    }
