"""arifosmcp/runtime/contradiction_margin.py — the Eureka margin, as a control.

(1) contradiction_margin(): one producer for n_act / n_resolved / phi_e and
    the register hash. The denominator comes ONLY from the contradiction
    register — never from a per-call parameter (Test E), so no caller can
    inflate phi_e by shrinking n_act.
(2) eureka_margin_gate(): NON_OPERATIONAL work without a declared margin is
    BLOCKED (execution_permitted=False, reason=EUREKA_MARGIN_UNDECLARED).
    The old state — "no paradoxes -> phiE waived (1.0)" — is gone: a waiver is
    an explicit classification (OPERATIONAL -> NOT_APPLICABLE), never a fallback
    for a missing field.

Wire name: contradiction_resolution_ratio. `phi_e` is the doctrine alias.

NAMED CONSUMER: /health `eureka_margin` block + arif_init session gate
(NON_OPERATIONAL sessions) — surfaces must agree (judge Test D, 2026-10-18).
NAMED FAILURE CLASSES: DENOMINATOR_SELF_EDIT (per-call n_act inflation),
MEASUREMENT_LAUNDERING (claims counted as measurements), WAIVER_AS_SUCCESS
(waived 1.0 presented as perfect closure).

Register home: $ARIFOS_CONTRADICTION_REGISTER or /var/lib/arifos/contradiction_register.json
Register header must name consumer + failure_classes (Law 2, 2026-10-18).

Floors engaged: F2 F4 F7 · DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REGISTER_PATH = Path(
    os.environ.get("ARIFOS_CONTRADICTION_REGISTER", "/var/lib/arifos/contradiction_register.json")
)

REQUIRED_ENTRY_FIELDS = (
    "id",
    "title",
    "scope",
    "evidence_pointer",
    "acceptance_test",
    "owner",
    "status",
    "falsifier",
)

PHI_UNDECLARED = "UNDECLARED"
PHI_NOT_APPLICABLE = "NOT_APPLICABLE"
PHI_MEASURED = "MEASURED"

REASON_UNDECLARED = "EUREKA_MARGIN_UNDECLARED"


def load_contradiction_register(register_path: Path | str | None = None) -> dict[str, Any] | None:
    """Read the register. Absent or unreadable -> None (an UNDECLARED margin)."""
    p = Path(register_path) if register_path else REGISTER_PATH
    try:
        raw = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def contradiction_margin(
    *,
    register_path: Path | str | None = None,
    register: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive the Eureka margin from the register. No caller-supplied n_act."""
    reg: Mapping[str, Any] | None = (
        dict(register) if register is not None else load_contradiction_register(register_path)
    )
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    if reg is None:
        return {
            "n_act": None,
            "n_resolved": None,
            "phi_e": {"value": None, "status": PHI_UNDECLARED},
            "contradiction_resolution_ratio": None,
            "contradiction_register_hash": None,
            "measured_at": now,
            "rejected_resolutions": [],
            "register_validation": {"present": False, "invalid_entries": []},
        }

    entries = list(reg.get("entries") or [])
    invalid: list[str] = []
    rejected: list[str] = []
    active = 0
    resolved = 0

    for e in entries:
        if not isinstance(e, dict):
            invalid.append(str(e)[:40])
            continue
        missing = [f for f in REQUIRED_ENTRY_FIELDS if not e.get(f)]
        if missing:
            invalid.append(f"{e.get('id', '?')}:missing={missing}")
        status = str(e.get("status") or "")
        has_acceptance = bool(e.get("resolution_evidence"))
        if status == "resolved":
            if has_acceptance:
                resolved += 1
            else:
                # Test F: a status change to resolved without acceptance
                # evidence is rejected — the contradiction stays active.
                rejected.append(str(e.get("id", "?")))
                active += 1
        elif status == "active":
            active += 1
        else:
            invalid.append(f"{e.get('id', '?')}:status={status or 'EMPTY'}")
            active += 1  # conservative: an unknown state is open backlog

    n_act: int | None = active if entries else 0
    if reg.get("n_act") is None and not entries:
        n_act = None

    if n_act is None:
        phi = {"value": None, "status": PHI_UNDECLARED}
    elif n_act == 0:
        phi = {"value": None, "status": PHI_NOT_APPLICABLE}
    else:
        phi = {"value": resolved / n_act, "status": PHI_MEASURED}

    canon = json.dumps(reg, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canon.encode()).hexdigest()

    return {
        "n_act": n_act,
        "n_resolved": resolved,
        "phi_e": phi,
        "contradiction_resolution_ratio": phi["value"],
        "contradiction_register_hash": digest,
        "measured_at": now,
        "rejected_resolutions": rejected,
        "register_validation": {"present": True, "invalid_entries": invalid},
    }


def eureka_margin_gate(work_class: str, margin: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """The control that bites: NON_OPERATIONAL work without a margin cannot run."""
    m = dict(margin) if margin is not None else contradiction_margin()
    phi = dict(m.get("phi_e") or {})
    if str(work_class) == "OPERATIONAL":
        return {
            "work_class": "OPERATIONAL",
            "execution_permitted": True,
            "reason": None,
            "phi_e": {"value": None, "status": PHI_NOT_APPLICABLE},
        }
    if m.get("n_act") is None:
        return {
            "work_class": str(work_class),
            "execution_permitted": False,
            "reason": REASON_UNDECLARED,
            "phi_e": {"value": None, "status": PHI_UNDECLARED},
        }
    return {
        "work_class": str(work_class),
        "execution_permitted": True,
        "reason": None,
        "phi_e": phi,
    }
