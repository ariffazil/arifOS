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
        # v43 Amanah Hash (Synthesized Proof)
        import hashlib
        amanah_hash = hashlib.sha256(json.dumps(pack).encode()).hexdigest()[:16]
        
        print(f"Forge Pack Created: {forge_path}")
        print(f"Amanah Hash: {amanah_hash}")
        print("Verdict: FORGED (Immutable)")
        
        print("\nCopy-paste:")
        print(f"/999 {session.data['id']}")
    return 20
