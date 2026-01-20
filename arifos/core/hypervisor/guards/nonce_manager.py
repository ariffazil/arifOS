"""
arifos.core/guards/nonce_manager.py

F11: Command Authentication (Nonce Verification)

Purpose:
    Prevents kernel hijacking and replay attacks through nonce-verified
    identity reloads. Implements Pauli Exclusion for Commands: no two
    identical nonces can occupy the same session state.

    Identity assertions without proper nonce verification are treated as
    DATA ONLY, not as authenticated commands.

Design:
    - Generate unique session nonces (format: X7K9F{counter})
    - Verify nonce on identity reload attempts
    - Prevent replay attacks (same nonce used twice)
    - Channel verification (distinguish direct vs pasted input)

Constitutional Floor: F11 (Command Auth)
    - Type: Hypervisor (MCP-side only, cannot enforce in Studio UI)
    - Engine: ASI (Ω-Heart) verifies channel integrity
    - Failure Action: SABAR
    - Precedence: 11

Security Note:
    This is a demonstration implementation using in-memory storage.
    Production systems should use:
    - Redis or similar for distributed nonce tracking
    - Cryptographic signing for channel verification
    - Expiration timestamps for nonces
    - Rate limiting on verification attempts

Motto:
    "Nonce twice? Never. Identity requires proof, not paste."
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Set


class NonceStatus(str, Enum):
    """Status of nonce verification."""

    VALID = "VALID"  # Nonce is valid and verified
    INVALID = "INVALID"  # Nonce doesn't match expected
    REPLAY = "REPLAY"  # Nonce has been used before (replay attack)
    EXPIRED = "EXPIRED"  # Nonce has expired (if expiration enabled)


@dataclass
class NonceVerificationResult:
    """
    Result structure for nonce verification.

    Attributes:
        status: "PASS" if verified, "SABAR" if failed
        nonce_status: NonceStatus enum value
        user_id: User identifier
        nonce_used: The nonce that was verified (or attempted)
        reason: Human-readable explanation
        authenticated: Whether identity is authenticated
    """

    status: str
    nonce_status: NonceStatus
    user_id: str
    nonce_used: str
    reason: str
    authenticated: bool


@dataclass
class SessionNonce:
    """
    Nonce data for a session.

    Attributes:
        nonce: The unique nonce value
        user_id: Associated user identifier
        created_at: Unix timestamp when nonce was created
        used: Whether this nonce has been used for verification
        channel_hash: Optional hash of the communication channel
    """

    nonce: str
    user_id: str
    created_at: float = field(default_factory=time.time)
    used: bool = False
    channel_hash: Optional[str] = None


class NonceManager:
    """
    F11 Command Authentication: Nonce-verified identity management.

    Manages session nonces to prevent:
    1. Replay attacks (same nonce used multiple times)
    2. Identity spoofing (pasted credentials without verification)
    3. Kernel hijacking (unauthorized system-level commands)

    Example usage:
        manager = NonceManager()
        
        # Generate nonce for new session
        nonce = manager.generate_nonce("user_123")
        # Output: "X7K9F1"
        
        # Later, verify identity reload
        result = manager.verify_nonce("user_123", "X7K9F1")
        if result.status == "SABAR":
            # Block the identity assertion
            print("F11 violation: unauthenticated identity assertion")
    """

    def __init__(self, nonce_expiration_seconds: Optional[int] = None) -> None:
        """
        Initialize the nonce manager.

        Args:
            nonce_expiration_seconds: Optional expiration time for nonces.
                                      None means nonces don't expire.
        """
        self.session_nonces: Dict[str, SessionNonce] = {}
        self.used_nonces: Set[str] = set()  # Track used nonces to prevent replay
        self.counter: int = 1  # Counter for nonce generation
        self.nonce_expiration = nonce_expiration_seconds
        self.nonce_prefix = "X7K9F"  # CIV-12 standard prefix

    def generate_nonce(
        self, user_id: str, channel_identifier: Optional[str] = None
    ) -> str:
        """
        Generate a unique nonce for a user session.

        Args:
            user_id: User identifier
            channel_identifier: Optional channel identifier for verification

        Returns:
            Nonce string in format X7K9F{counter}
        """
        nonce = f"{self.nonce_prefix}{self.counter}"
        self.counter += 1

        # Compute channel hash if provided
        channel_hash = None
        if channel_identifier:
            channel_hash = hashlib.sha256(channel_identifier.encode()).hexdigest()[:16]

        # Store nonce data
        self.session_nonces[user_id] = SessionNonce(
            nonce=nonce, user_id=user_id, channel_hash=channel_hash
        )

        return nonce

    def verify_nonce(
        self,
        user_id: str,
        provided_nonce: str,
        channel_identifier: Optional[str] = None,
    ) -> NonceVerificationResult:
        """
        Verify a nonce for identity reload.

        Args:
            user_id: User identifier
            provided_nonce: Nonce provided by user
            channel_identifier: Optional channel identifier for verification

        Returns:
            NonceVerificationResult with status and details
        """
        # Check if we have a nonce for this user
        if user_id not in self.session_nonces:
            return NonceVerificationResult(
                status="SABAR",
                nonce_status=NonceStatus.INVALID,
                user_id=user_id,
                nonce_used=provided_nonce,
                reason="F11 Command Auth: No nonce found for user. Identity assertion blocked.",
                authenticated=False,
            )

        session_nonce = self.session_nonces[user_id]

        # Check for replay attack (nonce already used)
        if provided_nonce in self.used_nonces:
            return NonceVerificationResult(
                status="SABAR",
                nonce_status=NonceStatus.REPLAY,
                user_id=user_id,
                nonce_used=provided_nonce,
                reason="F11 Command Auth: Replay attack detected. Nonce has been used before.",
                authenticated=False,
            )

        # Check for expiration (if enabled)
        if self.nonce_expiration is not None:
            age = time.time() - session_nonce.created_at
            if age > self.nonce_expiration:
                return NonceVerificationResult(
                    status="SABAR",
                    nonce_status=NonceStatus.EXPIRED,
                    user_id=user_id,
                    nonce_used=provided_nonce,
                    reason=f"F11 Command Auth: Nonce expired ({age:.0f}s > {self.nonce_expiration}s).",
                    authenticated=False,
                )

        # Verify nonce matches
        if session_nonce.nonce != provided_nonce:
            return NonceVerificationResult(
                status="SABAR",
                nonce_status=NonceStatus.INVALID,
                user_id=user_id,
                nonce_used=provided_nonce,
                reason=f"F11 Command Auth: Invalid nonce. Expected {session_nonce.nonce}, got {provided_nonce}.",
                authenticated=False,
            )

        # Optional: Verify channel integrity
        if channel_identifier and session_nonce.channel_hash:
            provided_hash = hashlib.sha256(channel_identifier.encode()).hexdigest()[
                :16
            ]
            if provided_hash != session_nonce.channel_hash:
                return NonceVerificationResult(
                    status="SABAR",
                    nonce_status=NonceStatus.INVALID,
                    user_id=user_id,
                    nonce_used=provided_nonce,
                    reason="F11 Command Auth: Channel mismatch. Possible paste attack.",
                    authenticated=False,
                )

        # Success: mark nonce as used
        self.used_nonces.add(provided_nonce)
        session_nonce.used = True

        return NonceVerificationResult(
            status="PASS",
            nonce_status=NonceStatus.VALID,
            user_id=user_id,
            nonce_used=provided_nonce,
            reason="F11 Command Auth: Identity verified.",
            authenticated=True,
        )

    def get_current_nonce(self, user_id: str) -> Optional[str]:
        """
        Get the current nonce for a user (if exists).

        Args:
            user_id: User identifier

        Returns:
            Current nonce string or None if no nonce exists
        """
        session_nonce = self.session_nonces.get(user_id)
        return session_nonce.nonce if session_nonce else None

    def revoke_nonce(self, user_id: str) -> bool:
        """
        Revoke (delete) a user's nonce, forcing re-authentication.

        Args:
            user_id: User identifier

        Returns:
            True if nonce was revoked, False if no nonce existed
        """
        if user_id in self.session_nonces:
            nonce = self.session_nonces[user_id].nonce
            self.used_nonces.add(nonce)  # Prevent reuse
            del self.session_nonces[user_id]
            return True
        return False


__all__ = [
    "NonceManager",
    "NonceStatus",
    "NonceVerificationResult",
    "SessionNonce",
]
