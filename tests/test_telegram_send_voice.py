"""
tests/test_telegram_send_voice.py — Smoke test for arif_telegram_send_voice.

Mirrors test_telegram_send.py gates for the voice path:
  1. Non-Hermes session -> VOID (F12 RESILIENCE)
  2. Hermes session without ack -> HOLD (F1 AMANAH)
  3. Hermes + ack + allowlist chat -> SEAL (success path)
  4. Voice file missing -> VOID (bridge file gate)

Bridge is mocked so no real Telegram API call is made. Token never leaves
the bridge layer; the mock supplies a deterministic TelegramReceipt.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "TEST_TOKEN_DO_NOT_USE_REAL")
os.environ.setdefault("TELEGRAM_ALLOWED_USERS", "267378578")


from arifosmcp.integrations.telegram_bridge import TelegramBridge, TelegramReceipt
from arifosmcp.tools.telegram import (
    HERMES_SESSION_KEY,
    arif_telegram_send_voice,
)


def _make_fake_bridge() -> TelegramBridge:
    async def fake_send_voice(voice_path: str, **kwargs):
        chat_id = kwargs.get("chat_id", "267378578")
        return TelegramReceipt(
            receipt_id="tg_fakevoice123456789",
            chat_id=str(chat_id),
            message_id=43,
            text_hash="deadbeef1234",
            text_length=1234,
            parse_mode=None,
            timestamp=datetime.now(UTC).isoformat(),
            sent_at_unix=1700000001,
        )

    bridge = TelegramBridge(
        bot_token="TEST_TOKEN_DO_NOT_USE_REAL",
        allowed_chat_ids=set(),
        allowed_user_ids={"267378578"},
    )
    bridge.send_voice = fake_send_voice  # type: ignore[method-assign]
    return bridge


@pytest.fixture(autouse=True)
def patch_bridge_singleton(monkeypatch):
    fake = _make_fake_bridge()
    TelegramBridge._instance = fake
    yield
    TelegramBridge._instance = None


@pytest.fixture
def voice_file(tmp_path: Path) -> str:
    f = tmp_path / "test_voice.ogg"
    f.write_bytes(b"\x00\x01\x02fake-ogg-bytes")
    return str(f)


async def test_non_hermes_session_returns_void(voice_file):
    r = await arif_telegram_send_voice(
        chat_id="267378578",
        voice_path=voice_file,
        session_id="claude-abc",
        ack_irreversible=True,
    )
    assert r.verdict == "VOID"
    assert "F12 RESILIENCE" in (r.detail or "")


async def test_no_ack_returns_hold(voice_file):
    r = await arif_telegram_send_voice(
        chat_id="267378578",
        voice_path=voice_file,
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=False,
    )
    assert r.verdict == "HOLD"
    assert "F1 AMANAH" in (r.detail or "")
    assert "ack_irreversible" in (r.detail or "")


async def test_seal_path(voice_file):
    r = await arif_telegram_send_voice(
        chat_id="267378578",
        voice_path=voice_file,
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r.verdict == "SEAL"
    assert r.ok is True
    assert r.payload["chat_id"] == "267378578"
    assert r.payload["message_id"] == 43
    assert r.payload["dedup"] is False
    assert r.payload["evidence_receipt"]["receipt_id"].startswith("tg_")


async def test_bad_chat_returns_void(voice_file):
    # Real bridge (not mock) to exercise the allowlist gate on the voice path
    real_bridge = TelegramBridge(
        bot_token="TEST_TOKEN_DO_NOT_USE_REAL",
        allowed_chat_ids=set(),
        allowed_user_ids={"267378578"},
    )
    TelegramBridge._instance = real_bridge

    r = await arif_telegram_send_voice(
        chat_id="999999999",
        voice_path=voice_file,
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r.verdict == "VOID"
    assert "Bridge rejected" in (r.detail or "")


async def test_missing_file_returns_void():
    # Real bridge; file does not exist -> file gate raises -> VOID
    real_bridge = TelegramBridge(
        bot_token="TEST_TOKEN_DO_NOT_USE_REAL",
        allowed_chat_ids=set(),
        allowed_user_ids={"267378578"},
    )
    TelegramBridge._instance = real_bridge

    r = await arif_telegram_send_voice(
        chat_id="267378578",
        voice_path="/tmp/does-not-exist-xyz.ogg",
        session_id=HERMES_SESSION_KEY,
        ack_irreversible=True,
    )
    assert r.verdict == "VOID"
    assert "not found" in (r.detail or "").lower()
