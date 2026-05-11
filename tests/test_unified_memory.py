from __future__ import annotations

from types import SimpleNamespace

import pytest

from core.organs.unified_memory import UnifiedMemory, vault


class _FakePoint:
    def __init__(self, point_id: str, score: float, payload: dict[str, object]):
        self.id = point_id
        self.score = score
        self.payload = payload


class _FakeQdrantClient:
    def __init__(self):
        self.collections: set[str] = set()
        self.points: dict[str, list[object]] = {}

    def get_collection(self, collection_name: str):
        if collection_name not in self.collections:
            raise RuntimeError("missing collection")
        return {"name": collection_name}

    def create_collection(self, collection_name: str, vectors_config):
        self.collections.add(collection_name)
        self.points.setdefault(collection_name, [])

    def upsert(self, collection_name: str, points: list[object]):
        self.collections.add(collection_name)
        self.points.setdefault(collection_name, []).extend(points)

    def query_points(
        self,
        collection_name: str,
        query,
        query_filter=None,
        limit: int = 5,
        with_payload: bool = True,
    ):
        items = list(self.points.get(collection_name, []))
        if query_filter and getattr(query_filter, "must", None):
            expected = query_filter.must[0].match.value
            items = [item for item in items if item.payload.get("session_id") == expected]
        return SimpleNamespace(points=items[:limit])

    def delete(self, collection_name: str, points_selector):
        to_delete = set(points_selector.points)
        self.points[collection_name] = [
            item for item in self.points.get(collection_name, []) if item.id not in to_delete
        ]


def test_unified_memory_store_search_and_forget(monkeypatch):
    fake_client = _FakeQdrantClient()

    monkeypatch.setattr("core.organs.unified_memory.embed", lambda text: [0.1, 0.2, 0.3])

    memory = UnifiedMemory(qdrant_url=None)
    memory.client = fake_client
    memory._ensure_collection(memory.collections["session"])

    stored_ids = memory.store(session_id="sess-1", content="constitutional memory")
    assert len(stored_ids) == 1

    fake_client.points[memory.collections["session"]][0] = _FakePoint(
        stored_ids[0],
        0.91,
        {
            "session_id": "sess-1",
            "source": "session_history",
            "path": "sess-1",
            "content": "constitutional memory",
            "metadata": {"kind": "note"},
        },
    )

    results = memory.search("constitutional", session_id="sess-1")
    assert len(results) == 1
    assert results[0].content == "constitutional memory"
    assert results[0].metadata["point_id"] == stored_ids[0]

    forgot_ids = memory.forget(stored_ids)
    assert forgot_ids == stored_ids
    assert memory.search("constitutional", session_id="sess-1") == []


@pytest.mark.asyncio
async def test_vault_store_and_recall_uses_unified_memory(monkeypatch):
    class _FakeMemory:
        def store(
            self,
            *,
            session_id: str,
            content: str,
            metadata=None,
            source: str = "session_history",
        ):
            assert session_id == "vault-session"
            assert content == "remember me"
            return ["mem-123"]

        def search(
            self,
            query: str,
            top_k: int = 5,
            domain: str = "all",
            session_id: str | None = None,
        ):
            assert query == "remember me"
            assert session_id == "vault-session"
            return [
                SimpleNamespace(
                    content="remember me",
                    score=0.88,
                    metadata={"kind": "note", "point_id": "mem-123"},
                    source="session_history",
                    path="vault-session",
                )
            ]

        def forget(self, memory_ids: list[str]):
            return memory_ids

    monkeypatch.setattr("core.organs.unified_memory.get_unified_memory", lambda: _FakeMemory())

    stored = await vault(operation="store", session_id="vault-session", content="remember me")
    assert stored.result.stored_ids == ["mem-123"]

    recalled = await vault(operation="search", session_id="vault-session", content="remember me")
    assert recalled.result.memories[0].content == "remember me"
    assert recalled.result.memories[0].id == "mem-123"
