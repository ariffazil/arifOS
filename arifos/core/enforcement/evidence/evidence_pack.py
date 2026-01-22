"""
arifOS v45 - EvidencePack Schema (Sovereign Witness)
Strict Pydantic contract for evidence handling.
"""

from typing import List, Optional
import hashlib
import uuid
from pydantic import BaseModel, Field, validator
import re

# Strict Hash Regex (Hex only for simplicity, length 6-128 for flexibility, no spaces)
HASH_REGEX = re.compile(r"^[a-fA-F0-9\-_]{6,128}$")


class EvidenceSource(BaseModel):
    """Receipt for a single source of evidence."""

    source_id: str
    doc_hash: str
    timestamp: float
    spans: List[str] = Field(default_factory=list)
    confidence: float = 1.0


class EvidencePack(BaseModel):
    """
    v45 EvidencePack - The atomic unit of truth.
    Holds provenance, coverage stats, and conflict scores.
    NO SEMANTIC CONTENT in the top-level routing attributes.
    """

    pack_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_hash: str
    sources: List[EvidenceSource] = Field(default_factory=list)

    # Physics Attributes (Required)
    coverage_pct: float = Field(..., ge=0.0, le=1.0)
    conflict_score: float = Field(..., ge=0.0, le=1.0)
    freshness_score: float = Field(..., ge=0.0, le=1.0)
    jargon_density: float = Field(..., ge=0.0, le=1.0)

    # v45 New Fields
    conflict_flag: bool
    freshness_timestamp: float  # Unix timestamp
    hash_chain_provenance: List[str] = Field(default_factory=list)
    source_uris: List[str] = Field(default_factory=list)  # Semantics Allowed HERE (URIs)

    # Optional Cryptography
    merkle_root: Optional[str] = None

    @validator("query_hash")
    def validate_hash_format(cls, v):
        if not HASH_REGEX.match(v):
            raise ValueError(f"Hash contains invalid characters or format: {v}")
        return v

    @validator("hash_chain_provenance", each_item=True)
    def validate_provenance_hashes(cls, v):
        if not HASH_REGEX.match(v):
            raise ValueError(f"Provenance hash invalid: {v}")
        return v

    @validator("source_uris")
    def validate_uri_list_size(cls, v):
        if len(v) > 32:
            raise ValueError("Too many source URIs (limit 32)")
        return v

    # Validation Rules Logic Gates (Implicit via Validator checking constraints?)
    # "If coverage_pct < 1.0 -> cannot SEAL" is a routing rule, not object validity rule.
    # But "If conflict_flag == True" is basic validity of the pack state.

    def compute_pack_hash(self) -> str:
        """Deterministic hash of the evidence pack attributes."""
        # Note: Exclude source_uris from hash to keep hash purely physics/provenance?
        # No, provenance includes URIs content usually.
        # But for firewall safety, maybe we hash them?
        # Let's include everything structural.

        payload_parts = [
            self.query_hash,
            f"{self.coverage_pct:.4f}",
            f"{self.conflict_score:.4f}",
            str(self.conflict_flag),
            f"{self.freshness_score:.4f}",
            f"{self.freshness_timestamp:.1f}",
            f"{self.jargon_density:.4f}",
        ]

        # Provenance Hashes
        payload_parts.extend(sorted(self.hash_chain_provenance))

        # Source URIs (Hashed individually then sorted to avoid semantic leak in payload string?)
        # Use content of URIs to secure pack identity
        uri_hashes = [hashlib.sha256(u.encode()).hexdigest() for u in self.source_uris]
        payload_parts.extend(sorted(uri_hashes))

        payload = ":".join(payload_parts)
        return hashlib.sha256(payload.encode()).hexdigest()
