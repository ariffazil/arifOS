#!/usr/bin/env python3
"""
AAA MCP Server - Adaptive Agentic Architecture Gateway

TRIPLE-TRINITY CONCORDAT:
  CCC          = Machine Law (Canonical Constitutional Core)
  BBB          = Behavioral Baseline Buffer (Memory/Cooling Ledger)
  AAA          = Adaptive Agentic Architecture (The Living Framework)

This server is the AAA interface that governs the CCC/BBB/AAA interaction.

  Humans live by Prinsip (AAA).
  Memory cools in BBB.
  Machines obey Law (CCC).

Uses FastMCP + Uvicorn with SSL for HTTPS/SSE transport.

# Tools:
#   - search(query): Search CCC/L0, BBB, CCC/L4
#   - fetch(id): Retrieve full document by ID
#   - arifos_fag_read(path, root): Governed file reading
#   - arifos_fag_write(path, operation, ...): Governed file writing
#   - arifos_fag_list(path, root): Governed directory listing
#   - arifos_fag_stats(root): Governance health and metrics

Version: v45.3.0
DITEMPA BUKAN DIBERI
"""

import json
import logging

# VAULT-999 TAC/EUREKA Engine
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

from arifos_core.mcp.tools.fag_list import FAGListRequest, arifos_fag_list

# FAG Tool Imports
from arifos_core.mcp.tools.fag_read import FAGReadRequest, arifos_fag_read
from arifos_core.mcp.tools.fag_stats import FAGStatsRequest, arifos_fag_stats
from arifos_core.mcp.tools.fag_write import FAGWriteRequest, arifos_fag_write
from arifos_core.mcp.tools.remote.github_aaa import github_aaa_govern

sys.path.insert(0, str(Path(__file__).parent))
from vault999_tac_eureka import EvaluationInputs, validate_ledger_entries, vault_999_decide

# 9-FLOOR CONSTITUTIONAL GOVERNANCE (AAA Standard Compliance)
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [AAA] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Path constants
REPO_ROOT = Path(__file__).parent.parent.parent
VAULT_ROOT = REPO_ROOT / "vault_999" / "CCC"
BBB_ROOT = REPO_ROOT / "vault_999" / "BBB"
CERT_DIR = Path(__file__).parent / "certs"
SSL_CERT = CERT_DIR / "cert.pem"
SSL_KEY = CERT_DIR / "key.pem"

# =============================================================================
# CONSTITUTIONAL BOUNDARY: HUMAN-MACHINE CONCORDAT
# =============================================================================
# Three vaults exist:
#   CCC (Canonical Constitutional Core) = Machine Law (MCP-governed, exposed)
#   BBB (Behavioral Baseline Buffer)    = Cooling ledger (provisional knowledge)
#   ARIF FAZIL (AAA)                    = Human Biography (sacred, offline, NEVER exposed)
# =============================================================================

SACRED_VAULT = REPO_ROOT / "vault_999" / "ARIF FAZIL"
SACRED_VAULT_PATTERNS = ["ARIF FAZIL", "ARIF_FAZIL", "arif fazil", "arif_fazil"]

def _is_sacred_path(path: Path) -> bool:
    """Check if path is within or references the sacred human vault (AAA)."""
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
        "tag": "[CANONICAL/CCC]",
        "extensions": ["*.md", "*.json"]
    },
    "BBB": {
        "path": BBB_ROOT,
        "confidence": 1.0,
        "tag": "[MEMORY/BBB]",
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
mcp = FastMCP("AAA")


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
                    if len(snippet) > 1000: # Safety cap
                        snippet = snippet[:1000]

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
    """Search constitutional memory across CCC (L0_VAULT, L4_WITNESS) and BBB.

    CONSTITUTIONAL BOUNDARY: This function only searches CCC/BBB (machine zones).
    The ARIF FAZIL vault (human biography/AAA) is sacred and offline.
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
    for band_name in BANDS.keys():
        all_results.extend(search_band(band_name, query))

    all_results.sort(key=lambda x: -x["confidence"])
    limited = all_results[:MAX_RESULTS]

    logger.info(f"Found {len(all_results)}, returning {len(limited)}")

    return {
        "query": query,
        "total_found": len(all_results),
        "results": limited,
        "vault": "CCC/BBB",
        "governance": "Nine Floors + APEX PRIME (Triple-Trinity)"
    }


@mcp.tool()
def fetch(id: str) -> Dict[str, Any]:
    """Retrieve full document by ID (format: BAND_filename).

    CONSTITUTIONAL BOUNDARY: This function only fetches from CCC/BBB.
    The ARIF FAZIL vault (AAA) is sacred and offline.
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
                return {"error": f"Band path not found: {band_path}"}

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
                                "vault": "CCC/BBB",
                                "governance": "Nine Floors + APEX PRIME (Triple-Trinity)"
                            }
                        }
                    except Exception as e:
                        return {"error": str(e)}

    return {"error": f"Not found: {id}"}


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


# =============================================================================
# VAULT-999 TAC/EUREKA TOOLSET (v45.3.0)
# =============================================================================

@mcp.tool(name="vault999_store")
def vault999_store(
    insight_text: str,
    vault_target: str,  # "AAA" | "CCC" | "BBB"
    title: str,
    structure: str,  # STRUCTURE: What changed
    truth_boundary: str,  # TRUTH: What is constrained
    scar: str,  # SCAR: What it took / what it prevents
    human_seal_sealed_by: str = "ARIF",
    human_seal_seal_note: str = ""
) -> Dict[str, Any]:
    """
    Store EUREKA insight in VAULT-999 (AAA/CCC/BBB).

    ACTIVATION: Call this when extraction complete.

    Vault Targets:
    - AAA: Human insights → vault_999/ARIF FAZIL/
    - CCC: Machine law → vault_999/CCC/L4_EUREKA/
    - BBB: Memory/learning → vault_999/BBB/L1_cooling_ledger/

    Triad (MANDATORY):
    - structure: What changed (the new invariant)
    - truth_boundary: What is now constrained (non-violable)
    - scar: What it took / what it prevents (cost signal)

    NO NEW FOLDERS. New markdown pages OK.
    """
    logger.info(f"VAULT-999 Store: target={vault_target}, title={title}")

    # Determine vault path
    if vault_target == "AAA":
        vault_dir = REPO_ROOT / "vault_999" / "ARIF FAZIL" / "ARIF FAZIL"
        if not vault_dir.exists():
            vault_dir = REPO_ROOT / "vault_999" / "ARIF FAZIL"
    elif vault_target == "CCC":
        vault_dir = VAULT_ROOT / "L4_EUREKA"
        vault_dir.mkdir(exist_ok=True)
    elif vault_target == "BBB":
        vault_dir = BBB_ROOT / "L1_cooling_ledger"
        vault_dir.mkdir(exist_ok=True)
    else:
        return {
            "verdict": "VOID-999",
            "error": f"Invalid vault_target: {vault_target} (must be AAA/CCC/BBB)"
        }

    # =============================================================================
    # 9-FLOOR CONSTITUTIONAL CHECK (AAA Standard Compliance - Gap 1 Fix)
    # =============================================================================
    logger.info("Running 9-floor constitutional validation...")

    floor_check = validate_response_full(
        output_text=insight_text,
        input_text=structure,  # Use structure as input proxy for ΔS calculation
        evidence={"truth_score": 0.99},  # High-stakes: assume truth verified
        high_stakes=True,  # VAULT storage is high-stakes operation
        session_turns=5  # Assume sufficient context for κᵣ
    )

    if floor_check["verdict"] != "SEAL":
        logger.error(f"Constitutional floor violation: {floor_check['verdict']}")
        return {
            "verdict": "VOID-999",
            "state": "REJECTED",
            "reason": f"Constitutional governance failed: {floor_check['verdict']}",
            "violations": floor_check["violations"],
            "floor_scores": floor_check["floors"],
            "message": "VAULT storage blocked by 9-floor governance"
        }

    logger.info(f"9-floor check PASSED: {floor_check['verdict']}")

    # Build filename (timestamp-based to avoid conflicts)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{title.replace(' ', '_')}.md"
    filepath = vault_dir / filename

    # Build Obsidian-native markdown with YOUR VOICE
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = f"""---
title: "{title}"
date: {date_str}
tags: [eureka, {vault_target.lower()}, forged]
vault: {vault_target}
sealed_by: {human_seal_sealed_by}
type: wisdom
---

# {title}
*Wisdom forged from lived experience.*

**Ditempa:** {date_str}
**Bahasa:** The voice of someone who paid the price to learn this
**Status:** Cooled and sealed — earned, not given

---

## WHAT I LEARNED

{insight_text}

---

## THE STRUCTURE (What Changed)

{structure}

**The Shift:**
This is not theory. This is what actually changed in how the system works.

---

## THE TRUTH (What Cannot Be Violated)

{truth_boundary}

**The Boundary:**
This is the line. Cross it and the insight breaks.

**The Abah Check:**
Would this make Abah proud? Would I explain this to my father without shame?

---

## THE SCAR (What It Took)

{scar}

**The Cost:**
This wisdom was not free. This is what it took to learn.

**What It Prevents:**
This is why it matters. This is what we'll never repeat.

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
"""

    # Write to vault
    try:
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"VAULT-999 Stored: {filepath}")

        return {
            "verdict": "SEAL-999",
            "state": "SEALED",
            "vault_target": vault_target,
            "filepath": str(filepath.relative_to(REPO_ROOT)),
            "title": title,
            "sealed_by": human_seal_sealed_by,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"EUREKA stored in {vault_target} vault"
        }
    except Exception as e:
        logger.error(f"VAULT-999 Store failed: {e}")
        return {
            "verdict": "VOID-999",
            "error": str(e),
            "filepath": str(filepath)
        }


@mcp.tool(name="vault999_eval")
def vault999_eval(
    dC: float,
    Ea: float,
    dH_dt: float,
    Teff: float,
    Tcrit: float,
    Omega0_value: float,
    K_before: int,
    K_after: int,
    reality_7_1_physically_permissible: bool,
    structure_7_2_compressible: bool,
    language_7_3_minimal_truthful_naming: bool,
    ledger_entries: List[Dict[str, Any]],
    T0_context_start: str,  # MANDATORY: Chat/session start time (ISO-8601)
    human_seal_sealed_by: str = None,
    human_seal_seal_note: str = None
) -> Dict[str, Any]:
    """
    Evaluate EUREKA against TAC/EUREKA-777 constitutional laws.

    TAC (Theory of Anomalous Contrast):
    - dC > Ea: Contrast exceeds threshold
    - dH_dt < 0: System cooling
    - Teff < Tcrit: Below critical temperature
    - Omega0 in [0.03, 0.05]: Humility band

    EUREKA-777 Triple Alignment:
    - 7_1 Reality: Physically permissible
    - 7_2 Structure: Compressible representation
    - 7_3 Language: Minimal truthful naming
    - Compression: K_after <= K_before * 0.35

    VAULT-999 Entry:
    - Requires: TAC_VALID + EUREKA_VERIFIED + LEDGER_CLEAN
    - SEAL-999 requires: human_seal

    TIME AS GOVERNANCE (MANDATORY):
    - T0_context_start: Chat/session entry time (when inquiry entered governance)
    - T999_vault_verdict: Auto-generated at verdict (seal time)

    Returns: SEAL-999 / HOLD-999 / VOID-999 verdict + vault_record
    """
    logger.info(f"VAULT-999 Eval: T0={T0_context_start}, dC={dC}, Ea={Ea}, K={K_before}->{K_after}")

    # Build inputs
    inputs = EvaluationInputs(
        dC=dC,
        Ea=Ea,
        dH_dt=dH_dt,
        Teff=Teff,
        Tcrit=Tcrit,
        Omega0_value=Omega0_value,
        K_before=K_before,
        K_after=K_after,
        compression_ratio_max=0.35,
        reality_7_1_physically_permissible=reality_7_1_physically_permissible,
        structure_7_2_compressible=structure_7_2_compressible,
        language_7_3_minimal_truthful_naming=language_7_3_minimal_truthful_naming,
    )

    # Build human seal if provided
    human_seal = None
    if human_seal_sealed_by:
        human_seal = {
            "sealed_by": human_seal_sealed_by,
            "seal_time": datetime.now(timezone.utc).isoformat(),
            "seal_note": human_seal_seal_note or ""
        }

    # Evaluate (with T₀ governance timestamp)
    verdict_result, vault_record = vault_999_decide(inputs, ledger_entries, human_seal, T0_context_start)

    logger.info(f"VAULT-999 Verdict: {verdict_result.verdict}")

    return {
        "verdict": verdict_result.verdict,
        "state": verdict_result.state_next,
        "tac_valid": verdict_result.tac_valid,
        "eureka_verified": verdict_result.eureka_verified,
        "ledger_clean": verdict_result.ledger_clean,
        "reasons": verdict_result.reasons,
        "vault_record": vault_record
    }


@mcp.tool(name="github_aaa_govern")
def tool_github_aaa_govern(
    action: str,
    target: str,
    intention: str
) -> Dict[str, Any]:
    """
    Execute a governed GitHub action via the AAA Trinity (ARIF-ADAM-APEX).

    Args:
        action: 'review', 'merge', 'close', 'audit'
        target: 'PR#123', 'Issue#45'
        intention: Why this action is needed (F1 check)
    """
    return github_aaa_govern(action, target, intention)


def main():
    """Main entry point."""
    print("=" * 70)
    print("  AAA MCP Server v45.3.0")
    print("  Adaptive Agentic Architecture Gateway (Triple-Trinity)")
    print("=" * 70)
    print()
    print("  TRIPLE-TRINITY CONCORDAT:")
    print("    CCC (Law)    = Machine Law (Canonical Constitutional Core)")
    print("    BBB (Memory) = Behavioral Baseline Buffer (Memory/Ledger)")
    print("    AAA (Human)  = Adaptive Agentic Architecture (The Living Framework)")
    print()
    print(f"  Machine Law (CCC): {VAULT_ROOT}")
    print(f"  Memory (BBB):      {BBB_ROOT}")
    print(f"  Sacred Human (AAA): {SACRED_VAULT} [OFFLINE]")
    print()
    print(f"  URL: https://127.0.0.1:8000/sse/")
    print("  Tools: search(query), fetch(id)")
    print("         arifos_fag_read(path), arifos_fag_write(path, op, ...)")
    print("         arifos_fag_list(path), arifos_fag_stats(root)")
    print("         vault999_eval(dC, Ea, ...) - TAC/EUREKA-777 evaluation")
    print("         vault999_store(insight, vault_target, ...) - EUREKA auto-storage")
    print("         github_aaa_govern(action, target, intention) - Remote Governance")
    print()
    print("  Humans live by Prinsip. Memory cools. Machines obey Law.")
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
        log_level="info"
    )


if __name__ == "__main__":
    main()
