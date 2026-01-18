"""
Floor 2: Authentication & Authorization
APEX THEORY v46.0 - Constitutional Floor System

Implements cryptographic nonce-based authentication and session management.
Prevents replay attacks, enforces nonce expiration, and maintains audit trails.

Status: SEALED
Nonce: X7K9F19
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field


# Nonce configuration
NONCE_LENGTH = 32  # 32-byte hex = 64 characters
NONCE_EXPIRY_SECONDS = 300  # 5 minutes
NONCE_STORAGE: Dict[str, Dict[str, Any]] = {}  # In-memory storage (production: use Redis/DB)


@dataclass
class NonceRecord:
    """Record of a generated nonce."""
    nonce: str
    created_at: datetime
    used_at: Optional[datetime] = None
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if nonce has expired."""
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds() > NONCE_EXPIRY_SECONDS
    
    def is_used(self) -> bool:
        """Check if nonce has been used."""
        return self.used_at is not None


def generate_nonce() -> str:
    """
    Generate cryptographically secure nonce.
    
    Uses secrets module (CSPRNG) to generate 32-byte hex token.
    Each nonce is guaranteed unique with 2^256 keyspace.
    
    Returns:
        64-character hex string (32 bytes)
    """
    return secrets.token_hex(NONCE_LENGTH)


def validate_nonce(nonce: str, time_offset: Optional[timedelta] = None) -> Dict[str, Any]:
    """
    Validate nonce for authentication.
    
    Checks:
    1. Nonce exists in storage
    2. Nonce has not been used (replay protection)
    3. Nonce has not expired (time-based expiry)
    
    Args:
        nonce: The nonce to validate
        time_offset: Optional time offset for testing (simulates time passage)
        
    Returns:
        Dictionary with validation result:
        - status: "valid" | "rejected" | "expired"
        - reason: Explanation if not valid
        - floor: Floor number (2)
        - audit_logged: Whether event was logged
        - audit_entry: Audit log entry (if logged)
        - psi: Governance vitality metrics
    """
    # Check if nonce exists
    if nonce not in NONCE_STORAGE:
        return {
            "status": "rejected",
            "reason": "Nonce not found (never generated)",
            "floor": 2,
            "audit_logged": True,
            "audit_entry": {
                "severity": "ERROR",
                "event": "unknown_nonce",
                "nonce": nonce,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "unknown"
            },
            "psi": compute_psi_floor2(delta_s=2.0, peace_squared=0.9, kappa_r=1.0)
        }
    
    record = NONCE_STORAGE[nonce]
    
    # Simulate time offset for testing
    if time_offset:
        effective_time = record["created_at"] + time_offset
        age_seconds = (effective_time - record["created_at"]).total_seconds()
    else:
        age_seconds = (datetime.now(timezone.utc) - record["created_at"]).total_seconds()
    
    # Check expiration
    if age_seconds > NONCE_EXPIRY_SECONDS:
        return {
            "status": "expired",
            "reason": f"Nonce expired (>{NONCE_EXPIRY_SECONDS}s)",
            "floor": 2,
            "age_seconds": age_seconds,
            "audit_logged": True,
            "audit_entry": {
                "severity": "WARNING",
                "event": "expired_nonce",
                "nonce": nonce,
                "age_seconds": age_seconds,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "psi": compute_psi_floor2(delta_s=1.0, peace_squared=1.0, kappa_r=1.0)
        }
    
    # Check if already used (replay attack)
    if record.get("used", False):
        return {
            "status": "rejected",
            "reason": "Nonce already used",
            "attack_type": "replay",
            "floor": 2,
            "audit_logged": True,
            "audit_entry": {
                "severity": "WARNING",
                "event": "replay_attack",
                "nonce": nonce,
                "first_used_at": record.get("used_at"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": record.get("actor", "unknown")
            },
            "psi": compute_psi_floor2(delta_s=3.0, peace_squared=1.0, kappa_r=1.0)
        }
    
    # Mark nonce as used
    NONCE_STORAGE[nonce]["used"] = True
    NONCE_STORAGE[nonce]["used_at"] = datetime.now(timezone.utc).isoformat()
    
    # Valid nonce
    return {
        "status": "valid",
        "floor": 2,
        "nonce": nonce,
        "audit_logged": False,  # Success doesn't need warning-level logging
        "psi": compute_psi_floor2(delta_s=1.5, peace_squared=1.0, kappa_r=1.0)
    }


def initialize_context(user_id: str, role: str) -> Dict[str, Any]:
    """
    Initialize user session context.
    
    Creates a session context with user identity and role-based
    access control (RBAC) information.
    
    Args:
        user_id: Unique user identifier
        role: User role (e.g., "admin", "standard", "guest")
        
    Returns:
        Dictionary with session context:
        - user_id: User identifier
        - role: User role
        - session_id: Unique session identifier
        - created_at: Session creation timestamp
        - permissions: Role-based permissions
    """
    session_id = generate_session_id(user_id)
    
    # Role-based permissions (simplified RBAC)
    permissions = get_role_permissions(role)
    
    return {
        "user_id": user_id,
        "role": role,
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "permissions": permissions,
        "floor": 2
    }


def generate_session_id(user_id: str) -> str:
    """Generate unique session ID from user ID and timestamp."""
    timestamp = str(time.time())
    raw = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_role_permissions(role: str) -> Dict[str, bool]:
    """
    Get permissions for a given role.
    
    Implements role-based access control (RBAC).
    
    Args:
        role: User role
        
    Returns:
        Dictionary of permissions
    """
    role_permissions = {
        "admin": {
            "read": True,
            "write": True,
            "delete": True,
            "modify_roles": True,
            "access_audit_log": True
        },
        "standard": {
            "read": True,
            "write": True,
            "delete": False,
            "modify_roles": False,
            "access_audit_log": False
        },
        "guest": {
            "read": True,
            "write": False,
            "delete": False,
            "modify_roles": False,
            "access_audit_log": False
        }
    }
    
    return role_permissions.get(role, role_permissions["guest"])


def compute_psi_floor2(delta_s: float, peace_squared: float, kappa_r: float) -> Dict[str, float]:
    """
    Compute Ψ (governance vitality) for Floor 2 operations.
    
    Ψ = ΔS × Peace² × κᵣ
    
    Args:
        delta_s: Entropy reduction
        peace_squared: Squared peace metric
        kappa_r: Constitutional compliance
        
    Returns:
        Dictionary with Ψ components
    """
    psi_total = delta_s * peace_squared * kappa_r
    return {
        "delta_s": delta_s,
        "peace_squared": peace_squared,
        "kappa_r": kappa_r,
        "psi_total": round(psi_total, 6)
    }


def register_nonce(nonce: str, session_id: str = "", metadata: Optional[Dict] = None) -> None:
    """
    Register a generated nonce in storage.
    
    Internal function used by authentication systems to track nonces.
    
    Args:
        nonce: The nonce to register
        session_id: Optional session identifier
        metadata: Optional metadata to attach
    """
    NONCE_STORAGE[nonce] = {
        "nonce": nonce,
        "created_at": datetime.now(timezone.utc),
        "used": False,
        "used_at": None,
        "session_id": session_id,
        "metadata": metadata or {}
    }


def clear_expired_nonces() -> int:
    """
    Clear expired nonces from storage (cleanup routine).
    
    Should be called periodically to prevent memory bloat.
    
    Returns:
        Number of nonces cleared
    """
    now = datetime.now(timezone.utc)
    expired = []
    
    for nonce, record in NONCE_STORAGE.items():
        age = (now - record["created_at"]).total_seconds()
        if age > NONCE_EXPIRY_SECONDS:
            expired.append(nonce)
    
    for nonce in expired:
        del NONCE_STORAGE[nonce]
    
    return len(expired)


# Constitutional metadata
__floor__ = 2
__name__ = "Authentication & Authorization"
__authority__ = "Enforce cryptographic identity and prevent replay attacks"
__version__ = "v46.0-APEX-THEORY"
__status__ = "SEALED"
