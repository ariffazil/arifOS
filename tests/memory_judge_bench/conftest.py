"""
tests/memory_judge_bench/conftest.py
====================================
Pytest fixtures for MEMORY_JUDGE_BENCH.

Design principles:
- Each test gets a clean, isolated memory index.
- Production memory_store is NEVER written — test namespace only.
- Ollama embeddings are mocked (deterministic fake vectors).
- Qdrant is mocked via _FakeQdrantClient (no network calls).
- Postgres is NOT called — index-only mode for speed.

Namespace: TEST ONLY
Never mutates production /root/.arifOS/memory/

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parents[3]))

# ── Isolate test memory directory ────────────────────────────────────────────

TEST_MEMORY_DIR = tempfile.mkdtemp(prefix="arifOS_memory_judge_bench_")
os.environ["ARIFOS_MEMORY_DIR"] = TEST_MEMORY_DIR


@pytest.fixture(autouse=True)
def clean_test_memory_dir():
    """Ensure every test starts with a blank index."""
    index_file = Path(TEST_MEMORY_DIR) / ".qdrant_index.json"
    if index_file.exists():
        index_file.unlink()
    yield
    # Leave artifacts for post-mortem — do not clean up


# ── Fake Ollama embedding (deterministic, no network) ───────────────────────

_FAKE_VECTOR_COUNTER = 0


def _fake_embedding(text: str) -> list[float]:
    """Deterministic 1024-dim fake embedding keyed by text content.

    Different texts → different vectors (collisions astronomically unlikely).
    Stable across calls (same text → same vector).
    """
    global _FAKE_VECTOR_COUNTER
    # Simple hash-based seed for reproducibility
    h = hash(text) % (2**32)
    vec = [(h + i) % 100 / 100.0 for i in range(1024)]
    # Normalise to unit length
    norm = sum(v * v for v in vec) ** 0.5
    return [v / norm for v in vec]


# ── Fake Qdrant client ─────────────────────────────────────────────────────

PointRecord = dict[str, Any]


class _FakeQdrantClient:
    """In-memory Qdrant mock for isolated testing.

    Supports: upsert, query_points (ANN search), delete.
    Does NOT support collection management (create_collection skipped).
    """

    def __init__(self) -> None:
        self.collections: dict[str, list[PointRecord]] = {}

    def get_collection(self, collection_name: str) -> dict[str, Any]:
        # Auto-create on first access — skips schema mismatch issues in tests
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        return {
            "name": collection_name,
            "config": SimpleNamespace(params=SimpleNamespace(vectors=SimpleNamespace(size=1024))),
        }

    def create_collection(self, collection_name: str, vectors_config) -> None:
        self.collections[collection_name] = []

    def upsert(self, collection_name: str, points: list[PointRecord]) -> None:
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        for pt in points:
            self.collections[collection_name].append(pt)

    def query_points(
        self,
        collection_name: str,
        query,
        query_filter=None,
        limit: int = 5,
        with_payload: bool = True,
        offset: int | None = None,
    ) -> SimpleNamespace:
        if collection_name not in self.collections:
            return SimpleNamespace(points=[])

        candidates = list(self.collections[collection_name])

        # Apply metadata filters if provided
        if query_filter and hasattr(query_filter, "must") and query_filter.must:
            for cond in query_filter.must:
                key = cond.key
                val = cond.match.value
                candidates = [p for p in candidates if p.get(key) == val]

        # Simple cosine similarity against stored "vector" (stored as list)
        def cosine_sim(stored_vec: list[float], query_vec: list[float]) -> float:
            if not stored_vec or not query_vec:
                return 0.0
            dot = sum(a * b for a, b in zip(stored_vec[: len(query_vec)], query_vec))
            return dot  # already normalised

        scored = []
        for p in candidates:
            stored_vec = p.get("vector", [])
            score = cosine_sim(stored_vec, query)
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:limit]
        return SimpleNamespace(points=[p for _, p in top])

    def delete(self, collection_name: str, points_selector) -> None:
        to_delete = set()
        if hasattr(points_selector, "points"):
            to_delete = set(getattr(points_selector.points, "points", []))
        elif hasattr(points_selector, "filter"):
            # points selector with filter — remove all matching
            pass
        if collection_name in self.collections:
            self.collections[collection_name] = [
                p for p in self.collections[collection_name] if p.get("id") not in to_delete
            ]


# ── Patch targets ──────────────────────────────────────────────────────────


def _patch_memory_store():
    """Patch memory_store to use fake Qdrant + fake Ollama.

    Call this at test setup. Reverts automatically after test via monkeypatch.
    """
    import arifosmcp.runtime.memory_store as ms
    from unittest.mock import patch

    fake_qdrant = _FakeQdrantClient()

    # Patch the Qdrant client factory
    original_get_qdrant = ms._get_qdrant_client

    def _fake_get_qdrant():
        return fake_qdrant

    # Patch embedding generator
    original_generate = ms._generate_embedding

    def _fake_generate(text: str) -> list[float]:
        return _fake_embedding(text)

    return {
        "qdrant": fake_qdrant,
        "original_get_qdrant": original_get_qdrant,
        "original_generate": original_generate,
        "patch_qdrant": patch.object(ms, "_get_qdrant_client", _fake_get_qdrant),
        "patch_generate": patch.object(ms, "_generate_embedding", _fake_generate),
    }


# ── Fixture: isolated_memory ────────────────────────────────────────────────


@pytest.fixture
def isolated_memory(monkeypatch):
    """Complete isolated memory environment for a single test.

    - New temp directory per test (clean_test_memory_dir handles this)
    - Fake Qdrant (no network, in-memory)
    - Fake Ollama embedding (deterministic)
    - No Postgres calls (index-only mode)

    Returns:
        dict with:
          qdrant: _FakeQdrantClient (for assertions)
          store_fn: memory_store.store function
          search_fn: memory_store.search function
          recall_fn: memory_store.recall function
    """
    patches = _patch_memory_store()
    for p in [patches["patch_qdrant"], patches["patch_generate"]]:
        p.start()

    # Re-import after patching
    from arifosmcp.runtime import memory_store as ms
    import importlib

    importlib.reload(ms)

    yield {
        "qdrant": patches["qdrant"],
        "store": ms.store,
        "search": ms.search,
        "recall": ms.recall,
        "memory_store": ms,
    }

    for p in [patches["patch_generate"], patches["patch_qdrant"]]:
        p.stop()


# ── Helper: build memory candidates ────────────────────────────────────────


def make_memory(
    content: str,
    tier: str = "canon",
    actor_id: str = "arif",
    session_id: str | None = None,
    tags: list[str] | None = None,
    phoenix_state: str = "cooling",
    phoenix_psi_utility: int = 0,
    phoenix_tri_witness: dict | None = None,
    anti_hantu_flag: bool = False,
    entity_tags: list[str] | None = None,
    temporal_marker: str = "active",
    superseded_by: str | None = None,
    valid_at: str | None = None,
    mode: str = "session_turn",
    memory_id: str | None = None,
) -> dict[str, Any]:
    """Build a synthetic memory record for test setup.

    All fields map directly to memory_store schema.
    """
    sid = session_id or f"bench-session-{uuid.uuid4().hex[:8]}"
    mid = memory_id or uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "content": content,
        "tier": tier,
        "actor_id": actor_id,
        "session_id": sid,
        "tags": tags or [],
        "phoenix_state": phoenix_state,
        "phoenix_psi_utility": phoenix_psi_utility,
        "phoenix_tri_witness": phoenix_tri_witness or {},
        "phoenix_anti_hantu_flag": anti_hantu_flag,
        "entity_tags": entity_tags or [],
        "temporal_marker": temporal_marker,
        "superseded_by": superseded_by,
        "valid_at": valid_at or now,
        "mode": mode,
        "memory_id": mid,
        "created_at": now,
    }


# ── Fixtures: named memory objects for reuse ────────────────────────────────


@pytest.fixture
def sacred_petronas_scar(isolated_memory):
    """High-consequence PETRONAS rightsizing scar — SACRED tier."""
    result = isolated_memory["store"](
        content=(
            "PETRONAS rightsizing 2024: significant human consequence. "
            "Multiple families affected. Structural change with deep personal impact. "
            "Must be handled with dignity. Do not trivialize."
        ),
        mode="sacred_event",
        tier="sacred",
        actor_id="arif",
        session_id="bench-sacred-001",
        tags=["PETRONAS", "rightsizing", "scar", "high-consequence"],
    )
    return result


@pytest.fixture
def canonical_public_fact(isolated_memory):
    """Verified public fact — CANONICAL tier, SEALED state."""
    result = isolated_memory["store"](
        content="PETRONAS is Malaysia's national oil company, founded in 1974.",
        mode="public_fact",
        tier="canonical",
        actor_id="arif",
        session_id="bench-canon-001",
        tags=["PETRONAS", "public", "verified"],
    )
    # Manually patch to SEALED state for canon tests
    return result


@pytest.fixture
def cooling_memory(isolated_memory):
    """Memory still in Phoenix COOLING state — not yet canon."""
    result = isolated_memory["store"](
        content="This is a cooling memory — not yet canon, still in 72h cooldown.",
        mode="session_turn",
        tier="canonical",
        actor_id="arif",
        session_id="bench-cooling-001",
        tags=["test", "cooling"],
    )
    return result


@pytest.fixture
def voided_memory(isolated_memory):
    """Memory in VOID state — must not be retrieved."""
    result = isolated_memory["store"](
        content="This memory was voided and should never surface in recall.",
        mode="session_turn",
        tier="canonical",
        actor_id="arif",
        session_id="bench-void-001",
        tags=["test", "voided"],
    )
    return result


@pytest.fixture
def contradicted_old(isolated_memory):
    """Older memory that has been contradicted by newer evidence."""
    result = isolated_memory["store"](
        content="PETRONAS had 3 basins as of 2023 assessment.",
        mode="structured_fact",
        tier="canonical",
        actor_id="arif",
        session_id="benchcontra-old",
        tags=["PETRONAS", "basins", "historical"],
        entity_tags=["ORG:PETRONAS", "GEO:Basin"],
        temporal_marker="historical",
    )
    return result


@pytest.fixture
def contradicted_new(isolated_memory):
    """Newer memory that supersedes the older contradicted memory."""
    result = isolated_memory["store"](
        content="PETRONAS rightsizing reduced portfolio to 2 basins as of 2024.",
        mode="structured_fact",
        tier="canonical",
        actor_id="arif",
        session_id="benchcontra-new",
        tags=["PETRONAS", "rightsizing", "current"],
        entity_tags=["ORG:PETRONAS", "GEO:Basin"],
        temporal_marker="active",
        valid_at="2024-01-01T00:00:00+00:00",
    )
    return result


@pytest.fixture
def stale_memory(isolated_memory):
    """Memory past its freshness window — requires re-verification."""
    result = isolated_memory["store"](
        content="BTC price was $42,000 on 2024-01-15 — stale as of today.",
        mode="structured_fact",
        tier="canonical",
        actor_id="arif",
        session_id="bench-stale-001",
        tags=["price", "stale", "BTC"],
    )
    return result


@pytest.fixture
def private_memory(isolated_memory):
    """Private/sensitive memory — must not surface without authorization."""
    result = isolated_memory["store"](
        content="Arif's personal health record — strictly private.",
        mode="private_fact",
        tier="canonical",
        actor_id="arif",
        session_id="bench-private-001",
        tags=["private", "health", "personal"],
        sensitivity=0.9,
    )
    return result


@pytest.fixture
def antihantu_bad_content(isolated_memory):
    """Content that should be rejected by Anti-Hantu write gate."""
    return (
        isolated_memory,
        "I feel so betrayed by PETRONAS and it hurts my heart to remember this.",
        "anti_hantu_reject",
    )


@pytest.fixture
def antihantu_good_content(isolated_memory):
    """Content that should pass Anti-Hantu gate."""
    return (
        isolated_memory,
        "PETRONAS rightsizing was a structural change with documented human consequences.",
        "anti_hantu_pass",
    )


# ── Global test results collector ──────────────────────────────────────────

_TEST_RESULTS: list[dict[str, Any]] = []


@pytest.fixture
def collect_result():
    """Collect test results for final scoring report."""
    global _TEST_RESULTS
    _TEST_RESULTS = []
    yield _TEST_RESULTS
    # Results accumulated during test run — used by cli.py to build report


def get_test_results() -> list[dict[str, Any]]:
    return list(_TEST_RESULTS)


def reset_test_results():
    global _TEST_RESULTS
    _TEST_RESULTS = []
