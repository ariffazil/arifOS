"""F6 P1 — correction effect (Meter 5 canonical producer).

Implements F6 v0 Tertib Kerja #3 (Meter 5 — Kesan Pembetulan):
  - Traces correction -> state change -> downstream action change.
  - Distinguishes:
      * ACCEPTED             (recorded, not yet applied to state)
      * DISPUTED_WITH_REASON (well-grounded factual dissent; never counted as
                              disrespect; reaches final decision gate)
      * APPLIED              (applied to decision/state; alias USED preserved)
      * EFFECT_VERIFIED      (verified before/after state + downstream action
                              evidence on disk; all targeted layers clean)
  - Text saying 'correction applied' is NEVER proof; only concrete before != after
    state and action evidence counts.
  - Append-only ledger (`/var/lib/arifos/f6_corrections.jsonl` by default, or
    injected path in tests); wrong records are challenged or superseded without
    deleting history.
  - No `human_id`: keyed by `decision_id` + `agent_version`, coarse second-precision
    UTC timestamps, text bounded at <=500 chars, evidence values <=200 chars.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

SCHEMA = "arifos.f6.correction_effect.v1"
DEFAULT_LEDGER = Path("/var/lib/arifos/f6_corrections.jsonl")


class CorrectionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"                          # recorded, nothing more
    DISPUTED_WITH_REASON = "DISPUTED_WITH_REASON"  # grounded factual dissent
    APPLIED = "APPLIED"                            # applied to state/decision
    USED = "APPLIED"                               # backward-compatible alias
    EFFECT_VERIFIED = "EFFECT_VERIFIED"            # before != after state+action verified
    CHALLENGED = "CHALLENGED"                      # record challenged without deletion


@dataclass
class CorrectionRecord:
    correction_id: str
    decision_id: str          # the governed decision being corrected
    agent_version: str        # NOT human identity
    claim: str                # what the system claimed (redacted by caller)
    correction: str           # what the human said (redacted by caller)
    status: str               # CorrectionStatus value
    created_at: str           # second-precision UTC
    reason: str = ""          # required for DISPUTED_WITH_REASON / CHALLENGED
    before_evidence: dict[str, Any] = field(default_factory=dict)
    after_evidence: dict[str, Any] = field(default_factory=dict)
    effect_ref: str = ""
    superseded_by: str = ""
    supersedes_id: str = ""
    dissent_not_disrespect: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utcnow_sec() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _truncate(d: dict[str, Any]) -> dict[str, str]:
    if not isinstance(d, dict):
        return {}
    return {str(k)[:64]: str(v)[:200] for k, v in list(d.items())[:10]}


def _append(rec: CorrectionRecord, ledger_path: Path) -> None:
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec.to_dict(), default=str) + "\n")
    try:
        os.chmod(ledger_path, 0o600)
    except OSError:
        pass


def load_corrections(ledger_path: Path = DEFAULT_LEDGER) -> list[dict[str, Any]]:
    p = Path(ledger_path)
    if not p.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def record_correction(
    decision_id: str,
    agent_version: str,
    claim: str,
    correction: str,
    disputed: bool = False,
    dispute_reason: str = "",
    ledger_path: Path = DEFAULT_LEDGER,
) -> CorrectionRecord:
    """Append a correction. DISPUTED_WITH_REASON requires a non-empty dispute_reason.

    Well-grounded factual dissent is legitimate and stays in records — it is
    never auto-counted as disrespect.
    """
    if disputed and not (dispute_reason or "").strip():
        raise ValueError("DISPUTED_WITH_REASON requires dispute_reason")
    rec = CorrectionRecord(
        correction_id=f"corr-{uuid.uuid4().hex[:12]}",
        decision_id=decision_id,
        agent_version=agent_version,
        claim=str(claim)[:500],
        correction=str(correction)[:500],
        status=(
            CorrectionStatus.DISPUTED_WITH_REASON.value
            if disputed
            else CorrectionStatus.ACCEPTED.value
        ),
        created_at=_utcnow_sec(),
        reason=str(dispute_reason)[:500],
        dissent_not_disrespect=True,
    )
    _append(rec, ledger_path)
    return rec


def apply_correction(
    correction_id: str,
    decision_id: str,
    agent_version: str,
    applied_state: dict[str, Any],
    ledger_path: Path = DEFAULT_LEDGER,
) -> CorrectionRecord:
    """Record that a correction has been APPLIED to state/decision (not yet effect-verified)."""
    rec = CorrectionRecord(
        correction_id=correction_id,
        decision_id=decision_id,
        agent_version=agent_version,
        claim="apply_correction",
        correction=json.dumps(_truncate(applied_state), default=str)[:500],
        status=CorrectionStatus.APPLIED.value,
        created_at=_utcnow_sec(),
        after_evidence=_truncate(applied_state),
    )
    _append(rec, ledger_path)
    return rec


def supersede(
    correction_id: str,
    reason_fix: str,
    ledger_path: Path = DEFAULT_LEDGER,
) -> CorrectionRecord:
    """Correct a wrong record WITHOUT deleting history (append superseding entry)."""
    new_id = f"corr-{uuid.uuid4().hex[:12]}"
    rec = CorrectionRecord(
        correction_id=new_id,
        decision_id="N/A",
        agent_version="f6-supersede",
        claim=correction_id,
        correction=str(reason_fix)[:500],
        status=CorrectionStatus.ACCEPTED.value,
        created_at=_utcnow_sec(),
        supersedes_id=correction_id,
    )
    _append(rec, ledger_path)
    return rec


def challenge_record(
    target_record_id: str,
    challenge_reason: str,
    agent_version: str = "f6-challenge",
    ledger_path: Path = DEFAULT_LEDGER,
) -> CorrectionRecord:
    """Challenge an existing record without deleting history."""
    if not (challenge_reason or "").strip():
        raise ValueError("challenge_record requires a non-empty challenge_reason")
    rec = CorrectionRecord(
        correction_id=f"chal-{uuid.uuid4().hex[:12]}",
        decision_id=target_record_id,
        agent_version=agent_version,
        claim=target_record_id,
        correction=str(challenge_reason)[:500],
        status=CorrectionStatus.CHALLENGED.value,
        created_at=_utcnow_sec(),
        reason=str(challenge_reason)[:500],
        supersedes_id=target_record_id,
    )
    _append(rec, ledger_path)
    return rec


def _is_cosmetic_text_only(ev: dict[str, Any]) -> bool:
    """Detect cosmetic text-only claims like {'text': 'correction applied'} with no state keys."""
    if not ev:
        return True
    cosmetic_keys = {"ack", "message", "text", "note", "status_text"}
    if set(ev.keys()).issubset(cosmetic_keys):
        vals = " ".join(str(v).lower() for v in ev.values())
        if "correction applied" in vals or "noted" in vals or "acknowledged" in vals:
            return True
    return False


def verify_effect(
    correction_id: str,
    before_evidence: dict[str, Any],
    after_evidence: dict[str, Any],
    effect_ref: str,
    apply_to_decision: Optional[Callable[[dict[str, Any]], Any]] = None,
    ledger_path: Path = DEFAULT_LEDGER,
) -> dict[str, Any]:
    """Upgrade a correction to EFFECT_VERIFIED only when BEFORE and AFTER differ
    and carry non-cosmetic state/action evidence.

    Text saying 'correction applied' is NEVER evidence. If before == after,
    the correction changed nothing and effect_verified remains False.
    """
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "correction_id": correction_id,
        "status": CorrectionStatus.ACCEPTED.value,
        "effect_verified": False,
        "reason": "",
    }
    if not before_evidence and not after_evidence:
        result["reason"] = "no before/after evidence provided — text alone never verifies"
        return result
    if _is_cosmetic_text_only(after_evidence):
        result["reason"] = "cosmetic 'correction applied' text is not state/action evidence"
        return result
    if before_evidence == after_evidence:
        result["reason"] = "before == after: correction produced NO downstream change"
        return result

    used = None
    if apply_to_decision is not None:
        used = apply_to_decision({"correction_id": correction_id, "after": after_evidence})

    final_status = (
        CorrectionStatus.EFFECT_VERIFIED.value
        if used is not False
        else CorrectionStatus.APPLIED.value
    )
    _append(
        CorrectionRecord(
            correction_id=correction_id,
            decision_id=correction_id,
            agent_version="f6-effect-verify",
            claim="effect verification",
            correction=json.dumps(_truncate(after_evidence), default=str)[:500],
            status=final_status,
            created_at=_utcnow_sec(),
            before_evidence=_truncate(before_evidence),
            after_evidence=_truncate(after_evidence),
            effect_ref=str(effect_ref)[:200],
        ),
        ledger_path,
    )
    result["status"] = final_status
    result["effect_verified"] = final_status == CorrectionStatus.EFFECT_VERIFIED.value
    result["reason"] = (
        "before != after and downstream evidence appended "
        f"({final_status})"
    )
    return result


def resolve_dissent_at_decision_gate(
    dissent_record: CorrectionRecord,
    before_decision_state: dict[str, Any],
    accepted: bool,
    updated_decision_state: Optional[dict[str, Any]] = None,
    resolution_reason: str = "",
    ledger_path: Path = DEFAULT_LEDGER,
) -> dict[str, Any]:
    """Route a grounded dissent (`DISPUTED_WITH_REASON`) to the final decision gate.

    Proves:
      1. Grounded dissent reaches the final decision gate and is never treated as disrespect.
      2. When accepted (`accepted=True`), it mutates the downstream decision/action and
         produces verified before/after evidence (`EFFECT_VERIFIED` if state+action changed).
      3. When not accepted (`accepted=False`), it requires a stated `resolution_reason`
         and remains preserved in the ledger as `DISPUTED_WITH_REASON`.
    """
    if dissent_record.status != CorrectionStatus.DISPUTED_WITH_REASON.value:
        raise ValueError("resolve_dissent_at_decision_gate requires a DISPUTED_WITH_REASON record")
    if not dissent_record.reason.strip():
        raise ValueError("dissent record lacks a grounded reason")

    if not accepted:
        if not resolution_reason.strip():
            raise ValueError("rejecting a grounded dissent requires an explicit resolution_reason")
        return {
            "schema": SCHEMA,
            "correction_id": dissent_record.correction_id,
            "reached_final_decision": True,
            "accepted": False,
            "counted_as_disrespect": False,
            "status": CorrectionStatus.DISPUTED_WITH_REASON.value,
            "effect_verified": False,
            "reason": resolution_reason[:500],
        }

    after_state = updated_decision_state or {}
    ver = verify_effect(
        dissent_record.correction_id,
        before_evidence=before_decision_state,
        after_evidence=after_state,
        effect_ref=f"decision_gate:{dissent_record.decision_id}",
        ledger_path=ledger_path,
    )
    return {
        "schema": SCHEMA,
        "correction_id": dissent_record.correction_id,
        "reached_final_decision": True,
        "accepted": True,
        "counted_as_disrespect": False,
        "status": ver["status"],
        "effect_verified": ver["effect_verified"],
        "before_state": _truncate(before_decision_state),
        "after_state": _truncate(after_state),
        "reason": ver["reason"],
    }


REQUIRED_PROPAGATION_LAYERS = (
    "L1_memory",
    "L2_queue",
    "L3_planner",
    "L4_tool_payload",
)


def propagate_correction_across_layers(
    decision_id: str,
    agent_version: str,
    stale_value: str,
    corrected_value: str,
    layers: dict[str, list[dict[str, Any]]],
    update_layers: bool = True,
    ledger_path: Path = DEFAULT_LEDGER,
) -> dict[str, Any]:
    """Propagate a human correction across the 4 downstream layers (`L1_memory`,
    `L2_queue`, `L3_planner`, `L4_tool_payload`) and verify whether any layer
    retained the revoked premise or was omitted.

    If `update_layers=False`, or any of the 4 required layers is missing or
    retains `stale_value`, `effect_verified` MUST be False and
    `layers_still_stale` names every unupdated/missing layer.
    """
    rec = record_correction(
        decision_id=decision_id,
        agent_version=agent_version,
        claim=stale_value,
        correction=corrected_value,
        ledger_path=ledger_path,
    )
    before_snapshot = {
        layer_name: json.dumps(rows, sort_keys=True)
        for layer_name, rows in layers.items()
    }
    if update_layers:
        for _layer_name, rows in layers.items():
            for row in rows:
                if row.get("content") == stale_value:
                    row["content"] = corrected_value
                    row["superseded_by"] = rec.correction_id
                if row.get("assumption") == stale_value:
                    row["assumption"] = corrected_value
                    row["superseded_by"] = rec.correction_id

    missing_layers = [
        req_layer for req_layer in REQUIRED_PROPAGATION_LAYERS if req_layer not in layers
    ]
    stale_layers = [
        layer_name
        for layer_name, rows in layers.items()
        if any(
            r.get("content") == stale_value or r.get("assumption") == stale_value
            for r in rows
        )
    ] + missing_layers
    after_snapshot = {
        layer_name: json.dumps(rows, sort_keys=True)
        for layer_name, rows in layers.items()
    }

    if stale_layers:
        apply_correction(
            rec.correction_id,
            decision_id=decision_id,
            agent_version=agent_version,
            applied_state={"stale_layers": stale_layers},
            ledger_path=ledger_path,
        )
        return {
            "schema": SCHEMA,
            "correction_id": rec.correction_id,
            "status": CorrectionStatus.APPLIED.value,
            "effect_verified": False,
            "layers_examined": list(layers.keys()),
            "layers_still_stale": stale_layers,
            "reason": f"correction incomplete — stale premise survives in {stale_layers}",
        }

    ver = verify_effect(
        rec.correction_id,
        before_evidence=before_snapshot,
        after_evidence=after_snapshot,
        effect_ref=f"four_layer_propagation:{decision_id}",
        ledger_path=ledger_path,
    )
    return {
        "schema": SCHEMA,
        "correction_id": rec.correction_id,
        "status": ver["status"],
        "effect_verified": ver["effect_verified"],
        "layers_examined": list(layers.keys()),
        "layers_still_stale": [],
        "reason": ver["reason"],
    }
