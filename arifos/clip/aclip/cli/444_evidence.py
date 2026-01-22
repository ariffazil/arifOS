"""CLI stage 444 - evidence."""
from datetime import datetime
import json

def run_stage(session, args):
    # Perform evidence stage logic (stub)
    prev_step = session.data['steps'][-1] if session.data.get('steps') else None
    result = "Evidence gathered."
    # Append this stage result to session
    session.data['steps'].append({
        'stage': 444,
        'name': 'evidence',
        'input': prev_step['output'] if prev_step else session.data.get('task'),
        'output': result,
        'exit_code': 0,
        'timestamp': datetime.now().isoformat()
    })
    session.data['status'] = 'ACTIVE'
    if args.json:
        # Output the latest step as JSON
        print(json.dumps(session.data['steps'][-1], indent=2))
    else:
        # v43 Audit Logic
        evidence_data = ' '.join(args.input) if hasattr(args, 'input') else "None"
        evidence_size = len(evidence_data)
        
        # Audit Check (Simulated)
        audit_status = "VERIFIED" if evidence_size > 50 else "WEAK (Low Data Volume)"
        
        print("Stage 444 (EVIDENCE) Complete.")
        print(f"Audit Status: {audit_status} (Size: {evidence_size} bytes)")
        
        # Conditional Routing (v43 Zero-Friction)
        if "CONTESTED" in evidence_data:
            print("\nAUTO-ROUTE (Contested Evidence):")
            print("\nCopy-paste:")
            print(f"/888 {session.data['id']} --reason 'Contested Evidence'")
        else:
            print("\nCopy-paste:")
            print(f"/555 {session.data['id']}")
    return 0
