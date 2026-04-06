"""
arifosmcp/agentzero/memory/agent_memory_integration.py
======================================================

Wires ConstitutionalMemoryStore to agent context.

Authority: A-ARCHITECT | A-ENGINEER
Status: PROVISIONAL — Requires A-VALIDATOR review

Usage:
    from arifosmcp.agentzero.memory.agent_memory_integration import AgentMemoryContext
    ctx = AgentMemoryContext(agent_id="A-ENGINEER", session_id="session_001")
    await ctx.initialize()
    await ctx.store_implementation(...)
"""

from arifosmcp.agentzero.memory.constitutional_memory import (
    AgentContext,
    ConstitutionalMemoryStore,
    MemoryArea,
    MemoryRecord,
    SearchResult,
)

__all__ = [
    "AgentContext",
    "ConstitutionalMemoryStore", 
    "MemoryArea",
    "MemoryRecord",
    "SearchResult",
]
