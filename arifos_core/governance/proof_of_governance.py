"""
arifOS v45 - Proof of Governance (Sovereign Witness)
Thin wiring layer for SealReceipt assembly, signing, and ledger integration.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import hashlib
import json
import uuid
import time

from arifos_core.judiciary.witness_council import ConsensusResult, Verdict
from arifos_core.governance.merkle_ledger import MerkleLedger, MerkleEntry
from arifos_core.governance.sovereign_signature import SovereignSigner, SignatureVerifier


class SealReceipt(BaseModel):
    """
    The Receipt of Governance.
    Atomic proof of a finalized decision.
    """

    schema_version: str = "45.0"
    trace_id: str
    timestamp: float
    verdict: str  # Enum string

    # Provenance Hashes
    pack_hash: str
    consensus_hash: str  # Hash of ConsensusResult details/score
    merkle_root_snapshot: str

    # Numeric Summary
    council_summary: Dict[str, float]

    def compute_receipt_hash(self) -> str:
        """Deterministic hash of the receipt content."""
        # Pydantic v2/v1 compatibility layer for deterministic JSON
        try:
            data = self.model_dump()
        except AttributeError:
            data = self.dict()

        # Sort keys is critical for hash stability
        payload = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()


class ProofOfGovernance:
    """
    Orchestrator for governance proofs.
    Wraps MerkleLedger and SovereignSigner.
    """

    def __init__(self):
        # Initialize ledger and signer
        # In a real app, these might be singletons or injected
        self.ledger = MerkleLedger()
        self.signer = SovereignSigner()

    @staticmethod
    def assemble_receipt(
        trace_id: str,
        timestamp: float,
        verdict: Verdict,
        pack_hash: str,
        consensus_result: ConsensusResult,
        merkle_root: str,
    ) -> SealReceipt:
        """Construct the immutable receipt."""

        # Hash consensus result to keep receipt clean of text details
        c_payload = f"{consensus_result.global_verdict}:{consensus_result.consensus_score}:{consensus_result.dissent_triggered}"
        consensus_hash = hashlib.sha256(c_payload.encode()).hexdigest()

        return SealReceipt(
            trace_id=trace_id,
            timestamp=timestamp,
            verdict=verdict.value,
            pack_hash=pack_hash,
            consensus_hash=consensus_hash,
            merkle_root_snapshot=merkle_root,
            council_summary={
                "score": consensus_result.consensus_score,
                # "quorum": 3.0 # Implicit in v45 config
            },
        )

    @classmethod
    def sign_receipt(cls, receipt: SealReceipt, tier: str = "T1") -> str:
        """
        Sign the receipt hash.
        Policy: T4 requires signature. T1-T3 optional?
        Implementation: Always sign if requested, but check T4 permissions in Signer.
        """
        signer = SovereignSigner()  # Ephemeral or loaded key
        receipt_hash = receipt.compute_receipt_hash()

        # SovereignSigner handles T4 lock checks internally if we pass tier
        try:
            signature = signer.sign_verdict(receipt_hash, tier=tier)
            return signature
        except Exception as e:
            # If not T4 and mock fails?
            if tier == "T4":
                raise e
            return "UNSIGNED"

    @classmethod
    def verify_receipt_signature(cls, receipt: SealReceipt, signature: str) -> bool:
        """Verify signature against receipt hash."""
        signer = SovereignSigner()
        pub_key = signer.get_public_key()
        receipt_hash = receipt.compute_receipt_hash()
        return SignatureVerifier.verify(pub_key, receipt_hash, signature)

    def append_to_ledger(self, receipt: SealReceipt) -> str:
        """
        Append receipt trace to Merkle Ledger.
        Returns the new Merkle Root.
        """
        # Create Merkle Entry payload
        try:
            data = receipt.model_dump()
        except AttributeError:
            data = receipt.dict()

        entry_payload = json.dumps(data, sort_keys=True, default=str)

        self.ledger.append_entry(entry_payload)
        return self.ledger.get_root_hash()

    def get_current_root(self) -> str:
        return self.ledger.get_root_hash()
