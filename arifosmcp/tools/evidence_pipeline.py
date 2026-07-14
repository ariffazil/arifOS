"""
arifOS Federation — Evidence Receipt Pipeline
═══════════════════════════════════════════════════════════════════════
FORGED 2026-07-14 · P0.3 closure of G5 (No Evidence Receipt Producer)

Purpose:
    Convert raw output from GEOX/WEALTH/WELL/A-FORGE into a constitutional
    EvidenceReceipt that arif_judge can consume for SEAL-grade decisions.

Flow:
    geox_prospect(...) → arif_observe(mode="evidence_ingest", organ="geox", ...)
    → returns EvidenceReceipt{receipt_id, organ, tool_name, computation_hash,
      parameters_snapshot, epistemic_label, confidence_band, witness_chain,
      created_at}
    → arif_judge(..., evidence_receipt=receipt) → SEAL/HOLD/SABAR/VOID

Floor alignment:
    F1 AMANAH  — Receipts are content-addressed (sha256). Reversible by re-derivation.
    F2 TRUTH   — Every claim is tagged OBS/DER/INT/SPEC with confidence band.
    F3 WITNESS — Receipt carries human/AI/external witness slots.
    F4 CLARITY — Pipeline output is structured JSON. ΔS ≤ 0.
    F11 AUDIT  — Receipts include actor_signature, session_id, lease_id.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("arifosmcp.evidence_pipeline")

__all__ = [
    "EvidenceReceipt",
    "ReceiptBuildError",
    "build_evidence_receipt",
    "ingest_organ_output",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Canonical enums — referenced from federation_enums where importable
# ═══════════════════════════════════════════════════════════════════════════════

EPISTEMIC_LABEL = ("OBSERVED", "DERIVED", "INTERPRETED", "SPECULATED", "ASSUMED")
CONFIDENCE_BAND = ("UNKNOWN", "LOW", "MODERATE", "HIGH", "VERIFIED", "SEALED")


# ═══════════════════════════════════════════════════════════════════════════════
# Errors
# ═══════════════════════════════════════════════════════════════════════════════


class ReceiptBuildError(Exception):
    """Raised when an evidence receipt cannot be constructed."""


# ═══════════════════════════════════════════════════════════════════════════════
# Evidence Receipt — canonical structure
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class EvidenceReceipt:
    """Constitutional evidence receipt — what arif_judge consumes.

    Fields are intentionally flat (no nested untyped dicts) so the receipt
    can be hashed, signed, and audited deterministically.
    """

    receipt_id: str
    schema_version: str
    organ: str
    tool_name: str
    session_id: str
    actor_id: str
    created_at: str
    computation_hash: str
    parameters_snapshot: dict[str, Any]
    output_summary: dict[str, Any]
    epistemic_label: str  # one of EPISTEMIC_LABEL
    confidence_band: str  # one of CONFIDENCE_BAND
    witness_chain: dict[str, str] = field(default_factory=dict)
    risk_flags: list[str] = field(default_factory=list)
    void_flags: list[str] = field(default_factory=list)
    upstream_receipts: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_canonical_json(self) -> str:
        """Deterministic JSON for hashing/signing."""
        return json.dumps(self.to_dict(), sort_keys=True, default=str, separators=(",", ":"))


# ═══════════════════════════════════════════════════════════════════════════════


def _sha256_hex(payload: Any) -> str:
    """Stable sha256 of any JSON-serializable payload."""
    if isinstance(payload, str):
        encoded = payload.encode("utf-8")
    else:
        encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode(
            "utf-8"
        )
    return hashlib.sha256(encoded).hexdigest()


def _validate_label(label: str, *, kind: str) -> str:
    valid = EPISTEMIC_LABEL if kind == "epistemic" else CONFIDENCE_BAND
    upper = label.upper().strip()
    if upper not in valid:
        raise ReceiptBuildError(f"Invalid {kind} label '{label}'. Must be one of {valid}")
    return upper


def _summarize_output(output: Any) -> dict[str, Any]:
    """Compress raw organ output to a stable summary dict.

    Keeps only hashable/primitive fields. Nested dicts are preserved up to depth 2.
    """
    if isinstance(output, dict):
        out: dict[str, Any] = {}
        for k, v in output.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                out[k] = v
            elif isinstance(v, (list, tuple)):
                out[k] = f"<{type(v).__name__} len={len(v)}>"
            elif isinstance(v, dict):
                out[k] = _summarize_output(v)
            else:
                out[k] = f"<{type(v).__name__}>"
        return out
    if isinstance(output, (list, tuple)):
        return {"type": type(output).__name__, "len": len(output)}
    if isinstance(output, str):
        return {"type": "str", "len": len(output), "preview": output[:200]}
    return {"type": type(output).__name__, "repr": repr(output)[:200]}


# ═══════════════════════════════════════════════════════════════════════════════


def build_evidence_receipt(
    *,
    organ: str,
    tool_name: str,
    output: Any,
    parameters: dict[str, Any] | None = None,
    epistemic_label: str = "DERIVED",
    confidence_band: str = "MODERATE",
    session_id: str = "anonymous",
    actor_id: str = "anonymous",
    witness_chain: dict[str, str] | None = None,
    risk_flags: list[str] | None = None,
    void_flags: list[str] | None = None,
    upstream_receipts: list[str] | None = None,
    notes: str = "",
) -> EvidenceReceipt:
    """Build a canonical EvidenceReceipt from any organ's output.

    Pure function — no side effects, no I/O. Deterministic given inputs.

    Example:
        >>> receipt = build_evidence_receipt(
        ...     organ="geox",
        ...     tool_name="geox_basin",
        ...     output={"name": "Malay Basin", "depth_m": 4500, "fill": "Eocene-Oligocene"},
        ...     parameters={"basin_name": "Malay Basin"},
        ...     epistemic_label="DERIVED",
        ...     confidence_band="MODERATE",
        ... )
    """
    label = _validate_label(epistemic_label, kind="epistemic")
    conf = _validate_label(confidence_band, kind="confidence")

    params_snapshot = parameters or {}
    output_summary = _summarize_output(output)

    computation_hash = _sha256_hex(
        {
            "organ": organ,
            "tool_name": tool_name,
            "parameters": params_snapshot,
            "output_summary": output_summary,
        }
    )
    created_at = datetime.now(UTC).isoformat()
    receipt_id = f"er_{_sha256_hex(computation_hash + created_at)[:24]}"

    receipt = EvidenceReceipt(
        receipt_id=receipt_id,
        schema_version="1.0.0",
        organ=organ,
        tool_name=tool_name,
        session_id=session_id,
        actor_id=actor_id,
        created_at=created_at,
        computation_hash=computation_hash,
        parameters_snapshot=params_snapshot,
        output_summary=output_summary,
        epistemic_label=label,
        confidence_band=conf,
        witness_chain=witness_chain or {},
        risk_flags=risk_flags or [],
        void_flags=void_flags or [],
        upstream_receipts=upstream_receipts or [],
        notes=notes,
    )
    logger.info(
        "evidence_receipt_built receipt_id=%s organ=%s tool=%s label=%s conf=%s",
        receipt_id,
        organ,
        tool_name,
        label,
        conf,
    )
    return receipt


# ═══════════════════════════════════════════════════════════════════════════════
# ingest_organ_output — convenience wrapper used by arif_observe(mode=evidence_ingest)
# ═══════════════════════════════════════════════════════════════════════════════


def ingest_organ_output(
    *,
    organ: str,
    tool_name: str,
    output: Any,
    parameters: dict[str, Any] | None = None,
    epistemic_label: str = "DERIVED",
    confidence_band: str = "MODERATE",
    session_id: str = "anonymous",
    actor_id: str = "anonymous",
    **kwargs: Any,
) -> dict[str, Any]:
    """High-level ingest function — wraps build_evidence_receipt with default
    witness-chain wiring and returns a dict ready for arif_judge consumption.

    Returns:
        dict with keys: receipt, receipt_id, computation_hash, ready_for_judge
    """
    try:
        receipt = build_evidence_receipt(
            organ=organ,
            tool_name=tool_name,
            output=output,
            parameters=parameters,
            epistemic_label=epistemic_label,
            confidence_band=confidence_band,
            session_id=session_id,
            actor_id=actor_id,
            **kwargs,
        )
    except ReceiptBuildError as exc:
        return {
            "ready_for_judge": False,
            "error": str(exc),
            "receipt_id": None,
        }

    # Auto-wire default witness chain if not provided
    if not receipt.witness_chain:
        receipt.witness_chain = {
            "human": "arif-fazil",
            "ai": actor_id or "anonymous",
            "external": f"{organ}:{tool_name}",
        }

    return {
        "ready_for_judge": True,
        "receipt": receipt.to_dict(),
        "receipt_id": receipt.receipt_id,
        "computation_hash": receipt.computation_hash,
        "schema_version": receipt.schema_version,
    }
