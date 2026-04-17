#!/usr/bin/env python3
"""
arifOS MCP v2 — Deployment Readiness Check

Run this before deploying to A-FORGE to verify all components are ready.
"""

import asyncio
import sys

def check_imports():
    """Verify all v2 modules can be imported."""
    print("Checking imports...")
    try:
        from arifosmcp.runtime.tool_specs_v2 import V2_TOOLS, v2_tool_names
        from arifosmcp.runtime.tools_v2 import V2_TOOL_HANDLERS
        from arifosmcp.runtime.tools_v2_forge import arifos_forge, ExecutionManifest
        from arifosmcp.runtime.philosophy_registry import inject_philosophy, FORGE_PRINCIPLE_S1
        print(f"  ✅ All v2 modules imported successfully")
        print(f"  ✅ {len(V2_TOOLS)} tools in registry")
        print(f"  ✅ {len(V2_TOOL_HANDLERS)} tool handlers")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def check_tool_count():
    """Verify exactly 10 tools."""
    from arifosmcp.runtime.tool_specs_v2 import V2_TOOL_COUNT
    print(f"\nChecking tool count...")
    if V2_TOOL_COUNT == 10:
        print(f"  ✅ Exactly 10 tools (got {V2_TOOL_COUNT})")
        return True
    else:
        print(f"  ❌ Expected 10 tools, got {V2_TOOL_COUNT}")
        return False

def check_s1_quote():
    """Verify S1 quote exists."""
    from arifosmcp.runtime.philosophy_registry import FORGE_PRINCIPLE_S1
    print(f"\nChecking S1 (Forge Principle)...")
    if FORGE_PRINCIPLE_S1.get("text") == "DITEMPA, BUKAN DIBERI.":
        print(f"  ✅ S1 quote correct: '{FORGE_PRINCIPLE_S1['text']}'")
        return True
    else:
        print(f"  ❌ S1 quote incorrect: {FORGE_PRINCIPLE_S1.get('text')}")
        return False

async def check_philosophy_injection():
    """Verify philosophy injection works correctly."""
    from arifosmcp.runtime.philosophy_registry import inject_philosophy
    
    print(f"\nChecking philosophy injection...")
    
    # Mock envelope
    class MockTelemetry:
        def __init__(self, g_star):
            self.G_star = g_star
    
    class MockMetrics:
        def __init__(self, g_star):
            self.telemetry = MockTelemetry(g_star)
    
    class MockEnvelope:
        def __init__(self, stage, verdict, g_star):
            self.stage = stage
            self.verdict = verdict
            self.session_id = "test"
            self.metrics = MockMetrics(g_star)
    
    # Test INIT override
    env = MockEnvelope("INIT", "PARTIAL", 0.5)
    result = inject_philosophy(env)
    if "DITEMPA" in result.get("entry", {}).get("text", ""):
        print(f"  ✅ INIT override works")
    else:
        print(f"  ❌ INIT override failed")
        return False
    
    # Test SEAL override
    env = MockEnvelope("JUDGE", "SEAL", 0.3)
    result = inject_philosophy(env)
    if "DITEMPA" in result.get("entry", {}).get("text", ""):
        print(f"  ✅ SEAL override works")
    else:
        print(f"  ❌ SEAL override failed")
        return False
    
    # Test G★ band mapping
    env = MockEnvelope("JUDGE", "PARTIAL", 0.1)
    result = inject_philosophy(env)
    if result.get("band") == 0:
        print(f"  ✅ G★ band mapping works (0.1 → Band 0)")
    else:
        print(f"  ❌ G★ band mapping failed (expected Band 0, got {result.get('band')})")
        return False
    
    return True

def check_horizon_mapping():
    """Verify unified server legacy tool mappings."""
    try:
        from server import LEGACY_TOOL_MAP
        print(f"\nChecking unified server legacy mappings...")
        
        expected_mappings = {
            "init_anchor": "arifos_init",
            "apex_soul": "arifos_judge",
            "agi_mind": "arifos_mind",
        }
        
        all_good = True
        for legacy_name, canonical_name in expected_mappings.items():
            if LEGACY_TOOL_MAP.get(legacy_name) == canonical_name:
                print(f"  ✅ {legacy_name} → {canonical_name}")
            else:
                print(f"  ❌ {legacy_name} mapping incorrect (got {LEGACY_TOOL_MAP.get(legacy_name)})")
                all_good = False
        
        print(f"  Total legacy aliases: {len(LEGACY_TOOL_MAP)}")
        return all_good
    except Exception as e:
        print(f"  ❌ Legacy mapping check failed: {e}")
        return False

async def main():
    print("=" * 70)
    print("ARIFOS MCP v2 — DEPLOYMENT READINESS CHECK")
    print("=" * 70)
    
    checks = [
        ("Imports", check_imports),
        ("Tool Count", check_tool_count),
        ("S1 Quote", check_s1_quote),
        ("Philosophy Injection", check_philosophy_injection),
        ("Horizon Mapping", check_horizon_mapping),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            if asyncio.iscoroutinefunction(check_fn):
                result = await check_fn()
            else:
                result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("🚀 READY FOR A-FORGE DEPLOYMENT")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("⚠️  DEPLOYMENT BLOCKED — Fix issues above")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
