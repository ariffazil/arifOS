"""
tests/runtime/test_sse_feed.py — Observatory SSE Feed Tests
═══════════════════════════════════════════════════════════════════════════════

Verify that the event bus correctly broadcasts sanitized events
and that the SSE endpoint emits only safe data.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio

import pytest

from arifosmcp.runtime.event_bus import (
    _event_buffer,
    _listeners,
    emit_event,
    get_recent_events,
    subscribe,
    unsubscribe,
)


@pytest.fixture(autouse=True)
def clean_bus():
    """Reset event bus state before each test."""
    _event_buffer.clear()
    _listeners.clear()
    yield
    _listeners.clear()


class TestEventBusSanitization:
    """Verify no secrets leak through the event bus."""

    @pytest.mark.asyncio
    async def test_safe_keys_only(self):
        raw = {
            "trace_id": "wh-001",
            "verdict": "QUALIFY",
            "source": "github",
            "event_type": "push",
            "actor": "ariffazil",
            "timestamp": "2026-05-11T00:00:00+00:00",
            "confidence": "HIGH",
            "routing": {"action": "adjudicate", "target": "arif_forge_execute"},
            "policy_version": "test-policy-v1",
            "approval_status": "approved",
            "seal_required": True,
            "vault_entry_id": "VAULT-123",
            "chain_hash": "abc123",
            # These must NOT appear in sanitized output
            "vault_record": {"secret": "shhh"},
            "issues": ["F01 AMANAH: missing ack"],
            "payload_hash": "abc123",
            "raw_payload": {"password": "hunter2"},
        }
        queue = await subscribe()
        await emit_event(raw)
        ev = await asyncio.wait_for(queue.get(), timeout=1.0)

        assert ev["trace_id"] == "wh-001"
        assert ev["verdict"] == "QUALIFY"
        assert ev["issue_count"] == 1
        assert ev["policy_version"] == "test-policy-v1"
        assert ev["approval_status"] == "approved"
        assert ev["seal_required"] is True
        assert ev["observation_only"] is True
        assert "vault_record" not in ev
        assert "raw_payload" not in ev
        assert "payload_hash" not in ev
        assert "issues" not in ev
        assert ev["_event_kind"] == "webhook_intake"

    @pytest.mark.asyncio
    async def test_no_hmac_or_signature_leak(self):
        raw = {
            "trace_id": "wh-002",
            "verdict": "VOID",
            "source": "github",
            "signature": "sha256=deadbeef",
            "secret_token": "bearer_xxx",
            "hmac_key": "super_secret",
        }
        queue = await subscribe()
        await emit_event(raw)
        ev = await asyncio.wait_for(queue.get(), timeout=1.0)

        assert "signature" not in ev
        assert "secret_token" not in ev
        assert "hmac_key" not in ev


class TestEventBusBuffer:
    """Bounded buffer behavior."""

    @pytest.mark.asyncio
    async def test_recent_events_returned(self):
        for i in range(5):
            await emit_event({"trace_id": f"wh-{i}", "verdict": "QUALIFY"})
        recent = get_recent_events(3)
        assert len(recent) == 3
        assert recent[-1]["trace_id"] == "wh-4"

    @pytest.mark.asyncio
    async def test_buffer_bounded(self):
        for i in range(12_000):
            await emit_event({"trace_id": f"wh-{i}", "verdict": "QUALIFY"})
        recent = get_recent_events(20_000)
        assert len(recent) <= 10_000


class TestEventBusSubscription:
    """Subscriber lifecycle."""

    @pytest.mark.asyncio
    async def test_subscribe_receives_events(self):
        queue = await subscribe()
        await emit_event({"trace_id": "wh-003", "verdict": "QUALIFY"})
        ev = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert ev["trace_id"] == "wh-003"

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_receiving(self):
        queue = await subscribe()
        await unsubscribe(queue)
        await emit_event({"trace_id": "wh-004", "verdict": "QUALIFY"})
        assert queue.empty()

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        q1 = await subscribe()
        q2 = await subscribe()
        await emit_event({"trace_id": "wh-005", "verdict": "QUALIFY"})
        e1 = await asyncio.wait_for(q1.get(), timeout=1.0)
        e2 = await asyncio.wait_for(q2.get(), timeout=1.0)
        assert e1["trace_id"] == e2["trace_id"] == "wh-005"


class TestSseRouter:
    """FastAPI SSE endpoint tests (using ASGI transport)."""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from httpx import ASGITransport, AsyncClient

        from arifosmcp.runtime.sse_router import router as sse_router

        app = FastAPI()
        app.include_router(sse_router)
        return AsyncClient(transport=ASGITransport(app), base_url="http://test")

    @pytest.mark.asyncio
    async def test_recent_endpoint(self, client):
        await emit_event({"trace_id": "wh-recent", "verdict": "QUALIFY"})
        resp = await client.get("/recent?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        assert data["events"][-1]["trace_id"] == "wh-recent"
        assert data["observation_only"] is True

    @pytest.mark.asyncio
    async def test_recent_endpoint_respects_limit(self, client):
        for i in range(20):
            await emit_event({"trace_id": f"wh-{i}", "verdict": "QUALIFY"})
        resp = await client.get("/recent?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 5
