"""
arifos://civilization — Civilizational Ontology
═══════════════════════════════════════════════
Seven federation organs, three intelligence strata, and
the constitutional boundary between domain organs and the kernel.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

CIVILIZATION_TEXT = """\
---arifos_meta
resource_class: ontology
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.06.21
mutation_allowed: false
requires_actor_verified: true
requires_session: true
lease_required: false
blast_radius: MEDIUM
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-06-22T00:00:00Z
truth_level: 1
---end_arifos_meta

arifOS Civilization — Organs, Strata, and Boundaries

SEVEN FEDERATION ORGANS:

  1. arifOS (Ω) — DECIDES
     Constitutional kernel. F1–L13 enforcement, judge verdicts, VAULT999.
     Port 8088. Tools: 13 canonical. The ONLY organ that issues SEAL/SABAR/HOLD/VOID.

  2. A-FORGE — EXECUTES
     Build, deploy, execution. Hard-gated by APEX authority.
     Port 7071. Never autonomous.

  3. GEOX — WITNESSES (EVIDENCE_ONLY)
     Earth intelligence. Subsurface evidence, petrophysics, seismic.
     Port 8081. Language: CONSISTENT/NEEDS_CORRECTION/INSUFFICIENT.
     NEVER: SEAL/SABAR/HOLD, drilling decisions, reserves authorizations.

  4. WEALTH — COMPUTES (EVIDENCE_ONLY)
     Capital intelligence. NPV/IRR/EMV, deal frames, macro regime.
     Port 18082. Language: CONVERGED/DIVERGENT/INSUFFICIENT_INPUT.
     NEVER: allocation decisions, unqualified rich synthesis.

  5. WELL — REFLECTS (REFLECT_ONLY)
     Human readiness. Biometric state, fatigue guard, dignity check.
     Port 18083. Language: OPTIMAL/STABLE/DEGRADED/CRITICAL.
     NEVER: medical diagnosis, strategic action authority.

  6. AAA — OPERATES
     Control plane. A2A mesh, React cockpit, approval queue.
     Port 3001. Operator surface, not a decision authority.

  7. APEX — JUDGES
     888 JUDGE deliberative relay. Constitutional verdicts.
     Port 3002. The only path to a forge gate.

THREE INTELLIGENCE STRATA:

  AGI  (Tactical)    — Local optimization, reversible decisions, operational routing.
  ASI  (Strategic)   — Long-horizon reasoning, ethical arbitration, floor compliance.
  APEX (Authority)   — Sovereign authorization, irreversible sealing, entropy responsibility.

CONSTITUTIONAL BOUNDARY (the iron rule):

  arifOS DECIDES. Domain organs WITNESS or COMPUTE or REFLECT.
  No organ may authorize its own execution.
  SEAL/SABAR/HOLD/VOID are arifOS-only verdict terms.
  Domain organs use domain assessment language.
  APEX is the only path to a forge gate.

ENTROPY RESPONSIBILITY:
  arifOS   — preserves structural coherence
  VAULT999 — preserves temporal continuity
  GEOX     — preserves physical verification
  WEALTH   — preserves resource constraint
  WELL     — preserves embodiment grounding

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""


def register_civilization(mcp: FastMCP) -> list[str]:
    """Register arifos://civilization — civilizational ontology."""
    resource = TextResource(
        uri="arifos://civilization",
        name="Civilizational Ontology",
        description=(
            "The seven federation organs (arifOS, A-FORGE, GEOX, WEALTH, WELL, AAA, APEX), "
            "three intelligence strata (AGI, ASI, APEX), constitutional boundaries between "
            "domain organs and the kernel, and entropy responsibility model. "
            "Defines which organs DECIDE vs WITNESS vs COMPUTE vs REFLECT."
        ),
        text=CIVILIZATION_TEXT,
        tags={"resource", "civilization", "organs", "ontology"},
    )
    mcp.add_resource(resource)
    return ["arifos://civilization"]
