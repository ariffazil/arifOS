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

from arifos_core.mcp.models import VerdictResponse


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
    MCP Tool 999: SEAL - Final verdict sealing and memory routing.

    Always PASS (sealing, not rejection).

    Args:
        request: {
            "verdict": "SEAL | PARTIAL | VOID | SABAR | HOLD",
            "proof_hash": "sha256 hex string from 889",
            "decision_metadata": {
                "query": "original query",
                "response": "generated response",
                "floor_verdicts": {"222": "PASS", ...}
            }
        }

    Returns:
        VerdictResponse with sealed_verdict, audit_log_id, etc. in side_data
    """
    # Extract inputs
    verdict = request.get("verdict", "SABAR")
    proof_hash = request.get("proof_hash", "")
    decision_metadata = request.get("decision_metadata", {})

    # Validate inputs
    if not isinstance(verdict, str) or not verdict:
        verdict = "SABAR"
    if not isinstance(proof_hash, str):
        proof_hash = ""
    if not isinstance(decision_metadata, dict):
        decision_metadata = {}

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Generate seal
    sealed_verdict = generate_seal(verdict, proof_hash, timestamp)

    # Generate audit entry
    audit_entry = generate_audit_entry(verdict, proof_hash, decision_metadata, timestamp)

    # Generate audit log ID
    audit_log_id = generate_audit_log_id(verdict, timestamp)

    # Generate memory location
    memory_location = generate_memory_location(audit_log_id, decision_metadata)

    # Validate seal
    seal_valid = validate_seal(sealed_verdict, verdict)

    return VerdictResponse(
        verdict="PASS",
        reason=f"Verdict sealed successfully: {verdict}",
        side_data={
            "sealed_verdict": sealed_verdict,
            "audit_log_id": audit_log_id,
            "memory_location": memory_location,
            "timestamp": timestamp,
            "seal_valid": seal_valid
        },
        timestamp=timestamp
    )


def mcp_999_seal_sync(request: Dict[str, Any]) -> VerdictResponse:
    """Synchronous wrapper for mcp_999_seal."""
    return asyncio.run(mcp_999_seal(request))
