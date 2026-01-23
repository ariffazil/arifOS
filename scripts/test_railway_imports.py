#!/usr/bin/env python3
"""
Railway Import Diagnostic Script

Tests if all required modules can be imported before starting the server.
Run this to quickly identify import errors.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("Railway Import Diagnostic Test")
print("=" * 80)

# Test 1: Basic Python modules
print("\n[1/6] Testing basic Python modules...")
try:
    import asyncio
    import json
    import os
    import logging
    print("✅ Basic Python modules OK")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Third-party dependencies
print("\n[2/6] Testing third-party dependencies...")
try:
    import fastapi
    import uvicorn
    import mcp
    import mcp.types
    print("✅ FastAPI, Uvicorn, MCP OK")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    print("Fix: Ensure requirements.txt includes fastapi, uvicorn, mcp")
    sys.exit(1)

# Test 3: Import unified_server
print("\n[3/6] Testing unified_server imports...")
try:
    from arifos.core.mcp import unified_server
    print(f"✅ unified_server imported ({len(unified_server.TOOLS)} tools)")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    print("Fix: Check tool imports in unified_server.py")
    sys.exit(1)

# Test 4: Import SSE server
print("\n[4/6] Testing SSE server imports...")
try:
    from arifos.core.mcp.sse import app
    print("✅ SSE server app imported")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    print("Fix: Check imports in sse.py")
    sys.exit(1)

# Test 5: Test FastAPI routes
print("\n[5/6] Testing FastAPI routes...")
try:
    routes = [route.path for route in app.routes]
    print(f"✅ FastAPI routes configured: {routes}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# Test 6: Environment variables
print("\n[6/6] Testing environment variables...")
required_vars = []  # Railway sets PORT automatically
optional_vars = ["ARIFOS_ENV", "GOVERNANCE_MODE", "LOG_LEVEL"]

missing = []
for var in optional_vars:
    value = os.environ.get(var, "NOT SET")
    if value == "NOT SET":
        print(f"⚠️  {var}: {value} (optional, will use default)")
    else:
        print(f"✅ {var}: {value}")

# Final verdict
print("\n" + "=" * 80)
print("✅ ALL IMPORT TESTS PASSED!")
print("=" * 80)
print("\nYour Railway deployment should work.")
print("If it still fails, check:")
print("  1. Railway deployment logs for runtime errors")
print("  2. Port binding (should use Railway's $PORT)")
print("  3. Health check endpoint accessibility")
