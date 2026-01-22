"""CLI stage 000 - void."""
from datetime import datetime
import json
import os

def run_stage(session, args):
    # v43 Configuration & Amanah Lock Check
    # Resolves to arifos_clip/config/v43_federation.json relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, 'config', 'v43_federation.json')
    
    # v43 Global Machine Constitution Check (Sovereign Layer)
    # Checks C:\Users\User\.antigravity\ARIFOS_GLOBAL_CONFIG.json
    global_config_path = os.path.expanduser("~/.antigravity/ARIFOS_GLOBAL_CONFIG.json")
    if os.path.exists(global_config_path):
        try:
            with open(global_config_path, 'r', encoding='utf-8') as f:
                g_config = json.load(f)
                print(f"Sovereign Node Identity: {g_config.get('MACHINE_IDENTITY')}")
                # Enforce Global F1
                if g_config.get('FLOORS', {}).get('F1_INTEGRITY') == 'STRICT':
                    # We will enforce this via the repo check later, but logging it here mandates it
                    pass 
        except Exception as e:
            print(f"WARNING: Global Governance File Corrupt: {e}")
    else:
        # Optional: Warn if this is a governed machine but file is missing
        pass

    # v43 Configuration & Amanah Lock Check
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # F1 Amanah Check
            f1_score = config.get('governance', {}).get('floors', {}).get('f1_amanah', 0.0)
            if f1_score < 0.95:
                print(f"SABAR: Amanah Integrity Violation (F1={f1_score} < 0.95)")
                return 30
            # Store config digest in session for audit
            session.data['v43_config_digest'] = {
                'epoch': config.get('epoch'),
                'mode': config.get('mode'),
                'f1_amanah': f1_score
            }
    except Exception as e:
        print(f"SABAR: Configuration Corrupt: {e}")
        return 30

    # Starting a new session (void stage)
    if getattr(session, 'loaded_from_file', False) and session.data.get('status') not in ['SEALED']:
        print('Error: Unsealed session already exists. Cannot start a new session.')
        return 30
    task_desc = ' '.join(args.task)
    # Initialize new session data
    session_id = session.data.get('id') or f"CLIP_{datetime.now().strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}" # Simplified ID
    session.data = {
        'id': session_id,
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
        print(f"Session {session_id} initialized.")
        print(f"Task: {task_desc}")
        print("\nCopy-paste:")
        print(f"/111 {session_id}")
    return 40
