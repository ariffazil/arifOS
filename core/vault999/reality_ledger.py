import json
import uuid
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path

# The canonical vault location
LEDGER_DIR = Path("/root/arifOS/VAULT999")
LEDGER_FILE = LEDGER_DIR / "REALITY_LEDGER.jsonl"


def append_to_ledger(entry_data: dict) -> str:
    """
    Appends a RealityLedgerEntry to the immutable ledger.
    """
    os.makedirs(LEDGER_DIR, exist_ok=True)

    entry_data.setdefault("entry_id", str(uuid.uuid4()))
    entry_data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    # Very basic validation to ensure it has the main keys required by schema
    required_keys = [
        "trace_id",
        "principal",
        "intent",
        "claims",
        "evidence",
        "prediction",
        "plan",
        "approval",
        "execution",
        "outcome",
        "delta",
        "seals",
    ]

    for key in required_keys:
        if key not in entry_data:
            entry_data[key] = {} if key not in ["claims", "evidence"] else []

    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry_data) + "\n")

    return entry_data["entry_id"]


def query_ledger(limit: int = 10, trace_id: str = None) -> list[dict]:
    """
    Queries the Reality Ledger.
    """
    if not LEDGER_FILE.exists():
        return []

    results = []
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            if trace_id and entry.get("trace_id") != trace_id:
                continue
            results.append(entry)

    return results[-limit:]


def replay_trace(trace_id: str):
    """
    Replays a specific trace_id to console.
    """
    entries = query_ledger(limit=1000, trace_id=trace_id)
    print(f"=== REALITY LEDGER REPLAY | trace_id: {trace_id} ===")
    if not entries:
        print("No entries found.")
        return

    for entry in entries:
        print(f"[{entry.get('timestamp')}] Entry ID: {entry.get('entry_id')}")
        intent = entry.get("intent", {})
        print(
            f"  ▶ INTENT:    {intent.get('description', 'N/A')} (Risk: {intent.get('risk_class', 'N/A')})"
        )
        plan = entry.get("plan", {})
        print(f"  ▶ PLAN:      {plan.get('selected_plan', 'N/A')}")
        approval = entry.get("approval", {})
        print(f"  ▶ APPROVAL:  {approval.get('judge_verdict', 'N/A')}")
        execution = entry.get("execution", {})
        print(
            f"  ▶ EXECUTION: {execution.get('adapter', 'N/A')} -> {execution.get('target', 'N/A')}"
        )
        outcome = entry.get("outcome", {})
        print(
            f"  ▶ OUTCOME:   {outcome.get('observed_result', 'N/A')} (Success: {outcome.get('success', False)})"
        )
        print("-" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reality Ledger Replay CLI")
    parser.add_argument("--trace-id", type=str, help="Trace ID to replay")
    parser.add_argument(
        "--limit", type=int, default=10, help="Number of recent entries to show if no trace_id"
    )

    args = parser.parse_args()

    if args.trace_id:
        replay_trace(args.trace_id)
    else:
        print(f"=== REALITY LEDGER LAST {args.limit} ENTRIES ===")
        entries = query_ledger(limit=args.limit)
        if not entries:
            print("Ledger is empty.")
        for e in entries:
            print(
                f"{e.get('timestamp')} | Trace: {e.get('trace_id')} | Intent: {e.get('intent', {}).get('description', 'N/A')}"
            )
