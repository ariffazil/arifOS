"""
arifosmcp/resources/hash_anchor.py — Hash/seal anchoring for MCP resources.

Every resource content object carries a _meta envelope with:
  - content_hash: blake3 hash of the text content
  - provenance: source, truth_level, truth_label, evidence_layer
  - seal_id: latest VAULT999 seal seq (if available)
  - observed_at: ISO-8601 UTC timestamp
  - schema_version: "resource-meta/v1"

This is the migration path from inline boilerplate metadata to structured
_meta envelopes per MCP 2025-03-26 spec (Shape A: _meta on contents object).

Forged 2026-07-15 — Reality Verdict P1 implementation.
DITEMPA BUKAN DIBERI — Hashes are forged, not assumed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SEAL_HEAD_PATH = Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
_SCHEMA_VERSION = "resource-meta/v1"


def _blake3_hash(text: str) -> str:
    """Compute blake3 hash of text content. Falls back to sha256."""
    try:
        import blake3

        return "blake3:" + blake3.blake3(text.encode("utf-8")).hexdigest()
    except ImportError:
        return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _latest_seal_seq() -> int | None:
    """Read the latest seal seq from VAULT999 head file."""
    try:
        if _SEAL_HEAD_PATH.exists():
            with open(_SEAL_HEAD_PATH, encoding="utf-8") as fh:
                head = json.load(fh)
            return head.get("seq")
    except Exception:
        pass
    return None


def anchor_resource_meta(
    text: str,
    uri: str,
    *,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the _meta envelope for a resource content object.

    Args:
        text: The resource text content to hash.
        uri: The resource URI (e.g., "arifos://doctrine").
        provenance: Optional provenance dict from _RESOURCE_PROVENANCE.

    Returns:
        dict suitable for assignment to content["_meta"].
    """
    content_hash = _blake3_hash(text)
    seal_seq = _latest_seal_seq()

    meta: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "content_hash": content_hash,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seal_seq": seal_seq,
        "seal_anchored": seal_seq is not None,
    }

    if provenance:
        meta["provenance"] = {
            "source": provenance.get("source", "unknown"),
            "truth_level": provenance.get("truth_level", 0),
            "truth_label": provenance.get("truth_label", "UNKNOWN"),
            "mutability": provenance.get("mutability", "unknown"),
            "evidence_layer": provenance.get("evidence_layer", "unknown"),
        }

    return meta


def anchor_contents(
    contents: list[dict[str, Any]],
    uri: str,
    *,
    provenance: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Anchor _meta on each content object in a contents list.

    Mutates in-place and returns the list for chaining.
    Per MCP spec: _meta lives on the contents object, not the response envelope.
    """
    for content in contents:
        text = content.get("text", "")
        if text:
            content["_meta"] = anchor_resource_meta(text, uri, provenance=provenance)
    return contents


def extract_inline_meta(text: str) -> tuple[dict[str, Any], str]:
    """Extract inline arifos_meta block from text content.

    Many arifOS resources embed metadata as:
        ---arifos_meta
        key: value
        key: value
        ---
        (actual content)

    Returns:
        (meta_dict, clean_text_without_meta_block)
    """
    if not text.startswith("---arifos_meta"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    meta_block = parts[1].strip()
    clean_text = parts[2].strip()

    meta = {}
    for line in meta_block.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Type coercion for known fields
            if value.lower() in ("true", "false"):
                meta[key] = value.lower() == "true"
            elif value.isdigit():
                meta[key] = int(value)
            else:
                meta[key] = value

    return meta, clean_text


__all__ = [
    "anchor_resource_meta",
    "anchor_contents",
    "extract_inline_meta",
]
