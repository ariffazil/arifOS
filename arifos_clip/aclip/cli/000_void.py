"""CLI stage 000 - void."""
from datetime import datetime
import json
import os

def run_stage(session, args):
    # Starting a new session (void stage)
    if getattr(session, 'loaded_from_file', False) and session.data.get('status') not in ['SEALED']:
        print('Error: Unsealed session already exists. Cannot start a new session.')
        return 30
    task_desc = ' '.join(args.task)
    # Initialize new session data
    session.data = {
        'id': session.data.get('id') or datetime.now().strftime('%Y%m%d%H%M%S'),
        'task': task_desc,
        'status': 'VOID',
        'steps': []
    }
    # Record initial step
    session.data['steps'].append({
        'stage': 0,
        'name': 'void',
        'input': task_desc,
        'output': None,
        'exit_code': 40,
        'timestamp': datetime.now().isoformat()
    })
    # Write session file immediately
    session.save()
    if args.json:
        print(json.dumps(session.data, indent=2))
    else:
        print(f"Session {session.data['id']} initialized. Task: {task_desc}")
    return 40
