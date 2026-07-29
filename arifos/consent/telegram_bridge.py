"""
telegram_bridge.py — Telegram Consent Routing
══════════════════════════════════════════════

Routes consent requests to Arif's Telegram via the 777-FORGE bot.
The bot is already running (openclaw-bot.service). This module
provides the message formatting and response parsing.

Consent flow:
  1. Agent calls consent gate → requires T3 consent
  2. This module formats a Telegram message
  3. 777-FORGE bot sends it to Arif
  4. Arif replies: "jalan terus" or "hold"
  5. Bot parses the reply and returns consent token
  6. Agent receives token and proceeds

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import logging
import re
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .consent_token import ConsentToken, TokenState

logger = logging.getLogger(__name__)

# File-based consent queue (777-FORGE bot polls this)
CONSENT_QUEUE_DIR = Path("/var/arifos/consent-queue")
CONSENT_RESPONSE_DIR = Path("/var/arifos/consent-responses")


class ConsentResponse(Enum):
    APPROVED = "approved"  # "jalan terus", "yes", "confirm", etc.
    DENIED = "denied"  # "hold", "no", "stop"
    EXPIRED = "expired"  # No response within TTL
    UNKNOWN = "unknown"  # Unrecognized response


SOVEREIGN_APPROVAL_PATTERNS = [
    r"\bjalan terus\b",
    r"\bjalan\b.*\bterus\b",
    r"\byes\b",
    r"\bconfirm\b",
    r"\bapprove\b",
    r"\bok\b",
    r"\bbuat ja\b",
    r"\bbuat je\b",
    r"\bgo\b",
    r"\bproceed\b",
    r"\bexecute\b",
    r"\backnowledge\b",
    r"\baccepted\b",
    r"\bteruskan\b",
    r"\bterus\b",
]

SOVEREIGN_DENIAL_PATTERNS = [
    r"\bhold\b",
    r"\bno\b",
    r"\bstop\b",
    r"\bcancel\b",
    r"\bdeny\b",
    r"\breject\b",
    r"\bjangan\b",
    r"\btunggu\b",
    r"\bnanti\b",
    r"\babort\b",
]


@dataclass
class ConsentQueueEntry:
    """A consent request queued for Telegram delivery."""

    request_id: str
    agent_id: str
    telegram_message: str
    token: ConsentToken | None = None
    queued_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    responded_at: str | None = None
    response: str | None = None


def parse_sovereign_response(text: str) -> ConsentResponse:
    """Parse Arif's Telegram reply into a consent verdict."""
    text_lower = text.lower().strip()

    # Check approval patterns
    for pattern in SOVEREIGN_APPROVAL_PATTERNS:
        if re.search(pattern, text_lower):
            return ConsentResponse.APPROVED

    # Check denial patterns
    for pattern in SOVEREIGN_DENIAL_PATTERNS:
        if re.search(pattern, text_lower):
            return ConsentResponse.DENIED

    return ConsentResponse.UNKNOWN


def format_consent_message(
    agent_id: str,
    action: str,
    justification: str,
    blast_radius: str,
    reversibility: str,
    rollback_plan: str,
    request_id: str,
) -> str:
    """Format a consent request as a Telegram message."""
    return (
        f"🔴 **Consent Required — {agent_id}**\n\n"
        f"**Action:** {action}\n"
        f"**Why:** {justification}\n"
        f"**Blast radius:** {blast_radius}\n"
        f"**Reversible:** {reversibility}\n"
        f"**Rollback:** {rollback_plan}\n\n"
        f"**Request ID:** `{request_id[:16]}…`\n"
        f"Reply: `jalan terus` or `hold`\n"
        f"⏱ Expires in 5 minutes"
    )


class TelegramConsentBridge:
    """Bridge between consent engine and Telegram bot.

    Writes consent requests to a queue file that the 777-FORGE bot
    polls. The bot delivers via Telegram, reads Arif's response,
    and writes the result to a response file.
    """

    def __init__(
        self,
        queue_dir: str | Path = CONSENT_QUEUE_DIR,
        response_dir: str | Path = CONSENT_RESPONSE_DIR,
    ):
        self.queue_dir = Path(queue_dir)
        self.response_dir = Path(response_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)
        self._pending: dict[str, ConsentQueueEntry] = {}

    def enqueue(
        self,
        agent_id: str,
        action: str,
        justification: str,
        blast_radius: str,
        reversibility: str,
        rollback_plan: str,
    ) -> ConsentQueueEntry:
        """Enqueue a consent request for Telegram delivery."""
        request_id = f"cr-{secrets.token_hex(8)}"
        message = format_consent_message(
            agent_id,
            action,
            justification,
            blast_radius,
            reversibility,
            rollback_plan,
            request_id,
        )

        entry = ConsentQueueEntry(
            request_id=request_id,
            agent_id=agent_id,
            telegram_message=message,
        )
        self._pending[request_id] = entry

        # Write queue file for bot to pick up
        queue_file = self.queue_dir / f"{request_id}.json"
        with open(queue_file, "w") as f:
            json.dump(
                {
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "message": message,
                    "queued_at": entry.queued_at,
                    "chat_id": "arif-fazil",  # Bot resolves this
                },
                f,
                indent=2,
            )

        logger.info(f"Consent queued: {request_id} → Telegram ({agent_id}: {action[:60]})")
        return entry

    def check_response(self, request_id: str, timeout_s: float = 300) -> ConsentResponse:
        """Poll for Arif's response. Blocks up to timeout_s."""
        response_file = self.response_dir / f"{request_id}.json"
        deadline = time.time() + timeout_s

        while time.time() < deadline:
            if response_file.exists():
                try:
                    with open(response_file) as f:
                        data = json.load(f)
                    response_text = data.get("response", "")
                    verdict = parse_sovereign_response(response_text)

                    # Update queue entry
                    entry = self._pending.get(request_id)
                    if entry:
                        entry.responded_at = datetime.now(UTC).isoformat()
                        entry.response = response_text

                    # Clean up response file
                    response_file.unlink(missing_ok=True)

                    logger.info(f"Consent response: {request_id} → {verdict.value}")
                    return verdict

                except (json.JSONDecodeError, OSError) as e:
                    logger.warning(f"Bad response file: {e}")
                    break

            time.sleep(2)  # Poll every 2 seconds

        # Timeout
        logger.warning(f"Consent timeout: {request_id}")
        return ConsentResponse.EXPIRED

    def cleanup(self, request_id: str) -> None:
        """Remove queue and response files."""
        (self.queue_dir / f"{request_id}.json").unlink(missing_ok=True)
        (self.response_dir / f"{request_id}.json").unlink(missing_ok=True)
        self._pending.pop(request_id, None)

    def pending_count(self) -> int:
        return len(self._pending)
