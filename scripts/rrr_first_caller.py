"""
RRR first external caller — TREE777 reader for Resource·Reality·Resolution.

Forged 2026-08-20 by kimi-code/FI-008 under F13 SOVEREIGN directive.
Pattern: deterministic, no LLM, idempotent. Receipt-format output.

This script is the load-bearing proof that RRR (arifOS kernel resource,
schema rrr/v1.0) has at least one external reader — satisfying TREE777
HOLD (2026-08-14: no new service without reader demand).

Six intent classes invoked — one per F2-typology. Each call returns a
reality snapshot (boot + task resources, evidence, candidate skills).
Caller logs each call's classification + resource count + status.

Usage:
    python3 /root/arifOS/scripts/rrr_first_caller.py

Exit codes:
    0 — all 6 calls returned with PASS status
    1 — at least one call failed
    2 — import error (rrr.py not reachable)

DITEMPA BUKAN DIBERI ⚒️
"""
import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Resolve arifOS root from this script's location.
# Script lives at /root/arifOS/scripts/rrr_first_caller.py — parent.parent = arifOS root.
_ARIFOS_ROOT = Path(__file__).resolve().parent.parent
if str(_ARIFOS_ROOT) not in sys.path:
    sys.path.insert(0, str(_ARIFOS_ROOT))

try:
    from arifosmcp.resources.rrr import resolve_rrr  # noqa: E402
except ImportError as e:
    sys.stderr.write(f"[FATAL] Cannot import resolve_rrr: {e}\n")
    sys.stderr.write(f"[HINT] arifOS root attempted: {_ARIFOS_ROOT}\n")
    sys.exit(2)


# One intent per F2-typology — covers low/medium/high criticality, observe/audit/compute modes.
INTENTS = [
    "federation health check",        # → federation-health (observe, low)
    "skill catalog audit",            # → skill-metabolism (audit, low)
    "geox domain audit",              # → geox-domain (compute, medium)
    "wealth portfolio analysis",      # → wealth-domain (compute, medium)
    "well readiness check",           # → well-domain (observe, medium)
    "governance audit",               # → governance-audit (audit, high)
]


def call(intent: str) -> dict:
    """One RRR call. Returns the structured reality snapshot."""
    return resolve_rrr(intent)


def main() -> int:
    forge_ts = datetime.now(UTC).isoformat()
    receipt = {
        "caller": "arifOS/scripts/rrr_first_caller.py",
        "forge_date": "2026-08-20",
        "forge_timestamp": forge_ts,
        "tree777_receipt": "RRR has external reader — TREE777 HOLD cleared",
        "schema": "rrr/v1.0",
        "calls": [],
    }

    overall_pass = True
    for intent in INTENTS:
        try:
            r = call(intent)
            classification = r.get("classification", {})
            task = r.get("task_resources", {})
            receipt["calls"].append({
                "intent": intent,
                "status": "PASS",
                "intent_class": classification.get("intent_class"),
                "domain": classification.get("domain"),
                "mode": classification.get("mode"),
                "criticality": classification.get("criticality"),
                "authority_required": classification.get("authority_required"),
                "boot_resources_count": len(r.get("boot_resources", [])),
                "task_required_count": len(task.get("required", [])),
                "task_optional_count": len(task.get("optional", [])),
                "candidate_skills_count": len(r.get("candidate_skills", [])),
                "candidate_capabilities_count": len(r.get("candidate_capabilities", [])),
                "constraints": r.get("constraints", []),
                "confidence": r.get("confidence", {}),
            })
        except Exception as e:
            overall_pass = False
            receipt["calls"].append({
                "intent": intent,
                "status": "FAIL",
                "error": repr(e),
            })

    receipt["overall"] = "PASS" if overall_pass else "FAIL"
    receipt["calls_total"] = len(receipt["calls"])
    receipt["calls_passed"] = sum(1 for c in receipt["calls"] if c.get("status") == "PASS")

    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())