"""Phoenix-72 cooling evaluator tests (2026-10-17).

The consumer side is exercised with an injected clock: the 72-hour band is
simulated in seconds, never by touching the production clock or waiting.

These tests also *document* current promotion semantics rather than wishing
them different: with the evaluator as shipped, a due record without an
explicit seal request resolves to VOID. That is recorded as a finding, not
silently "fixed" here.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from arifosmcp.runtime.phoenix_janitor import (
    OPEN_STATES,
    TERMINAL_STATES,
    evaluate_cooling,
    payload_to_entry,
    plan_transitions,
)

CREATED = datetime(2026, 10, 17, 4, 0, tzinfo=UTC)
EXPIRY = CREATED + timedelta(hours=72)


def _point(
    *,
    point_id: str = "11111111-1111-1111-1111-111111111111",
    memory_id: str = "22222222-2222-2222-2222-222222222222",
    state: str = "candidate",
    expiry: datetime = EXPIRY,
    psi: int = 0,
    witness: dict | None = None,
    anti_hantu: bool = False,
):
    payload = {
        "content": "synthetic canary",
        "phoenix_id": "phx-test-1",
        "phoenix_state": state,
        "phoenix_cooldown_expiry": expiry.isoformat(),
        "phoenix_psi_utility": psi,
        "phoenix_tri_witness": witness or {"human": False, "ai": False, "earth": False},
        "phoenix_anti_hantu_flag": anti_hantu,
        "metadata": {"memory_id": memory_id, "timestamp": CREATED.timestamp()},
    }
    return SimpleNamespace(id=point_id, payload=payload)


class _FakeQdrant:
    def __init__(self, points):
        self.points = points
        self.writes: list[dict] = []

    def scroll(self, **kwargs):
        return self.points, None

    def set_payload(self, *, collection_name, payload, points):
        self.writes.append({"collection": collection_name, "payload": payload, "points": points})
        return True


# ── record mapping ───────────────────────────────────────────────────────────


def test_payload_without_phoenix_is_ignored():
    assert payload_to_entry({"content": "plain"}) is None
    assert payload_to_entry(None) is None


def test_payload_to_entry_maps_fields():
    entry = payload_to_entry(_point().payload)
    assert entry["state"] == "candidate"
    assert entry["psi_utility"] == 0
    assert entry["cooldown_expiry"].startswith("2026-10-20")


# ── clock injection ──────────────────────────────────────────────────────────


def test_before_expiry_stays_open():
    plan = plan_transitions([_point()], now=EXPIRY - timedelta(hours=1))
    assert plan[0]["new_state"] == "cooling"
    assert plan[0]["old_state"] == "candidate"


def test_after_expiry_voids_when_utility_below_threshold():
    plan = plan_transitions([_point()], now=EXPIRY + timedelta(seconds=1))
    assert plan[0]["new_state"] == "void"
    assert "SEAL conditions not met" in plan[0]["reason"]


def test_same_record_two_clocks_two_outcomes():
    rec = _point()
    early = plan_transitions([rec], now=EXPIRY - timedelta(hours=2))[0]["new_state"]
    late = plan_transitions([rec], now=EXPIRY + timedelta(hours=2))[0]["new_state"]
    assert early == "cooling" and late == "void"


def test_due_high_utility_still_voids_without_explicit_seal_request():
    """Current semantics: should_seal() defaults explicit_seal_requested=False,
    which it treats as a veto. The evaluator never threads True, so SEAL is
    unreachable through this consumer — documented, not changed here."""
    rec = _point(psi=2, witness={"human": True, "ai": True, "earth": True})
    plan = plan_transitions([rec], now=EXPIRY + timedelta(seconds=1))
    assert plan[0]["new_state"] == "void"


def test_anti_hantu_voids_immediately():
    plan = plan_transitions([_point(anti_hantu=True)], now=CREATED)
    assert plan[0]["new_state"] == "void"
    assert plan[0]["changed"] is True


def test_terminal_states_are_skipped():
    for state in TERMINAL_STATES:
        assert plan_transitions([_point(state=state)], now=EXPIRY) == []
    assert set(OPEN_STATES) == {"candidate", "cooling"}


# ── apply / dry run ──────────────────────────────────────────────────────────


def test_dry_run_writes_nothing():
    qc = _FakeQdrant([_point()])
    import asyncio

    out = asyncio.run(
        evaluate_cooling(now=EXPIRY + timedelta(seconds=1), dry_run=True, client=qc)
    )
    assert out["mode"] == "dry_run"
    assert out["transitions_planned"] == 1
    assert out["transitions_applied"] == 0
    assert qc.writes == []


def test_apply_writes_only_state_and_stamp():
    qc = _FakeQdrant([_point()])
    import asyncio

    out = asyncio.run(
        evaluate_cooling(
            now=EXPIRY + timedelta(seconds=1),
            dry_run=False,
            client=qc,
            collection="arifos_memory",
        )
    )
    assert out["transitions_applied"] == 1
    assert qc.writes[0]["payload"]["phoenix_state"] == "void"
    assert "phoenix_evaluated_at" in qc.writes[0]["payload"]
    assert set(qc.writes[0]["payload"]) == {"phoenix_state", "phoenix_evaluated_at"}


def test_second_pass_is_idempotent():
    import asyncio

    qc = _FakeQdrant([_point()])
    now = EXPIRY + timedelta(seconds=1)
    first = asyncio.run(evaluate_cooling(now=now, dry_run=False, client=qc))
    assert first["transitions_applied"] == 1
    # Simulate the store now holding the applied state.
    qc.points = [_point(state="void")]
    second = asyncio.run(evaluate_cooling(now=now, dry_run=False, client=qc))
    assert second["transitions_planned"] == 0
    assert second["transitions_applied"] == 0
    assert len(qc.writes) == 1


def test_point_ids_scope_excludes_other_records():
    """Bounded application: a canary must never touch unrelated live records."""
    import asyncio

    mine = _point(point_id="aaaaaaaa-0000-0000-0000-000000000001")
    other = _point(
        point_id="bbbbbbbb-0000-0000-0000-000000000002",
        memory_id="33333333-3333-3333-3333-333333333333",
    )
    qc = _FakeQdrant([mine, other])
    out = asyncio.run(
        evaluate_cooling(
            now=EXPIRY + timedelta(seconds=1),
            dry_run=False,
            client=qc,
            point_ids=["aaaaaaaa-0000-0000-0000-000000000001"],
        )
    )
    assert out["scanned"] == 1
    assert out["transitions_applied"] == 1
    assert qc.writes[0]["points"] == ["aaaaaaaa-0000-0000-0000-000000000001"]
