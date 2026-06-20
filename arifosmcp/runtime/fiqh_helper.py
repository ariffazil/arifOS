"""
fiqh_helper.py — Agent-facing helpers for the F0 5-tier fiqh vocabulary.

Purpose: Make the ratified fiqh-of-floors (F0_FIQH.md) USEFUL for agents
without breaking existing code. Pure additive layer. Single import.

For an agent, the question is not "what is the tier?" — it's:
  "What should I DO when floor X is violated?"
  "Should I REJECT, FLAG, ACK, or stay silent?"
  "What is the human-language voice for this floor?"

This module answers those questions in one call.

Ratified 2026-06-11 by F13 SOVEREIGN (Arif) ed25519 signature.
See: /root/compose/sekrits/F0_FIQH_888_SEAL_2026-06-11.json
See: /root/arifOS/static/arifos/floors/F0_FIQH.md

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from arifosmcp.constitutional_map import _FLOOR_FIQH, FiqhTier, Law

# ─────────────────────────────────────────────────────────────────────────────
# Constants — single source of truth, agent-readable
# ─────────────────────────────────────────────────────────────────────────────

# Short floor code (F1..F13) → Law enum, for the common "F9" string input.
_FLOOR_CODE_TO_LAW: dict[str, Law] = {
    "F1": Law.L01_AMANAH,
    "F2": Law.L02_TRUTH,
    "F3": Law.L03_WITNESS,
    "F4": Law.L04_CLARITY,
    "F5": Law.L05_PEACE,
    "F6": Law.L06_EMPATHY,
    "F7": Law.L07_HUMILITY,
    "F8": Law.L08_GENIUS,
    "F9": Law.L09_ANTIHANTU,
    "F10": Law.L10_ONTOLOGY,
    "F11": Law.L11_AUDIT,
    "F12": Law.L12_INJECTION,
    "F13": Law.L13_SOVEREIGN,
}

# Bilingual tier label: Bahasa Melayu first (Arif's voice), English fallback.
TIER_LABEL: dict[FiqhTier, dict[str, str]] = {
    FiqhTier.WAJIB: {"bm": "Wajib", "en": "Obligatory", "code": "WAJ"},
    FiqhTier.SUNAT: {"bm": "Sunat", "en": "Recommended", "code": "SUN"},
    FiqhTier.HARUS: {"bm": "Harus", "en": "Permitted", "code": "HAR"},
    FiqhTier.MAKRUH: {"bm": "Makruh", "en": "Discouraged", "code": "MAK"},
    FiqhTier.HARAM: {"bm": "Haram", "en": "Forbidden", "code": "HRM"},
}

# Voice: the single human sentence a sovereign says about this floor's tier.
# This is what gets logged, shown in audit, or used in agent reasoning.
TIER_VOICE: dict[FiqhTier, str] = {
    FiqhTier.WAJIB: "Kena buat. Mandatory — kernel REJECTS if missing.",
    FiqhTier.SUNAT: "Elok buat. Recommended — kernel RECORDS if observed.",
    FiqhTier.HARUS: "Tak payah fikir. Permitted — kernel does not record.",
    FiqhTier.MAKRUH: "Jangan, tapi Arif boleh ya. Discouraged — ping 888 with ack.",
    FiqhTier.HARAM: "Tak boleh langsung. Forbidden — kernel REJECTS unconditionally.",
}

# Agent action: what should the agent DO when this tier is violated?
# This is the operational contract — not just a label.
TIER_ACTION: dict[FiqhTier, Literal["REJECT", "ACK_888", "LOG_ONLY", "SILENT", "REJECT_HARD"]] = {
    FiqhTier.WAJIB: "REJECT",  # void the call
    FiqhTier.SUNAT: "LOG_ONLY",  # record but proceed
    FiqhTier.HARUS: "SILENT",  # no record, no ping
    FiqhTier.MAKRUH: "ACK_888",  # ping sovereign, require ack
    FiqhTier.HARAM: "REJECT_HARD",  # unconditional reject (no override)
}


# ─────────────────────────────────────────────────────────────────────────────
# Core decision object — what an agent needs in ONE struct
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TierDecision:
    """Single-call answer to: 'What should I do with this floor?'"""

    floor: str  # "F9"
    floor_name: str  # "ANTIHANTU"
    tier: str  # "HARAM"
    tier_bm: str  # "Haram"
    tier_en: str  # "Forbidden"
    tier_code: str  # "HRM"
    voice: str  # the human sentence
    action: str  # REJECT | ACK_888 | LOG_ONLY | SILENT | REJECT_HARD
    sovereign_needed: bool  # True if 888 must be pinged/ack

    def __str__(self) -> str:
        return (
            f"[{self.floor} {self.floor_name}] "
            f"tier={self.tier} ({self.tier_bm}) "
            f"action={self.action} | {self.voice}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Public API — every function is additive, no side effects, no I/O
# ─────────────────────────────────────────────────────────────────────────────


def _resolve_floor(floor: str | Law) -> Law:
    """Accept either 'F9' (string) or Law.L09_ANTIHANTU (enum)."""
    if isinstance(floor, Law):
        return floor
    if isinstance(floor, str):
        code = floor.upper().strip()
        if code in _FLOOR_CODE_TO_LAW:
            return _FLOOR_CODE_TO_LAW[code]
        # Try matching by enum name (e.g. "L09_ANTIHANTU" or "ANTIHANTU")
        for law in Law:
            if law.name == code or law.name.endswith(code) or code in law.name:
                return law
    raise ValueError(
        f"Unknown floor: {floor!r}. Use 'F1'..'F13' or Law.L01_AMANAH..Law.L13_SOVEREIGN."
    )


def get_tier(floor: str | Law) -> FiqhTier:
    """Get the fiqh tier for a floor. Default HARUS if not mapped."""
    law = _resolve_floor(floor)
    return _FLOOR_FIQH.get(law, FiqhTier.HARUS)


def tier_label(floor: str | Law) -> str:
    """Bilingual label: 'WAJIB (Wajib / Obligatory)'."""
    tier = get_tier(floor)
    info = TIER_LABEL[tier]
    return f"{tier.value} ({info['bm']} / {info['en']})"


def tier_voice(floor: str | Law) -> str:
    """The single human sentence for this floor's tier."""
    return TIER_VOICE[get_tier(floor)]


def what_should_i_do(floor: str | Law) -> TierDecision:
    """The complete answer: tier + label + voice + action. One call."""
    law = _resolve_floor(floor)
    tier = _FLOOR_FIQH.get(law, FiqhTier.HARUS)
    info = TIER_LABEL[tier]
    action = TIER_ACTION[tier]
    return TierDecision(
        floor=law.value.replace("L0", "F0").replace("L", "F"),
        floor_name=law.name.split("_", 1)[-1] if "_" in law.name else law.name,
        tier=tier.value,
        tier_bm=info["bm"],
        tier_en=info["en"],
        tier_code=info["code"],
        voice=TIER_VOICE[tier],
        action=action,
        sovereign_needed=(action == "ACK_888"),
    )


def is_haram(floor: str | Law) -> bool:
    """Quick gate: should this floor unconditionally REJECT?"""
    return get_tier(floor) == FiqhTier.HARAM


def is_wajib(floor: str | Law) -> bool:
    """Quick gate: is this floor mandatory (REJECT on violation)?"""
    return get_tier(floor) == FiqhTier.WAJIB


def needs_sovereign_ack(floor: str | Law) -> bool:
    """Quick gate: does violation require 888 ack to proceed?"""
    return get_tier(floor) == FiqhTier.MAKRUH


def tier_summary() -> dict[str, str]:
    """F1..F13 → voice string. For agent dashboards, audit logs, briefings."""
    return {f"F{i + 1}": tier_voice(f"F{i + 1}") for i in range(13)}


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: format for arifOS audit receipts
# ─────────────────────────────────────────────────────────────────────────────


def format_floor_status(floor: str | Law, violated: bool = False) -> str:
    """
    One-line audit string for VAULT999 receipts / agent logs.

    Examples:
        format_floor_status("F1")   → "[F1 AMANAH] WAJIB ✓ pass"
        format_floor_status("F9", violated=True) → "[F9 ANTIHANTU] HARAM ✗ REJECT_HARD"
        format_floor_status("F5", violated=True) → "[F5 PEACE] MAKRUH ⚠ ack_888 needed"
    """
    d = what_should_i_do(floor)
    if not violated:
        marker = "✓"
        suffix = "pass"
    else:
        marker = {
            "REJECT": "✗",
            "REJECT_HARD": "✗",
            "ACK_888": "⚠",
            "LOG_ONLY": "·",
            "SILENT": "·",
        }.get(d.action, "?")
        suffix = d.action.lower()
    return f"[{d.floor} {d.floor_name}] {d.tier} {marker} {suffix}"


# ─────────────────────────────────────────────────────────────────────────────
# Self-test (run as script: python -m arifosmcp.runtime.fiqh_helper)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("F0_FIQH Helper — Self-test (F13 SOVEREIGN ratified 2026-06-11)")
    print("=" * 70)
    print()
    print("--- All 13 floors (dashboard view) ---")
    for f, voice in tier_summary().items():
        d = what_should_i_do(f)
        print(f"  {f} {d.floor_name:12s} {d.tier:6s} {d.action:11s} | {voice}")
    print()
    print("--- Sample TierDecision objects ---")
    for f in ["F1", "F5", "F9", "F12", "F13"]:
        print(f"  {what_should_i_do(f)}")
    print()
    print("--- Audit format examples ---")
    print(f"  {format_floor_status('F1')}")
    print(f"  {format_floor_status('F5', violated=True)}")
    print(f"  {format_floor_status('F9', violated=True)}")
    print()
    print("VERDICT: fiqh_helper is the agent-friendly face of F0_FIQH.md.")
    print("         Pure additive. No existing code broken.")
