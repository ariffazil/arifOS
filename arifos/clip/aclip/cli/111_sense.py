"""CLI stage 111 - sense."""
from datetime import datetime
import json

import os

def run_stage(session, args):
    # Amanah Sense: Integrity Check
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    secrets_path = os.path.join(repo_root, '.secrets.baseline')
    has_integrity = os.path.exists(secrets_path)
    integrity_status = "TRUSTED (Secrets Baseline Found)" if has_integrity else "WARNING (No Secrets Baseline - Dev Mode)"

    # Perform sense stage logic (stub aligned with v43)
    prev_step = session.data['steps'][-1] if session.data.get('steps') else None
    
    # Sense Context
    result = {
        "status": "SENSED",
        "integrity": integrity_status,
        "variables": "Context captured from session initiation."
    }
    
    # Append this stage result to session
    session.data['steps'].append({
        'stage': 111,
        'name': 'sense',
        'input': prev_step['output'] if prev_step else session.data.get('task'),
        'output': result,
        'exit_code': 0,
        'timestamp': datetime.now().isoformat()
    })
    session.data['status'] = 'ACTIVE'
    
    if args.json:
        print(json.dumps(session.data['steps'][-1], indent=2))
    else:
        print(f"Stage 111 (SENSE) Complete.")
        print(f"Amanah Integrity: {integrity_status}")
        print("\nCopy-paste:")
        print(f"/222 {session.data['id']}")
    return 0
