"""arifos seal — Write non-binding audit receipt to VAULT999."""

from __future__ import annotations

import hashlib
import os
import uuid

from arifosmcp.cli.common import CliError, get_writer_token, http_post_json


def run_seal(args: list[str]) -> int:
    """Entry point for `arifos seal`."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="arifos seal", description="Write audit receipt to VAULT999."
    )
    parser.add_argument("--message", "-m", required=True, help="Receipt message / payload summary.")
    parser.add_argument("--action", "-a", default="arifos-cli receipt", help="Action description.")
    parser.add_argument("--tags", default="", help="Comma-separated tags.")
    parser.add_argument(
        "--claim-state",
        default="OBSERVED",
        choices=["OBSERVED", "DRAFT", "HYPOTHESIS", "PENDING_RATIFICATION"],
        help="Epistemic state.",
    )
    parser.add_argument(
        "--session-id", default=os.getenv("ARIFOS_SESSION_ID", ""), help="Session ID."
    )
    parser.add_argument(
        "--agent-id", default=os.getenv("ARIFOS_AGENT_ID", "arifos-cli"), help="Agent ID."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument(
        "--url",
        default=os.getenv("VAULT_WRITER_URL", "http://127.0.0.1:5001") + "/audit-receipt",
        help="VAULT999 writer endpoint.",
    )
    parsed = parser.parse_args(args)

    token = get_writer_token()
    if not token:
        msg = "VAULT_WRITER_TOKEN not set and /run/secrets/vault_writer_token not found."
        if parsed.json:
            import json

            print(json.dumps({"success": False, "error": msg}))
        else:
            print(f"error: {msg}")
        return 1

    payload = {
        "message": parsed.message,
        "action": parsed.action,
        "source": "arifos-cli",
    }
    payload_text = str(payload)
    payload_hash = hashlib.sha256(payload_text.encode()).hexdigest()

    receipt = {
        "agent_id": parsed.agent_id,
        "action": parsed.action,
        "payload": payload,
        "payload_hash": payload_hash,
        "payload_summary": parsed.message[:240],
        "session_id": parsed.session_id or str(uuid.uuid4())[:8],
        "trace_id": str(uuid.uuid4()),
        "claim_state": parsed.claim_state,
        "binding": False,
        "irreversible": False,
        "human_ratifier": "arif",
        "tags": [t.strip() for t in parsed.tags.split(",") if t.strip()],
    }

    try:
        result = http_post_json(parsed.url, receipt, headers={"X-Writer-Token": token})
    except CliError as exc:
        if parsed.json:
            import json

            print(json.dumps({"success": False, "error": exc.message}))
        else:
            print(f"error: {exc.message}")
        return 1

    if parsed.json:
        import json

        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"success: {result.get('success', False)}")
        if "id" in result:
            print(f"id: {result['id']}")
        if "hash" in result:
            print(f"hash: {result['hash']}")
        if "timestamp" in result:
            print(f"timestamp: {result['timestamp']}")

    return 0 if result.get("success") else 1
