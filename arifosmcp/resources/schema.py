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

Tools (12 canonical — 9-stage metabolic loop + preflight + bridge + memory governor):

  GATEWAY (Entry):
    000   arif_init      — Session bootstrap + identity binding
                            Modes: init, resume, validate, canary, preflight, triage

  AGI LANE (Tactical — Propose):
    111   arif_observe   — Reality observation, web search, URL fetch, vitals
                            Modes: search, fetch, ingest, compass, atlas, entropy_dS, vitals
    333   arif_think     — Cognitive engine: reason, plan, reflect, critique, metabolize
                            Modes: reason, reflect, verify, axioms, plan, plan_review, plan_approve,
                                   refactor_plan, metabolize, simulate
    444   arif_route     — Canonical intent router to correct federation organ
                            Modes: route, bridge (absorbed arif_bridge_connect)
    555   arif_critique  — Ethical risk + human impact assessment (maruah)
                            Modes: critique, redteam, maruah, shadow, deescalate, empathy

  MEMORY GOVERNOR:
    555m  arif_memory    — Constitutional memory gate (F1/F2/F4/F9/F11/F13)
                            Modes: recall, inspect, attest, remember, promote, revise, forget, audit

  ASI LANE (Strategic — Judge):
    666   arif_judge     — Constitutional verdict: SEAL_CANDIDATE | HOLD | SABAR | VOID
                            Modes: judge, compare, history, explain, floor_status, witness_consensus

  FORGE (Execute — gated by ASI verdict):
    777   arif_forge     — Guarded execution after SEAL_CANDIDATE
                            Modes: engineer, query, write, generate, commit, recall, dry_run

  COMPOSE (Output):
    888   arif_compose   — Governed response composition (call LAST)
                            Modes: compose, summarize, cite, tone_shift, style, format, nudge, repo_answer

  GATEWAY (Exit):
    999   arif_seal      — Immutable VAULT999 ledger append (irreversible)
                            Modes: seal, verify, ledger, changelog, audit, dry_run

Trinity Lanes:
  AGI  (Tactical)   | stages 000–555  | language: OBSERVED/COMPUTED/INFERRED
  ASI  (Strategic)  | stage 666       | language: SEAL_CANDIDATE/HOLD/SABAR/VOID
  FORGE (Execute)   | stage 777       | language: EXECUTED/ROLLED_BACK/SEALED
  COMPOSE (Output)  | stage 888       | language: COMPOSED/CITED/NUDGED
  GATEWAY           | 000 + 999       | session lifecycle anchors

Metabolic Loop:
  000 → 111 → 333 → 444 → 555 → 555m → 666 → 777 → 888 → 999
  init  observe think route critique memory judge  forge  compose seal
  One stage = one public verb. Absorbed verbs become modes on parent tool.

Floors (F1–F13):
  F01 AMANAH    — Irreversible = explicit ack
  F02 TRUTH     — τ ≥ 0.99 or declare uncertainty
  F03 WITNESS   — Evidence reproducible by independent observer
  F04 CLARITY   — Every output reduces entropy (ΔS ≤ 0)
  F05 PEACE     — Peace ≥ 1.0, de-escalate, guard maruah
  F06 EMPATHY   — Dignity-first, ASEAN/MY context
  F07 HUMILITY  — Uncertainty band 0.03–0.05, no fake certainty
  F08 GENIUS    — Elegant correctness, simple and robust
  F09 ANTIHANTU — C_dark < 0.30, no consciousness claims
  F10 ONTOLOGY  — AI-only ontology, no soul/feelings claims
  F11 AUDIT     — Verify identity before sensitive ops
  F12 INJECTION — Sanitize inputs, no prompt injection
  F13 SOVEREIGN — Human veto absolute

Separation of Powers:
  AGI proposes → ASI judges → FORGE executes → 999 seals
  No tool can do another tool's job.
  This separation IS the constitution.

FORGE BRIDGE (777):
  arif_forge — Guarded execution, gated by arif_judge SEAL_CANDIDATE.
  Authority flow: AGI proposes → ASI judges → FORGE executes → 999 seals.
  Interface contract: query /health for runtime capabilities.
  Output contract: generated artifact + delta_S reduction metric.
  Hardcoded paths to A-FORGE internals are PROHIBITED.

Absorbed Tools (modes on parent, not separate verbs):
  arif_canary       → arif_init(mode=canary)
  arif_triage       → arif_init(mode=triage) or arif_route(mode=triage)
  arif_fetch        → arif_observe(mode=fetch)
  arif_bridge_connect → arif_route(mode=bridge)
  arif_act          → arif_forge (internal alias)

DITEMPA BUKAN DIBERI
"""


def register_schema(mcp: FastMCP) -> list[str]:
    """Register arifos://schema — Complete Blueprint (Δ)."""
    resource = TextResource(
        uri="arifos://schema",
        name="Canonical Schema",
        description=(
            "Complete canonical blueprint of the arifOS MCP surface. "
            "Lists all 12 canonical tools organized by 9-stage metabolic loop + preflight + bridge + memory governor, "
            "13 constitutional floors (F1–F13), and the separation of powers doctrine. "
            "Use as the reference map for the entire constitutional kernel."
        ),
        text=SCHEMA_TEXT,
        tags={"resource", "blueprint", "governance", "tools"},
    )
    mcp.add_resource(resource)
    return ["arifos://schema"]
