"""
VAULT999 Service Models
WELD-003: Unified Merkle-chained vault ledger
DITEMPA BUKAN DIBERI
"""

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class VaultEntry(BaseModel):
    """Input: write a governed action to the unified ledger.

    Note: prev_hash is filled by the server from the last chain entry.
    Client should NOT provide it — server manages chain continuity.
    """
    session_id: str
    domain: Literal["GEOX", "WEALTH", "ARIFOS", "A-FORGE"]
    tool: str
    verdict: str = Field(description="PROCEED | SEAL | HOLD | VOID")
    ac_risk: float
    claim_tag: str
    payload_hash: str = Field(description="SHA-256 of payload content")
    prev_hash: str = Field(default="", description="Filled by server — do not provide")
    floor_violations: list[str] = []
    epistemic: str = "ESTIMATE"
    witness_human: str = "ARIF"
    witness_ai: str = "AAA-AGENT"
    witness_earth: str = "SEISMIC"


class ChainedEntry(BaseModel):
    """Output: vault entry with computed chain_hash."""
    session_id: str
    epoch: str
    domain: str
    tool: str
    verdict: str
    ac_risk: float
    claim_tag: str
    payload_hash: str
    prev_hash: str
    chain_hash: str = Field(description="SHA-256(prev_hash + payload_hash)")
    timestamp: datetime
    floor_violations: list[str]
    seal_id: str


class SessionChain(BaseModel):
    """Full chain for a session — cross-domain audit trace."""
    session_id: str
    entries: list[ChainedEntry]
    chain_integrity: bool = Field(description="True if chain is unbroken")