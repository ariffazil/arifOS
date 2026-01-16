#!/usr/bin/env python3
"""
arifOS MCP Server - Direct Import Bypass

This script bypasses the broken arifos_core/__init__.py import chain
and directly imports the unified MCP server.

Usage:
    python scripts/start_mcp_direct.py

DITEMPA BUKAN DIBERI
"""

import sys
import os
import asyncio
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Set environment variables BEFORE importing anything
os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"
os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"

print("=" * 80)
print("arifOS Unified MCP Server (Direct Import Mode)")
print("=" * 80)
print()
print("Environment:")
print(f"  ARIFOS_ALLOW_LEGACY_SPEC={os.environ.get('ARIFOS_ALLOW_LEGACY_SPEC')}")
print(f"  ARIFOS_PHYSICS_DISABLED={os.environ.get('ARIFOS_PHYSICS_DISABLED')}")
print(f"  Python: {sys.version}")
print(f"  Working Directory: {os.getcwd()}")
print()

# Try to import the server DIRECTLY without going through arifos_core.__init__
try:
    print("Importing MCP server (bypassing arifos_core.__init__)...")

    # Direct import - avoid package __init__.py
    import importlib.util

    server_path = repo_root / "arifos_core" / "mcp" / "unified_server.py"

    if not server_path.exists():
        print(f"ERROR: Server file not found: {server_path}")
        sys.exit(1)

    print(f"  Loading from: {server_path}")

    spec = importlib.util.spec_from_file_location("unified_server", server_path)
    unified_server = importlib.util.module_from_spec(spec)

    # Execute the module
    print("  Executing module...")
    spec.loader.exec_module(unified_server)

    print("✅ MCP server module loaded successfully!")
    print()

    # Get server stats
    if hasattr(unified_server, 'print_stats'):
        unified_server.print_stats()
        print()

    # Start server
    if hasattr(unified_server, 'main'):
        print("Starting MCP server...")
        print("Transport: stdio (Claude Desktop)")
        print("Press Ctrl+C to stop.")
        print()

        asyncio.run(unified_server.main())
    else:
        print("ERROR: 'main' function not found in unified_server module")
        sys.exit(1)

except KeyboardInterrupt:
    print("\n\nServer stopped by user.")
    sys.exit(0)

except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nThis means the MCP server has dependencies that also can't import.")
    print("The import chain failure is deeper than just __init__.py")
    print("\nTo fix: Need to resolve import failures in:")
    print("  - arifos_core/mcp/unified_server.py")
    print("  - Its dependencies")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
