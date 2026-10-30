"""
arifos://model-governance-card/{lane} — Model Governance Card Resource Template
═══════════════════════════════════════════════════════════════════════════════

ARIFOS::AAA_MODEL_GOVERNANCE_RUNTIME_WIRING::2026-10-30::v1 (F13-SEALED).

Serves the deterministic per-lane governance cards compiled by the AAA supply-chain
registry (registry/governance_cards.py → generated/model-governance-cards/<lane>.json).

Contract (ratified):
  read-only, revision-bound, hash-addressed, no secrets, no arbitrary paths,
  fail-closed: card source unavailable → explicit UNKNOWN payload, never a
  fabricated card. The card may lower confidence; it may NEVER raise authority.

MCP semantics: this mission uses three MCP server primitives (resource, prompt,
tool) — a mission-scoped projection, not a claim that MCP contains only these.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastmcp import FastMCP

CARD_DIR = Path(
    os.getenv(
        "ARIFOS_MODEL_CARD_DIR",
        "/root/AAA/registry/generated/model-governance-cards",
    )
)

# actor (as presented to arif_init) → AAA lane. Deliberately small and explicit;
# unmapped actors get lane "UNKNOWN" and a fail-closed card.
ACTOR_LANE = {
    "QWEN": "333",
    "qwen": "333",
    "qwen-code": "333",
    "FI-003": "333",
    "333-AGI": "333",
    "KIMI": "555",
    "kimi": "555",
    "kimi-code": "555",
    "FI-008": "555",
    "555-ASI": "555",
    "CLAUDE": "888",
    "claude-code": "888",
    "FI-002": "888",
    "888-APEX": "888",
    "HERMES": "hermes",
    "hermes": "hermes",
    "FORGE": "forge",
    "forge": "forge",
    "000Ω": "forge",
}


def resolve_lane(actor_id: str | None) -> str:
    if not actor_id:
        return "UNKNOWN"
    return ACTOR_LANE.get(actor_id) or ACTOR_LANE.get(str(actor_id).split("/")[0]) or "UNKNOWN"


def load_card(lane: str) -> dict:
    """Load one lane card. Fail-closed: never fabricate, never raise authority."""
    if not re_safe_lane(lane):
        return _unavailable(lane, "invalid lane id")
    path = CARD_DIR / f"{lane}.json"
    try:
        if not path.is_file():
            return _unavailable(lane, "card file absent (registry compile owed or lane unassigned)")
        card = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-closed by construction
        return _unavailable(lane, f"card read failed: {type(exc).__name__}")
    if str(card.get("identity_state")) not in ("matched", "classified_remap", "MISMATCH", "UNRESOLVED"):
        return _unavailable(lane, "card failed identity_state grammar")
    card["card_source"] = "aaa-registry-projection"
    return card


def _unavailable(lane: str, reason: str) -> dict:
    return {
        "lane_id": lane,
        "card_source": "UNAVAILABLE",
        "identity_state": "UNKNOWN",
        "resolved_model": "UNKNOWN",
        "authority_ceiling": {"propose": False, "verify": False, "authorize": False, "execute": False},
        "operating_mode": "OBSERVE_ONLY",
        "reason": reason,
        "verdict": "HOLD",
        "note": "fail-closed: card unavailable never fabricates identity and never inflates authority",
    }


def re_safe_lane(lane: str) -> bool:
    import re
    return bool(re.fullmatch(r"[a-z0-9Ω][a-z0-9Ω-]{0,15}", lane or ""))


def register_model_governance_template(mcp: FastMCP) -> list[str]:
    @mcp.resource(
        "arifos://model-governance-card/{lane}",
        description="Model Governance Card for an AAA lane — deterministic registry "
                    "projection: requested vs resolved identity, route mutability, "
                    "failure domain, eligible/forbidden roles, authority ceiling. "
                    "Fail-closed: may lower confidence, never raise authority.",
    )
    def model_governance_card(lane: str) -> dict:
        return load_card(lane)

    return ["arifos://model-governance-card/{lane}"]
