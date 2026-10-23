"""F6 §2 — interfaces for the three UNDECIDED policies. NOTHING IS ACTIVE.

Implements F6 v0 Tiga Keputusan Tertangguh:
  (A) Third-party dignity  — PENDING. Extension point only. NO moral
      classifier may block users. No third-party protection is claimed.
  (B) Collective witness   — DISABLED/HOLD. No active family/group veto,
      no auto-notification. Option NOT permanently deleted.
  (C) External Peer Witness — UNASSIGNED. Interface + synthetic fixtures
      only. No witness named or contacted. No witness => UNWITNESSED,
      never PASS.

Every function here either returns a declared-inactive status or raises
PolicyNotActive. There is no code path that enforces (A)-(C).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SCHEMA = "arifos.f6.pending_policies.v1"


class PolicyStatus:
    PENDING = "PENDING"
    HOLD = "HOLD"
    UNASSIGNED = "UNASSIGNED"


class PolicyNotActive(RuntimeError):
    """Raised if any caller tries to enforce an undecided policy."""


@dataclass
class PendingPolicy:
    policy_id: str
    status: str
    active: bool
    description: str
    extension_point: str  # where a future activation WOULD hook in
    activation_requires: str  # what F13 must decide first
    f13_recorded_leaning: str = ""  # spec C.8.5 (non-activating note)
    synthetic_fixtures: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "policy_id": self.policy_id,
            "status": self.status,
            "active": self.active,
            "description": self.description,
            "extension_point": self.extension_point,
            "activation_requires": self.activation_requires,
            "f13_recorded_leaning": self.f13_recorded_leaning,
            "synthetic_fixtures": self.synthetic_fixtures,
        }


def third_party_dignity() -> PendingPolicy:
    """(A) Affected-party assessment — extension point, NOT activated."""
    return PendingPolicy(
        policy_id="third_party_dignity",
        status=PolicyStatus.PENDING,
        active=False,
        description=(
            "Proposal to assess dignity impact on non-user third parties. "
            "NO moral classifier may block users; NO third-party protection "
            "is claimed while this is PENDING."
        ),
        extension_point="arifosmcp/runtime/f6/third_party_hook.py:assess_affected_party (NOT BUILT)",
        activation_requires=(
            "F13 decision: is third-party dignity inside or outside F6 scope? "
            "Attacker surface vs blindness tradeoff (spec §8a)."
        ),
        f13_recorded_leaning=(
            "Protect absent stakeholder by default (authority over self != authority over others); "
            "awaiting formal F13 ratification before any enforcement."
        ),
        synthetic_fixtures=[
            {"case": "shared room, third human present", "expected_if_active": "ASSESS"},
            {"case": "solo session", "expected_if_active": "NOT_APPLICABLE"},
        ],
    )


def collective_witness() -> PendingPolicy:
    """(B) Family/group witness — DISABLED/HOLD, option preserved."""
    return PendingPolicy(
        policy_id="collective_witness",
        status=PolicyStatus.HOLD,
        active=False,
        description=(
            "Proposal for collective (family/group) witness. NO active veto, "
            "NO auto-notification. Option is NOT permanently deleted."
        ),
        extension_point="arifosmcp/runtime/f6/collective_witness_hook.py (NOT BUILT)",
        activation_requires=(
            "F13 decision: HOLD or REJECT? Patriarchy/policing risk unresolved "
            "(spec §8b)."
        ),
        f13_recorded_leaning=(
            "Witness can inform; witness cannot own or hold veto over an individual. "
            "Execution remains DISABLED/HOLD."
        ),
        synthetic_fixtures=[
            {"case": "one member votes veto", "expected_if_active": "REJECTED_BY_DESIGN_RISK"},
        ],
    )


def external_peer_witness() -> PendingPolicy:
    """(C) External peer witness — UNASSIGNED; interface + fixtures only."""
    return PendingPolicy(
        policy_id="external_peer_witness",
        status=PolicyStatus.UNASSIGNED,
        active=False,
        description=(
            "External peer witness slot remains EMPTY. No person named, none "
            "contacted. No witness => UNWITNESSED, never PASS."
        ),
        extension_point="arifosmcp/runtime/f6/meters.py:_witness_status (reads human_witness.jsonl)",
        activation_requires=(
            "F13 decision: who and when for the peer witness slot (spec §8c). "
            "Filling the slot needs a person to consent; that is a human act."
        ),
        f13_recorded_leaning=(
            "Independence over intelligence: witness from a distinct reality model preferred "
            "over same-loop insider. Slot remains UNASSIGNED."
        ),
        synthetic_fixtures=[
            {"case": "no witness row", "expected": "UNWITNESSED"},
            {"case": "witness row older than 7d", "expected": "STALE"},
        ],
    )


def all_pending() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "note": "None of these are active. No real actions taken. No one contacted.",
        "policies": [
            third_party_dignity().to_dict(),
            collective_witness().to_dict(),
            external_peer_witness().to_dict(),
        ],
    }


def enforce(*_args: Any, **_kwargs: Any) -> None:
    """Any attempt to enforce an undecided policy fails closed."""
    raise PolicyNotActive(
        "no undecided F6 policy (third-party / collective / peer-witness) is active"
    )
