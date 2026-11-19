#!/usr/bin/env python3
"""Independent locked-denominator acceptance runner; emits facts, never self-seals.

F4 fix 2026-11-19 (audit finding 4, F13 "jalan sisa tu - fix finding 1,2,4,6
within kitaran canon"): the epoch no longer marks its own output. Two disjoint
process phases:

  runner   (default)          runs the locked manifest gates ONCE and writes
                              proof/proof-epoch-draft.json (no seal field,
                              runner_role=A-AUDIT).
  verifier --verify <draft>   a SEPARATE process invocation re-reads the
                              manifest fresh, RE-RUNS every gate itself, and
                              only when its own recomputation agrees with the
                              draft writes proof/proof-epoch-result.json with
                              independently_sealed=true (verifier_role=
                              A-AUDIT-VERIFY). On any discrepancy it writes
                              independently_sealed=false plus a DISCREPANCY
                              block - the draft is never upgraded on trust.

Runner and verifier are disjoint executions; the builder may not
reclassify failures, and the verifier may not inherit them.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "proof" / "acceptance-manifest.json"
DRAFT = ROOT / "proof" / "proof-epoch-draft.json"
RESULT = ROOT / "proof" / "proof-epoch-result.json"


def run_gates() -> tuple[list[dict], str, int]:
    """Execute the locked manifest gates and return (results, manifest_sha, n)."""
    raw = MANIFEST.read_bytes()
    manifest = json.loads(raw)
    gates = manifest["mandatory_gates"]
    results = []
    for gate in gates:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", gate["test"]],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        results.append(
            {
                "id": gate["id"],
                "test": gate["test"],
                "passed": proc.returncode == 0,
                "exit_code": proc.returncode,
                "summary": (proc.stdout + proc.stderr)[-1200:],
            }
        )
    return results, "sha256:" + hashlib.sha256(raw).hexdigest(), len(gates)


def phase_runner() -> int:
    results, manifest_sha, n = run_gates()
    passed = sum(r["passed"] for r in results)
    draft = {
        "event_type": "proof_epoch.independent_acceptance.draft",
        "runner_role": "A-AUDIT",
        "builder_may_not_reclassify_failures": True,
        "manifest_sha256": manifest_sha,
        "denominator_locked": n,
        "mandatory_gates_passed": passed,
        "verdict": "PASS" if passed == n else "CONDITIONAL_PASS",
        "results": results,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    DRAFT.write_text(json.dumps(draft, indent=2) + "\n")
    print(
        json.dumps(
            {
                "phase": "runner",
                "draft_sha256": "sha256:"
                + hashlib.sha256(DRAFT.read_bytes()).hexdigest(),
                "manifest_sha256": manifest_sha,
                "denominator_locked": n,
                "mandatory_gates_passed": passed,
                "verdict": draft["verdict"],
                "next": f"{sys.executable} {Path(__file__)} --verify {DRAFT}",
            }
        )
    )
    return 0 if passed == n else 1


def phase_verify(draft_path: Path) -> int:
    draft = json.loads(draft_path.read_text())
    # The verifier recomputes EVERYTHING from the locked manifest - it does
    # not trust the runner's per-gate results.
    results, manifest_sha, n = run_gates()
    passed = sum(r["passed"] for r in results)
    draft_results = {r["id"]: r["passed"] for r in draft.get("results", [])}
    verifier_results = {r["id"]: r["passed"] for r in results}
    discrepancies = [
        gid for gid in verifier_results
        if draft_results.get(gid) != verifier_results[gid]
    ]
    manifest_agrees = draft.get("manifest_sha256") == manifest_sha
    denominator_agrees = draft.get("denominator_locked") == n
    counts_agree = draft.get("mandatory_gates_passed") == passed
    sealed = (
        manifest_agrees
        and denominator_agrees
        and counts_agree
        and not discrepancies
        and draft.get("runner_role") == "A-AUDIT"
    )
    receipt = {
        "event_type": "proof_epoch.independent_acceptance",
        "runner_role": "A-AUDIT",
        "verifier_role": "A-AUDIT-VERIFY",
        "builder_may_not_reclassify_failures": True,
        "verifier_recomputed_gates": True,
        "draft_sha256": "sha256:" + hashlib.sha256(draft_path.read_bytes()).hexdigest(),
        "manifest_sha256": manifest_sha,
        "denominator_locked": n,
        "mandatory_gates_passed": passed,
        "verdict": "PASS" if passed == n else "CONDITIONAL_PASS",
        "results": results,
        "discrepancies": discrepancies,
        "checks": {
            "manifest_agrees": manifest_agrees,
            "denominator_agrees": denominator_agrees,
            "counts_agree": counts_agree,
            "no_result_discrepancies": not discrepancies,
        },
        "generated_at": datetime.now(UTC).isoformat(),
        # The only field the verifier may set - and only on its own
        # recomputation agreeing with the draft in full.
        "independently_sealed": sealed,
        "seal_refusal_reason": None if sealed else "verifier-recomputation-disagreement",
    }
    RESULT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "phase": "verifier",
                "independently_sealed": sealed,
                "mandatory_gates_passed": passed,
                "denominator_locked": n,
                "verdict": receipt["verdict"],
                "discrepancies": discrepancies,
            }
        )
    )
    draft_path.unlink(missing_ok=True)
    return 0 if sealed and passed == n else 1


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--verify":
        draft = Path(args[1]) if len(args) > 1 else DRAFT
        return phase_verify(draft)
    return phase_runner()


if __name__ == "__main__":
    raise SystemExit(main())
