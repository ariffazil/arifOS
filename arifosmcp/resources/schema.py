"""
arifos://schema — Complete Blueprint (Δ)
═════════════════════════════════════════
Canonical tool surface, AAA Trinity lanes, and floor bindings.
Reflects the AAA Trinity architecture (000/111/444/888/999).
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

SCHEMA_TEXT = """\
---arifos_meta
resource_class: blueprint
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.07.07
mutation_allowed: false
requires_actor_verified: true
requires_session: true
lease_required: false
blast_radius: MEDIUM
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-07-07T00:00:00Z
truth_level: 1
---end_arifos_meta

arifOS Schema — Canonical Blueprint (Δ)

Source of truth: abi/capability_registry.json → KERNEL_ABI_8
Audited: 2026-07-15 (PROBE-01..08). Wire-verified: 8 tools, harness-agnostic.

Tools (8 canonical — capability-registered, wire-exposed):

  SESSION:
    000   arif_init      — Session bootstrap + identity binding
                            Modes: init, light, resume, validate, canary, preflight, triage
                            Capability: session.bind

  OBSERVATION:
    111   arif_observe   — Reality observation, web search, URL fetch, vitals
                            Modes: search, fetch, ingest, compass, atlas, entropy_dS, vitals
                            Capability: reality.observe

  COGNITION:
    333   arif_think     — Structured reasoning under F2/F7
                            Modes: reason, reflect, verify, axioms, plan, plan_review,
                                   plan_approve, refactor_plan, metabolize, simulate, critique
                            Capability: cognition.think
                            Note: critique mode absorbed here (not a separate tool)

  ROUTING:
    444   arif_route     — Intent router to correct federation organ
                            Modes: route, bridge, triage
                            Capability: intent.route

  MEMORY:
    555   arif_memory    — Constitutional memory gate (F1/F2/F4/F9/F11/F13)
                            Modes: recall, inspect, attest, remember, promote, revise, forget, audit, metabolize
                            Capability: memory.govern

  JUDGMENT:
    666   arif_judge     — Constitutional verdict: SEAL | HOLD | SABAR | VOID
                            Modes: judge, compare, history, explain, floor_status, witness_consensus
                            Capability: authority.judge

  EXECUTION:
    777   arif_forge     — Guarded execution after arif_judge SEAL
                            Modes: engineer, query, write, generate, commit, recall, dry_run
                            Capability: action.execute
                            Note: compose mode absorbed here (not a separate tool)

  SEAL:
    999   arif_seal      — VAULT999 immutable append (irreversible)
                            Modes: seal, verify, ledger, changelog, audit, dry_run
                            Capability: history.seal

Trinity Lanes:
  AGI   (Tactical)  | stages 000–555  | tools: init, observe, think, route, memory
  ASI   (Strategic) | stage 666       | tool: judge
  FORGE (Execute)   | stage 777       | tool: forge
  GATEWAY           | 000 + 999       | session lifecycle anchors

Pipeline (capability-enforced, not convention):
  000 → 111 → 333 → 444 → 555 → 666 → 777 → 999
  init  observe think route memory judge  forge  seal

Floors (F1–F13 — rendered from arifosmcp.constitutional_canon, not retyped):
{{FLOORS}}

Separation of Powers:
  arif_think proposes → arif_judge adjudicates → arif_forge executes → arif_seal records
  No tool can do another tool's job.

Absorbed Tools (modes on parent, not separate verbs):
  arif_critique       → arif_think(mode=critique)
  arif_compose        → arif_forge(mode=compose) [internal]
  arif_canary         → arif_init(mode=canary)
  arif_triage         → arif_init(mode=triage) or arif_route(intent=...) [W-05 FIX: no mode=]
  arif_fetch          → arif_observe(mode=fetch)
  arif_bridge_connect → arif_route(intent=..., organ_tool=...) [W-05 FIX: no mode=]
  arif_act            → arif_forge (internal alias)

DITEMPA BUKAN DIBERI
"""

# Single source substitution (2026-10-20). This block used to carry a copy of
# the floor table that retained an obsolete value long after F13
# sealed the Ω₀ band — a copy is a drift site, so render it instead.
from arifosmcp.constitutional_canon import doctrine_block as _doctrine_block  # noqa: E402

SCHEMA_TEXT = SCHEMA_TEXT.replace("{{FLOORS}}", _doctrine_block())


def register_schema(mcp: FastMCP) -> list[str]:
    """Register arifos://schema — Complete Blueprint (Δ)."""
    resource = TextResource(
        uri="arifos://schema",
        name="Canonical Schema",
        description=(
            "Complete canonical blueprint of the arifOS MCP surface. "
            "Lists 8 canonical tools (capability-registered, wire-verified), "
            "13 constitutional floors (F1–F13), and the separation of powers doctrine. "
            "Source of truth: abi/capability_registry.json. Audited 2026-07-15."
        ),
        text=SCHEMA_TEXT,
        tags={"resource", "blueprint", "governance", "tools"},
    )
    mcp.add_resource(resource)
    return ["arifos://schema"]
