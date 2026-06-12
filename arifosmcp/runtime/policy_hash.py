"""
arifosmcp/runtime/policy_hash.py
══════════════════════════════════
Canonical Policy Hash Generator

Computes sha256 of the complete constitutional covenant:
  CANONICAL_TOOLS + FLOOR_SPEC + TOOL_ANNOTATIONS

This hash is the "policy fingerprint" — every session_init must carry
a matching hash or be HOLD. If the kernel's constitution changes
(new tool, floor adjustment), the hash changes, and all stale
client sessions must re-initialize.

F2 TRUTH: The hash is computed from canonical sources, never fabricated.
F11 AUTH: Stale policy_hash → HOLD (re-init required).
F13 SOVEREIGN: Hash changes require F13 review.

Usage:
  from arifosmcp.runtime.policy_hash import compute_policy_hash, KERNEL_POLICY_HASH
  # At startup:
  KERNEL_POLICY_HASH = compute_policy_hash()
  # Then register with envelope_validator:
  from arifosmcp.runtime.envelope_validator import set_kernel_policy_hash
  set_kernel_policy_hash(KERNEL_POLICY_HASH)

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import hashlib
import json
import logging

logger = logging.getLogger("arifosmcp.policy_hash")

# The computed hash — set at startup by server.py
KERNEL_POLICY_HASH: str = ""
KERNEL_MANIFEST_HASH: str = ""


def _canonical_json(obj: object) -> str:
    """Serialize to deterministic JSON (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def compute_policy_hash(
    canonical_tools: dict | None = None,
    floor_spec: dict | None = None,
    annotations: dict | None = None,
) -> str:
    """
    Compute sha256 of the complete constitutional covenant.

    The hash covers everything that defines the kernel's governance
    contract. If any of these change, the policy has changed.

    Returns: 64-char hex string (sha256)
    """
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        tools = canonical_tools or CANONICAL_TOOLS
    except ImportError:
        tools = canonical_tools or {}

    # Normalize tools to serializable form
    tools_normalized: dict = {}
    for name, spec in (tools or {}).items():
        clean: dict = {}
        for k, v in spec.items():
            if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                clean[k] = v
            else:
                clean[k] = str(v)  # Enum, set, etc → string repr
        tools_normalized[name] = clean

    # Build the covenant payload
    covenant: dict = {
        "version": "v2026.06.12-AGI-KERNEL",
        "canonical_tools": tools_normalized,
        "floor_count": 13,
        "floor_names": [
            "L01_AMANAH",
            "L02_TRUTH",
            "L03_WITNESS",
            "L04_CLARITY",
            "L05_PEACE",
            "L06_EMPATHY",
            "L07_HUMILITY",
            "L08_GENIUS",
            "L09_ANTIHANTU",
            "L10_ONTOLOGY",
            "L11_AUTH",
            "L12_INJECTION",
            "L13_SOVEREIGN",
        ],
        "transport": "streamable-http",
        "protocol_version": "2025-11-25",
    }

    if floor_spec:
        covenant["floor_spec"] = floor_spec
    if annotations:
        covenant["annotations"] = annotations

    payload = _canonical_json(covenant)
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    logger.info(f"Policy hash computed: {h[:16]}...")
    return h


def compute_manifest_hash() -> str:
    """Compute sha256 of just the tool manifest (tools + their schemas)."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    manifest: dict = {}
    for name, spec in CANONICAL_TOOLS.items():
        manifest[name] = {
            "description": spec.get("description", ""),
            "floors": sorted(spec.get("floors", [])),
            "stage": spec.get("stage", ""),
            "lane": spec.get("lane", ""),
        }

    payload = _canonical_json({"tools": manifest})
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def policy_hash_matches(client_hash: str) -> bool:
    """
    Check if a client-provided policy hash matches the kernel.

    Returns True if:
    - KERNEL_POLICY_HASH is not set (development mode)
    - client_hash matches KERNEL_POLICY_HASH exactly
    """
    if not KERNEL_POLICY_HASH:
        logger.debug("Policy hash not set — accepting all (dev mode)")
        return True
    return client_hash == KERNEL_POLICY_HASH
