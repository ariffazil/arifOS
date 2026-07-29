"""
arifos/consent — Risk-Proportional Consent Module
══════════════════════════════════════════════════

Component #2 of Identity Binding + Consent Architecture.
Provides consent token minting, risk-tier classification,
and Telegram-based sovereign consent routing.

Usage:
    from arifos.consent import ConsentToken, ConsentGate, TelegramConsentBridge

    gate = ConsentGate(telegram_enabled=True)
    request = ConsentRequest(...)
    verdict = gate.gate(request)

    if verdict == ConsentVerdict.CONSENT_REQUIRED:
        bridge = TelegramConsentBridge()
        bridge.enqueue(request)
        response = bridge.check_response(request.request_id)

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from .consent_token import ConsentToken, TokenState, TokenStore
from .consent_request import (
    ConsentGate,
    ConsentRequest,
    ConsentVerdict,
    RiskTier,
    ACTION_TIER_MAP,
)
from .telegram_bridge import (
    ConsentQueueEntry,
    ConsentResponse,
    TelegramConsentBridge,
    parse_sovereign_response,
    format_consent_message,
)

__all__ = [
    "ConsentToken",
    "TokenState",
    "TokenStore",
    "ConsentGate",
    "ConsentRequest",
    "ConsentVerdict",
    "RiskTier",
    "ACTION_TIER_MAP",
    "TelegramConsentBridge",
    "ConsentQueueEntry",
    "ConsentResponse",
    "parse_sovereign_response",
    "format_consent_message",
]
