"""Phoenix-72 v5 wiring tests (2026-10-17).

The live `arif_memory(mode=remember)` path writes through
`memory_handlers_v5._handle_remember` → `vector_memory_qdrant.vector_store`,
NOT through the legacy `memory_store.store`. These tests pin the adapter that
attaches the existing Phoenix cooling contract to governed records only.
"""

from __future__ import annotations

import sys
import types

import pytest

from arifosmcp.runtime import memory_handlers_v5 as mh


def _payload(quality: str = "governed", idempotency_key: str | None = None) -> dict:
    return {
        "content": "Phoenix v5 canary: one reversible governed memory record.",
        "memory_class": "episodic",
        "truth_class": {"status": "observed", "confidence": 0.9},
        "provenance": {
            "actor_id": "kimi-code/FI-008",
            "session_id": "SEAL-phoenix-test",
            "origin": "tool",
        },
        "tier_hint": "L3",
        "quality": quality,
        "tags": ["canary"],
        "idempotency_key": idempotency_key,
    }


# ── 1. helper: governed invokes Phoenix ─────────────────────────────────────


def test_build_phoenix_metadata_governed():
    meta = mh.build_phoenix_metadata(
        memory_id="00000000-0000-0000-0000-000000000001",
        content="governed record",
        mode="remember",
        tags=["canary"],
        actor_id="kimi-code/FI-008",
        session_id="SEAL-phoenix-test",
        summary="governed record",
        tier="L3",
        provenance={"origin": "tool"},
        quality="governed",
    )
    assert set(meta) == set(mh.PHOENIX_FIELDS)
    assert meta["phoenix_state"] == "candidate"
    assert meta["phoenix_psi_utility"] == 0
    assert set(meta["phoenix_tri_witness"]) == {"human", "ai", "earth"}
    assert meta["phoenix_cooldown_expiry"].endswith("+00:00")


# ── 2. helper: non-governed preserves behaviour ─────────────────────────────


def test_build_phoenix_metadata_non_governed():
    meta = mh.build_phoenix_metadata(
        memory_id="id",
        content="quick note",
        mode="remember",
        tags=None,
        actor_id="kimi-code/FI-008",
        session_id="s",
        summary="quick",
        tier="L3",
        provenance=None,
        quality="quick",
    )
    assert meta == {}


# ── 3. merge never overwrites caller fields ─────────────────────────────────


def test_merge_phoenix_metadata_preserves_caller():
    metadata = {"phoenix_state": "caller-set", "phoenix_id": "caller-id"}
    merged = mh.merge_phoenix_metadata(metadata, {"phoenix_state": "candidate", "phoenix_id": "new"})
    assert merged["phoenix_state"] == "caller-set"
    assert merged["phoenix_id"] == "caller-id"


# ── handler fixture: fake redis/nats + memory stores ────────────────────────


@pytest.fixture
def fakes(monkeypatch):
    captured = {"pg": None, "vector": None}

    async def fake_pg_write(**kwargs):
        captured["pg"] = kwargs
        return True

    async def fake_update_qdrant(memory_id, qdrant_id):
        return True

    async def fake_vector_store(content, metadata=None, session_id="", actor_id="", **kwargs):
        captured["vector"] = {"content": content, "metadata": dict(metadata or {})}
        return {"ok": True, "qdrant_id": "fake-qdrant-id"}

    async def fake_idempotency(key):
        return None

    monkeypatch.setattr("arifosmcp.runtime.memory_store._pg_write", fake_pg_write)
    monkeypatch.setattr("arifosmcp.runtime.memory_store._pg_update_qdrant_id", fake_update_qdrant)
    monkeypatch.setattr("arifosmcp.memory.vector_memory_qdrant.vector_store", fake_vector_store)
    monkeypatch.setattr(mh, "_check_idempotency", fake_idempotency)

    # Keep the best-effort side channels instant and offline.
    redis_mod = types.ModuleType("redis")
    redis_asyncio = types.ModuleType("redis.asyncio")

    def _no_redis(*args, **kwargs):
        raise RuntimeError("redis offline in test")

    redis_asyncio.from_url = _no_redis
    redis_mod.asyncio = redis_asyncio
    monkeypatch.setitem(sys.modules, "redis", redis_mod)
    monkeypatch.setitem(sys.modules, "redis.asyncio", redis_asyncio)

    nats_mod = types.ModuleType("nats")

    async def _no_nats(*args, **kwargs):
        raise RuntimeError("nats offline in test")

    nats_mod.connect = _no_nats
    monkeypatch.setitem(sys.modules, "nats", nats_mod)

    return captured


# ── 4. governed record reaches L4 and L3 with Phoenix metadata ──────────────


@pytest.mark.asyncio
async def test_handler_governed_persists_to_l4_and_l3(fakes):
    result = await mh._handle_remember(_payload("governed"), None)
    assert result["verdict"] == "SEAL"

    pg_meta = fakes["pg"]["metadata"]
    assert "phoenix_id" in pg_meta
    assert pg_meta["phoenix_state"] == "candidate"

    vec_meta = fakes["vector"]["metadata"]
    assert "phoenix_id" in vec_meta
    assert vec_meta["phoenix_id"] == pg_meta["phoenix_id"]
    assert "phoenix_tri_witness" in vec_meta


# ── 5. non-governed record keeps current behaviour ──────────────────────────


@pytest.mark.asyncio
async def test_handler_non_governed_has_no_phoenix(fakes):
    result = await mh._handle_remember(_payload("quick"), None)
    assert result["verdict"] == "SEAL"
    assert not any(k.startswith("phoenix_") for k in fakes["pg"]["metadata"])
    assert not any(k.startswith("phoenix_") for k in fakes["vector"]["metadata"])


# ── 6. Phoenix failure is non-fatal and leaves no partial fields ────────────


@pytest.mark.asyncio
async def test_handler_phoenix_failure_is_non_fatal(monkeypatch, fakes):
    def boom(**kwargs):
        raise RuntimeError("phoenix exploded")

    monkeypatch.setattr(mh, "build_phoenix_metadata", boom)
    result = await mh._handle_remember(_payload("governed"), None)
    assert result["verdict"] == "SEAL"
    assert fakes["pg"] is not None  # L4 write still happened
    assert not any(k.startswith("phoenix_") for k in fakes["pg"]["metadata"])
    assert not any(k.startswith("phoenix_") for k in fakes["vector"]["metadata"])


# ── 7. idempotent replay skips Phoenix entirely ─────────────────────────────


@pytest.mark.asyncio
async def test_handler_idempotent_skips_phoenix(monkeypatch, fakes):
    async def existing(key):
        return "11111111-1111-1111-1111-111111111111"

    monkeypatch.setattr(mh, "_check_idempotency", existing)
    result = await mh._handle_remember(_payload("governed", idempotency_key="k-1"), None)
    assert result["payload"]["idempotent"] is True
    assert fakes["pg"] is None
    assert fakes["vector"] is None


# ── 8. vector_store hoists Phoenix fields to payload top level ──────────────


@pytest.mark.asyncio
async def test_vector_store_hoists_phoenix(monkeypatch):
    from arifosmcp.memory import vector_memory_qdrant as vq

    captured = {}

    class FakeClient:
        def upsert(self, collection_name, points):
            captured["payload"] = points[0]["payload"]

    monkeypatch.setattr(vq, "_ensure_collection", lambda: None)
    monkeypatch.setattr(vq, "_compute_truth_score", lambda content, metadata: 0.95)
    monkeypatch.setattr(
        vq,
        "_f10_ontology_check",
        lambda content, metadata: {"valid": True, "ontology_class": "general", "violations": []},
    )
    monkeypatch.setattr(vq, "_generate_embedding", lambda content: [0.0] * 1024)
    monkeypatch.setattr(vq, "_get_qdrant_client", lambda: FakeClient())

    result = await vq.vector_store(
        content="phoenix canary",
        metadata={
            "kernel_seal": True,
            "phoenix_id": "pid-1",
            "phoenix_state": "candidate",
            "phoenix_cooldown_expiry": "2026-10-20T00:00:00+00:00",
            "phoenix_psi_utility": 0,
            "phoenix_tri_witness": {"human": False, "ai": False, "earth": False},
            "phoenix_anti_hantu_flag": False,
        },
        session_id="SEAL-phoenix-test",
        actor_id="kimi-code/FI-008",
    )

    assert result.get("ok") is True
    payload = captured["payload"]
    assert payload["phoenix_id"] == "pid-1"
    assert payload["phoenix_state"] == "candidate"
    assert payload["metadata"]["phoenix_id"] == "pid-1"  # nested copy retained
