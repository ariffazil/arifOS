"""ExperienceMemory typed contract + legacy adapters (FI-003, 2026-10-29).

Contract: arifosmcp/runtime/contracts/experience-memory.schema.json

Rules under test:
- a legacy field that does not exist resolves to UNKNOWN, never to a
  fabricated default (a Seal C proposal has no outcome, so its outcome is
  UNKNOWN - not SUCCESS);
- placeholder / test-actor content is NOISE and cannot rise above RAW;
- the original payload is preserved verbatim;
- promotion vocabulary is shared with the ACD receipt contract - no second
  taxonomy;
- the model and the JSON Schema agree on the required field set.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from arifosmcp.runtime.experience_memory import (
    SCHEMA_VERSION,
    UNKNOWN,
    ExperienceMemory,
    from_adaptation,
    from_chron_lesson,
    from_dream_proposal,
    from_rsi_decision,
    from_seal_c_proposal,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "arifosmcp"
    / "runtime"
    / "contracts"
    / "experience-memory.schema.json"
)


# ── Seal C (the outcome-blind store) ────────────────────────────────────────
def test_seal_c_proposal_outcome_is_unknown_not_success():
    mem = from_seal_c_proposal(
        {
            "proposal_id": "prop-1",
            "ts": "2026-10-29T06:58:57Z",
            "requested_mode": "store",
            "actor_id": "qwen-code/FI-003",
            "session_id": "SEAL-1dcd23438c3d4fd8",
            "content": "a real lesson about canonical objects",
            "tags": [],
            "tier": None,
        }
    )
    assert mem.outcome == UNKNOWN
    assert mem.verdict == UNKNOWN
    assert mem.review_status == "UNREVIEWED"
    assert mem.promotion_status == "RAW"
    assert mem.source_surface == "seal_c_proposal"
    assert mem.source_record_id == "prop-1"


def test_placeholder_and_test_actor_content_is_noise():
    junk = from_seal_c_proposal(
        {"proposal_id": "p2", "actor_id": "arifos-federation", "session_id": "audit-session-p1-04", "content": "x"}
    )
    assert junk.memory_class == "NOISE"
    assert junk.promotion_status == "RAW"
    assert junk.outcome == UNKNOWN

    tester = from_seal_c_proposal(
        {"proposal_id": "p3", "actor_id": "test-actor", "session_id": "observe-only-session", "content": "a plausible line"}
    )
    assert tester.memory_class == "NOISE"


# ── CHRON lessons ──────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "status,expected",
    [
        ("ACTIVE", "ACTIVE"),
        ("CANDIDATE", "CANDIDATE"),
        ("REVIEWED", "REVIEWED"),
        ("SUPERSEDED", "RETIRED"),
        ("DIAGNOSTIC", "RAW"),
        (None, "UNKNOWN"),
    ],
)
def test_chron_lesson_promotion_mapping(status, expected):
    mem = from_chron_lesson({"lesson_id": "L1", "status": status, "lesson": "text", "basis": "b"})
    assert mem.promotion_status == expected
    assert mem.source_surface == "chron_lesson"


def test_chron_lesson_without_brier_is_unknown_not_inferred():
    mem = from_chron_lesson({"lesson_id": "L2", "status": "CANDIDATE", "lesson": "text"})
    # no measured brier -> no derivation to point at -> UNKNOWN, not INFERRED
    assert mem.epistemic_status == "UNKNOWN"
    assert mem.outcome == UNKNOWN
    assert mem.falsifier is None  # missing legacy field -> UNKNOWN, not invented


def test_chron_lesson_with_brier_is_verified():
    mem = from_chron_lesson(
        {"lesson_id": "L3", "status": "CANDIDATE", "lesson": "text", "brier_score": 0.0625}
    )
    assert mem.epistemic_status == "VERIFIED"
    assert mem.checker_type == "brier_score"


# ── adaptations (the one real loop) ─────────────────────────────────────────
def test_adaptation_keeps_falsifier_and_measured_delta():
    mem = from_adaptation(
        {
            "id": "AD-1",
            "pattern": "meter wrote into an immutable dir",
            "action": "moved OUTDIR",
            "metric": "meter file age (days)",
            "before": 4.0,
            "after": 0.0,
            "measured_delta": -4.0,
            "falsifier": "next scheduled run writes the meter",
            "deadline": "2026-10-26T21:15+08:00",
            "status": "ACTIVE",
            "owner": "333-AGI",
            "evidence": ["/root/.local/share/arifos/selfimprove/meter.json"],
            "ts": "2026-10-25T19:52:00Z",
            "check": {"kind": "meter_age_hours", "lt": 48},
        },
        {"decision": "KEPT", "observed": 0.0},
    )
    assert mem.memory_class == "SKILL"
    assert mem.outcome == "SUCCESS"
    assert mem.score_delta == -4.0
    assert mem.falsifier.startswith("next scheduled run")
    assert mem.promotion_status == "ACTIVE"
    assert mem.evidence_refs == ["/root/.local/share/arifos/selfimprove/meter.json"]


def test_adaptation_without_decision_has_unknown_outcome():
    mem = from_adaptation({"id": "AD-2", "status": "ACTIVE", "pattern": "p"}, None)
    assert mem.outcome == UNKNOWN
    assert mem.review_status == "UNREVIEWED"


# ── dream proposals ────────────────────────────────────────────────────────
def test_dream_proposal_is_a_hypothesis_never_a_rule():
    mem = from_dream_proposal(
        {
            "proposal_id": "d-1",
            "created_at": "2026-10-24T05:40:44Z",
            "actor_id": "qwen-code",
            "session_id": None,
            "proposition": "the raw lane was never built",
            "counterfactual": "if a populated raw-lane collection already exists, the gap is disproved",
            "evidence_class": "audit",
            "source_ref": {"path": "/root/forge_work/x.md", "sha256": "sha256:abc", "ratified_by": "qwen-code"},
        }
    )
    assert mem.memory_class == "EPISODE"
    assert mem.epistemic_status == "HYPOTHESIS"
    assert mem.promotion_status == "RAW"
    assert mem.outcome == "UNOBSERVED"
    assert "disproved" in (mem.falsifier or "")


# ── RSI decisions ──────────────────────────────────────────────────────────
def test_rsi_unresolved_decision_is_unobserved():
    mem = from_rsi_decision(
        {
            "decision_id": "d-9",
            "timestamp": "2026-10-29T00:00:00Z",
            "tool": "arif_judge",
            "original_verdict": "HOLD",
            "reason_class": "AUTHORITY",
            "review_outcome": "UNRESOLVED",
        }
    )
    assert mem.memory_class == "LEDGER"
    assert mem.verdict == "HOLD"
    assert mem.outcome == "UNOBSERVED"
    assert mem.review_status == "UNREVIEWED"
    assert mem.promotion_status == "RAW"


# ── invariants ─────────────────────────────────────────────────────────────
def test_source_payload_is_preserved_verbatim():
    raw = {"proposal_id": "p7", "content": "keep me", "actor_id": "x", "extra": {"nested": 1}}
    mem = from_seal_c_proposal(raw)
    assert mem.source_payload == raw
    assert mem.source_payload["extra"] == {"nested": 1}


def test_missing_fields_resolve_to_unknown_never_fabricated():
    mem = from_rsi_decision({"decision_id": "d-1"})
    assert mem.verdict == UNKNOWN
    assert mem.outcome == "UNOBSERVED"
    assert mem.actor_id is None
    assert mem.confidence is None
    assert mem.falsifier is None
    assert mem.times_retrieved == 0
    assert mem.times_applied == 0
    assert mem.authorized_by is None  # memory never carries authority by itself


def test_invalid_enum_is_rejected():
    with pytest.raises(ValidationError):
        ExperienceMemory(memory_id="m", source_surface="x", memory_class="NOT_A_CLASS")
    with pytest.raises(ValidationError):
        ExperienceMemory(memory_id="m", source_surface="x", promotion_status="SUPER_ACTIVE")


def test_model_and_schema_agree_on_required_fields():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert required <= set(ExperienceMemory.model_fields)
    props = schema["properties"]["classification"]["properties"]
    for field in ("memory_class", "epistemic_status", "outcome", "review_status", "promotion_status"):
        assert field in props
        assert set(props[field]["enum"]) <= set(
            ExperienceMemory.model_fields[field].annotation.__args__
        )


def test_schema_version_is_pinned():
    mem = from_seal_c_proposal({"proposal_id": "p"})
    assert mem.schema_version == SCHEMA_VERSION
    assert mem.schema_version == "experience-memory/1.0"
