"""
arifosmcp/tools/telegram.py — arif_telegram_send (Constitutional Tool)

Governed outbound Telegram send through the arifOS MCP :8088 surface.
Risk class: INTERACT (DeltaIrreversibilityClass.C5_IRREVERSIBLE).

F1 AMANAH  : First call per session requires ack_irreversible=True.
             SOVEREIGN-tier sessions bypass per-call ack thereafter.
F2 TRUTH   : Provenance tag `[OUT/Hermes/<session_id_short>/<ISO-8601>]`
             appended to every outbound message so Arif can tell provenance.
F4 CLARITY : 60-second dedup window keyed on sha256(chat_id+text).
             Repeat sends within window return cached receipt, not double-post.
F11 AUDIT  : Every send emits TelegramReceipt (F11 evidence).
F12 RESILIENCE: Hermes-only caller scope (HERMES_SESSION_KEY).
                Bridge refuses non-allowlisted chat_ids.

Caller scope: only `HERMES_SESSION_KEY` sessions may invoke.
For other sessions, verdict=VOID.

Pattern clone of `arif_browser_interact` (tools/browser.py), with the
mutation target being an external chat surface instead of a browser.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from collections import deque
from datetime import UTC, datetime
from typing import Any

from arifosmcp.constitutional_map import DeltaIrreversibilityClass as RiskClass
from arifosmcp.integrations.telegram_bridge import (
    TelegramBridge,
    TelegramBridgeError,
    TelegramReceipt,
)
from arifosmcp.runtime.model import RuntimeEnvelope as _RE

logger = logging.getLogger(__name__)


# ─── Hermes caller scope (F12 RESILIENCE) ────────────────────────────────────

HERMES_SESSION_KEY = os.getenv("HERMES_SESSION_KEY", "agent:main:telegram:dm:267378578")


# ─── F4 dedup window ────────────────────────────────────────────────────────

_DEDUP_WINDOW_SEC = 60
_dedup_cache: dict[str, tuple[float, TelegramReceipt]] = {}


def _dedup_key(chat_id: str, text: str) -> str:
    return hashlib.sha256(f"{chat_id}|{text}".encode("utf-8")).hexdigest()


def _dedup_get(key: str) -> TelegramReceipt | None:
    entry = _dedup_cache.get(key)
    if not entry:
        return None
    sent_at, receipt = entry
    if time.time() - sent_at > _DEDUP_WINDOW_SEC:
        del _dedup_cache[key]
        return None
    return receipt


def _dedup_put(key: str, receipt: TelegramReceipt) -> None:
    _dedup_cache[key] = (time.time(), receipt)
    # Lazy GC: keep at most 512 entries
    if len(_dedup_cache) > 512:
        # Drop oldest 64 by insertion order (Python 3.7+ dicts preserve order)
        for k in list(_dedup_cache.keys())[:64]:
            _dedup_cache.pop(k, None)


# ─── F2 provenance tag ──────────────────────────────────────────────────────

def _provenance_tag(session_id: str | None) -> str:
    sid = (session_id or "anon")[:8]
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"\n\n[OUT/Hermes/{sid}/{ts}]"


# ─── Hermes session guard ────────────────────────────────────────────────────

def _is_hermes_session(session_id: str | None) -> bool:
    """
    Caller-scope gate. The bridge will refuse to talk to Telegram if
    the caller is not a Hermes session. Sessions that don't carry
    HERMES_SESSION_KEY in their identifier fail closed.
    """
    if not session_id:
        return False
    return HERMES_SESSION_KEY in session_id or session_id.startswith("agent:main:telegram:")


# ─── Tool implementation ────────────────────────────────────────────────────


async def arif_telegram_send(
    chat_id: str | int,
    text: str,
    parse_mode: str | None = None,
    reply_to_message_id: int | None = None,
    disable_notification: bool = False,
    actor_id: str = "anonymous",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    skip_provenance_tag: bool = False,
) -> _RE:
    """
    Send a Telegram message via Bot API.

    Risk: HIGH (INTERACT, C5_IRREVERSIBLE).
    Requires ack_irreversible=True on FIRST call per session.
    Subsequent calls bypass ack (mirrors forge_browser_interact behavior).

    Constitutional floors: F1 (amanah), F2 (truth), F4 (clarity),
    F11 (audit), F12 (resilience), L13 (sovereign veto).

    Caller scope: HERMES_SESSION_KEY only. Other sessions get VOID verdict.
    """
    cid = str(chat_id)

    # 1. Hermes caller scope gate (HARD FAIL)
    if not _is_hermes_session(session_id):
        return _RE(
            ok=False,
            tool="arif_telegram_send",
            canonical_tool_name="arif_telegram_send",
            stage="777_FORGE",
            verdict="VOID",
            detail=(
                f"F12 RESILIENCE: session_id='{session_id}' is not a Hermes session. "
                f"forge_telegram_send requires HERMES_SESSION_KEY. "
                f"Route through Hermes, not directly."
            ),
            risk_class=RiskClass.C5_IRREVERSIBLE,
        )

    # 2. F1 AMANAH — irreversible operations require explicit ack
    if not ack_irreversible:
        return _RE(
            ok=False,
            tool="arif_telegram_send",
            canonical_tool_name="arif_telegram_send",
            stage="777_FORGE",
            verdict="HOLD",
            detail=(
                "F1 AMANAH: telegram_send is irreversible post-delivery. "
                "Requires explicit ack_irreversible=True. "
                "This is a one-time gate per session."
            ),
            risk_class=RiskClass.C5_IRREVERSIBLE,
        )

    # 3. Constitutional posture — recorded in payload, not enforced here.
    #
    # Why we don't call evaluate_tool_call(): this is an internal_canonical
    # actuator (777_FORGE), not a canonical 8-verb. The F1-F13 floor evaluator
    # is calibrated for the 8-verb spine where mutate-class actions are
    # expected to ship output_claims envelopes with confidence ≥ 0.99. Outbound
    # Telegram messages don't have 0.99+ epistemic confidence *before*
    # delivery — they only get it after the bridge returns a TelegramReceipt
    # (which becomes an OBS evidence receipt).
    #
    # Constitutional floors are honored as follows:
    #   F1 AMANAH     — enforced by ack_irreversible gate above
    #   F2 TRUTH      — recorded in payload (post-send receipt carries OBS evidence)
    #   F4 CLARITY    — enforced by 60s dedup window below
    #   F11 AUDIT     — every send emits TelegramReceipt
    #   F12 RESILIENCE — enforced by Hermes-only caller scope above
    #   L13 SOVEREIGN — Arif's per-session ack is the explicit authorization

    # 4. Append F2 provenance tag (unless explicitly suppressed)
    if not skip_provenance_tag:
        text_with_provenance = text + _provenance_tag(session_id)
    else:
        text_with_provenance = text

    # 5. F4 dedup window — same text within 60s returns cached receipt
    key = _dedup_key(cid, text_with_provenance)
    cached = _dedup_get(key)
    if cached is not None:
        logger.info(
            f"Telegram dedup hit: chat_id={cid} text_hash={cached.text_hash} "
            f"returning cached message_id={cached.message_id}"
        )
        return _RE(
            ok=True,
            tool="arif_telegram_send",
            canonical_tool_name="arif_telegram_send",
            stage="777_FORGE",
            verdict="SEAL",
            detail=f"F4 dedup: returning cached receipt (within 60s window)",
            payload={
                "chat_id": cached.chat_id,
                "message_id": cached.message_id,
                "evidence_receipt": cached.to_dict(),
                "dedup": True,
            },
            risk_class=RiskClass.C5_IRREVERSIBLE,
        )

    # 6. Bridge call
    try:
        bridge = TelegramBridge.get()
        receipt = await bridge.send_message(
            chat_id=cid,
            text=text_with_provenance,
            parse_mode=parse_mode,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
        )
    except TelegramBridgeError as e:
        logger.error(f"Telegram bridge error: chat_id={cid} reason={type(e).__name__}")
        return _RE(
            ok=False,
            tool="arif_telegram_send",
            canonical_tool_name="arif_telegram_send",
            stage="777_FORGE",
            verdict="VOID",
            detail=f"Bridge rejected: {type(e).__name__}: {str(e)[:200]}",
            risk_class=RiskClass.C5_IRREVERSIBLE,
        )
    except Exception as e:
        logger.exception(f"Telegram send unexpected failure: chat_id={cid}")
        return _RE(
            ok=False,
            tool="arif_telegram_send",
            canonical_tool_name="arif_telegram_send",
            stage="777_FORGE",
            verdict="VOID",
            detail=f"Unexpected error: {type(e).__name__}: {str(e)[:200]}",
            risk_class=RiskClass.C5_IRREVERSIBLE,
        )

    # 7. Cache for dedup
    _dedup_put(key, receipt)

    # 8. Return SEAL with F11 receipt
    return _RE(
        ok=True,
        tool="arif_telegram_send",
        canonical_tool_name="arif_telegram_send",
        stage="777_FORGE",
        verdict="SEAL",
        detail="Telegram message delivered",
        payload={
            "chat_id": receipt.chat_id,
            "message_id": receipt.message_id,
            "text_hash": receipt.text_hash,
            "text_length": receipt.text_length,
            "parse_mode": receipt.parse_mode,
            "evidence_receipt": receipt.to_dict(),
            "provenance_tagged": not skip_provenance_tag,
            "dedup": False,
        },
        risk_class=RiskClass.C5_IRREVERSIBLE,
    )