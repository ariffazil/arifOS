#!/usr/bin/env python3
"""
VAULT999 MCP Server - Constitutional Memory Gateway for ChatGPT

Uses FastMCP + Uvicorn with SSL for HTTPS/SSE transport.

Tools:
  - search(query): Search L0_VAULT, L1_LEDGER, L4_WITNESS
  - fetch(id): Retrieve full document by ID

Usage:
    python vault999_server.py

Version: v45.2.0
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

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

# Memory band configuration
BANDS = {
    "L0_VAULT": {
        "path": VAULT_ROOT / "L0_VAULT",
        "confidence": 1.0,
        "tag": "[CANONICAL]",
        "extensions": ["*.md", "*.json"]
    },
    "L1_LEDGER": {
        "path": VAULT_ROOT / "L1_LEDGERS",
        "confidence": 1.0,
        "tag": "[SEALED]",
        "extensions": ["*.jsonl", "*.md"]
    },
    "L4_WITNESS": {
        "path": VAULT_ROOT / "L4_WITNESS",
        "confidence": 0.85,
        "tag": "[OBSERVATION]",
        "extensions": ["*.md"]
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
                        "band": band_name
                    })
            except Exception as e:
                logger.warning(f"Error reading {file}: {e}")

    return results


@mcp.tool()
def search(query: str) -> Dict[str, Any]:
    """Search constitutional memory across L0_VAULT, L1_LEDGER, L4_WITNESS."""
    logger.info(f"Search: '{query}'")

    if not query or len(query.strip()) < 2:
        return {"error": "Query too short", "results": []}

    all_results = []
    for band_name in ["L0_VAULT", "L1_LEDGER", "L4_WITNESS"]:
        all_results.extend(search_band(band_name, query))

    all_results.sort(key=lambda x: -x["confidence"])
    limited = all_results[:MAX_RESULTS]

    logger.info(f"Found {len(all_results)}, returning {len(limited)}")

    return {
        "query": query,
        "total_found": len(all_results),
        "results": limited
    }


@mcp.tool()
def fetch(id: str) -> Dict[str, Any]:
    """Retrieve full document by ID (format: BAND_filename)."""
    logger.info(f"Fetch: '{id}'")

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
                                "canonical": bn == "L0_VAULT"
                            }
                        }
                    except Exception as e:
                        return {"error": str(e)}

    return {"error": f"Not found: {id}"}


def main():
    """Main entry point."""
    print("=" * 70)
    print("  VAULT999 MCP Server v45.2.0")
    print("  Constitutional Memory Gateway for ChatGPT")
    print("=" * 70)
    print(f"  Vault: {VAULT_ROOT}")
    print(f"  URL: https://127.0.0.1:8000/sse/")
    print()
    print("  Tools: search(query), fetch(id)")
    print()
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
        port=8000,
        ssl_certfile=str(SSL_CERT),
        ssl_keyfile=str(SSL_KEY),
        log_level="info"
    )


if __name__ == "__main__":
    main()
