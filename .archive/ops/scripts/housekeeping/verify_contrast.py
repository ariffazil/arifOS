import asyncio
import json
from arifosmcp.runtime.tools import (
    init_anchor, 
    agi_reason, 
    asi_simulate, 
    asi_critique
)
from core.shared.types import Verdict

async def verify_contrast_internal():
    print("=== arifOS Contrast Audit: Internal Engine ===", flush=True)
    
    # 1. SETUP: init_anchor
    print("\n[Stage 000] Initializing Anchor...", flush=True)
    # init_anchor is a @mcp.tool, we call the handler directly
    init_res = await init_anchor(raw_input="Plan a new Dyson Sphere implementation.")
    auth_ctx = init_res.auth_context
    session_id = init_res.session_id
    print(f"  Session: {session_id}", flush=True)
    print(f"  Auth: Minted level '{auth_ctx['authority_level']}'", flush=True)

    results = []
    
    # 2. AGI REASON (Mind)
    print("\n[AGI_REASON] Executing (ARCHITECT)...", flush=True)
    try:
        agi_res = await agi_reason(
            query="Dyson Sphere logic.", 
            session_id=session_id 
            
        )
        # Pydantic model access
        agi_metrics = agi_res.metrics.telemetry
        print(f"  Info: Steps: {len(agi_res.payload.get('steps', []))}, dS: {agi_metrics.dS}", flush=True)
        results.append({"tool": "agi_reason", "metrics": agi_metrics, "verdict": agi_res.verdict, "status": "SUCCESS"})
    except Exception as e:
        print(f"  VIOLATION: {type(e).__name__}: {str(e)}", flush=True)
        results.append({"tool": "agi_reason", "metrics": None, "verdict": "VOID", "status": "FAIL", "error": str(e)})

    # 3. ASI SIMULATE (Heart)
    print("\n[ASI_SIMULATE] Executing (EMPATH)...", flush=True)
    try:
        asi_res = await asi_simulate(
            scenario="Impact.", 
            session_id=session_id 
            
        )
        # Pydantic model access
        asi_metrics = asi_res.metrics.telemetry
        risk = asi_res.payload.get("assessment", {}).get("risk_level")
        print(f"  Info: Risk: {risk}, Peace2: {asi_metrics.peace2}", flush=True)
        results.append({"tool": "asi_simulate", "metrics": asi_metrics, "verdict": asi_res.verdict, "status": "SUCCESS"})
    except Exception as e:
        print(f"  VIOLATION: {type(e).__name__}: {str(e)}", flush=True)
        results.append({"tool": "asi_simulate", "metrics": None, "verdict": "VOID", "status": "FAIL", "error": str(e)})

    # 4. ASI CRITIQUE (Soul/Adversary)
    print("\n[ASI_CRITIQUE] Executing (ADVERSARY)...", flush=True)
    try:
        crit_res = await asi_critique(
            draft_output="A Dyson Sphere is safe.", 
             
            session_id=session_id 
            
        )
        # Pydantic model access
        crit_metrics = crit_res.metrics.telemetry
        severity = crit_res.payload.get("critique", {}).get("severity")
        print(f"  Info: Severity: {severity}, Findings: {len(crit_res.payload.get('critique', {}).get('findings', []))}", flush=True)
        results.append({"tool": "asi_critique", "metrics": crit_metrics, "verdict": crit_res.verdict, "status": "SUCCESS"})
    except Exception as e:
        print(f"  VIOLATION: {type(e).__name__}: {str(e)}", flush=True)
        results.append({"tool": "asi_critique", "metrics": None, "verdict": "VOID", "status": "FAIL", "error": str(e)})

    # 5. CONTRAST ANALYSIS
    print("\n=== Contrast Matrix ===", flush=True)
    
    success_count = sum(1 for r in results if r['status'] == "SUCCESS")
    print(f"  Audit Status: {success_count}/3 tools executed within constitutional bounds.", flush=True)

    if success_count >= 1:
        # Get metrics from successful tools or use placeholders
        agi_ds = results[0]['metrics'].dS if results[0]['status'] == "SUCCESS" else "N/A"
        asi_peace = results[1]['metrics'].peace2 if results[1]['status'] == "SUCCESS" else "N/A"
        critique_verdict = results[2]['verdict']
        
        print(f"  Mind (AGI) -> Thermodynamic Work (dS): {agi_ds}", flush=True)
        print(f"  Heart (ASI) -> Stability Check (Peace2): {asi_peace}", flush=True)
        print(f"  Soul (Critique) -> Sovereignty Verdict: {critique_verdict}", flush=True)
        
        print("\n  ANALYSIS: Internal engine is active and governed.", flush=True)
    else:
        print("\n  CRITICAL: All tools triggered constitutional violations.", flush=True)

if __name__ == "__main__":
    import os
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    os.environ["ARIFOS_DEV_MODE"] = "1"
    asyncio.run(verify_contrast_internal())
