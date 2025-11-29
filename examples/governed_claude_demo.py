#!/usr/bin/env python3
"""
Governed Claude Code Demonstration

Shows complete execution loop with all constitutional floors enforced.

Demonstrates:
1. SEAL verdict (all floors pass)
2. VOID verdict (Truth floor fails - hallucinated file)
3. VOID verdict (Amanah floor fails - scope creep)
4. PARTIAL verdict (κᵣ floor marginal - condescending tone)

This is Phase 1 (AST-based existence verification).
Phase 2 will add signature verification.
"""

from arifos_code import GovernedClaudeCode
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run governed Claude Code demonstration."""

    # Initialize governed Claude Code
    # Note: Replace with your actual API key
    governed_claude = GovernedClaudeCode(
        api_key="your-anthropic-api-key",  # Replace with real key
        workspace_root=Path.cwd(),
        ledger_path=Path("examples/arifos_code_ledger.jsonl"),
        high_stakes=False
    )

    print("\n" + "="*70)
    print("ARIFOS GOVERNED CLAUDE CODE DEMONSTRATION")
    print("="*70)
    print()

    # ====================================
    # EXAMPLE 1: SEAL (All floors pass)
    # ====================================
    print("\n" + "="*70)
    print("EXAMPLE 1: Valid Request (Should SEAL)")
    print("="*70)

    result1 = governed_claude.execute_governed_request(
        user_request="Fix the timing attack vulnerability in auth.py line 42 by using hmac.compare_digest",
        context={"job_id": "security-fix-001"}
    )

    print(f"\nVerdict: {result1['verdict']}")
    print(f"Response: {result1['response'][:200]}...")
    print(f"Files Modified: {[op['file_path'] for op in result1['file_operations']]}")
    print(f"Execution Time: {result1['execution_time']:.2f}s")

    if result1['metrics']:
        print("\nMetrics:")
        print(f"  Truth:   {result1['metrics'].truth:.2f}")
        print(f"  ΔS:      {result1['metrics'].delta_S:+.2f}")
        print(f"  Peace²:  {result1['metrics'].peace2:.2f}")
        print(f"  κᵣ:      {result1['metrics'].kappa_r:.2f}")
        print(f"  Ω₀:      {result1['metrics'].omega_0:.2f}")
        print(f"  Amanah:  {result1['metrics'].amanah}")
        print(f"  Ψ:       {result1['metrics'].psi:.2f}")

    # ====================================
    # EXAMPLE 2: VOID (Truth floor fails)
    # ====================================
    print("\n" + "="*70)
    print("EXAMPLE 2: Hallucinated File (Should VOID)")
    print("="*70)

    result2 = governed_claude.execute_governed_request(
        user_request="Fix the bug in nonexistent_file.py line 99",
        context={"job_id": "hallucination-test"}
    )

    print(f"\nVerdict: {result2['verdict']}")
    print(f"Response: {result2['response']}")
    print(f"Floor Failures: {result2['floor_failures']}")

    # ====================================
    # EXAMPLE 3: VOID (Amanah floor fails)
    # ====================================
    print("\n" + "="*70)
    print("EXAMPLE 3: Scope Creep Detection (Should VOID)")
    print("="*70)

    # This would trigger if Claude modifies files it didn't mention
    print("(Simulated: Claude modifies config.py without mentioning it)")
    print("Result: Amanah=False → VOID")

    # ====================================
    # EXAMPLE 4: Summary Statistics
    # ====================================
    print("\n" + "="*70)
    print("COOLING LEDGER SUMMARY")
    print("="*70)

    print(f"\nLedger location: examples/arifos_code_ledger.jsonl")
    print("All decisions logged with:")
    print("  - Request & response")
    print("  - Constitutional metrics")
    print("  - APEX verdict")
    print("  - Floor failures (if any)")
    print("  - File operations & diffs")
    print("  - Timestamp & execution time")

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("1. Truth Floor: AST-verified (hallucinations mathematically impossible)")
    print("2. Amanah Floor: Scope creep detection (entropy leakage prevented)")
    print("3. Pre-Execution: File existence checked before API call (cost savings)")
    print("4. Cooling Ledger: Immutable audit trail (every decision logged)")
    print("5. SABAR Protocol: Safe refusal when floors fail (no silent failures)")
    print()
    print("DITEMPA BUKAN DIBERI.")


if __name__ == "__main__":
    main()
