"""
scripts/verify_kernel_1.0.0.py — Canonical Schema Verification

Empirically verifies that arifOS.kernel (metabolic_loop) adheres to the
v1.0.0 Final Canonical Output Schema.

DITEMPA BUKAN DIBERI.
"""

import asyncio
import json
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())


async def main():
    # 1. Setup environment
    os.environ["ARIFOS_GOVERNANCE_SECRET"] = "verification-secret-123"
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"  # Speed up verification

    from arifosmcp.runtime.orchestrator import metabolic_loop

    print("🚀 Starting Kernel v1.0.0 Schema Verification...")

    query = "Indonesia's path to becoming a mineral superpower and implications for ASEAN"

    try:
        # 2. Execute Metabolic Loop
        # We use dry_run=False to test the actual loop logic
        # But we might want to mock the heavy lifting if it hangs
        # For now, let's try a direct call
        result = await metabolic_loop(
            query=query, actor_id="arif-verifier", risk_tier="low", allow_execution=False
        )

        # 3. Contrast Analysis against 1.0.0 Schema
        print("\n📊 Verification Report:")
        print(f"Tool: {result.get('tool')}")
        print(f"Status: {result.get('status')}")
        print(f"Verdict: {result.get('verdict')}")

        required_blocks = ["metrics", "trace", "authority", "payload", "errors", "meta"]
        missing = [b for b in required_blocks if b not in result]

        if not missing:
            print("✅ All 6 unified blocks present.")
        else:
            print(f"❌ Missing blocks: {missing}")

        # 4. Auth Continuity check
        if "auth_context" in result:
            print("✅ auth_context preserved in result (internal continuity).")
        else:
            # Note: in the user's report, auth_context was missing from the output object
            # but used in the logic. We want to ensure it's at least available internally
            # even if excluded from final JSON-RPC response (which exclude=True does)
            print("⚠️ auth_context not in final dict (expected if using exclude=True in model)")

        # 5. Check for the specific bug reported by user
        if "payload" in result and "error" in result["payload"]:
            if "AttributeError" in str(result["payload"]["error"]) or "RuntimeEnvelope" in str(
                result["payload"]["error"]
            ):
                print(f"❌ REGRESSION DETECTED: {result['payload']['error']}")
            else:
                print(f"ℹ️ Payload error: {result['payload']['error']}")

        print("\n--- Canonical 1.0.0 Output Preview ---")
        print(json.dumps(result, indent=2))
        print("--------------------------------------")

    except Exception as e:
        print(f"💥 CRITICAL FAILURE: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
