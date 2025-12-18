"""CLI stage 666 - align."""
from datetime import datetime
import json
from arifos_clip.aclip.bridge import arifos_client

from arifos_clip.aclip.core.agents import FederationEngine

def run_stage(session, args):
    # v43 Automatic Gatekeeper
    engine = FederationEngine()
    agent_results = engine.run_all(session.data) # Agents measure session
    
    # Compute Governance Score (Simple Average for Phase 1)
    scores = [r.get('score', 0) for r in agent_results.values()]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    vetoes = engine.check_veto(agent_results)
    
    # Decision Logic (Sovereign Gatekeeper)
    gate_decision = "FAIL"
    next_trigger = None
    
    if vetoes:
        gate_decision = "FLAG (Veto Triggered)"
        next_trigger = f"/888 {session.data['id']} --reason 'Agent Veto: {vetoes}'"
    elif avg_score >= 0.85:
        gate_decision = "PASS (Ready to Forge)"
        next_trigger = f"/777 {session.data['id']}"
    elif avg_score >= 0.50:
        gate_decision = "FLAG (Governance Gaps)"
        next_trigger = f"/888 {session.data['id']} --reason 'Low Governance Score ({avg_score:.2f})'"
    else:
        gate_decision = "FAIL (Refused)"
        # No trigger generated
        
    result = {
        "status": "ALIGNED",
        "score": avg_score,
        "gate": gate_decision,
        "agents": agent_results
    }
    
    # Append this stage result to session
    session.data['steps'].append({
        'stage': 666,
        'name': 'align',
        'input': session.data.get('id'),
        'output': result,
        'exit_code': 0,
        'timestamp': datetime.now().isoformat()
    })
    session.data['status'] = 'ACTIVE'

    if args.json:
        print(json.dumps(session.data['steps'][-1], indent=2))
    else:
        print(f"Stage 666 (ALIGN) Complete.")
        print(f"Governance Score: {avg_score:.2f} | Verdict: {gate_decision}")
        if next_trigger:
            print("\nCopy-paste:")
            print(next_trigger)
        else:
            print("\nSYSTEM REFUSAL: Governance score too low to proceed.")
    return 0
