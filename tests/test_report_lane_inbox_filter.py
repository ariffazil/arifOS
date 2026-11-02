"""
tests/test_report_lane_inbox_filter.py — arif_report inbox filter defect (2026-11-02)

Defect (OBS 2026-11-01T17:14–17:16Z, session canon-attribution-verify):
  case 2: mode=inbox thread_id="canon-attribution-pintu7-20261102" returned the
          IDENTICAL 10 oldest rows as an unfiltered read. Root cause: the MCP
          wrapper (tools.py _arif_report inbox branch) never forwarded
          thread_id and report_lane.inbox() had no thread_id parameter at all —
          the tool schema accepted the argument and silently dropped it.
  cursor: result["cursor"] displayed the newest filed timestamp on every read
          but was persisted only when mark_read=True — presented as pagination
          state while default reads never advanced it.

Regression contract:
  1. inbox(thread_id=X) returns ONLY rows whose thread_id == X.
  2. inbox(since=T) returns only rows with ts strictly greater than T.
  3. the async wrapper forwards thread_id to report_lane.inbox.
  4. default reads persist no cursor; cursor_persisted states the truth.
  5. the privacy floor applies under the thread filter (no decision/blocked
     row reaches an unverified reader through any filter combination).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime import report_lane as rl
from arifosmcp.runtime import tools as rt


def _row(
    report_id: str, ts: str, thread: str, kind: str = "fyi", sender: str = "pytest:333"
) -> dict:
    return {
        "report_id": report_id,
        "ts": ts,
        "sender": sender,
        "sender_claimed": None,
        "platform": "test",
        "kind": kind,
        "subject": f"subject {report_id}",
        "body": f"body {report_id}",
        "thread_id": thread,
        "claim_state": "SELF_REPORTED",
        "escalated": False,
    }


@pytest.fixture()
def lane(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    inbox = tmp_path / "inbox.jsonl"
    cursors = tmp_path / "cursors"
    cursors.mkdir()
    rows = [
        _row("r1", "2026-11-01T10:00:00+00:00", "thread-alpha"),
        _row("r2", "2026-11-01T11:00:00+00:00", "thread-beta", kind="peer"),
        _row("r3", "2026-11-01T12:00:00+00:00", "thread-alpha"),
        _row("r4", "2026-11-01T13:00:00+00:00", "thread-alpha", kind="decision"),
    ]
    inbox.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    monkeypatch.setattr(rl, "INBOX", inbox)
    monkeypatch.setattr(rl, "CURSOR_DIR", cursors)
    return inbox


def _ids(res: dict) -> list[str]:
    return [r["report_id"] for r in res["reports"]]


# 1. thread filter — the recorded defect ──────────────────────────────────────


def test_thread_filter_returns_only_matching_rows(lane):
    res = rl.inbox(thread_id="thread-alpha", reader="pytest-unverified")
    # unverified reader: the decision row (r4) stays hidden under the filter
    assert _ids(res) == ["r1", "r3"]

    res_b = rl.inbox(thread_id="thread-beta", reader="pytest-unverified")
    assert _ids(res_b) == ["r2"]

    res_none = rl.inbox(thread_id="thread-does-not-exist", reader="pytest-unverified")
    assert _ids(res_none) == []


# 2. since filter — strict string ordering as documented ──────────────────────


def test_since_filter_keeps_only_strictly_newer_rows(lane):
    res = rl.inbox(since="2026-11-01T10:00:00+00:00", reader="pytest-unverified")
    assert _ids(res) == ["r2", "r3"]  # r4 decision hidden (unverified)


# 3. wrapper forwards thread_id (was silently dropped) ────────────────────────


def test_wrapper_forwards_thread_id(lane, monkeypatch):
    seen: dict = {}
    real_inbox = rl.inbox

    def spy(**kw):
        seen.update(kw)
        return real_inbox(**kw)

    monkeypatch.setattr(rl, "inbox", spy)
    res = asyncio.run(rt._arif_report(mode="inbox", thread_id="thread-alpha"))
    assert seen.get("thread_id") == "thread-alpha", (
        "wrapper dropped thread_id before report_lane.inbox — the 2026-11-01 defect"
    )
    reports = (res.get("result") or res).get("reports", [])
    assert [r["report_id"] for r in reports] == ["r1", "r3"]


# 4. cursor honesty ──────────────────────────────────────────────────────────


def test_default_read_does_not_persist_cursor(lane):
    res = rl.inbox(reader="pytest-cursor")
    assert res["cursor_persisted"] is False
    assert res["cursor"] == "2026-11-01T13:00:00+00:00"  # newest filed, advisory


def test_mark_read_persists_cursor_and_floors_next_read(lane):
    res = rl.inbox(reader="pytest-cursor2", mark_read=True)
    assert res["cursor_persisted"] is True
    follow = rl.inbox(reader="pytest-cursor2")
    assert follow["reports"] == []  # cursor floor applied: nothing newer filed


# 5. privacy floor survives every filter combination ─────────────────────────


def test_thread_filter_never_leaks_human_class_to_unverified(lane):
    res = rl.inbox(thread_id="thread-alpha", reader="pytest-unverified", verified_actor=False)
    assert all(r["kind"] not in ("decision", "blocked") for r in res["reports"])
    assert res.get("hidden_sensitive", 0) >= 1

    res_v = rl.inbox(thread_id="thread-alpha", reader="pytest-verified", verified_actor=True)
    assert "r4" in _ids(res_v)
