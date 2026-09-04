"""Contract tests: retrieval score propagation (bug #2).

888 audit 2026-09-05 — P1: "Repair vector_query score mapping".
Failure-before evidence: evidence/SCORE-FAIL-BEFORE.txt — adapter returned
score=0.0 for every hit while Qdrant actually returned 0.5289/0.8967
(evidence/ ground-truth probe).

Contract (per audit spec #2–#6):
  1. res.score mapped verbatim (float), never replaced by 0.0
  2. missing score → None (fail closed), metadata.score_raw = None
  3. provenance: score_raw, score_metric, collection, embedding_model,
     query_hash, retrieved_at on every hit
  4. ranking preserved (deterministic near/mid/far fixture, monotonic order)
  5. dispatch gate: score>=0.1 admits; None-score candidate NEVER admitted,
     and surfaces reason SCORE_UNAVAILABLE (not silent NO_HITS)
  6. reasons: NO_VECTOR_HITS / NO_HITS_ABOVE_THRESHOLD / SCORE_UNAVAILABLE
     with candidate_count, threshold, top_score_raw
  7. legacy dict content + real score → admitted, coerced, flagged
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

import arifosmcp.hexagon.memory.constitutional_memory as cm
from arifosmcp.hexagon.memory.constitutional_memory import (
    ConstitutionalMemoryStore,
    MemoryEntry,
)
from arifosmcp.runtime import tools_internal as ti
from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl


# ── Deterministic fixture: fake Qdrant client + fake embedding ──────────────


class _FakeQdrantClient:
    def __init__(self, points):
        self._points = points
        self.last_query_vector = None

    def query_points(self, collection_name, query, limit, with_payload=True):
        self.last_query_vector = query
        return SimpleNamespace(points=self._points[:limit])


def _point(pid, score, content):
    return SimpleNamespace(
        id=pid,
        score=score,
        payload={"content": content, "metadata": {"origin": "fixture"}},
    )


FIXTURE = [
    _point("near", 0.91, "alpha document nearest to query"),
    _point("mid", 0.50, "beta document middle relevance"),
    _point("far", 0.05, "gamma document far from query"),
]


@pytest.fixture
def patched_store(monkeypatch):
    monkeypatch.setattr(cm, "_get_qdrant_client", lambda: _FakeQdrantClient(FIXTURE))
    monkeypatch.setattr(cm, "_generate_embedding", lambda text: [0.1] * 8)
    return ConstitutionalMemoryStore()


# ── Adapter unit contract ───────────────────────────────────────────────────


def test_scores_mapped_verbatim_not_zeroed(patched_store):
    entries = asyncio.run(patched_store.vector_query("probe", limit=5))
    scores = [e.score for e in entries]
    assert scores == [0.91, 0.50, 0.05]  # verbatim, ranked as returned
    assert all(s != 0.0 for s in scores)


def test_missing_score_becomes_none_not_zero(monkeypatch):
    pts = [_point("noscore", None, "content without score")]
    monkeypatch.setattr(cm, "_get_qdrant_client", lambda: _FakeQdrantClient(pts))
    monkeypatch.setattr(cm, "_generate_embedding", lambda t: [0.1] * 8)
    store = ConstitutionalMemoryStore()
    entries = asyncio.run(store.vector_query("probe"))
    assert entries[0].score is None
    assert entries[0].metadata["score_raw"] is None


def test_provenance_attached_to_every_hit(patched_store):
    entries = asyncio.run(patched_store.vector_query("probe", limit=3))
    for e in entries:
        m = e.metadata
        assert m["score_metric"] == "cosine"
        assert m["collection"] == "arifos_memory"
        assert isinstance(m["embedding_model"], str) and m["embedding_model"]
        assert len(m["query_hash"]) == 16
        assert "T" in m["retrieved_at"]  # ISO timestamp
        assert m["origin"] == "fixture"  # original payload metadata preserved


def test_ranking_monotonic_with_fixture(patched_store):
    entries = asyncio.run(patched_store.vector_query("probe", limit=3))
    assert [e.id for e in entries] == ["near", "mid", "far"]
    scores = [e.score for e in entries]
    assert scores == sorted(scores, reverse=True)


# ── Dispatch-level gate + reason taxonomy ──────────────────────────────────


class _FakeStore:
    def __init__(self, entries):
        self._entries = entries

    async def initialize_project(self, project_id):
        return True

    async def vector_query(self, query, limit=5, **kwargs):
        return self._entries


def _entry(content, score, metadata=None):
    return MemoryEntry(content=content, id=f"id-{abs(hash(repr(content)[:32]))}", score=score, metadata=metadata or {})


def _recall(monkeypatch, entries, query="probe"):
    monkeypatch.setattr(ti, "_constitutional_memory_store", _FakeStore(entries))
    env = asyncio.run(
        engineering_memory_dispatch_impl(
            mode="query",
            payload={"query": query},
            auth_context=None,
            risk_tier="low",
            dry_run=False,
            ctx=None,
        )
    )
    return getattr(env, "payload", None) or {}


def test_real_scores_now_admitted_found_true(monkeypatch):
    """THE bug-#2 regression: real scores must pass the gate (0.0-era → always found=False)."""
    p = _recall(monkeypatch, [_entry("relevant doc", 0.53), _entry("weak doc", 0.45)])
    assert p.get("found") is True
    assert p.get("count") == 2
    assert p["results"][0]["score"] == 0.53


def test_none_score_never_admitted_and_reason_scores_unavailable(monkeypatch):
    p = _recall(monkeypatch, [_entry("good content, no signal", None)])
    assert p.get("found") is False
    assert p.get("reason") == "SCORE_UNAVAILABLE"
    assert p.get("candidate_count") == 1
    assert p.get("top_score_raw") is None


def test_reason_no_vector_hits_on_empty(monkeypatch):
    p = _recall(monkeypatch, [])
    assert p.get("reason") == "NO_VECTOR_HITS"
    assert p.get("candidate_count") == 0


def test_reason_no_hits_above_threshold(monkeypatch):
    p = _recall(monkeypatch, [_entry("too far", 0.04), _entry("also far", 0.02)])
    assert p.get("reason") == "NO_HITS_ABOVE_THRESHOLD"
    assert p.get("candidate_count") == 2
    assert p.get("threshold") == 0.1
    assert p.get("top_score_raw") == 0.04


def test_legacy_dict_with_real_score_admitted_and_flagged(monkeypatch):
    p = _recall(monkeypatch, [_entry({"status": "VOID", "tool": "x"}, 0.53)])
    assert p.get("found") is True
    r = p["results"][0]
    assert isinstance(r["content"], str)
    assert r.get("content_coerced") is True
    assert r["score"] == 0.53
    assert p.get("content_coerced_count") == 1


def test_mixed_none_and_real_score_admits_only_scored(monkeypatch):
    p = _recall(monkeypatch, [_entry("unscored", None), _entry("scored", 0.6)])
    assert p.get("found") is True
    assert p.get("count") == 1
    assert p["results"][0]["content"] == "scored"


# ── POLICY 2026-09-05 (888): text-schema fallback — 57 dossier points ──────


def _text_point(pid, score, subject, text):
    return SimpleNamespace(
        id=pid,
        score=score,
        payload={"subject": subject, "text": text, "category": "dossier", "ts": "2026-08-11"},
    )


def test_text_schema_point_served_via_fallback(monkeypatch):
    pts = [
        _text_point("d1", 0.62, "Sovereign Decrees", "Full text of sovereign decree number four"),
        _point("c1", 0.40, "ordinary content point"),
    ]
    monkeypatch.setattr(cm, "_get_qdrant_client", lambda: _FakeQdrantClient(pts))
    monkeypatch.setattr(cm, "_generate_embedding", lambda t: [0.1] * 8)
    store = ConstitutionalMemoryStore()
    entries = asyncio.run(store.vector_query("sovereign decree"))
    d = entries[0]
    assert d.metadata["content_source"] == "text_fallback"
    assert "[Sovereign Decrees]" in d.content and "decree number four" in d.content
    assert d.score == 0.62
    assert entries[1].metadata["content_source"] == "content"


def test_text_fallback_survives_dispatch_gate(monkeypatch):
    from arifosmcp.runtime import tools_internal as ti2
    from arifosmcp.hexagon.memory.constitutional_memory import MemoryEntry as ME

    entry = ME(content="[Dossier] sample dossier text", id="d1", score=0.6,
               metadata={"content_source": "text_fallback"})
    monkeypatch.setattr(ti2, "_constitutional_memory_store", _FakeStore([entry]))
    env = asyncio.run(
        engineering_memory_dispatch_impl(
            mode="query", payload={"query": "dossier"},
            auth_context=None, risk_tier="low", dry_run=False, ctx=None,
        )
    )
    p = getattr(env, "payload", None) or {}
    assert p.get("found") is True
    assert p["results"][0]["metadata"]["content_source"] == "text_fallback"


def test_absent_content_and_no_text_yields_empty_not_crash(monkeypatch):
    pts = [SimpleNamespace(id="z", score=0.7, payload={"category": "orphan"})]
    monkeypatch.setattr(cm, "_get_qdrant_client", lambda: _FakeQdrantClient(pts))
    monkeypatch.setattr(cm, "_generate_embedding", lambda t: [0.1] * 8)
    entries = asyncio.run(ConstitutionalMemoryStore().vector_query("q"))
    assert entries[0].content == ""
    assert entries[0].metadata["content_source"] == "content"  # no fallback fired
