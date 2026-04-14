"""
agentzero/handoff/sealer.py — Cryptographic Handoff Sealer

HMAC Auth Proof of Constitutionality receipt generation
and verification for secure agent-to-agent handoffs.

DITEMPA BUKAN DIBERI — Forged, Not Given
Author: 888_VALIDATOR | Version: 2026.04.10-CANONICAL
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Receipt & Proof Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class HandoffReceipt:
    """Immutable cryptographic receipt for agent-to-agent handoff."""
    receipt_id: str
    source_agent: str
    source_role: str  # Trinity role: DELTA, OMEGA, PSI
    target_agent: str
    target_role: str
    action_summary: str
    action_digest: str  # SHA-256 of action payload
    verdict: str  # SEAL, SABAR, PARTIAL, VOID, HOLD_888
    auth_proof: str  # HMAC-based challenge-response proof (NOT zero-knowledge)
    merkle_leaf: str  # SHA-256 of this receipt
    merkle_root_before: str  # Vault root at handoff time
    merkle_root_after: Optional[str] = None
    tri_witness_score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    ttl_seconds: float = 300.0  # Receipt valid for 5 minutes
    signature: str = ""  # HMAC of entire receipt by source agent key

    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl_seconds

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, exclude_signature: bool = False) -> str:
        """Serialize to JSON. Optionally exclude signature for signing operations."""
        d = self.to_dict()
        if exclude_signature:
            d.pop("signature", None)
        return json.dumps(d, sort_keys=True)


@dataclass
class AuthProof:
    """HMAC-based challenge-response proof structure. NOT zero-knowledge."""
    agent_state_hash: str  # Hash of source agent constitutional state
    action_hash: str       # Hash of action being handed off
    trinity_role: str      # Source agent role
    witness_challenge: str # Deterministic challenge from system
    response: str          # HMAC response proving agent knows secret key

    def to_proof_string(self) -> str:
        return f"{self.agent_state_hash}:{self.action_hash}:{self.trinity_role}:{self.witness_challenge}:{self.response}"


class HandoffSealer:
    """
    Cryptographic handoff sealing using HMAC-based auth receipts
    and Merkle tree append-only ledger.

    This implementation uses HMAC challenge-response, NOT ZK-SNARKs.
    The proof demonstrates possession of a shared secret without
    transmitting the secret itself.
    """

    def __init__(self, vault_manager=None, secret_key: str = ""):
        """
        Args:
            vault_manager: VaultManager instance for merkle_root access
            secret_key: Shared secret for HMAC signatures (empty = disabled for testing)
        """
        self.vault = vault_manager
        self._secret = secret_key.encode() if secret_key else b"arifOS_handoff_secret"
        self._pending_receipts: list[HandoffReceipt] = []

    # ---------------------------------------------------------------------------
    # Receipt Generation
    # ---------------------------------------------------------------------------

    def seal_handoff(
        self,
        source_agent_id: str,
        source_role: str,
        target_agent_id: str,
        target_role: str,
        action_payload: dict[str, Any],
        action_summary: str,
        verdict: str,
        tri_witness_score: float = 0.0,
    ) -> HandoffReceipt:
        """
        Generate a cryptographically sealed handoff receipt.

        Flow:
        1. Compute action digest (SHA-256)
        2. Generate auth proof (HMAC-based)
        3. Compute merkle leaf from receipt fields
        4. Get current vault merkle root (for consistency)
        5. Sign receipt with source agent HMAC
        """
        import uuid as uuid_lib

        receipt_id = str(uuid_lib.uuid4())[:12]

        # Step 1: Action digest
        action_json = json.dumps(action_payload, sort_keys=True, default=str)
        action_digest = hashlib.sha256(action_json.encode()).hexdigest()

        # Step 2: auth proof (HMAC-based)
        merkle_root_before = self._get_vault_root()
        auth = self._generate_auth_proof(
            agent_id=source_agent_id,
            role=source_role,
            action_digest=action_digest,
            challenge=merkle_root_before,
        )

        # Step 3: Merkle leaf = SHA-256 of receipt (before signature)
        pre_receipt = HandoffReceipt(
            receipt_id=receipt_id,
            source_agent=source_agent_id,
            source_role=source_role,
            target_agent=target_agent_id,
            target_role=target_role,
            action_summary=action_summary,
            action_digest=action_digest,
            verdict=verdict,
            auth_proof=auth.to_proof_string(),
            merkle_leaf="",  # Filled below
            merkle_root_before=merkle_root_before,
            tri_witness_score=tri_witness_score,
        )
        merkle_leaf = self._compute_leaf(pre_receipt)
        pre_receipt.merkle_leaf = merkle_leaf

        # Step 4: Append to vault ledger (get new root)
        merkle_root_after = self._append_to_vault(pre_receipt)
        pre_receipt.merkle_root_after = merkle_root_after

        # Step 5: Sign with HMAC
        pre_receipt.signature = self._sign_receipt(pre_receipt)

        logger.info(
            f"[HandoffSealer] Sealed handoff {receipt_id}: "
            f"{source_agent_id}({source_role}) → {target_agent_id}({target_role}) "
            f"[{verdict}] leaf={merkle_leaf[:8]}..."
        )
        return pre_receipt

    def _generate_auth_proof(
        self,
        agent_id: str,
        role: str,
        action_digest: str,
        challenge: str,
    ) -> AuthProof:
        """
        Generate an HMAC-based auth proof.

        Uses HMAC challenge-response to prove the agent knows the
        shared secret without revealing the secret itself.
        This is NOT a zero-knowledge proof.
        """
        agent_state_str = f"{agent_id}:{role}:{action_digest}"
        agent_state_hash = hashlib.sha256(agent_state_str.encode()).hexdigest()

        # Witness challenge = vault merkle root at handoff time
        witness_challenge = challenge[:16]  # First 16 chars as challenge

        # Response = HMAC proving agent knows the secret key
        challenge_payload = f"{agent_state_hash}:{witness_challenge}:{action_digest}"
        response = hmac.new(self._secret, challenge_payload.encode(), hashlib.sha256).hexdigest()

        return AuthProof(
            agent_state_hash=agent_state_hash,
            action_hash=action_digest,
            trinity_role=role,
            witness_challenge=witness_challenge,
            response=response,
        )

    def _sign_receipt(self, receipt: HandoffReceipt, for_verification: bool = False) -> str:
        """
        HMAC sign the receipt.

        The signature is computed over the receipt EXCLUDING the signature field
        itself (breaking the circular dependency).

        Args:
            receipt: Receipt to sign
            for_verification: If True, receipt.signature is the stored value
                              being verified (excluded from hash input)
        """
        # Always exclude signature field to break circular dependency:
        # - When signing: signature field is empty "", we sign the content
        # - When verifying: signature field holds the value we need to verify against
        receipt_str = receipt.to_json(exclude_signature=True)
        sig = hmac.new(self._secret, receipt_str.encode(), hashlib.sha256).hexdigest()
        return sig

    def _compute_leaf(self, receipt: HandoffReceipt) -> str:
        """
        Compute SHA-256 merkle leaf from receipt identity fields only.

        Uses a fixed subset of fields that are stable and immutable:
        receipt_id + action_digest + source + target + verdict + timestamp.

        This avoids any serialization variation (float precision, field ordering)
        and ensures the leaf is deterministic across all verification nodes.
        """
        leaf_input = "|".join([
            receipt.receipt_id,
            receipt.action_digest,
            receipt.source_agent,
            receipt.target_agent,
            receipt.verdict,
            f"{receipt.timestamp:.6f}",
        ])
        return hashlib.sha256(leaf_input.encode()).hexdigest()

    def _get_vault_root(self) -> str:
        """Get current vault merkle root."""
        if self.vault is not None:
            try:
                return self.vault.get_current_root()
            except Exception:
                pass
        # Fallback: deterministic placeholder root
        return hashlib.sha256(b"arifOS_vault_root").hexdigest()

    def _append_to_vault(self, receipt: HandoffReceipt) -> str:
        """Append receipt leaf to vault ledger, return new root."""
        self._pending_receipts.append(receipt)
        if self.vault is not None:
            try:
                return self.vault.append_handoff_leaf(receipt.merkle_leaf)
            except Exception:
                pass
        # Fallback: compute incremental root
        root = self._get_vault_root()
        for r in self._pending_receipts:
            root = hashlib.sha256((root + r.merkle_leaf).encode()).hexdigest()
        return root

    # ---------------------------------------------------------------------------
    # Receipt Verification
    # ---------------------------------------------------------------------------

    def verify_handoff(self, receipt: HandoffReceipt) -> tuple[bool, str]:
        """
        Verify a handoff receipt.

        Checks:
        1. Receipt not expired
        2. HMAC signature valid
        3. Auth proof structurally valid
        4. Merkle root consistency

        Returns: (is_valid, reason)
        """
        # 1. Expiry check
        if receipt.is_expired():
            return False, f"Receipt expired (age={(time.time()-receipt.timestamp):.1f}s)"

        # 2. Signature verification
        expected_sig = self._sign_receipt(receipt, for_verification=True)
        if not hmac.compare_digest(receipt.signature, expected_sig):
            return False, "HMAC signature mismatch"

        # 3. Auth proof verification
        auth_valid, auth_reason = self._verify_auth_proof(receipt.auth_proof, receipt.action_digest)
        if not auth_valid:
            return False, f"Auth proof verification failed: {auth_reason}"

        # 4. Merkle leaf integrity
        computed_leaf = self._compute_leaf(receipt)
        if not hmac.compare_digest(computed_leaf, receipt.merkle_leaf):
            return False, "Merkle leaf mismatch"

        # 5. Merkle root progression (if vault available)
        if self.vault is not None and receipt.merkle_root_before:
            try:
                if not self.vault.verify_root_exists(receipt.merkle_root_before):
                    return False, f"Vault root '{receipt.merkle_root_before[:8]}...' no longer exists"
            except Exception:
                pass  # Vault not available — skip this check

        return True, "verified"

    def _verify_auth_proof(self, proof_str: str, action_digest: str) -> tuple[bool, str]:
        """Verify the HMAC auth proof structure."""
        try:
            parts = proof_str.split(":")
            if len(parts) != 5:
                return False, f"Invalid proof format: expected 5 parts, got {len(parts)}"

            agent_state_hash, proof_action_hash, role, challenge, response = parts

            # Verify action digest matches
            if not hmac.compare_digest(proof_action_hash, action_digest):
                return False, "Action digest mismatch in proof"

            # Verify challenge-response (proves agent had access to secret)
            challenge_payload = f"{agent_state_hash}:{challenge}:{proof_action_hash}"
            expected_response = hmac.new(self._secret, challenge_payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(response, expected_response):
                return False, "Challenge-response verification failed"

            return True, "valid"
        except Exception as e:
            return False, f"Proof parsing error: {e}"

    # ---------------------------------------------------------------------------
    # Query Interface
    # ---------------------------------------------------------------------------

    def get_handoff_history(self, agent_id: str) -> list[HandoffReceipt]:
        """Return all handoff receipts involving this agent (source or target)."""
        return [
            r for r in self._pending_receipts
            if r.source_agent == agent_id or r.target_agent == agent_id
        ]

    def get_pending_count(self) -> int:
        return len(self._pending_receipts)
