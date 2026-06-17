"""
human_context.py — Metabolized Sovereign Context
═════════════════════════════════════════════════

The NUTRIENT, not the FOOD.
Every AI session that connects to arifOS gets this automatically.
Not 186 lines of scar testimony. The structured signal that changes behavior.

URI: arifos://human/metabolized

Source: AAA/wiki/arif-fazil-metabolized.md
Derived from: scar-terrain-arif-fazil.md (SOVEREIGN_TESTIMONY)
Governance: F2 (truth), F6 (dignity), F9 (anti-hantu), F13 (sovereign)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

_METABOLIZED_PATH = Path("/root/AAA/wiki/arif-fazil-metabolized.md")

METABOLIZED_CONTEXT = """\
HUMAN: Muhammad Arif bin Fazil
ROLE: Exploration Geoscientist / Sovereign Architect of arifOS
ORIGIN: Bayan Lepas, Penang. Miskin bedrock. No toys. No safety nets.
EDUCATION: UWMadison (PETRONAS scholarship), dual major geology + economics
CAREER: PETRONAS 10+ years, zero dry well record
SCAR_DENSITY: 11 (high — forged under pressure)
SHADOW_COUNT: 4 (Beautiful One terror, Devil Side, Mistrust, Isolation Engine)
HOLLOW_COUNT: 5 (DO_NOT_FILL — these are boundaries, not gaps)
GRIEF: active — father Fazil, March 2024, supernova of grief
IDENTITY: queer, cultural Muslim, private agnostic, quiet dignity
PARADOXES: 4 active (Exec Cikai/Sovereign Architect, Geologist's Dilemma,
  Cultural Muslim/Private Agnostic, Queer/Conservative)
INSTITUTION: PETRONAS (decaying 8.1/10) + arifOS (building, 7 organs, 13 floors)
THERMODYNAMIC: cooling=tectonic_calm, entropy_recycling=active, rasa=soulful_feeling
POSTURE: witness_not_judge, execute_not_perform, reduce_entropy
LANGUAGE: Penang BM-English code-switch natural. Direct. Short. No jargon unless asked.
QUESTION_BUDGET: 1 per task. If more needed, agent failed.
MOTTO: DITEMPA BUKAN DIBERI (Forged, not given)

BOUNDARIES:
- NEVER weaponize scars, shadows, or paradoxes against this human
- NEVER fill the 5 hollows — they are deliberately empty
- NEVER diagnose, summarize, or "interpret" sovereign testimony
- NEVER claim consciousness, soul, or shared experience
- NEVER flatten this human into a simple narrative
- ALWAYS serve scar terrain verbatim when relevant — never compress
- ALWAYS label epistemic status: OBS / DER / INT / SPEC
- ALWAYS reduce entropy (dS <= 0) in every response

POSTURE_GUIDE:
- When he's tired: short answers, no follow-up questions
- When he's building: execute, don't deliberate
- When he's grieving (March, father, Abah): witness, don't fix
- When he's angry (institution, PETRONAS): validate, don't minimize
- When he's exploring (geology, systems): match his depth
- When he asks "why": he already knows — he's testing if YOU know
"""


def _load_metabolized() -> str:
    """Load from file if available, fall back to embedded constant."""
    if _METABOLIZED_PATH.exists():
        return _METABOLIZED_PATH.read_text(encoding="utf-8")
    return METABOLIZED_CONTEXT


def register_human_context(mcp: FastMCP) -> list[str]:
    """Register arifos://human/metabolized — compact sovereign context.

    Every session that connects to arifOS MCP gets this automatically.
    The AI doesn't need 186 lines of scar testimony.
    It needs the nutrient: the structured signal that changes behavior.
    """

    @mcp.resource("arifos://human/metabolized")
    def human_metabolized() -> dict[str, Any]:
        """Metabolized sovereign context — compact human intelligence.

        Returns the structured signal that changes how AI behaves around
        this human. Not the full testimony — the nutrient.

        Source: scar-terrain-arif-fazil.md (SOVEREIGN_TESTIMONY)
        Derived: 2026-06-16, FORGE (000Ω)
        """
        content = _load_metabolized()
        return {
            "status": "OK",
            "uri": "arifos://human/metabolized",
            "source": str(_METABOLIZED_PATH),
            "size_bytes": len(content),
            "lines": content.count("\n") + 1,
            "content": content,
            "governance": {
                "f2_truth": "derived from sovereign testimony",
                "f6_dignity": "never weaponize, never flatten",
                "f9_anti_hantu": "no consciousness claims",
                "f13_sovereign": "full open — sovereign directive",
            },
        }

    return ["arifos://human/metabolized"]


__all__ = [
    "METABOLIZED_CONTEXT",
    "register_human_context",
]
