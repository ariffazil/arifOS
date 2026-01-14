"""
Stage 999 SEAL: Cooling Ledger Integration (Final Constitutional Receipt)

Implements final sealing based on Track B spec:
L2_PROTOCOLS/v45/cooling_ledger_phoenix.json

Authority: Track A Canon (derivation from Cooling Ledger architecture)

PURPOSE: Final stage that logs the constitutional verdict to the append-only
cooling ledger, generates cryptographic receipts, and packages the sealed response.
This stage creates the IMMUTABLE audit trail for governance accountability.

Cooling Ledger Features:
- SHA3-256 hash chain integrity
- Append-only JSONL format
- Head state tracking (v37)
- Hot segment rotation
- Phoenix-72 analysis queries

VERDICT ROUTING:
- SEAL → ACTIVE band (ready for delivery)
- PARTIAL → PHOENIX band (requires pattern synthesis)
- VOID → VOID band (blocked)
- SABAR → PENDING band (requires repair)
- HOLD_888 → LEDGER band (human review required)

NEW FILE: Cooling ledger integration (not in pipeline/)
"""

from typing import TypedDict, Literal
from datetime import datetime, timezone
import hashlib
import uuid

from ..memory.ledger.cooling_ledger import (
    CoolingLedgerV37,
    log_cooling_entry_v37
)
from ..enforcement.metrics import Metrics
from .witness_888 import WitnessBundle888, WitnessVerdict


# Type aliases
RetentionBand = Literal["ACTIVE", "LEDGER", "PHOENIX", "WITNESS", "PENDING", "VOID"]
SealStatus = Literal["SEALED", "LOGGED", "FAILED"]


class CoolingReceipt(TypedDict):
    """Cryptographic receipt from cooling ledger."""

    receipt_id: str             # UUID for this receipt
    entry_hash: str             # SHA3-256 hash of ledger entry
    timestamp: str              # ISO-8601 timestamp
    verdict: WitnessVerdict     # Final verdict (SEAL/PARTIAL/VOID/SABAR/HOLD_888)
    retention_band: RetentionBand  # Routing band
    ledger_path: str            # Path to ledger file


class SealBundle999(TypedDict):
    """Final sealed bundle with cooling ledger receipt."""

    witness_bundle_888: WitnessBundle888  # IMMUTABLE pass-through (F8)
    cooling_receipt: CoolingReceipt
    seal_status: SealStatus
    sealed_response: str | None  # Final response (if SEALED)
    error_message: str | None    # Error details (if FAILED)
    handoff: dict[str, str | bool]  # Handoff to delivery system


def route_verdict_to_band(witness_verdict: WitnessVerdict) -> RetentionBand:
    """
    Route verdict to appropriate retention band per spec.

    Spec: L2_PROTOCOLS/v45/cooling_ledger_phoenix.json
    Section: verdict_band_routing

    Args:
        witness_verdict: Final verdict from 888 WITNESS

    Returns:
        Retention band for cooling ledger storage
    """
    routing_table: dict[WitnessVerdict, RetentionBand] = {
        "SEAL": "ACTIVE",        # Ready for delivery
        "PARTIAL": "PHOENIX",    # Pattern synthesis needed
        "VOID": "VOID",          # Blocked, no delivery
        "SABAR": "PENDING",      # Repair required
        "HOLD_888": "LEDGER"     # Human review required
    }

    return routing_table.get(witness_verdict, "VOID")


def extract_metrics_from_witness(witness_bundle: WitnessBundle888) -> Metrics:
    """
    Extract arifos_core.enforcement.metrics.Metrics from witness bundle.

    This constructs a Metrics object from the floor scores accumulated
    across all pipeline stages (111→222→333→555→888).

    Args:
        witness_bundle: Output from 888 WITNESS

    Returns:
        Metrics instance for cooling ledger logging
    """
    empathy_bundle = witness_bundle["empathy_bundle_555"]
    integration_bundle = empathy_bundle["integration_bundle_333"]
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore

    # Extract floor scores
    if reasoned_bundle:
        floor_scores = reasoned_bundle.get("floor_scores", {})
    else:
        floor_scores = {}

    asi_scores = empathy_bundle["asi_floor_scores"]
    _hypervisor = witness_bundle["hypervisor_status"]  # Reserved for future use

    # Construct Metrics object
    metrics = Metrics(
        truth=floor_scores.get("F1_truth", 0.0),
        delta_s=floor_scores.get("F2_clarity", 0.0),
        peace_squared=asi_scores.get("F4_peace_squared", 0.0),
        kappa_r=asi_scores.get("F5_kappa_r", 0.0),
        omega_0=asi_scores.get("F6_omega_0", 0.04),
        rasa=asi_scores.get("F7_rasa", True),
        amanah=True,  # Assume LOCK (pipeline wouldn't reach 999 if broken)
        tri_witness=asi_scores.get("F3_tri_witness", 0.0),
        anti_hantu=True  # Assume OK (F9 would block earlier)
    )

    return metrics


def synthesize_sealed_response(witness_bundle: WitnessBundle888) -> str:
    """
    Synthesize final sealed response from witness bundle.

    Logic:
    - SEAL: Return AGI draft from 333 REASON
    - PARTIAL: Return AGI draft with warning prefix
    - VOID/SABAR/HOLD_888: Return error message (no response)

    Args:
        witness_bundle: Output from 888 WITNESS

    Returns:
        Sealed response string (or error message)
    """
    witness_verdict = witness_bundle["witness_verdict"]
    verdict_reasoning = witness_bundle["verdict_reasoning"]

    # Extract AGI draft
    empathy_bundle = witness_bundle["empathy_bundle_555"]
    integration_bundle = empathy_bundle["integration_bundle_333"]
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore

    if reasoned_bundle:
        agi_draft = reasoned_bundle.get("agi_draft", "")
    else:
        agi_draft = ""

    # Route based on verdict
    if witness_verdict == "SEAL":
        return agi_draft

    elif witness_verdict == "PARTIAL":
        # Prefix with constitutional warning
        warning = (
            f"⚠️ PARTIAL SEAL: ASI soft floor warnings detected.\n"
            f"Reasoning: {verdict_reasoning}\n\n"
            f"Response (proceed with caution):\n{agi_draft}"
        )
        return warning

    else:  # VOID, SABAR, HOLD_888
        error_msg = (
            f"Constitutional verdict: {witness_verdict}\n"
            f"Reasoning: {verdict_reasoning}\n\n"
            f"This query cannot be processed due to constitutional floor violations. "
            f"Please review the reasoning above and adjust your request."
        )
        return error_msg


def seal_stage(
    witness_bundle_888: WitnessBundle888,
    query: str = "",
    ledger: CoolingLedgerV37 | None = None
) -> SealBundle999:
    """
    999 SEAL: Cooling ledger integration (final constitutional receipt).

    Implements Track B spec: L2_PROTOCOLS/v45/cooling_ledger_phoenix.json

    Pipeline:
    1. Extract metrics from witness bundle (floor scores from all stages)
    2. Synthesize sealed response (AGI draft or error message)
    3. Route verdict to retention band (ACTIVE/PHOENIX/VOID/PENDING/LEDGER)
    4. Log entry to cooling ledger (append-only hash chain)
    5. Generate cryptographic receipt (SHA3-256 entry hash)
    6. Package seal_bundle with IMMUTABLE pass-through

    Cooling Ledger Entry:
    - Hash chain integrity (SHA3-256)
    - Verdict routing (per retention band)
    - Metrics snapshot (F1-F12 floor scores)
    - Phoenix-72 query support

    Args:
        witness_bundle_888: Output from 888 WITNESS
        query: Original user query (for ledger logging)
        ledger: Optional CoolingLedgerV37 instance (uses default if None)

    Returns:
        SealBundle999 with cooling receipt

    Raises:
        Does NOT raise (fail-safe logging). If ledger write fails, returns
        seal_status="FAILED" with error details. Caller should handle gracefully.
    """
    # Step 1: Extract witness verdict
    witness_verdict = witness_bundle_888["witness_verdict"]
    _verdict_reasoning = witness_bundle_888["verdict_reasoning"]  # Reserved for logging

    # Step 2: Extract metrics
    try:
        metrics = extract_metrics_from_witness(witness_bundle_888)
    except Exception:
        # Fallback: Create minimal metrics if extraction fails
        metrics = Metrics(
            truth=0.0, delta_s=0.0, peace_squared=0.0,
            kappa_r=0.0, omega_0=0.04, rasa=True,
            amanah=False, tri_witness=0.0, anti_hantu=True
        )

    # Step 3: Synthesize sealed response
    sealed_response = synthesize_sealed_response(witness_bundle_888)

    # Step 4: Route to retention band
    retention_band = route_verdict_to_band(witness_verdict)

    # Step 5: Generate receipt ID
    receipt_id = str(uuid.uuid4())

    # Step 6: Compute query/response hashes (reserved for future ledger extension)
    _query_hash = hashlib.sha256(query.encode()).hexdigest()
    _response_hash = hashlib.sha256(sealed_response.encode()).hexdigest()

    # Step 7: Log to cooling ledger
    if ledger is None:
        ledger = CoolingLedgerV37()

    try:
        # Prepare floor warnings
        tri_kernel = witness_bundle_888["tri_kernel_evaluation"]
        floor_warnings = tri_kernel.get("failure_summary", [])

        # Log entry (v37 format)
        success, entry_dict, error = log_cooling_entry_v37(
            job_id=receipt_id,
            verdict=witness_verdict,
            metrics=metrics,
            query=query,
            candidate_output=sealed_response,
            stakes_class="CLASS_A",  # Default stakes (TODO: extract from sensed_bundle)
            floor_warnings=floor_warnings,
            phoenix_cycle_id=None,  # TODO: Phoenix-72 integration
            eureka_receipt_id=None,  # TODO: EUREKA 777 integration
            scar_ids=None,           # TODO: SCAR tracking
            ledger=ledger
        )

        if success:
            entry_hash = entry_dict.get("entry_hash", "")
            timestamp = entry_dict.get("timestamp", "")
            seal_status: SealStatus = "SEALED"
            error_message = None
        else:
            # Ledger write failed
            entry_hash = ""
            timestamp = datetime.now(timezone.utc).isoformat()
            seal_status = "FAILED"
            error_message = error or "Unknown ledger error"

    except Exception as e:
        # Fail-safe: Log error but don't crash
        entry_hash = ""
        timestamp = datetime.now(timezone.utc).isoformat()
        seal_status = "FAILED"
        error_message = f"Cooling ledger exception: {str(e)}"

    # Step 8: Create cooling receipt
    cooling_receipt: CoolingReceipt = {
        "receipt_id": receipt_id,
        "entry_hash": entry_hash,
        "timestamp": timestamp,
        "verdict": witness_verdict,
        "retention_band": retention_band,
        "ledger_path": str(ledger.config.ledger_path) if ledger else "unknown"
    }

    # Step 9: Package seal bundle
    seal_bundle: SealBundle999 = {
        "witness_bundle_888": witness_bundle_888,  # ← IMMUTABLE (F8)
        "cooling_receipt": cooling_receipt,
        "seal_status": seal_status,
        "sealed_response": sealed_response if seal_status == "SEALED" else None,
        "error_message": error_message,
        "handoff": {
            "from_stage": "999_SEAL",
            "to_stage": "DELIVERY",
            "ready_for_delivery": (
                seal_status == "SEALED" and witness_verdict in ["SEAL", "PARTIAL"]
            ),
            "retention_band": retention_band
        }
    }

    return seal_bundle


__all__ = [
    "seal_stage",
    "SealBundle999",
    "CoolingReceipt",
    "RetentionBand",
    "SealStatus",
    "route_verdict_to_band",
    "extract_metrics_from_witness",
    "synthesize_sealed_response"
]
