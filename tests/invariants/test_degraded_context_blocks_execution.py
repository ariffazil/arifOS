"""
Invariant Tests: Degraded Context Blocks Execution

Root Invariant 5 (No component may claim more certainty than its
evidence receipt) and the state-machine rule in docs/VERDICT_SEMANTICS.md
require that a DEGRADED_CONTEXT receipt caps the claim at
KERNEL_SEAL_AWARENESS. The schemas encode this as a structural rule;
the contract layer (closed in PR 2+) enforces it at the runtime.

Forged 2026-06-02 18:41 UTC under F13 SOVEREIGN ratification.
See docs/CORE_INVARIANTS.md, docs/AUTHORITY_MODEL.md, and
docs/VERDICT_SEMANTICS.md.
"""

import os
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).parents[2]
MISSION_SCHEMA = REPO_ROOT / "schemas" / "mission.schema.json"
RECEIPT_SCHEMA = REPO_ROOT / "schemas" / "receipt.schema.json"
AUTHORITY_STATE_SCHEMA = REPO_ROOT / "schemas" / "authority-state.schema.json"


@pytest.fixture(scope="module")
def schemas() -> dict:
    return {
        "mission": json.loads(MISSION_SCHEMA.read_text()),
        "receipt": json.loads(RECEIPT_SCHEMA.read_text()),
        "authority_state": json.loads(AUTHORITY_STATE_SCHEMA.read_text()),
    }


def _valid_receipt(
    context_verdict: str = "STABLE", actor_verified: bool = True
) -> dict:
    return {
        "receipt_id": "rcp_test_12345678",
        "claim_id": "claim_test_12345678",
        "evidence_type": "primary",
        "source": "GEOX",
        "timestamp": "2026-06-02T18:00:00Z",
        "ingested_at": "2026-06-02T18:00:01Z",
        "evidence_level": "L4_SUPABASE_STRUCTURED",
        "actor_verified": actor_verified,
        "verification_method": "session" if actor_verified else "none",
        "context_verdict": context_verdict,
        "non_overclaim_check": "passed",
    }


def _degraded_state() -> dict:
    return {
        "state_id": "as_2026_06_02_184159",
        "snapshot_at": "2026-06-02T18:41:59Z",
        "actor": {
            "claimed_id": "test",
            "verified": True,
            "verification_method": "session",
        },
        "context_verdict": "DEGRADED_CONTEXT",
        "seals": {
            "kernel_seal_awareness": "ACTIVE",
            "domain_seal_validity": "INACTIVE",
            "judge_seal_authorization": "INACTIVE",
            "vault999_seal_record": "INACTIVE",
            "public_seal_readiness": "INACTIVE",
        },
        "execution_authority": "HOLD",
        "apex_approval": "ABSENT",
        "active_holds": [],
        "active_missions": [],
        "forge_gate": {
            "enabled": False,
            "reversibility_threshold": 0.85,
            "blockers": ["context_degraded"],
        },
        "public_posture": {
            "service_health": "yellow",
            "execution_readiness": "held",
            "human_visible_summary": "Context degraded; forge gate disabled.",
        },
        "non_overclaim_check": "passed",
    }


class TestDegradedContextBlocksExecution:
    """Enforce: DEGRADED_CONTEXT caps certainty; cannot reach SEAL_AUTHORIZED."""

    def test_receipt_with_degraded_context_is_structurally_valid(
        self, schemas: dict
    ) -> None:
        """The receipt is structurally valid; the contract layer must
        refuse to use it as the basis for any execution authority claim.

        The schema permits it because the schema is the data layer.
        The kernel's contract layer (added in PR 2) is what caps the
        claim. This test pins the gap and the receipt's structural
        shape.
        """
        receipt = _valid_receipt(context_verdict="DEGRADED_CONTEXT")
        jsonschema.validate(receipt, schemas["receipt"])

    def test_receipt_with_unverified_actor_is_structurally_valid(
        self, schemas: dict
    ) -> None:
        """Same pattern: structurally valid; capped at KERNEL_SEAL_AWARENESS
        by the contract layer.
        """
        receipt = _valid_receipt(actor_verified=False)
        jsonschema.validate(receipt, schemas["receipt"])

    def test_authority_state_degraded_has_disabled_forge_gate(
        self, schemas: dict
    ) -> None:
        """When context_verdict=DEGRADED_CONTEXT, the forge gate MUST
        be disabled and the blockers list MUST include 'context_degraded'.

        This is the data-layer shape that PR 2 will enforce at the
        runtime. For now, we pin the shape.
        """
        state = _degraded_state()
        assert state["context_verdict"] == "DEGRADED_CONTEXT"
        assert state["forge_gate"]["enabled"] is False
        assert "context_degraded" in state["forge_gate"]["blockers"]
        assert state["execution_authority"] == "HOLD"
        jsonschema.validate(state, schemas["authority_state"])

    def test_authority_state_degraded_cannot_have_seal_authorized(
        self, schemas: dict
    ) -> None:
        """Document the gap: schema permits the combination; contract
        layer must not.

        A SEAL_AUTHORIZED execution_authority with context_verdict=
        DEGRADED_CONTEXT is overclaim. The schema permits it because
        the data layer cannot infer the rule. PR 2 (arif-sites) plus
        PR 4 (A-FORGE gate) close this at the contract layer.
        """
        state = _degraded_state()
        state["execution_authority"] = "SEAL_AUTHORIZED"  # illegal but schema-permitted
        state["forge_gate"]["enabled"] = True
        state["forge_gate"]["blockers"] = []
        # Schema permits. Contract layer is the next gate.
        jsonschema.validate(state, schemas["authority_state"])

    def test_mission_degraded_context_with_seal_authorized_is_documented_gap(
        self, schemas: dict
    ) -> None:
        """Document the structural gap: a mission with degraded context
        and a SEAL_AUTHORIZED stage is schema-permitted. The contract
        layer is responsible for refusing it.

        Closed in PR 2 (arif-sites public language + AAA truth-bound
        cockpit) and PR 4 (A-FORGE forge gate).
        """
        mission = {
            "mission_id": "m_2026_06_02_184159_degraded_gap",
            "objective": "Document the structural gap.",
            "actor": {
                "claimed_id": "test",
                "verified": True,
                "verification_method": "session",
            },
            "context": {
                "verdict": "DEGRADED_CONTEXT",
                "timezone": "UTC",
                "host": "test",
                "workspace": os.environ.get("ARIFOS_HOME", "/root") + "/arifOS",
            },
            "authority": {
                "self_approval_allowed": False,
                "human_final_authority": True,
                "apex_approval": "PRESENT",
                "execution_authority": "SEAL_AUTHORIZED",
            },
            "stages": {
                "000_INIT": "PASS",
                "111_SENSE": "PASS",
                "222_EVIDENCE": "PASS",
                "333_MIND": "PASS",
                "444_HEART": "PASS",
                "888_JUDGE": "SEAL",
                "999_VAULT": "PENDING",
                "666_FORGE": "DRY_RUN",
            },
            "receipts": [],
            "holds": [],
            "seals": [
                {
                    "seal_type": "JUDGE_SEAL_AUTHORIZATION",
                    "issued_at": "2026-06-02T18:41:59Z",
                    "issued_by": "arifOS_888",
                    "evidence_chain": ["rcp_test_12345678"],
                }
            ],
            "non_overclaim_check": "passed",
            "created_at": "2026-06-02T18:41:59Z",
            "updated_at": "2026-06-02T18:41:59Z",
        }
        # Schema permits. Contract layer is the next gate.
        jsonschema.validate(mission, schemas["mission"])
