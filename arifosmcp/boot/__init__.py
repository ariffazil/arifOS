"""
arifOS Boot Governor — Swarm Ignition Kernel

DITEMPA BUKAN DIBERI — Forged, Not Given.

Package:  arifosmcp.boot
Purpose: Federated Boot Governor — swarm ignition, VAULT999 reconstruction,
         lease registry, capability attestation, task continuity.

Architecture:
  swarm_schemas.py    — 5 canonical Pydantic v2 models
  swarm_manifest.py   — build_swarm_manifest()
  swarm_registry.py   — SWARM_STATE_LEDGER (Redis)
  vault999_state.py   — Latest seal + reconstruct from VAULT999
  lease_registry.py   — LEASE_LEDGER (Redis)
  capability_attest.py— CAPABILITY_LEDGER (NATS)
  task_registry.py    — TASK_LEDGER (Redis)
  swarm_ignition.py   — Orchestrator INIT_0→INIT_10

Invariant:
  tools.py remains the MCP surface.
  boot/ is the ignition kernel.
  VAULT999 is the black box.
  Redis is the live swarm state.
  NATS is the federation nervous system.
"""

from arifosmcp.boot.swarm_schemas import (
    BootReceipt,
    CapabilityAttestation,
    ReIgnitionReceipt,
    SwarmLease,
    SwarmManifest,
)

__all__ = [
    "BootReceipt",
    "SwarmManifest",
    "CapabilityAttestation",
    "SwarmLease",
    "ReIgnitionReceipt",
]
