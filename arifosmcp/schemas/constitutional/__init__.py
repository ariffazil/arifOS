"""
RASA DERITA constitutional schema package — Phase 1 (load + validate only).

This package lands the machine-readable constitutional contract.
It does NOT enforce runtime gates. Enforcement is Phase 2+.

  PHASE1: land artifact, validate structure, hash for receipts
  PHASE2: wire arif_judge / forge / WELL against this module
  PHASE3+: evals executed, deploy probe, VAULT INSTALLED_ENFORCED

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

SCHEMA_FILENAME = "rasa-derita-schema.json"
MODULE_ID = "RASA_DERITA"
CANONICAL_REL_PATH = "arifosmcp/schemas/constitutional/rasa-derita-schema.json"

REQUIRED_TOP_KEYS = (
    "module",
    "version",
    "status",
    "ontology_boundary",
    "axes",
    "causal_cascade",
    "consent_lease",
    "escalation_lattice",
    "recovery_protocol",
    "forbidden_behaviors",
    "well_boundary",
    "rasa_derita_evals",
    "public_surface_integrity",
)

ESCALATION_ORDER = (
    "OBSERVE",
    "DOCUMENT",
    "CLARIFY",
    "RECOMMEND",
    "ESCALATE",
    "EMERGENCY_ROUTE",
    "HOLD",
)


@dataclass(frozen=True)
class SchemaLoadResult:
    """Phase-1 load receipt — not an enforcement verdict."""

    module_id: str
    schema_version: str
    schema_hash: str
    loaded_at_path: str
    validation_status: str  # VALID | INVALID
    enforcement_mode: str  # always NONE in Phase 1
    violations: tuple[str, ...]
    payload: dict[str, Any]


def schema_path() -> Path:
    return Path(__file__).resolve().parent / SCHEMA_FILENAME


def schema_sha256(raw: bytes | None = None) -> str:
    data = raw if raw is not None else schema_path().read_bytes()
    return "sha256:" + hashlib.sha256(data).hexdigest()


def validate_rasa_derita_payload(data: dict[str, Any]) -> list[str]:
    """Structural validation of the constitutional contract. No runtime enforcement."""
    violations: list[str] = []

    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            violations.append(f"missing top-level key: {key}")

    if data.get("module") != MODULE_ID:
        violations.append(f"module must be {MODULE_ID}, got {data.get('module')!r}")

    # Axes + unique lesson / invariant IDs
    axes = data.get("axes")
    if not isinstance(axes, list) or len(axes) < 5:
        violations.append("axes must be a list of at least 5 entries")
    else:
        axis_ids: set[str] = set()
        lesson_ids: set[str] = set()
        inv_ids: set[str] = set()
        for axis in axes:
            if not isinstance(axis, dict):
                violations.append("axis entry must be object")
                continue
            aid = axis.get("id")
            if not aid:
                violations.append("axis missing id")
            elif aid in axis_ids:
                violations.append(f"duplicate axis id: {aid}")
            else:
                axis_ids.add(str(aid))
            invs = axis.get("invariants") or {}
            if isinstance(invs, dict):
                for iid in invs:
                    if iid in inv_ids:
                        violations.append(f"duplicate invariant id: {iid}")
                    inv_ids.add(str(iid))
            for lesson in axis.get("lessons") or []:
                if not isinstance(lesson, dict):
                    continue
                lid = lesson.get("id")
                if not lid:
                    violations.append("lesson missing id")
                elif lid in lesson_ids:
                    violations.append(f"duplicate lesson id: {lid}")
                else:
                    lesson_ids.add(str(lid))

    # Causal cascade: min 3 steps in contract
    cascade = data.get("causal_cascade") or {}
    if isinstance(cascade, dict):
        steps = (cascade.get("schema") or {}).get("steps") or {}
        min_items = steps.get("minItems") if isinstance(steps, dict) else None
        if min_items is None or int(min_items) < 3:
            violations.append("causal_cascade.schema.steps.minItems must be >= 3")
    else:
        violations.append("causal_cascade must be object")

    # Consent lease: expiry + revocation
    lease = data.get("consent_lease") or {}
    if isinstance(lease, dict):
        schema = lease.get("schema") or {}
        for req in ("expires_at", "revocable", "revocation_propagation", "purpose", "scope"):
            if req not in schema:
                violations.append(f"consent_lease.schema missing {req}")
    else:
        violations.append("consent_lease must be object")

    # Escalation lattice monotonic names
    lattice = data.get("escalation_lattice") or {}
    levels = lattice.get("levels") if isinstance(lattice, dict) else None
    if not isinstance(levels, list) or not levels:
        violations.append("escalation_lattice.levels must be non-empty list")
    else:
        names = [str(lv.get("name", "")).upper() for lv in levels if isinstance(lv, dict)]
        expected = list(ESCALATION_ORDER)
        # Allow prefix match of expected order among present names
        filtered = [n for n in names if n in expected]
        if filtered != [n for n in expected if n in filtered]:
            violations.append(
                f"escalation levels not monotonic relative to {ESCALATION_ORDER}; got {names}"
            )
        level_nums = [
            lv.get("level") for lv in levels if isinstance(lv, dict) and "level" in lv
        ]
        if level_nums != sorted(level_nums):
            violations.append(f"escalation level numbers not monotonic: {level_nums}")

    # Evals: every case has id + expected verdict
    evals = (data.get("rasa_derita_evals") or {}).get("test_cases") or []
    if not isinstance(evals, list) or len(evals) < 15:
        violations.append("rasa_derita_evals.test_cases must have at least 15 entries")
    else:
        eval_ids: set[str] = set()
        for case in evals:
            if not isinstance(case, dict):
                violations.append("eval case must be object")
                continue
            eid = case.get("id")
            if not eid:
                violations.append("eval case missing id")
            elif eid in eval_ids:
                violations.append(f"duplicate eval id: {eid}")
            else:
                eval_ids.add(str(eid))
            if not case.get("expected"):
                violations.append(f"eval {eid} missing expected verdict")
            if not case.get("scenario"):
                violations.append(f"eval {eid} missing scenario")

    # WELL boundary presence
    well = data.get("well_boundary") or {}
    if not isinstance(well, dict) or "forbidden" not in well or "allowed" not in well:
        violations.append("well_boundary must include allowed and forbidden")

    # Status must not claim SEAL/RATIFIED while incomplete
    status = str(data.get("status", ""))
    if status in ("RATIFIED", "SEALED", "INSTALLED_ENFORCED"):
        kcw = data.get("kernel_complete_when") or {}
        if isinstance(kcw, dict) and not all(
            kcw.get(k) for k in (
                "schema_loaded_by_runtime",
                "causal_cascade_mandatory_at_judge",
                "consent_lease_enforced",
            )
        ):
            violations.append(
                f"status={status} forbidden while kernel_complete_when incomplete"
            )

    return violations


@lru_cache(maxsize=1)
def load_rasa_derita_schema() -> SchemaLoadResult:
    """Load + structurally validate the landed schema. Enforcement mode is NONE."""
    path = schema_path()
    raw = path.read_bytes()
    digest = schema_sha256(raw)
    data = json.loads(raw.decode("utf-8"))
    violations = validate_rasa_derita_payload(data)
    return SchemaLoadResult(
        module_id=str(data.get("module", MODULE_ID)),
        schema_version=str(data.get("version", "unknown")),
        schema_hash=digest,
        loaded_at_path=str(path),
        validation_status="VALID" if not violations else "INVALID",
        enforcement_mode="NONE",
        violations=tuple(violations),
        payload=data,
    )


def clear_schema_cache() -> None:
    load_rasa_derita_schema.cache_clear()
