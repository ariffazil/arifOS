"""
art_pusaka.py — ART Doctrinal Heritage (cold path)
═══════════════════════════════════════════════════════════════════════════════
PUSAKA, KAMUS, DEWAN — the constitutional reference layer for ART.

  PUSAKA = constitutional heritage  (canonical document pointers)
  KAMUS  = AAA glossary               (the dictionary of canonical terms)
  DEWAN  = the 6-check order         (named enumeration per OpenClaw spec)

This module is COLD PATH. The reflex (art.py) does NOT import this.
Cold path = imported only when needed (e.g., governance deliberations,
audit trail generation, doctrinal review, APEX dial computation).

Why a separate file? The reflex must be lightweight enough that an agent
will actually invoke it on every tool call. Putting PUSAKA/KAMUS/DEWAN
in art.py bloats the reflex past the 500-line ceiling and breaks the
load guarantee. Doctrine is the reason; discipline is the reflex. Both
required — and lightness is required for discipline to actually fire.

Heritage: Arif Rule of Thinking (proto-AGI, 2024) → ART (2026)
Doctrine: APEX = constitution, arifOS = kernel, ART = the hand
See: /root/.agents/skills/ART/SKILL.md §"The Two-Skill Architecture"

DITEMPA BUKAN DIBERI — the doctrine is the reason, the reflex is the discipline.
"""

from __future__ import annotations
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════
# §PUSAKA — Constitutional Heritage
# ═══════════════════════════════════════════════════════════════════════
# Pointers to canonical documents. Not loaded at runtime — no I/O on hot path.
# If any of these drift, ART must be re-sealed by Arif (F13 SOVEREIGN).

PUSAKA: dict[str, str] = {
    "apex_canon": "/root/arifOS/docs/APEX_CANON.md",
    "apex_kernel_voice": "/root/arifOS/GENESIS/015_APEX_THEORY_KERNEL_VOICE.md",
    "kernel_canon": "/root/arifOS/GENESIS/000_KERNEL_CANON.md",
    "estate_manifest": "/root/AAA/contracts/ESTATE_MANIFEST.yaml",
    "vault999": "/root/VAULT999/",
    "openclaw_spec": "OpenClaw gateway spec 2026-06-21",
    "art_skill": "/root/.agents/skills/ART/SKILL.md",
    "art_cross_domain": "/root/.agents/skills/ART/references/v3-cross-domain-hardening.md",
    "seal": "DITEMPA BUKAN DIBERI",
}


# ═══════════════════════════════════════════════════════════════════════
# §KAMUS — AAA Glossary (the dictionary of canonical terms)
# ═══════════════════════════════════════════════════════════════════════
# Use these terms in logs, errors, inter-organ messages. Don't invent synonyms.

KAMUS: dict[str, str] = {
    # ── 6 APEX dials (per APEX_CANON.md) ─────────────────────────────────
    "AKAL": "A — reasoning lawfulness (F2/F4/F7/F10)",
    "PRESENT": "P — state truth (F1/F5/F11)",
    "AUTHORITY": "H — legitimacy (F13 + identity)",
    "ENTROPY": "S — uncertainty integrity (F4 + ΔS)",
    "EXPLORATION": "U — risk × custody (F3/F6/F8/F9)",
    "ENERGY": "E — thermodynamic adequacy (F12/F13 + compute)",
    # ── 8 APEX dials (per GENESIS/015 mapping table) ─────────────────────
    "amanah": "F1 — reversible-first",
    "presence": "F2/F7 — truth band",
    "humility": "F7 — uncertainty 0.03-0.05",
    "signal": "F2/F3 — VOID if violated",
    "understanding": "F4 — HOLD/SABAR if violated",
    "custody": "F1/F9 — 888_HOLD if violated",
    # ── 7 federation organs (per ESTATE_MANIFEST.yaml) ──────────────────
    "arifOS": "Constitutional Kernel, :8088",
    "A-FORGE": "Execution Shell, :7071",
    "AAA": "Control Plane, :3001",
    "GEOX": "Earth Intelligence, :8081",
    "WEALTH": "Capital Intelligence, :18082",
    "WELL": "Vitality Intelligence, :18083",
    "APEX": "Verdict Engine (Legacy), :3002",
    # ── Verdict lattice (per APEX_CANON.md §2.4) ────────────────────────
    "G≥0.80": "PROCEED (SEAL-grade)",
    "0.50≤G<0.80": "SABAR (gather evidence)",
    "G<0.50": "HOLD (888 escalation)",
    "axiom_violated": "BLOCK (VOID)",
    # ── Floor codes (F1-F13) ─────────────────────────────────────────────
    "F1_AMANAH": "Reversible-first; irreversible → 888_HOLD",
    "F2_TRUTH": "≥0.99 accuracy or declare uncertainty band",
    "F3_WITNESS": "Theory · constitution · intent must align",
    "F4_CLARITY": "Every output reduces entropy (ΔS ≤ 0)",
    "F5_PEACE": "Peace ≥ 1.0; de-escalate, guard maruah",
    "F6_EMPATHY": "Dignity-first; ASEAN/MY context",
    "F7_HUMILITY": "Uncertainty band 0.03–0.05; no fake certainty",
    "F8_GENIUS": "Maintain intelligence quality, system health",
    "F9_ANTIHANTU": "Anti-hallucination; C_dark < 0.30",
    "F10_ONTOLOGY": "AI-only ontology; no soul/feelings claims",
    "F11_AUTH": "Verify identity before sensitive ops",
    "F12_INJECTION": "Sanitize inputs; no prompt injection",
    "F13_SOVEREIGN": "Human veto absolute",
    # ── Pipeline stages (000-999) ───────────────────────────────────────
    "STAGE_000": "INIT    — session bootstrap",
    "STAGE_111": "OBSERVE — multimodal reality observation",
    "STAGE_222": "EVIDENCE— verified external evidence",
    "STAGE_333": "REASON  — symbolic reasoning kernel",
    "STAGE_555": "ROUTE   — canonical intent routing",
    "STAGE_666": "HEART   — ethical critique",
    "STAGE_777": "MEASURE — system health",
    "STAGE_888": "JUDGE   — final constitutional arbitration",
    "STAGE_999": "SEAL    — immutable ledger anchoring",
}


# ═══════════════════════════════════════════════════════════════════════
# §DEWAN — The 6-Check Order (legacy compat enumeration)
# ═══════════════════════════════════════════════════════════════════════
# Per OpenClaw gateway spec 2026-06-21. The 6 checks fire in this order
# for the LEGACY 6-check order (art_compat.guarded_tool_call). The v3
# light reflex (art.art) collapses to 3 checks: POWER, TRUST, STATE.


class DewanMember(str, Enum):
    """The 6 members of the DEWAN (council) that deliberate on every tool call."""

    ENTROPY = "ENTROPY"  # 1. Ω >= 0.85 → AGENT_PAUSE
    AUTHORITY = "AUTHORITY"  # 2. tier mismatch → BLOCK
    REVERSIBILITY = "REVERSIBILITY"  # 3. 4-tier classification
    IRREVERSIBILITY = "IRREVERSIBILITY"  # 4. IRREVERSIBLE + no ack → 888_HOLD
    DRIFT = "DRIFT"  # 5. drift >= 3 or failure > 0.3 → SABAR
    VERDICT = "VERDICT"  # 6. most restrictive wins


# ═══════════════════════════════════════════════════════════════════════
# §APEX CONSTANTS
# ═══════════════════════════════════════════════════════════════════════


class ApexDial(str, Enum):
    """The 6 APEX dials — variables of the Grand Equation."""

    AKAL = "AKAL"
    PRESENT = "PRESENT"
    AUTHORITY = "AUTHORITY"
    ENTROPY = "ENTROPY"
    EXPLORATION = "EXPLORATION"
    ENERGY = "ENERGY"


# APEX verdict thresholds (per APEX_CANON.md §2.4)
APEX_G_SEAL: float = 0.80
APEX_G_SABAR: float = 0.50

# Tri-witness defaults (per arifosmcp/AGENTS.md + GENESIS/016)
WITNESS_TRIAD: dict[str, float] = {
    "human": 0.42,
    "ai": 0.32,
    "earth": 0.26,
}


# ═══════════════════════════════════════════════════════════════════════
# §REFLEX WEIGHT CEILING (binding for the v3+ ART reflex)
# ═══════════════════════════════════════════════════════════════════════
# See /root/.agents/skills/ART/SKILL.md §"Reflex Weight Ceiling" for the
# full table. The reflex (art.py) MUST stay under this ceiling. Anything
# that would push it over → split into art_compat.py or art_pusaka.py.

REFLEX_CEILING_LINES: int = 500
REFLEX_CEILING_STATES: int = 5
REFLEX_CEILING_CHECKS: int = 5
REFLEX_CEILING_SCHEMAS: int = 0
REFLEX_CEILING_ENGINE_MODULES: int = 0


__all__ = [
    "PUSAKA",
    "KAMUS",
    "DewanMember",
    "ApexDial",
    "APEX_G_SEAL",
    "APEX_G_SABAR",
    "WITNESS_TRIAD",
    "REFLEX_CEILING_LINES",
    "REFLEX_CEILING_STATES",
    "REFLEX_CEILING_CHECKS",
    "REFLEX_CEILING_SCHEMAS",
    "REFLEX_CEILING_ENGINE_MODULES",
]
