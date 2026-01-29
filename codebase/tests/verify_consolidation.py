"""
Verification Script for AGI/ASI Consolidation (v53.3.1)
"""
import asyncio
import logging
from codebase.agi import get_agi_core
from codebase.asi import get_asi_core

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFIER")

async def test_consolidation():
    print("=== IGNTION PROTOCOL ===")
    
    # 1. Ignite AGI (Mind)
    print("\n[1] Igniting AGI (Mind)...")
    agi = get_agi_core()
    print(f"    AGI Version: {agi.version}")
    
    query = "Deploy a new authentication system which might delete old user data."
    print(f"    Query: '{query}'")
    
    agi_result = await agi.sense(query, {"session_id": "test_session_001"})
    print(f"    AGI Status: {agi_result['status']}")
    print(f"    AGI Insight: {agi_result['insight']}")
    print(f"    AGI Verdict: {agi_result['verdict']}")
    print(f"    F4 Clarity: {agi_result['metrics']['delta_bundle']['floor_scores']['F4_clarity']}")

    # 2. Ignite ASI (Heart)
    print("\n[2] Igniting ASI (Heart)...")
    asi = get_asi_core()
    print(f"    ASI Version: {asi.version}")
    
    asi_result = await asi.empathize(query, {"session_id": "test_session_001"})
    print(f"    ASI Status: {asi_result['status']}")
    print(f"    ASI Verdict: {asi_result['verdict']}")
    print(f"    Weakest Stakeholder: {asi_result['weakest_stakeholder']}")
    print(f"    Empathy Score (F6): {asi_result['metrics']['kappa_r']}")

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_consolidation())
