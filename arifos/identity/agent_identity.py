"""
agent_identity.py — Ed25519 Agent Identity
════════════════════════════════════════════

Cryptographic identity for every federation agent.
One keypair per agent. Private key never leaves disk (mode 600).
Public key registered in IdentityRegistry.

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import blake3
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey


@dataclass
class AgentIdentity:
    """Cryptographic identity for a federation agent.

    Each agent gets one Ed25519 keypair at birth. The private key
    is stored with mode 600 and never transmitted. The public key
    is registered in the IdentityRegistry for verification.

    Attributes:
        agent_id: Unique agent identifier (e.g. "opencode")
        actor_id: Actor identifier (e.g. "opencode/FI-001")
        ed25519_pubkey_hex: Public key as hex string (64 chars)
        bound_to: Sovereign anchor (e.g. "arif-fazil/F13")
        capabilities: Allowed action classes
        max_blast_radius: Maximum autonomy tier (T0-T3)
        created_at: ISO 8601 timestamp
        fingerprint: BLAKE3 hash of identity fields
    """

    agent_id: str
    actor_id: str
    ed25519_pubkey_hex: str
    bound_to: str
    capabilities: list[str] = field(default_factory=lambda: ["OBSERVE", "REASON"])
    max_blast_radius: str = "T2"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    fingerprint: str = ""

    # Private key is NOT stored in this dataclass — it lives in a separate file
    _private_key: SigningKey | None = field(default=None, repr=False, compare=False)

    # ── Factory: Create new identity with fresh keypair ──────────────────

    @classmethod
    def create(
        cls,
        agent_id: str,
        *,
        actor_id: str | None = None,
        bound_to: str = "arif-fazil/F13",
        capabilities: list[str] | None = None,
        max_blast_radius: str = "T2",
    ) -> "AgentIdentity":
        """Generate a new Ed25519 keypair and create agent identity."""
        keypair = SigningKey.generate()
        pubkey_hex = keypair.verify_key.encode().hex()

        identity = cls(
            agent_id=agent_id,
            actor_id=actor_id or f"{agent_id}/FI-???",
            ed25519_pubkey_hex=pubkey_hex,
            bound_to=bound_to,
            capabilities=capabilities or ["OBSERVE", "REASON", "EXECUTE_REVERSIBLE"],
            max_blast_radius=max_blast_radius,
        )
        identity._private_key = keypair
        identity.fingerprint = identity.compute_fingerprint()
        return identity

    # ── Load / Save ─────────────────────────────────────────────────────

    @classmethod
    def load(
        cls, identity_path: str | Path, private_key_path: str | Path | None = None
    ) -> "AgentIdentity":
        """Load identity from JSON file, optionally with private key."""
        with open(identity_path) as f:
            data = json.load(f)

        identity = cls(
            agent_id=data["agent_id"],
            actor_id=data["actor_id"],
            ed25519_pubkey_hex=data["ed25519_pubkey_hex"],
            bound_to=data.get("bound_to", "arif-fazil/F13"),
            capabilities=data.get("capabilities", ["OBSERVE", "REASON"]),
            max_blast_radius=data.get("max_blast_radius", "T2"),
            created_at=data.get("created_at", ""),
            fingerprint=data.get("fingerprint", ""),
        )

        # Load private key if path provided
        if private_key_path:
            pk_path = Path(private_key_path)
            if pk_path.exists():
                with open(pk_path, "rb") as f:
                    seed = f.read()
                identity._private_key = SigningKey(seed)

        return identity

    def save(self, directory: str | Path) -> tuple[Path, Path]:
        """Save identity.json (public) and identity.key (private, mode 600)."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        # Save public identity
        identity_path = directory / "identity.json"
        public_data = self.to_dict()
        with open(identity_path, "w") as f:
            json.dump(public_data, f, indent=2)

        # Save private key with strict permissions
        if self._private_key:
            key_path = directory / "identity.key"
            with open(key_path, "wb") as f:
                f.write(bytes(self._private_key))
            os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
        else:
            key_path = directory / "identity.key"

        return identity_path, key_path

    # ── Serialization ───────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Public identity as dictionary (NO private key)."""
        return {
            "agent_id": self.agent_id,
            "actor_id": self.actor_id,
            "ed25519_pubkey_hex": self.ed25519_pubkey_hex,
            "bound_to": self.bound_to,
            "capabilities": self.capabilities,
            "max_blast_radius": self.max_blast_radius,
            "created_at": self.created_at,
            "fingerprint": self.fingerprint,
        }

    def to_registry_entry(self) -> dict[str, Any]:
        """Compact entry for IdentityRegistry."""
        return {
            "agent_id": self.agent_id,
            "actor_id": self.actor_id,
            "pubkey_hex": self.ed25519_pubkey_hex,
            "fingerprint": self.fingerprint,
            "capabilities": self.capabilities,
            "max_blast_radius": self.max_blast_radius,
            "registered_at": datetime.now(UTC).isoformat(),
        }

    # ── Cryptography ────────────────────────────────────────────────────

    def compute_fingerprint(self) -> str:
        """BLAKE3 hash of core identity fields."""
        canonical = f"{self.agent_id}|{self.actor_id}|{self.ed25519_pubkey_hex}|{self.bound_to}"
        return blake3.blake3(canonical.encode()).hexdigest()[:32]

    def sign(self, message: bytes | str) -> str:
        """Sign a message with the agent's private key. Returns hex signature."""
        if not self._private_key:
            raise ValueError(f"Agent '{self.agent_id}' has no private key loaded")
        if isinstance(message, str):
            message = message.encode()
        signed = self._private_key.sign(message)
        return signed.signature.hex()

    def verify(self, message: bytes | str, signature_hex: str) -> bool:
        """Verify a signature against this agent's public key."""
        if isinstance(message, str):
            message = message.encode()
        try:
            signature_bytes = bytes.fromhex(signature_hex)
            verify_key = VerifyKey(bytes.fromhex(self.ed25519_pubkey_hex))
            verify_key.verify(message, signature_bytes)
            return True
        except (BadSignatureError, ValueError):
            return False

    def sign_challenge(self, challenge: str) -> str:
        """Sign a session challenge to prove identity."""
        payload = f"{self.agent_id}:{self.fingerprint}:{challenge}:{int(time.time())}"
        return self.sign(payload)

    @staticmethod
    def verify_signature(pubkey_hex: str, message: bytes | str, signature_hex: str) -> bool:
        """Static method: verify any signature against a public key hex."""
        if isinstance(message, str):
            message = message.encode()
        try:
            signature_bytes = bytes.fromhex(signature_hex)
            verify_key = VerifyKey(bytes.fromhex(pubkey_hex))
            verify_key.verify(message, signature_bytes)
            return True
        except (BadSignatureError, ValueError):
            return False

    # ── Validation ──────────────────────────────────────────────────────

    def is_valid(self) -> bool:
        """Check identity integrity."""
        if not self.agent_id or not self.ed25519_pubkey_hex:
            return False
        if len(self.ed25519_pubkey_hex) != 64:
            return False
        if self.fingerprint != self.compute_fingerprint():
            return False
        return True

    def capability_check(self, requested: str) -> bool:
        """Check if agent has a specific capability."""
        return requested in self.capabilities

    def blast_radius_check(self, tier: str) -> bool:
        """Check if action tier is within agent's max blast radius."""
        tier_order = {"T0": 0, "T1": 1, "T2": 2, "T3": 3}
        return tier_order.get(tier, 99) <= tier_order.get(self.max_blast_radius, 0)

    def __repr__(self) -> str:
        return f"AgentIdentity({self.agent_id}, pubkey={self.ed25519_pubkey_hex[:12]}…, bound={self.bound_to})"
