from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

REQUIRED_TRACE_FIELDS = (
    "actor_id",
    "trace_id",
    "decision_class",
)
DECISION_CLASSES = {"C0", "C1", "C2", "C3", "C4"}
TRACE_PATTERN = re.compile(r"^TRACE-[0-9a-fA-F]{8,64}$")


@dataclass(frozen=True)
class TraceCheck:
    status: str
    violations: list[str]


def validate_trace(payload: Mapping[str, Any], *, consequential: bool = True) -> list[str]:
    violations: list[str] = []

    if consequential:
        for key in REQUIRED_TRACE_FIELDS:
            if not payload.get(key):
                violations.append(f"missing_trace_field:{key}")

    trace_id = str(payload.get("trace_id", "")).strip()
    if trace_id and not TRACE_PATTERN.match(trace_id):
        violations.append("invalid_trace_id_format")

    decision_class = str(payload.get("decision_class", "")).strip().upper()
    if decision_class and decision_class not in DECISION_CLASSES:
        violations.append(f"invalid_decision_class:{decision_class}")

    return violations


def enforce_trace(payload: Mapping[str, Any], *, consequential: bool = True) -> TraceCheck:
    violations = validate_trace(payload, consequential=consequential)
    if violations:
        return TraceCheck(status="HOLD", violations=violations)
    return TraceCheck(status="OK", violations=[])
