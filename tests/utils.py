"""
Shared utilities for v45 tests.
"""
import time
import uuid
import hashlib
from arifos.core.enforcement.evidence.evidence_pack import EvidencePack

VALID_HASH = "a" * 64

def make_valid_evidence_pack(**overrides) -> EvidencePack:
    """
    Constructs a minimal valid v45 EvidencePack.
    All required fields are populated with safe defaults.
    """
    defaults = {
        "query_hash": VALID_HASH,
        "coverage_pct": 1.0,
        "conflict_score": 0.0,
        "conflict_flag": False,
        "freshness_timestamp": time.time(),
        "freshness_score": 1.0,
        "hash_chain_provenance": [VALID_HASH],
        "source_uris": [],
        "jargon_density": 0.0
    }
    # Update defaults with overrides
    config = defaults.copy()
    config.update(overrides)
    
    return EvidencePack(**config)
