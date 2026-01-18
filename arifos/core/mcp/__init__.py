"""
arifOS MCP Package - Model Context Protocol server for IDE integration.

This module provides MCP tools for integrating arifOS governance
with IDEs like VS Code, Cursor, and others.

Unified Server (v47.0.0):
- 17 tools consolidated from 34 (across 3 old servers)
- 5 constitutional pipeline + 2 search + 3 vault999 + 4 FAG + 1 validation + 2 system
- Dual semantic search (agi_search, asi_search)
- All 12 constitutional floors enforced

Quantum Architecture (v47+):
- Parallel AGI+ASI execution (orthogonal particles)
- 47% faster than sequential pipeline
- AAA-level separation: LLM generation ⊥ Quantum validation

Quantum Governance (v47.1+):
- Settlement Policy: Hard timeouts (AGI: 1.5s, ASI: 1.5s, APEX: 0.5s)
- Orthogonality Guard: Ω_ortho measurement (threshold: ≥0.95)
- Immutable Ledger: SHA256 hash chain (tamper-evident history)

Usage:
    # MCP Tools
    from arifos.core.mcp import list_tools, arifos_judge, arifos_recall, arifos_audit

    # Quantum Executor (AAA-level)
    from arifos.core.mcp import generate_and_validate_async, validate_text_sync

    # Generate + Validate (async)
    draft, state = await generate_and_validate_async(
        query="What is 2+2?",
        llm_model="gpt-4o-mini"
    )
    if state.final_verdict == "SEAL":
        print(draft)

    # Governed Quantum (production-grade)
    from arifos.core.mcp import govern_query_async, GovernedQuantumExecutor

    # With full governance enforcement
    state, proof = await govern_query_async("What is 2+2?")
    print(f"Verdict: {state.final_verdict}")
    print(f"Ω_ortho: {proof['omega_ortho']}")
    print(f"Ledger: {proof['ledger_hash']}")

Version: v47.1.0
"""

from .tools.audit import arifos_audit
from .tools.judge import arifos_judge
from .tools.recall import arifos_recall
from .unified_server import TOOLS, list_tools, mcp_server, run_tool

# AAA-level quantum helpers (v47+)
from .helpers import (
    generate_and_validate_async,
    generate_and_validate_sync,
    validate_text_async,
    validate_text_sync,
    QuantumPipeline,
)

# Quantum executor (low-level)
from .orthogonal_executor import OrthogonalExecutor, QuantumState

# Governed quantum (production-grade, v47.1+)
from .governed_executor import (
    GovernedQuantumExecutor,
    govern_query_async,
    govern_query_sync,
)

# Governance layers (advanced usage)
from .settlement_policy import SettlementPolicyHandler, SettlementResult, SettlementStatus
from .orthogonality_guard import OrthogonalityGuard, OrthogonalityMetrics, CouplingType
from .immutable_ledger import ImmutableLedger, LedgerRecord

__all__ = [
    # MCP Server
    "list_tools",
    "run_tool",
    "TOOLS",
    "mcp_server",
    "arifos_judge",
    "arifos_recall",
    "arifos_audit",

    # AAA-level helpers (recommended)
    "generate_and_validate_async",
    "generate_and_validate_sync",
    "validate_text_async",
    "validate_text_sync",
    "QuantumPipeline",

    # Governed quantum (production-grade)
    "GovernedQuantumExecutor",
    "govern_query_async",
    "govern_query_sync",

    # Low-level quantum (advanced usage)
    "OrthogonalExecutor",
    "QuantumState",

    # Governance layers (expert usage)
    "SettlementPolicyHandler",
    "SettlementResult",
    "SettlementStatus",
    "OrthogonalityGuard",
    "OrthogonalityMetrics",
    "CouplingType",
    "ImmutableLedger",
    "LedgerRecord",
]
