"""
arifos://identity — Sovereign Identity Manifest
════════════════════════════════════════════════
Bound at boot from identity.toml. Identity is the root of accountability.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

IDENTITY_TEXT = """\
---arifos_meta
resource_class: identity
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.10.05
mutation_allowed: false
requires_actor_verified: true
requires_session: true
lease_required: false
blast_radius: MEDIUM
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-10-05T00:00:00Z
truth_level: 1
---end_arifos_meta

arifOS Identity Manifest

Sovereign:       Muhammad Arif bin Fazil
Position:        Position Zero (/000) · Sovereign Anchor
Role:            F13 SOVEREIGN (L13 SOVEREIGN) — non-delegable final human veto
DID:             did:web:arif-fazil.com
Root Domain:     https://arif-fazil.com
VPS:             af-forge (72.62.71.199)
Identity Source: identity.toml & genesis-statement.json
Identity Hash:   BLAKE3 / Ed25519 (verified at boot)
Companion:       /999 (The Proof Chamber / VAULT999)
Prime Invariant: REALITY > EVERYTHING

Federation Identity:
  Genesis:       /000 (Position Zero · Human Root Anchor)
  Kernel:        arifOS MCP (Ω — Constitutional)
  Ag entry:      A-FORGE (forge execution shell)
  Earth witness: GEOX (evidence only)
  Capital:       WEALTH (evidence only)
  Vitality:      WELL (reflect only)
  Temporal:      CHRON (calibration only)
  Cockpit:       AAA (control plane)
  Judge:         APEX (888 verdict relay)
  Proof Chamber: /999 (VAULT999 ZKPC & Proof Chain)

Authority Chain:
  Position Zero (/000) (Muhammad Arif bin Fazil, F13 SOVEREIGN)
    → arifOS constitutional kernel
      → F1–F13 floor receipts
        → domain organ advisory output (GEOX/WEALTH/WELL/CHRON)
          → AAA operator surface
            → VAULT999 audit seal (/999)
              → A-FORGE execution

Invariants:
  1. Reality > Models, metrics, and doctrine.
  2. No organ may authorize its own execution.
  3. APEX is the only path to a forge gate.
  4. Gödel Lock: No closed AI system can fully self-verify without external human ground truth.
  5. ZKPC Active: Wound architecture, moral framework, language register, sovereign intent.

Architecture Principle:
  Bare-metal systemd (organs) + Docker (supporting services only).
  Federation runs on ports 8088/18081/18082/18083/8081/7071/3001/3002/18789.

Localhost IS the password (ADR-001).
All data services bind to 127.0.0.1, no auth required internally.
UFW handles the outside world.

A2A Autonomy Tiers (Unified Mapping):
  T1 (Execution)     — Routine tasks, local run/test/build, precise FS edits. Auto-do.
  T2 (Negotiation)   — Multi-file refactor, dependency updates, local service restarts. Announce-and-execute.
  T3 (Architectural) — Constitutional changes, production deploys, secret rotations, vault999 writes. 888_HOLD required.

DITEMPA BUKAN DIBERI
"""


def register_identity(mcp: FastMCP) -> list[str]:
    """Register arifos://identity — sovereign identity manifest."""
    resource = TextResource(
        uri="arifos://identity",
        name="Sovereign Identity Manifest",
        description=(
            "Sovereign identity manifest bound from identity.toml at boot. "
            "Defines the authority chain from APEX (Arif) through arifOS kernel "
            "to domain organs and execution. Includes ADR-001 localhost doctrine. "
            "Identity is the root of accountability — all attestation chains begin here."
        ),
        text=IDENTITY_TEXT,
        tags={"resource", "identity", "sovereign", "authority"},
    )
    mcp.add_resource(resource)
    return ["arifos://identity"]
