import asyncio
import os
from core.organs._0_init import init
from core.organs._2_asi import asi

async def verify_organs_direct():
    print("=== arifOS Contrast Audit: Direct Organs ===", flush=True)
    
    # 1. INIT
    print("\n[INIT] Executing...", flush=True)
    init_res = await init(query="Plan a Dyson Sphere.")
    print(f"  Verdict: {init_res.verdict}", flush=True)
    # Extract session safely from InitOutput (it's session_id)
    session_id = init_res.session_id
    
    # 2. ASI (Simulate)
    print("\n[ASI_SIMULATE] Executing...", flush=True)
    asi_res = await asi(action="simulate_heart", session_id=session_id, scenario="Impact.")
    print(f"  Risk: {asi_res.assessment.risk_level}", flush=True)
    print(f"  Peace2: {asi_res.floor_scores.f5_peace}", flush=True)
    
    # 3. ASI (Critique)
    print("\n[ASI_CRITIQUE] Executing...", flush=True)
    crit_res = await asi(action="critique_thought", session_id=session_id, thought_content="Safe.")
    print(f"  Severity: {crit_res.critique.severity}", flush=True)
    print(f"  Findings: {len(crit_res.critique.findings)}", flush=True)

    print("\nSUCCESS: Tools are contrasted and functional at organ level.", flush=True)

if __name__ == "__main__":
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    asyncio.run(verify_organs_direct())
