#!/usr/bin/env python3
"""
Test MCP Server Connection and Tool Availability
Quick validation that the unified MCP server is operational
"""

import os
import sys
import json
from pathlib import Path

# Set environment variables
os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"
os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"

# Add repo to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

def test_imports():
    """Test that all critical imports work"""
    print("=" * 80)
    print("Test 1: Import Validation")
    print("=" * 80)

    tests = [
        ("arifos_core", "Core package"),
        ("arifos_core.mcp.unified_server", "Unified MCP server"),
        ("arifos_core.agi.delta_kernel", "AGI Delta kernel"),
        ("arifos_core.asi.omega_kernel", "ASI Omega kernel"),
        ("arifos_core.apex.psi_kernel", "APEX Psi kernel"),
        ("arifos_core.system.apex_prime", "APEX Prime"),
        ("arifos_core.enforcement.metrics", "Constitutional metrics"),
    ]

    passed = 0
    failed = 0

    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"[PASS] {description:40s} [{module_name}]")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {description:40s} [{module_name}]")
            print(f"       Error: {e}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_server_module():
    """Test that the MCP server module loads correctly"""
    print("\n" + "=" * 80)
    print("Test 2: MCP Server Module")
    print("=" * 80)

    try:
        from arifos.mcp.unified_server import UNIFIED_TOOLS

        print(f"[PASS] Unified server module loaded")
        print(f"   Total tools available: {len(UNIFIED_TOOLS)}")
        print()
        print("Available tools:")
        for i, tool in enumerate(UNIFIED_TOOLS, 1):
            print(f"   {i:2d}. {tool['name']:30s} - {tool.get('description', 'N/A')[:50]}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to load unified server module")
        print(f"   Error: {e}")
        return False


def test_constitutional_metrics():
    """Test that constitutional metrics can be calculated"""
    print("\n" + "=" * 80)
    print("Test 3: Constitutional Metrics Calculation")
    print("=" * 80)

    try:
        from arifos.enforcement.metrics import Metrics

        # Create sample metrics
        metrics = Metrics()

        print("[PASS] Metrics class instantiated")
        print(f"   Metrics attributes: {list(vars(metrics).keys())[:5]}...")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to create metrics")
        print(f"   Error: {e}")
        return False


def test_trinity_kernels():
    """Test that Trinity kernels can be instantiated"""
    print("\n" + "=" * 80)
    print("Test 4: Trinity Kernel Instantiation")
    print("=" * 80)

    results = []

    # Test AGI Delta Kernel
    try:
        from arifos.agi.delta_kernel import DeltaKernel
        delta = DeltaKernel()
        print(f"[PASS] AGI Delta Kernel (Δ) - Architect")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] AGI Delta Kernel failed: {e}")
        results.append(False)

    # Test ASI Omega Kernel
    try:
        from arifos.asi.omega_kernel import OmegaKernel
        omega = OmegaKernel()
        print(f"[PASS] ASI Omega Kernel (Ω) - Engineer")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] ASI Omega Kernel failed: {e}")
        results.append(False)

    # Test APEX Psi Kernel
    try:
        from arifos.apex.psi_kernel import PsiKernel
        psi = PsiKernel()
        print(f"[PASS] APEX Psi Kernel (Ψ) - Judge")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] APEX Psi Kernel failed: {e}")
        results.append(False)

    return all(results)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("arifOS MCP Server Connection Test")
    print("Version: v47.0.0")
    print("=" * 80)
    print()

    all_passed = True

    # Run tests
    all_passed &= test_imports()
    all_passed &= test_server_module()
    all_passed &= test_constitutional_metrics()
    all_passed &= test_trinity_kernels()

    # Final summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    if all_passed:
        print("[PASS] ALL TESTS PASSED - MCP server is ready")
        print()
        print("Next steps:")
        print("1. Start the MCP server: python scripts\\unified_mcp_entry.py")
        print("2. Or use the batch file: start_mcp.bat")
        print("3. Connect your agents using the configs in .kimi/, .codex/, .antigravity/")
        sys.exit(0)
    else:
        print("[FAIL] SOME TESTS FAILED - Review errors above")
        print()
        print("Troubleshooting:")
        print("1. Ensure ARIFOS_ALLOW_LEGACY_SPEC=1 is set")
        print("2. Check that all import fixes are applied")
        print("3. Review MCP_SERVER_ACTIVATION_REPORT_v47.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
