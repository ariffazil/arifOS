"""
PR5 — Receipt classes for the Capital Judge.

Audit-4 mandates 4 disjoint receipt types. NEVER collapsed into one SEAL.
Each receipt class validates its own shape against /runtime/contracts/receipt.schema.json.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, ClassVar

from .state_machine import CapitalCase, Receipt, _hash, _now


def _required_fields(d: dict[str, Any], fields: list[str]) -> None:
    missing = [f for f in fields if f not in d]
    if missing:
        raise ValueError(f"receipt missing required fields: {missing}")


@dataclass
class ComputationReceipt(Receipt):
    """COMPUTATION receipt — what WEALTH produced, with hashes for replay."""

    receipt_type: ClassVar[str] = "COMPUTATION"
    required_fields: ClassVar[list[str]] = [
        "receipt_type", "input_hash", "output_hash",
        "wealth_version", "tool_versions", "status",
    ]

    def __init__(
        self,
        *,
        case: CapitalCase,
        output: dict[str, Any],
        wealth_version: str,
        tool_versions: dict[str, str],
        input_payload: dict[str, Any],
    ) -> None:
        data = {
            "receipt_type": "COMPUTATION",
            "input_hash": _hash(input_payload),
            "output_hash": _hash(output),
            "wealth_version": wealth_version,
            "tool_versions": tool_versions,
            "status": "COMPUTED",
            "case_id": case.case_id,
            "trace_id": case.trace_id,
        }
        _required_fields(data, self.required_fields)
        super().__init__(receipt_type="COMPUTATION", data=data)


@dataclass
class JudgmentReceipt(Receipt):
    """JUDGMENT receipt — what arifOS / APEX decided about a case."""

    receipt_type: ClassVar[str] = "JUDGMENT"
    required_fields: ClassVar[list[str]] = [
        "receipt_type", "evidence_hash", "judgment",
        "active_holds", "judge_state_hash",
    ]

    def __init__(
        self,
        *,
        case: CapitalCase,
        verdict: str,  # "PROCEED" | "HOLD" | "DENY"
        active_holds: list[str] | None = None,
        evidence_hash: str | None = None,
    ) -> None:
        if verdict not in ("PROCEED", "HOLD", "DENY"):
            raise ValueError(f"invalid verdict: {verdict!r}")
        if verdict == "PROCEED" and not case.governance.get("reversibility"):
            raise ValueError("PROCEED verdict requires reversibility field in governance")
        data = {
            "receipt_type": "JUDGMENT",
            "evidence_hash": evidence_hash or _hash({"case_id": case.case_id, "input": case.inputs, "evidence": case.evidence}),
            "judgment": verdict,
            "active_holds": active_holds or [],
            "judge_state_hash": _hash({"case_id": case.case_id, "verdict": verdict, "active_holds": active_holds or []}),
            "case_id": case.case_id,
            "trace_id": case.trace_id,
        }
        _required_fields(data, self.required_fields)
        super().__init__(receipt_type="JUDGMENT", data=data)


@dataclass
class HumanRatificationReceipt(Receipt):
    """HUMAN_RATIFICATION receipt — an authorized human accepted/rejected the proposal."""

    receipt_type: ClassVar[str] = "HUMAN_RATIFICATION"
    required_fields: ClassVar[list[str]] = [
        "receipt_type", "actor", "decision", "scope", "timestamp",
    ]

    def __init__(
        self,
        *,
        case: CapitalCase,
        actor: str,
        decision: str,  # "approve" | "reject"
        timestamp: str | None = None,
    ) -> None:
        if decision not in ("approve", "reject"):
            raise ValueError(f"invalid ratification decision: {decision!r}")
        data = {
            "receipt_type": "HUMAN_RATIFICATION",
            "actor": actor,
            "decision": decision,
            "scope": f"case:{case.case_id}",
            "timestamp": timestamp or _now(),
            "case_id": case.case_id,
            "trace_id": case.trace_id,
        }
        _required_fields(data, self.required_fields)
        super().__init__(receipt_type="HUMAN_RATIFICATION", data=data)


@dataclass
class ExecutionReceipt(Receipt):
    """EXECUTION receipt — only created if A-FORGE actually performs an authorized action."""

    receipt_type: ClassVar[str] = "EXECUTION"
    required_fields: ClassVar[list[str]] = [
        "receipt_type", "approved_action_hash", "execution_result_hash", "rollback_reference",
    ]

    def __init__(
        self,
        *,
        case: CapitalCase,
        approved_action_hash: str,
        execution_result_hash: str,
        rollback_reference: str,
    ) -> None:
        data = {
            "receipt_type": "EXECUTION",
            "approved_action_hash": approved_action_hash,
            "execution_result_hash": execution_result_hash,
            "rollback_reference": rollback_reference,
            "case_id": case.case_id,
            "trace_id": case.trace_id,
        }
        _required_fields(data, self.required_fields)
        super().__init__(receipt_type="EXECUTION", data=data)
