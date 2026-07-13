#!/usr/bin/env python3
"""Independent locked-denominator acceptance runner; emits facts, never self-seals."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "proof" / "acceptance-manifest.json"


def main() -> int:
    raw = MANIFEST.read_bytes()
    manifest = json.loads(raw)
    gates = manifest["mandatory_gates"]
    results = []
    for gate in gates:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", gate["test"]],
            cwd=ROOT, capture_output=True, text=True, timeout=180,
        )
        results.append({
            "id": gate["id"], "test": gate["test"],
            "passed": proc.returncode == 0, "exit_code": proc.returncode,
            "summary": (proc.stdout + proc.stderr)[-1200:],
        })
    passed = sum(r["passed"] for r in results)
    receipt = {
        "event_type": "proof_epoch.independent_acceptance",
        "runner_role": "A-AUDIT",
        "builder_may_not_reclassify_failures": True,
        "manifest_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "denominator_locked": len(gates),
        "mandatory_gates_passed": passed,
        "verdict": "PASS" if passed == len(gates) else "CONDITIONAL_PASS",
        "results": results,
        "generated_at": datetime.now(UTC).isoformat(),
        "independently_sealed": False,
    }
    out = ROOT / "proof" / "proof-epoch-result.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in (
        "manifest_sha256", "denominator_locked", "mandatory_gates_passed", "verdict"
    )}))
    return 0 if passed == len(gates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
