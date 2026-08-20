"""
tests/test_telegram_send.py — Smoke test for arif_telegram_send.

Six-gate suite that mirrors the production gates:
  1. Non-Hermes session → VOID (F12 RESILIENCE)
  2. Hermes session without ack → HOLD (F1 AMANAH)
  3. Hermes + ack + allowlist chat → SEAL (success path)
  4. Hermes + ack + repeat text within 60s → SEAL with dedup=True (F4 CLARITY)
  5. Hermes + ack + non-allowlist chat → VOID (bridge allowlist gate)
  6. Hermes + ack + over-length text → VOID (bridge length gate)

Bridge is mocked so no real Telegram API call is made. Token never leaves
the bridge layer; the mock supplies a deterministic TelegramReceipt.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime

import pytest

# Set up env BEFORE importing the tool — bridge reads env at import time.
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "TEST_TOKEN_DO_NOT_USE_REAL")
os.environ.setdefault("TELEGRAM_ALLOWED_USERS", "267378578")


from arifosmcp.integrations.telegram_bridge import TelegramBridge, TelegramReceipt
from arifosmcp.tools.telegram import (
    HERMES_SESSION_KEY,
    arif_telegram_send,
)


# ─── Mock setup ─────────────────────────────────────────────────────────────


def _make_fake_bridge() -> TelegramBridge:
    """Build a TelegramBridge whose send_message returns a deterministic receipt."""
    async def fake_send_message(*args, **kwargs):
        chat_id = kwargs.get("chat_id", args[0] if args else "267378578")
        return TelegramReceipt(
            receipt_id="tg_fake1234567890ab",
            chat_id=str(chat_id),
            message_id=42,
            text_hash="abcd1234",
            text_length=100,
            parse_mode=None,
            timestamp=datetime.now(UTC).isoformat(),
            sent_at_unix=1700000000,
        )

    bridge = TelegramBridge(
        bot_token="TEST_TOKEN_DO_NOT_USE_REAL",
        allowed_chat_ids=set(),
        allowed_user_ids={"267378578"},
    )
    bridge.send_message = fake_send_message  # type: ignore[method-assign]
    return bridge


@pytest.fixture(autouse=True)
def patch_bridge_singleton(monkeypatch):
    """Install a mock bridge as the singleton for the duration of each test."""
    fake = _make_fake_bridge()
    TelegramBridge._instance = fake
    yield
    TelegramBridge._instance = None


# ─── Hermes scope gate ───────────────────────────────────────────────────────


async def test_non_hermes_session_returns_void():
    r = await arif_telegram_send(
        chat_id="267378578",
        text="hello",
        session_id="claude-abc",  # not a Hermes session
        ack_irreversible=True,
    )
    assert r.verdict == "VOID"
    assert "F12 RESILIENCE" in (r.detail or "")
    assert "Hermes" in (r.detail or "")


# ─── F1 AMANAH gate ─────────────────────────────────────────────────────────


async def test_no_ack_returns_hold():
    r = await arif_telegram_send(
        chat_id="267378578",
        text="hello",
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=False,
    )
    assert r.verdict == "HOLD"
    assert "F1 AMANAH" in (r.detail or "")
    assert "ack_irreversible" in (r.detail or "")


# ─── Success path ───────────────────────────────────────────────────────────


async def test_seal_path():
    r = await arif_telegram_send(
        chat_id="267378578",
        text="sabah carbonate probe reply",
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r.verdict == "SEAL"
    assert r.ok is True
    assert r.payload is not None
    assert r.payload["chat_id"] == "267378578"
    assert r.payload["message_id"] == 42
    assert r.payload["provenance_tagged"] is True
    assert r.payload["dedup"] is False
    assert "evidence_receipt" in r.payload
    assert r.payload["evidence_receipt"]["receipt_id"].startswith("tg_")


# ─── F4 CLARITY dedup ────────────────────────────────────────────────────────


async def test_dedup_returns_cached_receipt():
    # Use unique text for this test to avoid colliding with test_seal_path
    unique_text = "dedup test message 2026-08-20"

    # First send — fresh
    r1 = await arif_telegram_send(
        chat_id="267378578",
        text=unique_text,
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r1.verdict == "SEAL"
    assert r1.payload["dedup"] is False

    # Second send with identical text — cached
    r2 = await arif_telegram_send(
        chat_id="267378578",
        text=unique_text,
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r2.verdict == "SEAL"
    assert r2.payload["dedup"] is True
    assert r2.payload["message_id"] == r1.payload["message_id"]


# ─── Bridge allowlist gate ───────────────────────────────────────────────────


async def test_bad_chat_returns_void():
    # Use the REAL bridge (not the mock) to exercise the allowlist gate
    real_bridge = TelegramBridge(
        bot_token="TEST_TOKEN_DO_NOT_USE_REAL",
        allowed_chat_ids=set(),
        allowed_user_ids={"267378578"},
    )
    TelegramBridge._instance = real_bridge

    r = await arif_telegram_send(
        chat_id="999999999",  # not in allowlist
        text="hi",
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r.verdict == "VOID"
    assert "Bridge rejected" in (r.detail or "")


# ─── Bridge length gate ─────────────────────────────────────────────────────


async def test_over_length_returns_void():
    real_bridge = TelegramBridge(
        bot_token="TEST_TOKEN_DO_NOT_USE_REAL",
        allowed_chat_ids=set(),
        allowed_user_ids={"267378578"},
    )
    TelegramBridge._instance = real_bridge

    r = await arif_telegram_send(
        chat_id="267378578",
        text="x" * 5000,  # exceeds Telegram's 4096 limit
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r.verdict == "VOID"
    assert "4096" in (r.detail or "")