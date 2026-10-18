"""Single health function — one producer for floor truth and substrate state.

T1 (2026-10-18). Before this module, `/health` and the kernel verbs derived
the same two words from different predicates:

  * `/health` counted per-floor provenance and could report 13/13 pass.
  * `verdict.py` set ``_floors_actually_checked = bool(failed_floors)``, so a
    verb could only ever report ``floor_passed=None`` (unmeasured) unless
    something had already failed. A measured PASS was structurally impossible
    on that path.

Same field name, two scopes, no way for a consumer to tell which was which.
This module is the single place that turns floor statuses into a tri-state,
and drift facts into a substrate state. Consumers pass their own measurements
in; the rule that maps them to words lives here and nowhere else.

Doctrine: FLOOR_HONESTY / STAB-2026-08-07b. ``floor_passed`` is a sensor:
True = every floor measured and passing, False = at least one measured
failure, None = at least one floor has no instrument. Evidence hierarchy:
a measured pass outranks a narrative label; a measured failure outranks
everything.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

FLOOR_STATUS_PASS = "pass"
FLOOR_STATUS_FAIL = "fail"
FLOOR_STATUS_UNMEASURED = "unmeasured"

FLOOR_SCOPE_SYSTEM = "system"
FLOOR_SCOPE_TOOL_CALL = "tool_call"


@dataclass(frozen=True)
class FloorTruth:
    """Tri-state result of one floor measurement."""

    status: str  # healthy | partial | degraded
    floor_passed: bool | None
    measurement: str  # measured | unmeasured
    floors_pass: int
    floors_total: int
    floors_failing: tuple[str, ...] = ()
    floors_unmeasured: tuple[str, ...] = ()
    derivation: str = "health_truth.floor_truth:single_producer"

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "floor_passed": self.floor_passed,
            "_floor_measurement": self.measurement,
            "floors_pass": self.floors_pass,
            "floors_total": self.floors_total,
            "floors_failing": list(self.floors_failing),
            "floors_unmeasured": list(self.floors_unmeasured),
            "floor_scope": FLOOR_SCOPE_SYSTEM,
            "_derivation": self.derivation,
        }


def floor_truth(floor_detail: Mapping[str, Any] | None, floors_total: int = 13) -> FloorTruth:
    """Map per-floor statuses to one tri-state.

    ``floor_detail`` values are the status vocabulary only: pass | fail |
    unmeasured. Any other value is treated as unmeasured — an unknown status
    is an absent instrument, never a pass.
    """
    statuses = {str(k): str(v) for k, v in (floor_detail or {}).items()}
    total = int(floors_total) if floors_total else len(statuses)
    failing = tuple(sorted(k for k, v in statuses.items() if v == FLOOR_STATUS_FAIL))
    unmeasured = tuple(sorted(k for k, v in statuses.items() if v != FLOOR_STATUS_PASS and v != FLOOR_STATUS_FAIL))
    passed = sum(1 for v in statuses.values() if v == FLOOR_STATUS_PASS)

    if failing:
        # A measured failure dominates; unmeasured floors cannot soften it.
        return FloorTruth(
            status="degraded",
            floor_passed=False,
            measurement="measured",
            floors_pass=passed,
            floors_total=total,
            floors_failing=failing,
            floors_unmeasured=unmeasured,
        )
    if passed == 0:
        return FloorTruth(
            status="partial",
            floor_passed=None,
            measurement="unmeasured",
            floors_pass=0,
            floors_total=total,
            floors_unmeasured=unmeasured,
        )
    if not unmeasured and passed >= total:
        return FloorTruth(
            status="healthy",
            floor_passed=True,
            measurement="measured",
            floors_pass=passed,
            floors_total=total,
        )
    return FloorTruth(
        status="partial",
        floor_passed=None,
        measurement="measured",
        floors_pass=passed,
        floors_total=total,
        floors_unmeasured=unmeasured,
    )


def substrate_truth(
    *,
    runtime_drift: bool = False,
    source_drift: bool = False,
    contract_drift: bool = False,
    boot_unhealthy: bool = False,
) -> dict[str, Any]:
    """One predicate for substrate_state.

    ``runtime_drift``  — live running code differs from the deployed commit.
    ``source_drift``   — repo HEAD differs from the built commit (unbuilt work).
    ``contract_drift`` — tool contract schemas differ from the registry.
    ``boot_unhealthy`` — boot attestation is present and not ALIVE.

    Any of these degrades the substrate. They are named separately in
    ``degraded_causes`` so a consumer can tell an unbuilt tree from a running
    mismatch without re-deriving the judgement.
    """
    causes: list[str] = []
    if runtime_drift:
        causes.append("RUNTIME_DRIFT")
    if source_drift:
        causes.append("SOURCE_BUILD_DRIFT")
    if contract_drift:
        causes.append("CONTRACT_DRIFT")
    if boot_unhealthy:
        causes.append("BOOT_UNHEALTHY")
    return {
        "substrate_state": "DEGRADED" if causes else "HEALTHY",
        "degraded_causes": causes,
        "drift": bool(causes),
        "_derivation": "health_truth.substrate_truth:single_producer",
    }
