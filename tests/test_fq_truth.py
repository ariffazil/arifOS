"""T2 — one FQ object: value, measured_at, scope.

Before T2 a session payload could carry the session quotient (often None),
a live apex G and a frozen apex G, each a bare number with no scope and no
timestamp. These tests pin the single shape and both producer paths:

  * ``fq_gate.metabolic_cap``  -> scope="session"  (measured_at set only
    when arifFlow was actually read)
  * ``health_truth.publish_system_floor_truth`` -> scope="federation"
    (the reading /health publishes and the verbs echo)

A shape test would pass on a system that still emitted a second number, so
the producer tests assert the old key is gone, not merely that the new one
appeared.
"""

from __future__ import annotations

import io
import json
import pathlib
import re

import pytest

from arifosmcp.runtime import fq_gate
from arifosmcp.runtime.fq_gate import metabolic_cap
from arifosmcp.runtime.fq_truth import (
    FQ_SCOPE_FEDERATION,
    FQ_SCOPE_SESSION,
    fq_object,
    normalize_fq,
)
from arifosmcp.runtime.health_truth import (
    FLOOR_STATUS_PASS,
    clear_system_floor_truth,
    floor_truth,
    publish_system_floor_truth,
    read_system_floor_truth,
)

ALL_PASS = {f"F{i}": FLOOR_STATUS_PASS for i in range(1, 14)}
FQ_KEYS = {"value", "measured_at", "scope"}


@pytest.fixture(autouse=True)
def _isolated_system_reading():
    clear_system_floor_truth()
    yield
    clear_system_floor_truth()


class _Resp:
    def __init__(self, payload: dict) -> None:
        self._buf = io.BytesIO(json.dumps(payload).encode())

    def read(self) -> bytes:
        return self._buf.read()

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def _fake_flow(per_actor: dict) -> _Resp:
    return _Resp({"fq": {"quotient": 0.72, "per_actor": per_actor}})


# ── the shape ─────────────────────────────────────────────────────────────


def test_object_has_exactly_three_keys() -> None:
    obj = fq_object(0.5)
    assert set(obj) == FQ_KEYS
    assert obj["scope"] == FQ_SCOPE_SESSION
    assert obj["measured_at"] is None


def test_absent_reading_is_none_not_zero() -> None:
    # K2: unknown != zero. A bool is not a measurement either.
    for raw in (None, "UNMEASURED", "UNKNOWN", "", True, {"nested": 1}):
        assert fq_object(raw)["value"] is None


def test_scope_is_never_invented() -> None:
    assert fq_object(1.0, scope="planetary")["scope"] == FQ_SCOPE_SESSION
    assert fq_object(1.0, scope=FQ_SCOPE_FEDERATION)["scope"] == FQ_SCOPE_FEDERATION


def test_normalize_legacy_shapes() -> None:
    assert normalize_fq({"quotient": 0.4})["value"] == 0.4
    assert normalize_fq({"fq": "0.31"})["value"] == 0.31
    assert normalize_fq({"G": 0.6}, scope=FQ_SCOPE_FEDERATION)["scope"] == FQ_SCOPE_FEDERATION
    assert normalize_fq(0.33)["value"] == 0.33
    assert normalize_fq({"quotient": "UNMEASURED"})["value"] is None
    legacy = normalize_fq({"quotient": 0.9, "measured_at": "2026-01-01T00:00:00Z"})
    assert legacy["measured_at"] == "2026-01-01T00:00:00Z"


# ── producer 1: the session gate ─────────────────────────────────────────


def test_session_gate_writes_the_object_and_drops_quotient(monkeypatch) -> None:
    monkeypatch.setattr(
        fq_gate.urllib.request,
        "urlopen",
        lambda *a, **k: _fake_flow({"Q": {"quotient": 0.62, "verdict": "FLOWING"}}),
    )
    authority, state = metabolic_cap("Q", "LIMITED_MUTATE")
    assert authority == "LIMITED_MUTATE"
    # The second representation is gone, not shadowed by the new one.
    assert "quotient" not in state
    assert set(state["fq"]) == FQ_KEYS
    assert state["fq"]["value"] == 0.62
    assert state["fq"]["scope"] == FQ_SCOPE_SESSION
    assert state["fq"]["measured_at"]


def test_capped_session_reports_the_worst_reading_in_the_object(monkeypatch) -> None:
    monkeypatch.setattr(
        fq_gate.urllib.request,
        "urlopen",
        lambda *a, **k: _fake_flow({"Q": {"quotient": 0.2, "verdict": "BURNING"}}),
    )
    authority, state = metabolic_cap("Q", "LIMITED_MUTATE")
    assert authority == "OBSERVE_ONLY"
    assert state["capped"] is True
    assert state["fq"]["value"] == 0.2


def test_unread_gate_leaves_the_object_unmeasured(monkeypatch) -> None:
    def _boom(*a, **k):
        raise OSError("arifFlow down")

    monkeypatch.setattr(fq_gate.urllib.request, "urlopen", _boom)
    authority, state = metabolic_cap("Q", "LIMITED_MUTATE")
    assert authority == "LIMITED_MUTATE"  # session gate fails open
    assert state["fq_outcome"] == "UNREACHABLE"
    assert state["fq"] == {
        "value": None,
        "measured_at": None,
        "scope": FQ_SCOPE_SESSION,
    }


# ── producer 2: the published federation reading ─────────────────────────


def test_published_federation_fq_is_stored_with_its_scope_and_instant() -> None:
    publish_system_floor_truth(
        floor_truth(ALL_PASS, 13),
        fq=fq_object(
            0.6964, measured_at="2026-10-18T10:00:00Z", scope=FQ_SCOPE_FEDERATION
        ),
    )
    read = read_system_floor_truth()
    assert read is not None
    assert read["fq"] == {
        "value": 0.6964,
        "measured_at": "2026-10-18T10:00:00Z",
        "scope": FQ_SCOPE_FEDERATION,
    }


def test_publishing_without_an_fq_does_not_invent_one() -> None:
    publish_system_floor_truth(floor_truth(ALL_PASS, 13))
    read = read_system_floor_truth()
    assert read is not None
    assert "fq" not in read


def test_a_legacy_fq_dict_cannot_smuggle_a_session_scope_into_the_reading() -> None:
    # A caller passing {"quotient": x} must land as federation scope here:
    # /health measures the federation, and the stored object says so.
    publish_system_floor_truth(
        floor_truth(ALL_PASS, 13), fq={"quotient": 0.55}
    )
    read = read_system_floor_truth()
    assert read is not None
    assert read["fq"]["value"] == 0.55
    assert read["fq"]["scope"] == FQ_SCOPE_FEDERATION


# ── the falsifier: one writer ────────────────────────────────────────────


def test_the_object_literal_exists_in_one_module_only() -> None:
    root = pathlib.Path(__file__).resolve().parents[1] / "arifosmcp"
    # Match an actual dict literal with the three keys, not a file that merely
    # mentions them somewhere (runtime/tools.py has unrelated "value" schemas).
    pattern = re.compile(
        r'\{\s*"value"\s*:[\s\S]{0,200}?"measured_at"\s*:[\s\S]{0,200}?"scope"\s*:',
        re.M,
    )
    offenders = []
    for path in root.rglob("*.py"):
        if pattern.search(path.read_text(errors="ignore")) and path.name != "fq_truth.py":
            offenders.append(str(path.relative_to(root)))
    assert offenders == [], (
        "an FQ object is being built outside fq_truth.py: " + ", ".join(offenders)
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
