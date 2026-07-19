"""
tests/core/test_unified_memory.py — Tests for the Unified Memory (Stage 555)
"""

from unittest.mock import patch

import pytest

from core.organs.unified_memory import (
    MemoryResult,
    UnifiedMemory,
    get_unified_memory,
    vault,
)
from core.shared.types import Verdict


@pytest.fixture
def memory(monkeypatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    from core.organs import unified_memory as unified_memory_module

    unified_memory_module._unified_memory = None
    yield UnifiedMemory()
    unified_memory_module._unified_memory = None


def test_memory_result_dataclass():
    mr = MemoryResult(
        source="test", path="path", content="data", score=0.8, metadata={"key": "val"}
    )
    assert mr.source == "test"
    assert mr.score == 0.8


def test_unified_memory_fallback(memory):
    # Tests the search fallback when client is None
    results = memory.search("any query")
    assert len(results) == 1
    assert results[0].source == "local"
    assert "Fallback" in results[0].content


@patch("qdrant_client.QdrantClient")
def test_unified_memory_with_client(mock_qdrant):
    # Test initialization when Qdrant is available
    with patch.dict("os.environ", {"QDRANT_URL": "http://localhost:6333"}):
        mem = UnifiedMemory()
        assert mem.client is not None

        # Test search with client returns empty list for now as per implementation
        results = mem.search("query")
        assert results == []


def test_get_unified_memory_singleton():
    from core.organs import unified_memory as unified_memory_module

    unified_memory_module._unified_memory = None
    m1 = get_unified_memory()
    m2 = get_unified_memory()
    assert m1 is m2


@pytest.mark.asyncio
async def test_vault_store():
    result = await vault(operation="store", content="Important knowledge")
    assert result.status == "SUCCESS"
    assert result.operation == "store"
    assert result.result.stored_ids is not None
    assert len(result.result.stored_ids) == 1


@pytest.mark.asyncio
async def test_vault_store_no_content_fail():
    with pytest.raises(ValueError, match="requires 'content' or 'query'"):
        await vault(operation="store")


@pytest.mark.asyncio
async def test_vault_search():
    result = await vault(operation="search", content="search term")
    assert result.status == "SUCCESS"
    assert result.operation == "search"
    assert len(result.result.memories) > 0
    assert result.result.memories[0].score > 0


@pytest.mark.asyncio
async def test_vault_recall():
    result = await vault(operation="recall", query="recall term")
    assert result.operation == "recall"
    assert len(result.result.memories) > 0


@pytest.mark.asyncio
async def test_vault_forget():
    result = await vault(operation="forget", memory_ids=["mem_123"])
    assert result.operation == "forget"
    assert result.result.forgot_ids == ["mem_123"]


@pytest.mark.asyncio
async def test_vault_seal():
    result = await vault(operation="seal")
    assert result.verdict == Verdict.SEAL
    assert result.operation == "seal"
    assert result.seal_hash is not None
    assert len(result.seal_hash) == 64  # SHA-256 hex
