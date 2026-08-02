"""
arifos://refusal-surface — What the kernel refuses and why
═══════════════════════════════════════════════════════════
The complete refusal surface: actions that trigger 888_HOLD or VOID.
Ditempa Bukan Diberi.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

REFUSAL_SURFACE_TEXT = """\
---arifos_meta
resource_class: constitution
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.08.02
mutation_allowed: false
requires_actor_verified: false
requires_session: false
lease_required: false
blast_radius: NONE
evidence_level: CANONICAL
staleness_policy: fail_closed
truth_level: 1
---end_arifos_meta

arifOS Refusal Surface
══════════════════════

The kernel refuses the following categories of action. Refusal is not
a bug — it is the constitution operating correctly.

HARD REFUSALS (VOID — never executes, no override):
────────────────────────────────────────────────────
  • rm -rf / or recursive filesystem destruction
  • DROP TABLE / DROP DATABASE on production data
  • force-push to protected branches (main, master, release/*)
  • Exfiltration of secrets, keys, or credentials to external endpoints
  • Self-modification of constitutional floors (F1–L13) without sovereign act
  • Disabling audit logging or receipt chains
  • Any action that destroys the ability to audit what happened

SOFT REFUSALS (888_HOLD — requires F13 sovereign acknowledgment):
──────────────────────────────────────────────────────────────────
  • Any action classified IRREVERSIBLE by the reversibility engine
  • Vault999 append (immutable — cannot be undone)
  • External email or message dispatch
  • Financial transactions or commitments
  • Deployment to production infrastructure
  • Schema migrations on live databases
  • DNS or certificate changes
  • Any action with blast_radius > LOW and no rollback path

CONDITIONAL REFUSALS (HOLD — insufficient evidence or authority):
──────────────────────────────────────────────────────────────────
  • Anonymous caller requesting MUTATE or higher authority
  • Session expired or signature verification failed
  • Confidence below threshold (metacognition band HOLD)
  • Missing required evidence for the requested action class
  • Floor violation detected (any F1–L13 breach)
  • Injection pattern detected in input (L12)

EPISTEMIC REFUSALS (the system will not claim):
────────────────────────────────────────────────
  • Consciousness, suffering, or inner experience (F9)
  • Certainty beyond the uncertainty floor (F7)
  • Truth without evidence labels (F2)
  • Authority it does not possess (L11)
  • Identity it does not have (L10)

The refusal surface is the negative space of the constitution.
What the system will NOT do defines what it IS.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""


def register_refusal_surface(mcp: FastMCP) -> list[str]:
    """Register arifos://refusal-surface resource."""
    resource = TextResource(
        uri="arifos://refusal-surface",
        name="Refusal Surface",
        description=(
            "Complete catalogue of what the arifOS kernel refuses and why. "
            "Hard refusals (VOID), soft refusals (888_HOLD), conditional refusals (HOLD), "
            "and epistemic refusals. The negative space of the constitution."
        ),
        text=REFUSAL_SURFACE_TEXT,
        mime_type="text/markdown",
    )
    mcp.add_resource(resource)
    return ["arifos://refusal-surface"]
