import pytest
from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict


@pytest.mark.asyncio
async def test_engineering_memory_query_falls_back_without_vector_backend(monkeypatch):
    async def fake_query(*, query, session_id):
        return RuntimeEnvelope(
            ok=True,
            tool="engineering_memory",
            session_id=session_id,
            stage="555_MEMORY",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={"query": query, "backend": "legacy"},
        )

    monkeypatch.setattr("arifosmcp.runtime.tools_internal._constitutional_memory_store", None)
    monkeypatch.setattr("arifosmcp.runtime.tools_internal._get_constitutional_memory_store", lambda: None)
    monkeypatch.setattr("arifosmcp.runtime.tools_internal._az_memory_query", fake_query)

    result = await engineering_memory_dispatch_impl(
        "query",
        {"query": "test query", "session_id": "test-session"},
        None,
        "low",
        True,
        None,
    )

    assert result.ok is True
    assert result.payload["backend"] == "legacy"


@pytest.mark.asyncio
async def test_engineering_memory_write_degrades_to_backend_none_without_vector_backend(monkeypatch):
    monkeypatch.setattr("arifosmcp.runtime.tools_internal._constitutional_memory_store", None)
    monkeypatch.setattr("arifosmcp.runtime.tools_internal._get_constitutional_memory_store", lambda: None)

    result = await engineering_memory_dispatch_impl(
        "write",
        {"content": "remember this", "session_id": "test-session"},
        None,
        "low",
        True,
        None,
    )

    assert result.ok is True
    assert result.status == RuntimeStatus.SUCCESS
    assert result.verdict == Verdict.SEAL
    assert result.payload["backend"] == "none"

@pytest.mark.asyncio
async def test_engineering_memory_vector_forget_no_backend_returns_not_implemented(monkeypatch):
    monkeypatch.setattr("arifosmcp.runtime.tools_internal._constitutional_memory_store", None)
    monkeypatch.setattr("arifosmcp.runtime.tools_internal._get_constitutional_memory_store", lambda: None)

    result = await engineering_memory_dispatch_impl(
        "vector_forget",
        {"query": "test query", "session_id": "test-session"},
        None,
        "low",
        True,
        None,
    )

    assert result.ok is True
    assert result.verdict == Verdict.SABAR
    assert result.payload["error"] == "NOT_IMPLEMENTED"
    assert "Vector backend (Qdrant) is not configured or available." in result.payload["message"]
