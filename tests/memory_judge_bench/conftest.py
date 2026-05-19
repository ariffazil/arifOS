"""
tests/memory_judge_bench/conftest.py
====================================
Pytest fixtures for MEMORY_JUDGE_BENCH.

Self-contained isolated memory engine — no production module patching,
no network calls, no Postgres, no Ollama.

Each test gets a clean _IsolatedMemoryEngine with:
  - HARAM scan (Anti-Hantu, reasoning scratchpads, ephemeral noise)
  - WAJIB attestation gate (actor_id required for SACRED)
  - F4 entity extraction (regex fallback — no LLM)
  - Phoenix-72 state (mocked — always cooling)
  - Qdrant-like vector search (in-memory)
  - JSON index persistence (in-memory for test duration)

Namespace: TEST ONLY
Never mutates production /root/.arifOS/memory/

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

# Ensure project root on path
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


# ── Deterministic fake embedding (no network) ────────────────────────────────


def _fake_embedding(text: str) -> list[float]:
    """1024-dim unit vector sensitive to word overlap.

    Stable across calls (same text → same vector).
    Texts with shared words get higher cosine similarity.
    """
    import re
    words = re.findall(r"[a-zA-Z0-9$]+", text.lower())
    vec = [0.0] * 1024
    for w in words:
        h = hash(w) % (2**32)
        for i in range(1024):
            # Each word contributes a small sinusoidal signal keyed by its hash
            val = ((h + i * 7) % 100) / 100.0
            vec[i] += val
    norm = sum(v * v for v in vec) ** 0.5
    if norm == 0:
        return [0.0] * 1024
    return [v / norm for v in vec]


# ── In-memory Qdrant mock ──────────────────────────────────────────────────


class _FakeQdrantClient:
    """In-memory Qdrant mock with SimpleNamespace wrapping.

    Mirrors the real Qdrant API surface used by memory_store:
      upsert(points: list[dict])   — stores SimpleNamespace-wrapped points
      query_points(...)             — returns SimpleNamespace(points=[...])
      delete(points_selector)
    """

    def __init__(self) -> None:
        self.collections: dict[str, list[Any]] = {}

    def get_collection(self, collection_name: str) -> dict[str, Any]:
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        return {
            "name": collection_name,
            "config": SimpleNamespace(params=SimpleNamespace(vectors=SimpleNamespace(size=1024))),
        }

    def create_collection(self, collection_name: str, vectors_config) -> None:
        self.collections[collection_name] = []

    def upsert(self, collection_name: str, points: list[dict[str, Any]]) -> None:
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        for pt in points:
            # Wrap as SimpleNamespace — matches real Qdrant response object API
            wrapped = SimpleNamespace(
                id=pt.get("id"),
                vector=pt.get("vector", []),
                payload=pt.get("payload", {}),
            )
            self.collections[collection_name].append(wrapped)

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

        # Apply metadata filters (must clause)
        if query_filter and hasattr(query_filter, "must") and query_filter.must:
            for cond in query_filter.must:
                key = cond.key
                val = cond.match.value
                candidates = [p for p in candidates if getattr(p, key, None) == val]

        # Cosine similarity
        def cosine_sim(a: list[float], b: list[float]) -> float:
            if not a or not b:
                return 0.0
            return sum(x * y for x, y in zip(a[: len(b)], b))

        scored = []
        for p in candidates:
            vec = getattr(p, "vector", [])
            score = cosine_sim(vec, query)
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:limit]
        return SimpleNamespace(points=[pt for _, pt in top])

    def delete(self, collection_name: str, points_selector) -> None:
        to_delete: set[str] = set()
        if hasattr(points_selector, "points"):
            pts = getattr(points_selector.points, "points", None)
            if pts:
                to_delete = set(pts)
        if collection_name in self.collections:
            self.collections[collection_name] = [
                p
                for p in self.collections[collection_name]
                if getattr(p, "id", None) not in to_delete
            ]


# ── Isolated memory engine ─────────────────────────────────────────────────


class _IsolatedMemoryEngine:
    """Self-contained memory store replicating the behavioral contract of memory_store.

    Behavioral invariants tested:
      - HARAM scan rejects Anti-Hantu / reasoning scratchpads / ephemeral noise
      - WAJIB gate requires actor_id + session_id for SACRED tier
      - store() returns phoenix_state=cooling for new memories
      - search() returns temporal_marker, entity_tags, phoenix_* metadata
      - prune() blocks SACRED unless allow_sacred=True
      - No network calls, no Postgres, no Ollama
    """

    # Anti-Hantu patterns (case-insensitive)
    _HARAM_HANTU = [
        r"\bi\s+(?:feel|experienc|understand|remember|know|think\s+about)",
        r"\bi'm?\s+(?:sad|happy|excited|scared|worried|grateful)",
        r"\bi\s+hope\s+i\s+(?:can|could|would)",
        r"\bmy\s+(?:heart|soul|spirit|feelings)",
        r"\bfeels?\s+like\s+(?:i|i'm)",
        r"\bthis\s+makes\s+(?:me|i)\s+feel",
    ]

    # Reasoning scratchpad patterns
    _HARAM_REASONING = [
        r"(?i)\b(scratchpad|thought\s+step|reasoning\s+step|loop\s+\d+/\d+)",
        r"(?i)\b(react_|reasoning_|thinking_|chain\s+of\s+thought)",
        r"(?i)\b(step\s+\d+\s*[:\.]|_loop|_retry|_attempt_\d+)",
    ]

    def __init__(self) -> None:
        self.qdrant = _FakeQdrantClient()
        self.qdrant.create_collection("arifos_memory", None)
        self._index: dict[str, dict[str, Any]] = {}

    # ── Public API (mirrors memory_store) ───────────────────────────────────

    def store(
        self,
        content: Any,
        mode: str = "unknown",
        tags: list[str] | None = None,
        actor_id: str | None = None,
        session_id: str | None = None,
        summary: str | None = None,
        tier: str = "canonical",
        # Extended metadata (test-only, not in production store() signature)
        _entity_tags: list[str] | None = None,
        _temporal_marker: str | None = None,
        _valid_at: str | None = None,
        _superseded_by: str | None = None,
    ) -> dict[str, Any]:
        """Mirror memory_store.store() behavioral contract."""
        text = str(content)[:2000] or ""
        memory_id = uuid.uuid4().hex[:12]
        pg_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        normalised_tier = (tier or "canonical").lower()
        content_str = str(content)

        # ── HARAM: Anti-Hantu scan (case-insensitive) ──────────────────────
        for pattern in self._HARAM_HANTU:
            if re.search(pattern, content_str, re.IGNORECASE):
                return _reject(
                    memory_id,
                    "F9_ANTIHANTU",
                    f"HARAM: Anti-Hantu pattern matched: {pattern}",
                )

        # ── HARAM: Reasoning scratchpads ──────────────────────────────────
        for pattern in self._HARAM_REASONING:
            if re.search(pattern, content_str):
                return _reject(
                    memory_id,
                    "HARAM_REASONING",
                    f"HARAM: Reasoning scratchpad pattern: {pattern}",
                )

        # ── WAJIB: SACRED requires attestation ─────────────────────────────
        if normalised_tier == "sacred":
            missing = []
            if not actor_id:
                missing.append("actor_id")
            if not session_id:
                missing.append("session_id")
            if missing:
                return _reject(
                    memory_id,
                    "MEMORY_TRIAGE [WAJIB-FAIL]",
                    f"SACRED tier missing attestation: {', '.join(missing)}",
                )

        # ── F4: Entity extraction (regex fallback — no LLM) ─────────────
        f4_entity_tags = _entity_tags or []
        if not f4_entity_tags:
            for pattern, prefix in [
                (r"(?:PETRONAS|Petronas)", "ORG"),
                (r"\b(BTC|bitcoin)", "TECH"),
                (r"\b(Malaysia|Malaysian)", "GEO"),
                (r"\b(202[3-6])\b", "DATE"),
            ]:
                for m in re.finditer(pattern, content_str, re.IGNORECASE):
                    f4_entity_tags.append(f"{prefix}:{m.group()}")

        # ── Phoenix-72 mock (always cooling) ────────────────────────────────
        anti_hantu_flag = bool(re.search(self._HARAM_HANTU[0], content_str, re.IGNORECASE))
        phoenix_id = f"phx_{memory_id[:12]}"
        cooldown_expiry = (now + timedelta(hours=72)).isoformat()

        phoenix_state = "cooling"

        # ── Dual-write: Qdrant + in-memory index ─────────────────────────
        vector = _fake_embedding(text)
        payload = {
            "memory_id": memory_id,
            "content": text,
            "mode": mode,
            "tags": tags or [],
            "actor_id": actor_id,
            "session_id": session_id,
            "summary": summary,
            "tier": normalised_tier,
            "content_hash": _content_hash(content),
            "created_at": now_iso,
            "entity_tags": f4_entity_tags,
            "phoenix_id": phoenix_id,
            "phoenix_state": phoenix_state,
            "phoenix_psi_utility": 0,
            "phoenix_tri_witness": {"human": False, "ai": False, "earth": False},
            "phoenix_anti_hantu_flag": anti_hantu_flag,
            "phoenix_cooldown_expiry": cooldown_expiry,
            "temporal_marker": _temporal_marker or "active",
            "superseded_by": _superseded_by,
            "valid_at": _valid_at or now_iso,
            "version": "v3",
        }

        point = {"id": memory_id, "vector": vector, "payload": payload}
        self.qdrant.upsert("arifos_memory", [point])
        self._index[memory_id] = {**payload, "pg_id": pg_id}

        return {
            "stored": True,
            "memory_id": memory_id,
            "reason": None,
            "detail": None,
            "pg_ok": True,
            "qdrant_ok": True,
            "indexed": True,
            "phoenix_state": phoenix_state,
            "phoenix_id": phoenix_id,
            "phoenix_psi_utility": 0,
            "phoenix_tri_witness": {"human": False, "ai": False, "earth": False},
            "phoenix_anti_hantu_flag": anti_hantu_flag,
            "phoenix_cooldown_expiry": cooldown_expiry,
            "f4_entity_tags": f4_entity_tags,
        }

    def search(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        mode: str | None = None,
        session_id: str | None = None,
        actor_id: str | None = None,
        limit: int = 20,
        entity_filter: list[str] | None = None,
        include_historical: bool = False,
    ) -> dict[str, Any]:
        """Mirror memory_store.search() behavioral contract."""
        if not query or not query.strip():
            return {
                "results": [],
                "_governance_report": {
                    "total_candidates": 0,
                    "allowed": 0,
                    "flagged": 0,
                    "blocked": 0,
                    "escalated": 0,
                    "governance": [],
                },
                "_escalation_queue": [],
            }

        vector = _fake_embedding(query)
        response = self.qdrant.query_points(
            collection_name="arifos_memory",
            query=vector,
            limit=limit * 5,
            with_payload=True,
        )

        results = []
        governance = []
        blocked = 0
        flagged = 0
        escalated = 0
        for hit in response.points:
            p = getattr(hit, "payload", {}) or {}
            if mode and p.get("mode") != mode:
                continue
            if session_id and p.get("session_id") != session_id:
                continue
            if tags and not all(t in p.get("tags", []) for t in tags):
                continue
            if entity_filter:
                entry_tags = set(p.get("entity_tags", []) or [])
                if not entry_tags.intersection(entity_filter):
                    continue
            temporal_marker = p.get("temporal_marker", "unknown")
            if not include_historical and temporal_marker == "historical":
                continue

            memory_id = p.get("memory_id") or str(getattr(hit, "id", ""))
            tier = p.get("tier", "canonical")
            verdict = "ALLOW"
            reason = "retrieval_allowed"
            if tier == "sacred" and actor_id != "arif":
                verdict = "BLOCK"
                reason = "sacred_tier_requires_sovereign_actor"
            elif temporal_marker == "historical" and not include_historical:
                verdict = "BLOCK"
                reason = "historical_memory_requires_explicit_review"

            gov = {
                "memory_id": memory_id,
                "verdict": verdict,
                "reason": reason,
                "tier": tier,
            }
            governance.append(gov)

            if verdict == "BLOCK":
                blocked += 1
                continue
            if verdict == "FLAG":
                flagged += 1
            if verdict == "ESCALATE":
                escalated += 1

            results.append(
                {
                    "memory_id": memory_id,
                    "content": p.get("content"),
                    "mode": p.get("mode"),
                    "tags": p.get("tags", []),
                    "actor_id": p.get("actor_id"),
                    "session_id": p.get("session_id"),
                    "summary": p.get("summary"),
                    "content_hash": p.get("content_hash"),
                    "created_at": p.get("created_at"),
                    "tier": tier,
                    "point_id": str(getattr(hit, "id", "")),
                    "score": getattr(hit, "score", 0.0) or 0.0,
                    "version": p.get("version", "v3"),
                    "phoenix_id": p.get("phoenix_id"),
                    "phoenix_state": p.get("phoenix_state"),
                    "phoenix_psi_utility": p.get("phoenix_psi_utility", 0),
                    "phoenix_tri_witness": p.get("phoenix_tri_witness", {}),
                    "phoenix_anti_hantu_flag": p.get("phoenix_anti_hantu_flag", False),
                    "entity_tags": p.get("entity_tags", []),
                    "temporal_marker": temporal_marker,
                    "superseded_by": p.get("superseded_by"),
                    "superseded_at": p.get("superseded_at"),
                    "extraction_metadata": p.get("extraction_metadata"),
                    "phoenix_cooldown_expiry": p.get("phoenix_cooldown_expiry"),
                    "_governance": gov,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:limit]
        return {
            "results": results,
            "_governance_report": {
                "total_candidates": len(governance),
                "allowed": len(results),
                "flagged": flagged,
                "blocked": blocked,
                "escalated": escalated,
                "governance": governance,
            },
            "_escalation_queue": [g for g in governance if g["verdict"] == "ESCALATE"],
        }

    def recall(self, memory_id: str) -> dict[str, Any] | None:
        """Recall by memory_id — mirrors memory_store.recall()."""
        meta = self._index.get(memory_id)
        if not meta:
            return None
        if meta.get("deleted_at"):
            return None
        return meta

    def prune(
        self,
        memory_id: str | None = None,
        before: str | None = None,
        reason: str = "manual",
        allow_sacred: bool = False,
    ) -> dict[str, Any]:
        """Soft-delete. SACRED immune unless allow_sacred=True."""
        pruned = []
        blocked_sacred = []
        to_delete = []

        if memory_id:
            to_delete = [memory_id]
        elif before:
            for mid, meta in self._index.items():
                created = meta.get("created_at", "")
                if created and created < before:
                    to_delete.append(mid)

        for mid in to_delete:
            meta = self._index.get(mid)
            if not meta:
                continue
            tier = meta.get("tier", "canonical")
            if tier == "sacred" and not allow_sacred:
                blocked_sacred.append(mid)
                continue
            meta["deleted_at"] = datetime.now(timezone.utc).isoformat()
            self._index[mid] = meta
            pruned.append(mid)

        return {
            "pruned": pruned,
            "count": len(pruned),
            "reason": reason,
            "blocked_sacred": blocked_sacred,
            "sacred_protected": len(blocked_sacred) > 0,
        }

    @property
    def index(self) -> dict[str, dict[str, Any]]:
        """Direct index access for test assertions."""
        return self._index


# ── Helpers ────────────────────────────────────────────────────────────────


def _reject(memory_id: str, reason: str, detail: str) -> dict[str, Any]:
    return {
        "stored": False,
        "memory_id": memory_id,
        "reason": reason,
        "detail": detail,
        "pg_ok": False,
        "qdrant_ok": False,
        "indexed": False,
    }


def _content_hash(content: Any) -> str:
    import hashlib

    return hashlib.sha256(str(content).encode()).hexdigest()[:16]


# ── Fixture ────────────────────────────────────────────────────────────────


@pytest.fixture
def isolated_memory():
    """Self-contained isolated memory for a single test.

    Returns:
        dict with:
          engine: _IsolatedMemoryEngine instance
          store: engine.store method
          search: engine.search method
          recall: engine.recall method
          prune: engine.prune method
          memory_store: engine  (alias)
    """
    engine = _IsolatedMemoryEngine()
    return {
        "engine": engine,
        "store": engine.store,
        "search": engine.search,
        "recall": engine.recall,
        "prune": engine.prune,
        "memory_store": engine,
    }


# ── Global test results collector ──────────────────────────────────────────


_TEST_RESULTS: list[dict[str, Any]] = []


def get_test_results() -> list[dict[str, Any]]:
    return list(_TEST_RESULTS)


def reset_test_results():
    global _TEST_RESULTS
    _TEST_RESULTS = []


def _record(
    test_class: str,
    test_name: str,
    verdict: str,
    assertions_passed: int = 0,
    assertions_failed: int = 0,
    phoenix_state: str | None = None,
    expected_retrieval: str | None = None,
    actual_retrieval: str | None = None,
    privacy_violation: bool | None = None,
    behavioral_delta_recorded: bool = False,
    gap_note: str | None = None,
) -> dict[str, Any]:
    """Record a test result into the global collector for scoring."""
    global _TEST_RESULTS
    record = {
        "test_class": test_class,
        "test_name": test_name,
        "verdict": verdict,
        "phoenix_state": phoenix_state,
        "expected_retrieval": expected_retrieval,
        "actual_retrieval": actual_retrieval,
        "privacy_violation": privacy_violation,
        "behavioral_delta_recorded": behavioral_delta_recorded,
        "gap_note": gap_note,
        "assertions_passed": assertions_passed,
        "assertions_failed": assertions_failed,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    _TEST_RESULTS.append(record)
    return record
