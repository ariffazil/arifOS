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

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

FLOOR_STATUS_PASS = "pass"
FLOOR_STATUS_FAIL = "fail"
FLOOR_STATUS_UNMEASURED = "unmeasured"

FLOOR_SCOPE_SYSTEM = "system"
FLOOR_SCOPE_TOOL_CALL = "tool_call"

# Measurement-class taxonomy (F13 judge order 2026-10-18, KX-003).
#   LIVE_PROBE -> measured · SIGNED_ATTESTATION -> attested
#   STATIC_CLAIM -> declared · MISSING -> unmeasured
# Rule: no class is ever promoted to `measured`. A claim (claims.json) is
# evidence OF a claim, never a measurement. Unknown instruments are not
# measurements either (K2: unknown != zero).
MEASUREMENT_MEASURED = "measured"
MEASUREMENT_ATTESTED = "attested"
MEASUREMENT_DECLARED = "declared"
MEASUREMENT_UNMEASURED = "unmeasured"


def classify_provenance(provenance: str | None) -> str:
    """Map one provenance string to its measurement class."""
    p = str(provenance or "").strip()
    if not p:
        return MEASUREMENT_UNMEASURED
    head = p.split(":", 1)[0]
    if "claims.json" in p or head in ("static_claim", "claims"):
        return MEASUREMENT_DECLARED
    if head.startswith("unmeasured"):
        return MEASUREMENT_UNMEASURED
    if head.startswith("attestation") or head.startswith("signed"):
        return MEASUREMENT_ATTESTED
    if any(t in head for t in ("probe", "producer", "live")):
        return MEASUREMENT_MEASURED
    return MEASUREMENT_UNMEASURED


def promotion_allowed(current: str, target: str) -> bool:
    """Only a measurement may be called measured (anti-laundering, KX-003)."""
    return not (target == MEASUREMENT_MEASURED and current != MEASUREMENT_MEASURED)


# One field, one vocabulary. A scoped verdict speaks PASS/FAIL; a substrate
# speaks HEALTHY/DEGRADED. utils.py historically copied the former into a
# field named substrate_state, so arif_init reported "PASS" while /health
# reported "HEALTHY" for the same machine (measured 2026-10-18).
_SUBSTRATE_ALIASES = {
    "HEALTHY": "HEALTHY",
    "PASS": "HEALTHY",
    "OK": "HEALTHY",
    "SEAL": "HEALTHY",
    "DEGRADED": "DEGRADED",
    "FAIL": "DEGRADED",
    "DENIED": "DEGRADED",
    "HOLD": "DEGRADED",
    "VOID": "DEGRADED",
    "SABAR": "DEGRADED",
}

_SYSTEM_TRUTH: dict[str, Any] = {}
_SYSTEM_TRUTH_LOCK = threading.Lock()
_SYSTEM_TRUTH_TTL_S = 120.0


def normalize_substrate_label(value: Any) -> str:
    """Map any substrate-ish token to HEALTHY | DEGRADED | UNMEASURED."""
    token = str(value or "").strip().upper()
    return _SUBSTRATE_ALIASES.get(token, "UNMEASURED")


def publish_system_floor_truth(
    truth: FloorTruth,
    *,
    measured_at: str | None = None,
    substrate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Record the system reading so tool envelopes can echo it.

    Called by /health, which is the one surface that measures all 13 floors.
    ``substrate`` is the ``substrate_truth()`` result from the same /health
    pass. Verbs echo it rather than recomputing drift from a second predicate
    (``build.get_runtime_attestation().drift`` answers a different question
    than /health's build-stamp comparison, and the two disagree — measured
    2026-10-18 on staging: injector said HEALTHY, /health said RUNTIME_DRIFT).
    """
    record = {
        "floor_passed": truth.floor_passed,
        "measurement": truth.measurement,
        "status": truth.status,
        "floors_pass": truth.floors_pass,
        "floors_total": truth.floors_total,
        "floors_failing": list(truth.floors_failing),
        "floors_unmeasured": list(truth.floors_unmeasured),
        "measured_at": measured_at
        or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "_monotonic": time.monotonic(),
    }
    if substrate:
        record["substrate_state"] = normalize_substrate_label(
            substrate.get("substrate_state")
        )
        record["substrate_degraded_causes"] = list(
            substrate.get("degraded_causes") or []
        )
    with _SYSTEM_TRUTH_LOCK:
        _SYSTEM_TRUTH.clear()
        _SYSTEM_TRUTH.update(record)
    return record


def read_system_floor_truth(max_age_s: float = _SYSTEM_TRUTH_TTL_S) -> dict[str, Any] | None:
    """Return the last published system reading, or None if absent/stale."""
    with _SYSTEM_TRUTH_LOCK:
        if not _SYSTEM_TRUTH:
            return None
        record = dict(_SYSTEM_TRUTH)
    age = time.monotonic() - float(record.get("_monotonic", 0.0))
    record["stale"] = age > max_age_s
    record["age_s"] = round(age, 1)
    return record


def clear_system_floor_truth() -> None:
    """Drop the published reading.

    Tests and long-lived processes must be able to say "no reading has been
    published in this process" explicitly — a leaked reading from an earlier
    call would silently become the machine's state for every later consumer.
    """
    with _SYSTEM_TRUTH_LOCK:
        _SYSTEM_TRUTH.clear()


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
    floors_declared: tuple[str, ...] = ()
    measurement_status: dict[str, str] = field(default_factory=dict)
    aggregate: str = ""
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
            "floors_declared": list(self.floors_declared),
            "floors_measurement_status": dict(self.measurement_status),
            "floors_aggregate": self.aggregate,
            "floor_scope": FLOOR_SCOPE_SYSTEM,
            "_derivation": self.derivation,
        }


def floor_truth(
    floor_detail: Mapping[str, Any] | None,
    floors_total: int = 13,
    provenance: Mapping[str, str] | None = None,
) -> FloorTruth:
    """Map per-floor statuses to one tri-state.

    ``floor_detail`` values are the status vocabulary only: pass | fail |
    unmeasured. Any other value is treated as unmeasured — an unknown status
    is an absent instrument, never a pass.

    ``provenance`` (optional) carries the per-floor source string. When the
    caller tracks it, the measurement CLASS of each floor comes from its
    provenance and overrides a claimed status: a STATIC_CLAIM pass becomes
    ``declared`` and never counts as a measurement (KX-003 anti-laundering).
    A claimed FAIL is never softened either way — fail-closed.
    """
    statuses = {str(k): str(v) for k, v in (floor_detail or {}).items()}
    prov = {str(k): str(v) for k, v in (provenance or {}).items()}
    total = int(floors_total) if floors_total else len(statuses)

    mstatus: dict[str, str] = {}
    for fid, st in statuses.items():
        if fid in prov:
            mstatus[fid] = classify_provenance(prov[fid])
        elif st in (FLOOR_STATUS_PASS, FLOOR_STATUS_FAIL):
            # No provenance tracked for this floor; a known pass/fail implies
            # some instrument took a reading.
            mstatus[fid] = MEASUREMENT_MEASURED
        else:
            mstatus[fid] = MEASUREMENT_UNMEASURED

    def _bucket(fid: str) -> str:
        st, cls = statuses[fid], mstatus[fid]
        if st == FLOOR_STATUS_FAIL:
            return "fail"
        if cls == MEASUREMENT_DECLARED:
            return "declared"
        if st == FLOOR_STATUS_PASS and cls in (MEASUREMENT_MEASURED, MEASUREMENT_ATTESTED):
            return "pass"
        return "unmeasured"

    buckets = {fid: _bucket(fid) for fid in statuses}
    failing = tuple(sorted(f for f, b in buckets.items() if b == "fail"))
    declared = tuple(sorted(f for f, b in buckets.items() if b == "declared"))
    unmeasured = tuple(sorted(f for f, b in buckets.items() if b == "unmeasured"))
    passed = sum(1 for b in buckets.values() if b == "pass")
    measured_n = sum(1 for c in mstatus.values() if c == MEASUREMENT_MEASURED)
    attested_n = sum(1 for c in mstatus.values() if c == MEASUREMENT_ATTESTED)
    aggregate = (
        f"{measured_n} measured · {attested_n} attested · "
        f"{len(declared)} declared · {len(unmeasured)} unmeasured / {total}"
    )

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
            floors_declared=declared,
            measurement_status=mstatus,
            aggregate=aggregate,
        )
    if passed == 0:
        return FloorTruth(
            status="partial",
            floor_passed=None,
            measurement="unmeasured",
            floors_pass=0,
            floors_total=total,
            floors_unmeasured=unmeasured,
            floors_declared=declared,
            measurement_status=mstatus,
            aggregate=aggregate,
        )
    if not unmeasured and not declared and passed >= total:
        return FloorTruth(
            status="healthy",
            floor_passed=True,
            measurement="measured",
            floors_pass=passed,
            floors_total=total,
            measurement_status=mstatus,
            aggregate=aggregate,
        )
    return FloorTruth(
        status="partial",
        floor_passed=None,
        measurement="measured",
        floors_pass=passed,
        floors_total=total,
        floors_unmeasured=unmeasured,
        floors_declared=declared,
        measurement_status=mstatus,
        aggregate=aggregate,
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
