"""
VAULT999 State Reader — Latest seal reconstruction

DITEMPA BUKAN DIBERI — Forged, Not Given.

Read-only. No mutation. Reads latest federation seal from VAULT999
and reconstructs swarm state for new agent boot.

Wire: vault999-writer HTTP health endpoint (port 5001)
      + SEALED_EVENTS.jsonl (local filesystem)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────

VAULT999_SEALED_EVENTS = Path("/opt/arifos/app/VAULT999/SEALED_EVENTS.jsonl")
VAULT999_HEALTH_URL = "http://localhost:5001/health"
VAULT999_TIMEOUT = 3.0  # seconds


# ── Public API ────────────────────────────────────────────────────


def get_latest_seal() -> dict[str, Any]:
    """
    Read the latest seal entry from VAULT999.

    Returns a dict with:
      - latest_seal: latest entry dict or None
      - chain_height: number of entries
      - reconstructable: whether swarm state can be rebuilt
      - source: "sealed_events" | "health_endpoint" | "unavailable"

    Degrades gracefully — never raises.
    """
    # Try local SEALED_EVENTS.jsonl first (canonical)
    try:
        if VAULT999_SEALED_EVENTS.exists():
            seals = _read_sealed_events()
            if seals:
                latest = seals[-1]
                return {
                    "latest_seal": latest,
                    "chain_height": len(seals),
                    "reconstructable": True,
                    "source": "sealed_events",
                    "latest_merkle_leaf": latest.get("merkle_leaf"),
                    "latest_verdict": latest.get("verdict"),
                    "latest_id": latest.get("id"),
                }
    except Exception as exc:
        logger.warning(f"SEALED_EVENTS read failed: {exc}")

    # Fallback: vault999-writer health endpoint
    try:
        import urllib.request

        with urllib.request.urlopen(VAULT999_HEALTH_URL, timeout=VAULT999_TIMEOUT) as resp:
            health = json.loads(resp.read())
            return {
                "latest_seal": None,
                "chain_height": health.get("chain_height", 0),
                "reconstructable": health.get("chain_height", 0) > 0,
                "source": "health_endpoint",
                "latest_hash": health.get("latest_hash"),
                "latest_action": health.get("latest_action"),
            }
    except Exception as exc:
        logger.warning(f"VAULT999 health probe failed: {exc}")

    return {
        "latest_seal": None,
        "chain_height": 0,
        "reconstructable": False,
        "source": "unavailable",
        "reason": "All sources failed",
    }


def reconstruct_latest_state() -> dict[str, Any]:
    """
    Reconstruct swarm state from the latest VAULT999 seal.

    Returns a dict with:
      - latest_seal: summary of latest sealed entry
      - last_good_state: hash of last known good state
      - handoff_pointer: last task that can be resumed
      - reconstructable: whether enough data exists
      - source: source of truth
      - degraded: True if reconstruction degraded
    """
    seal = get_latest_seal()

    if not seal.get("reconstructable"):
        return {
            "latest_seal": seal.get("latest_seal"),
            "last_good_state": None,
            "handoff_pointer": None,
            "reconstructable": False,
            "source": seal.get("source", "unavailable"),
            "degraded": True,
            "reason": "No reconstructable VAULT999 state",
        }

    # From the latest seal, extract what we can
    latest_entry = seal.get("latest_seal", {})

    return {
        "latest_seal": latest_entry,
        "last_good_state": latest_entry.get("merkle_leaf"),
        "handoff_pointer": latest_entry.get("action"),
        "reconstructable": True,
        "source": seal.get("source"),
        "chain_height": seal.get("chain_height"),
        "degraded": False,
    }


def seal_boot_receipt(manifest: dict[str, Any]) -> dict[str, Any]:
    """
    Seal a boot receipt to VAULT999.

    IMPORTANT: In early version, this returns a DRY_RUN seal.
    Real irreversible VAULT999 write must respect F01/F13 gates.

    Returns a dict with:
      - status: "DRY_RUN_SEAL" | "SEALED"
      - manifest_hash: hash of the manifest
      - irreversible_write: True only when real seal is performed
    """
    manifest_hash = manifest.get("manifest_hash", "pending")

    # DRY_RUN: no actual write yet
    return {
        "status": "DRY_RUN_SEAL",
        "seal_type": "boot_receipt",
        "manifest_hash": manifest_hash,
        "irreversible_write": False,
        "note": "Real VAULT999 seal requires F01/F13 gates via arif_vault_seal()",
        "sealed_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Internal helpers ──────────────────────────────────────────────


def _read_sealed_events() -> list[dict[str, Any]]:
    """Read all sealed events from the canonical JSONL file."""
    entries: list[dict[str, Any]] = []
    with open(VAULT999_SEALED_EVENTS) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries
