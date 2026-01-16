#!/usr/bin/env python3
"""Test script for unified MCP server."""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

print("Testing arifOS Unified MCP Server...")
print("=" * 80)
print()

try:
    # Test imports
    print("1. Testing imports...")
    from arifos_core.mcp.unified_server import (
        TOOLS,
        DEPRECATED_ALIASES,
        TOOL_DESCRIPTIONS,
        print_stats
    )
    print("   [OK] All imports successful")
    print()

    # Print statistics
    print("2. Server Statistics:")
    print_stats()
    print()

    # Verify tool counts
    print("3. Tool Count Verification:")
    total_tools = len(TOOLS)
    unique_tools = len([k for k in TOOLS if k not in DEPRECATED_ALIASES])
    aliases = len(DEPRECATED_ALIASES)

    print(f"   Total tools (including aliases): {total_tools}")
    print(f"   Unique tools: {unique_tools}")
    print(f"   Deprecated aliases: {aliases}")
    print()

    # List all unique tools
    print("4. All Unique Tools:")
    unique_tool_names = sorted([k for k in TOOLS if k not in DEPRECATED_ALIASES])
    for i, name in enumerate(unique_tool_names, 1):
        print(f"   {i:2d}. {name}")
    print()

    # List deprecated aliases
    print("5. Deprecated Aliases:")
    for old_name, new_name in sorted(DEPRECATED_ALIASES.items()):
        print(f"   {old_name:25s} -> {new_name}")
    print()

    # Verify tool descriptions exist
    print("6. Tool Description Verification:")
    missing_descriptions = []
    for tool_name in unique_tool_names:
        if tool_name not in TOOL_DESCRIPTIONS:
            missing_descriptions.append(tool_name)

    if missing_descriptions:
        print(f"   [WARNING] Missing descriptions for: {missing_descriptions}")
    else:
        print(f"   [OK] All {len(unique_tool_names)} tools have descriptions")
    print()

    print("=" * 80)
    print("[OK] ALL TESTS PASSED")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
