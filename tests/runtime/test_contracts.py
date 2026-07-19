"""
Tests for /root/arifOS/arifosmcp/runtime/contracts/*.schema.json
Verifies that every contract parses and that a minimal example validates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Use a minimal jsonschema implementation via dict-validation if jsonschema is not available.
# We don't strictly need the dependency — check structural fields manually.
try:
    from jsonschema import validate as _jsv  # type: ignore

    def _validate(schema, instance):
        _jsv(instance=instance, schema=schema)
except ImportError:  # graceful fallback to trivial check
    def _validate(schema, instance):
        # Use the schema's "required" + "type" only
        if "required" in schema:
            for r in schema["required"]:
                if r not in instance:
                    raise AssertionError(f"missing required field: {r}")
        if schema.get("type") == "object":
            for k, v in schema.get("properties", {}).items():
                if k in instance:
                    if "type" in v and v["type"] != "string" and isinstance(instance[k], bool):
                        raise AssertionError(f"field {k} has wrong type")
        if "oneOf" in schema:
            # Just check that one branch validates
            sub_ok = False
            for branch in schema["oneOf"]:
                try:
                    _validate(branch, instance)
                    sub_ok = True
                    break
                except Exception:
                    continue
            if not sub_ok:
                raise AssertionError("instance fits no oneOf branch")


CONTRACTS = Path(__file__).resolve().parents[2] / "arifosmcp" / "runtime" / "contracts"


@pytest.mark.parametrize("schema_file,example", [
    ("session.schema.json", {
        "session_id": "session-abc123",
        "issuer": "did:web:arif-fazil.com",
        "subject_did": "did:web:arif-fazil.com:agents:wealth",
        "audience": ["wealth", "arifOS"],
        "actor_id": "ARIF",
        "allowed_capabilities": ["wealth_npv_reward"],
        "authority_band": "OPERATOR",
        "issued_at": "2026-07-15T08:00:00Z",
        "not_before": "2026-07-15T08:00:00Z",
        "expires_at": "2026-07-15T09:00:00Z",
        "jti": "token-uuid",
        "trace_id": "trc-test"
    }),
    ("capability.schema.json", {
        "id": "wealth_npv_reward",
        "resource": "wealth",
        "action_class": "COMPUTE",
        "public_simulation": True,
        "requires_judgment": True,
        "requires_ratification": False,
        "blast_radius": "NONE",
        "minimum_authority": "OPERATOR"
    }),
    ("lease.schema.json", {
        "lease_id": "lease-001",
        "holder_did": "did:web:arif-fazil.com:agents:arif_init",
        "resources": ["wealth", "geox"],
        "ceiling": { "max_invocations": 100, "authority_band_max": "OPERATOR" },
        "window": { "start": "2026-07-15T08:00:00Z", "end": "2026-07-15T12:00:00Z" },
        "issued_at": "2026-07-15T08:00:00Z",
        "expires_at": "2026-07-15T12:00:00Z",
        "revocable": True
    }),
    ("actor.schema.json", {
        "actor_id": "ARIF",
        "did": "did:web:arif-fazil.com",
        "role": "SOVEREIGN"
    }),
    ("audience.schema.json", { "organ": "wealth" }),
    ("action-class.schema.json", "COMPUTE"),
    ("judgment.schema.json", {
        "verdict": "PROCEED",
        "evidence_hash": "sha256:abc123def4567890",
        "active_holds": [],
        "judge_state_hash": "sha256:def456abc7890123"
    }),
    ("ratification.schema.json", {
        "actor": "ARIF",
        "decision": "approve",
        "scope": "case:CAP-2026-001",
        "timestamp": "2026-07-15T08:30:00Z",
        "revocation_window": 3600
    }),
    ("errors.schema.json", {
        "status": "HOLD",
        "error_code": "SESSION_REQUIRED",
        "message": "A governed session is required for this WEALTH capability.",
        "required_action": "INITIALIZE_SESSION_AT_AAA_OR_MCP_GATEWAY",
        "requested_capability": "wealth_npv_reward",
        "retryable": True,
        "mutation_occurred": False,
        "trace_id": "trc-test"
    })
])
def test_contract_parses_and_validates(schema_file: str, example: dict) -> None:
    path = CONTRACTS / schema_file
    assert path.exists(), f"missing {path}"
    schema = json.loads(path.read_text())
    _validate(schema, example)


def test_receipt_oneof_covers_all_four_types() -> None:
    """The receipt contract must accept each of the four types as distinct oneOf branches."""
    schema = json.loads((CONTRACTS / "receipt.schema.json").read_text())
    assert "oneOf" in schema
    assert len(schema["oneOf"]) == 4
    types = {next((k["const"] for k in branch["properties"].values() if "const" in k), None) for branch in schema["oneOf"]}
    assert types == {"COMPUTATION", "JUDGMENT", "HUMAN_RATIFICATION", "EXECUTION"}


def test_receipt_oneof_rejects_two_type_fields() -> None:
    """A receipt with multiple type fields must NOT validate (no overlap)."""
    import jsonschema
    schema = json.loads((CONTRACTS / "receipt.schema.json").read_text())
    bad = {
        "receipt_type": "COMPUTATION",
        "judgment": "PROCEED",
        "evidence_hash": "sha256:abc123def4567890"
    }
    # This sample satisfies NONE of the oneOf branches (COMPUTATION lacks input/output;
    # JUDGMENT lacks active_holds/judge_state_hash). Either way the validator must raise.
    with pytest.raises(jsonschema.exceptions.ValidationError):
        _validate(schema, bad)


@pytest.mark.parametrize("receipt", [
    {"receipt_type": "COMPUTATION",
     "input_hash": "sha256:abcdef0123456789",
     "output_hash": "sha256:1234567890abcdef",
     "wealth_version": "1.3.1",
     "tool_versions": {"wealth_npv_reward": "1.3.1"},
     "status": "COMPUTED"},
    {"receipt_type": "JUDGMENT",
     "evidence_hash": "sha256:abcdef0123456789",
     "judgment": "PROCEED",
     "active_holds": [],
     "judge_state_hash": "sha256:1234567890abcdef"},
    {"receipt_type": "HUMAN_RATIFICATION",
     "actor": "ARIF",
     "decision": "approve",
     "scope": "case:CAP-2026-001",
     "timestamp": "2026-07-15T08:30:00Z"},
    {"receipt_type": "EXECUTION",
     "approved_action_hash": "sha256:abcdef0123456789",
     "execution_result_hash": "sha256:1234567890abcdef",
     "rollback_reference": "case:CAP-2026-001:rollback"}
])
def test_receipt_oneof_accepts_each_type(receipt: dict) -> None:
    """Each of the four receipt types must validate against its oneOf branch."""
    import jsonschema
    schema = json.loads((CONTRACTS / "receipt.schema.json").read_text())
    # Must validate without raising.
    _validate(schema, receipt)
