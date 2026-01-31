"""
arifOS RootKey v55.0 - Centralized Cryptographic Foundation
Solves: Storage fragmentation, derivation inconsistency, access control gaps

Reference: 000_THEORY/ROOTKEY_SPEC.md (updated to v55.0)
"""

from __future__ import annotations
import os
import json
import hashlib
import secrets
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from pathlib import Path
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

logger = logging.getLogger(__name__)


# ============================================
# BAND DEFINITIONS (Constitutional Access Control)
# ============================================


class Band(Enum):
    """
    Constitutional bands for data access control.

    AAA: Human-only (AI forbidden) - Root keys, sovereign decisions
    BBB: Human-AI collaborative - Session data, working memory
    CCC: AI-accessible - Ephemeral computation, non-sensitive
    """

    AAA_HUMAN = "AAA_HUMAN"  # Root keys, sovereign authority
    BBB_COLLAB = "BBB_COLLAB"  # Session keys, shared state
    CCC_AI = "CCC_AI"  # Ephemeral, non-sensitive


# ============================================
# CANONICAL PATHS (Solves storage fragmentation)
# ============================================


class CanonicalPaths:
    """
    Single source of truth for all arifOS paths.
    All modules MUST import from here.
    """

    # Base directory (from environment or default)
    BASE_DIR = Path(os.environ.get("ARIFOS_HOME", Path.home() / ".arifos"))

    # Band directories
    @classmethod
    def aaa_human(cls) -> Path:
        """AAA_HUMAN band - AI forbidden"""
        return cls.BASE_DIR / "AAA_HUMAN"

    @classmethod
    def bbb_collab(cls) -> Path:
        """BBB_COLLAB band - Human-AI shared"""
        return cls.BASE_DIR / "BBB_COLLAB"

    @classmethod
    def ccc_ai(cls) -> Path:
        """CCC_AI band - AI accessible"""
        return cls.BASE_DIR / "CCC_AI"

    # Specific files
    @classmethod
    def rootkey(cls) -> Path:
        """Root key storage (AAA_HUMAN)"""
        return cls.aaa_human() / "rootkey.json"

    @classmethod
    def vault999(cls) -> Path:
        """Vault999 storage (BBB_COLLAB)"""
        return cls.bbb_collab() / "VAULT999"

    @classmethod
    def session_keys(cls) -> Path:
        """Session key cache (BBB_COLLAB)"""
        return cls.bbb_collab() / "session_keys"

    @classmethod
    def ensure_dirs(cls):
        """Ensure all band directories exist with proper permissions"""
        base = Path(cls.BASE_DIR)  # allow BASE_DIR to be set to str externally
        cls.BASE_DIR = base

        # AAA: 700 (owner only)
        base_aaa = cls.aaa_human()
        base_aaa.mkdir(parents=True, exist_ok=True)
        os.chmod(base_aaa, 0o700)

        # BBB: 750 (owner + group)
        base_bbb = cls.bbb_collab()
        base_bbb.mkdir(parents=True, exist_ok=True)
        os.chmod(base_bbb, 0o750)

        # CCC: 755 (world readable)
        base_ccc = cls.ccc_ai()
        base_ccc.mkdir(parents=True, exist_ok=True)
        os.chmod(base_ccc, 0o755)


# ============================================
# ENTROPY MANAGEMENT
# ============================================


class EntropySource:
    """
    Manages entropy sources for cryptographic operations.

    Minimum entropy requirements:
    - Root key generation: 256 bits (32 bytes)
    - Session key derivation: 128 bits (16 bytes)
    """

    MIN_ROOT_ENTROPY = 32  # 256 bits
    MIN_SESSION_ENTROPY = 16  # 128 bits

    @staticmethod
    def generate(bits: int = 256) -> bytes:
        """Generate cryptographically secure random bytes"""
        return secrets.token_bytes(bits // 8)

    @staticmethod
    def combine(*sources: bytes) -> bytes:
        """
        Combine multiple entropy sources using XOR.
        All sources must be same length.
        """
        if not sources:
            raise ValueError("At least one entropy source required")

        result = sources[0]
        for source in sources[1:]:
            if len(source) != len(result):
                raise ValueError("All entropy sources must be same length")
            result = bytes(a ^ b for a, b in zip(result, source))

        return result


# ============================================
# ROOTKEY CLASS (Centralized)
# ============================================


@dataclass
class RootKey:
    """
    The constitutional root key for arifOS.

    Golden Rule: Root key never leaves AAA_HUMAN band.
    AI never sees root key.
    """

    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    generated_at: datetime
    generated_by: str  # Human sovereign identity
    entropy_sources: int
    band: Band = Band.AAA_HUMAN

    # Class-level lock
    _instance: Optional[RootKey] = None
    _initialized: bool = False

    def __post_init__(self):
        if self.band != Band.AAA_HUMAN:
            raise ValueError("RootKey MUST be in AAA_HUMAN band")

    @classmethod
    def generate(cls, sovereign_identity: str, entropy_bits: int = 256) -> RootKey:
        """
        Generate a new root key.

        Args:
            sovereign_identity: Human sovereign who owns this key
            entropy_bits: Entropy for key generation (default 256)

        Returns:
            New RootKey instance
        """
        # Generate entropy
        entropy = EntropySource.generate(entropy_bits)

        # Create Ed25519 keypair
        private_key = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(entropy).digest()[:32])
        public_key = private_key.public_key()

        rootkey = cls(
            private_key=private_key,
            public_key=public_key,
            generated_at=datetime.now(timezone.utc),
            generated_by=sovereign_identity,
            entropy_sources=1,
        )

        # Save to AAA_HUMAN band
        rootkey._save()

        logger.info(f"RootKey generated for {sovereign_identity}")
        return rootkey

    @classmethod
    def load(cls) -> Optional[RootKey]:
        """Load root key from AAA_HUMAN band (human-only)"""
        path = CanonicalPaths.rootkey()

        if not path.exists():
            logger.warning("No root key found - call generate() first")
            return None

        with open(path, "r") as f:
            data = json.load(f)

        # Deserialize
        private_bytes = bytes.fromhex(data["private_key"])
        public_bytes = bytes.fromhex(data["public_key"])

        private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
        public_key = Ed25519PublicKey.from_public_bytes(public_bytes)

        return cls(
            private_key=private_key,
            public_key=public_key,
            generated_at=datetime.fromisoformat(data["generated_at"]),
            generated_by=data["generated_by"],
            entropy_sources=data["entropy_sources"],
            band=Band.AAA_HUMAN,
        )

    def _save(self):
        """Save root key to AAA_HUMAN band"""
        CanonicalPaths.ensure_dirs()
        path = CanonicalPaths.rootkey()

        # Serialize
        private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )

        data = {
            "private_key": private_bytes.hex(),
            "public_key": public_bytes.hex(),
            "generated_at": self.generated_at.isoformat(),
            "generated_by": self.generated_by,
            "entropy_sources": self.entropy_sources,
            "band": self.band.value,
            "version": "v55.0",
        }

        # Write with restricted permissions
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        os.chmod(path, 0o400)  # Read-only

        logger.info(f"RootKey saved to {path}")

    def derive_session_key(self, session_id: str, context: Optional[bytes] = None) -> bytes:
        """
        Derive session key from root key using HKDF.

        Session keys are in BBB_COLLAB band (AI can use, not see root).

        Args:
            session_id: Unique session identifier
            context: Optional additional context

        Returns:
            32-byte session key
        """
        private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"arifos_root_key_salt",
            info=f"arifos_session_key_v55_{session_id}".encode(),
        )

        session_key = hkdf.derive(private_bytes + (context or b""))

        # Cache in BBB_COLLAB
        self._cache_session_key(session_id, session_key)

        return session_key

    def _cache_session_key(self, session_id: str, key: bytes):
        """Cache session key in BBB_COLLAB band"""
        cache_dir = CanonicalPaths.session_keys()
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / f"{session_id}.key"
        with open(cache_file, "wb") as f:
            f.write(key)
        os.chmod(cache_file, 0o600)

    def sign(self, message: bytes) -> bytes:
        """Sign message with root key"""
        return self.private_key.sign(message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify signature with public key"""
        try:
            self.public_key.verify(signature, message)
            return True
        except Exception:
            return False


# ============================================
# BAND ENFORCEMENT (F1/F10 Guards)
# ============================================


class BandGuard:
    """
    Enforces constitutional band access rules.

    F1 Amanah: Reversibility and audit
    F10 Ontology: No AGI-consciousness claims
    """

    @staticmethod
    def check_access(band: Band, accessor_type: str) -> bool:
        """
        Check if accessor can access band.

        Args:
            band: Target band
            accessor_type: "human" or "ai"

        Returns:
            True if access allowed

        Raises:
            OntologyLock: If AI tries to access AAA_HUMAN
        """
        if band == Band.AAA_HUMAN and accessor_type == "ai":
            raise OntologyLock(
                "F10 ONTOLOGY LOCK: AI cannot access AAA_HUMAN band. "
                "Root key access is human-sovereign only."
            )

        if band == Band.BBB_COLLAB:
            return True  # Both human and AI can access

        if band == Band.CCC_AI:
            return accessor_type == "ai" or accessor_type == "human"

        return accessor_type == "human"

    @staticmethod
    def audit_access(band: Band, accessor_type: str, action: str) -> Dict:
        """Create audit log entry for band access"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "band": band.value,
            "accessor": accessor_type,
            "action": action,
            "allowed": BandGuard.check_access(band, accessor_type),
        }


class OntologyLock(Exception):
    """F10 Ontology Wall violation"""

    pass


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    # Ensure directories exist
    CanonicalPaths.ensure_dirs()

    # Generate root key (human-only operation)
    rootkey = RootKey.generate(sovereign_identity="Muhammad Arif bin Fazil", entropy_bits=256)

    # Derive session key
    session_key = rootkey.derive_session_key("session_001")

    # Sign message
    message = b"Constitutional operation authorized"
    signature = rootkey.sign(message)

    # Verify
    assert rootkey.verify(message, signature)

    print("RootKey v55.0 operational")
