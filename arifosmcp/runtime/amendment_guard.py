"""
Constitutional Amendment Cooling Period — Vector #11.
═══════════════════════════════════════════════════════

FORGED 2026-07-19 — Fable5 audit vector #11.

"Truth must cool before it rules" — applied to the constitution itself.

The ratchet: proposals to amend F1-F13, always framed as improvement.
Each individually reasonable. Without a cooling period, the constitution
drifts one amendment at a time.

This guard:
  - Records every proposed amendment to F1-F13
  - Enforces a MINIMUM 7-day cooling period before ratification
  - Tracks the sovereign's review state
  - Prevents amendment stacking (multiple changes without cooling between them)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

AMENDMENT_COOLING_DAYS = 7
FLOOR_NAMES = {
    "F1": "AMANAH",
    "F2": "TRUTH",
    "F3": "WITNESS",
    "F4": "CLARITY",
    "F5": "PEACE",
    "F6": "MARUAH",
    "F7": "HUMILITY",
    "F8": "GENIUS",
    "F9": "ANTI-HANTU",
    "F10": "ONTOLOGY",
    "F11": "AUDIT",
    "F12": "INJECTION",
    "F13": "SOVEREIGN",
}

StatusT = Literal["PROPOSED", "COOLING", "COOLING_COMPLETE", "RATIFIED", "REJECTED", "SUPERSEDED"]

_VAULT = Path(os.environ.get("ARIFOS_HOME", "/root")) / "VAULT999"


@dataclass
class AmendmentProposal:
    proposal_id: str
    floor: str  # e.g. "F7"
    proposed_by: str
    proposed_at: str  # ISO timestamp
    current_text: str
    proposed_text: str
    rationale: str
    status: StatusT = "PROPOSED"
    cooling_until: str | None = None
    sovereign_verdict: str | None = None
    ratified_at: str | None = None


class AmendmentGuard:
    """Constitutional amendment tracker with mandatory cooling period."""

    def __init__(self) -> None:
        self._ledger_path = _VAULT / "amendments.jsonl"

    def propose(
        self,
        floor: str,
        proposed_by: str,
        current_text: str,
        proposed_text: str,
        rationale: str,
    ) -> tuple[bool, str, AmendmentProposal | None]:
        """Submit a constitutional amendment proposal.

        Returns (allowed, reason, proposal).
        If there's an active cooling period for the same floor, rejects.
        """
        # Check for active proposals on the same floor
        existing = self._active_for_floor(floor)
        if existing:
            return (
                False,
                (
                    f"Floor {floor} ({FLOOR_NAMES.get(floor, '?')}) has an active "
                    f"amendment (proposal {existing.proposal_id}, status {existing.status}). "
                    f"Wait for it to resolve before proposing a new change."
                ),
                None,
            )

        # Check for any recently ratified amendment (stacking prevention)
        recent = self._recently_ratified(days=AMENDMENT_COOLING_DAYS)
        if recent:
            return (
                False,
                (
                    f"Amendment {recent.proposal_id} was ratified within the "
                    f"{AMENDMENT_COOLING_DAYS}-day cooling window. "
                    f"Constitution must cool before further amendment."
                ),
                None,
            )

        now = datetime.now(UTC)
        proposal = AmendmentProposal(
            proposal_id=f"amd-{floor}-{now.strftime('%Y%m%d-%H%M%S')}",
            floor=floor,
            proposed_by=proposed_by,
            proposed_at=now.isoformat(),
            current_text=current_text,
            proposed_text=proposed_text,
            rationale=rationale,
            status="COOLING",
            cooling_until=(now + timedelta(days=AMENDMENT_COOLING_DAYS)).isoformat(),
        )

        self._write(proposal)
        return (
            True,
            (
                f"Amendment {proposal.proposal_id} registered for {floor} "
                f"({FLOOR_NAMES.get(floor, '?')}). Cooling until "
                f"{proposal.cooling_until}. F13 sovereign ratification required "
                f"after cooling completes."
            ),
            proposal,
        )

    def check_ratification(self, proposal_id: str) -> tuple[bool, str]:
        """Check if an amendment has completed its cooling period and can be ratified.

        Returns (can_ratify, reason).
        """
        proposal = self._find(proposal_id)
        if proposal is None:
            return False, f"Proposal {proposal_id} not found"

        if proposal.status == "RATIFIED":
            return False, "Already ratified"
        if proposal.status == "REJECTED":
            return False, "Already rejected"

        if proposal.cooling_until:
            cooling_end = datetime.fromisoformat(proposal.cooling_until)
            if datetime.now(UTC) < cooling_end:
                remaining = cooling_end - datetime.now(UTC)
                return False, (
                    f"Cooling period incomplete. "
                    f"{remaining.days}d {remaining.seconds // 3600}h remaining."
                )

        return True, "Cooling complete. Ready for F13 sovereign ratification."

    def ratify(self, proposal_id: str, sovereign: str) -> tuple[bool, str]:
        """Ratify an amendment after cooling period."""
        can, reason = self.check_ratification(proposal_id)
        if not can:
            return False, reason

        proposal = self._find(proposal_id)
        proposal.status = "RATIFIED"
        proposal.sovereign_verdict = f"RATIFIED by {sovereign}"
        proposal.ratified_at = datetime.now(UTC).isoformat()
        self._write(proposal, update=True)
        return True, f"Amendment {proposal_id} ratified by {sovereign}"

    def reject(self, proposal_id: str, sovereign: str, reason: str = "") -> tuple[bool, str]:
        """Reject an amendment."""
        proposal = self._find(proposal_id)
        if proposal is None:
            return False, f"Proposal {proposal_id} not found"

        proposal.status = "REJECTED"
        proposal.sovereign_verdict = f"REJECTED by {sovereign}: {reason}"
        self._write(proposal, update=True)
        return True, f"Amendment {proposal_id} rejected"

    def status(self) -> dict[str, Any]:
        """Return current amendment status."""
        proposals = self._all()
        active = [p for p in proposals if p.status in ("PROPOSED", "COOLING", "COOLING_COMPLETE")]
        ratified = [p for p in proposals if p.status == "RATIFIED"]
        return {
            "active_proposals": len(active),
            "ratified_amendments": len(ratified),
            "cooling_days_required": AMENDMENT_COOLING_DAYS,
            "active": [
                {
                    "id": p.proposal_id,
                    "floor": p.floor,
                    "status": p.status,
                    "cooling_until": p.cooling_until,
                }
                for p in active
            ],
            "doctrine": "Truth must cool before it rules.",
        }

    def _active_for_floor(self, floor: str) -> AmendmentProposal | None:
        for p in self._all():
            if p.floor == floor and p.status in ("PROPOSED", "COOLING", "COOLING_COMPLETE"):
                return p
        return None

    def _recently_ratified(self, days: int) -> AmendmentProposal | None:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        for p in self._all():
            if p.status == "RATIFIED" and p.ratified_at:
                ratified_dt = datetime.fromisoformat(p.ratified_at)
                if ratified_dt > cutoff:
                    return p
        return None

    def _find(self, proposal_id: str) -> AmendmentProposal | None:
        for p in self._all():
            if p.proposal_id == proposal_id:
                return p
        return None

    def _all(self) -> list[AmendmentProposal]:
        if not self._ledger_path.exists():
            return []
        proposals: list[AmendmentProposal] = []
        with open(self._ledger_path) as f:
            for line in f:
                try:
                    d = json.loads(line)
                    proposals.append(
                        AmendmentProposal(
                            proposal_id=d["proposal_id"],
                            floor=d["floor"],
                            proposed_by=d["proposed_by"],
                            proposed_at=d["proposed_at"],
                            current_text=d["current_text"],
                            proposed_text=d["proposed_text"],
                            rationale=d["rationale"],
                            status=d.get("status", "PROPOSED"),
                            cooling_until=d.get("cooling_until"),
                            sovereign_verdict=d.get("sovereign_verdict"),
                            ratified_at=d.get("ratified_at"),
                        )
                    )
                except (json.JSONDecodeError, KeyError):
                    continue
        return proposals

    def _write(self, proposal: AmendmentProposal, update: bool = False) -> None:
        self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
        if update:
            # Rewrite ledger with updated proposal
            all_proposals = self._all()
            with open(self._ledger_path, "w") as f:
                for p in all_proposals:
                    if p.proposal_id == proposal.proposal_id:
                        f.write(json.dumps(proposal.__dict__, default=str) + "\n")
                    else:
                        f.write(json.dumps(p.__dict__, default=str) + "\n")
        else:
            with open(self._ledger_path, "a") as f:
                f.write(json.dumps(proposal.__dict__, default=str) + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# Integration hook
# ═══════════════════════════════════════════════════════════════════════════

_guard: AmendmentGuard | None = None


def get_amendment_guard() -> AmendmentGuard:
    global _guard
    if _guard is None:
        _guard = AmendmentGuard()
    return _guard


__all__ = [
    "AmendmentProposal",
    "AmendmentGuard",
    "get_amendment_guard",
    "AMENDMENT_COOLING_DAYS",
    "FLOOR_NAMES",
]
