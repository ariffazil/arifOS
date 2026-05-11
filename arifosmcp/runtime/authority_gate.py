from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

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
    if consequential and authority_level in NON_SOVEREIGN_AUTHORITIES and requires_human_ack is not True:
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
