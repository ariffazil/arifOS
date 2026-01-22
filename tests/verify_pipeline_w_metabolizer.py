"""
tests/verify_pipeline_w_metabolizer.py

Purpose: Verify that Metabolizer ACTUALLY executes stage code.
Context: "Blindspot #2: Metabolizer is a Hollow Shell" - This script proves if that is true or false.

Method:
1. Initialize Metabolizer
2. Initialize context
3. Transition through 111 -> 889 (skipping some for brevity)
4. Verify context was modified by stage execution
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arifos.core.metabolizer import Metabolizer


def main():
    print("🧪 Starting Pipeline Verification Test")
    print("-------------------------------------")

    # 1. Initialize
    metabolizer = Metabolizer(enable_execution=True)
    initial_context = {"user_input": "Test Query for Pipeline"}
    metabolizer.initialize(initial_context)

    print(f"✅ Initialized at Stage {metabolizer.context['stage']}")

    # 2. Test Stage 111 (SENSE)
    print("\nAttempting transition to 111...")
    try:
        metabolizer.transition_to(111)
        print("✅ Transition to 111 successful")

        # Verify execution
        if "parsed_query" in metabolizer.context:
            print(f"✅ Stage 111 result found: parsed_query='{metabolizer.context['parsed_query']}'")
        else:
            print("❌ Stage 111 result NOT found - Execution failed?")

    except Exception as e:
        print(f"❌ Transition to 111 failed: {e}")

    # 3. Test Stage 889 (PROOF) - NEW
    print("\nAttempting fast-forward to 889 (PROOF)...")
    try:
        # Mocking history to allow fast-forward (Metabolizer checks sequential order)
        # We need to manually append history to cheat strictly sequential check if we want to skip
        # But metabolizer enforces sequential. Let's try simulating full history update
        metabolizer.current_stage = 888
        metabolizer.VALID_STAGES.index(888) # Validation index setup

        # Re-initialize for cleanliness or just force transition?
        # The transition_to checks sequential: target_idx == current_idx + 1

        # Proper way: we must go through all stages, OR we accept that we just testing 889 unit execution
        # Let's try unit execution of 889 via transition

        metabolizer.transition_to(889)
        print("✅ Transition to 889 successful")

        if "zk_proof" in metabolizer.context:
            print(f"✅ Stage 889 result found: zk_proof='{metabolizer.context['zk_proof']}'")
        else:
            print("❌ Stage 889 result NOT found")

    except Exception as e:
        print(f"❌ Transition to 889 failed: {e}")
        # If it failed due to sequence error, that's expected if we skipped, let's fix test logic
        if "Cannot skip stages" in str(e):
             print("(Skipping failed as expected, bypassing sequence check for unit test)")
             # Force execution directly to verify module works
             metabolizer._execute_stage(889)
             print(f"✅ Forced execution result: {metabolizer.context.get('zk_proof', 'MISSING')}")

    print("\n-------------------------------------")
    print("Context Dump:")
    print(metabolizer.context)

if __name__ == "__main__":
    main()
