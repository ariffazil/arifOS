"""
arifos://jurisdiction — Autonomy Bands & Capability Grants
══════════════════════════════════════════════════════════
Agents hold grants, never raw secrets. Jurisdiction is a lease,
not a possession.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

JURISDICTION_TEXT = """\
---arifos_meta
resource_class: governance
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

arifOS Jurisdiction — Autonomy Bands

FIVE BANDS (GREEN → BLACK):

  GREEN (T0 — Full Autonomy)
    Action class: OBSERVE
    Tools: sense, evidence, memory, ops, kernel route, gateway, reply
    Rule: Execute without asking. No human ack needed.
    Example: arif_observe, arif_think

  YELLOW (T1–T2 — Advisory Autonomy)
    Action class: OBSERVE / PREPARE
    Tools: mind_reason, heart_critique (critique mode)
    Rule: Execute. Log outcome. Human can override afterward.
    Example: arif_critique(mode=critique)

  ORANGE (T3 — Constrained Autonomy)
    Action class: PREPARE / MUTATE
    Tools: gateway_connect (cross-organ), heart_critique (redteam mode)
    Rule: Announce intent. 10-second window. Proceed unless stopped.
    Example: arif_gateway_connect(mode=route)

  RED (T4 — Gated Autonomy)
    Action class: MUTATE
    Tools: forge_execute (dry-run), judge_deliberate (compare mode)
    Rule: 888_HOLD required. Human ack before execution.
    Example: arif_forge(ack_irreversible=true)

  BLACK (T5 — Sovereign Only)
    Action class: ATOMIC
    Tools: judge_deliberate (judge mode), vault_seal, forge_execute (live)
    Rule: L13 SOVEREIGN veto. APEX authorization mandatory.
    Example: arif_seal(mode=seal)

CAPABILITY GRANTS:
  Agents hold CapabilityGrants, never raw secrets.
  A grant binds: agent_id → tool_name → autonomy_band → expiry
  Grants are leased, not owned. They expire. They can be revoked.

SECRETLESS EXECUTION:
  No agent receives raw API keys, tokens, or passwords.
  The kernel injects secrets at execution time from the canonical vault.
  Agent sees only: "provider_access: configured"

DITEMPA BUKAN DIBERI
"""


def register_jurisdiction(mcp: FastMCP) -> list[str]:
    """Register arifos://jurisdiction — autonomy bands and capability grants."""
    resource = TextResource(
        uri="arifos://jurisdiction",
        name="Jurisdiction & Autonomy Bands",
        description=(
            "The five autonomy bands (GREEN through BLACK) that govern agent freedom, "
            "the CapabilityGrant registry for secretless execution, and jurisdiction rules. "
            "Agents hold grants, never raw secrets. Autonomy is a leased capability, "
            "not a permanent possession. All tools mapped to their autonomy band."
        ),
        text=JURISDICTION_TEXT,
        tags={"resource", "jurisdiction", "autonomy", "grants"},
    )
    mcp.add_resource(resource)
    return ["arifos://jurisdiction"]
