#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml

from arifosmcp.runtime import (
    authority_gate,
    evidence_guard,
    irreversibility_guard,
    uncertainty_gate,
)

DOCTRINE_PATH = Path("000/ROOT/K013_LANGUAGE_GOVERNANCE.md")


class DoctrineDiffError(RuntimeError):
    pass


def _extract_machine_contract(doc: str) -> dict:
    match = re.search(r"```yaml\\n(.*?)\\n```", doc, flags=re.DOTALL)
    if not match:
        raise DoctrineDiffError("K013 machine contract YAML block not found")

    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict) or "k013" not in data:
        raise DoctrineDiffError("Invalid K013 machine contract structure")
    return data["k013"]


def run_checks() -> list[str]:
    errors: list[str] = []

    if not DOCTRINE_PATH.exists():
        return [f"missing doctrine file: {DOCTRINE_PATH}"]

    contract = _extract_machine_contract(DOCTRINE_PATH.read_text())

    contract_axioms = set(contract.get("axioms", []))
    runtime_axioms = set(authority_gate.AXIOMS.keys())
    if contract_axioms != runtime_axioms:
        errors.append(
            f"axiom mismatch doctrine={sorted(contract_axioms)} runtime={sorted(runtime_axioms)}"
        )

    contract_required_fields = set(contract.get("required_fields", []))
    runtime_required_fields = set(authority_gate.REQUIRED_CONSEQUENTIAL_FIELDS)
    if contract_required_fields != runtime_required_fields:
        errors.append(
            "required field mismatch "
            f"doctrine={sorted(contract_required_fields)} runtime={sorted(runtime_required_fields)}"
        )

    contract_evidence_states = tuple(contract.get("evidence_states", []))
    if contract_evidence_states != evidence_guard.EVIDENCE_STATES:
        errors.append(
            "evidence state mismatch "
            f"doctrine={contract_evidence_states} runtime={evidence_guard.EVIDENCE_STATES}"
        )

    contract_uncertainty = tuple(contract.get("uncertainty_keys", []))
    if contract_uncertainty != uncertainty_gate.MANDATORY_UNCERTAINTY_KEYS:
        errors.append(
            "uncertainty key mismatch "
            f"doctrine={contract_uncertainty} runtime={uncertainty_gate.MANDATORY_UNCERTAINTY_KEYS}"
        )

    contract_rule = contract.get("irreversible_rule")
    runtime_rule = irreversibility_guard.RULE_NO_IRREVERSIBLE_ACTION_WITHOUT_EXPLICIT_HUMAN_ACK
    if contract_rule != runtime_rule:
        errors.append(
            f"irreversibility rule mismatch doctrine={contract_rule} runtime={runtime_rule}"
        )

    return errors


def main() -> int:
    try:
        errors = run_checks()
    except DoctrineDiffError as exc:
        print(f"FAIL: {exc}")
        return 1

    if errors:
        print("FAIL: doctrine/runtime divergence detected")
        for error in errors:
            print(f" - {error}")
        return 1

    print("PASS: doctrine/runtime parity for K013")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
