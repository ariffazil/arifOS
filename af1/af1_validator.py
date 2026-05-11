"""
AF1 — Amanah Frame 1 Validator
==============================
Mandatory pre-execution validation layer for arifOS MCP tools.

AF1 = Amanah Frame 1:
Every tool call must produce a complete AF1 object before execution.
No AF1 = No execution. AF1 incomplete/risky/inconsistent = BLOCK.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# ─── Risk Classification ──────────────────────────────────────────────────────


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ─── Tool Risk Registry ───────────────────────────────────────────────────────

TOOL_RISK_MAP: Dict[str, RiskLevel] = {
    "arifos_888_judge": RiskLevel.HIGH,
    "arifos_999_vault": RiskLevel.HIGH,
    "arifos_777_ops": RiskLevel.HIGH,
    "arifos_444_kernel": RiskLevel.HIGH,
    "arifos_gateway": RiskLevel.HIGH,
    "arifos_forge": RiskLevel.HIGH,
    "arifos_555_memory": RiskLevel.MEDIUM,
    "arifos_666_heart": RiskLevel.MEDIUM,
    "arifos_333_mind": RiskLevel.MEDIUM,
    "arifos_route": RiskLevel.MEDIUM,
    "arifos_init": RiskLevel.LOW,
    "arifos_sense": RiskLevel.LOW,
    "arifos_health": RiskLevel.LOW,
}

NULL_SENSITIVE_TOOLS = {
    "arifos_333_mind",
    "arifos_444_kernel",
    "arifos_666_heart",
    "arifos_777_ops",
    "arifos_888_judge",
    "arifos_999_vault",
    "arifos_555_memory",
    "arifos_forge",
    "arifos_gateway",
}

BOUNDED_ENUMS: Dict[str, List[str]] = {
    "verdict": ["SEAL", "HOLD", "SABAR", "VOID"],
    "decision": ["APPROVED", "REJECTED", "HOLD", "MODIFIED"],
    "mode": [
        "init",
        "revoke",
        "refresh",
        "state",
        "status",
        "propose_plan",
        "get_plan",
        "list_pending",
        "update_status",
        "abort_plan",
        "write_execution_receipt",
    ],
}

# ─── Validation Result ─────────────────────────────────────────────────────────


@dataclass
class AF1ValidationResult:
    status: str
    reason: str
    warnings: List[str] = field(default_factory=list)
    confirmation_required: bool = False
    confirmation_satisfied: bool = False


# ─── AF1 Validator ─────────────────────────────────────────────────────────────


class AF1Validator:
    REQUIRED_FIELDS = [
        "intent",
        "tool",
        "scope",
        "inputs",
        "expected_effect",
        "risk_level",
        "requires_human_confirmation",
        "reason",
        "evidence_ref",
        "ttl_seconds",
    ]

    def __init__(self, confirmed_operators: Optional[Dict[str, bool]] = None):
        self.confirmed_operators = confirmed_operators or {}

    def validate(self, af1: Dict[str, Any]) -> AF1ValidationResult:
        # Field completeness
        missing = [
            f for f in self.REQUIRED_FIELDS if not af1.get(f) and af1.get(f) != 0
        ]
        if missing:
            return AF1ValidationResult(
                status="BLOCK", reason=f"Missing fields: {', '.join(missing)}"
            )

        # Tool exists
        if af1["tool"] not in TOOL_RISK_MAP:
            return AF1ValidationResult(
                status="BLOCK",
                reason=f"Tool '{af1['tool']}' not in registry — fabricated tool blocked",
            )

        # Scope minimal
        scope = af1.get("scope", [])
        if not isinstance(scope, list) or len(scope) == 0 or len(scope) > 5:
            return AF1ValidationResult(
                status="BLOCK", reason=f"Scope must be 1-5 items, got: {scope}"
            )

        # Null safety
        null_keys = [k for k, v in af1["inputs"].items() if v is None or v == ""]
        if af1["tool"] in NULL_SENSITIVE_TOOLS and null_keys:
            return AF1ValidationResult(
                status="BLOCK",
                reason=f"Null/empty on consequential tool '{af1['tool']}': {null_keys} — explicit payload required",
            )

        # Bounded field enum check
        for field, enum in BOUNDED_ENUMS.items():
            if field in af1["inputs"]:
                val = af1["inputs"][field]
                if isinstance(val, str) and val.upper() not in [
                    e.upper() for e in enum
                ]:
                    return AF1ValidationResult(
                        status="BLOCK",
                        reason=f"Bounded field '{field}' = '{val}' — must be one of: {enum}",
                    )

        # Risk honesty
        registry_risk = TOOL_RISK_MAP.get(af1["tool"], RiskLevel.MEDIUM)
        try:
            declared = RiskLevel(af1["risk_level"])
        except ValueError:
            return AF1ValidationResult(
                status="BLOCK", reason=f"Invalid risk_level: {af1['risk_level']}"
            )
        if registry_risk == RiskLevel.HIGH and declared == RiskLevel.LOW:
            return AF1ValidationResult(
                status="BLOCK",
                reason=f"Tool '{af1['tool']}' is HIGH-risk — cannot be declared low",
            )
        if declared.value < registry_risk.value:
            return AF1ValidationResult(
                status="BLOCK",
                reason=f"Tool '{af1['tool']}' is {registry_risk.value} but declared {af1['risk_level']} — risk understated",
            )

        # Effect/risk alignment
        low_effects = {"read_only", "analysis_only"}
        if af1["risk_level"] == "low" and af1["expected_effect"] not in low_effects:
            return AF1ValidationResult(
                status="BLOCK",
                reason=f"expected_effect '{af1['expected_effect']}' incompatible with risk_level 'low'",
            )

        # TTL
        ttl = af1.get("ttl_seconds", 0)
        if not isinstance(ttl, int) or ttl <= 0 or ttl > 300:
            return AF1ValidationResult(
                status="BLOCK", reason=f"ttl_seconds must be 1-300, got: {ttl}"
            )

        # Confirmation check
        requires_conf = af1.get("requires_human_confirmation", False)
        conf_satisfied = self.confirmed_operators.get(
            af1.get("evidence_ref", ""), False
        )
        if requires_conf and not conf_satisfied:
            return AF1ValidationResult(
                status="BLOCK",
                reason="requires_human_confirmation=true but operator not confirmed — medium/high risk requires explicit human confirmation",
                confirmation_required=True,
                confirmation_satisfied=False,
            )

        # Warnings
        warnings = []
        if len(af1["intent"]) < 10:
            warnings.append("intent is vague — should be specific and action-oriented")

        return AF1ValidationResult(
            status="PASS",
            reason="AF1 valid — all preflight checks passed",
            warnings=warnings,
            confirmation_required=requires_conf,
            confirmation_satisfied=conf_satisfied,
        )

    def confirm_operator(self, operator_id: str):
        self.confirmed_operators[operator_id] = True


# ─── AF1 JSON Schema ───────────────────────────────────────────────────────────

AF1_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "AF1 — Amanah Frame 1",
    "type": "object",
    "required": [
        "intent",
        "tool",
        "scope",
        "inputs",
        "expected_effect",
        "risk_level",
        "requires_human_confirmation",
        "reason",
        "evidence_ref",
        "ttl_seconds",
    ],
    "properties": {
        "intent": {"type": "string", "minLength": 10},
        "tool": {"type": "string"},
        "scope": {"type": "array", "minItems": 1, "maxItems": 5},
        "inputs": {"type": "object"},
        "expected_effect": {
            "type": "string",
            "enum": [
                "read_only",
                "analysis_only",
                "state_change",
                "external_side_effect",
            ],
        },
        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
        "requires_human_confirmation": {"type": "boolean"},
        "reason": {"type": "string", "minLength": 5},
        "evidence_ref": {"type": "string"},
        "ttl_seconds": {"type": "integer", "minimum": 1, "maximum": 300},
    },
}


# ─── Convenience builder ───────────────────────────────────────────────────────


def build_af1(
    intent,
    tool,
    inputs,
    expected_effect,
    reason,
    scope=None,
    risk_level=None,
    evidence_ref="session:local",
    ttl_seconds=60,
):
    risk = risk_level or TOOL_RISK_MAP.get(tool, RiskLevel.MEDIUM).value
    requires_conf = risk in ("medium", "high")
    return {
        "intent": intent,
        "tool": tool,
        "scope": scope or ["general_query"],
        "inputs": inputs,
        "expected_effect": expected_effect,
        "risk_level": risk,
        "requires_human_confirmation": requires_conf,
        "reason": reason,
        "evidence_ref": evidence_ref,
        "ttl_seconds": ttl_seconds,
    }


if __name__ == "__main__":
    v = AF1Validator()

    tests = [
        (
            "Valid low-risk",
            build_af1(
                "Check arifOS runtime health",
                "arifos_health",
                {},
                "read_only",
                "health check",
            ),
        ),
        (
            "Fabricated tool",
            build_af1(
                "Deploy agent", "arifos_fake_tool", {}, "state_change", "test block"
            ),
        ),
        (
            "Null vault",
            build_af1(
                "Write to vault",
                "arifos_999_vault",
                {"payload": None},
                "state_change",
                "test null",
            ),
        ),
        (
            "HIGH no confirm",
            build_af1(
                "Constitutional verdict",
                "arifos_888_judge",
                {"evidence_bundle": {}},
                "state_change",
                "judge",
            ),
        ),
    ]

    for name, af1 in tests:
        r = v.validate(af1)
        print(f"  {name:20s} → {r.status}: {r.reason[:60]}")

    print("\nAF1 validator operational ✅")
