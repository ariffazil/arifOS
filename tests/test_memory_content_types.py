"""Contract tests: memory content type resilience.

Regression witness for scar_1788553451571_643a230c / BUG-555m-content-dict-strip
(found MCPJam kernel conformance 2026-09-05, FI-008).

Reality: Qdrant collection `arifos_memory` holds 99 points — 94 str + 5 dict
(test/probe points + VOID-fallback tool receipts stored as envelope dicts).
Recall filters must coerce non-str content, never crash, never drop usable
str content, and never admit null/low-score noise as signal.

Contract matrix (per 888 audit 2026-09-05):
  content: str    → passthrough
  content: dict   → coerced to JSON string, still searchable
  content: null   → filtered out (no signal)
  content: list   → coerced, does not crash
  metadata malformed → must not affect the content filter
  mixed legacy/canonical in one query → no fleet-wide crash
"""

from __future__ import annotations

import asyncio
import json

import pytest

from arifosmcp.hexagon.memory.constitutional_memory import MemoryEntry
from arifosmcp.runtime import tools_internal as ti
from arifosmcp.runtime.tools_internal import _memory_content_str
from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl


# ── Unit: _memory_content_str contract ──────────────────────────────────────


def test_content_str_passthrough():
    assert _memory_content_str("hello") == "hello"
    assert _memory_content_str("") == ""


def test_content_none_becomes_empty():
    assert _memory_content_str(None) == ""


def test_content_dict_coerces_to_json_roundtrip():
    out = _memory_content_str({"test": "hello", "n": 1})
    assert isinstance(out, str)
    assert json.loads(out) == {"test": "hello", "n": 1}


def test_content_list_coerces():
    out = _memory_content_str([1, 2, "x"])
    assert isinstance(out, str)
    assert "x" in out


def test_content_nonserializable_never_raises():
    class Weird:
        pass

    out = _memory_content_str({"obj": Weird()})  # default=str must absorb
    assert isinstance(out, str) and out  # non-empty, did not blow up


def test_content_missing_key_default():
    # simulate r.get("content", "") receiving nothing
    assert _memory_content_str("") == ""


# ── Integration: dispatch-level filter with fake store ─────────────────────


class _FakeStore:
    """Stands in for ConstitutionalMemoryStore; returns crafted entries."""

    def __init__(self, entries: list[MemoryEntry]):
        self._entries = entries
        self.initialize_calls = 0

    async def initialize_project(self, project_id: str) -> bool:
        self.initialize_calls += 1
        return True

    async def vector_query(self, query: str, limit: int = 5, **kwargs):
        return self._entries


def _entry(content, score=0.5, metadata=None) -> MemoryEntry:
    return MemoryEntry(
        content=content,
        id=f"id-{abs(hash(repr(content)[:40]))}",
        score=score,
        metadata=metadata if metadata is not None else {},
    )


def _run_recall(payload=None):
    return asyncio.run(
        engineering_memory_dispatch_impl(
            mode="query",
            payload=payload or {"query": "probe"},
            auth_context=None,
            risk_tier="low",
            dry_run=False,
            ctx=None,
        )
    )


def _patch_store(monkeypatch, entries):
    monkeypatch.setattr(ti, "_constitutional_memory_store", _FakeStore(entries))


def _payload_of(env) -> dict:
    return getattr(env, "payload", None) or {}


def test_recall_mixed_legacy_dict_and_str_no_crash(monkeypatch):
    """THE regression: one poisoned dict point must not kill the whole recall."""
    _patch_store(
        monkeypatch,
        [
            _entry({"status": "VOID", "tool": "arif_heart_critique"}),  # real poison shape
            _entry("normal string memory"),
            _entry(None),  # null content
            _entry(["legacy", "list"]),
        ],
    )
    env = _run_recall()
    results = _payload_of(env).get("results", [])
    contents = [r.get("content") for r in results]
    assert any(isinstance(c, str) and "normal string" in c for c in contents)
    # every admitted content is a str — dict poison coerced, not crashed, not leaked raw
    assert all(isinstance(c, str) for c in contents)


def test_recall_null_and_low_score_filtered(monkeypatch):
    _patch_store(
        monkeypatch,
        [
            _entry(None, score=0.9),  # null → no signal even with high score
            _entry("low score", score=0.05),  # below F2 threshold 0.1
            _entry("good", score=0.4),
        ],
    )
    env = _run_recall()
    results = _payload_of(env).get("results", [])
    assert [r["content"] for r in results] == ["good"]


def test_recall_malformed_metadata_does_not_crash_filter(monkeypatch):
    class Opaque:
        pass

    _patch_store(
        monkeypatch,
        [_entry("with weird meta", metadata={"unexpected": {"nested": Opaque()}})],
    )
    env = _run_recall()
    assert _payload_of(env).get("count", 0) == 1


def test_recall_all_empty_returns_honest_not_found(monkeypatch):
    """F2 TRUTH: zero usable matches → explicit found=False, not fabricated."""
    _patch_store(monkeypatch, [_entry(None)])
    env = _run_recall()
    payload = _payload_of(env)
    assert payload.get("found") is False
    assert payload.get("count") == 0


def test_recall_dict_content_preserves_information(monkeypatch):
    """Coerced dict must stay informative (JSON round-trippable), not str(dict) mush."""
    _patch_store(monkeypatch, [_entry({"verdict": "SABAR", "reason": "budget"})])
    env = _run_recall()
    content = _payload_of(env)["results"][0]["content"]
    parsed = json.loads(content)
    assert parsed["verdict"] == "SABAR"
