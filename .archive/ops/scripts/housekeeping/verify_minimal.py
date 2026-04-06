import asyncio
import os
import sys

# MOCK context for no-import run
async def verify_contrast_minimal():
    print("=== arifOS Contrast Audit: Minimal ===", flush=True)
    from arifosmcp.runtime.tools import init_anchor, asi_simulate
    
    print("Imported core tools.", flush=True)
    res = await init_anchor(raw_input="test")
    print(f"Init OK. Session: {res.session_id}", flush=True)
    
    res2 = await asi_simulate(scenario="test", session_id=res.session_id)
    print(f"Simulate OK. Risk: {res2.payload.get('assessment', {}).get('risk_level')}", flush=True)

if __name__ == "__main__":
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    asyncio.run(verify_contrast_minimal())
