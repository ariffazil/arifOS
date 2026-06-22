"""
arifos://trinity — AAA Trinity Lane Definitions
═══════════════════════════════════════════════
AGI proposes. ASI judges. APEX authorizes. FORGE executes.
Separation of powers is architectural, not aspirational.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

TRINITY_TEXT = """\
---arifos_meta
resource_class: constitution
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.06.21
mutation_allowed: false
requires_actor_verified: true
requires_session: true
lease_required: false
blast_radius: HIGH
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-06-22T00:00:00Z
truth_level: 1
---end_arifos_meta

arifOS AAA Trinity — Separation of Powers

┌─────────────────────────────────────────────────────────────┐
│  AGI proposes ──→ ASI judges ──→ APEX authorizes ──→ FORGE  │
│   (111)           (444)          (888)              (010)    │
└─────────────────────────────────────────────────────────────┘

THREE LANES:

  000 — GATEWAY (Entry)
    Anchor identity. Emit manifest. Root the audit chain.
    Tool: arif_init
    Domain language: SELAMAT / KUKUH / AMANAH / BIJAKSANA

  111 — AGI (Tactical Intelligence)
    Role: PROPOSE. Abstract, abduce, synthesize.
    Tools: arif_observe, arif_fetch, arif_think,
           arif_kernel_route, arif_memory_recall, arif_measure,
           arif_compose, arif_gateway_connect
    Domain language: OBSERVED / COMPUTED / INFERRED / HYPOTHESIZED / ESTIMATED / UNKNOWN
    NEVER: judge, authorize, seal

  444 — ASI (Strategic Judgment)
    Role: JUDGE. Attest. Floor-check. Deliberate. Emit verdict.
    Tools: arif_critique
    Domain language: CONSISTENT / NEEDS_CORRECTION / INSUFFICIENT
    NEVER: execute, authorize, seal

  888 — APEX (Authority Resolution)
    Role: AUTHORIZE. Verify verdict. Check sovereignty. Authorize or block.
    Tools: arif_judge
    Domain language: SEAL / SABAR / HOLD / VOID
    SEAL = constitutional approval, irreversibly sealed
    SABAR = held — needs more evidence or human review
    HOLD = blocked — constitutional violation
    VOID = rejected or self-contradictory

  999 — GATEWAY (Exit)
    Verify path. Write immutable record. Terminate session.
    Tool: arif_seal
    Domain language: SEALED / CHAIN_HEIGHT / MERKLE_LEAF

THE IRON RULE:
  No prompt can do another prompt's job.
  The AGI cannot judge. The ASI cannot authorize. The APEX cannot propose.
  This separation IS the constitution.

DITEMPA BUKAN DIBERI
"""


def register_trinity(mcp: FastMCP) -> list[str]:
    """Register arifos://trinity — AAA Trinity lane definitions."""
    resource = TextResource(
        uri="arifos://trinity",
        name="AAA Trinity Lanes",
        description=(
            "The AAA Trinity lane architecture: AGI proposes (111), ASI judges (444), "
            "APEX authorizes (888), FORGE executes (010), 999 seals. "
            "Defines which tools belong to which lane and which domain language each lane uses. "
            "SEAL/SABAR/HOLD/VOID are APEX-only verdict terms."
        ),
        text=TRINITY_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://trinity"]
