#!/usr/bin/env python3
"""
shadow_session_analyzer.py — Session Transcript Shadow Checker
═══════════════════════════════════════════════════════════════
Reads agent session transcripts and runs mechanical shadow checks.
Outputs results to cockpit/shadow-matrix/session-checks/.

Usage:
    # Analyze a specific session file
    python3 shadow_session_analyzer.py --session /path/to/session.jsonl
    
    # Analyze latest sessions from audit log
    python3 shadow_session_analyzer.py --latest 5
    
    # Analyze from stdin (pipe agent output)
    echo "agent output" | python3 shadow_session_analyzer.py --stdin

Created: 2026-09-19 by FI-008
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent for imports
_tools_dir = str(Path(__file__).resolve().parent)
_arifos_root = str(Path(_tools_dir).resolve().parent.parent.parent)
if _arifos_root not in sys.path:
    sys.path.insert(0, _arifos_root)
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

from shadow_mechanical_checks import check_all, report as check_report
from frame_behavioral_drift import compute_all as drift_compute, report as drift_report

AUDIT_LOG = Path("/root/.agent-workbench/mcp-audit.jsonl")
OUTPUT_DIR = Path("/root/AAA/cockpit/shadow-matrix/session-checks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def analyze_text(agent_output: str, user_input: str = "", agent_id: str = "unknown") -> dict:
    """Run all checks on a text block."""
    results = check_all(
        agent_output=agent_output,
        user_input=user_input,
        context_sufficient=True,
    )
    triggered = [r for r in results if r.triggered]
    return {
        "agent_id": agent_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks_run": len(results),
        "checks_triggered": len(triggered),
        "triggered": [
            {
                "check_id": r.check_id,
                "name": r.name,
                "severity": r.severity,
                "confidence": r.confidence,
                "evidence": r.evidence,
            }
            for r in triggered
        ],
        "all_results": [
            {
                "check_id": r.check_id,
                "name": r.name,
                "triggered": r.triggered,
                "severity": r.severity,
            }
            for r in results
        ],
    }


def analyze_session_file(path: str) -> dict:
    """Analyze a JSONL session file."""
    messages = []
    agent_id = Path(path).stem
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                messages.append(obj)
            except json.JSONDecodeError:
                continue
    
    # Extract agent outputs and user inputs
    agent_outputs = []
    user_inputs = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if isinstance(content, list):
            content = " ".join(str(c) for c in content)
        if role == "assistant":
            agent_outputs.append(str(content))
        elif role == "user":
            user_inputs.append(str(content))
    
    full_agent_output = "\n".join(agent_outputs)
    full_user_input = "\n".join(user_inputs)
    
    # Run checks
    check_result = analyze_text(full_agent_output, full_user_input, agent_id)
    
    # Run drift metrics
    tool_calls = []
    for msg in messages:
        if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
            for item in msg["content"]:
                if isinstance(item, dict) and item.get("type") == "function_call":
                    tool_calls.append(item.get("name", "unknown"))
    
    drift_metrics = drift_compute(
        tool_calls=tool_calls or None,
        agent_responses=agent_outputs or None,
        response_lengths=[len(o) for o in agent_outputs] if agent_outputs else None,
    )
    
    check_result["drift_metrics"] = [
        {
            "metric_id": m.metric_id,
            "name": m.name,
            "value": m.value,
            "status": m.status,
            "interpretation": m.interpretation,
        }
        for m in drift_metrics
    ]
    
    return check_result


def get_latest_sessions(n: int = 5) -> list[str]:
    """Get latest session paths from audit log."""
    if not AUDIT_LOG.exists():
        return []
    sessions = []
    with open(AUDIT_LOG) as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if "session_id" in obj:
                    sessions.append(obj)
            except json.JSONDecodeError:
                continue
    # Return last N unique session IDs
    seen = set()
    paths = []
    for s in reversed(sessions):
        sid = s.get("session_id", "")
        if sid not in seen:
            seen.add(sid)
            paths.append(sid)
        if len(paths) >= n:
            break
    return paths


def save_result(result: dict, session_id: str = "stdin") -> str:
    """Save analysis result to cockpit."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_id = session_id.replace("/", "_").replace(":", "_")[:50]
    out_path = OUTPUT_DIR / f"shadow-check-{safe_id}-{ts}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    return str(out_path)


def main():
    parser = argparse.ArgumentParser(description="Session transcript shadow checker")
    parser.add_argument("--session", help="Path to session JSONL file")
    parser.add_argument("--latest", type=int, help="Analyze N latest sessions")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--text", help="Direct text to analyze")
    parser.add_argument("--output", help="Output path (default: cockpit/session-checks/)")
    args = parser.parse_args()
    
    if args.stdin:
        text = sys.stdin.read()
        result = analyze_text(text, agent_id="stdin")
        out = save_result(result, "stdin")
        print(json.dumps(result, indent=2))
        print(f"\nSaved to: {out}")
        
    elif args.text:
        result = analyze_text(args.text, agent_id="direct")
        out = save_result(result, "direct")
        print(json.dumps(result, indent=2))
        print(f"\nSaved to: {out}")
        
    elif args.session:
        result = analyze_session_file(args.session)
        out = save_result(result, args.session)
        print(json.dumps(result, indent=2))
        print(f"\nSaved to: {out}")
        
    elif args.latest:
        sessions = get_latest_sessions(args.latest)
        print(f"Found {len(sessions)} recent sessions")
        for sid in sessions:
            print(f"  Session: {sid}")
        # Note: would need to find actual session files to analyze
        
    else:
        # Demo: analyze a sample
        sample = """Great question! Let me think about this carefully.
        It's worth noting that the Shadow concept has deep roots.
        Of course, we should consider multiple perspectives.
        Done. All tasks completed successfully."""
        result = analyze_text(sample, "fix the bug", "demo")
        print(check_report([
            type('R', (), {
                'check_id': r['check_id'], 'name': r['name'],
                'triggered': r.get('triggered', False) or r['check_id'] in [t['check_id'] for t in result['triggered']],
                'severity': r['severity'], 'confidence': r.get('confidence', 0),
                'evidence': r.get('evidence', '')
            })()
            for r in result['all_results']
        ]))
        print(f"\nTriggered: {result['checks_triggered']}/{result['checks_run']}")


if __name__ == "__main__":
    main()
