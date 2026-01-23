"""CLI stage 333 - reason."""
from datetime import datetime
import json

def run_stage(session, args):
    # Perform reason stage logic (stub)
    prev_step = session.data['steps'][-1] if session.data.get('steps') else None
    result = "Logical reasoning completed."
    # Append this stage result to session
    session.data['steps'].append({
        'stage': 333,
        'name': 'reason',
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
        print("Stage 333 (REASON) Complete.")
        print("Logic Decomposed: 000-999 is a 'Thermodynamic Metabolism' cycle.")
        print("\nCopy-paste:")
        print(f"/444 {session.data['id']}")
    return 0
