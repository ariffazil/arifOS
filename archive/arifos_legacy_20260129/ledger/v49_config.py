"""
v49 Ledger Configuration
Maps v49 canonical paths to existing ledger implementation.

Version: v49.0.2
Authority: 888 Judge (APEX)
"""

from pathlib import Path
from typing import Optional

# v49 Canonical Paths (per 000_ARCHITECTURE.md §3)
V49_LEDGER_PATH = Path("vault_999/BBB_LEDGER/LAYER_3_AUDIT/constitutional_ledger.jsonl")
V49_MERKLE_PATH = Path("vault_999/INFRASTRUCTURE/zkpc_receipts/merkle_roots.jsonl")
V49_HEAD_STATE_PATH = Path("vault_999/BBB_LEDGER/LAYER_3_AUDIT/head_state.json")
V49_ARCHIVE_PATH = Path("vault_999/BBB_LEDGER/LAYER_2_WORKING/archive/")
V49_HASH_CHAIN_PATH = Path("vault_999/BBB_LEDGER/LAYER_3_AUDIT/hash_chain.txt")


def get_v49_ledger_config():
    """
    Get LedgerConfigV37 configured for v49 canonical paths.

    Returns:
        LedgerConfigV37: Configured for v49 vault_999 structure
    """
    from arifos.core.memory.ledger.cooling_ledger import LedgerConfigV37

    return LedgerConfigV37(
        ledger_path=V49_LEDGER_PATH,
        head_state_path=V49_HEAD_STATE_PATH,
        archive_path=V49_ARCHIVE_PATH,
        hot_segment_days=7,
        hot_segment_max_entries=10000,
        fail_behavior="SABAR_HOLD_WITH_LOG"  # v49 constitutional requirement
    )


def init_v49_ledger():
    """
    Initialize v49 ledger infrastructure.

    Creates:
    - vault_999/BBB_LEDGER/LAYER_3_AUDIT/ structure
    - Empty constitutional_ledger.jsonl
    - Genesis hash_chain.txt
    - head_state.json

    Returns:
        CoolingLedgerV37: Initialized ledger instance
    """
    from arifos.core.memory.ledger.cooling_ledger import CoolingLedgerV37

    config = get_v49_ledger_config()

    # Ensure directories exist
    config.ledger_path.parent.mkdir(parents=True, exist_ok=True)
    config.archive_path.mkdir(parents=True, exist_ok=True)
    V49_MERKLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Create empty ledger if doesn't exist
    if not config.ledger_path.exists():
        config.ledger_path.write_text("")

    # Initialize hash chain
    if not V49_HASH_CHAIN_PATH.exists():
        V49_HASH_CHAIN_PATH.write_text("GENESIS")

    # Create ledger instance (will load or create head_state.json)
    ledger = CoolingLedgerV37(config)

    return ledger


def write_constitutional_entry(
    verdict: str,
    floor_scores: dict,
    trinity_indices: Optional[dict] = None,
    session_id: Optional[str] = None,
    cooling_tier: int = 0
):
    """
    Write a constitutional verdict to the v49 audit trail.

    Args:
        verdict: SEAL|PARTIAL|VOID|SABAR|888_HOLD
        floor_scores: F1-F13 floor scores (dict)
        trinity_indices: Optional Ψ, G, C_dark metrics
        session_id: Optional CLIP_YYYYMMDD_NNN format
        cooling_tier: Phoenix-72 tier (0/1/2/3)

    Returns:
        Tuple of (success: bool, entry_hash: str, error: Optional[str])
    """
    import uuid
    from datetime import datetime, timezone

    ledger = init_v49_ledger()

    # Build entry per v49 schema
    entry = {
        "entry_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id or f"CLIP_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:3]}",
        "verdict": verdict,
        "floor_scores": floor_scores,
        "trinity_indices": trinity_indices or {},
        "zkpc_receipt": {
            "merkle_root": "PLACEHOLDER",  # TODO: Implement actual zkPC
            "proof_type": "Merkle",
            "witness_consensus": floor_scores.get("F8_genius", 0.0)
        },
        "cooling_tier": cooling_tier,
    }

    # Append via v37 ledger (handles hash-chain automatically)
    result = ledger.append_v37(entry)

    if result.success:
        # Update hash_chain.txt with latest hash
        V49_HASH_CHAIN_PATH.write_text(result.entry_hash or "")

        return (True, result.entry_hash, None)
    else:
        return (False, None, result.error)


__all__ = [
    "V49_LEDGER_PATH",
    "V49_MERKLE_PATH",
    "V49_HEAD_STATE_PATH",
    "V49_ARCHIVE_PATH",
    "V49_HASH_CHAIN_PATH",
    "get_v49_ledger_config",
    "init_v49_ledger",
    "write_constitutional_entry",
]
