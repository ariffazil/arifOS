#!/usr/bin/env python3
"""
VAULT999 MCP Server - Constitutional Memory Gateway for ChatGPT

HUMAN-MACHINE CONCORDAT:
  VAULT999     = Machine Law (MCP-governed, constitutional, exposed)
  ARIF FAZIL   = Human Biography (sacred, offline, NEVER exposed)

This separation embodies L0_COVENANT:
  Humans live by Prinsip.
  Machines obey Law.

Uses FastMCP + Uvicorn with SSL for HTTPS/SSE transport.

# Tools:
#   - search(query): Search L0_VAULT, L1_LEDGER, L4_WITNESS
#   - fetch(id): Retrieve full document by ID
#   - receipts(limit): Verify ZKPC receipts in ledger
#   - arifos_fag_read(path, root): Governed file reading
#   - arifos_fag_write(path, operation, ...): Governed file writing
#   - arifos_fag_list(path, root): Governed directory listing
#   - arifos_fag_stats(root): Governance health and metrics
#
# Usage:
#     python vault999_server.py
#
# Version: v46.0.0
# DITEMPA BUKAN DIBERI
# """

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

from arifos.mcp.tools.fag_list import FAGListRequest, arifos_fag_list

# FAG Tool Imports
from arifos.mcp.tools.fag_read import FAGReadRequest, arifos_fag_read
from arifos.mcp.tools.fag_stats import FAGStatsRequest, arifos_fag_stats
from arifos.mcp.tools.fag_write import FAGWriteRequest, arifos_fag_write
from arifos.memory.vault.vault_manager import VaultManager

# Strict ZKPC Compliance (v46)
# Legacy Spec Bypass REMOVED





# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [VAULT999] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Path constants
REPO_ROOT = Path(__file__).parent.parent.parent
VAULT_ROOT = REPO_ROOT / "vault_999" / "VAULT999"
CERT_DIR = Path(__file__).parent / "certs"
SSL_CERT = CERT_DIR / "cert.pem"
SSL_KEY = CERT_DIR / "key.pem"

# =============================================================================
# CONSTITUTIONAL BOUNDARY: HUMAN-MACHINE CONCORDAT
# =============================================================================
# Two vaults exist:
#   VAULT999     = Machine Law (MCP-governed, constitutional, exposed)
#   ARIF FAZIL   = Human Biography (sacred, offline, NEVER exposed)
#
# This separation embodies L0_COVENANT:
#   Humans live by Prinsip.
#   Machines obey Law.
#
# DITEMPA BUKAN DIBERI
# =============================================================================

SACRED_VAULT = REPO_ROOT / "vault_999" / "ARIF FAZIL"
SACRED_VAULT_PATTERNS = ["ARIF FAZIL", "ARIF_FAZIL", "arif fazil", "arif_fazil"]

def _is_sacred_path(path: Path) -> bool:
    """Check if path is within or references the sacred human vault."""
    path_str = str(path).lower()
    for pattern in SACRED_VAULT_PATTERNS:
        if pattern.lower() in path_str:
            return True
    return False

def _log_sacred_violation(query: str, source: str) -> None:
    """Log any attempt to access sacred human vault. F1 Amanah violation."""
    logger.error(f"[VOID] SACRED_BOUNDARY_VIOLATION: source={source}, query='{query}'")
    logger.error(f"[VOID] Human vault 'ARIF FAZIL' is offline. Machine may not access.")

# Memory band configuration (ONLY MACHINE VAULT)
BANDS = {
    "L0_VAULT": {
        "path": VAULT_ROOT / "L0_VAULT",
        "confidence": 1.0,
        "tag": "[CANONICAL]",
        "geometry": "ORTHOGONAL",  # The Crystal (Truth)
        "extensions": ["*.md", "*.json"]
    },
    "L1_LEDGERS": {
        "path": VAULT_ROOT / "L1_LEDGERS",
        "confidence": 1.0,
        "tag": "[SEALED]",
        "geometry": "TOROIDAL",    # The Loop (History)
        "extensions": ["*.jsonl", "*.md"]
    },
    "L4_WITNESS": {
        "path": VAULT_ROOT / "L4_WITNESS",
        "confidence": 0.85,
        "tag": "[OBSERVATION]",
        "geometry": "FRACTAL",     # The Spiral (Context)
        "extensions": ["*.md"]
    },
    "00_ENTROPY": {
        "path": VAULT_ROOT / "00_ENTROPY",
        "confidence": 0.1,
        "tag": "[HOT]",
        "geometry": "CHAOS",       # The Heat (Raw)
        "extensions": ["*.json", "*.md", "*.txt"]
    }
}

MAX_RESULTS = 10

# Create MCP server
mcp = FastMCP("VAULT999")


def search_band(band_name: str, query: str) -> List[Dict[str, Any]]:
    """Search a single memory band."""
    results = []
    band = BANDS.get(band_name)
    if not band or not band["path"].exists():
        return results

    query_lower = query.lower()

    for ext in band["extensions"]:
        for file in band["path"].glob(ext):
            try:
                content = file.read_text(encoding='utf-8')
                if query_lower in content.lower():
                    idx = content.lower().find(query_lower)
                    start = max(0, idx - 100)
                    snippet = content[start:start + 300]
                    if start > 0:
                        snippet = "..." + snippet
                    if len(content) > start + 300:
                        snippet = snippet + "..."

                    results.append({
                        "id": f"{band_name}_{file.stem}",
                        "title": f"{band['tag']} {file.stem}",
                        "text": snippet,
                        "url": f"vault://{band_name}/{file.name}",
                        "confidence": band["confidence"],
                        "band": band_name,
                        "geometry": band.get("geometry", "UNKNOWN")
                    })
            except Exception as e:
                logger.warning(f"Error reading {file}: {e}")

    return results


@mcp.tool()
def search(query: str) -> Dict[str, Any]:
    """Search constitutional memory across L0_VAULT, L1_LEDGER, L4_WITNESS.

    CONSTITUTIONAL BOUNDARY: This function only searches VAULT999 (machine law).
    The ARIF FAZIL vault (human biography) is sacred and offline.
    """
    logger.info(f"Search: '{query}'")

    # SACRED VAULT PROTECTION: Block any query targeting human biography
    query_lower = query.lower()
    for pattern in SACRED_VAULT_PATTERNS:
        if pattern.lower() in query_lower:
            _log_sacred_violation(query, "search")
            return {
                "error": "SACRED_BOUNDARY: Query references human vault which is offline.",
                "verdict": "VOID",
                "guidance": "The ARIF FAZIL vault contains human biography and is not MCP-governed.",
                "results": []
            }

    if not query or len(query.strip()) < 2:
        return {"error": "Query too short", "results": []}

    all_results = []
    for band_name in ["L0_VAULT", "L1_LEDGERS", "L4_WITNESS", "00_ENTROPY"]:
        all_results.extend(search_band(band_name, query))

    all_results.sort(key=lambda x: -x["confidence"])
    limited = all_results[:MAX_RESULTS]

    logger.info(f"Found {len(all_results)}, returning {len(limited)}")

    return {
        "query": query,
        "total_found": len(all_results),
        "results": limited,
        "vault": "VAULT999",
        "governance": "Nine Floors + APEX PRIME"
    }


@mcp.tool()
def fetch(id: str) -> Dict[str, Any]:
    """Retrieve full document by ID (format: BAND_filename).

    CONSTITUTIONAL BOUNDARY: This function only fetches from VAULT999.
    The ARIF FAZIL vault is sacred and offline.
    """
    logger.info(f"Fetch: '{id}'")

    # SACRED VAULT PROTECTION: Block any fetch targeting human biography
    id_lower = id.lower() if id else ""
    for pattern in SACRED_VAULT_PATTERNS:
        if pattern.lower() in id_lower:
            _log_sacred_violation(id, "fetch")
            return {
                "error": "SACRED_BOUNDARY: Document is in human vault which is offline.",
                "verdict": "VOID",
                "guidance": "The ARIF FAZIL vault contains human biography and is not MCP-governed."
            }

    if not id or "_" not in id:
        return {"error": f"Invalid ID: {id}"}

    for bn, band in BANDS.items():
        if id.startswith(bn + "_"):
            filename_stem = id[len(bn) + 1:]
            band_path = band["path"]

            if not band_path.exists():
                return {"error": f"Band not found: {bn}"}

            for ext in band["extensions"]:
                pattern = ext.replace("*", filename_stem)
                matches = list(band_path.glob(pattern))
                if matches:
                    file = matches[0]
                    try:
                        content = file.read_text(encoding='utf-8')
                        return {
                            "id": id,
                            "title": f"{band['tag']} {file.stem}",
                            "text": content,
                            "url": f"vault://{bn}/{file.name}",
                            "metadata": {
                                "confidence": band["confidence"],
                                "band": bn,
                                "canonical": bn == "L0_VAULT",
                                "vault": "VAULT999",
                                "governance": "Nine Floors + APEX PRIME",
                                "geometry": band.get("geometry", "UNKNOWN")
                            }
                        }
                    except Exception as e:
                        return {"error": str(e)}

    return {"error": f"Not found: {id}"}

@mcp.tool()
def receipts(limit: int = 10) -> Dict[str, Any]:
    """
    Verify ZKPC receipts in the constitutional ledger.

    Proof of Integrity (F8 Tri-Witness):
    Returns the cryptographic receipts for recent actions.
    """
    try:
        manager = VaultManager()
        items = manager.get_receipts(limit=limit)
        return {
            "status": "SEALED",
            "protocol": "ZKPC-v46",
            "count": len(items),
            "receipts": items
        }
    except Exception as e:
        return {"error": str(e), "status": "BROKEN"}


# =============================================================================
# FAG TOOLSET (v45.3.0)
# =============================================================================

@mcp.tool(name="arifos_fag_read")
def tool_fag_read(path: str, root: str = ".", human_seal_token: str = None) -> Any:
    """Read file with constitutional governance (FAG)."""
    return arifos_fag_read(FAGReadRequest(path=path, root=root, human_seal_token=human_seal_token))


@mcp.tool(name="arifos_fag_write")
def tool_fag_write(
    path: str,
    operation: str,
    justification: str,
    diff: str = None,
    root: str = ".",
    human_seal_token: str = None
) -> Any:
    """Validate/execute file write with FAG Write Contract."""
    return arifos_fag_write(FAGWriteRequest(
        path=path,
        operation=operation,
        justification=justification,
        diff=diff,
        root=root,
        human_seal_token=human_seal_token
    ))


@mcp.tool(name="arifos_fag_list")
def tool_fag_list(path: str = ".", root: str = ".", human_seal_token: str = None) -> Any:
    """List directory contents with constitutional filtering."""
    return arifos_fag_list(FAGListRequest(path=path, root=root, human_seal_token=human_seal_token))


@mcp.tool(name="arifos_fag_stats")
def tool_fag_stats(root: str = ".") -> Any:
    """Get FAG access statistics and constitutional health."""
    return arifos_fag_stats(FAGStatsRequest(root=root))


def main():
    """Main entry point."""
    print("=" * 70)
    print("  VAULT999 MCP Server v46.0.0")
    print("  Constitutional Memory Gateway for ChatGPT")
    print("=" * 70)
    print()
    print("  HUMAN-MACHINE CONCORDAT:")
    print("    VAULT999     = Machine Law (MCP-governed, exposed)")
    print("    ARIF FAZIL   = Human Biography (sacred, offline)")
    print()
    print(f"  Machine Vault: {VAULT_ROOT}")
    print(f"  Sacred Vault:  {SACRED_VAULT} [OFFLINE]")
    print()
    print(f"  URL: https://127.0.0.1:8000/sse/")
    print("  Tools: search(query), fetch(id), receipts(limit)")
    print("         arifos_fag_read(path), arifos_fag_write(path, op, ...)")
    print("         arifos_fag_list(path), arifos_fag_stats(root)")
    print()
    print("  Humans live by Prinsip. Machines obey Law.")
    print("  DITEMPA BUKAN DIBERI")
    print("=" * 70)

    # Check prerequisites
    if not VAULT_ROOT.exists():
        print(f"\nERROR: Vault not found: {VAULT_ROOT}")
        sys.exit(1)

    if not SSL_CERT.exists() or not SSL_KEY.exists():
        print(f"\nERROR: SSL certs missing in {CERT_DIR}")
        print("Generate with Python cryptography or openssl")
        sys.exit(1)

    logger.info("Starting server with SSL...")
    logger.info("Ready for ChatGPT connection...")

    # Run with uvicorn + SSL
    import uvicorn

    # Get the ASGI app from FastMCP
    app = mcp.http_app(path="/sse")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=9999,
        ssl_certfile=str(SSL_CERT),
        ssl_keyfile=str(SSL_KEY),
        log_level="info"
    )


if __name__ == "__main__":
    main()
