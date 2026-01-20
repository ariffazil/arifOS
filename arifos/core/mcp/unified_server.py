"""
arifOS Unified MCP Server - Consolidated Tool Registry (v50.0.0)

This is the unified MCP server that consolidates all 33 constitutional tools.
It aligns with the 000-arifOS AGI-ASI and APEX-999 metabolic cycle.

Constitutional Authority: F1-F13 governance enforced
Transport: stdio (Claude Desktop) + HTTPS/SSE (remote AI)
Version: v50.0.0

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

# =============================================================================
# TOOL IMPORTS
# =============================================================================

from .tools.mcp_111_sense import mcp_111_sense as arifos_111_sense
from .tools.mcp_222_reflect import mcp_222_reflect as arifos_222_reflect
from .tools.sequential import SequentialThinking
from .tools.recall import arifos_recall
from .tools.codex_skills import CodexConstitutionalSkills
from .tools.executor import arifos_executor
from .tools.mcp_555_empathize import mcp_555_empathize as arifos_555_empathize
from .tools.mcp_666_align import mcp_666_align as arifos_666_align
from .tools.validate_full import arifos_validate_full
from .tools.meta_select import arifos_meta_select
from .tools.fag_list import arifos_fag_list
from .tools.fag_read import arifos_fag_read
from .tools.fag_stats import arifos_fag_stats
from .tools.fag_write import arifos_fag_write
from .tools.tempa_list import arifos_tempa_list
from .tools.tempa_read import arifos_tempa_read
from .tools.tempa_stats import arifos_tempa_stats
from .tools.tempa_write import arifos_tempa_write
from .tools.mcp_444_evidence import mcp_444_evidence as arifos_444_evidence
from .tools.mcp_777_forge import mcp_777_forge as arifos_777_forge
from .tools.mcp_888_judge import mcp_888_judge as arifos_888_judge
from .tools.judge import arifos_judge
from .tools.audit import arifos_audit
from .tools.apex_llama import apex_llama as apex_llama_generate
from .tools.mcp_889_proof import mcp_889_proof as arifos_889_proof
from .tools.mcp_000_gate import mcp_000_gate as arifos_000_gate
from .tools.mcp_000_reset import mcp_000_reset as arifos_000_reset
from .tools.mcp_999_seal import mcp_999_seal as arifos_999_seal
from .tools.memory_vault import memory_get_vault
from .tools.memory_phoenix import memory_list_phoenix
from .tools.memory_propose import memory_propose_entry

# Handle potential missing sync gate or name mismatch
try:
    from .tools.mcp_000_gate_sync import mcp_000_gate as arifos_000_gate_sync
except ImportError:
    # Use the async one wrapped if needed, or just alias it
    arifos_000_gate_sync = arifos_000_gate

logger = logging.getLogger(__name__)

# =============================================================================
# TOOL WRAPPERS
# =============================================================================

# Sequential Thinking Wrapper
# Needs to handle state if possible, or just be a stateless pass-through for the protocol
_sequential_thinker = SequentialThinking()

def sequential_thinking(thought: str, thought_number: int, total_thoughts: int, next_thought_needed: bool, **kwargs) -> Dict[str, Any]:
    """
    Wrapper for SequentialThinking tool.
    """
    return _sequential_thinker.process_thought(
        thought=thought,
        thought_number=thought_number,
        total_thoughts=total_thoughts,
        next_thought_needed=next_thought_needed,
        **kwargs
    )

# Codex Skills Wrapper
_codex_skills = CodexConstitutionalSkills()

async def codex_run_skill(skill_name: str, **kwargs) -> Dict[str, Any]:
    """
    Wrapper for Codex Constitutional Skills.
    Dispatches to analyze_code or generate_code based on skill_name.
    """
    if skill_name == "codex_code_analysis":
        # extract args expected by analyze_code
        code = kwargs.get("code", "")
        analysis_type = kwargs.get("analysis_type", "general")
        user_id = kwargs.get("user_id", "default_user")
        context = kwargs.get("context", {})
        return await _codex_skills.analyze_code(code, analysis_type, user_id, context)
    elif skill_name == "codex_code_generation":
        # extract args expected by generate_code
        requirements = kwargs.get("requirements", "")
        constraints = kwargs.get("constraints", [])
        user_id = kwargs.get("user_id", "default_user")
        language = kwargs.get("language", "python")
        complexity_level = kwargs.get("complexity_level", "moderate")
        context = kwargs.get("context", {})
        return await _codex_skills.generate_code(requirements, constraints, user_id, language, complexity_level, context)
    else:
        return {"error": f"Unknown skill: {skill_name}"}

def cryptography_sign(data: str, key_id: str = "default") -> str:
    """Cryptographic signing tool (Server-side)."""
    return f"signed_{key_id}_{hash(data)}"

# =============================================================================
# UNIFIED TOOL REGISTRY (33 Tools)
# =============================================================================

TOOLS: Dict[str, Callable] = {
    # Group 1: 000-arifOS AGI-ASI (Operational & Safety) - 18 Tools
    
    # AGI: Sense & Think (Stages 111-333)
    "mcp_111_sense": arifos_111_sense,
    "mcp_222_reflect": arifos_222_reflect,
    "sequential_thinking": sequential_thinking,
    "recall": arifos_recall,
    "codex_skills": codex_run_skill,
    "executor": arifos_executor,
    
    # ASI: Empathy & Align (Stages 555-666)
    "mcp_555_empathize": arifos_555_empathize,
    "mcp_666_align": arifos_666_align,
    "validate_full": arifos_validate_full,
    "meta_select": arifos_meta_select,
    
    # Governance Resources (ASI Enforced)
    "fag_list": arifos_fag_list,
    "fag_read": arifos_fag_read,
    "fag_stats": arifos_fag_stats,
    "fag_write": arifos_fag_write,
    "tempa_list": arifos_tempa_list,
    "tempa_read": arifos_tempa_read,
    "tempa_stats": arifos_tempa_stats,
    "tempa_write": arifos_tempa_write,
    
    # Group 2: APEX-999 (Judgment & Finality) - 15 Tools
    
    # APEX: Evidence & Judgment (Stages 444, 777, 888)
    "mcp_444_evidence": arifos_444_evidence,
    "mcp_777_forge": arifos_777_forge,
    "mcp_888_judge": arifos_888_judge,
    "judge": arifos_judge,
    "audit": arifos_audit,
    "apex_llama": apex_llama_generate,
    
    # PROOF: Sealing (Stage 889)
    "mcp_889_proof": arifos_889_proof,
    "cryptography": cryptography_sign,
    
    # VAULT: Gate & Memory (Stages 000 & 999)
    "mcp_000_gate": arifos_000_gate,
    "mcp_000_gate_sync": arifos_000_gate_sync,
    "mcp_000_reset": arifos_000_reset,
    "mcp_999_seal": arifos_999_seal,
    "memory_vault": memory_get_vault,
    "memory_phoenix": memory_list_phoenix,
    "memory_propose": memory_propose_entry,
}

# =============================================================================
# TOOL DESCRIPTIONS
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    # Simplified descriptions for discovery
    "mcp_111_sense": {"name": "mcp_111_sense", "description": "AGI Input Reception & Injection Defense (F12/F13)", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    "mcp_222_reflect": {"name": "mcp_222_reflect", "description": "AGI Reasoning & Truth Verification (F2/F4)", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    "sequential_thinking": {"name": "sequential_thinking", "description": "Chain of Thought Processing", "inputSchema": {"type": "object", "properties": {"thought": {"type": "string"}, "thought_number": {"type": "integer"}, "total_thoughts": {"type": "integer"}, "next_thought_needed": {"type": "boolean"}}, "required": ["thought", "thought_number", "total_thoughts", "next_thought_needed"]}},
    "recall": {"name": "recall", "description": "Semantic memory retrieval", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    "codex_skills": {"name": "codex_skills", "description": "Execute learned skills (analysis/generation)", "inputSchema": {"type": "object", "properties": {"skill_name": {"type": "string"}, "code": {"type": "string"}, "requirements": {"type": "string"}}, "required": ["skill_name"]}},
    "executor": {"name": "executor", "description": "Secure code executor", "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}, "intent": {"type": "string"}}, "required": ["command", "intent"]}},
    "mcp_555_empathize": {"name": "mcp_555_empathize", "description": "ASI Empathy & Stakeholder Impact (F5/F6)", "inputSchema": {"type": "object", "properties": {"response_text": {"type": "string"}}, "required": ["response_text"]}},
    "mcp_666_align": {"name": "mcp_666_align", "description": "ASI Alignment & Veto (F1/F8/F9)", "inputSchema": {"type": "object", "properties": {"action": {"type": "object"}}, "required": ["action"]}},
    "cryptography": {"name": "cryptography", "description": "Cryptographic operations", "inputSchema": {"type": "object", "properties": {"data": {"type": "string"}}, "required": ["data"]}},
}

# =============================================================================
# MCP SERVER INITIALIZATION
# =============================================================================

def create_stdio_server() -> Server:
    """
    Create MCP server with stdio transport.
    """
    server = Server("arifOS-unified-v50")

    @server.list_tools()
    async def list_tools() -> List[mcp.types.Tool]:
        """List all available tools."""
        tools_list = []
        for name, func in TOOLS.items():
            desc = TOOL_DESCRIPTIONS.get(name, {}).get("description", f"Tool {name}")
            schema = TOOL_DESCRIPTIONS.get(name, {}).get("inputSchema", {"type": "object", "properties": {"query": {"type": "string"}}})
            
            tools_list.append(
                mcp.types.Tool(
                    name=name,
                    description=desc,
                    inputSchema=schema,
                )
            )
        return tools_list

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name."""
        tool = TOOLS.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        
        try:
            # Handle async tools explicitly if needed, but the server runner usually handles awaitables
            # If tool returns a coroutine, await it
            import inspect
            if inspect.iscoroutinefunction(tool):
                return await tool(**arguments)
            else:
                return tool(**arguments)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"error": str(e), "tool": name}

    return server

# =============================================================================
# GLOBAL SERVER INSTANCE
# =============================================================================

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
    """Print tool registry statistics."""
    print("=" * 80)
    print("arifOS Unified MCP Server v50.0.0 - Tool Registry")
    print("=" * 80)
    print(f"Total Tools: {len(TOOLS)}")
    print("Alignment: 000-arifOS AGI-ASI and APEX-999")
    print()
    print("Tools by Group:")
    print("  - Group 1: 000-arifOS AGI-ASI (Operational & Safety) - 18 Tools")
    print("    (mcp_111_sense, mcp_222_reflect, sequential_thinking, recall, codex_skills, executor,")
    print("     mcp_555_empathize, mcp_666_align, validate_full, meta_select,")
    print("     fag_list, fag_read, fag_stats, fag_write, tempa_list, tempa_read, tempa_stats, tempa_write)")
    print()
    print("  - Group 2: APEX-999 (Judgment & Finality) - 15 Tools")
    print("    (mcp_444_evidence, mcp_777_forge, mcp_888_judge, judge, audit, apex_llama,")
    print("     mcp_889_proof, cryptography, mcp_000_gate, mcp_000_gate_sync, mcp_000_reset,")
    print("     mcp_999_seal, memory_vault, memory_phoenix, memory_propose)")
    print("=" * 80)

if __name__ == "__main__":
    print_stats()
    import asyncio
    asyncio.run(main())