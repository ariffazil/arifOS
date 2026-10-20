"""
arifos://doctrine — Immutable Law (Ψ)
══════════════════════════════════════
The 13 Constitutional Laws (F1–L13).
Ditempa Bukan Diberi.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

from arifosmcp.constitutional_canon import doctrine_block

# Floor block is derived from arifosmcp.constitutional_canon — the single
# machine-readable source for F1–F13. Do NOT retype floor names here: the
# 2026-10-20 drift (F06 MARUAH here vs F06 EMPATHY in arif_think) happened
# precisely because this text and the axioms catalogue were typed twice.
DOCTRINE_TEXT = """\
---arifos_meta
resource_class: constitution
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.10.20
mutation_allowed: false
requires_actor_verified: true
requires_session: true
lease_required: false
blast_radius: HIGH
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-10-20T13:30:00Z
truth_level: 1
---end_arifos_meta

Amendment 2026-10-20: F02 confidence band restored to 1 − Ω₀ ∈ [0.95, 0.97]
(per GENESIS/000_KERNEL_CANON.md §3.2 F7 unification); floor block is now
rendered from arifosmcp.constitutional_canon — no floor name is retyped here.

arifOS Doctrine — 13 Floors (F1–F13)

{{FLOORS}}

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

# Single-line substitution keeps the ratified text as ONE literal (the
# resource-conformance test parses the literal) while the floor block is
# rendered from arifosmcp.constitutional_canon — never retyped.
DOCTRINE_TEXT = DOCTRINE_TEXT.replace("{{FLOORS}}", doctrine_block())


def register_doctrine(mcp: FastMCP) -> list[str]:
    """Register arifos://doctrine — Immutable Law (Ψ)."""
    resource = TextResource(
        uri="arifos://doctrine",
        name="Constitutional Doctrine",
        description=(
            "The immutable 13-floor constitution (F1–F13) that governs all arifOS operations. "
            "Includes Amanah, Truth, Witness, Clarity, Peace, Maruah, Humility, Genius, "
            "Anti-Hantu, Ontology, Audit, Injection, and Sovereign. "
            "Source of truth for floor definitions. Audited 2026-07-15."
        ),
        text=DOCTRINE_TEXT,
        tags={"resource", "constitution", "sovereign", "immutable"},
    )
    mcp.add_resource(resource)
    return ["arifos://doctrine"]
