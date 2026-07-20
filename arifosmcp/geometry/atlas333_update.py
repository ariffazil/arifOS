"""
arifosmcp/geometry/atlas333_update.py — ATLAS333 Governed Updater
═══════════════════════════════════════════════════════════════════

The governed updater that reads eureka entries, classifies deltas against
TEARFRAME + Amanah, applies accepted deltas to CUBE777 state, and emits receipts.

This is the "atlas333_update" in the closed loop:
  Θ_t → E_s → atlas333_update → Θ_{t+1}

Classification rules:
  ACCEPTABLE_DELTA: EUREKA + all witnesses + TEARFRAME passes + Amanah >= min
  REQUIRES_WITNESS: TEARFRAME soft-fail, or missing witnesses, or ladder < EUREKA
  REJECTED: No paradox axes, no evidence, or constitutional violation

F-binding:
  F1 AMANAH   — reversible by default; delta files are additive, never destructive
  F2 TRUTH    — all classifications labeled with evidence
  F4 CLARITY  — single entry point, structured output
  F7 HUMILITY — rejects eureka entries that don't meet quality thresholds
  F9 ANTI-HANTU — mechanical process, no consciousness claims
  F11 AUDIT   — every update emits a receipt
  F13 SOVEREIGN — REQUIRES_WITNESS entries need human ratification

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
import pathlib
from datetime import UTC, datetime
from typing import Any

from arifosmcp.schemas.eureka_ledger import (
    Cube777Cell,
    DeltaClassification,
    EurekaLedgerEntry,
    LadderState,
    ProposedDelta,
)

logger = logging.getLogger("arifosmcp.atlas333_update")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[ATLAS333_UPDATE] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ── Paths ────────────────────────────────────────────────────────────────────

_EUREKA_DIR = pathlib.Path("/root/.local/share/arifos/atlas333/eureka")
_CUBE777_STATE_PATH = pathlib.Path("/root/.local/share/arifos/atlas333/cube777_state.json")
_RECEIPTS_DIR = pathlib.Path("/root/.local/share/arifos/atlas333/receipts")
_DELTAS_DIR = pathlib.Path("/root/.local/share/arifos/atlas333/deltas")

# ── TEARFRAME Thresholds (from ATLAS333_EVERGREEN.md) ───────────────────────

_TEARFRAME_TRM = 0.94  # Truth-Reliability Metric
_TEARFRAME_ECHO = 0.87  # Evidence Coherence
_TEARFRAME_RASA = 0.85  # Resonance-Alignment
_AMANAH_MIN = 0.50  # Minimum evidence-bounded change score (Laplace-smoothed)


# ─────────────────────────────────────────────────────────────────────────────
# TEARFRAME computation (v1 proxies)
# ─────────────────────────────────────────────────────────────────────────────


def _compute_tearframe(entry: EurekaLedgerEntry) -> dict[str, Any]:
    """Compute TEARFRAME metrics for a eureka entry.

    v1 proxies:
      TRM  = average witness confidence (truth reliability)
      Echo = evidence quality ratio (structured / total)
      RASA = human witness presence (dignity signal)

    Returns dict with trm, echo, rasa values and pass/fail for each.
    """
    # TRM: average witness confidence
    witness_confs = [w.confidence for w in entry.witnesses]
    trm = sum(witness_confs) / max(len(witness_confs), 1)

    # Echo: evidence quality — count entries that look structured (short = OBS/DER)
    all_evidence = entry.evidence_for_a + entry.evidence_for_b
    if not all_evidence:
        echo = 0.0
    else:
        quality_count = sum(1 for e in all_evidence if len(e) < 200)
        echo = quality_count / len(all_evidence)

    # RASA: human witness presence
    human_conf = next((w.confidence for w in entry.witnesses if w.channel == "human"), 0.0)
    rasa = human_conf

    return {
        "trm": round(trm, 4),
        "echo": round(echo, 4),
        "rasa": round(rasa, 4),
        "trm_pass": trm >= _TEARFRAME_TRM,
        "echo_pass": echo >= _TEARFRAME_ECHO,
        "rasa_pass": rasa >= _TEARFRAME_RASA,
        "tearframe_pass": (
            trm >= _TEARFRAME_TRM and echo >= _TEARFRAME_ECHO and rasa >= _TEARFRAME_RASA
        ),
    }


def _compute_amanah(entry: EurekaLedgerEntry) -> float:
    """Compute Amanah score (evidence-bounded change).

    A = evidence_count / (evidence_count + 1) — Laplace-smoothed.
    Higher score = more evidence = more trustworthy change.
    """
    evidence_count = len(entry.evidence_for_a) + len(entry.evidence_for_b)
    return evidence_count / (evidence_count + 1)


# ─────────────────────────────────────────────────────────────────────────────
# Delta classification
# ─────────────────────────────────────────────────────────────────────────────


def classify_delta(entry: EurekaLedgerEntry) -> tuple[DeltaClassification, dict[str, Any]]:
    """Classify a eureka entry's proposed delta.

    Classification rules (soft gates):
      ACCEPTABLE_DELTA: EUREKA + all witnesses + TEARFRAME passes + Amanah >= min
      REQUIRES_WITNESS: TEARFRAME soft-fail, or missing witnesses, or ladder < EUREKA
      REJECTED: No paradox axes, no evidence, or constitutional violation

    TEARFRAME is a SOFT gate — failure means REQUIRES_WITNESS, not REJECTED.
    Only hard violations (no axes, no evidence) cause REJECTED.
    """
    tearframe = _compute_tearframe(entry)
    amanah = _compute_amanah(entry)

    diagnostics: dict[str, Any] = {
        "tearframe": tearframe,
        "amanah_score": round(amanah, 4),
        "amanah_threshold": _AMANAH_MIN,
        "ladder_state": entry.ladder_state.value,
        "paradox_axis_count": len(entry.paradox_axis_ids),
        "evidence_count": len(entry.evidence_for_a) + len(entry.evidence_for_b),
        "witness_count": len(entry.witnesses),
    }

    # Gate 1 (HARD): Must have paradox axes
    if not entry.paradox_axis_ids:
        diagnostics["rejection_reason"] = "No paradox axes specified"
        return DeltaClassification.REJECTED, diagnostics

    # Gate 2 (HARD): Must have at least some evidence
    evidence_count = len(entry.evidence_for_a) + len(entry.evidence_for_b)
    if evidence_count == 0:
        diagnostics["rejection_reason"] = "No evidence provided"
        return DeltaClassification.REJECTED, diagnostics

    # Gate 3 (SOFT): Ladder state — EUREKA required for automatic acceptance
    if entry.ladder_state != LadderState.EUREKA:
        diagnostics["rejection_reason"] = f"Ladder state is {entry.ladder_state.value}, not EUREKA"
        return DeltaClassification.REQUIRES_WITNESS, diagnostics

    # Gate 4 (SOFT): Witness completeness (all three channels)
    channels = {w.channel for w in entry.witnesses}
    if channels != {"human", "ai", "external"}:
        missing = {"human", "ai", "external"} - channels
        diagnostics["rejection_reason"] = f"Missing witnesses: {missing}"
        return DeltaClassification.REQUIRES_WITNESS, diagnostics

    # Gate 5 (SOFT): TEARFRAME
    if not tearframe["tearframe_pass"]:
        failed = [k for k in ("trm", "echo", "rasa") if not tearframe[f"{k}_pass"]]
        diagnostics["rejection_reason"] = f"TEARFRAME failed: {failed}"
        return DeltaClassification.REQUIRES_WITNESS, diagnostics

    # Gate 6 (SOFT): Amanah
    if amanah < _AMANAH_MIN:
        diagnostics["rejection_reason"] = f"Amanah {amanah:.3f} < {_AMANAH_MIN}"
        return DeltaClassification.REQUIRES_WITNESS, diagnostics

    # All gates passed
    diagnostics["classification"] = "ACCEPTABLE_DELTA"
    return DeltaClassification.ACCEPTABLE_DELTA, diagnostics


# ─────────────────────────────────────────────────────────────────────────────
# CUBE777 state management
# ─────────────────────────────────────────────────────────────────────────────


def _load_cube777_state() -> dict[str, Any]:
    """Load CUBE777 state from file. Returns empty state if not found."""
    if _CUBE777_STATE_PATH.exists():
        try:
            return json.loads(_CUBE777_STATE_PATH.read_text())
        except Exception as exc:
            logger.warning(f"Failed to load CUBE777 state: {exc}")

    return {
        "version": "1.0.0",
        "last_update": None,
        "total_updates": 0,
        "cells": {},
        "paradox_heat": {},
        "lane_weights": {
            "FACTUAL": {"tau": 0.5, "kappa": 0.5, "rho": 0.5},
            "CARE": {"tau": 0.5, "kappa": 0.5, "rho": 0.5},
            "SOCIAL": {"tau": 0.5, "kappa": 0.5, "rho": 0.5},
            "CRISIS": {"tau": 0.5, "kappa": 0.5, "rho": 0.5},
        },
    }


def _save_cube777_state(state: dict[str, Any]) -> None:
    """Save CUBE777 state to file."""
    _CUBE777_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CUBE777_STATE_PATH.write_text(json.dumps(state, indent=2, default=str))


def _cell_key(cell: Cube777Cell) -> str:
    """Canonical cell key: i/j/k."""
    return f"{cell.i}/{cell.j}/{cell.k}"


def _apply_delta_to_cell(
    state: dict[str, Any],
    cell: Cube777Cell,
    delta: ProposedDelta,
    entry: EurekaLedgerEntry,
) -> dict[str, Any]:
    """Apply a delta to a specific CUBE777 cell.

    Returns the before state of the cell.
    """
    key = _cell_key(cell)

    # Initialize cell if not exists
    if key not in state["cells"]:
        state["cells"][key] = {
            "tau": 0.5,
            "kappa": 0.5,
            "rho": 0.5,
            "touch_count": 0,
            "first_touch": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_touch": None,
            "history": [],
        }

    cell_state = state["cells"][key]
    before = {
        "tau": cell_state["tau"],
        "kappa": cell_state["kappa"],
        "rho": cell_state["rho"],
    }

    # Apply lane tensor adjustments (system-wide)
    for lane, adjustments in delta.lane_tensor_adjustments.items():
        if lane in state["lane_weights"]:
            for dim, delta_val in adjustments.items():
                if dim in ("tau", "kappa", "rho"):
                    old = state["lane_weights"][lane][dim]
                    new = max(0.0, min(1.0, old + delta_val))
                    state["lane_weights"][lane][dim] = round(new, 4)

    # Apply cell-level tensor update (additive, bounded)
    # Use contradiction class to determine dimension weighting
    cc = entry.contradiction_class.value
    if cc <= 3:
        # Truth-seeking contradictions: weight tau
        cell_state["tau"] = max(0.0, min(1.0, cell_state["tau"] + 0.01))
    elif cc <= 5:
        # Risk/domain contradictions: weight rho
        cell_state["rho"] = max(0.0, min(1.0, cell_state["rho"] + 0.01))
    else:
        # Meaning/action contradictions: weight kappa
        cell_state["kappa"] = max(0.0, min(1.0, cell_state["kappa"] + 0.01))

    # Update metadata
    cell_state["touch_count"] += 1
    cell_state["last_touch"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    cell_state["history"].append(
        {
            "entry_id": entry.id,
            "contradiction_class": cc,
            "ladder_state": entry.ladder_state.value,
            "timestamp": cell_state["last_touch"],
        }
    )

    # Keep history bounded (last 50 entries)
    if len(cell_state["history"]) > 50:
        cell_state["history"] = cell_state["history"][-50:]

    # Update paradox heat map
    for axis_id in entry.paradox_axis_ids:
        state["paradox_heat"][str(axis_id)] = state["paradox_heat"].get(str(axis_id), 0) + 1

    return before


# ─────────────────────────────────────────────────────────────────────────────
# Receipt emission
# ─────────────────────────────────────────────────────────────────────────────


def _emit_receipt(
    entry: EurekaLedgerEntry,
    classification: DeltaClassification,
    diagnostics: dict[str, Any],
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> str:
    """Write a receipt to the receipts directory.

    Returns the receipt file path.
    """
    _RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

    receipt = {
        "receipt_id": f"atlas333-update-{entry.id}",
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session_id": entry.session_id,
        "entry_id": entry.id,
        "classification": classification.value,
        "diagnostics": diagnostics,
        "before": before,
        "after": after,
        "contradiction_class": entry.contradiction_class.value,
        "ladder_state": entry.ladder_state.value,
        "paradox_axis_ids": entry.paradox_axis_ids,
        "cube777_cell": entry.cube777_cell.model_dump() if entry.cube777_cell else None,
        "witnesses": [w.model_dump() for w in entry.witnesses],
        "seal": "DITEMPA BUKAN DIBERI",
    }

    receipt_path = _RECEIPTS_DIR / f"{entry.session_id}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, default=str))
    logger.info(f"Receipt written: {receipt_path}")

    return str(receipt_path)


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────


def atlas333_update(session_id: str) -> dict[str, Any]:
    """Main entry point — read eureka entries, classify, apply, emit receipt.

    This is the governed updater in the closed loop:
      Θ_t → E_s → atlas333_update → Θ_{t+1}

    Args:
        session_id: The session that produced the eureka entry.

    Returns:
        Structured result with classification, diagnostics, and receipt path.
    """
    logger.info(f"atlas333_update called for session: {session_id}")

    # Step 1: Load eureka entry
    eureka_path = _EUREKA_DIR / f"{session_id}.json"
    if not eureka_path.exists():
        matches = list(_EUREKA_DIR.glob(f"{session_id}*.json"))
        if matches:
            eureka_path = matches[0]
        else:
            return {
                "status": "NO_ENTRY",
                "session_id": session_id,
                "reason": f"No eureka entry found for session {session_id}",
            }

    try:
        entry_data = json.loads(eureka_path.read_text())
        entry = EurekaLedgerEntry(**entry_data)
    except Exception as exc:
        return {
            "status": "PARSE_ERROR",
            "session_id": session_id,
            "reason": f"Failed to parse eureka entry: {exc}",
        }

    # Step 2: Classify delta
    classification, diagnostics = classify_delta(entry)
    logger.info(f"Classification: {classification.value}")

    # Step 3: Load CUBE777 state
    state = _load_cube777_state()
    before = None
    after = None

    # Step 4: Apply delta if acceptable
    if classification == DeltaClassification.ACCEPTABLE_DELTA and entry.cube777_cell:
        cell = entry.cube777_cell
        before = _apply_delta_to_cell(state, cell, entry.proposed_delta, entry)
        after = {
            "tau": state["cells"][_cell_key(cell)]["tau"],
            "kappa": state["cells"][_cell_key(cell)]["kappa"],
            "rho": state["cells"][_cell_key(cell)]["rho"],
        }

        state["total_updates"] += 1
        state["last_update"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        _save_cube777_state(state)
        logger.info(f"CUBE777 state updated: cell {_cell_key(cell)}")

    # Step 5: Write delta record
    _DELTAS_DIR.mkdir(parents=True, exist_ok=True)
    delta_record = {
        "session_id": session_id,
        "entry_id": entry.id,
        "classification": classification.value,
        "diagnostics": diagnostics,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    delta_path = _DELTAS_DIR / f"{session_id}.json"
    delta_path.write_text(json.dumps(delta_record, indent=2, default=str))

    # Step 6: Emit receipt
    receipt_path = _emit_receipt(entry, classification, diagnostics, before, after)

    # Step 7: Update entry with classification
    entry.delta_classification = classification
    eureka_path.write_text(entry.model_dump_json(indent=2))

    result = {
        "status": "COMPLETE",
        "session_id": session_id,
        "entry_id": entry.id,
        "classification": classification.value,
        "diagnostics": diagnostics,
        "receipt_path": receipt_path,
        "delta_path": str(delta_path),
        "cube777_updated": classification == DeltaClassification.ACCEPTABLE_DELTA,
    }

    logger.info(f"atlas333_update complete: {classification.value}")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: write eureka entry from session data
# ─────────────────────────────────────────────────────────────────────────────


def write_eureka_entry(
    session_id: str,
    contradiction_class: int,
    ladder_state: str,
    commitment_a: str,
    commitment_b: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Write a eureka entry to the ledger and run atlas333_update.

    This is the write path for the EUREKA777 capture flow.
    """
    from arifosmcp.schemas.eureka_ledger import build_eureka_entry

    _EUREKA_DIR.mkdir(parents=True, exist_ok=True)

    entry = build_eureka_entry(
        session_id=session_id,
        contradiction_class=contradiction_class,
        ladder_state=ladder_state,
        commitment_a=commitment_a,
        commitment_b=commitment_b,
        **kwargs,
    )

    entry_path = _EUREKA_DIR / f"{session_id}.json"
    entry_path.write_text(entry.model_dump_json(indent=2))
    logger.info(f"Eureka entry written: {entry_path}")

    update_result = atlas333_update(session_id)

    return {
        "entry_id": entry.id,
        "entry_path": str(entry_path),
        "update_result": update_result,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Self-test
# ─────────────────────────────────────────────────────────────────────────────


def _self_test() -> None:
    """Run basic self-test."""
    # Test 1: Classification with proper evidence and witnesses
    from arifosmcp.schemas.eureka_ledger import build_eureka_entry

    entry = build_eureka_entry(
        session_id="test-self-test-001",
        contradiction_class=5,
        ladder_state="EUREKA",
        commitment_a="GEOX says go",
        commitment_b="WEALTH says no",
        why_old_frame_failed="Frame assumed physical = investable",
        new_structure="Split geological validity from capital survivability",
        paradox_axis_ids=[3, 7, 14],
        affected_stage="555",
        human_conf=0.95,
        ai_conf=0.92,
        ext_conf=0.96,
    )
    # Add evidence
    entry.evidence_for_a = [
        "GEOX prospect evaluation: POS=0.72",
        "Seismic amplitude anomaly confirmed",
    ]
    entry.evidence_for_b = ["WEALTH NPV analysis: negative at P50", "Capital asymmetry detected"]

    classification, diagnostics = classify_delta(entry)
    assert classification == DeltaClassification.ACCEPTABLE_DELTA, (
        f"Expected ACCEPTABLE, got {classification}: {diagnostics.get('rejection_reason', 'OK')}"
    )
    assert diagnostics["tearframe"]["tearframe_pass"] is True
    assert diagnostics["amanah_score"] >= _AMANAH_MIN
    print(
        f"Test 1 PASS: {classification.value} (TRM={diagnostics['tearframe']['trm']}, Echo={diagnostics['tearframe']['echo']}, RASA={diagnostics['tearframe']['rasa']})"
    )

    # Test 2: CUBE777 state load/save
    state = _load_cube777_state()
    assert state["version"] == "1.0.0"
    assert state["total_updates"] == 0
    print("Test 2 PASS: CUBE777 state loaded")

    # Test 3: Cell application
    cell = entry.cube777_cell
    assert cell is not None
    before = _apply_delta_to_cell(state, cell, entry.proposed_delta, entry)
    assert before["tau"] == 0.5
    assert state["cells"][f"{cell.i}/{cell.j}/{cell.k}"]["touch_count"] == 1
    print(
        f"Test 3 PASS: Cell {_cell_key(cell)} updated (tau={state['cells'][_cell_key(cell)]['tau']})"
    )

    # Test 4: REQUIRES_WITNESS for incomplete witnesses
    entry2 = build_eureka_entry(
        session_id="test-self-test-002",
        contradiction_class=3,
        ladder_state="EUREKA",
        commitment_a="Model A says X",
        commitment_b="Model B says Y",
        paradox_axis_ids=[1, 2],
        affected_stage="333",
        human_conf=0.95,
        ai_conf=0.90,
        ext_conf=0.0,  # Missing external witness
    )
    entry2.evidence_for_a = ["Model A output"]
    entry2.evidence_for_b = ["Model B output"]
    classification2, diag2 = classify_delta(entry2)
    assert classification2 == DeltaClassification.REQUIRES_WITNESS, (
        f"Expected REQUIRES_WITNESS, got {classification2}"
    )
    print(f"Test 4 PASS: {classification2.value} ({diag2.get('rejection_reason', '')})")

    # Test 5: REJECTED for no evidence
    entry3 = build_eureka_entry(
        session_id="test-self-test-003",
        contradiction_class=1,
        ladder_state="TENSION",
        commitment_a="Something feels off",
        commitment_b="But not sure what",
        paradox_axis_ids=[5],
        affected_stage="000",
    )
    classification3, diag3 = classify_delta(entry3)
    assert classification3 == DeltaClassification.REJECTED, (
        f"Expected REJECTED, got {classification3}"
    )
    print(f"Test 5 PASS: {classification3.value} ({diag3.get('rejection_reason', '')})")

    print("\nALL SELF-TESTS PASSED")


if __name__ == "__main__":
    _self_test()
