"""External-agent token registry (card-backed; no Ed25519).

A registered external agent carries a long-lived opaque token
(``ext_v1_<agent_id>_<secret>``). Only the SHA-256 of the token is stored in the
agent card at ``/root/AAA/agents/_external/<agent_id>/agent-card.json``.

The kernel resolves the card to a lane, authority ceiling, allowed-tool list and
memory compartment. The token is a *delegated* credential: the ceiling is capped
at LIMITED_MUTATE, never FULL/SOVEREIGN (F13 remains the only sovereign).

This module is deliberately side-effect free and import-light so both the kernel
and the onboarding script can use it. No network, no writes.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any

DEFAULT_ROOT = "/var/lib/arifos/external-agents/registry"
LEGACY_ROOT = "/root/AAA/agents/_external"
TOKEN_PREFIX = "ext_v1_"
MAX_EXTERNAL_CEILING = "LIMITED_MUTATE"
_VALID_CEILINGS = {"OBSERVE_ONLY", "LIMITED_MUTATE"}


def registry_root() -> Path:
    return Path(os.getenv("ARIFOS_EXTERNAL_AGENTS_ROOT", DEFAULT_ROOT))


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _iter_cards() -> list[tuple[Path, dict[str, Any]]]:
    roots = [registry_root(), Path(LEGACY_ROOT)]
    seen: set[Path] = set()
    out: list[tuple[Path, dict[str, Any]]] = []
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen or not root.is_dir():
            continue
        seen.add(resolved)
        for card_path in sorted(root.glob("*/agent-card.json")):
            try:
                card = json.loads(card_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(card, dict):
                out.append((card_path, card))
    return out


def card_agent_id(card: dict[str, Any], fallback: str = "") -> str:
    return str(card.get("id") or card.get("agentId") or fallback).strip()


def card_lane(card: dict[str, Any]) -> str:
    warga = card.get("warga_binding") if isinstance(card.get("warga_binding"), dict) else {}
    return str(warga.get("lane") or card.get("lane") or "EXT").strip() or "EXT"


def card_ceiling(card: dict[str, Any]) -> str:
    ext = card.get("external_agent") if isinstance(card.get("external_agent"), dict) else {}
    ceiling = str(
        ext.get("authority_ceiling") or card.get("authority_ceiling") or "OBSERVE_ONLY"
    ).upper()
    if ceiling not in _VALID_CEILINGS:
        ceiling = "OBSERVE_ONLY"
    # Hard cap: external agents are delegates, never sovereign.
    if ceiling == "FULL":
        ceiling = MAX_EXTERNAL_CEILING
    return ceiling


def card_allowed_tools(card: dict[str, Any]) -> list[str]:
    ext = card.get("external_agent") if isinstance(card.get("external_agent"), dict) else {}
    raw = ext.get("allowed_tools")
    if not isinstance(raw, list):
        return []
    return [str(t).strip() for t in raw if isinstance(t, str) and t.strip()]


def card_memory_compartment(card: dict[str, Any]) -> str:
    ext = card.get("external_agent") if isinstance(card.get("external_agent"), dict) else {}
    agent_id = card_agent_id(card)
    return str(ext.get("memory_compartment") or f"external/{agent_id}").strip()


def card_vendor(card: dict[str, Any]) -> str:
    ext = card.get("external_agent") if isinstance(card.get("external_agent"), dict) else {}
    return str(ext.get("vendor") or card.get("provider", {}).get("organization") or "unknown")


def build_agent_policy(card: dict[str, Any]) -> dict[str, Any]:
    """Map an external card to the kernel session agent_policy (GAP-C)."""
    agent_id = card_agent_id(card)
    return {
        "agent_role": "external_delegate",
        "allowed_tools": card_allowed_tools(card),
        "denied_tools": [],
        "allowed_organs": ["arifos"],
        "irreversibility_threshold": 0.0,
        "policy_version": "1.0.0-external",
        "external_agent_id": agent_id,
        "authority_ceiling": card_ceiling(card),
        "memory_compartment": card_memory_compartment(card),
        "note": (
            "Token-verified external agent card. Delegated authority; capped at "
            "LIMITED_MUTATE. F13 remains sovereign."
        ),
    }


def resolve_external_agent(token: str | None) -> dict[str, Any] | None:
    """Return the resolved external-agent context for a valid token, else None.

    Constant-time hash comparison; revoked/expired cards are rejected.
    """
    if not token or not isinstance(token, str):
        return None
    token = token.strip()
    if not token.startswith(TOKEN_PREFIX):
        return None
    presented = _token_hash(token)
    now = time.time()
    for card_path, card in _iter_cards():
        ext = card.get("external_agent") if isinstance(card.get("external_agent"), dict) else {}
        stored = ext.get("token_sha256")
        if not isinstance(stored, str) or not stored:
            continue
        if not hmac.compare_digest(presented, stored.strip().lower()):
            continue
        if ext.get("revoked") is True:
            return None
        expires = ext.get("token_expires_at")
        if expires is not None:
            try:
                if now > float(expires):
                    return None
            except (TypeError, ValueError):
                return None
        agent_id = card_agent_id(card, card_path.parent.name)
        if not agent_id:
            return None
        return {
            "agent_id": agent_id,
            "lane": card_lane(card),
            "authority_ceiling": card_ceiling(card),
            "allowed_tools": card_allowed_tools(card),
            "memory_compartment": card_memory_compartment(card),
            "vendor": card_vendor(card),
            "card_path": str(card_path),
            "card": card,
        }
    return None


def token_prefix(token: str) -> str:
    """Non-secret display prefix for receipts (never the full token)."""
    if not token:
        return ""
    return token[:14] + "…" if len(token) > 14 else token[:4] + "…"
