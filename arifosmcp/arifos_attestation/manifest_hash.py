"""
Manifest Hasher — BLAKE3 manifest hashing for arifOS.

BLAKE3 is the substrate hash function for all arifOS artifacts.
Already in deps (blake3>=1.0.0).

Use cases:
- Per-tool manifest hash (capability attestation)
- Per-receipt content hash
- Per-session state hash
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ManifestHasher:
    """BLAKE3 + SHA-256 dual hash for forensic compatibility."""

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Return b3:<hex> hash."""
        import blake3
        return "b3:" + blake3.blake3(data).hexdigest()

    @staticmethod
    def hash_file(path: str | Path) -> str:
        """Hash a file's contents."""
        p = Path(path)
        if not p.exists():
            return "b3:missing"
        return ManifestHasher.hash_bytes(p.read_bytes())

    @staticmethod
    def hash_obj(obj: Any) -> str:
        """Hash a JSON-serializable object deterministically."""
        return ManifestHasher.hash_bytes(
            json.dumps(obj, sort_keys=True, default=str).encode()
        )

    @staticmethod
    def dual_hash_bytes(data: bytes) -> dict[str, str]:
        """Return both b3 and sha256 for forensic audit."""
        import blake3
        return {
            "b3": "b3:" + blake3.blake3(data).hexdigest(),
            "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        }
