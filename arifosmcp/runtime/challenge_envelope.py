"""arifosmcp/runtime/challenge_envelope.py — the 555 challenge envelope.

One verification protocol for the whole federation (shape approved 2026-10-18):
claim · evidence · provenance · freshness · contradiction · falsifier ·
confidence · independent_witness. Verdicts: ACCEPT · REJECT · UNKNOWN_OUTCOME.
A claim without a falsifier is not a challenge — it is a wish.

(1) validate_envelope(): the gate. CLAIM_WITHOUT_FALSIFIER is REJECTED; absent
    evidence is UNKNOWN_OUTCOME (never ACCEPT); the claimant cannot be its own
    only witness (WITNESS_SELF); confidence outside [0,1] cannot judge.
(2) Four named adapters map native organ shapes into the envelope so HERMES,
    CHRON, FRAME and A-FORGE all speak one protocol instead of four dialects.

NAMED CONSUMERS: arif_judge evidence gate (kernel) · HERMES claim_validate ·
CHRON prediction mint · FRAME observation handoff · A-FORGE claim gates.
NAMED FAILURE CLASSES: CLAIM_WITHOUT_FALSIFIER · WITNESS_SELF ·
EVIDENCE_ABSENT (-> UNKNOWN_OUTCOME) · CONFIDENCE_UNBOUNDED.
Spec home: /root/AAA/schemas/challenge-envelope.schema.json

Floors engaged: F2 F3 F7 · DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from typing import Any, Mapping

VERDICT_ACCEPT = "ACCEPT"
VERDICT_REJECT = "REJECT"
VERDICT_UNKNOWN_OUTCOME = "UNKNOWN_OUTCOME"

CLAIM_WITHOUT_FALSIFIER = "CLAIM_WITHOUT_FALSIFIER"
WITNESS_SELF = "WITNESS_SELF"
EVIDENCE_ABSENT = "EVIDENCE_ABSENT"
CONFIDENCE_UNBOUNDED = "CONFIDENCE_UNBOUNDED"

REQUIRED_FIELDS = (
    "claim",
    "evidence",
    "provenance",
    "freshness",
    "contradiction",
    "falsifier",
    "confidence",
    "independent_witness",
)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True  # numbers incl. 0.0 are present; the band check judges them


def validate_envelope(env: Mapping[str, Any]) -> dict[str, Any]:
    """Gate one challenge envelope. Deterministic; no network."""
    e = dict(env or {})
    out: dict[str, Any] = {"verdict": VERDICT_ACCEPT, "reason": None, "missing": []}

    # 1) The failure class first: no falsifier -> not a challenge.
    if not _present(e.get("falsifier")):
        out.update(verdict=VERDICT_REJECT, reason=CLAIM_WITHOUT_FALSIFIER)
        return out

    # 2) Absent evidence cannot be judged — UNKNOWN_OUTCOME, never ACCEPT.
    missing = [f for f in REQUIRED_FIELDS if not _present(e.get(f))]
    if missing:
        out.update(verdict=VERDICT_UNKNOWN_OUTCOME, missing=missing)
        return out

    # 3) Witness independence: the claimant is not its own witness.
    claimant = str(e.get("claimant") or "")
    witnesses = e.get("independent_witness") or []
    independent = [
        w for w in witnesses if isinstance(w, Mapping) and str(w.get("id") or "") != claimant
    ]
    if not independent:
        out.update(verdict=VERDICT_UNKNOWN_OUTCOME, reason=WITNESS_SELF)
        return out

    # 4) Confidence must be a bounded number to mean anything.
    try:
        conf = float(e.get("confidence"))
    except (TypeError, ValueError):
        out.update(verdict=VERDICT_UNKNOWN_OUTCOME, reason=CONFIDENCE_UNBOUNDED)
        return out
    if not 0.0 <= conf <= 1.0:
        out.update(verdict=VERDICT_UNKNOWN_OUTCOME, reason=CONFIDENCE_UNBOUNDED)
        return out

    return out


# ── Adapters: native organ shape -> envelope ─────────────────────────────────


def from_hermes_claim(rec: Mapping[str, Any]) -> dict[str, Any]:
    """HERMES claim_validate record: sources, counterstory, ts."""
    counterstory = str(rec.get("counterstory") or "")
    return {
        "claim": rec.get("claim"),
        "evidence": [{"ref": str(s)} for s in (rec.get("sources") or [])],
        "provenance": f"hermes:{rec.get('actor') or 'claim_validate'}",
        "freshness": rec.get("ts"),
        "contradiction": counterstory or None,
        "falsifier": rec.get("falsifier")
        or (f"counterstory confirmed: {counterstory}" if counterstory else None),
        "confidence": rec.get("confidence"),
        "independent_witness": [{"id": "hermes-claim-store", "kind": "record"}],
    }


def from_chron_prediction(rec: Mapping[str, Any]) -> dict[str, Any]:
    """CHRON prediction: resolution criteria ARE the falsifier."""
    return {
        "claim": rec.get("prediction") or rec.get("claim"),
        "evidence": [{"ref": str(rec.get("episode_id"))}] if rec.get("episode_id") else [],
        "provenance": f"chron:{rec.get('mint_id') or 'prediction_mint'}",
        "freshness": rec.get("minted_at"),
        "contradiction": rec.get("contradiction"),
        "falsifier": rec.get("resolution") or rec.get("falsifier"),
        "confidence": rec.get("confidence"),
        "independent_witness": [{"id": "chron-verification", "kind": "record"}],
    }


def from_frame_observation(rec: Mapping[str, Any]) -> dict[str, Any]:
    """FRAME observation: drift signals become the contradiction surface."""
    signals = rec.get("signals") or []
    sig = "signals: " + ", ".join(str(s) for s in signals) if signals else None
    return {
        "claim": rec.get("observation") or rec.get("claim"),
        "evidence": [{"ref": str(rec.get("evidence_ref"))}] if rec.get("evidence_ref") else [],
        "provenance": f"frame:{rec.get('observer') or 'observation'}",
        "freshness": rec.get("observed_at"),
        "contradiction": sig,
        "falsifier": rec.get("falsifier")
        or ("observation withdrawn when signals clear: " + sig if sig else None),
        "confidence": rec.get("confidence"),
        "independent_witness": [{"id": "frame", "kind": "witness"}],
    }


def from_aforge_receipt(rec: Mapping[str, Any]) -> dict[str, Any]:
    """A-FORGE receipt: KEEP/REVERT first-class — the revert path is falsifier."""
    return {
        "claim": rec.get("justification") or rec.get("claim"),
        "evidence": [{"ref": str(rec.get("receipt_id"))}] if rec.get("receipt_id") else [],
        "provenance": f"a-forge:{rec.get('receipt_id') or 'receipt'}",
        "freshness": rec.get("created_at"),
        "contradiction": rec.get("contradiction"),
        "falsifier": rec.get("revert") or rec.get("falsifier"),
        "confidence": rec.get("confidence"),
        "independent_witness": [{"id": "a-forge-vault", "kind": "record"}],
    }
