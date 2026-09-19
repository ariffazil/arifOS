"""KITARAN Tuas 2 — arifOS MCP dispatch invocation telemetry (in-process proof).

WHAT IS PROVEN HERE (and nothing more):

  (i)   a real call through the instrumented dispatch path lands a receipt in
        the shared sink, in the frozen federation format;
  (ii)  a failure INSIDE the logger cannot break the tool call — telemetry is
        additive, never load-bearing;
  (iii) the readback (exercise_count) counts those receipts, so the
        CER/ASD numerator stops being a numbered PROXY.

WHY: the 2026-09-19 KITARAN audit found only ONE organ (GEOX) kept a real
invocation log, so every ceremony/exercise measurement rested on a proxy.
arifOS emitted thousands of doctrine artifacts and never recorded which one
was actually used.

THE PATH UNDER TEST: arifosmcp.runtime.tools._wrap_handler — the live per-tool
dispatch boundary. register_tools() wraps every canonical tool with it (and
server.py does the same for the rest). Under fastmcp 4.x the FastMCP Middleware
chain is NOT attached (server.py gates it on `fastmcp.__version__.startswith("3")`),
so ingress_middleware.on_call_tool is not the live call site — this wrapper is.

ISOLATION: the shared sink is redirected to tmp_path (monkeypatched LOG_PATH)
and ARIFOS_HOME is redirected away from /root. The production sink
(/var/lib/arifos/metrics/tool_invocations.jsonl) must never receive a test row.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SHARED_CONTRACT = "/root/AAA/lib/invocation_log.py"

# Receipt keys permitted by the frozen contract — anything else would be
# argument/payload leakage into telemetry.
_ALLOWED_KEYS = {
    "ts",
    "organ",
    "tool",
    "actor_id",
    "ok",
    "duration_ms",
    "session_id",
    "epoch",
    "host",
    "error",
    "extra",
}


def _shared_module():
    """Load the frozen federation contract by path — never vendored."""
    mod = sys.modules.get("invocation_log")
    if mod is None:
        spec = importlib.util.spec_from_file_location("invocation_log", SHARED_CONTRACT)
        assert spec is not None and spec.loader is not None, SHARED_CONTRACT
        mod = importlib.util.module_from_spec(spec)
        # Register BEFORE exec_module — the module carries postponed annotations.
        sys.modules["invocation_log"] = mod
        spec.loader.exec_module(mod)
    return mod


def _receipts(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


@pytest.fixture()
def sink(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the shared telemetry sink to tmp, and ARIFOS_HOME off /root."""
    monkeypatch.setenv("ARIFOS_HOME", str(tmp_path))
    mod = _shared_module()
    path = tmp_path / "tool_invocations.jsonl"
    monkeypatch.setattr(mod, "LOG_PATH", path)
    return path


async def test_dispatch_call_lands_receipt_in_tmp_sink(sink: Path) -> None:
    """(i) A real call through _wrap_handler writes one receipt to the sink."""
    from arifosmcp.runtime.tools import _wrap_handler

    async def probe_tool(actor_id: str | None = None, session_id: str | None = None):
        return {"status": "OK", "result": {"probe": True}}

    wrapped = _wrap_handler(probe_tool, "kitaran_probe_tool")
    result = await wrapped(actor_id="KITARAN-TEST-ACTOR", session_id="KITARAN-TEST-SESS")

    assert result is not None, "dispatch path must still return a response"

    recs = _receipts(sink)
    assert len(recs) == 1, f"expected exactly one receipt, got {recs}"
    rec = recs[0]

    assert rec["organ"] == "arifOS"
    assert rec["tool"] == "kitaran_probe_tool"
    assert rec["actor_id"] == "KITARAN-TEST-ACTOR"
    assert rec["session_id"] == "KITARAN-TEST-SESS"
    assert rec["ok"] is True
    assert isinstance(rec["duration_ms"], float)

    # PRIVACY BOUNDARY: a tool name is MAP, an argument is STORY.
    assert set(rec) <= _ALLOWED_KEYS, f"unexpected receipt keys: {set(rec) - _ALLOWED_KEYS}"
    assert "arguments" not in rec
    assert "result" not in rec


async def test_failed_dispatch_is_receipted_as_failure(sink: Path) -> None:
    """A raising handler still produces a receipt (ok=False) — failures count too."""
    from arifosmcp.runtime.tools import _wrap_handler

    async def boom_tool(actor_id: str | None = None, session_id: str | None = None):
        raise RuntimeError("deliberate failure")

    wrapped = _wrap_handler(boom_tool, "kitaran_boom_tool")
    result = await wrapped(actor_id="KITARAN-TEST-ACTOR")  # must not raise

    assert result is not None
    recs = _receipts(sink)
    assert len(recs) == 1, f"expected exactly one receipt, got {recs}"
    assert recs[0]["tool"] == "kitaran_boom_tool"
    assert recs[0]["ok"] is False
    assert recs[0]["error"] == "RuntimeError"


async def test_logger_explosion_cannot_break_the_tool_call(
    sink: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """(ii) If the logger itself raises, the tool call must still complete."""
    from arifosmcp.runtime.tools import _wrap_handler

    mod = _shared_module()

    def _explode(*_args, **_kwargs):
        raise RuntimeError("telemetry exploded")

    monkeypatch.setattr(mod, "log_invocation", _explode)

    calls = {"n": 0}

    async def probe_tool(actor_id: str | None = None, session_id: str | None = None):
        calls["n"] += 1
        return {"status": "OK", "result": {"survived": True}}

    wrapped = _wrap_handler(probe_tool, "kitaran_probe_tool")
    result = await wrapped(actor_id="KITARAN-TEST-ACTOR")

    assert calls["n"] == 1, "the handler must have really run"
    # A response still came back from the dispatch of OUR tool — the logger
    # exploding changed nothing observable.
    assert isinstance(result, dict) and result.get("tool") == "kitaran_probe_tool"
    assert _receipts(sink) == [], "nothing written — and nothing broken"


async def test_unavailable_shared_module_cannot_break_the_tool_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing/broken shared module is a silent no-op, never a tool failure."""
    import arifosmcp.runtime.tools as tools_mod

    monkeypatch.setenv("ARIFOS_HOME", str(tmp_path))
    monkeypatch.delitem(sys.modules, "invocation_log", raising=False)
    monkeypatch.setattr(tools_mod, "_INVOCATION_LOG_PATH", str(tmp_path / "absent.py"))

    async def probe_tool(actor_id: str | None = None, session_id: str | None = None):
        return {"status": "OK", "result": {"survived": True}}

    wrapped = tools_mod._wrap_handler(probe_tool, "kitaran_probe_tool")
    result = await wrapped(actor_id="KITARAN-TEST-ACTOR")

    assert isinstance(result, dict) and result.get("tool") == "kitaran_probe_tool"
    assert not (tmp_path / "absent.py").exists()


def test_readback_counts_receipts_from_the_wiring(sink: Path) -> None:
    """(iii) exercise_count() reads back what the wiring wrote — no proxy."""
    from arifosmcp.runtime.tools import _record_invocation

    _record_invocation("kitaran_probe_tool", actor_id="ACTOR-A", ok=True, duration_ms=3.0)
    _record_invocation("kitaran_probe_tool", actor_id="ACTOR-B", ok=False, error="RuntimeError")
    _record_invocation("kitaran_other_tool", actor_id="ACTOR-A", ok=True, duration_ms=1.0)

    counts = _shared_module().exercise_count("arifOS", 30, path=sink)

    assert counts["total"] == 3
    assert counts["distinct_tools"] == 2
    assert counts["distinct_actors"] == 2
    assert counts["failed"] == 1
    assert counts["unparsable"] == 0
    assert counts["organs_seen"] == ["arifOS"]
