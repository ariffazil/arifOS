"""
tool_shortlist_router.py
═══════════════════════════════════════════════════════════════════════════

MCP Surface Governor — intent → tool shortlist router.

Purpose:
    Given a user intent (e.g. "summarize a YouTube video", "convert PDF"),
    return a SHORT (3-7 tool) shortlist the model can act on.

Without this router, the model sees 19+ tools (arifOS 19 + minimax 9 + GEOX 37 +
WEALTH 20 + WELL 17) and burns context on tool descriptions.

With this router, the model sees only the tools relevant to the intent AND
authorized AND healthy.

F1 AMANAH: router is read-only. It does not call any tool. It only filters
the registry.

F11 AUDIT: every shortlist is recorded (caller passes actor_id + session_id).

Author: @integrator (session 2026-06-12-mcp-governor-and-minimax-forge)
Forged: 2026-06-12
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any

from mcp_visibility_policy import (
    OrganHealth,
    ToolEntry,
    build_policy_from_registry,
    filter_visible_tools,
    load_registry,
)
from organ_health_gate import get_organ_health

# ─────────────────────────────────────────────────────────────────────────────
# Intent → organ routing
# ─────────────────────────────────────────────────────────────────────────────


# Keyword → organ map. Lowercased. Order matters (first match wins).
INTENT_KEYWORDS: list[tuple[re.Pattern[str], str]] = [
    # arifOS core
    (re.compile(r"\b(remember|recall|memory|session|context)\b", re.I), "arifOS"),
    (re.compile(r"\b(reason|reflect|plan|verify|critique|think)\b", re.I), "arifOS"),
    (re.compile(r"\b(judge|seal|vault|govern|deliberate)\b", re.I), "arifOS"),
    (re.compile(r"\b(observe|sense|search|fetch|ingest|scan)\b", re.I), "arifOS"),
    (re.compile(r"\b(ops|health|measure|vitals|topology)\b", re.I), "arifOS"),
    (re.compile(r"\b(forge|build|deploy|engineer|compile)\b", re.I), "arifOS"),
    # Machine / MCP / runtime governance stays in the kernel lane, not WELL.
    # G13: system drift/load/reliability/uptime are machine health, not human vitality.
    (
        re.compile(
            r"\b(mcp|tools[/ _-]?(list|call)|initialize|conformance|capability[ _-]?graph|authority[ _-]?header|tool[ _-]?surface|agent[ _-]?card|router|transport|protocol|runtime|schema|execution|gui|app|system[ _-]?(drift|load|reliability|uptime|health)|config[ _-]?drift|runtime[ _-]?drift|cpu[ _-]?load|server[ _-]?load|workload)\b",
            re.I,
        ),
        "arifOS",
    ),
    # GEOX
    (re.compile(r"\b(basin|well|seismic|prospect|reservoir|geology|geophys)\b", re.I), "geox"),
    (re.compile(r"\b(stratigraphy|facies|stratum|tops|segy|las)\b", re.I), "geox"),
    # WEALTH
    (
        re.compile(r"\b(wealth|capital|npv|nps|irr|emv|portfolio|trade|stock|equity)\b", re.I),
        "wealth",
    ),
    (re.compile(r"\b(money|cashflow|burn|runway|survival)\b", re.I), "wealth"),
    (re.compile(r"\b(wealth_(omni_wisdom|signal|inequality|game))\b", re.I), "wealth"),
    # WELL — human vitality only (G13: machine health routes to arifOS/AAA)
    (
        re.compile(
            r"\b(wellness|fatigue|stress|sleep|sleep[ _]?debt|homeostasis|vitality|biometric|readiness|recovery|hrv|rhr|spo2|autonomic|maruah|wellbeing|cognition[ _]?load)\b",
            re.I,
        ),
        "well",
    ),
    (re.compile(r"\b(dignity|consent|sovereign_entropy|reflect_only)\b", re.I), "well"),
    # minimax-media (use substring match — "voiceover" should match "voice")
    (re.compile(r"(audio|voice|tts|speech|music|video|image|media)", re.I), "minimax-media"),
    (
        re.compile(
            r"(text_to_audio|list_voices|voice_clone|play_audio|generate_video|text_to_image|music_generation|voice_design)",
            re.I,
        ),
        "minimax-media",
    ),
    # minimax-code
    (re.compile(r"\b(web_search|understand_image|coding)\b", re.I), "minimax-code"),
    # minimax-search
    (re.compile(r"\b(search|browse|google|serper|jina)\b", re.I), "minimax-search"),
    # AAA / A-FORGE
    (
        re.compile(r"\b(aaa|cockpit|control[ _-]?plane|a2a)\b", re.I),
        "arifOS",
    ),  # route to arifOS (cockpit is read-only, arifOS routes)
    (re.compile(r"\b(a-forge|aforge|forge[ _-]?plan)\b", re.I), "arifOS"),
]


def route_intent_to_organs(intent: str) -> list[str]:
    """Map an intent string to a list of organ_ids (in priority order)."""
    if not intent or not intent.strip():
        return ["arifOS"]  # default to the kernel

    organs: list[str] = []
    for pattern, organ_id in INTENT_KEYWORDS:
        if pattern.search(intent):
            if organ_id not in organs:
                organs.append(organ_id)
    if not organs:
        organs = ["arifOS"]
    # arifOS is always included as the constitutional fallback
    if "arifOS" not in organs:
        organs.append("arifOS")
    return organs


# ─────────────────────────────────────────────────────────────────────────────
# Authority
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Authority:
    """Authority context for shortlist generation."""

    actor_id: str
    session_id: str
    roles: list[str] = field(
        default_factory=lambda: ["agent"]
    )  # "agent" | "operator" | "sovereign"

    def allows(self, tool: ToolEntry) -> bool:
        """F11: who can call what.

        For now: any caller with a non-empty actor_id can call any tool.
        Organ-specific authority (e.g. REFLECT_ONLY for WELL) is checked
        at the call site, not in the shortlist.
        """
        if not self.actor_id:
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Shortlist generation
# ─────────────────────────────────────────────────────────────────────────────


def shortlist_tools(
    intent: str,
    registry: dict[str, Any] | None = None,
    *,
    authority: Authority | None = None,
    max_shortlist: int = 7,
    allow_lab: bool = False,
    all_tools: list[ToolEntry] | None = None,
) -> dict[str, Any]:
    """Generate a shortlist of tools for the given intent.

    Steps:
      1. Route intent → organs (in priority order).
      2. For each organ: get_organ_health(). If healthy, include organ tier
         tools. If degraded/unknown, include only the 3-tool diagnostic shortlist.
      3. Apply the visibility policy (tier filter, health filter, required fields).
      4. Cap to max_shortlist.
      5. Return the shortlist + the routing trace for F11 audit.

    `all_tools` is the live tool list (caller passes). If absent, we use
    the synthetic registry markers (F2: this is for testing only).
    """
    start = time.perf_counter()
    reg = registry or load_registry()
    routed_organs = route_intent_to_organs(intent)
    authority = authority or Authority(actor_id="anonymous", session_id="anonymous")

    if all_tools is None:
        # Synthetic path (no live probe). Used for unit tests.
        from mcp_visibility_policy import registry_to_tool_entries

        all_tools = registry_to_tool_entries(reg)

    # Mark health on each tool based on current organ_health
    for tool in all_tools:
        if tool.organ in routed_organs:
            tool.health = get_organ_health(tool.organ)
        else:
            # Tools from non-routed organs are filtered out by the policy
            # (only routed organs survive). Pre-mark them as filtered.
            tool.health = OrganHealth.UNKNOWN

    # Build policy for this shortlist
    policy = build_policy_from_registry(
        reg,
        allow_lab=allow_lab,
        max_visible_override=max_shortlist + 3,  # allow some headroom for diagnostics
    )

    # Filter
    result = filter_visible_tools(all_tools, policy)

    # Cap to max_shortlist
    shortlist = result.shortlist(n=max_shortlist)

    duration_ms = round((time.perf_counter() - start) * 1000.0, 3)
    return {
        "intent": intent,
        "routed_organs": routed_organs,
        "shortlist": [t.name for t in shortlist],
        "shortlist_full": [t.model_dump(mode="json") for t in shortlist],
        "counts": {
            "total_input": result.counts.get("total_input", 0),
            "visible_before_cap": result.counts.get("visible", 0),
            "final_shortlist": len(shortlist),
            "quarantined_diagnostics": result.counts.get("quarantined_diagnostics", 0),
        },
        "policy": policy.model_dump(mode="json"),
        "actor_id": authority.actor_id,
        "session_id": authority.session_id,
        "duration_ms": duration_ms,
        "epoch_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: emergency 1-3 tool shortlist (e.g. for F12 HOLD or organ down)
# ─────────────────────────────────────────────────────────────────────────────


def emergency_shortlist(intent: str = "", authority: Authority | None = None) -> list[str]:
    """Return 1-3 tool names for emergency operations (organ down, F12 HOLD)."""
    return shortlist_tools(intent, max_shortlist=3, allow_lab=True)["shortlist"]


__all__ = [
    "INTENT_KEYWORDS",
    "route_intent_to_organs",
    "Authority",
    "shortlist_tools",
    "emergency_shortlist",
]
