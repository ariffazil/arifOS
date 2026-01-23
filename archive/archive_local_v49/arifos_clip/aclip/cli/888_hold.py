"""CLI stage 888 - hold."""
from datetime import datetime
import json
import os

def run_stage(session, args):
    reason = args.reason or 'Manual hold invoked.'
    # Mark session status as HOLD
    session.data['status'] = 'HOLD'
    # Append hold step to session
    session.data.setdefault('steps', []).append({
        'stage': 888,
        'name': 'hold',
        'input': None,
        'output': f"HOLD: {reason}",
        'exit_code': 88,
        'timestamp': datetime.now().isoformat()
    })
    # Write hold bundle
    os.makedirs('.arifos_clip/holds', exist_ok=True)
    hold_json_path = f".arifos_clip/holds/hold.json"
    hold_md_path = f".arifos_clip/holds/hold.md"
    hold_data = {
        'session_id': session.data.get('id'),
        'reason': reason,
        'timestamp': datetime.now().isoformat(),
        'resolved': False
    }
    with open(hold_json_path, 'w') as f:
        json.dump(hold_data, f, indent=2)
    with open(hold_md_path, 'w') as f:
        f.write(f"""# A CLIP HOLD\n\nSession: {session.data.get('id')}\nReason: {reason}\n\nThis hold requires resolution by a human or authority before continuing.\n""")
    if args.json:
        print(json.dumps(hold_data, indent=2))
    else:
        print(f"HOLD applied. Reason: {reason}")
    return 88
