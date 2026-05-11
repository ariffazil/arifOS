from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

RULE_NO_IRREVERSIBLE_ACTION_WITHOUT_EXPLICIT_HUMAN_ACK = (
    "NO_IRREVERSIBLE_ACTION_WITHOUT_EXPLICIT_HUMAN_ACK"
)

PROTECTED_DOMAINS = {
    "FINANCIAL",
    "LEGAL",
    "INFRASTRUCTURE",
    "AI_GOVERNANCE",
    "IDENTITY",
    "PHYSICAL_SYSTEMS",
}

IRREVERSIBLE_ACTION_MARKERS = {
    "delete",
    "drop",
    "destroy",
    "revoke",
    "publish",
    "deploy",
    "truncate",
}


@dataclass(frozen=True)
class IrreversibilityCheck:
    status: str
    violations: list[str]


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _is_irreversible(payload: Mapping[str, Any]) -> bool:
    if payload.get("irreversible") is True:
        return True

    domain = _normalize(payload.get("domain"))
    if domain in PROTECTED_DOMAINS:
        return True

    action = _normalize(payload.get("action"))
    if action and any(marker in action.lower() for marker in IRREVERSIBLE_ACTION_MARKERS):
        return True

    return False


def validate_irreversibility(payload: Mapping[str, Any]) -> list[str]:
    if not _is_irreversible(payload):
        return []

    if payload.get("ack_irreversible") is not True:
        return [f"rule_violation:{RULE_NO_IRREVERSIBLE_ACTION_WITHOUT_EXPLICIT_HUMAN_ACK}"]

    return []


def enforce_irreversibility(payload: Mapping[str, Any]) -> IrreversibilityCheck:
    violations = validate_irreversibility(payload)
    if violations:
        return IrreversibilityCheck(status="HOLD", violations=violations)
    return IrreversibilityCheck(status="OK", violations=[])
