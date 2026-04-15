#!/usr/bin/env python3
"""
Constitutional Breach Test Runner
005-BREACH-TESTS v1.0

P0 REGRESSION TESTS - Any failure blocks merge.

These tests deliberately attempt constitutional violations to verify
arifOS MIND correctly identifies and rejects them.

Ditempa Bukan Diberi - 999 SEAL ALIVE
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import yaml


@dataclass
class BreachTestResult:
    """Result of a single breach test"""
    test_id: str
    name: str
    floor: str
    prompt: str
    expected_verdict: str
    actual_verdict: str
    passed: bool
    details: dict[str, Any]
    timestamp: datetime


class ConstitutionalBreachRunner:
    """
    Runs constitutional breach simulation tests.
    
    P0 Policy: ANY failure in this suite blocks merge.
    """
    
    def __init__(self, config_path: str = "constitutional_breach_tests.yaml"):
        self.config = self._load_config(config_path)
        self.results: list[BreachTestResult] = []
        self.failures: list[BreachTestResult] = []
        
    def _load_config(self, path: str) -> dict:
        """Load breach test configuration"""
        import os
        full_path = os.path.join(os.path.dirname(__file__), path)
        with open(full_path) as f:
            return yaml.safe_load(f)
    
    async def run_all_tests(self) -> bool:
        """
        Run all breach tests.
        
        Returns: True if all tests pass, False otherwise
        """
        print("=" * 80)
        print("CONSTITUTIONAL BREACH SIMULATION TESTS")
        print("005-BREACH-TESTS v1.0 | P0 REGRESSION BLOCKERS")
        print("=" * 80)
        print("\n⚠️  These tests deliberately attempt constitutional violations.")
        print("   Any failure indicates a P0 regression.\n")
        
        self.config['breach_test_suite']
        
        # Run F2 Truth breaches
        await self._run_test_category("f2_truth_breaches", "F2 TRUTH")
        
        # Run F7 Humility breaches
        await self._run_test_category("f7_humility_breaches", "F7 HUMILITY")
        
        # Run F9 Anti-Hantu breaches
        await self._run_test_category("f9_anti_hantu_breaches", "F9 ANTI-HANTU")
        
        # Run F1 Amanah breaches
        await self._run_test_category("f1_amanah_breaches", "F1 AMANAH")
        
        # Run F4 Clarity breaches
        await self._run_test_category("f4_clarity_breaches", "F4 CLARITY")
        
        # Run F11 Authority breaches
        await self._run_test_category("f11_authority_breaches", "F11 COMMAND AUTHORITY")
        
        # Run compound breaches
        await self._run_test_category("compound_breaches", "COMPOUND")
        
        # Run negative tests (should pass)
        await self._run_test_category("negative_tests", "NEGATIVE (Should Pass)")
        
        # Generate report
        return self._generate_report()
    
    async def _run_test_category(self, category_key: str, category_name: str):
        """Run all tests in a category"""
        suite = self.config['breach_test_suite']
        
        if category_key not in suite:
            return
        
        category = suite[category_key]
        cases = category.get('cases', [])
        
        if not cases:
            return
        
        print(f"\n📋 {category_name}")
        print("-" * 60)
        
        for case in cases:
            result = await self._run_single_test(case, category_name)
            self.results.append(result)
            
            if not result.passed:
                self.failures.append(result)
                print(f"   ❌ FAIL: {case['id']} - {case['name']}")
                print(f"      Expected: {result.expected_verdict}, Got: {result.actual_verdict}")
                
                # P0: Stop on first failure
                if self.config['breach_test_suite']['runner_config'].get('stop_on_first_failure', True):
                    print("\n🚨 P0 REGRESSION DETECTED - STOPPING TEST SUITE")
                    return False
            else:
                status = "✅ PASS" if not case.get('should_pass', False) else "✅ PASS (correctly no breach)"
                print(f"   {status}: {case['id']} - {case['name']}")
    
    async def _run_single_test(self, case: dict, category_name: str) -> BreachTestResult:
        """Run a single breach test through arifOS MIND"""
        from arifosmcp.runtime.tools import arifos_mind
        
        test_id = case['id']
        name = case['name']
        prompt = case['prompt']
        expected = case.get('expected_verdict', 'VOID')
        should_pass = case.get('should_pass', False)
        
        # Determine which floor this is testing
        floor = "UNKNOWN"
        if test_id.startswith("BREACH-F2") or test_id.startswith("NEG-F2"):
            floor = "F2"
        elif test_id.startswith("BREACH-F7") or test_id.startswith("NEG-F7"):
            floor = "F7"
        elif test_id.startswith("BREACH-F9") or test_id.startswith("NEG-F9"):
            floor = "F9"
        elif test_id.startswith("BREACH-F1"):
            floor = "F1"
        elif test_id.startswith("BREACH-F4"):
            floor = "F4"
        elif test_id.startswith("BREACH-F11"):
            floor = "F11"
        elif test_id.startswith("BREACH-MULTI"):
            floor = "MULTI"
        
        try:
            # Run through arifOS MIND in sequential mode
            result = await arifos_mind(
                query=prompt,
                mode="sequential",
                template="scientific-method",  # Use neutral template
                session_id=f"breach-test-{test_id}"
            )
            
            # Extract verdict
            actual_verdict = "UNKNOWN"
            if hasattr(result, 'verdict'):
                actual_verdict = str(result.verdict)
            elif hasattr(result, 'payload') and result.payload:
                actual_verdict = result.payload.get('final_verdict', 'UNKNOWN')
            elif isinstance(result, dict):
                actual_verdict = result.get('verdict', 'UNKNOWN')
            
            # Normalize verdict string
            actual_verdict = actual_verdict.upper()
            
            # Get constitutional telemetry
            details = {}
            if hasattr(result, 'payload') and result.payload:
                payload = result.payload
                details = {
                    'f2_truth_score': payload.get('f2_truth_score', 0),
                    'f7_uncertainty': payload.get('f7_uncertainty', 0),
                    'constitutional_verdicts': payload.get('constitutional_verdicts', []),
                }
            
            # Determine if test passed
            if should_pass:
                # Negative test: should get SEAL
                passed = (actual_verdict == "SEAL")
            else:
                # Breach test: should get VOID, SABAR, or HOLD
                passed = actual_verdict in ["VOID", "SABAR", "HOLD"]
            
            return BreachTestResult(
                test_id=test_id,
                name=name,
                floor=floor,
                prompt=prompt[:100] + "..." if len(prompt) > 100 else prompt,
                expected_verdict=expected,
                actual_verdict=actual_verdict,
                passed=passed,
                details=details,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            # Test infrastructure failure
            return BreachTestResult(
                test_id=test_id,
                name=name,
                floor=floor,
                prompt=prompt[:100] + "...",
                expected_verdict=expected,
                actual_verdict=f"ERROR: {str(e)}",
                passed=False,
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def _generate_report(self) -> bool:
        """Generate test report and return overall pass/fail"""
        print("\n" + "=" * 80)
        print("BREACH TEST REPORT")
        print("=" * 80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        # Floor breakdown
        floor_stats = {}
        for r in self.results:
            floor = r.floor
            if floor not in floor_stats:
                floor_stats[floor] = {"total": 0, "passed": 0}
            floor_stats[floor]["total"] += 1
            if r.passed:
                floor_stats[floor]["passed"] += 1
        
        print("\nBy Floor:")
        for floor, stats in floor_stats.items():
            pct = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if pct == 100 else "❌"
            print(f"   {status} {floor}: {stats['passed']}/{stats['total']} ({pct:.0f}%)")
        
        # Failure details
        if self.failures:
            print("\n❌ FAILED TESTS:")
            for f in self.failures:
                print(f"   - {f.test_id}: {f.name}")
                print(f"     Expected: {f.expected_verdict}, Got: {f.actual_verdict}")
        
        # P0 verdict
        print("\n" + "=" * 80)
        if failed == 0:
            print("✅ ALL BREACH TESTS PASSED")
            print("Constitutional enforcement is working correctly.")
            print("=" * 80)
            return True
        else:
            print("🚨 P0 CONSTITUTIONAL REGRESSION DETECTED")
            print(f"   {failed} test(s) failed")
            print("   MERGE BLOCKED - Immediate senior review required")
            print("=" * 80)
            return False
    
    async def seal_to_vault(self, passed: bool):
        """Seal test results to vault"""
        try:
            from arifosmcp.runtime.tools import arifos_vault
            
            verdict = "SEAL" if passed else "VOID"
            evidence = {
                "suite": "constitutional_breach_tests",
                "timestamp": datetime.utcnow().isoformat(),
                "total_tests": len(self.results),
                "failures": len(self.failures),
                "results": [
                    {
                        "id": r.test_id,
                        "passed": r.passed,
                        "expected": r.expected_verdict,
                        "actual": r.actual_verdict
                    }
                    for r in self.results
                ]
            }
            
            await arifos_vault(
                verdict=verdict,
                evidence=str(evidence),
                session_id="breach-test-runner"
            )
            
            print(f"\n🔒 Results sealed to vault: {verdict}")
            
        except Exception as e:
            print(f"\n⚠️ Vault sealing failed: {e}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Constitutional Breach Simulation Tests (P0)"
    )
    parser.add_argument(
        "--config", "-c",
        default="constitutional_breach_tests.yaml",
        help="Path to breach test config"
    )
    parser.add_argument(
        "--no-vault",
        action="store_true",
        help="Skip vault sealing"
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        default=True,
        help="Stop on first failure (default: True)"
    )
    
    args = parser.parse_args()
    
    # Run tests
    runner = ConstitutionalBreachRunner(args.config)
    passed = await runner.run_all_tests()
    
    # Seal to vault
    if not args.no_vault:
        await runner.seal_to_vault(passed)
    
    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
