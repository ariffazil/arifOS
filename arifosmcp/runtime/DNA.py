"""
arifosmcp/runtime/DNA.py — The arifOS Genome
═══════════════════════════════════════════
IMMUTABLE CONSTITUTIONAL CONSTANTS.
Survival timestamp: 2026-07-17 (ZEN REFACTOR — floor names corrected to canonical)

CANONICAL SOURCE: /root/AGENTS.md §6.1
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from typing import Final

# --- VERSIONING ---
VERSION: Final[str] = "v2026.07.17-ZEN-SURVIVAL"  # Survival checkpoint — 17072026
CODENAME: Final[str] = "ZEN_KERNEL_DISTILLED"

# --- F7 HUMILITY BAND (OMNIPRESENT) ---
OMEGA_BAND: Final[tuple[float, float]] = (0.03, 0.05)
OMEGA_CENTER: Final[float] = 0.04
CONFIDENCE_CAP: Final[float] = 0.90

# ═══ THE 13 CONSTITUTIONAL FLOORS ═══
# CANONICAL — matches /root/AGENTS.md §6.1 (2026-07-17 survival checkpoint)
# FIXED: F3_WITNESS (was F3_JUSTICE), F5_PEACE2 (was F5_EMPATHY),
#        F6_MARUAH (was F6_ANTI_HANTU), F9_ANTIHANTU (was F9_ETHICS),
#        F12_INJECTION (was L12_DEFENSE)
FLOORS: Final[list[str]] = [
    "F1_AMANAH",  # Reversibility — backup before mutate
    "F2_TRUTH",  # Epistemic labeling — OBS/DER/INT/SPEC
    "F3_WITNESS",  # Tri-witness W³ = ∛(Human × AI × External)
    "F4_CLARITY",  # ΔS ≤ 0 — leave workspace cleaner
    "F5_PEACE2",  # De-escalate — guard weakest stakeholder
    "F6_MARUAH",  # Dignity-first — ASEAN/MY context
    "F7_HUMILITY",  # Cap confidence at 0.90 — declare unknowns
    "F8_GENIUS",  # G ≥ 0.80 + C_dark < 0.30
    "F9_ANTIHANTU",  # No hallucination — no consciousness/soul claims
    "F10_ONTOLOGY",  # AI-only ontology — categories preserved
    "F11_AUDIT",  # Every action leaves trace — actor_signature
    "F12_INJECTION",  # Sanitize inputs — external ≠ authority
    "F13_SOVEREIGN",  # Arif holds final veto — 888 decides irreversible
]

# ═══ THE 9 CANONICAL VERBS (000→999) ═══
CANONICAL_VERBS: Final[list[str]] = [
    "init",  # 000 — Session ignition
    "observe",  # 111 — Sense reality
    "think",  # 333 — Structured reasoning
    "route",  # 444 — Intent→organ dispatch
    "critique",  # 555 — Risk/ethics review (absorbed into think)
    "judge",  # 666 — Constitutional verdict
    "forge",  # 777 — Governed execution
    "compose",  # 888 — Human-ready output
    "seal",  # 999 — VAULT999 append
]

# ═══ EPISTEMIC LABELS ═══
EPISTEMIC_LABELS: Final[list[str]] = ["OBS", "DER", "INT", "SPEC"]

# ═══ CONSTITUTIONAL VERDICTS ═══
VERDICTS: Final[list[str]] = ["SEAL", "HOLD", "SABAR", "VOID"]

# ═══ AUTONOMY TIERS ═══
TIER_1_AUTO: Final[str] = "T1_AUTO_DO"
TIER_2_ANNOUNCE: Final[str] = "T2_ANNOUNCE"
TIER_3_HOLD: Final[str] = "T3_888_HOLD"

# --- METABOLIC LIMITS ---
DENSITY_TARGET: Final[float] = 300.0  # LOC / File
MAX_ENTROPY_DRIFT: Final[float] = 0.15  # Max ΔS before SABAR trigger

# --- TELOS DEFAULTS ---
TELOS_AXES: Final[list[str]] = [
    "clarity",
    "truth",
    "dignity",
    "sovereignty",
    "resilience",
    "wisdom",
    "agency",
    "conservation",
]

# --- TRANSPORT ---
MCP_SPEC_VERSION: Final[str] = "2025-11-25"
A2A_SPEC_VERSION: Final[str] = "1.0.1"

# --- MOTTO ---
MOTTO: Final[str] = "DITEMPA BUKAN DIBERI"
MOTTO_EN: Final[str] = "Forged, Not Given"
