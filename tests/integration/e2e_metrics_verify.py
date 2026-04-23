import asyncio
import json
import os
import sys

# Ensure arifosmcp is in path
sys.path.append(os.getcwd())

from arifosmcp.runtime.tools_hardened_dispatch import hardened_agi_mind_dispatch

async def run_test():
    print("--- E2E EMPIRICAL VERIFICATION REPORT ---")
    
    # Scenario 1: Detailed Query -> Resulting in Clarity
    query_1 = "Requesting logical analysis of the 13 Constitutional Floors specifically regarding F11 and F13 interaction."
    res_1 = await hardened_agi_mind_dispatch('reason', {'query': query_1})
    
    # Scenario 2: Minimal Query -> Higher relative entropy compared to input
    query_2 = "..."
    res_2 = await hardened_agi_mind_dispatch('reason', {'query': query_2})
    
    print(f"Test 1 (High Signal):")
    print(f"  Input Len: {len(query_1)}")
    print(f"  Delta S:   {res_1['entropy']['delta_s']}")
    print(f"  G-Score:   {res_1['g_score']}")
    print(f"  Humility:  {res_1['humility_band']}")
    
    print(f"\nTest 2 (Low Signal):")
    print(f"  Input Len: {len(query_2)}")
    print(f"  Delta S:   {res_2['entropy']['delta_s']}")
    print(f"  G-Score:   {res_2['g_score']}")
    print(f"  Humility:  {res_2['humility_band']}")
    
    # Conclusion on Reality
    # If entropy is live, Delta-S must be different for different inputs
    if res_1['entropy']['delta_s'] != res_2['entropy']['delta_s']:
        print("\nVERDICT: MEASUREMENTS ARE LIVE AND VARIABLE. ✅")
    else:
        print("\nVERDICT: MEASUREMENTS ARE STAGNANT. ❌")

if __name__ == '__main__':
    asyncio.run(run_test())
