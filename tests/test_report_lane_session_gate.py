"""
tests/test_report_lane_session_gate.py — p0-kernel-anon-report-inbox-read (2026-11-18)

Defect (MEASURED 2026-11-11, RECEIPT-audit-verification-2026-11-11.md):
`tools/call arif_report {mode:"inbox"}` with NO session returned peer reports
to actor=anonymous on localhost AND on the public ingress (mcp.arif-fazil.com),
while the tool description already claimed "Requires a session from arif_init".
Label true, enforcement absent.

Fix contract: read / read-modify modes (inbox, ack, flush, stats) are gated by
_require_session — an anonymous caller gets the standard L11 AUTH hold shape.
Filing (mode=report) stays open: the peer lane is agent coordination and peer
emitters file without kernel sessions (the F13 privacy floor in report_lane
already hides HUMAN_CLASSES rows from unverified readers).

Falsifier: delete the gate block in _arif_report → the anonymous-read tests
die (rows returned instead of HOLD).
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime import tools as _tools
from arifosmcp.runtime.tools import _arif_report

GATED_MODES = ["inbox", "ack", "flush", "stats"]


class _StubSessionStore(dict):
    """dict-like stand-in carrying the two methods _require_session touches."""

    def get(self, key, default=None):  # noqa: D102 — test double
        return super().get(key, default)

    def delete(self, key):  # noqa: D102 — test double
        self.pop(key, None)


def _seed_session(monkeypatch, session_id: str, age_hours: float = 0.0) -> None:
    created = (datetime.now(timezone.utc) - timedelta(hours=age_hours)).isoformat()
    monkeypatch.setattr(
        _tools, "_SESSIONS", _StubSessionStore({session_id: {"created_at": created}})
    )


# NOTE on planes: the kernel envelope keeps transport `status` (completed) and
# the constitutional `verdict` (HOLD) separate — the R1b/R1d verdict machinery
# records the refusal on the verdict plane. Assertions live on THAT plane:
# what matters is that no rows are served to an anonymous caller.


@pytest.mark.parametrize("mode", GATED_MODES)
def test_read_modes_refuse_anonymous_caller(mode):
    out = asyncio.run(_arif_report(mode=mode))
    assert out.get("verdict") == "HOLD", f"mode={mode} must refuse an anonymous caller"
    assert out.get("effective_verdict") == "HOLD"
    reasons = " ".join(str(r) for r in out.get("reasons", []))
    assert "L11 AUTH" in reasons, "refusal must cite the session floor, not a generic error"
    assert "results" not in out and "reports" not in out, "no payload rows may leak"


@pytest.mark.parametrize("mode", GATED_MODES)
def test_read_modes_accept_bound_session(monkeypatch, mode):
    sid = f"sess-{uuid.uuid4().hex[:12]}"
    _seed_session(monkeypatch, sid)
    kwargs: dict = {"mode": mode, "session_id": sid}
    if mode == "ack":
        kwargs["report_id"] = "r-probe-nonexistent"  # lane-level miss, NOT an auth hold
    out = asyncio.run(_arif_report(**kwargs))
    reasons = " ".join(str(r) for r in out.get("reasons", []))
    assert "L11 AUTH" not in reasons, f"mode={mode} with a bound session must pass the gate"
    assert out.get("verdict") != "HOLD", f"mode={mode} with a bound session must not HOLD on auth"


def test_read_modes_refuse_expired_session(monkeypatch):
    sid = f"sess-{uuid.uuid4().hex[:12]}"
    _seed_session(monkeypatch, sid, age_hours=25.0)
    out = asyncio.run(_arif_report(mode="inbox", session_id=sid))
    assert out.get("verdict") == "HOLD", "a >24h session must not read the inbox"
    reasons = " ".join(str(r) for r in out.get("reasons", []))
    assert "L11 AUTH" in reasons


def test_filing_stays_open_for_peer_emitters():
    out = asyncio.run(
        _arif_report(
            mode="report",
            sender="pytest:peer",
            kind="fyi",
            subject="lane filing stays open",
            body="gate probe — dry run",
            dry_run=True,
        )
    )
    reasons = " ".join(str(r) for r in out.get("reasons", []))
    assert "L11 AUTH" not in reasons, "filing is the peer lane; it must not gain a session gate"
    assert out.get("verdict") != "HOLD"
