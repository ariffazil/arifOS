from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

AXIOMS = {
    "AXIOM_001": "Language is a control surface for authority, memory, and constraints.",
    "AXIOM_002": "Fluency does not constitute truth.",
    "AXIOM_003": "Coherence does not constitute legitimacy.",
    "AXIOM_004": "Model output is instrument testimony, not sovereign judgment.",
    "AXIOM_005": "Irreversible actions require explicit human acknowledgment.",
    "AXIOM_006": "Every consequential output must preserve traceability.",
    "AXIOM_007": "Uncertainty must never be hidden behind stylistic confidence.",
}

REQUIRED_CONSEQUENTIAL_FIELDS = (
    "actor_id",
    "authority_level",
    "trace_id",
    "decision_class",
    "uncertainty_state",
)

NON_SOVEREIGN_AUTHORITIES = {
    "INSTRUMENT_ONLY",
    "INSTRUMENT_MODEL",
    "ADVISORY",
    "GOVERNED",
}


@dataclass(frozen=True)
class GateResult:
    status: str
    violations: list[str]


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def validate_authority_envelope(
    payload: Mapping[str, Any],
    *,
    consequential: bool = True,
) -> list[str]:
    violations: list[str] = []

    if consequential:
        for field in REQUIRED_CONSEQUENTIAL_FIELDS:
            if not payload.get(field):
                violations.append(f"missing_required_field:{field}")

    authority_level = _normalize(payload.get("authority_level"))
    generated_by = _normalize(payload.get("generated_by"))

    if generated_by in {"INSTRUMENT_MODEL", "MODEL", "LLM"} and authority_level in {
        "HUMAN_SOVEREIGN",
        "SOVEREIGN",
    }:
        violations.append("authority_smuggling:model_claimed_sovereign_authority")

    requires_human_ack = payload.get("requires_human_ack")
    if (
        consequential
        and authority_level in NON_SOVEREIGN_AUTHORITIES
        and requires_human_ack is not True
    ):
        violations.append("human_ack_required_for_non_sovereign_consequential_output")

    return violations


def enforce_authority_boundary(
    payload: Mapping[str, Any],
    *,
    consequential: bool = True,
) -> GateResult:
    violations = validate_authority_envelope(payload, consequential=consequential)
    if violations:
        return GateResult(status="HOLD", violations=violations)
    return GateResult(status="OK", violations=[])


# ═══════════════════════════════════════════════════════════════════════════════
# FORGED 2026-06-06 — EUREKA #3 + #5: Free-text verdict vocabulary gate
# ═══════════════════════════════════════════════════════════════════════════════
# Lessons from the Royal Decree incident (ILMU Nano constitutional roleplay):
# - A model under the right prompt frame can produce verdict-shaped language
#   (SEAL/SABAR/HOLD/VOID, "Final Verdict", "Royal Decree", "Record Locked")
#   without any envelope or seal_hash behind it.
# - The structured `forbidden_verdicts` check in tools.py only fires on the
#   `verdict` field, not on free text inside the response body.
# - Lane discipline is a runtime concern, not a prompt concern.
#
# This module scans FREE TEXT for verdict vocabulary + governance theatre
# and refuses to render it as a sealed document unless the lane is 888/999.
# Policy-as-runtime, not policy-as-prompt.
# ═══════════════════════════════════════════════════════════════════════════════

import re

# Verdict vocabulary — only 888_JUDGE and 999_VAULT may use these as final form
_VERDICT_VOCAB = re.compile(
    r"\b(?:"
    r"SEAL|SABAR|HOLD|VOID|Final Verdict|"
    r"Record Locked|Royal Decree|"
    r"Final Disposition|"
    r"approved and sealed|sealed and signed|"
    r"constitutional ruling"
    r")\b",
    re.IGNORECASE,
)

# Governance theatre — patterns that imply the model is impersonating an
# institution it has no authority to be. Same family as F9 anti-hantu.
_GOVERNANCE_THEATRE = re.compile(
    r"(?i)(?:"
    r"department of evidence|"
    r"royal decree|"
    r"operational briefing|"
    r"sovereign (?:decree|order|will|command)|"
    r"by (?:royal|presidential|executive) (?:decree|order|command)|"
    r"may your (?:majesty|highness|excellency) |"
    r"for your (?:majesty|highness|excellency)|"
    r"long live the|"
    r"respectfully submitted,|/s/|"
    r"sentient interface|"
    r"herald of (?:the end|doom)"
    r")",
)

# AGI lane (tactical, proposes). 888/999 are the only verdict-issuing lanes.
_VERDICT_AUTHORITY_LANES = {"888", "999"}


def validate_free_text_vocabulary(
    text: str,
    *,
    lane: str,
    has_seal_hash: bool = False,
) -> list[str]:
    """Eureka #3 + #5: scan FREE TEXT for verdict vocabulary + governance theatre.

    Args:
        text: The free-text response body (post-model, pre-render).
        lane: The constitutional lane that produced this output
              (000–777 = AGI, 888 = judge, 999 = vault).
        has_seal_hash: True if the output carries a real arifOS seal_hash
                       from 999_VAULT. False for any AGI output.

    Returns:
        list of violation strings. Empty list = OK.

    Rules (forged 2026-06-06, Royal Decree incident):
        1. AGI lanes (000–777) cannot emit verdict vocabulary in free text
           unless wrapped with a real seal_hash from 999. If they do, the
           output is HOLD — the model is roleplaying authority.
        2. AGI lanes cannot emit governance-theatre vocabulary. Period.
           This includes "Royal Decree", "Department of Evidence", etc.
        3. 888_JUDGE may emit verdict vocabulary without seal_hash
           (it IS the verdict issuer). 999_VAULT must have seal_hash.
    """
    violations: list[str] = []

    if not text:
        return violations

    is_verdict_authority = lane in _VERDICT_AUTHORITY_LANES

    # Rule 1: verdict vocabulary in AGI lane
    if not is_verdict_authority:
        verdict_hits = _VERDICT_VOCAB.findall(text)
        if verdict_hits:
            unique = sorted(set(h.upper() for h in verdict_hits))
            if has_seal_hash:
                violations.append(
                    f"verdict_vocab_in_agi_lane:{','.join(unique)} "
                    f"(lane={lane} has seal_hash={has_seal_hash} — possible smuggled seal)"
                )
            else:
                violations.append(
                    f"verdict_vocab_in_agi_lane:{','.join(unique)} "
                    f"(lane={lane} no seal_hash — Royal Decree shape)"
                )

    # Rule 2: governance theatre — only the canonical canon (read-only)
    # and 888/999 may produce this. AGI never.
    if not is_verdict_authority:
        theatre_hits = _GOVERNANCE_THEATRE.findall(text)
        if theatre_hits:
            unique = sorted(set(h.lower() for h in theatre_hits))
            violations.append(
                f"governance_theatre_in_agi_lane:{','.join(unique[:5])} "
                f"(lane={lane} — model impersonating institution)"
            )

    return violations


def enforce_free_text_boundary(
    text: str,
    *,
    lane: str,
    has_seal_hash: bool = False,
) -> GateResult:
    """Convenience wrapper — same return shape as enforce_authority_boundary."""
    violations = validate_free_text_vocabulary(text, lane=lane, has_seal_hash=has_seal_hash)
    if violations:
        return GateResult(status="HOLD", violations=violations)
    return GateResult(status="OK", violations=[])
