"""CLI stage 999 - seal."""
from datetime import datetime
import json
import os
import sys
from arifos_clip.aclip.bridge import arifos_client
from arifos_clip.aclip.bridge import authority
from arifos_clip.aclip.bridge import verdicts

# Exit codes (canonical)
EXIT_PASS = 0
EXIT_PARTIAL = 20
EXIT_SABAR = 30
EXIT_VOID = 40
EXIT_HOLD = 88
EXIT_SEALED = 100


def run_stage(session, args):
    # Prevent double seal
    if session.data.get("status") == "SEALED":
        print("Session is already SEALED.")
        return EXIT_SEALED

    # Prevent sealing if any hold is unresolved
    if os.path.isdir('.arifos_clip/holds') and os.listdir('.arifos_clip/holds'):
        print('Cannot seal: unresolved HOLD present.')
        return EXIT_HOLD

    verdict_response = arifos_client.request_verdict(session)
    verdict_value = verdict_response.get("verdict")
    verdict_reason = verdict_response.get("reason")
    if verdict_value is None:
        verdict_value = verdicts.VERDICT_HOLD  # treat missing as HOLD

    # If not applying, just perform a dry-run check
    if not args.apply:
        if verdict_value == verdicts.VERDICT_SEAL:
            print('Ready to seal. Use --apply with authority token to finalize.')
            return EXIT_SABAR
        else:
            reason = verdict_reason or f'verdict={verdict_value}'
            print(f"Seal check failed: {reason}")
            if verdict_value == verdicts.VERDICT_HOLD:
                return EXIT_HOLD
            return EXIT_SABAR
    # If applying, require authority token
    if args.apply:
        session_id = session.data.get("id")
        repo_fpr = authority.get_repo_fingerprint()
        if not authority.validate_token(
            args.authority_token,
            session_id=session_id,
            repo_fpr=repo_fpr,
        ):
            print('Error: invalid or missing --authority-token (HMAC/expiry/repo-bound).')
            return EXIT_SABAR
        # Check verdict again for final confirmation
        if verdict_value != verdicts.VERDICT_SEAL:
            reason = verdict_reason or f'verdict={verdict_value}'
            print(f"Cannot seal: {reason}")
            if verdict_value == verdicts.VERDICT_HOLD:
                return EXIT_HOLD
            return EXIT_SABAR
        # All conditions satisfied: seal the session
        session.data['status'] = 'SEALED'
        session.data['sealed_at'] = datetime.now().isoformat()
        session.data['authority_fpr'] = authority.fingerprint(args.authority_token)
        session.data['repo_fpr'] = repo_fpr
        session.save()
        seal_msg = f"SEALED by A CLIP (Session {session.data.get('id')})"
        if args.json:
            print(json.dumps({'sealed': True, 'session_id': session.data.get('id')}, indent=2))
        else:
            print(f"Session sealed successfully. Use commit message: '{seal_msg}'")
        return EXIT_SEALED
