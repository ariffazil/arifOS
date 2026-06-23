"""
Capability Grant Registry — Agents Hold Grants, Not Secrets
═══════════════════════════════════════════════════════════════════════════════

Agents never see raw API keys, passwords, or tokens.
They request capabilities. The gateway resolves secrets.
The registry tracks who can do what, under what constraints.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.schemas.jurisdiction import AutonomyBand, CapabilityGrant

logger = logging.getLogger(__name__)


class CapabilityGrantRegistry:
    """
    In-memory registry of capability grants per actor.

    Production: backed by L4 (Supabase) + L6 (VAULT999 for issuance receipts).
    This runtime layer is the hot path.
    """

    def __init__(self) -> None:
        self._grants: dict[str, list[CapabilityGrant]] = {}
        self.lookup_count = 0
        self.denial_count = 0

    # ──────────────────────────────────────────────────────────────────────────
    # Grant lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    def issue(self, grant: CapabilityGrant) -> None:
        """Issue a new capability grant to an actor."""
        self._grants.setdefault(grant.actor_id, []).append(grant)
        logger.info(
            f"Grant issued: {grant.grant_id} → actor={grant.actor_id} "
            f"tool={grant.tool_name} band={grant.band.value}"
        )

    def revoke(self, grant_id: str, reason: str) -> bool:
        """Revoke a grant by ID. Returns True if found."""
        for _actor_id, grants in self._grants.items():
            for g in grants:
                if g.grant_id == grant_id:
                    g.revoked = True
                    g.revocation_reason = reason
                    logger.warning(f"Grant revoked: {grant_id} — {reason}")
                    return True
        logger.warning(f"Grant revoke failed: {grant_id} not found")
        return False

    # ──────────────────────────────────────────────────────────────────────────
    # Authorization checks
    # ──────────────────────────────────────────────────────────────────────────

    def authorize(
        self,
        actor_id: str,
        tool_name: str,
        required_band: AutonomyBand,
    ) -> tuple[bool, CapabilityGrant | None, str]:
        """
        Check if actor is authorized for tool at required band.

        Returns:
            (authorized: bool, grant: CapabilityGrant | None, reason: str)
        """
        self.lookup_count += 1
        grants = self._grants.get(actor_id, [])

        # Find matching active grants
        matches = [
            g for g in grants if g.tool_name == tool_name and g.is_active() and not g.revoked
        ]

        if not matches:
            self.denial_count += 1
            return False, None, f"No active grant for actor={actor_id} tool={tool_name}"

        # Take the highest-band grant (most permissive)
        best = max(matches, key=lambda g: _band_rank(g.band))

        if _band_rank(best.band) < _band_rank(required_band):
            self.denial_count += 1
            return (
                False,
                best,
                f"Grant band {best.band.value} < required {required_band.value}",
            )

        return True, best, f"Authorized via grant {best.grant_id}"

    def list_actor_grants(self, actor_id: str) -> list[CapabilityGrant]:
        """Return all grants for an actor."""
        return list(self._grants.get(actor_id, []))

    def dump_stats(self) -> dict[str, Any]:
        """Registry telemetry."""
        total = sum(len(g) for g in self._grants.values())
        active = sum(1 for grants in self._grants.values() for g in grants if g.is_active())
        return {
            "total_grants": total,
            "active_grants": active,
            "revoked_grants": total - active,
            "lookup_count": self.lookup_count,
            "denial_count": self.denial_count,
        }


def _band_rank(band: AutonomyBand) -> int:
    return {
        AutonomyBand.GREEN: 0,
        AutonomyBand.YELLOW: 1,
        AutonomyBand.ORANGE: 2,
        AutonomyBand.RED: 3,
        AutonomyBand.BLACK: 4,
    }[band]
