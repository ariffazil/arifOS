"""
Stage 999: SEAL - Memory Consolidation (Cooling)
Scientific Principle: Hippocampal-Cortical Consolidation
Function: Moves 'Hot' state (Labile) to 'Cool' state (Stable).

This module provides the pipeline-compatible execute_stage function
that wraps the SEAL999 class for integration with the metabolic loop.

Hardening:
- Phoenix Cooling Protocol (72h truth stabilization)
- Merkle-sealed hash chain integrity
- Eureka Sieve verdict routing
- ZKPC proof generation
"""
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib

from .vault import SEAL999
from .state import VaultEntry, VaultConfig


# Singleton SEAL999 instance for pipeline use
_seal999_instance: Optional[SEAL999] = None


def get_seal999() -> SEAL999:
    """Get or create the singleton SEAL999 instance."""
    global _seal999_instance
    if _seal999_instance is None:
        _seal999_instance = SEAL999()
    return _seal999_instance


def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 999: SEAL - Constitutional Memory Consolidation

    The final stage of the metabolic loop. Seals the judgment from Stage 888/889
    into the immutable ledger with Merkle proofs and Phoenix cooling.

    Eureka Sieve Routing:
    - SEAL + High Genius (>0.85) -> L5_ETERNAL (CCC_CANON)
    - SEAL -> L2_PHOENIX (72h cooling)
    - PARTIAL -> L4_MONTHLY (BBB_LEDGER)
    - SABAR -> L3_WEEKLY (cooling)
    - VOID -> DISCARD (never stored)

    Args:
        context: Pipeline context containing:
            - session_id: Session identifier
            - verdict: Constitutional verdict (SEAL/PARTIAL/VOID/SABAR)
            - proof_hash: From Stage 889
            - floor_scores: All 13 floor scores
            - forge_result: From Stage 777

    Returns:
        Updated context with:
            - stage: "999"
            - merkle_root: Seal of the entry
            - cooling_tier: Assigned memory tier
            - seal_timestamp: When sealed
    """
    context["stage"] = "999"

    seal999 = get_seal999()

    # Extract data from context
    session_id = context.get("session_id", f"session_{datetime.utcnow().isoformat()}")
    verdict = context.get("verdict", "PARTIAL")
    proof_hash = context.get("proof_hash")
    floor_scores = context.get("floor_scores", {})

    # Only seal if we have a valid proof from Stage 889
    if not proof_hash:
        context["seal_status"] = "SKIPPED"
        context["seal_reason"] = "No proof_hash from Stage 889"
        return context

    # Create vault entry from context
    entry = VaultEntry(
        session_id=session_id,
        stage=999,
        timestamp=datetime.utcnow(),
        verdict=verdict,
        floor_scores=floor_scores,
        payload={
            "proof_hash": proof_hash,
            "forge_result": context.get("forge_result"),
            "judgment": context.get("judgment_result"),
            "thermodynamic_state": {
                "entropy": context.get("entropy", 0.0),
                "peace_squared": context.get("peace_squared", 1.0),
                "humility": context.get("humility", 0.04),
            },
        },
    )

    try:
        # Seal the entry
        merkle_root = seal999.seal_entry(entry)

        context["merkle_root"] = merkle_root
        context["cooling_tier"] = entry.cooling_tier
        context["seal_timestamp"] = entry.timestamp.isoformat()
        context["seal_status"] = "SEALED"

        # For VOID verdicts, note that it was discarded
        if entry.cooling_tier == -1:
            context["seal_status"] = "DISCARDED"
            context["seal_reason"] = "VOID verdicts are not persisted"

    except Exception as e:
        context["seal_status"] = "ERROR"
        context["seal_error"] = str(e)

    # Reset transient state for next cycle (homeostasis)
    # Keep session persistence, clear temporary computation state
    transient_keys = [
        "sense_result",
        "reflect_result",
        "reason_result",
        "evidence_result",
        "empathize_result",
        "align_result",
    ]
    for key in transient_keys:
        context.pop(key, None)

    return context


# Alias for backward compatibility
vault_999 = execute_stage
