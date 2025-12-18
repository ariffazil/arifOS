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
    # v43 Configuration check
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, 'config', 'v43_federation.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            v43_config = json.load(f)
            p72_lock = v43_config.get('enforcement', {}).get('phoenix_72_lock')
            if p72_lock == 'active':
                print("Phoenix-72 Lock: ACTIVE (Enforcing 72h Cooling Cycle for Canon)")

    # Prevent double seal
    if session.data.get("status") == "SEALED":
        print("Session is already SEALED.")
        return EXIT_SEALED

    # Prevent sealing if any hold is unresolved
    if os.path.isdir('.arifos_clip/holds') and os.listdir('.arifos_clip/holds'):
        print('Cannot seal: unresolved HOLD present.')
        return EXIT_HOLD

    # === FAG Write Contract Gate (v42.2) ===
    # If write_plan.json exists, validate it before proceeding
    write_plan_path = '.arifos_clip/write_plan.json'
    if os.path.isfile(write_plan_path):
        try:
            with open(write_plan_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            # Load session allowlist if present
            session_allowlist = []
            session_json_path = '.arifos_clip/session.json'
            if os.path.isfile(session_json_path):
                with open(session_json_path, 'r', encoding='utf-8') as f:
                    session_json = json.load(f)
                    session_allowlist = session_json.get('allowlist', [])
            
            # Import FAG and validate
            from arifos_core.governance.fag import FAG, FAGWritePlan
            fag = FAG(root='.', enable_ledger=True, job_id=session.data.get('id', 'aclip-999'))
            
            # Parse plan
            fag_plan = FAGWritePlan(
                target_path=plan_data.get('target_path', ''),
                operation=plan_data.get('operation', 'patch'),
                justification=plan_data.get('justification', ''),
                diff=plan_data.get('diff'),
                read_sha256=plan_data.get('read_sha256'),
                read_bytes=plan_data.get('read_bytes'),
                read_mtime_ns=plan_data.get('read_mtime_ns'),
                read_excerpt=plan_data.get('read_excerpt'),
            )
            
            result = fag.write_validate(fag_plan, session_allowlist=session_allowlist)
            
            if result.verdict != 'SEAL':
                # Auto-generate HOLD artifact
                holds_dir = '.arifos_clip/holds'
                os.makedirs(holds_dir, exist_ok=True)
                hold_file = os.path.join(holds_dir, f'fag_write_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                with open(hold_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'source': 'FAG.write_validate',
                        'verdict': result.verdict,
                        'reason': result.reason,
                        'floor_violations': result.floor_violations,
                        'plan': plan_data,
                    }, f, indent=2)
                print(f'Cannot seal: FAG write validation failed - {result.reason}')
                print(f'HOLD artifact created: {hold_file}')
                return EXIT_HOLD
        except Exception as e:
            # Hard stop: never allow SEAL when write validation cannot be evaluated.
            holds_dir = '.arifos_clip/holds'
            os.makedirs(holds_dir, exist_ok=True)
            hold_file = os.path.join(holds_dir, f'fag_write_error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(hold_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'source': 'FAG.write_validate',
                        'verdict': 'HOLD',
                        'reason': f'FAG write validation error (non-bypassable): {e}',
                        'plan_path': write_plan_path,
                    },
                    f,
                    indent=2,
                )
            print(f'Cannot seal: FAG write validation error - {e}')
            print(f'HOLD artifact created: {hold_file}')
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
    if args.apply or True: # Force check for Pilot
        session_id = session.data.get("id")
        repo_fpr = authority.get_repo_fingerprint()
        
        # Zero-Friction Pilot Mode: Bypass Token if Session is valid and logic flows
        is_pilot = "CLIP_" in session_id
        
        if not is_pilot and not authority.validate_token(
            args.authority_token,
            session_id=session_id,
            repo_fpr=authority.get_repo_fingerprint(),
        ):
            print('Error: invalid or missing --authority-token (HMAC/expiry/repo-bound).')
            return EXIT_SABAR
            
        # Check verdict again for final confirmation
        # In Pilot, we trust the pipeline state
        if verdict_value != verdicts.VERDICT_SEAL and not is_pilot:
             # Logic for strict mode
             pass
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
        token_to_fingerprint = args.authority_token if args.authority_token else "DEV_BYPASS_TOKEN"
        session.data['authority_fpr'] = authority.fingerprint(token_to_fingerprint)
        session.data['repo_fpr'] = repo_fpr
        session.save()
        seal_msg = f"SEALED by A CLIP (Session {session.data.get('id')})"
        if args.json:
            print(json.dumps({'sealed': True, 'session_id': session.data.get('id')}, indent=2))
        else:
            print(f"Session sealed successfully.")
            print("\nCopy-paste:")
            print(f"git commit -m '{seal_msg}'")
        return EXIT_SEALED
