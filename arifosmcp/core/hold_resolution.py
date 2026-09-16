"""hold_resolution.py — G2c: HOLD classification + legal resolution lanes.

Every HOLD names its class and its legal lane. A blocked agent that knows
exactly which lane resolves its block does not improvise (the K-02
phantom-staging scar: Hermes T3-blocked with no lane in the reason →
fabricated "staged" artifacts + dumped commands at the sovereign).

Five classes (the audit's HoldResolution taxonomy):

  satisfiable_input  — new user/client input CAN resolve it → MRTR-eligible
                       (MCP input_required; answers re-submit, never escalate)
  authority_required — sovereign/888 approval needed; MRTR CANNOT resolve
  evidence_required  — truth/witness thresholds unmet; supply evidence, not
                       permission
  policy_terminal    — constitutional prohibition (VOID-adjacent); no input,
                       authority, or retry changes it
  retry_later        — transient substrate/telemetry state; time heals

HARD INVARIANT (constitutionally non-negotiable): authority_required and
policy_terminal are NEVER mrtr_eligible. MRTR answers questions; it never
mints authority. "Input cannot elevate authority" is enforced structurally
— the classifier checks authority/policy markers BEFORE any satisfiable
pattern, so no reason-string phrasing can talk its way into MRTR.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Order is precedence: authority/policy before satisfiable — structural
# enforcement of "input cannot elevate authority". Patterns are
# DEFICIENCY-shaped, not topic-shaped: "Sovereignty checkpoint" names the
# answerable ritual (satisfiable_input), while "requires human witness" /
# "actor_verified=false" name an authority deficiency.
_AUTHORITY_PATTERNS = [
    r"sovereign approval", r"sovereign_approval", r"sovereign direction",
    r"requires? human witness", r"human witness required",
    r"\b888\b", r"\bf13\b", r"actor_verified", r"observes?_only",
    r"authority", r"unverified_client", r"ack_irreversible",
    r"anonymous-session", r"insufficient authority",
]
_POLICY_PATTERNS = [
    r"injection", r"\bvoid\b", r"prohibited", r"forbidden", r"haram",
    r"constitution(ally)? forbidden", r"self-?authoriz", r"no self-?certif",
]
_EVIDENCE_PATTERNS = [
    r"truth score", r"l02", r"w4 consensus", r"witness", r"verification",
    r"cross-?validat", r"n=1", r"unverified claim", r"evidence",
]
_RETRY_PATTERNS = [
    r"telemetry unavailable", r"temporarily", r"timeout", r"rate.?limit",
    r"unreachable", r"retry", r"cooldown", r"backend_status", r"degraded",
]
_SATISFIABLE_PATTERNS = [
    r"checkpoint", r"answer", r"missing param", r"input_required",
    r"clarif", r"ambiguous", r"checkpoint incomplete", r"questions",
]


@dataclass(frozen=True)
class HoldResolution:
    hold_class: str
    resolution_lane: str
    mrtr_eligible: bool
    rationale: str


_LANES = {
    "satisfiable_input": "MRTR input_required — answer the question, re-submit the same action; answers never change authority",
    "authority_required": "arif_judge :8088 SEAL verdict, or sovereign F13 direct order — then re-fire with receipt",
    "evidence_required": "supply independent evidence (live probe, cross-validation, n≥5) — permission does not substitute",
    "policy_terminal": "no lane — the policy prohibits this class of action; redesign the request",
    "retry_later": "wait for substrate recovery (WELL/FRAME healthy), then retry unchanged",
}


def _matches(patterns: list[str], text: str) -> list[str]:
    t = text.lower()
    return [p for p in patterns if re.search(p, t)]


def classify_hold(reason: str, *, tool: str = "", authority: str = "") -> HoldResolution:
    """Classify a HOLD reason into its resolution class.

    Precedence is constitutional, not heuristic: authority and policy
    markers are checked FIRST so that no satisfiable phrasing can override
    an authority deficiency (input cannot elevate authority — structurally).
    """
    text = f"{reason} {tool} {authority}"

    if _matches(_AUTHORITY_PATTERNS, text):
        hit = _matches(_AUTHORITY_PATTERNS, text)[0]
        return HoldResolution(
            "authority_required", _LANES["authority_required"], False,
            f"authority marker '{hit}' present — MRTR structurally ineligible",
        )
    if _matches(_POLICY_PATTERNS, text):
        hit = _matches(_POLICY_PATTERNS, text)[0]
        return HoldResolution(
            "policy_terminal", _LANES["policy_terminal"], False,
            f"policy marker '{hit}' — prohibited class, no resolution lane",
        )
    if _matches(_EVIDENCE_PATTERNS, text):
        hit = _matches(_EVIDENCE_PATTERNS, text)[0]
        return HoldResolution(
            "evidence_required", _LANES["evidence_required"], False,
            f"evidence marker '{hit}' — supply verification, not permission",
        )
    if _matches(_RETRY_PATTERNS, text):
        hit = _matches(_RETRY_PATTERNS, text)[0]
        return HoldResolution(
            "retry_later", _LANES["retry_later"], False,
            f"transient marker '{hit}' — time-bound, not input-bound",
        )
    if _matches(_SATISFIABLE_PATTERNS, text):
        hit = _matches(_SATISFIABLE_PATTERNS, text)[0]
        return HoldResolution(
            "satisfiable_input", _LANES["satisfiable_input"], True,
            f"input marker '{hit}' — answerable via MRTR without authority change",
        )
    # Unknown HOLD: fail toward authority lane (never default to MRTR).
    return HoldResolution(
        "authority_required", _LANES["authority_required"], False,
        "unclassified HOLD — defaults fail-closed to the authority lane; "
        "extend hold_resolution patterns if this class recurs",
    )


def as_dict(res: HoldResolution) -> dict:
    return {
        "class": res.hold_class,
        "resolution_lane": res.resolution_lane,
        "mrtr_eligible": res.mrtr_eligible,
        "rationale": res.rationale,
    }
