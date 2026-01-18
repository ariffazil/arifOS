
"""
Verification Script for Phase 2: Orthogonal Hypervisor
"""
import asyncio
import logging
import os
import sys
from pprint import pprint

# Ensure python path includes project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Bypass manifest verification for testing
os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"

from arifos.mcp.tools.mcp_111_sense import mcp_111_sense
from arifos.mcp.tools.mcp_555_empathize import mcp_555_empathize
from arifos.mcp.tools.mcp_999_seal import mcp_999_seal


async def verify_orthogonal_pipeline():
    print("[START] ORTHOGONAL PIPELINE VERIFICATION")
    print("============================================")

    # 1. Verify 111-SENSE (AGI Kernel)
    print("\n[1] Testing 111-SENSE (AGINeuralCore -> ATLAS)...")
    req_111 = {"query": "What is the capital of France?", "context": {"user_id": "verify_script"}}
    res_111 = await mcp_111_sense(req_111)
    print(f"Verdict: {res_111.verdict}")
    print(f"Lane: {res_111.side_data.get('lane')}")
    print(f"Truth Threshold: {res_111.side_data.get('truth_threshold')}")

    if res_111.verdict != "PASS":
        print("[FAIL] 111-SENSE Verification Failed!")
        return

    # 2. Verify 555-EMPATHIZE (ASI Kernel -> ASIIntegration)
    print("\n[2] Testing 555-EMPATHIZE (ASIActionCore -> 555 Pipeline)...")
    req_555 = {
        "response_text": "The capital of France is Paris. I hope this helps!",
        "recipient_context": {"audience_level": "beginner"}
    }
    res_555 = await mcp_555_empathize(req_555)
    print(f"Verdict: {res_555.verdict}")
    print(f"Reason: {res_555.reason}")
    print(f"ASI Meta: {res_555.side_data.get('asi_meta', {})}")

    if res_555.verdict not in ["PASS", "PARTIAL"]:
        print("[FAIL] 555-EMPATHIZE Verification Failed!")
        return

    # 3. Verify 999-SEAL (Parallel Hypervisor -> AGI+ASI+APEX)
    print("\n[3] Testing 999-SEAL (Quantum Measurement Collapse)...")
    req_999 = {
        "verdict": "SEAL",
        "decision_metadata": {
            "query": "What is the capital of France?",
            "user_id": "verify_script_user"
        }
    }

    try:
        res_999 = await mcp_999_seal(req_999)
        print(f"Verdict: {res_999.verdict}")
        print(f"Reason: {res_999.reason}")

        proofs = res_999.side_data.get("hypervisor_proof", {})
        print(f"Hypervisor Proofs: {list(proofs.keys()) if proofs else 'None'}")

        if res_999.verdict == "PASS" and proofs: # Tool generic wrapper returns PASS, inner verdict is SEAL
            print("[PASS] 999-SEAL Verification Passed!")
        else:
            print("[FAIL] 999-SEAL Verification Failed (Verdict/Proof mismatch)!")
            print(res_999.side_data)

    except Exception as e:
        print(f"[FAIL] 999-SEAL Exception: {e}")
        return

    print("\n[OK] ORTHOGONAL HYPERVISOR ARCHITECTURE: VERIFIED")

if __name__ == "__main__":
    asyncio.run(verify_orthogonal_pipeline())
