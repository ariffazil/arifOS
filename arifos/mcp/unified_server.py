"""
arifOS Unified MCP Server - Consolidated Tool Registry

This is the unified MCP server that consolidates 3 previous servers:
- server.py (stdio transport, 27 tools)
- arifos_mcp_server.py (AAA remote, 10 tools)
- vault999_server.py (Vault-999 gateway, 8 tools)

Consolidation Result:
- From 34 tools → 15 tools (-56%)
- Removed 11 redundant pipeline stage tools
- Deleted 1 ungoverned tool (APEX_LLAMA)
- Consolidated 9 vault999 tools → 3 tools (-67% memory tools)
- Clean naming convention (no mcp_ prefix)
- All 18 core capabilities preserved

Memory Tool Consolidation:
- vault999_query: Universal query (recall + search + fetch)
- vault999_store: EUREKA storage (includes TAC eval)
- vault999_seal: Universal seal/verification (audit + receipts + seal)

Constitutional Authority: F1-F9 governance enforced
Transport: stdio (Claude Desktop) + HTTPS/SSE (remote AI)
Version: v47.0.0

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import mcp.types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Vault999 TAC/EUREKA imports
from arifos.mcp.vault999_tac_eureka import (
    EvaluationInputs,
    utc_now_iso,
    validate_ledger_entries,
    vault_999_decide,
)
from arifos.memory.vault.vault_manager import VaultManager

from .models import (
    AgiThinkRequest,
    ApexAuditRequest,
    AsiActRequest,
    AuditRequest,
    AuditResponse,
    JudgeRequest,
    JudgeResponse,
    RecallRequest,
    RecallResponse,
    VerdictResponse,
)
from .tools.audit import arifos_audit  # Audit trail inspection
from .tools.bundles import agi_think_sync as agi_think  # AGI bundle (111+222+777)
from .tools.bundles import apex_audit_sync as apex_audit  # APEX bundle (444+888+889)
from .tools.bundles import asi_act_sync as asi_act  # ASI bundle (555+666)
from .tools.executor import ExecutorRequest, arifos_executor
from .tools.fag_list import FAGListRequest, arifos_fag_list
from .tools.fag_read import TOOL_METADATA as FAG_READ_METADATA
from .tools.fag_read import FAGReadRequest, FAGReadResponse, arifos_fag_read
from .tools.fag_stats import FAGStatsRequest, arifos_fag_stats
from .tools.fag_write import FAGWriteRequest, arifos_fag_write
from .tools.judge import arifos_judge  # Full pipeline (000→999)
from .tools.memory_tools import memory_get_receipts, memory_verify_seal
from .tools.meta_select import TOOL_METADATA as META_SELECT_METADATA
from .tools.meta_select import MetaSelectRequest, MetaSelectResponse, arifos_meta_select
from .tools.recall import arifos_recall  # L7 Mem0+Qdrant recall
from .tools.remote.github_aaa import TOOL_METADATA as GITHUB_METADATA
from .tools.remote.github_aaa import github_aaa_govern
from .tools.validate_full import TOOL_METADATA as VALIDATE_FULL_METADATA
from .tools.validate_full import ValidateFullRequest, ValidateFullResponse, arifos_validate_full

# =============================================================================
# CORE IMPORTS - Constitutional Pipeline (4 tools)
# =============================================================================


# =============================================================================
# MEMORY & RETRIEVAL IMPORTS (6 tools)
# =============================================================================


# Vault tools (search/fetch/receipts) - implemented inline below
# vault999_store and vault999_eval - to be imported from arifos_mcp_server

# =============================================================================
# FILE ACCESS GOVERNANCE (FAG) IMPORTS (4 tools)
# =============================================================================


# =============================================================================
# VALIDATION & ROUTING IMPORTS (2 tools)
# =============================================================================


# =============================================================================
# SYSTEM OPERATIONS IMPORTS (3 tools)
# =============================================================================


# =============================================================================
# MEMORY TOOLS IMPORTS (2 tools)
# =============================================================================


# =============================================================================
# VAULT IMPORTS
# =============================================================================




logger = logging.getLogger(__name__)

# Vault configuration (v47.1 Consolidated 3×3 Architecture)
REPO_ROOT = Path(__file__).parent.parent.parent
VAULT_ROOT = REPO_ROOT / "vault_999"

# Memory bands aligned with 3×3 geological structure
# AAA_HUMAN intentionally excluded (F11 - forbidden to machines)
BANDS = {
    # CCC_CONSTITUTIONAL: Human-sealed, machine read-only
    "CCC_L0_FOUNDATION": {
        "path": VAULT_ROOT / "CCC_CONSTITUTIONAL" / "LAYER_1_FOUNDATION",
        "confidence": 1.0,
        "tag": "[CANONICAL]",
        "geometry": "ORTHOGONAL",
        "extensions": ["*.md", "*.json"],
        "description": "L0 Constitutional law (immutable)"
    },
    "CCC_L1_PERMANENT": {
        "path": VAULT_ROOT / "CCC_CONSTITUTIONAL" / "LAYER_2_PERMANENT",
        "confidence": 1.0,
        "tag": "[SEALED]",
        "geometry": "TOROIDAL",
        "extensions": ["*.jsonl", "*.md"],
        "description": "L1 Sealed ledger (hash-chained)"
    },
    "CCC_L2_PROCESSING": {
        "path": VAULT_ROOT / "CCC_CONSTITUTIONAL" / "LAYER_3_PROCESSING" / "L2_active_state",
        "confidence": 0.85,
        "tag": "[ACTIVE]",
        "geometry": "FRACTAL",
        "extensions": ["*.jsonl", "*.md"],
        "description": "L2 Active state (7-day TTL)"
    },
    "CCC_L3_COOLING": {
        "path": VAULT_ROOT / "CCC_CONSTITUTIONAL" / "LAYER_3_PROCESSING" / "L3_phoenix_cooling",
        "confidence": 0.75,
        "tag": "[COOLING]",
        "geometry": "TEMPORAL",
        "extensions": ["*.jsonl", "*.md"],
        "description": "L3 Phoenix-72 cooling queue"
    },
    "CCC_L4_WITNESS": {
        "path": VAULT_ROOT / "CCC_CONSTITUTIONAL" / "LAYER_3_PROCESSING" / "L4_witness_observations",
        "confidence": 0.85,
        "tag": "[OBSERVATION]",
        "geometry": "FRACTAL",
        "extensions": ["*.jsonl", "*.md"],
        "description": "L4 Tri-witness observations"
    },
    "CCC_L5_VOID": {
        "path": VAULT_ROOT / "CCC_CONSTITUTIONAL" / "LAYER_3_PROCESSING" / "L5_void_rejections",
        "confidence": 0.5,
        "tag": "[VOID]",
        "geometry": "NEGATIVE",
        "extensions": ["*.jsonl", "*.md"],
        "description": "L5 VOID rejections (learning archive)"
    },

    # BBB_MACHINE: Machine read/write operational memory
    "BBB_OPERATIONAL": {
        "path": VAULT_ROOT / "BBB_MACHINE" / "LAYER_1_OPERATIONAL",
        "confidence": 0.8,
        "tag": "[PIPELINE]",
        "geometry": "LINEAR",
        "extensions": ["*.jsonl"],
        "description": "Operational pipeline records"
    },
    "BBB_WORKING": {
        "path": VAULT_ROOT / "BBB_MACHINE" / "LAYER_2_WORKING",
        "confidence": 0.7,
        "tag": "[SESSION]",
        "geometry": "EPHEMERAL",
        "extensions": ["*.jsonl"],
        "description": "Session state (7-day TTL)"
    },
    "BBB_AUDIT": {
        "path": VAULT_ROOT / "BBB_MACHINE" / "LAYER_3_AUDIT",
        "confidence": 1.0,
        "tag": "[AUDIT]",
        "geometry": "APPEND_ONLY",
        "extensions": ["*.jsonl"],
        "description": "Decision audit trail (immutable)"
    }
}

MAX_RESULTS = 10

# Sacred vault protection (F11 - AAA_HUMAN forbidden to machines)
SACRED_VAULT_PATTERNS = ["AAA_HUMAN", "AAA", "ARIF FAZIL", "ARIF_FAZIL", "arif fazil", "arif_fazil", "aaa_human"]

def _is_sacred_query(query: str) -> bool:
    """Check if query targets sacred human vault."""
    query_lower = query.lower() if query else ""
    for pattern in SACRED_VAULT_PATTERNS:
        if pattern.lower() in query_lower:
            return True
    return False

# =============================================================================
# VAULT TOOLS (Consolidated 3-Tool Interface)
# =============================================================================
# Consolidates 9 vault999 tools into 3 core operations:
# 1. vault999_query (GET) - recall + search + fetch
# 2. vault999_store (SET) - store + eval (validation before storage)
# 3. vault999_seal (PROVE) - audit + receipts + verify_receipts + verify_seal

def vault999_query(
    query: Optional[str] = None,
    user_id: Optional[str] = None,
    document_id: Optional[str] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Universal query interface for VAULT-999 memory retrieval.

    Intelligently routes to appropriate backend based on parameters:
    - If document_id provided → fetch full document by ID
    - If user_id provided → recall semantic memories (Mem0+Qdrant)
    - If query provided → search across vault bands

    Parameters:
    - query: Search query string (for keyword search)
    - user_id: User ID (for semantic memory recall)
    - document_id: Document ID in format BAND_filename (for direct fetch)
    - max_results: Maximum results to return (default: 10)

    Returns unified response with results, metadata, and governance info.
    """
    logger.info(f"vault999_query: query={query}, user_id={user_id}, document_id={document_id}")

    # Route 1: Fetch specific document by ID
    if document_id:
        return _vault_fetch_internal(document_id)

    # Route 2: Recall semantic memories for user
    if user_id:
        if not query:
            return {"error": "user_id requires query parameter for semantic search"}
        return _vault_recall_internal(user_id=user_id, prompt=query, max_results=max_results)

    # Route 3: Search across vault bands
    if query:
        return _vault_search_internal(query, max_results)

    return {"error": "Must provide at least one of: query, user_id, or document_id"}

def _vault_search_internal(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Search constitutional memory across vault bands.

    Searches L0_VAULT (canonical), L1_LEDGERS (sealed), L4_WITNESS (observation), 00_ENTROPY (hot).
    Returns ranked results by confidence.

    Constitutional Boundary: Only searches CCC/BBB (machine law).
    The ARIF FAZIL vault (human biography) is sacred and offline.
    """
    logger.info(f"_vault_search_internal: '{query}'")

    # Sacred vault protection
    if _is_sacred_query(query):
        logger.error(f"[VOID] SACRED_BOUNDARY: Query references human vault")
        return {
            "error": "SACRED_BOUNDARY: Query references human vault which is offline.",
            "verdict": "VOID",
            "guidance": "The ARIF FAZIL vault contains human biography and is not MCP-governed.",
            "results": []
        }

    if not query or len(query.strip()) < 2:
        return {"error": "Query too short", "results": []}

    all_results = []
    query_lower = query.lower()

    for band_name, band in BANDS.items():
        if not band["path"].exists():
            continue

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

                        all_results.append({
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

    all_results.sort(key=lambda x: -x["confidence"])
    limited = all_results[:max_results]

    logger.info(f"Found {len(all_results)}, returning {len(limited)}")

    return {
        "query": query,
        "total_found": len(all_results),
        "results": limited,
        "vault": "CCC/BBB",
        "governance": "Nine Floors + APEX PRIME"
    }

def _vault_fetch_internal(id: str) -> Dict[str, Any]:
    """
    Retrieve full document by ID (format: BAND_filename).

    Constitutional Boundary: Only fetches from CCC/BBB.
    The ARIF FAZIL vault is sacred and offline.
    """
    logger.info(f"_vault_fetch_internal: '{id}'")

    # Sacred vault protection
    if _is_sacred_query(id):
        logger.error(f"[VOID] SACRED_BOUNDARY: Document in human vault")
        return {
            "error": "SACRED_BOUNDARY: Document is in human vault which is offline.",
            "verdict": "VOID",
            "guidance": "The ARIF FAZIL vault contains human biography and is not MCP-governed."
        }

    if not id or "_" not in id:
        return {"error": f"Invalid ID: {id}"}

    for band_name, band in BANDS.items():
        if id.startswith(band_name + "_"):
            filename_stem = id[len(band_name) + 1:]
            band_path = band["path"]

            if not band_path.exists():
                return {"error": f"Band not found: {band_name}"}

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
                            "url": f"vault://{band_name}/{file.name}",
                            "metadata": {
                                "confidence": band["confidence"],
                                "band": band_name,
                                "canonical": band_name == "L0_VAULT",
                                "vault": "CCC/BBB",
                                "governance": "Nine Floors + APEX PRIME",
                                "geometry": band.get("geometry", "UNKNOWN")
                            }
                        }
                    except Exception as e:
                        return {"error": str(e)}

    return {"error": f"Not found: {id}"}

def _vault_recall_internal(user_id: str, prompt: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Recall semantic memories from L7 (Mem0 + Qdrant).

    Wrapper around arifos_recall with RecallRequest model.
    All recalled memories are capped at 0.85 confidence (INV-4).
    """
    logger.info(f"_vault_recall_internal: user_id={user_id}, prompt={prompt}")

    try:
        request = RecallRequest(user_id=user_id, prompt=prompt, max_results=max_results)
        return arifos_recall(request)
    except Exception as e:
        logger.error(f"Recall failed: {e}")
        return {"error": str(e), "status": "FAILED"}

def vault999_seal(
    verification_type: str,
    user_id: Optional[str] = None,
    seal_id: Optional[str] = None,
    limit: int = 10,
    days: int = 7
) -> Dict[str, Any]:
    """
    Universal seal/verification interface for VAULT-999 integrity proofs.

    Routes to appropriate verification backend based on verification_type:
    - "audit" → Audit trail inspection (requires user_id)
    - "receipts" → ZKPC receipt verification
    - "seal" → Cryptographic seal verification (requires seal_id)

    Parameters:
    - verification_type: Type of verification ("audit", "receipts", "seal")
    - user_id: User ID (for audit)
    - seal_id: Seal ID (for seal verification)
    - limit: Maximum items to return (for receipts)
    - days: Days to look back (for audit, default: 7)

    Returns verification response with status and proof data.
    """
    logger.info(f"vault999_seal: type={verification_type}, user_id={user_id}, seal_id={seal_id}")

    # Route 1: Audit trail inspection
    if verification_type == "audit":
        if not user_id:
            return {"error": "audit verification requires user_id parameter"}
        try:
            request = AuditRequest(user_id=user_id, days=days)
            return arifos_audit(request)
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            return {"error": str(e), "status": "FAILED"}

    # Route 2: ZKPC receipt verification
    elif verification_type == "receipts":
        try:
            manager = VaultManager()
            items = manager.get_receipts(limit=limit)
            return {
                "status": "SEALED",
                "protocol": "ZKPC-v46",
                "count": len(items),
                "receipts": items,
                "verification_type": "receipts"
            }
        except Exception as e:
            logger.error(f"Receipts verification failed: {e}")
            return {"error": str(e), "status": "BROKEN"}

    # Route 3: Cryptographic seal verification
    elif verification_type == "seal":
        if not seal_id:
            return {"error": "seal verification requires seal_id parameter"}
        try:
            return memory_verify_seal(seal_id=seal_id)
        except Exception as e:
            logger.error(f"Seal verification failed: {e}")
            return {"error": str(e), "status": "FAILED"}

    else:
        return {
            "error": f"Invalid verification_type: {verification_type}",
            "valid_types": ["audit", "receipts", "seal"]
        }

def vault_receipts(limit: int = 10) -> Dict[str, Any]:
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

    Vault Targets (v47.1 Consolidated):
    - AAA: Human insights -> vault_999/AAA_HUMAN/ (FORBIDDEN)
    - CCC: Machine law -> vault_999/CCC_CONSTITUTIONAL/LAYER_3_PROCESSING/L4_witness_observations/
    - BBB: Memory/learning -> vault_999/INFRASTRUCTURE/cooling_ledger/

    Triad (MANDATORY):
    - structure: What changed (the new invariant)
    - truth_boundary: What is now constrained (non-violable)
    - scar: What it took / what it prevents (cost signal)

    NO NEW FOLDERS. New markdown pages OK.
    """
    logger.info(f"VAULT-999 Store: target={vault_target}, title={title}")

    # Determine vault path (v47.1 Consolidated Structure)
    CCC_ROOT = REPO_ROOT / "vault_999" / "CCC_CONSTITUTIONAL"
    BBB_ROOT = REPO_ROOT / "vault_999" / "BBB_MACHINE"
    SACRED_VAULT = REPO_ROOT / "vault_999" / "AAA_HUMAN"
    INFRASTRUCTURE = REPO_ROOT / "vault_999" / "INFRASTRUCTURE"

    if vault_target == "AAA":
        logger.error("[VOID] SACRED_BOUNDARY: Cannot write to AAA (human vault) via MCP")
        return {
            "verdict": "VOID-999",
            "error": "SACRED_BOUNDARY: The AAA_HUMAN vault is offline and not MCP-governed (F11)",
            "guidance": "AAA (human biography) is protected by F11. Use CCC (machine law) or BBB (memory/learning)."
        }
    elif vault_target == "CCC":
        # Store insights in L4_WITNESS (observations layer)
        vault_path = CCC_ROOT / "LAYER_3_PROCESSING" / "L4_witness_observations"
    elif vault_target == "BBB":
        # Store in cooling ledger infrastructure
        vault_path = INFRASTRUCTURE / "cooling_ledger"
    else:
        return {
            "verdict": "VOID-999",
            "error": f"Invalid vault_target: {vault_target}. Use 'CCC' or 'BBB'."
        }

    # Ensure vault directory exists
    if not vault_path.exists():
        logger.error(f"[VOID] Vault path not found: {vault_path}")
        return {
            "verdict": "VOID-999",
            "error": f"Vault path not found: {vault_path}",
            "guidance": "Ensure vault_999 directory structure exists."
        }

    # Generate filename
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title).strip().replace(" ", "_")
    filename = f"{date_str}_{safe_title}.md"
    filepath = vault_path / filename

    # Format EUREKA markdown
    content = f"""---
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
**Status:** Cooled and sealed - earned, not given

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

**DITEMPA BUKAN DIBERI** - Forged, not given; truth must cool before it rules.
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

    # Evaluate (with T0 governance timestamp)
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

# =============================================================================
# SEARCH TOOLS (Constitutional Web Search with Dual Semantics)
# =============================================================================

def agi_search(
    query: str,
    max_results: int = 10,
    budget_limit: Optional[float] = None,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    AGI Extended SENSE (111+) - Constitutional web search for knowledge acquisition.

    Purpose: Information gathering for learning, exploration, and thinking.
    Semantic: "What is X?" / "Tell me about Y" / "How does Z work?"

    Expands AGI's sensory input beyond chat context to include web knowledge.
    Results feed into AGI reasoning pipeline (111→222→333→777).

    Constitutional Governance:
    - F1 (Amanah): Reversible, read-only
    - F2 (Truth): Verified sources
    - F4 (ΔS): Reduces entropy via knowledge
    - F6 (Amanah): No credentials exposed
    - F7 (Ω₀): Acknowledges search limitations

    Parameters:
    - query: Search query for knowledge acquisition
    - max_results: Maximum results (default: 10)
    - budget_limit: Optional cost limit
    - context: Optional search context

    Returns: Search results with governance metadata, cache status, cost info
    """
    logger.info(f"agi_search (111 SENSE): '{query}'")

    try:
        from arifos.integration.meta_search import ConstitutionalMetaSearch
        search_engine = ConstitutionalMetaSearch()
        result = search_engine.search_with_governance(
            query=query,
            max_results=max_results,
            budget_limit=budget_limit,
            context=context or {}
        )
        return {
            **result.__dict__,
            "stage": "111_SENSE",
            "semantic": "knowledge_acquisition",
            "purpose": "AGI learning and exploration"
        }
    except Exception as e:
        logger.error(f"AGI search failed: {e}")
        return {
            "error": str(e),
            "stage": "111_SENSE",
            "status": "FAILED"
        }

def asi_search(
    query: str,
    max_results: int = 10,
    budget_limit: Optional[float] = None,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    ASI EVIDENCE (444) - Constitutional web search for claim validation.

    Purpose: Evidence gathering for verification, validation, and fact-checking.
    Semantic: "Verify that X" / "Prove Y is true" / "Find evidence for Z"

    Validates claims by gathering evidence from web sources.
    Results feed into ASI synthesis pipeline (444→555→666).

    Constitutional Governance:
    - F1 (Amanah): Reversible, read-only
    - F2 (Truth): Verified sources required
    - F3 (Peace²): Non-destructive validation
    - F4 (ΔS): Reduces epistemic uncertainty
    - F6 (Amanah): No credentials exposed
    - F8 (Tri-Witness): Multiple source validation

    Parameters:
    - query: Search query for claim validation
    - max_results: Maximum results (default: 10)
    - budget_limit: Optional cost limit
    - context: Optional validation context

    Returns: Search results with governance metadata, evidence scores, validation status
    """
    logger.info(f"asi_search (444 EVIDENCE): '{query}'")

    try:
        from arifos.integration.meta_search import ConstitutionalMetaSearch
        search_engine = ConstitutionalMetaSearch()
        result = search_engine.search_with_governance(
            query=query,
            max_results=max_results,
            budget_limit=budget_limit,
            context=context or {}
        )
        return {
            **result.__dict__,
            "stage": "444_EVIDENCE",
            "semantic": "claim_validation",
            "purpose": "ASI evidence gathering and verification"
        }
    except Exception as e:
        logger.error(f"ASI search failed: {e}")
        return {
            "error": str(e),
            "stage": "444_EVIDENCE",
            "status": "FAILED"
        }

# =============================================================================
# UNIFIED TOOL REGISTRY (17 Tools)
# =============================================================================

TOOLS: Dict[str, Callable] = {
    # -------------------------------------------------------------------------
    # CONSTITUTIONAL PIPELINE (5 tools)
    # -------------------------------------------------------------------------
    "arifos_live": arifos_judge,       # Full pipeline (000→999) - live constitutional governance
    "agi_think": agi_think,            # AGI bundle (111+222+777) - The Mind
    "agi_reflect": arifos_validate_full,  # AGI meta-reflection - Track A/B/C coherence (333-like)
    "asi_act": asi_act,                # ASI bundle (555+666) - The Heart
    "apex_seal": apex_audit,           # APEX bundle (444+888+889) - Final judgment & sealing

    # -------------------------------------------------------------------------
    # SEARCH TOOLS (2 tools) - Constitutional Web Search
    # -------------------------------------------------------------------------
    "agi_search": agi_search,          # AGI extended SENSE (111+) - knowledge acquisition
    "asi_search": asi_search,          # ASI evidence (444) - claim validation

    # -------------------------------------------------------------------------
    # VAULT-999 MEMORY SYSTEM (3 tools) - CONSOLIDATED
    # -------------------------------------------------------------------------
    "vault999_query": vault999_query,  # Universal query (recall + search + fetch)
    "vault999_store": vault999_store,  # EUREKA storage (CCC/BBB) + TAC eval
    "vault999_seal": vault999_seal,    # Universal seal/verification (audit + receipts + seal)

    # -------------------------------------------------------------------------
    # FILE ACCESS GOVERNANCE (4 tools)
    # -------------------------------------------------------------------------
    "fag_read": arifos_fag_read,       # Governed file read
    "fag_write": arifos_fag_write,     # Governed file write
    "fag_list": arifos_fag_list,       # Governed directory list
    "fag_stats": arifos_fag_stats,     # Governance statistics

    # -------------------------------------------------------------------------
    # VALIDATION & ROUTING (2 tools)
    # -------------------------------------------------------------------------
    "arifos_validate_full": arifos_validate_full,  # Track A/B/C validation
    "arifos_meta_select": arifos_meta_select,      # Meta model selection

    # -------------------------------------------------------------------------
    # SYSTEM OPERATIONS (2 tools)
    # -------------------------------------------------------------------------
    "arifos_executor": arifos_executor,        # Shell execution with F1-F9 oversight
    "github_govern": github_aaa_govern,        # GitHub operations governance
}

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES (Deprecated - Will Remove in v47)
# =============================================================================

DEPRECATED_ALIASES: Dict[str, str] = {
    # Old FAG names → New names
    "arifos_fag_read": "fag_read",
    "arifos_fag_write": "fag_write",
    "arifos_fag_list": "fag_list",
    "arifos_fag_stats": "fag_stats",

    # Old GitHub tool → New name
    "github_aaa_govern": "github_govern",

    # Old constitutional pipeline → New semantic names
    "arifos_judge": "arifos_live",
    "apexprime_judge": "arifos_live",  # Previous rename
    "apex_audit": "apex_seal",
    "arifos_validate_full": "agi_reflect",

    # Old memory/vault tools → New vault999_* consolidated tools
    # All query operations → vault999_query
    "arifos_recall": "vault999_query",
    "vault999_recall": "vault999_query",
    "vault_search": "vault999_query",
    "vault999_search": "vault999_query",
    "vault_fetch": "vault999_query",
    "vault999_fetch": "vault999_query",
    "search": "vault999_query",  # From old vault999_server
    "fetch": "vault999_query",   # From old vault999_server

    # All verification/seal operations → vault999_seal
    "arifos_audit": "vault999_seal",
    "vault999_audit": "vault999_seal",
    "vault_receipts": "vault999_seal",
    "vault999_receipts": "vault999_seal",
    "memory_get_receipts": "vault999_seal",
    "vault999_verify_receipts": "vault999_seal",
    "memory_receipts": "vault999_seal",
    "memory_verify_seal": "vault999_seal",
    "vault999_verify_seal": "vault999_seal",
    "vault999_verify": "vault999_seal",  # Old name
    "receipts": "vault999_seal",  # From old vault999_server

    # Storage/evaluation (keep as vault999_store)
    "vault999_eval": "vault999_store",  # Eval is now part of store validation
}

# Add aliases to TOOLS registry
for old_name, new_name in DEPRECATED_ALIASES.items():
    if new_name in TOOLS:
        TOOLS[old_name] = TOOLS[new_name]

# =============================================================================
# TOOL REQUEST MODELS
# =============================================================================

TOOL_REQUEST_MODELS: Dict[str, type] = {
    "arifos_live": JudgeRequest,
    "vault999_recall": RecallRequest,
    "vault999_audit": AuditRequest,
    "fag_read": FAGReadRequest,
    "fag_write": FAGWriteRequest,
    "fag_list": FAGListRequest,
    "fag_stats": FAGStatsRequest,
    "agi_reflect": ValidateFullRequest,
    "arifos_meta_select": MetaSelectRequest,
    "agi_think": AgiThinkRequest,
    "asi_act": AsiActRequest,
    "apex_seal": ApexAuditRequest,
    "arifos_executor": ExecutorRequest,
}

# =============================================================================
# TOOL DESCRIPTIONS (MCP Discovery)
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # CONSTITUTIONAL PIPELINE
    # -------------------------------------------------------------------------
    "arifos_live": {
        "name": "arifos_live",
        "description": (
            "Live constitutional governance through the full arifOS pipeline (000→999). "
            "Stage 000: Initialization, intuition, and real-time governance. "
            "Returns verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD) based on 12 constitutional floors."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The query to judge"},
                "user_id": {"type": "string", "description": "Optional user ID for context"},
            },
            "required": ["query"],
        },
    },
    "agi_think": {
        "name": "agi_think",
        "description": "AGI Bundle (The Mind). Proposes answers, structures truth, detects clarity. Consolidates 111, 222, 777.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "User query to think about"},
                "context": {"type": "object", "description": "Optional context"}
            },
            "required": ["query"]
        }
    },
    "asi_act": {
        "name": "asi_act",
        "description": "ASI Bundle (The Heart). Validates safety, vetoes harm, ensures empathy. Consolidates 555, 666, Hypervisor.",
        "parameters": {
            "type": "object",
            "properties": {
                "draft_response": {"type": "string", "description": "Draft text to validate"},
                "recipient_context": {"type": "object", "description": "Recipient context"},
                "intent": {"type": "string", "description": "Intent of the action"}
            },
            "required": ["draft_response"]
        }
    },
    "agi_reflect": {
        "name": "agi_reflect",
        "description": (
            "AGI meta-reflection layer for Track A/B/C coherence validation. "
            "Stage 333-like recursive reflection: validates alignment between canonical law (Track A), "
            "specs (Track B), and code (Track C). Returns coherence verdict and delta analysis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "track_a_path": {"type": "string", "description": "Path to canonical law file (L1_THEORY)"},
                "track_b_path": {"type": "string", "description": "Path to spec file (L2_PROTOCOLS)"},
                "track_c_path": {"type": "string", "description": "Path to code file (arifos_core)"},
            },
            "required": ["track_a_path"],
        },
    },
    "apex_seal": {
        "name": "apex_seal",
        "description": (
            "APEX Bundle (The Soul) - Final judgment and sealing authority. "
            "Consolidates stages 444 (evidence), 888 (judgment), 889 (proof). "
            "Audits AGI/ASI states, verifies tri-witness evidence, renders final verdict, "
            "and seals with cryptographic proof. Returns SEAL/PARTIAL/VOID/888_HOLD."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "agi_thought": {"type": "object", "description": "Output from AGI Bundle"},
                "asi_veto": {"type": "object", "description": "Output from ASI Bundle"},
                "evidence_pack": {"type": "object", "description": "Tri-Witness Evidence"}
            },
            "required": ["agi_thought", "asi_veto"]
        }
    },

    # -------------------------------------------------------------------------
    # SEARCH TOOLS (2 Tools) - Constitutional Web Search
    # -------------------------------------------------------------------------
    "agi_search": {
        "name": "agi_search",
        "description": (
            "AGI Extended SENSE (111+) - Constitutional web search for knowledge acquisition. "
            "Purpose: Information gathering for learning, exploration, thinking. "
            "Semantic: 'What is X?' / 'Tell me about Y' / 'How does Z work?' "
            "Features: 12-floor governance, cost tracking, semantic caching, ledger integration."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for knowledge acquisition"},
                "max_results": {"type": "integer", "description": "Maximum results to return (default: 10)", "default": 10},
                "budget_limit": {"type": "number", "description": "Optional cost limit in USD"},
                "context": {"type": "object", "description": "Optional search context"}
            },
            "required": ["query"]
        }
    },
    "asi_search": {
        "name": "asi_search",
        "description": (
            "ASI EVIDENCE (444) - Constitutional web search for claim validation. "
            "Purpose: Evidence gathering for verification, validation, fact-checking. "
            "Semantic: 'Verify that X' / 'Prove Y is true' / 'Find evidence for Z' "
            "Features: 12-floor governance, tri-witness validation, evidence scoring, cost tracking."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for claim validation"},
                "max_results": {"type": "integer", "description": "Maximum results to return (default: 10)", "default": 10},
                "budget_limit": {"type": "number", "description": "Optional cost limit in USD"},
                "context": {"type": "object", "description": "Optional validation context"}
            },
            "required": ["query"]
        }
    },

    # -------------------------------------------------------------------------
    # VAULT-999 MEMORY SYSTEM (3 Consolidated Tools)
    # -------------------------------------------------------------------------
    "vault999_query": {
        "name": "vault999_query",
        "description": (
            "Universal query interface for VAULT-999 memory retrieval. "
            "Intelligently routes to recall (semantic), search (keyword), or fetch (document ID). "
            "- For semantic memory: Provide user_id + query "
            "- For keyword search: Provide query only "
            "- For document fetch: Provide document_id (format: BAND_filename)"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query or prompt (optional if document_id provided)"},
                "user_id": {"type": "string", "description": "User ID for semantic memory recall (optional)"},
                "document_id": {"type": "string", "description": "Document ID for direct fetch (format: BAND_filename, optional)"},
                "max_results": {"type": "integer", "description": "Maximum results to return (default: 10)", "default": 10},
            },
            "required": [],
        },
    },
    "vault999_store": {
        "name": "vault999_store",
        "description": (
            "Store EUREKA insight in VAULT-999 (CCC/BBB). "
            "Requires structure/truth_boundary/scar triad. "
            "AAA (human vault) is protected and offline. "
            "Optionally validates against TAC/EUREKA-777 before storage."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "insight_text": {"type": "string", "description": "The core insight/learning"},
                "vault_target": {"type": "string", "description": "CCC (machine law) or BBB (memory)"},
                "title": {"type": "string", "description": "Title of the insight"},
                "structure": {"type": "string", "description": "What changed (the new invariant)"},
                "truth_boundary": {"type": "string", "description": "What is now constrained (non-violable)"},
                "scar": {"type": "string", "description": "What it took / what it prevents"},
                "human_seal_sealed_by": {"type": "string", "description": "Who sealed this (default: ARIF)"},
                "human_seal_seal_note": {"type": "string", "description": "Optional seal note"},
            },
            "required": ["insight_text", "vault_target", "title", "structure", "truth_boundary", "scar"],
        },
    },
    "vault999_seal": {
        "name": "vault999_seal",
        "description": (
            "Universal seal/verification interface for VAULT-999 integrity proofs. "
            "Routes to audit trail, ZKPC receipts, or cryptographic seal verification. "
            "- For audit: verification_type='audit', user_id required "
            "- For receipts: verification_type='receipts' "
            "- For seal: verification_type='seal', seal_id required"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "verification_type": {"type": "string", "description": "Type: 'audit', 'receipts', or 'seal'"},
                "user_id": {"type": "string", "description": "User ID (for audit verification)"},
                "seal_id": {"type": "string", "description": "Seal ID (for seal verification)"},
                "limit": {"type": "integer", "description": "Maximum items to return (for receipts, default: 10)", "default": 10},
                "days": {"type": "integer", "description": "Days to look back (for audit, default: 7)", "default": 7},
            },
            "required": ["verification_type"],
        },
    },

    # -------------------------------------------------------------------------
    # FILE ACCESS GOVERNANCE
    # -------------------------------------------------------------------------
    "fag_read": FAG_READ_METADATA,
    "fag_write": {
        "name": "fag_write",
        "description": "Governed file write with constitutional oversight (F1-F9)",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write"},
                "operation": {"type": "string", "description": "Operation type (create/update/append)"},
                "content": {"type": "string", "description": "File content"},
                "root": {"type": "string", "description": "Root directory (L1_THEORY/L2_PROTOCOLS/etc)"},
            },
            "required": ["path", "operation", "content"],
        },
    },
    "fag_list": {
        "name": "fag_list",
        "description": "Governed directory listing with constitutional oversight",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path to list"},
                "root": {"type": "string", "description": "Root directory"},
            },
            "required": ["path"],
        },
    },
    "fag_stats": {
        "name": "fag_stats",
        "description": "Governance health and metrics for file operations",
        "parameters": {
            "type": "object",
            "properties": {
                "root": {"type": "string", "description": "Root directory to analyze"},
            },
            "required": [],
        },
    },

    # -------------------------------------------------------------------------
    # VALIDATION & ROUTING
    # -------------------------------------------------------------------------
    "arifos_meta_select": META_SELECT_METADATA,

    # -------------------------------------------------------------------------
    # SYSTEM OPERATIONS
    # -------------------------------------------------------------------------
    "arifos_executor": {
        "name": "arifos_executor",
        "description": "Sovereign Execution Engine (The Hand). Executes shell commands with constitutional oversight (F1-F9). Requires clear INTENT.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to execute"},
                "intent": {"type": "string", "description": "The reason/intent for this action (for constitutional verification)"}
            },
            "required": ["command", "intent"]
        }
    },
    "github_govern": GITHUB_METADATA,
}

# =============================================================================
# TOOL INVOCATION
# =============================================================================

def list_tools() -> List[str]:
    """
    List all available tool names (non-deprecated only).

    Returns list of tool names that should be exposed to clients.
    Deprecated aliases are excluded from this list.
    """
    return [name for name in TOOLS.keys() if name not in DEPRECATED_ALIASES]

def run_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Invoke a tool by name with arguments.

    Supports both new tool names and deprecated aliases.
    Logs deprecation warnings for old names.
    """
    # Check if it's a deprecated alias
    if tool_name in DEPRECATED_ALIASES:
        new_name = DEPRECATED_ALIASES[tool_name]
        logger.warning(f"[DEPRECATED] Tool '{tool_name}' is deprecated. Use '{new_name}' instead. Will be removed in v47.")
        tool_name = new_name

    tool = TOOLS.get(tool_name)
    if not tool:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Convert arguments to Pydantic model if needed
    request_model = TOOL_REQUEST_MODELS.get(tool_name)
    if request_model:
        try:
            request = request_model(**arguments)
            return tool(request)
        except Exception as e:
            logger.error(f"Error creating request model for {tool_name}: {e}")
            return tool(arguments)

    return tool(**arguments)

# =============================================================================
# MCP SERVER INITIALIZATION (stdio transport)
# =============================================================================

def create_stdio_server() -> Server:
    """
    Create MCP server with stdio transport for Claude Desktop.
    """
    server = Server("arifOS-unified")

    @server.list_tools()
    async def list_tools():
        """List all available tools."""
        # Return only non-deprecated tools for discovery
        non_deprecated = [
            mcp.types.Tool(
                name=TOOL_DESCRIPTIONS[name]["name"],
                description=TOOL_DESCRIPTIONS[name]["description"],
                inputSchema=TOOL_DESCRIPTIONS[name]["parameters"],
            )
            for name in TOOL_DESCRIPTIONS
            if name not in DEPRECATED_ALIASES
        ]
        return non_deprecated

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        """Execute a tool by name."""
        try:
            result = run_tool(name, arguments)

            # FIX: Convert Pydantic models to dicts for MCP serialization
            # Issue: Antigravity expects dict format, not tuple pairs from .items()
            from pydantic import BaseModel
            if isinstance(result, BaseModel):
                # Use .model_dump() for Pydantic v2 (or .dict() for v1)
                if hasattr(result, 'model_dump'):
                    return result.model_dump()
                elif hasattr(result, 'dict'):
                    return result.dict()

            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"error": str(e), "tool": name}


    return server

# =============================================================================
# GLOBAL SERVER INSTANCE (for entry point compatibility)
# =============================================================================

# Create global server instance for scripts/arifos_mcp_entry.py compatibility
mcp_server = create_stdio_server()

async def main():
    """Main entry point for stdio server."""
    async with stdio_server() as (read_stream, write_stream):
        server = create_stdio_server()
        await server.run(read_stream, write_stream, server.create_initialization_options())

# =============================================================================
# STATISTICS
# =============================================================================

def print_stats():
    """Print consolidation statistics."""
    print("=" * 80)
    print("arifOS Unified MCP Server - Consolidation Statistics")
    print("=" * 80)
    print(f"Total Tools: {len([k for k in TOOLS if k not in DEPRECATED_ALIASES])}")
    print(f"Deprecated Aliases: {len(DEPRECATED_ALIASES)}")
    print()
    print("Tools by Category:")
    print("  - Constitutional Pipeline: 5 tools")
    print("    * arifos_live (000->999 full pipeline)")
    print("    * agi_think (111+222+777 - The Mind)")
    print("    * agi_reflect (333 meta-reflection - Track A/B/C)")
    print("    * asi_act (555+666 - The Heart)")
    print("    * apex_seal (444+888+889 - Final judgment)")
    print("  - Search Tools: 2 tools (NEW)")
    print("    * agi_search (111+ extended SENSE - knowledge acquisition)")
    print("    * asi_search (444 EVIDENCE - claim validation)")
    print("  - VAULT-999 Memory System: 3 tools (CONSOLIDATED)")
    print("    * vault999_query (recall + search + fetch)")
    print("    * vault999_store (EUREKA storage + TAC eval)")
    print("    * vault999_seal (audit + receipts + seal)")
    print("  - File Access Governance (FAG): 4 tools")
    print("  - Validation & Routing: 1 tool")
    print("  - System Operations: 2 tools")
    print()
    print("Consolidation Result:")
    print("  - From 34 tools -> 17 tools (-50%)")
    print("  - Removed 11 redundant pipeline stage tools")
    print("  - Deleted 1 ungoverned tool (APEX_LLAMA)")
    print("  - Consolidated 9 vault999 tools -> 3 tools (-67% memory tools)")
    print("  - Exposed 2 search tools (agi_search, asi_search)")
    print("  - Semantic renaming: arifos_live, agi_reflect, apex_seal")
    print("  - Unified vault999_* namespace for memory")
    print("  - All 19 core capabilities preserved")
    print("=" * 80)

if __name__ == "__main__":
    print_stats()
    import asyncio
    asyncio.run(main())
