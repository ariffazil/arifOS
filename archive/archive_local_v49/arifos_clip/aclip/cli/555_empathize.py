"""CLI stage 555 - empathize."""
from datetime import datetime
import json

def run_stage(session, args):
    # Perform empathize stage logic (stub)
    prev_step = session.data['steps'][-1] if session.data.get('steps') else None
    result = "Stakeholder perspectives considered."
    # Append this stage result to session
    session.data['steps'].append({
        'stage': 555,
        'name': 'empathize',
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
        print("Stage 555 (EMPATHIZE) Complete.")
        
        # Mock Ethics Logic (v43 F5 Peace Squared)
        context = ' '.join(args.input) if hasattr(args, 'input') else ""
        hostility_detected = "hate" in context.lower() or "stupid" in context.lower()
        peace_score = 0.40 if hostility_detected else 0.95
        
        print(f"Peace² Metric (F5): {peace_score:.2f} (Threshold: 1.00 Damping)")
        if peace_score < 0.5:
            print("WARNING: High Entropic Friction Detected.")
            
        print("\nCopy-paste:")
        print(f"/666 {session.data['id']}")
    return 0
