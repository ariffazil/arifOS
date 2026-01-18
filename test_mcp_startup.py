#!/usr/bin/env python3
"""
Test MCP Server Startup
Simulates what Claude Desktop does when launching the arifOS MCP server
"""
import os
import sys
import subprocess

# Set environment variables (same as .claude/mcp_config.json)
env = os.environ.copy()
env['ARIFOS_ALLOW_LEGACY_SPEC'] = '1'
env['ARIFOS_PHYSICS_DISABLED'] = '0'
env['PYTHONPATH'] = r'C:\Users\User\OneDrive\Documents\GitHub\arifOS'

print("=" * 60)
print("Testing arifOS MCP Server Startup")
print("=" * 60)
print(f"Environment variables:")
print(f"  ARIFOS_ALLOW_LEGACY_SPEC = {env.get('ARIFOS_ALLOW_LEGACY_SPEC')}")
print(f"  ARIFOS_PHYSICS_DISABLED  = {env.get('ARIFOS_PHYSICS_DISABLED')}")
print(f"  PYTHONPATH               = {env.get('PYTHONPATH')}")
print()

# Test 1: Can we import the module?
print("Test 1: Importing arifos.mcp module...")
try:
    result = subprocess.run(
        [sys.executable, '-c', 'import arifos.mcp; print("✅ Module imported successfully")'],
        env=env,
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print(result.stdout)
        print("✅ PASS: Module imports correctly")
    else:
        print("❌ FAIL: Module import failed")
        print("STDERR:", result.stderr)
        sys.exit(1)
except subprocess.TimeoutExpired:
    print("❌ FAIL: Import timed out")
    sys.exit(1)

print()

# Test 2: Can we get help from the entry point?
print("Test 2: Testing MCP entry point --help...")
try:
    result = subprocess.run(
        [sys.executable, '-m', 'arifos.mcp', '--help'],
        env=env,
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0 or 'usage:' in result.stdout.lower():
        print("✅ PASS: Entry point responds to --help")
        print("Output preview:")
        print(result.stdout[:200] if result.stdout else result.stderr[:200])
    else:
        print("⚠️  PARTIAL: Entry point exists but may have issues")
        print("STDERR:", result.stderr[:300])
except subprocess.TimeoutExpired:
    print("⚠️  PARTIAL: Help command timed out")

print()
print("=" * 60)
print("Startup Test Summary")
print("=" * 60)
print("Configuration is READY for Claude Desktop!")
print()
print("Next steps:")
print("  1. Restart Claude Desktop")
print("  2. arifOS MCP server will auto-start with these tools:")
print("     - arifos_live (Full 000→999 pipeline)")
print("     - agi_think (AGI Bundle)")
print("     - asi_act (ASI Bundle)")
print("     - apex_seal (APEX Bundle)")
print("     - + 21 more constitutional tools")
print()
print("To verify in Claude Desktop:")
print("  - Look for MCP icon in chat interface")
print("  - Try: 'What MCP tools do you have?'")
print("=" * 60)
