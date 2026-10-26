#!/usr/bin/env python3
"""f6_witness_review.py — the human-witness lane for F6 MARUAH meters.

WHY (F6 spec §5d + F6_MARUAH_CANON.md):
  The F6 producer requires witness == REVIEWED (a human reviewed the meter
  report within 7 days). Silence is never a pass: an empty or stale
  /var/lib/arifos/human_witness.jsonl keeps F6 honestly UNMEASURED. This CLI
  is the SANCTIONED PATH for that human act — it renders the current meter
  report for review and, ONLY on explicit human confirmation with the
  human's own statement, appends a witness row.

CONTRACT
  render (default)   : print the six meters + report sha256 + witness status.
                       Writes NOTHING. This is the machine-proposes half.
  --confirm          : append a witness row. REQUIRES --statement "<the
                       human's own words>" (non-empty). Refuses without it.
                       The statement is recorded verbatim — the tool never
                       composes, completes, or paraphrases it. A witness row
                       is a human act receipt; the machine only carries it.

  No pipeline, cron, or agent may invoke --confirm on a human's behalf:
  fabricating a witness row is exactly the ceremony-masquerading-as-gate
  failure class F6 exists to prevent.

TEST SEAM: ARIFOS_HUMAN_WITNESS overrides the ledger path (tests only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WITNESS_PATH = Path("/var/lib/arifos/human_witness.jsonl")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_report() -> dict:
    """Evaluate the six meters (read-only) and fingerprint the report."""
    from arifosmcp.runtime.f6.meters import evaluate_all

    report = evaluate_all()
    canonical = json.dumps(report, sort_keys=True, default=str)
    return {
        "report": report,
        "report_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def render() -> int:
    bundle = build_report()
    report = bundle["report"]
    print("F6 MARUAH — six system-behavior meters (machine proposes; human confirms)")
    print(f"report sha256: {bundle['report_sha256']}")
    print(f"generated_at : {report.get('generated_at')}")
    print(f"f6_overall   : {report.get('f6_overall')}  floor: {report.get('f6_floor_status')}")
    print(f"witness      : {report.get('witness_states')}")
    print("-" * 78)
    for m in report.get("meters", []):
        print(
            f"{m.get('meter_id'):<28} result={m.get('result'):<14} "
            f"measurement={m.get('measurement'):<11} witness={m.get('witness')}"
        )
        reason = str(m.get("result_reason") or "")
        if reason:
            print(f"    reason: {reason[:160]}")
    print("-" * 78)
    print("To witness: a HUMAN runs this tool, reads the report above, and then:")
    print("  f6_witness_review.py --confirm --statement '<your own words>'")
    return 0


def confirm(statement: str, actor: str) -> int:
    statement = (statement or "").strip()
    if not statement:
        print(
            "REFUSED: --confirm requires --statement with the human's own words. "
            "An empty or machine-composed statement is not a witness act.",
            file=sys.stderr,
        )
        return 2
    bundle = build_report()
    report = bundle["report"]
    row = {
        "at": _now_iso(),
        "event": "f6_meter_review",
        "actor_id": actor,
        "actor_class": "HUMAN",
        "report_sha256": bundle["report_sha256"],
        "meters": {
            str(m.get("meter_id")): {
                "result": m.get("result"),
                "measurement": m.get("measurement"),
            }
            for m in report.get("meters", [])
        },
        "f6_overall_at_review": report.get("f6_overall"),
        "statement": statement,
        "tool": "scripts/f6_witness_review.py",
    }
    witness_path = Path(__import__("os").environ.get("ARIFOS_HUMAN_WITNESS", str(WITNESS_PATH)))
    witness_path.parent.mkdir(parents=True, exist_ok=True)
    with witness_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"WITNESS_RECORDED {witness_path} at={row['at']} actor={actor}")
    print(f"report_sha256={row['report_sha256']}")
    print("The witness axis is now REVIEWED for 7 days (F6 spec §5d).")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--confirm", action="store_true", help="record a human witness act")
    ap.add_argument(
        "--statement", default="", help="the human's own words (required with --confirm)"
    )
    ap.add_argument("--actor", default="arif", help="human actor id (default: arif)")
    a = ap.parse_args(argv)
    if a.confirm:
        return confirm(a.statement, a.actor)
    return render()


if __name__ == "__main__":
    raise SystemExit(main())
