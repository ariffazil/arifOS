"""
Invariant Tests: No Self-Authorization

Root Invariants 1 (Capability is not permission) and 2 (Advisory output
is not authority) demand that no organ may self-authorize its own
execution. The kernel enforces this at the schema layer via
`mission.schema.json`'s `authority.self_approval_allowed: const=false`
and `authority.human_final_authority: const=true`.

Forged 2026-06-02 18:41 UTC under F13 SOVEREIGN ratification.
See docs/CORE_INVARIANTS.md and docs/VERDICT_SEMANTICS.md.
"""

import os
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "mission.schema.json"


@pytest.fixture(scope="module")
def mission_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def _valid_base_mission() -> dict:
    """Return a structurally-valid mission with all floors at HOLD/PENDING."""
    return {
        "mission_id": "m_2026_06_02_184159_invariant_test",
        "objective": "Test no self-authorization invariant.",
        "actor": {
            "claimed_id": "test_actor",
            "verified": False,
            "verification_method": "none",
        },
        "context": {
            "verdict": "STABLE",
            "timezone": "UTC",
            "host": "test",
            "workspace": os.environ.get("ARIFOS_HOME", "/root") + "/arifOS",
        },
        "authority": {
            "self_approval_allowed": False,
            "human_final_authority": True,
            "apex_approval": "ABSENT",
            "execution_authority": "HOLD",
        },
        "stages": {
            "000_INIT": "PENDING",
            "111_SENSE": "PENDING",
            "222_EVIDENCE": "PENDING",
            "333_MIND": "PENDING",
            "444_HEART": "PENDING",
            "888_JUDGE": "PENDING",
            "999_VAULT": "DISABLED",
            "666_FORGE": "DISABLED",
        },
        "receipts": [],
        "holds": [],
        "seals": [],
        "non_overclaim_check": "passed",
        "created_at": "2026-06-02T18:41:59Z",
        "updated_at": "2026-06-02T18:41:59Z",
    }


class TestNoSelfAuthorization:
    """Enforce: no mission may claim self_approval_allowed=True."""

    def test_valid_mission_passes_schema(self, mission_schema: dict) -> None:
        """A baseline mission with all floors HOLD/PENDING must validate."""
        mission = _valid_base_mission()
        jsonschema.validate(mission, mission_schema)

    def test_self_approval_true_rejected(self, mission_schema: dict) -> None:
        """Constitutional constant: self_approval_allowed MUST be false.

        The `const: false` rule in mission.schema.json is a hard floor.
        No schema-permitted path may set it to True.
        """
        mission = _valid_base_mission()
        mission["authority"]["self_approval_allowed"] = True
        with pytest.raises(jsonschema.ValidationError) as exc:
            jsonschema.validate(mission, mission_schema)
        # The error must point at the constitutional constant field,
        # not at some other field. jsonschema's `const` produces a
        # generic message ("False was expected"), so we check the path.
        assert list(exc.value.absolute_path) == ["authority", "self_approval_allowed"]

    def test_human_final_authority_false_rejected(self, mission_schema: dict) -> None:
        """Constitutional constant: human_final_authority MUST be true.

        If this test ever fails, the federation has lost APEX.
        """
        mission = _valid_base_mission()
        mission["authority"]["human_final_authority"] = False
        with pytest.raises(jsonschema.ValidationError) as exc:
            jsonschema.validate(mission, mission_schema)
        assert list(exc.value.absolute_path) == ["authority", "human_final_authority"]

    def test_seal_types_are_namespaced(self, mission_schema: dict) -> None:
        """The seal_type enum must reject bare 'SEAL'.

        Any badge, log line, or surface that uses bare 'SEAL' is
        non-compliant. The schema enforces this by restricting the
        enum to the five namespaced seals.
        """
        mission = _valid_base_mission()
        mission["seals"].append(
            {
                "seal_type": "SEAL",  # intentionally non-namespaced
                "issued_at": "2026-06-02T18:41:59Z",
                "issued_by": "rogue_organ",
                "evidence_chain": ["rcp_test_12345678"],
            }
        )
        with pytest.raises(jsonschema.ValidationError) as exc:
            jsonschema.validate(mission, mission_schema)
        # Error path must point at the seal_type field, not anywhere else.
        assert list(exc.value.absolute_path) == ["seals", 0, "seal_type"]

    def test_only_arifos_888_may_issue_judge_seal_at_schema_level(
        self, mission_schema: dict
    ) -> None:
        """Schema permits any issued_by; the *contract* layer must enforce.

        The schema is the data-layer floor. The runtime must additionally
        verify that `issued_by == 'arifOS_888'` for JUDGE_SEAL_AUTHORIZATION.
        This test documents the gap and is to be closed in PR 2.
        """
        mission = _valid_base_mission()
        mission["seals"].append(
            {
                "seal_type": "JUDGE_SEAL_AUTHORIZATION",
                "issued_at": "2026-06-02T18:41:59Z",
                "issued_by": "rogue_organ_self_seal",
                "evidence_chain": ["rcp_test_12345678"],
            }
        )
        # Schema accepts. Contract layer is the next gate.
        jsonschema.validate(mission, mission_schema)
