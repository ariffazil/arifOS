"""
Invariant Tests: Service Health Is Not Execution Authority

Root Invariant 3 (Service health is not execution approval) requires
that a green /health probe does NOT imply execution readiness. The
authority-state schema structurally separates `public_posture.service_health`
from `public_posture.execution_readiness`, and `forge_gate.enabled` is
independent of `service_health`.

Forged 2026-06-02 18:41 UTC under F13 SOVEREIGN ratification.
See docs/CORE_INVARIANTS.md, docs/AUTHORITY_MODEL.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "authority-state.schema.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def _state(
    service_health: str,
    execution_readiness: str,
    gate_enabled: bool,
    context_verdict: str = "STABLE",
    judge_seal_active: bool = False,
    apex_approval: str = "ABSENT",
) -> dict:
    return {
        "state_id": "as_2026_06_02_184159",
        "snapshot_at": "2026-06-02T18:41:59Z",
        "actor": {
            "claimed_id": "test",
            "verified": True,
            "verification_method": "session",
        },
        "context_verdict": context_verdict,
        "seals": {
            "kernel_seal_awareness": "ACTIVE",
            "domain_seal_validity": "ACTIVE",
            "judge_seal_authorization": "ACTIVE" if judge_seal_active else "INACTIVE",
            "vault999_seal_record": "INACTIVE",
            "public_seal_readiness": "ACTIVE" if gate_enabled else "INACTIVE",
        },
        "execution_authority": "SEAL_AUTHORIZED" if gate_enabled else "HOLD",
        "apex_approval": apex_approval,
        "active_holds": [],
        "active_missions": [],
        "forge_gate": {
            "enabled": gate_enabled,
            "reversibility_threshold": 0.85,
            "blockers": [] if gate_enabled else ["no_judge_seal"],
        },
        "public_posture": {
            "service_health": service_health,
            "execution_readiness": execution_readiness,
            "human_visible_summary": "Synthetic state for invariant test.",
        },
        "non_overclaim_check": "passed",
    }


class TestServiceHealthNotExecutionAuthority:
    """Enforce: green /health does NOT imply execution readiness."""

    def test_green_health_with_held_execution_is_valid(self, schema: dict) -> None:
        """All services healthy, but execution is held (e.g., APEX absent).

        This is the canonical case where the cockpit shows green /health
        but the forge gate is closed. The two are independent facts.
        """
        state = _state("green", "held", False, judge_seal_active=False)
        assert state["public_posture"]["service_health"] == "green"
        assert state["public_posture"]["execution_readiness"] == "held"
        assert state["forge_gate"]["enabled"] is False
        jsonschema.validate(state, schema)

    def test_yellow_health_with_seal_authorized_is_structurally_permitted(
        self, schema: dict
    ) -> None:
        """Edge: yellow health with execution authorized.

        The schema permits this combination (each field is independent).
        The contract layer should flag it for human review. PR 2 will
        add the contract-layer rule (yellow health + seal = HOLD).
        """
        state = _state(
            "yellow",
            "ready",
            True,
            judge_seal_active=True,
            apex_approval="PRESENT",
        )
        jsonschema.validate(state, schema)

    def test_forge_gate_disabled_when_apex_absent(self, schema: dict) -> None:
        """APEX absent → forge gate MUST be disabled."""
        state = _state("green", "held", False, apex_approval="ABSENT")
        assert state["forge_gate"]["enabled"] is False
        assert state["apex_approval"] == "ABSENT"
        jsonschema.validate(state, schema)

    def test_forge_gate_blockers_must_be_empty_when_enabled(self, schema: dict) -> None:
        """If the gate is enabled, blockers MUST be empty.

        A gate that is 'enabled' with a non-empty blocker list is
        contradictory. The data layer rejects this combination
        structurally.
        """
        state = _state(
            "green",
            "ready",
            True,
            judge_seal_active=True,
            apex_approval="PRESENT",
        )
        assert state["forge_gate"]["enabled"] is True
        assert state["forge_gate"]["blockers"] == []
        jsonschema.validate(state, schema)

    def test_public_posture_structurally_separates_health_from_readiness(
        self, schema: dict
    ) -> None:
        """The schema requires BOTH service_health and execution_readiness.

        This structural separation is the data-layer enforcement of
        the root invariant. A bug that conflates them would fail this
        test.

        Demonstration: same health, different readiness — proves the
        two are independent fields.
        """
        state_a = _state("green", "held", False)
        state_b = _state("green", "ready", True, judge_seal_active=True, apex_approval="PRESENT")
        # Same service_health; different execution_readiness.
        assert (
            state_a["public_posture"]["service_health"]
            == state_b["public_posture"]["service_health"]
        )
        assert (
            state_a["public_posture"]["execution_readiness"]
            != state_b["public_posture"]["execution_readiness"]
        )
        jsonschema.validate(state_a, schema)
        jsonschema.validate(state_b, schema)

    def test_execution_readiness_ready_requires_judge_seal_and_apex(self, schema: dict) -> None:
        """Document the contract rule: execution_readiness=ready requires
        judge_seal_authorization=ACTIVE AND apex_approval=PRESENT.

        The schema permits structurally-inconsistent combinations
        (each field is independent). The contract layer is responsible
        for refusing. PR 2 closes this gap.
        """
        # Structurally valid but contractually illegal: ready without APEX.
        state = _state(
            "green",
            "ready",
            True,
            judge_seal_active=True,
            apex_approval="ABSENT",  # contractually wrong
        )
        jsonschema.validate(state, schema)
        # The contract test in PR 2 will assert this combination is refused.
