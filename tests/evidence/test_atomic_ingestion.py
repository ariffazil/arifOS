"""
Tests for v45 EvidencePack (Atomic Ingestion)
Strict schema validation and firewall isolation rules.
"""
import pytest
from pydantic import ValidationError
from arifos_core.enforcement.judiciary.semantic_firewall import SemanticFirewall, ApexTelemetry
from arifos_core.enforcement.evidence.evidence_pack import EvidencePack

# --- Test Data ---
VALID_HASH = "a" * 64
VALID_URI = "https://example.com/source"

from arifos_core.enforcement.evidence.evidence_pack import EvidencePack
from tests.utils import make_valid_evidence_pack, VALID_HASH

def test_atomic_reject_incomplete_pack():
    """EvidencePack must fail validation if required fields are missing."""
    # Using Pydantic, missing required fields raises ValidationError
    with pytest.raises(ValidationError):
        EvidencePack(
            query_hash=VALID_HASH, # Valid Format
            conflict_score=0.0
            # Missing coverage, freshness, etc.
        )

def test_coverage_gate_blocks_seal():
    """Logic gate: If coverage < 1.0, downstream logic must know."""
    # This test verifies the ATTRIBUTE exists and validation passes 0-1 range.
    # The actual blocking logic is in ConflictRouter/Firewall, butPack must hold the truth.
    pack = make_valid_evidence_pack(
        coverage_pct=0.99 # Not 1.0
    )
    assert pack.coverage_pct == 0.99

def test_source_uris_never_cross_firewall():
    """The EvidencePack holds URIs, but the Firewall strips them."""
    pack = make_valid_evidence_pack(
        source_uris=["https://dangerous.semantic.content/leak"],
        jargon_density=0.1
    )
    
    # Pass through firewall
    # Mock metrics/sentinel
    metrics = {"truth": 1.0}
    flags = []
    
    telemetry = SemanticFirewall.sanitize(metrics, pack, flags)
    
    # Inspect Telemetry - Strict Whitelist Check
    # Ensure source_uris is NOT an attribute of telemetry
    assert not hasattr(telemetry, "source_uris")
    
    # Extra paranoid: serialize and search
    json_dump = telemetry.compute_hash() # Or simple str() if repr exposes fields
    # Since compute_hash only dumps defined fields...
    # Let's inspect vars() directly
    vars_dict = vars(telemetry)
    for key, val in vars_dict.items():
        if isinstance(val, str):
            assert "dangerous" not in val, f"Leak detected in field {key}"
        if isinstance(val, list):
            for item in val:
                 assert "dangerous" not in str(item), f"Leak detected in list {key}"

def test_hash_chain_strictness():
    """Hashes must be strict hex/base64, no whitespace."""
    # Bad hash with space
    with pytest.raises(ValidationError):
        EvidencePack(
            query_hash="q 123", # Space illegal
            coverage_pct=1.0,
            conflict_score=0.0,
            conflict_flag=False,
            freshness_timestamp=1000,
            freshness_score=1.0,
            hash_chain_provenance=[VALID_HASH],
            source_uris=[],
            jargon_density=0.0
        )
    
    # Chain provenance bad hash
    with pytest.raises(ValidationError):
        EvidencePack(
            query_hash=VALID_HASH, # Valid hash to ensure we test provenance failure
            coverage_pct=1.0,
            conflict_score=0.0,
            conflict_flag=False,
            freshness_timestamp=1000,
            freshness_score=1.0,
            hash_chain_provenance=["bad hash with space"],
            source_uris=[],
            jargon_density=0.0
        )
