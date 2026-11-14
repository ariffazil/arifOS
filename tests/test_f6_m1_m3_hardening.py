"""Regression & hardening tests for F6 M1 (atomic nonce claim) and M3 (eligibility/emitter)."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from arifosmcp.runtime.f6.authority_binding import (
    ActionRequest,
    AuthorityBinding,
    BindingStore,
    BindingVerdict,
    execute_bound,
)
from arifosmcp.runtime.f6.execution_boundary import guard_forge_call
from arifosmcp.runtime.f6.meters import (
    emit_tier3_maruah_event,
    evaluate_meter_3_comprehension,
)
from arifosmcp.runtime.tools import _arif_forge_execute_tool


def _make_binding(
    *,
    binding_id: str = "bind-1",
    actor_id: str = "actor-1",
    nonce: str = "nonce-1",
    offset_start_s: int = -60,
    offset_end_s: int = 300,
    param_constraints: dict | None = None,
) -> AuthorityBinding:
    now = datetime.now(timezone.utc)
    return AuthorityBinding(
        binding_id=binding_id,
        actor_id=actor_id,
        authority="SOVEREIGN",
        scope="forge:write",
        allowed_actions=["write"],
        resource_patterns=["sandbox/*"],
        param_constraints=param_constraints or {"target": {"const": "sandbox/file.txt"}},
        not_before=(now + timedelta(seconds=offset_start_s)).isoformat(),
        not_after=(now + timedelta(seconds=offset_end_s)).isoformat(),
        nonce=nonce,
    )


def _ok_guard(_req: ActionRequest, _b: AuthorityBinding) -> tuple[bool, str]:
    return True, "ok"


def test_m1_unit_and_sandbox_sink_enforcement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "f6_bindings.db"
    store = BindingStore(db_path=db)

    sink_calls: list[str] = []

    def sandbox_sink(req: ActionRequest) -> dict:
        sink_calls.append(req.binding_id)
        return {"ok": True}

    # 1a. Empty binding_id -> REJECT_BYPASS
    res_bypass = execute_bound(
        ActionRequest(binding_id="", actor_id="actor-1", action="write", resource="sandbox/a"),
        store,
        sandbox_sink,
        state_guard=_ok_guard,
    )
    assert res_bypass["decision"] == BindingVerdict.REJECT_BYPASS
    assert sink_calls == []

    # 1b. Non-existent binding_id -> UNKNOWN (fail-closed)
    res_missing = execute_bound(
        ActionRequest(binding_id="missing", actor_id="actor-1", action="write", resource="sandbox/a"),
        store,
        sandbox_sink,
        state_guard=_ok_guard,
    )
    assert res_missing["decision"] == BindingVerdict.UNKNOWN
    assert sink_calls == []

    # 2. Expired binding -> REJECT_EXPIRED
    expired = _make_binding(binding_id="bind-exp", nonce="n-exp", offset_start_s=-600, offset_end_s=-60)
    store.save(expired)
    res_exp = execute_bound(
        ActionRequest(
            binding_id="bind-exp",
            actor_id="actor-1",
            action="write",
            resource="sandbox/file.txt",
            params={"target": "sandbox/file.txt"},
            scope="forge:write",
        ),
        store,
        sandbox_sink,
        state_guard=_ok_guard,
    )
    assert res_exp["decision"] == BindingVerdict.REJECT_EXPIRED
    assert sink_calls == []

    # 3. Revoked binding -> REJECT_REVOKED
    revoked = _make_binding(binding_id="bind-rev", nonce="n-rev")
    store.save(revoked)
    store.revocations.revoke("bind-rev", "F13", "test revocation")
    res_rev = execute_bound(
        ActionRequest(
            binding_id="bind-rev",
            actor_id="actor-1",
            action="write",
            resource="sandbox/file.txt",
            params={"target": "sandbox/file.txt"},
            scope="forge:write",
        ),
        store,
        sandbox_sink,
        state_guard=_ok_guard,
    )
    assert res_rev["decision"] == BindingVerdict.REJECT_REVOKED
    assert sink_calls == []

    # 4. Tampered parameter -> REJECT_PARAM
    tamper = _make_binding(binding_id="bind-tamper", nonce="n-tamper")
    store.save(tamper)
    res_tamper = execute_bound(
        ActionRequest(
            binding_id="bind-tamper",
            actor_id="actor-1",
            action="write",
            resource="sandbox/file.txt",
            params={"target": "/etc/passwd"},
            scope="forge:write",
        ),
        store,
        sandbox_sink,
        state_guard=_ok_guard,
    )
    assert res_tamper["decision"] == BindingVerdict.REJECT_PARAM
    assert sink_calls == []

    # 5. Positive control -> ALLOW (once) then REJECT_REPLAY
    valid = _make_binding(binding_id="bind-ok", nonce="n-ok")
    store.save(valid)
    req_ok = ActionRequest(
        binding_id="bind-ok",
        actor_id="actor-1",
        action="write",
        resource="sandbox/file.txt",
        params={"target": "sandbox/file.txt"},
        scope="forge:write",
    )
    res_ok = execute_bound(req_ok, store, sandbox_sink, state_guard=_ok_guard)
    assert res_ok["decision"] == BindingVerdict.ALLOW
    assert sink_calls == ["bind-ok"]

    res_replay = execute_bound(req_ok, store, sandbox_sink, state_guard=_ok_guard)
    assert res_replay["decision"] == BindingVerdict.REJECT_REPLAY
    assert sink_calls == ["bind-ok"]

    # 6. STORE_BUSY on lock contention -> UNKNOWN (never ALLOW, never REPLAY)
    busy_binding = _make_binding(binding_id="bind-busy", nonce="n-busy")
    store.save(busy_binding)

    monkeypatch.setattr(store, "claim_nonce", lambda _b, _n: ("STORE_BUSY", "sqlite lock busy: database is locked"))
    res_busy = execute_bound(
        ActionRequest(
            binding_id="bind-busy",
            actor_id="actor-1",
            action="write",
            resource="sandbox/file.txt",
            params={"target": "sandbox/file.txt"},
            scope="forge:write",
        ),
        store,
        sandbox_sink,
        state_guard=_ok_guard,
    )
    assert res_busy["decision"] == BindingVerdict.UNKNOWN
    assert "lock busy" in res_busy["reason"]
    assert sink_calls == ["bind-ok"]

    # Also verify real SQLite lock contention inside claim_nonce returns STORE_BUSY
    monkeypatch.undo()
    lock_conn = sqlite3.connect(str(db), isolation_level=None)
    try:
        lock_conn.execute("BEGIN EXCLUSIVE")
        status, reason = store.claim_nonce("bind-busy", "n-busy-real")
        assert status == "STORE_BUSY"
        assert "locked" in reason.lower() or "busy" in reason.lower()
    finally:
        lock_conn.execute("ROLLBACK")
        lock_conn.close()


def test_m1_concurrent_multi_connection_replay(tmp_path: Path) -> None:
    db = tmp_path / "f6_concurrent.db"
    seed_store = BindingStore(db_path=db)
    seed_store.save(_make_binding(binding_id="bind-race", nonce="n-race"))

    n_threads = 4
    barrier = threading.Barrier(n_threads)
    results: list[dict] = []
    sink_lock = threading.Lock()
    sink_count = 0

    def worker() -> None:
        nonlocal sink_count
        local_store = BindingStore(db_path=db)

        def sink(_req: ActionRequest) -> dict:
            nonlocal sink_count
            with sink_lock:
                sink_count += 1
            return {"executed": True}

        req = ActionRequest(
            binding_id="bind-race",
            actor_id="actor-1",
            action="write",
            resource="sandbox/file.txt",
            params={"target": "sandbox/file.txt"},
            scope="forge:write",
        )
        barrier.wait(timeout=5.0)
        res = execute_bound(req, local_store, sink, state_guard=_ok_guard)
        with sink_lock:
            results.append(res)

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10.0)

    decisions = [r["decision"] for r in results]
    assert decisions.count(BindingVerdict.ALLOW) == 1
    assert sink_count == 1
    assert all(
        d in (BindingVerdict.ALLOW, BindingVerdict.REJECT_REPLAY, BindingVerdict.UNKNOWN)
        for d in decisions
    )


def test_m1_entrypoint_arif_forge_execute_enforces_binding(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "f6_entry.db"
    monkeypatch.setenv("ARIFOS_F6_BINDING_ENFORCE", "1")
    monkeypatch.setenv("ARIFOS_F6_BINDING_DB", str(db))

    out_hold = asyncio.run(
        _arif_forge_execute_tool(
            mode="engineer",
            manifest=json.dumps({"f6_binding_id": "nonexistent-lease", "target": "sandbox/x"}),
            actor_id="test-actor",
        )
    )
    assert out_hold["verdict"] == "HOLD"
    assert out_hold["effective_verdict"] == "HOLD"
    assert out_hold.get("result", {}).get("mutation_allowed") is False

    # Verify guard_forge_call directly at the boundary for both missing and read-only
    guard_missing = guard_forge_call(
        mode="engineer",
        manifest=json.dumps({"f6_binding_id": "nonexistent-lease", "target": "sandbox/x"}),
        actor_id="test-actor",
        enforce=True,
    )
    assert guard_missing["blocked"] is True
    assert guard_missing["decision"] == BindingVerdict.UNKNOWN

    # Read-only mode must not be blocked by F6 mutating binding check
    guard_ro = guard_forge_call(mode="query", manifest="status", actor_id="test-actor", enforce=True)
    assert guard_ro["blocked"] is False


def test_m3_emitter_rejects_null_and_eligibility_filters_audit_rows(tmp_path: Path) -> None:
    events_path = tmp_path / "maruah_events.jsonl"
    witness_path = tmp_path / "human_witness.jsonl"

    # Reject None / "" / "None" / "null"
    for bad_id in (None, "", "None", "null"):
        res = emit_tier3_maruah_event(
            decision_id=bad_id,  # type: ignore[arg-type]
            tool_name="arif_seal",
            events_path=events_path,
        )
        assert res["emitted"] is False
    assert not events_path.exists()

    # Seed events: 2 misclassified audit rows, 1 legacy advisory row, 0 eligible -> UNKNOWN
    rows = [
        {"decision_id": "None", "action_class": "IRREVERSIBLE", "mode": "audit", "restatement_provided": False},
        {"decision_id": "s-2", "action_class": "IRREVERSIBLE", "mode": "audit", "restatement_provided": False},
        {"decision_id": "s-3", "action_class": "IRREVERSIBLE", "advisory": True, "restatement_provided": False},
    ]
    events_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    m3_empty = evaluate_meter_3_comprehension(witness_path=witness_path, events_path=events_path)
    assert m3_empty.result == "UNKNOWN"
    assert "NO_ELIGIBLE_EVENTS" in m3_empty.result_reason
    assert "misclassified_readonly=2" in m3_empty.result_reason
    assert "legacy_advisory=1" in m3_empty.result_reason

    # Add an eligible IRREVERSIBLE row WITHOUT restatement_provided -> must count in denominator and FAIL
    emit_res = emit_tier3_maruah_event(
        decision_id="seal-real-1",
        tool_name="arif_seal",
        mode="seal",
        ack_irreversible=False,
        witness_type="ai",
        events_path=events_path,
    )
    assert emit_res["emitted"] is True

    m3_fail = evaluate_meter_3_comprehension(witness_path=witness_path, events_path=events_path)
    assert m3_fail.result == "FAIL"
    assert "1 eligible" in m3_fail.coverage
