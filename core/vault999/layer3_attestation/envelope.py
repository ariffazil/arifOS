"""
Layer 3: Execution Attestation — Signed Execution Envelopes

If attacker gains MCP control, they must not gain execution authority.

All execution requires cryptographic attestation from 888_JUDGE or delegated authority.
Compromise of MCP ≠ Execution authority.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import nacl.encoding

# Ed25519 for signatures
import nacl.signing


class ExecutionStatus(Enum):
    PENDING = "pending"         # Awaiting signature
    SIGNED = "signed"           # Signed by authority
    VERIFIED = "verified"       # Signature verified
    EXECUTED = "executed"       # Successfully executed
    REJECTED = "rejected"       # Verification failed
    EXPIRED = "expired"         # Nonce too old
    REPLAY = "replay"           # Nonce already used


@dataclass
class ExecutionEnvelope:
    """
    Cryptographically signed execution payload.
    
    Without a valid signature from an authorized key, execution is VOID.
    This ensures that even if MCP is compromised, execution requires
    access to the signing keys (stored in KMS/HSM, not on VPS).
    """
    
    # Payload
    operation: str              # What to execute
    payload: dict[str, Any]     # Operation parameters
    target: str                 # Target system (forge, mcp, etc.)
    
    # Authorization
    authority: str              # Who is authorizing (888_JUDGE, AGENT_X)
    delegated_from: str | None = None  # If delegated, original authority
    
    # Temporal constraints
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    
    # Anti-replay
    nonce: str = field(default_factory=lambda: secrets.token_hex(16))
    
    # Signature (filled after creation)
    signature: str | None = None
    public_key: str | None = None
    
    # Status tracking
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    def canonical_payload(self) -> bytes:
        """
        Generate canonical representation for signing.
        
        Only these fields are signed — adding fields requires re-signing.
        """
        content = {
            "operation": self.operation,
            "payload": self.payload,
            "target": self.target,
            "authority": self.authority,
            "delegated_from": self.delegated_from,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "nonce": self.nonce,
        }
        return json.dumps(content, sort_keys=True).encode()
    
    def compute_hash(self) -> str:
        """Compute hash of envelope (for reference/logging)."""
        return hashlib.sha256(self.canonical_payload()).hexdigest()[:32]
    
    def sign(self, signing_key: nacl.signing.SigningKey) -> ExecutionEnvelope:
        """Sign the envelope with Ed25519."""
        signature = signing_key.sign(self.canonical_payload())
        self.signature = signature.signature.hex()
        self.public_key = signing_key.verify_key.encode().hex()
        self.status = ExecutionStatus.SIGNED
        return self
    
    def verify(self, public_key: nacl.signing.VerifyKey | None = None) -> bool:
        """
        Verify envelope signature.
        
        If public_key not provided, will attempt to verify against
        registered authority keys.
        """
        if not self.signature or not self.public_key:
            self.status = ExecutionStatus.REJECTED
            return False
        
        # Check expiration
        if datetime.utcnow() > self.expires_at:
            self.status = ExecutionStatus.EXPIRED
            return False
        
        try:
            if public_key is None:
                # Load from registry
                public_key = self._load_authority_key(self.authority)
            
            signature_bytes = bytes.fromhex(self.signature)
            public_key.verify(self.canonical_payload(), signature_bytes)
            
            self.status = ExecutionStatus.VERIFIED
            return True
            
        except Exception:
            self.status = ExecutionStatus.REJECTED
            return False
    
    def _load_authority_key(self, authority: str) -> nacl.signing.VerifyKey:
        """Load public key for authority from environment or registry file."""
        import os

        env_var = f"ARIFOS_{authority.upper()}_PUBLIC_KEY"
        key_hex = os.getenv(env_var)
        if not key_hex:
            registry_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "..",
                "..",
                "..",
                ".arifos",
                "keys",
                f"{authority.lower()}.pub",
            )
            if os.path.exists(registry_path):
                with open(registry_path) as f:
                    key_hex = f.read().strip()
        if not key_hex or len(key_hex) != 64:
            raise RuntimeError(
                f"No valid public key found for authority {authority}. "
                f"Set {env_var} or create registry key file."
            )
        return nacl.signing.VerifyKey(bytes.fromhex(key_hex))
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "payload": self.payload,
            "target": self.target,
            "authority": self.authority,
            "delegated_from": self.delegated_from,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "nonce": self.nonce,
            "signature": self.signature,
            "public_key": self.public_key,
            "status": self.status.value,
            "hash": self.compute_hash(),
        }


class NonceRegistry:
    """
    Tracks used nonces to prevent replay attacks.
    
    Even if an attacker steals a valid envelope, they cannot replay it
    because the nonce will already be marked as used.
    """
    
    def __init__(self, ttl_hours: int = 24):
        self._used_nonces: set[str] = set()
        self._nonce_timestamps: dict[str, datetime] = {}
        self._ttl = timedelta(hours=ttl_hours)
    
    def check_and_record(self, nonce: str) -> bool:
        """
        Check if nonce is available and mark it used.
        
        Returns True if nonce was available (first use).
        Returns False if nonce already used (replay attempt).
        """
        self._cleanup_expired()
        
        if nonce in self._used_nonces:
            return False
        
        self._used_nonces.add(nonce)
        self._nonce_timestamps[nonce] = datetime.utcnow()
        return True
    
    def _cleanup_expired(self):
        """Remove expired nonces to prevent unbounded growth."""
        now = datetime.utcnow()
        expired = [
            nonce for nonce, timestamp in self._nonce_timestamps.items()
            if now - timestamp > self._ttl
        ]
        for nonce in expired:
            self._used_nonces.discard(nonce)
            del self._nonce_timestamps[nonce]


class ExecutionAttestor:
    """
    Manages execution attestation.
    
    Keys are stored outside the VPS (KMS/HSM).
    The attestor communicates with the key storage to sign envelopes.
    """
    
    def __init__(self, kms_endpoint: str | None = None):
        self.kms_endpoint = kms_endpoint
        self.nonce_registry = NonceRegistry()
        self._delegation_chain: dict[str, str] = {}  # agent -> delegator
    
    async def create_envelope(
        self,
        operation: str,
        payload: dict[str, Any],
        authority: str = "888_JUDGE",
        target: str = "forge",
        ttl_minutes: int = 60,
    ) -> ExecutionEnvelope:
        """Create a new execution envelope."""
        envelope = ExecutionEnvelope(
            operation=operation,
            payload=payload,
            target=target,
            authority=authority,
            expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
        )
        return envelope
    
    async def sign_envelope(self, envelope: ExecutionEnvelope) -> ExecutionEnvelope:
        """
        Sign envelope using KMS/HSM.
        
        The private key NEVER touches the VPS.
        """
        if self.kms_endpoint:
            # Call out to KMS for signing
            signature = await self._kms_sign(
                envelope.canonical_payload(),
                envelope.authority
            )
            envelope.signature = signature
            envelope.status = ExecutionStatus.SIGNED
        else:
            # Fallback: local signing (development only)
            signing_key = nacl.signing.SigningKey.generate()
            envelope.sign(signing_key)
        
        return envelope
    
    async def verify_and_execute(
        self,
        envelope: ExecutionEnvelope,
        executor: callable,
    ) -> dict[str, Any]:
        """
        Verify envelope and execute if valid.
        
        This is the critical security gate.
        """
        # 1. Check nonce (replay protection)
        if not self.nonce_registry.check_and_record(envelope.nonce):
            envelope.status = ExecutionStatus.REPLAY
            return {
                "success": False,
                "error": "REPLAY_ATTACK",
                "message": "Nonce already used — possible replay attack",
            }
        
        # 2. Verify signature
        if not envelope.verify():
            return {
                "success": False,
                "error": "INVALID_SIGNATURE",
                "message": f"Envelope status: {envelope.status.value}",
            }
        
        # 3. Check authorization chain
        if not self._verify_authority_chain(envelope.authority):
            return {
                "success": False,
                "error": "UNAUTHORIZED",
                "message": f"Authority {envelope.authority} not valid",
            }
        
        # 4. Execute
        try:
            result = executor(envelope.payload)
            envelope.status = ExecutionStatus.EXECUTED
            return {
                "success": True,
                "result": result,
                "envelope_hash": envelope.compute_hash(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": "EXECUTION_FAILED",
                "message": str(e),
            }
    
    async def _kms_sign(self, payload: bytes, authority: str) -> str:
        """Request signature from KMS or fall back to HMAC with explicit dev warning."""
        import hashlib
        import hmac
        import os

        if self.kms_endpoint:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.kms_endpoint,
                    json={"payload": payload.hex(), "authority": authority},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"KMS signing failed: {resp.status}")
                    data = await resp.json()
                    return data["signature"]

        secret = os.getenv("ARIFOS_KMS_SECRET")
        if not secret:
            raise RuntimeError(
                "No KMS endpoint configured and ARIFOS_KMS_SECRET not set. "
                "Cannot sign execution envelope."
            )
        logger.warning(
            "_kms_sign using HMAC dev fallback — "
            "private key is derived from environment, not a secure enclave"
        )
        return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    
    def _verify_authority_chain(self, authority: str) -> bool:
        """Verify authority is valid or has valid delegation."""
        if authority == "888_JUDGE":
            return True
        
        # Check delegation chain
        delegator = self._delegation_chain.get(authority)
        if delegator:
            return self._verify_authority_chain(delegator)
        
        return False
    
    def delegate_authority(self, from_authority: str, to_agent: str):
        """
        Delegate authority from one entity to another.
        
        Creates chain: to_agent -> from_authority -> ... -> 888_JUDGE
        """
        self._delegation_chain[to_agent] = from_authority


__all__ = [
    "ExecutionStatus",
    "ExecutionEnvelope",
    "NonceRegistry",
    "ExecutionAttestor",
]
