"""
arifosmcp/federation — Organ Constitution Registry
══════════════════════════════════════════════════════════════════════════════
The formal constitutional surface for the arifOS federation.

This package closes the gap between "each organ has a /health endpoint" and
"the federation has a single observable, hashable, F2-auditable constitution."

Components:
  - organ_constitution.py    — Pydantic v2 schema for one organ's constitution
  - promotion_gates.py       — GREEN/YELLOW/RED/BLACK tier logic
  - constitution_aggregator.py — aggregate live attestations into FederationConstitution
  - routes.py                — FastAPI REST routes for the aggregate
  - kernel_mode.py           — wires the aggregate into arif_kernel_route

Design invariants (F1-F13):
  - 13 canonical tools stay at 13 (no new surface)
  - This package adds a *new mode* on arif_kernel_route (mode="federation_status")
    and a *new REST route family* (constitutional observability)
  - All F1-reversible: no file deletions, no schema changes to existing tools
  - F2-honest: missing constitution file → tier=YELLOW, never GREEN-by-default
  - F13: promotion/demotion of arifOS itself still requires sovereign ack

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

__version__ = "2026.06.13-federation-v1"
__all__ = [
    "Tier",
    "OrganConstitution",
    "ConstitutionalFloor",
    "OrganAuthority",
    "OrganBoundaries",
    "FederationConstitution",
    "PromotionGate",
    "compute_tier",
    "aggregate",
    "get_federation_constitution",
    "as_dict",
]
