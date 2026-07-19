#!/usr/bin/env python3
"""
authorize_mutation_cli.py — Deterministic CLI bridge for A-FORGE mutation authorization.

Reads JSON from stdin, calls canonical core.shared.authorize_mutation.authorize_mutation(),
outputs AuthorizationResult as JSON to stdout.

Single source of truth. No TypeScript duplicate. Fail-closed.
Called by A-FORGE forgeShell.ts preExecutionGate().

Usage:
    echo '{"executable":"rm","arguments":["-rf","/data"]}' | python3 -m core.shared.authorize_mutation_cli

Input JSON:
    {
      "executable": "rm",
      "arguments": ["-rf", "/var/lib/postgresql"],
      "args_text": "",
      "actor_privilege": "root",
      "actor_id": "forge",
      "session_id": "session-123",
      "target_environment": "production",
      "supplied_controls": [],
      "judgment_reference": ""
    }

Output JSON:
    {
      "allowed": false,
      "verdict": "HOLD",
      "reasonCodes": ["DESTRUCTIVE_OPERATION", ...],
      "rejectionReason": "...",
      "authorizedExecution": null
    }

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import sys

# Ensure arifOS source is importable
sys.path.insert(0, "/root/arifOS")

from core.shared.authorize_mutation import authorize_mutation


def main() -> None:
    """Read JSON from stdin, classify, output JSON to stdout."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            result = {
                "allowed": False,
                "verdict": "HOLD_UNCLASSIFIED",
                "reasonCodes": ["EMPTY_INPUT"],
                "rejectionReason": "No input provided — fail-closed.",
                "authorizedExecution": None,
            }
            json.dump(result, sys.stdout)
            sys.exit(0)

        input_data = json.loads(raw)

        # Call the canonical boundary
        auth = authorize_mutation(
            executable=input_data.get("executable", ""),
            arguments=input_data.get("arguments"),
            args_text=input_data.get("args_text", ""),
            actor_privilege=input_data.get("actor_privilege", "unknown"),
            actor_id=input_data.get("actor_id", "unknown"),
            session_id=input_data.get("session_id", "unknown"),
            target_environment=input_data.get("target_environment", "unknown"),
            supplied_controls=input_data.get("supplied_controls"),
            judgment_reference=input_data.get("judgment_reference", ""),
        )

        # Serialize
        output = {
            "allowed": auth.allowed,
            "verdict": auth.verdict,
            "reasonCodes": auth.reason_codes,
            "requiredControls": auth.required_controls,
            "missingControls": auth.missing_controls,
            "rejectionReason": auth.rejection_reason,
            "authorizedExecution": (
                {
                    "profileHash": auth.authorized_execution.profile_hash,
                    "authorizationReceipt": auth.authorized_execution.authorization_receipt,
                    "normalizedCommand": auth.authorized_execution.normalized_command,
                    "issuedAt": auth.authorized_execution.issued_at,
                    "expiresAt": auth.authorized_execution.expires_at,
                    "actorId": auth.authorized_execution.actor_id,
                    "sessionId": auth.authorized_execution.session_id,
                    "targetEnvironment": auth.authorized_execution.target_environment,
                }
                if auth.authorized_execution
                else None
            ),
        }

        json.dump(output, sys.stdout)
        sys.exit(0)

    except json.JSONDecodeError as e:
        result = {
            "allowed": False,
            "verdict": "HOLD_UNCLASSIFIED",
            "reasonCodes": ["INVALID_JSON"],
            "rejectionReason": f"Invalid JSON input: {e}",
            "authorizedExecution": None,
        }
        json.dump(result, sys.stdout)
        sys.exit(1)
    except Exception as e:
        result = {
            "allowed": False,
            "verdict": "HOLD_UNCLASSIFIED",
            "reasonCodes": ["BRIDGE_EXCEPTION"],
            "rejectionReason": f"Bridge exception: {e}",
            "authorizedExecution": None,
        }
        json.dump(result, sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
