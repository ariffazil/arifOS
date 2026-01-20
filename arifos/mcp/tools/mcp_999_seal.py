"""
MCP Tool 999: SEAL

Final verdict sealing and memory routing.

Constitutional validation:
- F1 (Amanah): Audit trail proves reversibility
- F9 (Anti-Hantu): Memory log prevents soul claims (timestamps everything)

This tool seals verdicts, creates audit entries, and routes to persistent storage.
Always PASS (never blocks).
"""

import asyncio
import base64
import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict

from arifos.mcp.models import VerdictResponse


def generate_seal(verdict: str, proof_hash: str, timestamp: str) -> str:
    """
    Create base64-encoded seal from verdict, proof, and timestamp.

    Args:
        verdict: Final verdict (SEAL, PARTIAL, VOID, etc.)
        proof_hash: SHA-256 proof hash from Tool 889
        timestamp: ISO8601 timestamp

    Returns:
        Base64-encoded seal string
    """
    seal_string = f"{verdict}:{proof_hash}:{timestamp}"
    seal_bytes = seal_string.encode('utf-8')
    sealed = base64.b64encode(seal_bytes).decode('utf-8')
    return sealed


def generate_audit_entry(
    verdict: str,
    proof_hash: str,
    decision_metadata: Dict[str, Any],
    timestamp: str
) -> Dict[str, Any]:
    """
    Create audit log entry.

    Args:
        verdict: Final verdict
        proof_hash: Proof hash from Tool 889
        decision_metadata: Metadata from decision pipeline
        timestamp: ISO8601 timestamp

    Returns:
        Complete audit entry dict
    """
    sealed_verdict = generate_seal(verdict, proof_hash, timestamp)

    return {
        "sealed_verdict": sealed_verdict,
        "decision_metadata": decision_metadata,
        "timestamp": timestamp,
        "floor_verdicts": decision_metadata.get("floor_verdicts", {})
    }


def generate_audit_log_id(verdict: str, timestamp: str) -> str:
    """
    Create deterministic audit log ID.

    Args:
        verdict: Final verdict
        timestamp: ISO8601 timestamp

    Returns:
        Audit log ID (e.g., "SEAL_2025-12-25_a1b2c3d4")
    """
    # Extract date portion
    date_part = timestamp[:10]  # YYYY-MM-DD

    # Create short hash from timestamp
    timestamp_hash = hashlib.sha256(timestamp.encode('utf-8')).hexdigest()[:8]

    audit_id = f"{verdict.upper()}_{date_part}_{timestamp_hash}"
    return audit_id


def generate_memory_location(audit_log_id: str, decision_metadata: Dict[str, Any]) -> str:
    """
    Create memory path for audit entry.

    Args:
        audit_log_id: Audit log ID
        decision_metadata: Decision metadata (may contain query)

    Returns:
        Memory location path
    """
    base_path = f"audit_trail/{audit_log_id}"

    # If query present, sanitize and append
    query = decision_metadata.get("query", "")
    if query:
        # Sanitize: replace spaces/special chars with underscores
        sanitized_query = re.sub(r'[^a-zA-Z0-9_-]', '_', query)

        # Limit to 50 chars
        sanitized_query = sanitized_query[:50]

        # Remove trailing underscores
        sanitized_query = sanitized_query.rstrip('_')

        if sanitized_query:
            base_path = f"{base_path}/{sanitized_query}"

    return base_path


def validate_seal(sealed_verdict: str, original_verdict: str) -> bool:
    """
    Validate that sealed verdict matches original.

    Args:
        sealed_verdict: Base64-encoded seal
        original_verdict: Original verdict string

    Returns:
        True if seal is valid
    """
    try:
        # Decode from base64
        decoded_bytes = base64.b64decode(sealed_verdict.encode('utf-8'))
        decoded_string = decoded_bytes.decode('utf-8')

        # Check if starts with original verdict
        return decoded_string.startswith(original_verdict)
    except Exception:
        # Decoding error → invalid
        return False


async def mcp_999_seal(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 999: SEAL - Quantum Measurement Collapse via ParallelHypervisor.

    Constitutional validation:
    - F1 (Amanah): Audit trail proves reversibility
    - F9 (Anti-Hantu): Memory log prevents soul claims
    - Kimi Directive: Collapses AGI/ASI/APEX superposition

    Args:
        request: {
            "verdict": "SEAL | PARTIAL | VOID | SABAR | HOLD", (optional hint)
            "decision_metadata": { "query": ... }
        }

    Returns:
        VerdictResponse with constitutional proof.
    """
    from arifos.mcp.constitution import (
        ConstitutionalViolationError,
        execute_constitutional_physics,
    )

    # Extract inputs
    verdict_hint = request.get("verdict", "SABAR")
    decision_metadata = request.get("decision_metadata", {})
    query = decision_metadata.get("query", "Unknown Query")

    # We use a mocked user_id here as the tool signature doesn't mandate it,
    # but hypervisor needs it. In real flow, context provides it.
    user_id = decision_metadata.get("user_id", "user_generic")

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        # EXECUTE SUPERPOSITION (The real 999 logic)
        # This runs AGI, ASI, and APEX in parallel and collapses the result
        hypervisor_result = await execute_constitutional_physics(query, user_id, decision_metadata)

        final_verdict = hypervisor_result.get("verdict", "VOID")
        proofs = hypervisor_result.get("aggregated_proofs", {})
        receipt = hypervisor_result.get("final_receipt")

        # If Hypervisor returns SEAL, we proceed to create the official seal string
        # using the generic generator for compatibility
        # We use the Action Hash from the receipt as the proof_hash
        proof_hash_from_hypervisor = receipt.action_hash if receipt else "no_receipt"

        sealed_verdict = generate_seal(final_verdict, proof_hash_from_hypervisor, timestamp)

        # Log Logic (kept for compatibility with 000-999 flow expecting these side_data fields)
        audit_log_id = generate_audit_log_id(final_verdict, timestamp)
        memory_location = generate_memory_location(audit_log_id, decision_metadata)

        # DEBUG: Check receipt processing
        print(f"[DEBUG_999] Processing receipt: {receipt}")
        if receipt:
            try:
                from dataclasses import asdict

                from arifos.core.memory.vault.vault_manager import VaultManager

                vault = VaultManager()
                print(f"[DEBUG_999] Vault path: {vault.config.receipts_path}")

                # Convert dataclass to dict and handle datetimes
                receipt_dict = asdict(receipt)
                if isinstance(receipt_dict.get('timestamp'), datetime):
                    receipt_dict['timestamp'] = receipt_dict['timestamp'].isoformat()

                vault.record_receipt(receipt_dict)
                print("[DEBUG_999] Receipt recorded successfully.")
            except Exception as e:
                print(f"[WARNING_999] Failed to persist receipt to Vault: {e}")
        else:
            print("[DEBUG_999] No receipt found in hypervisor result.")

        return VerdictResponse(
            verdict="PASS" if final_verdict == "SEAL" else "VOID", # Tool execution passed, but verdict might be VOID
            reason=f"Quantum Measurement Complete: {final_verdict}",
            side_data={
                "sealed_verdict": sealed_verdict,
                "audit_log_id": audit_log_id,
                "memory_location": memory_location,
                "timestamp": timestamp,
                "seal_valid": True,
                "hypervisor_proof": proofs,
                "constitutional_status": hypervisor_result.get("constitutional_status")
            },
            timestamp=timestamp
        )

    except ConstitutionalViolationError as e:
        return VerdictResponse(
            verdict="VOID",
            reason=f"Constitutional Crisis: {e}",
            side_data={"error": str(e)},
            timestamp=timestamp
        )
    except Exception as e:
        # Catch robustness issues
        return VerdictResponse(
             verdict="VOID",
             reason=f"Hypervisor Failure: {e}",
             side_data={"error": str(e)},
             timestamp=timestamp
        )


def mcp_999_seal_sync(request: Dict[str, Any]) -> VerdictResponse:
    """Synchronous wrapper for mcp_999_seal."""
    return asyncio.run(mcp_999_seal(request))
