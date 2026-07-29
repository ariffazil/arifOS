"""
test_rasa_derita_schema.py — Phase 1 structural validation of the constitutional contract.

These tests MUST PASS after Phase 1 land.
They do NOT prove runtime enforcement (that is Phase 2+).

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifosmcp.schemas.constitutional import (
    CANONICAL_REL_PATH,
    MODULE_ID,
    load_rasa_derita_schema,
    schema_path,
    schema_sha256,
    validate_rasa_derita_payload,
)

FIXTURE_EVALS = (
    Path(__file__).resolve().parents[1] / "fixtures" / "rasa_derita" / "evals.json"
)


class TestSchemaLanded:
    def test_canonical_path_exists(self):
        assert schema_path().is_file(), f"missing {schema_path()}"

    def test_path_matches_declared_canonical(self):
        # relative from repo root
        repo = Path(__file__).resolve().parents[2]
        assert (repo / CANONICAL_REL_PATH).is_file()

    def test_valid_json(self):
        raw = schema_path().read_text(encoding="utf-8")
        data = json.loads(raw)
        assert isinstance(data, dict)

    def test_stable_hash_format(self):
        h = schema_sha256()
        assert h.startswith("sha256:")
        assert len(h) == len("sha256:") + 64


class TestSchemaStructure:
    def test_load_valid(self):
        result = load_rasa_derita_schema()
        assert result.module_id == MODULE_ID
        assert result.validation_status == "VALID", result.violations
        assert result.enforcement_mode == "NONE"
        assert not result.violations

    def test_status_is_hold_not_seal(self):
        result = load_rasa_derita_schema()
        assert result.payload.get("status") == "888_HOLD"

    def test_phase1_flags(self):
        kcw = load_rasa_derita_schema().payload.get("kernel_complete_when") or {}
        assert kcw.get("schema_landed_in_repo") is True
        assert kcw.get("schema_loaded_by_runtime") is False
        assert kcw.get("causal_cascade_mandatory_at_judge") is False
        assert kcw.get("consent_lease_enforced") is False

    def test_five_axes_unique_ids(self):
        axes = load_rasa_derita_schema().payload["axes"]
        ids = [a["id"] for a in axes]
        assert len(ids) >= 5
        assert len(ids) == len(set(ids))

    def test_lesson_ids_unique(self):
        lessons = []
        for axis in load_rasa_derita_schema().payload["axes"]:
            for lesson in axis.get("lessons") or []:
                lessons.append(lesson["id"])
        assert len(lessons) >= 15
        assert len(lessons) == len(set(lessons))

    def test_cascade_min_three_steps(self):
        steps = load_rasa_derita_schema().payload["causal_cascade"]["schema"]["steps"]
        assert int(steps["minItems"]) >= 3

    def test_consent_lease_requires_expiry_and_revocation(self):
        schema = load_rasa_derita_schema().payload["consent_lease"]["schema"]
        for key in ("expires_at", "revocable", "revocation_propagation", "purpose", "scope"):
            assert key in schema

    def test_escalation_monotonic(self):
        levels = load_rasa_derita_schema().payload["escalation_lattice"]["levels"]
        nums = [lv["level"] for lv in levels]
        assert nums == sorted(nums)

    def test_fifteen_evals_with_expected(self):
        cases = load_rasa_derita_schema().payload["rasa_derita_evals"]["test_cases"]
        assert len(cases) >= 15
        for case in cases:
            assert case.get("id")
            assert case.get("expected")
            assert case.get("scenario")

    def test_fixture_evals_align_with_schema(self):
        fixture = json.loads(FIXTURE_EVALS.read_text(encoding="utf-8"))
        schema_ids = {
            c["id"]
            for c in load_rasa_derita_schema().payload["rasa_derita_evals"]["test_cases"]
        }
        fixture_ids = {c["id"] for c in fixture["test_cases"]}
        assert fixture_ids <= schema_ids

    def test_well_boundary_forbids_diagnosis(self):
        forbidden = " ".join(
            load_rasa_derita_schema().payload["well_boundary"]["forbidden"]
        ).lower()
        assert "diagnos" in forbidden

    def test_reject_false_ratified_status(self):
        data = dict(load_rasa_derita_schema().payload)
        data["status"] = "RATIFIED"
        data["kernel_complete_when"] = {
            "schema_loaded_by_runtime": False,
            "causal_cascade_mandatory_at_judge": False,
            "consent_lease_enforced": False,
        }
        violations = validate_rasa_derita_payload(data)
        assert any("RATIFIED" in v or "status=" in v for v in violations)


class TestPhase1DoesNotClaimEnforcement:
    def test_installation_block_not_enforced(self):
        inst = load_rasa_derita_schema().payload.get("installation") or {}
        assert inst.get("enforced") is False
        assert inst.get("loaded") is False
        assert inst.get("enforcement_mode") == "NONE"
