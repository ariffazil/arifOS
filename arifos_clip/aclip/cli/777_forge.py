"""CLI stage 777 - forge."""
from datetime import datetime
import json
import os

def run_stage(session, args):
    # Compile forge pack from session data
    pack = {
        'session_id': session.data.get('id'),
        'task': session.data.get('task'),
        'steps': session.data.get('steps', [])
    }
    os.makedirs('.arifos_clip/forge', exist_ok=True)
    forge_path = f".arifos_clip/forge/forge.json"
    with open(forge_path, 'w') as f:
        json.dump(pack, f, indent=2)
    session.data['status'] = 'FORGED'
    if args.json:
        print(json.dumps(pack, indent=2))
    else:
        print(f"Forge pack created: {forge_path}")
    return 20
