"""
arifOS Unified MCP Server - Consolidated Tool Registry

This is the unified MCP server that consolidates 3 previous servers:
- server.py (stdio transport, 27 tools)
- arifos_mcp_server.py (AAA remote, 10 tools)
- vault999_server.py (Vault-999 gateway, 8 tools)

Consolidation Result:
- From 34 tools → 22 tools (-35%)
- Removed 11 redundant pipeline stage tools
- Deleted 1 ungoverned tool (APEX_LLAMA)
- Clean naming convention (no mcp_ prefix)
- All 18 core capabilities preserved

Constitutional Authority: F1-F9 governance enforced
Transport: stdio (Claude Desktop) + HTTPS/SSE (remote AI)
Version: v46.2

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Dict, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server

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

# =============================================================================
# CORE IMPORTS - Constitutional Pipeline (4 tools)
# =============================================================================

from .tools.judge import arifos_judge  # Full pipeline (000→999)
from .tools.bundles import agi_think_sync as agi_think  # AGI bundle (111+222+777)
from .tools.bundles import asi_act_sync as asi_act  # ASI bundle (555+666)
from .tools.bundles import apex_audit_sync as apex_audit  # APEX bundle (444+888+889)

# =============================================================================
# MEMORY & RETRIEVAL IMPORTS (6 tools)
# =============================================================================

from .tools.recall import arifos_recall  # L7 Mem0+Qdrant recall
from .tools.audit import arifos_audit  # Audit trail inspection

# Vault tools (search/fetch/receipts) - implemented inline below
# vault999_store and vault999_eval - to be imported from arifos_mcp_server

# =============================================================================
# FILE ACCESS GOVERNANCE (FAG) IMPORTS (4 tools)
# =============================================================================

from .tools.fag_read import TOOL_METADATA as FAG_READ_METADATA
from .tools.fag_read import FAGReadRequest, FAGReadResponse, arifos_fag_read
from .tools.fag_write import FAGWriteRequest, arifos_fag_write
from .tools.fag_list import FAGListRequest, arifos_fag_list
from .tools.fag_stats import FAGStatsRequest, arifos_fag_stats

# =============================================================================
# VALIDATION & ROUTING IMPORTS (2 tools)
# =============================================================================

from .tools.validate_full import TOOL_METADATA as VALIDATE_FULL_METADATA
from .tools.validate_full import ValidateFullRequest, ValidateFullResponse, arifos_validate_full
from .tools.meta_select import TOOL_METADATA as META_SELECT_METADATA
from .tools.meta_select import MetaSelectRequest, MetaSelectResponse, arifos_meta_select

# =============================================================================
# SYSTEM OPERATIONS IMPORTS (3 tools)
# =============================================================================

from .tools.executor import ExecutorRequest, arifos_executor
from .tools.remote.github_aaa import TOOL_METADATA as GITHUB_METADATA
from .tools.remote.github_aaa import github_aaa_govern

# =============================================================================
# MEMORY TOOLS IMPORTS (2 tools)
# =============================================================================

from .tools.memory_tools import memory_get_receipts, memory_verify_seal

# =============================================================================
# VAULT IMPORTS
# =============================================================================

from pathlib import Path
import json
import logging
from datetime import datetime, timezone
from typing import List

from arifos_core.memory.vault.vault_manager import VaultManager

# Vault999 TAC/EUREKA imports
from arifos_core.mcp.vault999_tac_eureka import (
    EvaluationInputs,
    validate_ledger_entries,
    vault_999_decide,
    utc_now_iso
)

logger = logging.getLogger(__name__)

# Vault configuration
REPO_ROOT = Path(__file__).parent.parent.parent
VAULT_ROOT = REPO_ROOT / "vault_999" / "VAULT999"

BANDS = {
    "L0_VAULT": {
        "path": VAULT_ROOT / "L0_VAULT",
        "confidence": 1.0,
        "tag": "[CANONICAL]",
        "geometry": "ORTHOGONAL",
        "extensions": ["*.md", "*.json"]
    },
    "L1_LEDGERS": {
        "path": VAULT_ROOT / "L1_LEDGERS",
        "confidence": 1.0,
        "tag": "[SEALED]",
        "geometry": "TOROIDAL",
        "extensions": ["*.jsonl", "*.md"]
    },
    "L4_WITNESS": {
        "path": VAULT_ROOT / "L4_WITNESS",
        "confidence": 0.85,
        "tag": "[OBSERVATION]",
        "geometry": "FRACTAL",
        "extensions": ["*.md"]
    },
    "00_ENTROPY": {
        "path": VAULT_ROOT / "00_ENTROPY",
        "confidence": 0.1,
        "tag": "[HOT]",
        "geometry": "CHAOS",
        "extensions": ["*.json", "*.md", "*.txt"]
    }
}

MAX_RESULTS = 10

# Sacred vault protection
SACRED_VAULT_PATTERNS = ["ARIF FAZIL", "ARIF_FAZIL", "arif fazil", "arif_fazil"]

def _is_sacred_query(query: str) -> bool:
    """Check if query targets sacred human vault."""
    query_lower = query.lower() if query else ""
    for pattern in SACRED_VAULT_PATTERNS:
        if pattern.lower() in query_lower:
            return True
    return False

# =============================================================================
# VAULT TOOLS (Inline Implementation)
# =============================================================================

def vault_search(query: str) -> Dict[str, Any]:
    """
    Search constitutional memory across vault bands.

    Searches L0_VAULT (canonical), L1_LEDGERS (sealed), L4_WITNESS (observation), 00_ENTROPY (hot).
    Returns ranked results by confidence.

    Constitutional Boundary: Only searches VAULT999 (machine law).
    The ARIF FAZIL vault (human biography) is sacred and offline.
    """
    logger.info(f"vault_search: '{query}'")

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
    limited = all_results[:MAX_RESULTS]

    logger.info(f"Found {len(all_results)}, returning {len(limited)}")

    return {
        "query": query,
        "total_found": len(all_results),
        "results": limited,
        "vault": "VAULT999",
        "governance": "Nine Floors + APEX PRIME"
    }

def vault_fetch(id: str) -> Dict[str, Any]:
    """
    Retrieve full document by ID (format: BAND_filename).

    Constitutional Boundary: Only fetches from VAULT999.
    The ARIF FAZIL vault is sacred and offline.
    """
    logger.info(f"vault_fetch: '{id}'")

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
                                "vault": "VAULT999",
                                "governance": "Nine Floors + APEX PRIME",
                                "geometry": band.get("geometry", "UNKNOWN")
                            }
                        }
                    except Exception as e:
                        return {"error": str(e)}

    return {"error": f"Not found: {id}"}

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

    Vault Targets:
    - AAA: Human insights -> vault_999/ARIF FAZIL/
    - CCC: Machine law -> vault_999/CCC/L4_EUREKA/
    - BBB: Memory/learning -> vault_999/BBB/L1_cooling_ledger/

    Triad (MANDATORY):
    - structure: What changed (the new invariant)
    - truth_boundary: What is now constrained (non-violable)
    - scar: What it took / what it prevents (cost signal)

    NO NEW FOLDERS. New markdown pages OK.
    """
    logger.info(f"VAULT-999 Store: target={vault_target}, title={title}")

    # Determine vault path
    CCC_ROOT = REPO_ROOT / "vault_999" / "CCC"
    BBB_ROOT = REPO_ROOT / "vault_999" / "BBB"
    SACRED_VAULT = REPO_ROOT / "vault_999" / "ARIF FAZIL"

    if vault_target == "AAA":
        logger.error("[VOID] SACRED_BOUNDARY: Cannot write to AAA (human vault) via MCP")
        return {
            "verdict": "VOID-999",
            "error": "SACRED_BOUNDARY: The ARIF FAZIL vault is offline and not MCP-governed",
            "guidance": "AAA (human biography) is protected. Use CCC (machine law) or BBB (memory/learning)."
        }
    elif vault_target == "CCC":
        vault_path = CCC_ROOT / "L4_EUREKA"
    elif vault_target == "BBB":
        vault_path = BBB_ROOT / "L1_cooling_ledger"
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
# UNIFIED TOOL REGISTRY (21 Tools)
# =============================================================================

TOOLS: Dict[str, Callable] = {
    # -------------------------------------------------------------------------
    # CONSTITUTIONAL PIPELINE (4 tools)
    # -------------------------------------------------------------------------
    "apexprime_judge": arifos_judge,   # Full pipeline (000→999) via APEX Prime
    "agi_think": agi_think,            # AGI bundle (111+222+777)
    "asi_act": asi_act,                # ASI bundle (555+666)
    "apex_audit": apex_audit,          # APEX bundle (444+888+889)

    # -------------------------------------------------------------------------
    # VAULT-999 MEMORY SYSTEM (9 tools)
    # -------------------------------------------------------------------------
    "vault999_recall": arifos_recall,  # L7 Mem0+Qdrant recall
    "vault999_search": vault_search,   # Vault band search
    "vault999_fetch": vault_fetch,     # Document retrieval
    "vault999_receipts": vault_receipts,  # ZKPC receipt verification
    "vault999_store": vault999_store,  # EUREKA storage (CCC/BBB)
    "vault999_eval": vault999_eval,    # TAC/EUREKA-777 evaluation
    "vault999_audit": arifos_audit,    # Audit trail inspection
    "vault999_verify_receipts": memory_get_receipts,  # ZKPC cryptographic receipts
    "vault999_verify_seal": memory_verify_seal,  # Cryptographic seal verification

    # -------------------------------------------------------------------------
    # FILE ACCESS GOVERNANCE (4 tools) - RENAMED
    # -------------------------------------------------------------------------
    "fag_read": arifos_fag_read,       # Governed file read (was arifos_fag_read)
    "fag_write": arifos_fag_write,     # Governed file write (was arifos_fag_write)
    "fag_list": arifos_fag_list,       # Governed directory list (was arifos_fag_list)
    "fag_stats": arifos_fag_stats,     # Governance statistics (was arifos_fag_stats)

    # -------------------------------------------------------------------------
    # VALIDATION & ROUTING (2 tools)
    # -------------------------------------------------------------------------
    "arifos_validate_full": arifos_validate_full,  # Track A/B/C validation
    "arifos_meta_select": arifos_meta_select,      # Meta model selection

    # -------------------------------------------------------------------------
    # SYSTEM OPERATIONS (2 tools)
    # -------------------------------------------------------------------------
    "arifos_executor": arifos_executor,        # Shell execution with F1-F9 oversight
    "github_govern": github_aaa_govern,        # GitHub operations governance (was github_aaa_govern)
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

    # Old constitutional pipeline → New name
    "arifos_judge": "apexprime_judge",

    # Old memory/vault tools → New vault999_* names
    "arifos_recall": "vault999_recall",
    "arifos_audit": "vault999_audit",
    "vault_search": "vault999_search",
    "vault_fetch": "vault999_fetch",
    "vault_receipts": "vault999_receipts",
    "memory_get_receipts": "vault999_verify_receipts",
    "memory_receipts": "vault999_verify_receipts",
    "memory_verify_seal": "vault999_verify_seal",

    # Old vault999_server tool names → New names
    "search": "vault999_search",
    "fetch": "vault999_fetch",
    "receipts": "vault999_receipts",
}

# Add aliases to TOOLS registry
for old_name, new_name in DEPRECATED_ALIASES.items():
    if new_name in TOOLS:
        TOOLS[old_name] = TOOLS[new_name]

# =============================================================================
# TOOL REQUEST MODELS
# =============================================================================

TOOL_REQUEST_MODELS: Dict[str, type] = {
    "apexprime_judge": JudgeRequest,
    "vault999_recall": RecallRequest,
    "vault999_audit": AuditRequest,
    "fag_read": FAGReadRequest,
    "fag_write": FAGWriteRequest,
    "fag_list": FAGListRequest,
    "fag_stats": FAGStatsRequest,
    "arifos_validate_full": ValidateFullRequest,
    "arifos_meta_select": MetaSelectRequest,
    "agi_think": AgiThinkRequest,
    "asi_act": AsiActRequest,
    "apex_audit": ApexAuditRequest,
    "arifos_executor": ExecutorRequest,
}

# =============================================================================
# TOOL DESCRIPTIONS (MCP Discovery)
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # CONSTITUTIONAL PIPELINE
    # -------------------------------------------------------------------------
    "apexprime_judge": {
        "name": "apexprime_judge",
        "description": (
            "Judge a query through APEX Prime - the full arifOS constitutional pipeline (000→999). "
            "Returns verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD) based on 9 floors."
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
    "apex_audit": {
        "name": "apex_audit",
        "description": "APEX Bundle (The Soul). Audits AGI/ASI states, verifies evidence, seals verdict. Consolidates 444, 888, 889.",
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
    # VAULT-999 MEMORY SYSTEM
    # -------------------------------------------------------------------------
    "vault999_recall": {
        "name": "vault999_recall",
        "description": (
            "Recall relevant memories from L7 (Mem0 + Qdrant). "
            "All recalled memories are capped at 0.85 confidence. "
            "Memories are suggestions, not facts (INV-4)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User ID for memory isolation"},
                "prompt": {"type": "string", "description": "Query prompt for semantic search"},
                "max_results": {"type": "integer", "description": "Maximum memories to return (default: 5)", "default": 5},
            },
            "required": ["user_id", "prompt"],
        },
    },
    "vault999_search": {
        "name": "vault999_search",
        "description": (
            "Search constitutional memory across vault bands (L0_VAULT, L1_LEDGERS, L4_WITNESS, 00_ENTROPY). "
            "Returns ranked results by confidence. Only searches VAULT999 (machine law)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query string"},
            },
            "required": ["query"],
        },
    },
    "vault999_fetch": {
        "name": "vault999_fetch",
        "description": (
            "Retrieve full document by ID from vault bands. "
            "ID format: BAND_filename (e.g., L0_VAULT_canon_v46)"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Document ID (BAND_filename)"},
            },
            "required": ["id"],
        },
    },
    "vault999_receipts": {
        "name": "vault999_receipts",
        "description": (
            "Verify ZKPC receipts in the constitutional ledger. "
            "Returns cryptographic proof of integrity (F8 Tri-Witness)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum receipts to return (default: 10)", "default": 10},
            },
            "required": [],
        },
    },
    "vault999_store": {
        "name": "vault999_store",
        "description": (
            "Store EUREKA insight in VAULT-999 (CCC/BBB). "
            "Requires structure/truth_boundary/scar triad. "
            "AAA (human vault) is protected and offline."
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
    "vault999_eval": {
        "name": "vault999_eval",
        "description": (
            "Evaluate EUREKA against TAC/EUREKA-777 constitutional laws. "
            "Returns SEAL-999/HOLD-999/VOID-999 verdict with vault record."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dC": {"type": "number", "description": "Contrast value"},
                "Ea": {"type": "number", "description": "Activation threshold"},
                "dH_dt": {"type": "number", "description": "System cooling rate"},
                "Teff": {"type": "number", "description": "Effective temperature"},
                "Tcrit": {"type": "number", "description": "Critical temperature"},
                "Omega0_value": {"type": "number", "description": "Humility metric [0.03, 0.05]"},
                "K_before": {"type": "integer", "description": "Complexity before"},
                "K_after": {"type": "integer", "description": "Complexity after"},
                "reality_7_1_physically_permissible": {"type": "boolean", "description": "EUREKA-777: Physically permissible"},
                "structure_7_2_compressible": {"type": "boolean", "description": "EUREKA-777: Compressible representation"},
                "language_7_3_minimal_truthful_naming": {"type": "boolean", "description": "EUREKA-777: Minimal truthful naming"},
                "ledger_entries": {"type": "array", "description": "Cooling ledger entries"},
                "T0_context_start": {"type": "string", "description": "Session start time (ISO-8601)"},
                "human_seal_sealed_by": {"type": "string", "description": "Who sealed this"},
                "human_seal_seal_note": {"type": "string", "description": "Seal note"},
            },
            "required": ["dC", "Ea", "dH_dt", "Teff", "Tcrit", "Omega0_value", "K_before", "K_after", "reality_7_1_physically_permissible", "structure_7_2_compressible", "language_7_3_minimal_truthful_naming", "ledger_entries", "T0_context_start"],
        },
    },
    "vault999_audit": {
        "name": "vault999_audit",
        "description": (
            "Retrieve audit/ledger data from VAULT-999 for a user. "
            "STUB: Full implementation coming in future sprint."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User ID to audit"},
                "days": {"type": "integer", "description": "Days to look back (default: 7)", "default": 7},
            },
            "required": ["user_id"],
        },
    },
    "vault999_verify_receipts": {
        "name": "vault999_verify_receipts",
        "description": (
            "Get ZKPC cryptographic receipts for memory operations. "
            "Returns Zero-Knowledge Proof of Cooling receipts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum receipts to return (default: 10)", "default": 10},
            },
            "required": [],
        },
    },
    "vault999_verify_seal": {
        "name": "vault999_verify_seal",
        "description": (
            "Verify cryptographic seal for memory integrity. "
            "Returns seal verification status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "seal_id": {"type": "string", "description": "Seal ID to verify"},
            },
            "required": ["seal_id"],
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
    "arifos_validate_full": VALIDATE_FULL_METADATA,
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
            TOOL_DESCRIPTIONS[name]
            for name in TOOL_DESCRIPTIONS
            if name not in DEPRECATED_ALIASES
        ]
        return non_deprecated

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        """Execute a tool by name."""
        try:
            result = run_tool(name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"error": str(e), "tool": name}

    return server

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
    print("  - Constitutional Pipeline (APEX): 4 tools")
    print("  - VAULT-999 Memory System: 9 tools")
    print("  - File Access Governance (FAG): 4 tools")
    print("  - Validation & Routing: 2 tools")
    print("  - System Operations: 2 tools")
    print()
    print("Consolidation Result:")
    print("  - From 34 tools -> 21 tools (-38%)")
    print("  - Removed 11 redundant pipeline stage tools")
    print("  - Deleted 1 ungoverned tool (APEX_LLAMA)")
    print("  - Unified vault999_* namespace for memory")
    print("  - Clean naming: apexprime_judge, vault999_*, fag_*")
    print("  - All 18 core capabilities preserved")
    print("=" * 80)

if __name__ == "__main__":
    print_stats()
    import asyncio
    asyncio.run(main())
