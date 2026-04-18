"""
arifOS Federation — MCP Server Entry Point
=========================================
Run individual agents or unified server.

Usage:
    python -m arifOS.arifosmcp.run --agent P
    python -m arifOS.arifosmcp.run --agents P,T,V
    python -m arifOS.arifosmcp.run --catalog
"""

from __future__ import annotations

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arifosmcp.mcp_tools import (
    create_perception_mcp,
    create_transformation_mcp,
    create_valuation_mcp,
    create_governance_mcp,
    create_execution_mcp,
    create_meta_mcp,
    create_unified_mcp,
    TOOL_CATALOG,
)


AGENT_FACTORIES = {
    "P": create_perception_mcp,
    "T": create_transformation_mcp,
    "V": create_valuation_mcp,
    "G": create_governance_mcp,
    "E": create_execution_mcp,
    "M": create_meta_mcp,
}


def run_agent(agent_id: str):
    """Run a single agent MCP server."""
    if agent_id not in AGENT_FACTORIES:
        print(f"Unknown agent: {agent_id}")
        print(f"Available: {list(AGENT_FACTORIES.keys())}")
        return 1

    factory = AGENT_FACTORIES[agent_id]
    mcp = factory()
    print(f"Starting {agent_id} agent MCP server...")
    print(f"  Transport: stdio")
    try:
        tools = mcp._tool_manager.tools
        print(f"  Tools: {len(tools)}")
    except AttributeError:
        pass
    mcp.run()
    return 0


def run_multiple_agents(agent_ids: list[str]):
    """Run multiple agent MCP servers combined."""
    mcp = create_unified_mcp(agents=agent_ids)
    print(f"Starting unified MCP server for agents: {agent_ids}")
    print(f"  Transport: stdio")
    try:
        tools = mcp._tool_manager.tools
        print(f"  Tools: {len(tools)}")
    except AttributeError:
        pass
    mcp.run()
    return 0


def run_all_agents():
    """Run all 6 agents in unified server."""
    mcp = create_unified_mcp()
    print("Starting unified arifOS MCP server (all 6 agents)")
    print("  Transport: stdio")
    print("  Agents: P (Perception), T (Transformation), V (Valuation)")
    print("          G (Governance), E (Execution), M (Meta)")
    try:
        tools = mcp._tool_manager.tools
        print(f"  Total Tools: {len(tools)}")
    except AttributeError:
        pass
    mcp.run()
    return 0


def show_catalog():
    """Show the tool catalog."""
    print(TOOL_CATALOG)
    return 0


def main():
    args = sys.argv[1:]

    if "--catalog" in args or "-c" in args:
        return show_catalog()

    if "--help" in args or "-h" in args:
        print(__doc__)
        print("\nExamples:")
        print("  python -m arifOS.arifosmcp.run --agent P")
        print("  python -m arifOS.arifosmcp.run --agents P,T,V")
        print("  python -m arifOS.arifosmcp.run --catalog")
        return 0

    # Parse --agent or --agents
    agent_arg = None
    for i, arg in enumerate(args):
        if arg == "--agent" and i + 1 < len(args):
            agent_arg = args[i + 1]
            break
        if arg == "--agents" and i + 1 < len(args):
            agent_ids = args[i + 1].split(",")
            return run_multiple_agents(agent_ids)

    if agent_arg:
        return run_agent(agent_arg)

    # Default: run all
    return run_all_agents()


if __name__ == "__main__":
    sys.exit(main())
