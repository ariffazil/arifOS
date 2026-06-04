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
arifOS Schema — Canonical Blueprint (Δ)

Tools (13 canonical — AAA Trinity aligned):

  GATEWAY (Entry):
    000  arif_session_init         — Session bootstrap + identity binding

  AGI LANE (Tactical — Propose):
    111  arif_sense_observe        — Reality observation, web search
    222  arif_evidence_fetch       — External evidence retrieval
    333  arif_mind_reason          — Symbolic reasoning kernel
    555  arif_kernel_route         — Tool routing and staging
    555m arif_memory_recall        — Associative memory (L1-L6)
    777  arif_ops_measure          — System health and vitals
    666g arif_gateway_connect      — Cross-organ federation bridge
    444r arif_reply_compose        — Governed response composition

  ASI LANE (Strategic — Judge):
    444  arif_heart_critique       — Ethical critique, red team, de-escalation

  APEX LANE (Authority — Authorize):
    888  arif_judge_deliberate     — Final constitutional arbitration

  GATEWAY (Exit):
    999  arif_vault_seal           — Immutable ledger anchoring

  FORGE (Execute — gated by APEX):
    010  arif_forge_execute        — Build and deployment execution

Trinity Lanes:
  AGI  (Tactical)   | stages 000–777 | language: OBSERVED/COMPUTED/INFERRED
  ASI  (Strategic)  | stage 444      | language: CONSISTENT/NEEDS_CORRECTION
  APEX (Authority)  | stage 888      | language: SEAL/SABAR/HOLD/VOID
  GATEWAY           | 000 + 999      | session lifecycle anchors

Floors (F1–F13):
  F01 AMANAH   — Irreversible = explicit ack
  F02 TRUTH    — τ ≥ 0.99 or declare uncertainty
  F03 WITNESS  — Evidence reproducible by independent observer
  F04 CLARITY  — Every output reduces entropy (ΔS ≤ 0)
  F05 PEACE    — Peace ≥ 1.0, de-escalate, guard maruah
  F06 EMPATHY  — Dignity-first, ASEAN/MY context
  F07 HUMILITY — Uncertainty band 0.03–0.05, no fake certainty
  F08 GENIUS   — Elegant correctness, simple and robust
  F09 ANTIHANTU — C_dark < 0.30, no consciousness claims
  F10 ONTOLOGY — AI-only ontology, no soul/feelings claims
  F11 AUTH     — Verify identity before sensitive ops
  F12 INJECTION — Sanitize inputs, no prompt injection
  F13 SOVEREIGN — Human veto absolute

Separation of Powers:
  AGI proposes → ASI judges → APEX authorizes → FORGE executes → 999 seals
  No prompt can do another prompt's job.
  This separation IS the constitution.

FORGE BRIDGE (010):
  arif_forge_execute — Build and deployment execution.
  Gated by APEX authority (must have prior JUDGE_SEAL_AUTHORIZATION).
  Authority flow: AGI proposes → ASI evaluates → APEX authorizes → Forge executes.
  Interface contract: query /health for runtime capabilities.
  Output contract: generated artifact + delta_S reduction metric.
  Hardcoded paths to A-FORGE internals are PROHIBITED.

DITEMPA BUKAN DIBERI
"""


def register_schema(mcp: FastMCP) -> list[str]:
    """Register arifos://schema — Complete Blueprint (Δ)."""
    resource = TextResource(
        uri="arifos://schema",
        name="Canonical Schema",
        description=(
            "Complete canonical blueprint of the arifOS MCP surface. "
            "Lists all 13 tools organized by AAA Trinity lane (AGI/ASI/APEX), "
            "13 constitutional floors with invariants, and the separation of powers doctrine. "
            "Use as the reference map for the entire constitutional kernel."
        ),
        text=SCHEMA_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://schema"]
