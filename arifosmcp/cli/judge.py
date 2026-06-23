"""arifos judge — 888 constitutional deliberation via AAA a2a-server."""

from __future__ import annotations

import os

from arifosmcp.cli.common import CliError, http_post_json


def run_judge(args: list[str]) -> int:
    """Entry point for `arifos judge`."""
    import argparse

    parser = argparse.ArgumentParser(prog="arifos judge", description="888 constitutional deliberation.")
    parser.add_argument("--goal", required=True, help="Candidate action to judge.")
    parser.add_argument("--class", dest="action_class", choices=["observer", "interpreter", "maker", "messenger", "mutator", "destroyer", "sovereign"], help="Action class.")
    parser.add_argument("--blast-radius", choices=["low", "medium", "high"], help="Blast radius.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--url", default=os.getenv("AAA_JUDGE_URL", "http://127.0.0.1:3001/judge"), help="AAA deliberation endpoint.")
    parsed = parser.parse_args(args)

    candidate = {
        "text": parsed.goal,
        "action_class": parsed.action_class or "maker",
        "blast_radius": parsed.blast_radius or "medium",
        "source": "arifos-cli",
    }

    try:
        result = http_post_json(parsed.url, candidate)
    except CliError as exc:
        if parsed.json:
            import json
            print(json.dumps({"verdict": "HOLD", "error": exc.message}))
        else:
            print("verdict: HOLD")
            print(f"rationale: {exc.message}")
        return 1

    if parsed.json:
        import json
        print(json.dumps(result, indent=2, default=str))
    else:
        verdict = result.get("verdict", "HOLD")
        print(f"verdict: {verdict}")
        if "rationale" in result:
            print(f"rationale: {result['rationale']}")
        if "notes" in result:
            print(f"notes: {result['notes']}")
        if "G" in result:
            print(f"confidence (G): {result['G']}")
        if "weakest_gate" in result:
            print(f"weakest_gate: {result['weakest_gate']}")

    return 0 if result.get("verdict") == "SEAL" else 1
