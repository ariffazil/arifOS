"""Canonical identity loader for arifOS.

Single SoT: identity.toml is the root source of truth.
All identity surfaces (/identity, /health, Agent Card) derive from here.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

try:
    import blake3 as _b3

    _HAS_B3 = True
except ImportError:
    _HAS_B3 = False

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

IDENTITY_TOML_PATH = Path("/opt/arifos/app/identity.toml")
_cached_identity: dict[str, Any] | None = None


def _load_identity_toml() -> dict[str, Any]:
    """Load canonical identity from identity.toml. Cached after first load."""
    global _cached_identity
    if _cached_identity is not None:
        return _cached_identity
    try:
        with open(IDENTITY_TOML_PATH, "rb") as f:
            _cached_identity = tomllib.load(f)
        return _cached_identity
    except Exception:
        # Fallback if TOML missing — return minimal safe identity
        return {
            "agent_id": "arifos",
            "display_name": "arifOS",
            "owner": "Muhammad Arif bin Fazil",
            "canonical_commit": os.environ.get("ARIFOS_GIT_COMMIT", "unknown")[:7],
            "identity_marker": "arifos-sovereign-runtime",
            "forbidden_self_names": ["Grok", "OpenClaw", "Claude", "Gemini", "ChatGPT"],
            "boot_attestation": True,
            "vault999_required": True,
            "runtime_drift_allowed": False,
            "a2a": {"enabled": True},
            "health": {
                "include_git_commit": True,
                "include_runtime_drift": True,
                "include_vault999_health": True,
                "include_identity_marker": True,
                "include_boot_attestation": True,
            },
        }


def get_identity(running_commit: str = "unknown") -> dict[str, Any]:
    """Return canonical identity from identity.toml plus current runtime state.

    Args:
        running_commit: The actual git commit currently running (from build.py).

    Returns:
        Full identity object with both static (from TOML) and dynamic (runtime) fields.
    """
    identity = _load_identity_toml()
    return {
        "agent_id": identity.get("agent_id", "arifos"),
        "display_name": identity.get("display_name", "arifOS"),
        "owner": identity.get("owner", "Muhammad Arif bin Fazil"),
        "domain": identity.get("domain", "aaa.arif-fazil.com"),
        "canonical_commit": identity.get("canonical_commit", running_commit),
        "running_commit": running_commit,
        "identity_marker": identity.get("identity_marker", "arifos-sovereign-runtime"),
        "forbidden_self_names": identity.get("forbidden_self_names", []),
        "boot_attestation": identity.get("boot_attestation", True),
        "vault999_required": identity.get("vault999_required", True),
        "runtime_drift_allowed": identity.get("runtime_drift_allowed", False),
        "source": "identity.toml",
        "status": "healthy",
    }


def get_identity_hash() -> str:
    """Return a deterministic hash of the canonical identity.

    Hashes: agent_id + canonical_commit + identity_marker.
    Used to detect unexpected identity changes.
    """
    identity = _load_identity_toml()
    payload = (
        f"{identity.get('agent_id', 'arifos')}"
        f"|{identity.get('canonical_commit', '')}"
        f"|{identity.get('identity_marker', 'arifos-sovereign-runtime')}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def invalidate_cache() -> None:
    """Invalidate the identity cache. Useful for testing or hot-reload."""
    global _cached_identity
    _cached_identity = None


def get_identity_b3_hash() -> dict[str, Any]:
    """Return BLAKE3 hash of the canonical identity.toml file content.

    Provides tamper-evidence for the identity file itself. If the file content
    changes, the hash changes. This is the recommended identity anchor for
    the federation identity chain.

    Returns:
        dict with algorithm, source, and the full b3_hash.
    """
    try:
        with open(IDENTITY_TOML_PATH, "rb") as f:
            content = f.read()
        if _HAS_B3:
            b3_hash = _b3.blake3(content).hexdigest()
        else:
            # Fallback to blake2b (standard library)
            b3_hash = hashlib.blake2b(content, digest_size=32).hexdigest()
        return {
            "algorithm": "BLAKE3" if _HAS_B3 else "BLAKE2B",
            "source": "identity.toml",
            "b3_hash": b3_hash,
            "b3_prefix": b3_hash[:16],
        }
    except Exception as e:
        return {
            "algorithm": "UNAVAILABLE",
            "source": "identity.toml",
            "error": str(e),
        }
