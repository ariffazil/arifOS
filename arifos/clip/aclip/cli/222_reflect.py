"""CLI stage 222 - reflect."""
from datetime import datetime
import json

def run_stage(session, args):
    # Perform reflect stage logic (stub)
    prev_step = session.data['steps'][-1] if session.data.get('steps') else None
    result = "Reflections noted."
    # Append this stage result to session
    session.data['steps'].append({
        'stage': 222,
        'name': 'reflect',
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
        print("Stage 222 (REFLECT) Complete.")
        print("\nCopy-paste:")
        print(f"/333 {session.data['id']}")
    return 0
