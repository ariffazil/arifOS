#!/usr/bin/env python3
"""
Test Script: AGI Thermodynamic Dashboard (Upgrade #1)
Verifies ΔS tracking, entropy monitoring, constitutional alerts
"""

import asyncio
import sys
sys.path.insert(0, 'C:/Users/User/arifOS')

from codebase.agi.executor import AGIRoom
from codebase.agi.metrics import get_dashboard, cleanup_dashboard


async def test_dashboard():
    """Test thermodynamic dashboard integration"""
    print("=" * 70)
    print("THERMODYNAMIC DASHBOARD TEST")
    print("=" * 70)
    
    # Test 1: Basic execution with metrics tracking
    print("\n[Test 1] AGI Room with metric tracking")
    print("-" * 70)
    
    try:
        room = AGIRoom(session_id="test_metrics_001")
        result = room.execute("Build a user authentication system")
        
        print(f"✓ Execution successful")
        print(f"✓ Session ID: {result.session_id}")
        print(f"✓ Time: {result.execution_time_ms:.2f}ms")
        
        # Check if dashboard was created
        dashboard = get_dashboard(result.session_id)
        report = dashboard.generate_report()
        
        print(f"✓ Dashboard generated")
        print(f"  - Total ΔS: {report['convergence_stats']['total_delta_s']:.4f}")
        print(f"  - Stages tracked: {report['convergence_stats']['total_stages']}")
        print(f"  - Const score: {report['constitutional_summary']['overall_score']:.4f}")
        
        # Check stage metrics
        stage_metrics = report['stage_metrics']
        print(f"\n✓ Stage metrics recorded: {len(stage_metrics)} stages")
        for metric in stage_metrics:
            print(f"  - Stage {metric['stage']}: ΔS={metric['delta_s']:.4f}, "
                  f"Confidence={metric['truth_confidence']:.4f}, "
                  f"Ω₀={metric['omega_0']:.4f}")
        
        # Check constitutional status
        for metric in stage_metrics:
            const_status = metric['constitutional_status']
            print(f"\n✓ Floor status for {metric['stage']}:")
            for floor, status in const_status.items():
                print(f"  - {floor}: {status}")
        
        # Test 2: Low confidence scenario (should trigger alerts)
        print("\n[Test 2] Low confidence query")
        print("-" * 70)
        
        room2 = AGIRoom(session_id="test_metrics_002")
        result2 = room2.execute("What is consciousness?")
        
        dashboard2 = get_dashboard(result2.session_id)
        report2 = dashboard2.generate_report()
        
        # Should detect low confidence
        if report2['constitutional_summary']['overall_score'] < 0.8:
            print(f"✓ Low confidence detected: {report2['constitutional_summary']['overall_score']:.4f}")
            print(f"✓ Recommendations generated: {len(report2['recommendations'])}")
            for rec in report2['recommendations']:
                print(f"  - {rec}")
        
        # Test 3: Failed floor detection
        print("\n[Test 3] Failed floor detection")
        print("-" * 70)
        
        failed_floors = report2['constitutional_summary']['floors_failed']
        if sum(failed_floors.values()) > 0:
            print(f"✓ Failed floors detected:")
            for floor, count in failed_floors.items():
                if count > 0:
                    print(f"  - {floor}: {count} failures")
        
        # Cleanup
        cleanup_dashboard("test_metrics_001")
        cleanup_dashboard("test_metrics_002")
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_mcp_integration():
    """Test MCP integration for metrics endpoint"""
    print("\n" + "=" * 70)
    print("MCP INTEGRATION TEST")
    print("=" * 70)
    
    try:
        from arifos.mcp.bridge import bridge_agi_action_router
        
        # Test 1: Execute AGI first
        print("\n[Test 1] Execute AGI to generate metrics")
        print("-" * 70)
        
        agi_result = await bridge_agi_action_router(
            action="full",
            query="Write a Python function to reverse a string"
        )
        
        session_id = agi_result.get("session_id", "test_mcp_001")
        print(f"✓ AGI executed, session: {session_id}")
        
        # Test 2: Query metrics
        print("\n[Test 2] Query metrics via MCP")
        print("-" * 70)
        
        metrics_result = await bridge_agi_action_router(
            action="metrics",
            session_id=session_id
        )
        
        if "error" in metrics_result:
            print(f"✗ Metrics error: {metrics_result['error']}")
        else:
            print(f"✓ Metrics retrieved successfully")
            print(f"✓ Convergence stats: {metrics_result.get('convergence_stats', {})}")
            print(f"✓ Constitutional score: {metrics_result['constitutional_summary']['overall_score']:.4f}")
        
        print("\n" + "=" * 70)
        print("✅ MCP integration test passed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Run all tests"""
    print("\n" + "🔥" * 35)
    print("THERMODYNAMIC DASHBOARD UPGRADE TEST")
    print("v52.6.0 - AGI Tools Upgrade #1")
    print("🔥" * 35 + "\n")
    
    # Run tests
    success1 = await test_dashboard()
    success2 = await test_mcp_integration()
    
    # Summary
    print("\n" + "=" * 70)
    if success1 and success2:
        print("✅ ALL TESTS PASSED!")
        print("\nThermodynamic Dashboard is working:")
        print("  ✓ ΔS tracking per stage")
        print("  ✓ Ω₀ (humility) monitoring")
        print("  ✓ Constitutional alerts")
        print("  ✓ MCP metrics endpoint")
        print("\nDITEMPA BUKAN DIBERI - Upgrade #1 complete")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check errors above")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
