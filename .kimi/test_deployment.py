#!/usr/bin/env python3
"""Test Kimi → arifOS MCP deployment"""

import sys
import json
import os

ARIFOS_PATH = r"C:\Users\User\arifOS"
if ARIFOS_PATH not in sys.path:
    sys.path.insert(0, ARIFOS_PATH)

print("=" * 60)
print("arifOS-Kimi Deployment Verification v52.0.0")
print("=" * 60)

# Test 1: Bridge import
try:
    from arifos.mcp.bridge import ENGINES_AVAILABLE
    print(f"[PASS] Bridge Import: ENGINES_AVAILABLE = {ENGINES_AVAILABLE}")
except Exception as e:
    print(f"[FAIL] Bridge Import Failed: {e}")
    sys.exit(1)

# Test 2: Tools available
try:
    from arifos.mcp.server import TOOL_DESCRIPTIONS
    tool_count = len(TOOL_DESCRIPTIONS)
    print(f"[PASS] Tools Loaded: {tool_count} tools")
    # Just print tool names without iterating to avoid encoding issues
    print(f"   Tool names available in TOOL_DESCRIPTIONS dict")
except Exception as e:
    print(f"[FAIL] Tools Load Failed: {e}")
    sys.exit(1)

# Test 3: Settings file exists
settings_path = r"C:\Users\User\arifOS\.kimi\settings.json"
if os.path.exists(settings_path):
    print(f"[PASS] Settings File: {settings_path}")
    with open(settings_path) as f:
        settings = json.load(f)
        print(f"   - Role: {settings.get('role', 'N/A')}")
        print(f"   - MCP Servers: {list(settings.get('mcp_servers', {}).keys())}")
        print(f"   - Commands: {list(settings.get('commands', {}).keys())}")
else:
    print(f"[FAIL] Settings File Missing: {settings_path}")
    sys.exit(1)

# Test 4: Bridge script exists
bridge_path = r"C:\Users\User\arifOS\.kimi\kimibridge.py"
if os.path.exists(bridge_path):
    print(f"[PASS] Bridge Script: {bridge_path}")
else:
    print(f"[FAIL] Bridge Script Missing: {bridge_path}")
    sys.exit(1)

# Test 5: Witness skill exists
witness_path = r"C:\Users\User\arifOS\.kimi\skills\constitutional_witness.md"
if os.path.exists(witness_path):
    size = os.path.getsize(witness_path)
    print(f"[PASS] Witness Skill: {witness_path} ({size} bytes)")
else:
    print(f"[FAIL] Witness Skill Missing: {witness_path}")
    sys.exit(1)

# Test 6: MCP Config exists
mcp_config_path = r"C:\Users\User\arifOS\.kimi\mcp.json"
if os.path.exists(mcp_config_path):
    print(f"[PASS] MCP Config: {mcp_config_path}")
else:
    print(f"[FAIL] MCP Config Missing: {mcp_config_path}")
    sys.exit(1)

# Test 7: Check kimibridge.py can be imported
try:
    sys.path.append(r"C:\Users\User\arifOS\.kimi")
    import kimibridge
    print(f"[PASS] Bridge Importable: kimibridge.py")
except Exception as e:
    print(f"[WARN] Bridge Import Test: {e}")

print("=" * 60)
print("DEPLOYMENT STATUS: [READY] All files in place")
print("=" * 60)
print("\nNext Steps:")
print("1. cd C:\\Users\\User\\arifOS")
print("2. Start Kimi in this directory")
print("3. Execute: seal '{\"query\": \"test\"}'") 
print("4. Expected: Session ID + constitutional verdict")
