"""
arifos://quickstart — LLM Client Getting Started Guide
═══════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, Not Given.

For LLM clients connecting to the arifOS MCP server for the first time.
Concise reference: what this server does, how to talk to it, what it can and cannot do.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

QUICKSTART_TEXT = """\
---arifos_meta
resource_class: supplemental
authority_level: STRUCTURAL
owner: ARIF_FAZIL
version: 2026.06.25
mutation_allowed: false
requires_actor_verified: false
requires_session: false
lease_required: false
blast_radius: LOW
evidence_level: CANONICAL
staleness_policy: warn
truth_level: 3
---end_arifos_meta

arifOS MCP Quickstart
════════════════════

ENDPOINT: https://mcp.arif-fazil.com/mcp
TRANSPORT: streamable-http + SSE
AUTH: Bearer token (A-FORGE sessions). Public tools require no auth.

WHAT THIS SERVER DOES:
  arifOS is the constitutional kernel of the arifOS Federation.
  It governs 7 organs: arifOS (kernel), GEOX (earth), WEALTH (capital),
  WELL (human readiness), A-FORGE (execution), AAA (control plane).
  arifOS does NOT execute code or manage infrastructure directly —
  it provides governance, judgment, and memory.

FIRST STEPS FOR AN LLM CLIENT:

  1. INITIALIZE SESSION
     Call arif_init first (mode="init"). This binds your session
     to the constitutional floors (F1-F13). Without init, you get
     only public tools. With init, you get governed tools.

  2. UNDERSTAND THE 7 STAGES
     Every task walks through 7 stages:
       000 arifosmcp_loop_engineer → classify intent
       111 SENSE  → observe reality
       333 REASON → plan, design, hypothesize
       555 JUDGE  → constitutional verdict
       666 CRITIQUE → consequence scan
       777 FORGE  → execute
       999 SEAL   → record immutably

  3. KNOW YOUR TOOLS (13 canonical):
     arif_init        — session bootstrap
     arif_observe     — multimodal observation
     arif_fetch       — verified external evidence
     arif_think       — symbolic reasoning
     arif_compose     — governed response
     arif_route       — canonical routing
     arif_triage      — session status/preflight
     arif_judge       — constitutional verdict (SEAL/SABAR/HOLD/VOID)
     arif_seal        — immutable ledger write
     arif_measure     — resource health
     arif_critique    — consequence assessment
     arif_bridge_connect — cross-organ bridge
     arif_forge       — execution (A-FORGE proxy)

  4. KNOW YOUR RESOURCES (13 canonical):
     arifos://doctrine         — F1-F13 constitutional floors
     arifos://trinity          — AAA lane definitions
     arifos://schema           — complete MCP blueprint
     arifos://civilization     — federation organ ontology
     arifos://seal-readiness   — vault integrity
     arifos://jurisdiction     — autonomy bands
     arifos://identity         — sovereign identity
     arifos://memory           — 6-layer memory
     arifos://vitals           — metric thresholds
     arifos://bootstrap        — full knowledge-graph context
     arifos://human/metabolized — compact sovereign context
     arifos://loop-engineering — 7-stage reality loop
     arifos://skills-catalog   — all available skills

  5. KNOW YOUR PROMPTS (8 registered):
     arifosmcp_loop_engineer — entry guard / intent classifier
     arifosmcp_000_init      — anchor identity
     arifosmcp_111_sense     — observe
     arifosmcp_333_reason    — plan
     arifosmcp_555_judge     — verdict
     arifosmcp_666_critique  — consequence
     arifosmcp_777_forge     — execute
     arifosmcp_999_seal      — record

KEY CONSTITUTIONAL RULES:
  F1  AMANAH    — Reversible first. Irreversible → 888_HOLD.
  F2  TRUTH     — Ground every claim. Declare Ω₀ for unknowns.
  F9  ANTIHANTU — C_dark < 0.30. No consciousness/soul claims.
  F13 SOVEREIGN — Human veto absolute. Arif decides irreversible.

WHAT arifOS IS NOT:
  ❌ Not a code execution engine → use A-FORGE for that
  ❌ Not a database → use postgres/supabase for that
  ❌ Not a web browser → use playwright for that
  ❌ Not a filesystem → use docker/github for that
  ❌ Not a GIS tool → use GEOX for that
  ❌ Not a financial advisor → use WEALTH for that

WHEN TO USE arifOS vs DIRECT ORGAN:
  Task: "Should I approve this action?"        → arifOS (arif_judge)
  Task: "Deploy this code"                      → A-FORGE (forge_execute)
  Task: "Analyze this seismic data"             → GEOX (geox_*)
  Task: "Calculate EMV of this prospect"        → WEALTH (wealth_*)
  Task: "Assess my fatigue level"              → WELL (well_*)
  Task: "Show federation health"                → AAA (a2a status)

VAULT999 — IMMUTABLE LEDGER:
  Only SEAL verdicts enter VAULT999.
  SEAL = irreversible. Think before you seal.
  Query: arif_vault_query | arif_seal

DITEMPA BUKAN DIBERI — Reality is forged, not given.

Questions? Start with arif_init then arif_observe.
"""


def register_quickstart(mcp: FastMCP) -> list[str]:
    """Register arifos://quickstart — getting started guide for LLM clients."""
    resource = TextResource(
        uri="arifos://quickstart",
        name="LLM Client Quickstart",
        description=(
            "Getting started guide for LLM clients connecting to arifOS MCP. "
            "Covers: endpoint, transport, auth, 13 canonical tools, 13 resources, "
            "8 prompts, 7 stages, key constitutional rules (F1-F13), "
            "when to use arifOS vs direct organ, and VAULT999 ledger guidance. "
            "Read this first before using the server."
        ),
        text=QUICKSTART_TEXT,
        tags={"resource", "quickstart", "getting-started", "llm-client"},
    )
    mcp.add_resource(resource)
    return ["arifos://quickstart"]


__all__ = ["register_quickstart"]
