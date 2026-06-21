"""
arifos://seal-readiness — Vault Integrity & Seal Readiness
══════════════════════════════════════════════════════════
Reports vault health, chain integrity, and seal gate status.
Does NOT contain secret values — this is a diagnostic resource.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

SEAL_TEXT = """\
---arifos_meta
resource_class: governance
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
truth_level: 1  # SOVEREIGN_CANON (1-7 scale)
---end_arifos_meta

arifOS Seal Readiness — Vault Integrity Report

VAULT999:
  Type:         Append-only hash-chained ledger
  Layers:       3 (local JSONL + Postgres + Supabase)
  Writer:       vault999-writer (port 5001)
  API:          vault999-api (port 8100)
  Chain:        Merkle leaf chain, SHA-256

SEAL TYPES (disambiguated):
  KERNEL_SEAL_AWARENESS    — kernel knows about it (informational)
  DOMAIN_SEAL_VALIDITY     — calculation valid in domain (e.g. WEALTH NPV converged)
  JUDGE_SEAL_AUTHORIZATION — action authorized (F1–L13 cleared, APEX present)
  VAULT999_SEAL_RECORD     — record written (immutable audit trail entry exists)
  PUBLIC_SEAL_READINESS    — candidate posture, not execution approval

SEAL GATE (what must pass before a SEAL):
  1. F1 AMANAH:     ack_irreversible = true
  2. F2 TRUTH:      tau_confidence >= 0.99
  3. F3 WITNESS:    witness triad scores present
  4. F8 REVERSIBILITY: escape path documented
  5. F9 ANTIHANTU:  C_dark < 0.30
  6. L11 AUTH:      actor identity verified
  7. L13 SOVEREIGN: human ratifier = arif-fazil

NON-SEAL VERDICTS:
  SABAR — held, needs more evidence or human review
  HOLD  — blocked by constitutional floor violation
  VOID  — rejected or self-contradictory

Bare "SEAL" without namespaced context is NON-COMPLIANT.
Every seal must declare its type.

DITEMPA BUKAN DIBERI
"""


def register_seal_readiness(mcp: FastMCP) -> list[str]:
    """Register arifos://seal-readiness — vault integrity and seal gate."""
    resource = TextResource(
        uri="arifos://seal-readiness",
        name="Seal Readiness & Vault Integrity",
        description=(
            "Vault integrity report and seal gate requirements. "
            "Defines the five disambiguated seal types, the seven-floor seal gate, "
            "and the non-seal verdicts (SABAR/HOLD/VOID). "
            "Bare SEAL without namespace is non-compliant."
        ),
        text=SEAL_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://seal-readiness"]
