"""
arifosmcp/integrations/telegram_bridge.py — Telegram Bot API Bridge

Governed HTTPS client for the Telegram Bot API. Singleton class with
fail-closed behavior: refuses to start without TELEGRAM_BOT_TOKEN,
refuses to send to any chat_id not in TELEGRAM_ALLOWED_CHATS or
TELEGRAM_ALLOWED_USERS.

Pattern clone of playwright_bridge.py but with direct HTTPS POST
(no MCP handshake — Telegram has no MCP server). Reads config from
environment variables populated by the 5-R Protocol
(`set -a && source /root/.secrets/kunci-root.env && set +a`).

Token never appears in logs or exceptions. Allowlist is enforced
before any HTTP call. Receipts are returned to the tool layer for
F11 AUDIT sealing.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# ─── Configuration ──────────────────────────────────────────────────────────

TELEGRAM_API_BASE = "https://api.telegram.org"
TELEGRAM_HTTP_TIMEOUT = float(os.getenv("TELEGRAM_HTTP_TIMEOUT", "30.0"))


def _parse_chat_allowlist(raw: str | None) -> set[str]:
    """Parse a comma-separated allowlist from env into a set of strings."""
    if not raw:
        return set()
    return {x.strip() for x in raw.split(",") if x.strip()}


def _redact_token(token: str) -> str:
    """Return a redacted token suitable for logs. Never logs full token."""
    if not token or len(token) < 10:
        return "***"
    return f"{token[:4]}***{token[-4:]}"


# Module-level allowlists, populated at import time from env.
# Hermes session can mutate these via set_allowlist() at runtime.
ALLOWED_CHAT_IDS: set[str] = _parse_chat_allowlist(os.getenv("TELEGRAM_ALLOWED_CHATS"))
ALLOWED_USER_IDS: set[str] = _parse_chat_allowlist(os.getenv("TELEGRAM_ALLOWED_USERS"))


class TelegramBridgeError(Exception):
    """Raised on any Telegram bridge failure. Token never appears in str()."""


@dataclass
class TelegramReceipt:
    """Structured receipt for a successful send. F11 AUDIT evidence."""

    receipt_id: str
    chat_id: str
    message_id: int
    text_hash: str
    text_length: int
    parse_mode: str | None
    timestamp: str
    sent_at_unix: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "chat_id": self.chat_id,
            "message_id": self.message_id,
            "text_hash": self.text_hash,
            "text_length": self.text_length,
            "parse_mode": self.parse_mode,
            "timestamp": self.timestamp,
            "sent_at_unix": self.sent_at_unix,
        }


class TelegramBridge:
    """
    Singleton HTTPS client for the Telegram Bot API.

    Usage:
        bridge = TelegramBridge.get()
        result = await bridge.send_message(chat_id="267378578", text="hello")

    Fail-closed:
        - Raises TelegramBridgeError if TELEGRAM_BOT_TOKEN is unset.
        - Raises TelegramBridgeError if chat_id is not in the allowlist.
        - Raises TelegramBridgeError on any non-200 upstream response.
    """

    _instance: TelegramBridge | None = None

    def __init__(
        self,
        bot_token: str | None = None,
        allowed_chat_ids: set[str] | None = None,
        allowed_user_ids: set[str] | None = None,
        timeout: float = TELEGRAM_HTTP_TIMEOUT,
    ) -> None:
        self.bot_token = bot_token if bot_token is not None else os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise TelegramBridgeError(
                "TELEGRAM_BOT_TOKEN is not set. 5-R Protocol: "
                "`set -a && source /root/.secrets/kunci-root.env && set +a` "
                "before launching arifOS MCP."
            )
        # Allowlist may be passed (tests) or inherited from module env.
        self.allowed_chat_ids = (
            allowed_chat_ids if allowed_chat_ids is not None else set(ALLOWED_CHAT_IDS)
        )
        self.allowed_user_ids = (
            allowed_user_ids if allowed_user_ids is not None else set(ALLOWED_USER_IDS)
        )
        if not self.allowed_chat_ids and not self.allowed_user_ids:
            raise TelegramBridgeError(
                "TELEGRAM_ALLOWED_CHATS and TELEGRAM_ALLOWED_USERS are both empty. "
                "Refusing to start: an empty allowlist would permit send-to-anyone."
            )
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        # Token fingerprint for logging — never log the token itself.
        self._token_fingerprint = _redact_token(self.bot_token)
        logger.info(f"TelegramBridge initialized (token={self._token_fingerprint})")

    @classmethod
    def get(cls) -> TelegramBridge:
        """Singleton accessor. Raises if TELEGRAM_BOT_TOKEN is unset."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for tests only)."""
        if cls._instance is not None:
            # Best-effort close; ignore errors during test teardown.
            try:
                import asyncio

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        return  # leave open; will be GC'd
                    loop.run_until_complete(cls._instance.aclose())
                except RuntimeError:
                    pass
            except Exception:
                pass
            cls._instance = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    # ─── Allowlist enforcement ───────────────────────────────────────────────

    def _chat_authorized(self, chat_id: str) -> bool:
        """
        A chat is authorized if:
          - chat_id is in ALLOWED_CHAT_IDS (group/channel), OR
          - chat_id is in ALLOWED_USER_IDS (DM with allowed user)
        Both are checked as strings — Telegram IDs are always strings in JSON,
        but may be parsed as int by callers.
        """
        cid = str(chat_id)
        # Direct membership
        if cid in self.allowed_chat_ids or cid in self.allowed_user_ids:
            return True
        # Some users send the negative group form ("-100..."); check prefix
        # and the stripped form too.
        if cid.startswith("-100") and cid[4:] in self.allowed_chat_ids:
            return True
        return False

    # ─── Send ────────────────────────────────────────────────────────────────

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str | None = None,
        reply_to_message_id: int | None = None,
        disable_notification: bool = False,
    ) -> TelegramReceipt:
        """
        Send a Telegram message via Bot API sendMessage.

        Raises TelegramBridgeError on:
          - chat_id not in allowlist
          - text exceeds 4096 chars
          - upstream HTTP non-200
        """
        # 1. Allowlist gate
        cid = str(chat_id)
        if not self._chat_authorized(cid):
            raise TelegramBridgeError(
                f"chat_id={cid} not in TELEGRAM_ALLOWED_CHATS or TELEGRAM_ALLOWED_USERS. "
                "Refusing to send."
            )

        # 2. Length gate (Telegram hard limit is 4096)
        if len(text) > 4096:
            raise TelegramBridgeError(
                f"text length {len(text)} exceeds Telegram limit 4096. "
                "Use multiple messages or shorten."
            )

        # 3. Strip control chars that could break Telegram rendering.
        #    Allow common whitespace (\n, \t, \r) but drop other C0 controls.
        cleaned_text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        if cleaned_text != text:
            logger.warning(f"Stripped control chars from outbound text ({len(text)-len(cleaned_text)} removed)")

        # 4. Build payload
        payload: dict[str, Any] = {
            "chat_id": cid,
            "text": cleaned_text,
            "disable_notification": disable_notification,
        }
        if parse_mode in ("HTML", "MarkdownV2", "Markdown"):
            payload["parse_mode"] = parse_mode
        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = int(reply_to_message_id)

        # 5. POST
        url = f"{TELEGRAM_API_BASE}/bot{self.bot_token}/sendMessage"
        client = await self._get_client()
        try:
            resp = await client.post(url, json=payload)
        except httpx.TimeoutException as e:
            raise TelegramBridgeError(f"Telegram API timeout after {self.timeout}s") from e
        except httpx.HTTPError as e:
            raise TelegramBridgeError(f"Telegram API HTTP error: {type(e).__name__}") from e

        # 6. Parse response
        if resp.status_code != 200:
            # Telegram returns error_description; do not echo token.
            try:
                err_body = resp.json()
                err_desc = err_body.get("description", "unknown")
            except Exception:
                err_desc = resp.text[:200]
            raise TelegramBridgeError(
                f"Telegram API returned {resp.status_code}: {err_desc}"
            )

        body = resp.json()
        if not body.get("ok"):
            raise TelegramBridgeError(f"Telegram API ok=false: {body.get('description', 'unknown')}")

        result = body["result"]
        message_id = int(result["message_id"])
        text_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()[:16]

        # 7. Receipt
        from datetime import UTC, datetime

        sent_at_unix = int(result.get("date", datetime.now(UTC).timestamp()))
        receipt = TelegramReceipt(
            receipt_id=f"tg_{hashlib.sha256(f'{cid}{message_id}{sent_at_unix}'.encode()).hexdigest()[:16]}",
            chat_id=cid,
            message_id=message_id,
            text_hash=text_hash,
            text_length=len(cleaned_text),
            parse_mode=parse_mode,
            timestamp=datetime.now(UTC).isoformat(),
            sent_at_unix=sent_at_unix,
        )
        logger.info(
            f"Telegram send OK: chat_id={cid} message_id={message_id} "
            f"text_hash={text_hash} bytes={len(cleaned_text)}"
        )
        return receipt

    # ─── Inspect ─────────────────────────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """Call getMe to verify token validity. Does NOT consume a send quota."""
        url = f"{TELEGRAM_API_BASE}/bot{self.bot_token}/getMe"
        client = await self._get_client()
        try:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200 and resp.json().get("ok"):
                bot = resp.json()["result"]
                return {
                    "status": "OK",
                    "service": "telegram-bot-api",
                    "bot_id": bot.get("id"),
                    "bot_username": bot.get("username"),
                    "allowlist_chats": len(self.allowed_chat_ids),
                    "allowlist_users": len(self.allowed_user_ids),
                }
            return {
                "status": "DOWN",
                "service": "telegram-bot-api",
                "error": f"HTTP {resp.status_code}",
            }
        except Exception as e:
            return {"status": "DOWN", "service": "telegram-bot-api", "error": type(e).__name__}


# ─── Module-level convenience ────────────────────────────────────────────────


def get_bridge() -> TelegramBridge:
    """Shorthand for TelegramBridge.get()."""
    return TelegramBridge.get()