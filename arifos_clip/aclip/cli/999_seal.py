"""CLI stage 999 - seal."""
from datetime import datetime
import json
import os
import sys
from arifos_clip.aclip.bridge import arifos_client
from arifos_clip.aclip.bridge import authority
from arifos_clip.aclip.bridge import verdicts

def run_stage(session, args):
    # Prevent sealing if any hold is unresolved
    if os.path.isdir('.arifos_clip/holds') and os.listdir('.arifos_clip/holds'):
        print('Cannot seal: unresolved HOLD present.')
        return 88
    # If not applying, just perform a dry-run check
    verdict_value, verdict_reason = arifos_client.request_verdict(session)
    if not args.apply:
        if verdict_value == verdicts.VERDICT_SEAL:
            print('Ready to seal. Use --apply with authority token to finalize.')
            return 30
        else:
            reason = verdict_reason or f'verdict={verdict_value}'
            print(f"Seal check failed: {reason}")
            if verdict_value == verdicts.VERDICT_HOLD or verdict_value is None:
                return 88
            else:
                return 30
    # If applying, require authority token
    if args.apply:
        if not authority.validate_token(args.authority_token):
            print('Error: --authority-token is required to apply seal.')
            return 30
        # Check verdict again for final confirmation
        if verdict_value != verdicts.VERDICT_SEAL:
            reason = verdict_reason or f'verdict={verdict_value}'
            print(f"Cannot seal: {reason}")
            if verdict_value == verdicts.VERDICT_HOLD or verdict_value is None:
                return 88
            else:
                return 30
        # All conditions satisfied: seal the session
        session.data['status'] = 'SEALED'
        session.data['sealed_at'] = datetime.now().isoformat()
        session.data['authority'] = args.authority_token
        session.save()
        seal_msg = f"SEALED by A CLIP (Session {session.data.get('id')})"
        if args.json:
            print(json.dumps({'sealed': True, 'session_id': session.data.get('id')}, indent=2))
        else:
            print(f"Session sealed successfully. Use commit message: '{seal_msg}'")
        return 100
