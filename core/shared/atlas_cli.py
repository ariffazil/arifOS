#!/usr/bin/env python3
"""atlas_cli.py — ATLAS333 Cognitive Wire Python Bridge (Approach A)

Called by membrane_middleware.js via child_process.execFile.
Takes JSON via stdin, runs Phi() classification via GPV, returns JSON on stdout.
Boot, run, die fast. F1 fail-safe: exits 0 on any error.

NOTE: Print statements from Phi() go to stderr. We suppress stdout during import
      to isolate clean JSON output.

Forged: 2026-08-05 by 333-AGI under Approach A SOT directive.
"""

import sys
import json
import os
import traceback

sys.path.insert(0, "/root/arifOS")

# Suppress ATLAS_AUDIT from Phi() — it writes to stdout on import
_real_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")

try:
    from core.shared.atlas import Phi
    from arifosmcp.core.enforcement.paradox_gate import evaluate_paradox_gate_gpv
except ImportError as e:
    sys.stdout = _real_stdout
    _real_stdout.write(
        json.dumps(
            {
                "status": "error",
                "message": f"ATLAS333 kernel import failed: {e}",
                "approach_a_unavailable": True,
            }
        )
    )
    sys.exit(0)

sys.stdout = _real_stdout


def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.stdout.write(json.dumps({"status": "error", "message": "No input provided"}))
            sys.exit(0)

        payload = json.loads(input_data)
        text = payload.get("text", "")
        session_id = payload.get("session_id", "membrane_unknown")
        organ = payload.get("organ", "UNKNOWN")

        # 1. Phi() — ATLAS333 cognitive classification
        gpv = Phi(text, session_id=session_id)

        # 2. Paradox gate evaluation
        gate_result = evaluate_paradox_gate_gpv(gpv, output_text=text)

        # 3. Structured output
        output = {
            "status": "success",
            "verdict": gate_result.gate_verdict,
            "organ": organ,
            "session_id": session_id,
            "lane": gpv.lane,
            "rho": gpv.rho,
            "tau": gpv.tau,
            "kappa": gpv.kappa,
            "paradox_count": gate_result.active_paradoxes,
            "paradox_score": round(gate_result.paradox_score, 3),
            "paradox_ids": list(gpv.paradox_axes) if gpv.paradox_axes else [],
            "flags": [
                {
                    "paradox_id": f.paradox_id,
                    "flag": f.flag,
                    "tension": f.tension,
                    "detail": f.detail,
                }
                for f in gate_result.flags
            ]
            if gate_result.flags
            else [],
        }
        sys.stdout.write(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        sys.stdout.write(
            json.dumps(
                {
                    "status": "error",
                    "message": str(e),
                    "trace": traceback.format_exc()[-300:],
                }
            )
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
