#!/usr/bin/env python3
"""FederationReceipt composer — the v2 orchestrator's runtime.

This script is the concrete reference implementation of the
`arifos-agentic-federation` skill's Step 5 (Compose the FederationReceipt).
It does not call any external services. It is a deterministic composer that
takes pre-computed AbstractionLabel, FloorReceipt, and BoundedExplanation
(and verifies orthogonality, entropy budget, recursion depth, and floor
pass conditions) and emits a sealed FederationReceipt.

Run: python3 compose_federation_receipt.py <input.json>
Input: {"abstraction": {...}, "attestation": {...}, "abduction": {...}}
Output: FederationReceipt as JSON.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import Any


SCHEMA_VERSION = "2.0.0"
L13_CRITICAL_FLOORS = {"F1", "F2", "F9", "L11", "L12", "L13"}


@dataclass
class FederationReceipt:
    schema_version: str
    request_hash: str
    intent: dict
    abstraction: dict
    attestation: dict
    abduction: dict
    verdict: str
    seal_hash: str
    residual_risk: list = field(default_factory=list)
    next_action: str = ""
    hold_code: str | None = None
    refinements: int = 0
    bounded: bool = True
    approval_required: dict | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _hash(payload: Any) -> str:
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def compose(
    abstraction: dict,
    attestation: dict,
    abduction: dict,
    intent: dict,
    refinements: int = 0,
) -> FederationReceipt:
    """Compose a FederationReceipt from the three axis outputs.

    Verifies:
    1. The 3 axes are consistent (organ label agrees with attested organ, etc.)
    2. Entropy budget is respected
    3. Recursion depth is within budget
    4. F1-F13 floor pass conditions map to the right verdict class
    """
    request_hash = intent.get("request_hash") or _hash(intent.get("request", ""))

    # --- orthogonality & consistency check ---
    abst_organ = abstraction.get("organ", "arifOS")
    att_organ = attestation.get("abstraction_label", {}).get("organ", abst_organ)
    abd_organ = abduction.get("organ", abst_organ)
    if not (abst_organ == att_organ == abd_organ):
        # axes disagreed on organ — flag and force default
        residual = [f"axis_organ_disagreement: abst={abst_organ} att={att_organ} abd={abd_organ}"]
        abst_organ = "arifOS"
    else:
        residual = []

    # --- entropy budget check ---
    entropy_spent = abduction.get("entropy_total", 0)
    budget = intent.get("entropy_budget_tokens", 4000)
    if entropy_spent > budget:
        return FederationReceipt(
            schema_version=SCHEMA_VERSION,
            request_hash=request_hash,
            intent=intent,
            abstraction=abstraction,
            attestation=attestation,
            abduction=abduction,
            verdict="HOLD",
            seal_hash="",
            residual_risk=residual + [f"entropy_budget_exceeded: {entropy_spent} > {budget}"],
            next_action="arifOS 888_HOLD",
            hold_code="entropy",
            refinements=refinements,
        )

    # --- recursion depth check ---
    max_depth = intent.get("max_recursion_depth", 3)
    if refinements > max_depth:
        return FederationReceipt(
            schema_version=SCHEMA_VERSION,
            request_hash=request_hash,
            intent=intent,
            abstraction=abstraction,
            attestation=attestation,
            abduction=abduction,
            verdict="HOLD",
            seal_hash="",
            residual_risk=residual + [f"recursion_depth_exceeded: {refinements} > {max_depth}"],
            next_action="arifOS 888_HOLD",
            hold_code="recursion",
            refinements=refinements,
        )

    # --- floor-pass → verdict mapping ---
    fail = set(attestation.get("floors_fail", []))
    warn = set(attestation.get("floors_warn", []))
    risk_tier = attestation.get("risk_tier", 0)

    verdict = "SEAL"
    hold_code = None
    next_action = "deliver to caller"

    if "L12" in fail:
        verdict = "HOLD"
        hold_code = "injection"
        next_action = "arifOS 888_HOLD"
    elif fail & L13_CRITICAL_FLOORS:
        verdict = "SEAL_REJECTED"
        next_action = "arifOS 888_JUDGE"
    elif "F1" in fail and risk_tier >= 2:
        verdict = "HOLD"
        hold_code = "floor_fail"
        next_action = "arifOS 888_HOLD requesting ack_irreversible"
    elif warn:
        verdict = "CONDITIONAL_SEAL"
        next_action = "deliver with caveats"
    elif risk_tier == 3:
        verdict = "CONDITIONAL_SEAL"
        next_action = "arifOS 888_JUDGE for tier-3 final say"
        residual.append("tier-3 action requires F13 SOVEREIGN")

    # --- final hash ---
    # Only SEAL-family verdicts carry a seal_hash. HOLD/SEAL_REJECTED have
    # empty hash, signaling "no SEAL was granted." The absence of the hash
    # is itself part of the receipt contract.
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request_hash": request_hash,
        "intent": intent,
        "abstraction": abstraction,
        "attestation": attestation,
        "abduction": abduction,
        "verdict": verdict,
        "refinements": refinements,
    }
    seal_hash = _hash(payload) if verdict in ("SEAL", "CONDITIONAL_SEAL") else ""

    return FederationReceipt(
        schema_version=SCHEMA_VERSION,
        request_hash=request_hash,
        intent=intent,
        abstraction=abstraction,
        attestation=attestation,
        abduction=abduction,
        verdict=verdict,
        seal_hash=seal_hash,
        residual_risk=residual,
        next_action=next_action,
        hold_code=hold_code,
        refinements=refinements,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: compose_federation_receipt.py <input.json>", file=sys.stderr)
        return 1
    with open(sys.argv[1]) as f:
        data = json.load(f)
    receipt = compose(
        abstraction=data.get("abstraction", {}),
        attestation=data.get("attestation", {}),
        abduction=data.get("abduction", {}),
        intent=data.get("intent", {}),
        refinements=data.get("refinements", 0),
    )
    print(json.dumps(receipt.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
