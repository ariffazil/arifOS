"""
arifos://vault/{vault_type} — VAULT999 Resource Template
═══════════════════════════════════════════════════════════

FastMCP 3.4.x resource template for parameterized VAULT999 queries.
Allows agents to read vault entries by type (judge, heart, sense, etc.)
using URI templates instead of tool calls.

URI patterns:
  arifos://vault/{vault_type}           — last N entries from vault type
  arifos://vault/{vault_type}?limit=N   — last N entries

Vault types: judge, heart, sense, outcomes, governance-sidecar

DITEMPA BUKAN DIBERI — Sealed, not guessed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastmcp import FastMCP

VAULT_DIR = Path(os.getenv("ARIFOS_VAULT_DIR", "/var/lib/arifos/vault"))
# Fallback: if the resolved dir doesn't have vault files, use the canonical path
if not (VAULT_DIR / "judge.jsonl").exists():
    VAULT_DIR = Path("/var/lib/arifos/vault")

# Canonical vault file mapping
VAULT_FILES: dict[str, str] = {
    "judge": "judge.jsonl",
    "heart": "heart.jsonl",
    "sense": "sense.jsonl",
    "outcomes": "outcomes.jsonl",
    "governance": "governance-sidecar.jsonl",
}

DEFAULT_LIMIT = 5


def _read_vault_entries(vault_type: str, limit: int = DEFAULT_LIMIT) -> dict:
    """Read the last N entries from a vault JSONL file."""
    if vault_type not in VAULT_FILES:
        return {
            "error": f"Unknown vault type: {vault_type}",
            "available": list(VAULT_FILES.keys()),
        }

    vault_file = VAULT_DIR / VAULT_FILES[vault_type]
    if not vault_file.exists():
        return {
            "error": f"Vault file not found: {vault_file}",
            "vault_type": vault_type,
        }

    try:
        lines = vault_file.read_text().strip().split("\n")
        # Read more lines than requested to account for malformed entries
        read_window = limit * 3
        entries = []
        for line in reversed(lines):
            if len(entries) >= limit:
                break
            line = line.strip()
            if line and line not in ("none", "null", ""):
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed trailing lines (e.g. partial writes)
                    pass
        entries.reverse()

        return {
            "vault_type": vault_type,
            "vault_file": str(vault_file),
            "total_lines": len(lines),
            "returned": len(entries),
            "limit": limit,
            "entries": entries,
        }
    except Exception as e:
        return {
            "error": f"Failed to read vault: {e}",
            "vault_type": vault_type,
        }


def register_vault999_template(mcp: FastMCP) -> list[str]:
    """Register arifos://vault/{vault_type} resource template."""

    @mcp.resource(
        uri="arifos://vault/{vault_type}",
        name="VAULT999 Entry Reader",
        description=(
            "Read entries from VAULT999 audit ledger by vault type. "
            "Available types: judge, heart, sense, outcomes, governance. "
            "Returns the last N entries (default 5). "
            "Use ?limit=N to control how many entries are returned. "
            "Truth level: SEALED_VAULT (rank 2)."
        ),
        tags={"resource", "vault", "audit", "sealed", "template"},
    )
    def vault_resource(vault_type: str, limit: int = DEFAULT_LIMIT) -> dict:
        return _read_vault_entries(vault_type, limit)

    return ["arifos://vault/{vault_type}"]
