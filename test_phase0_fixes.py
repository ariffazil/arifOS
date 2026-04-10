#!/usr/bin/env python3
"""
Phase 0 Triage Verification Script
Tests the three hardened lanes:
1. arifos.mind - Kernel invocation
2. arifos.memory - Filesystem operations
3. arifos.ops - Coroutine/validation

Usage: python test_phase0_fixes.py
"""

import asyncio
import sys
import os

# Add arifOS to path
sys.path.insert(0, '/root/arifOS')

from arifosmcp.runtime.tools_internal import (
    agi_mind_dispatch_impl,
    engineering_memory_dispatch_impl,
    math_estimator_dispatch_impl,
    _create_error_envelope,
)
from arifosmcp.runtime.models import Verdict, RuntimeStatus


class MockContext:
    """Mock FastMCP context for testing."""
    async def info(self, msg):
        print(f"  [INFO] {msg}")
    async def error(self, msg):
        print(f"  [ERROR] {msg}")


async def test_mind_lane():
    """Test arifos.mind hardened dispatch."""
    print("\n" + "="*60)
    print("TEST 1: arifos.mind (Kernel Invocation)")
    print("="*60)
    
    ctx = MockContext()
    
    # Test 1a: Missing query (should return error envelope, not raise)
    print("\n1a. Testing missing query validation...")
    try:
        result = await agi_mind_dispatch_impl(
            mode="reason",
            payload={"session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == False, "Should return error for missing query"
        assert result.verdict == Verdict.VOID, "Should be VOID verdict"
        assert "Query is required" in result.detail, "Should mention missing query"
        print("  ✅ PASS: Missing query handled gracefully")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    # Test 1b: Invalid mode (should return error envelope)
    print("\n1b. Testing invalid mode validation...")
    try:
        result = await agi_mind_dispatch_impl(
            mode="invalid_mode",
            payload={"query": "test", "session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == False, "Should return error for invalid mode"
        assert "Invalid mode" in result.detail, "Should mention invalid mode"
        print("  ✅ PASS: Invalid mode handled gracefully")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    print("\n✅ arifos.mind lane: ALL TESTS PASSED")
    return True


async def test_memory_lane():
    """Test arifos.memory hardened dispatch."""
    print("\n" + "="*60)
    print("TEST 2: arifos.memory (Filesystem Operations)")
    print("="*60)
    
    ctx = MockContext()
    
    # Test 2a: Invalid mode (should return error envelope)
    print("\n2a. Testing invalid mode validation...")
    try:
        result = await engineering_memory_dispatch_impl(
            mode="invalid_mode",
            payload={"session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == False, "Should return error for invalid mode"
        assert "Invalid mode" in result.detail, "Should mention invalid mode"
        print("  ✅ PASS: Invalid mode handled gracefully")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    # Test 2b: vector_store with empty content
    print("\n2b. Testing vector_store with empty content...")
    try:
        result = await engineering_memory_dispatch_impl(
            mode="vector_store",
            payload={"content": "", "session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == False, "Should return error for empty content"
        assert "non-empty" in result.detail.lower() or "MISSING_CONTENT" in str(result.errors), "Should mention empty content"
        print("  ✅ PASS: Empty content handled gracefully")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    # Test 2c: vector_forget without memory_ids or query
    print("\n2c. Testing vector_forget without identifiers...")
    try:
        result = await engineering_memory_dispatch_impl(
            mode="vector_forget",
            payload={"session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == False, "Should return error for missing identifiers"
        print("  ✅ PASS: Missing identifiers handled gracefully")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    print("\n✅ arifos.memory lane: ALL TESTS PASSED")
    return True


async def test_ops_lane():
    """Test arifos.ops hardened dispatch."""
    print("\n" + "="*60)
    print("TEST 3: arifos.ops (Coroutine/Validation)")
    print("="*60)
    
    ctx = MockContext()
    
    # Test 3a: Invalid mode (should return error envelope)
    print("\n3a. Testing invalid mode validation...")
    try:
        result = await math_estimator_dispatch_impl(
            mode="invalid_mode",
            payload={"session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == False, "Should return error for invalid mode"
        assert "Invalid mode" in result.detail, "Should mention invalid mode"
        print("  ✅ PASS: Invalid mode handled gracefully")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    # Test 3b: Vitals mode (should work without psutil too)
    print("\n3b. Testing vitals mode...")
    try:
        result = await math_estimator_dispatch_impl(
            mode="vitals",
            payload={"action": "system_check", "session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == True, "Should return success for vitals"
        assert result.payload is not None, "Should have payload"
        assert "vitals" in result.payload or "constitutional" in result.payload, "Should have vitals data"
        print("  ✅ PASS: Vitals mode works")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    # Test 3c: Cost mode
    print("\n3c. Testing cost mode...")
    try:
        result = await math_estimator_dispatch_impl(
            mode="cost",
            payload={"action": "deploy production", "session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == True, "Should return success for cost"
        assert result.payload.get("mode") == "cost", "Should be cost mode"
        print("  ✅ PASS: Cost mode works")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    # Test 3d: Health mode
    print("\n3d. Testing health mode...")
    try:
        result = await math_estimator_dispatch_impl(
            mode="health",
            payload={"session_id": "test-session"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=ctx,
        )
        assert result.ok == True, "Should return success for health"
        assert result.payload.get("mode") == "health", "Should be health mode"
        print("  ✅ PASS: Health mode works")
    except Exception as e:
        print(f"  ❌ FAIL: Exception raised: {e}")
        return False
    
    print("\n✅ arifos.ops lane: ALL TESTS PASSED")
    return True


async def test_error_envelope_creation():
    """Test the error envelope helper."""
    print("\n" + "="*60)
    print("TEST 4: Error Envelope Helper")
    print("="*60)
    
    envelope = _create_error_envelope(
        tool_name="test_tool",
        stage="TEST_STAGE",
        session_id="test-session",
        error_msg="Test error message",
        error_code="TEST_ERROR",
        verdict=Verdict.VOID,
    )
    
    assert envelope.ok == False, "Error envelope should not be ok"
    assert envelope.tool == "test_tool", "Tool name should match"
    assert envelope.stage == "TEST_STAGE", "Stage should match"
    assert envelope.verdict == Verdict.VOID, "Verdict should match"
    assert envelope.status == RuntimeStatus.ERROR, "Status should be ERROR"
    assert "Test error" in envelope.detail, "Detail should contain error message"
    assert len(envelope.errors) == 1, "Should have one error"
    assert envelope.errors[0].code == "TEST_ERROR", "Error code should match"
    
    print("  ✅ PASS: Error envelope creation works correctly")
    return True


async def main():
    """Run all Phase 0 tests."""
    print("\n" + "="*60)
    print("PHASE 0 TRIAGE VERIFICATION")
    print("Testing hardened lanes for arifOS MCP")
    print("="*60)
    
    results = []
    
    try:
        results.append(await test_mind_lane())
    except Exception as e:
        print(f"\n❌ arifos.mind lane CRASHED: {e}")
        results.append(False)
    
    try:
        results.append(await test_memory_lane())
    except Exception as e:
        print(f"\n❌ arifos.memory lane CRASHED: {e}")
        results.append(False)
    
    try:
        results.append(await test_ops_lane())
    except Exception as e:
        print(f"\n❌ arifos.ops lane CRASHED: {e}")
        results.append(False)
    
    try:
        results.append(await test_error_envelope_creation())
    except Exception as e:
        print(f"\n❌ Error envelope test CRASHED: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("PHASE 0 TRIAGE SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n✅ ALL PHASE 0 FIXES VERIFIED")
        print("The three broken lanes are now hardened:")
        print("  - arifos.mind: Kernel invocation validated")
        print("  - arifos.memory: Filesystem errors handled")
        print("  - arifos.ops: Coroutine/validation guarded")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Review the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
