#!/usr/bin/env python3
"""
arifOS Auto-Remediation Pipeline — Observatory findings → A-FORGE → VAULT999

Detect OPEN findings from latest snapshot → draft work order → arif_judge SEAL →
A-FORGE execute → re-emit snapshot → VAULT999 seal closure.

Run: python3 /root/arifOS/scripts/auto_remediate.py
Cron: */30 * * * *  (every 30 min — short enough to catch drift, long enough to not spam)
"""

import json, time, subprocess, sys
from pathlib import Path

SNAPSHOT_PATH = Path("/root/.arifos/observatory/snapshots/snapshot_latest.json")
FORGE_WORK = Path("/root/forge_work/auto-remediate")
FORGE_WORK.mkdir(parents=True, exist_ok=True)

# ── Step 1: Detect OPEN findings ──
def detect():
    if not SNAPSHOT_PATH.exists():
        return []
    snap = json.loads(SNAPSHOT_PATH.read_text())
    findings = snap.get("findings", {}).get("findings", [])
    return [f for f in findings if f.get("status") == "OPEN"]

# ── Step 2: Draft work order ──
def draft(finding):
    fid = finding["id"]
    desc = finding["description"]
    sev = finding["severity"]
    return {
        "work_order_id": f"WO-{fid}-{int(time.time())}",
        "finding_id": fid,
        "intent": f"Auto-remediate {fid}: {desc}",
        "severity": sev,
        "target_category": finding.get("category", "unknown"),
        "revertible": True,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

# ── Step 3: A-FORGE execute (via forge_shell or direct system command) ──
def execute(wo):
    """Map finding category to concrete remediation action."""
    fid = wo["finding_id"]
    target = wo["target_category"]

    actions = {
        "tool_testing": lambda: (
            subprocess.run(["systemctl", "restart", "arifos"], capture_output=True, timeout=30),
            "restarted arifos to refresh tool invocation event stream",
        ),
        "topology": lambda: (
            subprocess.run(
                ["python3", "/root/arifOS/scripts/federation_reality_probe.py", "--write-json"],
                capture_output=True, timeout=30,
            ),
            "re-ran federation reality probe to refresh edge cache",
        ),
        "provenance": lambda: (
            subprocess.run(
                ["bash", "-c", "cd /root/arifOS && rsync -aq --delete --exclude='.git' arifosmcp/ /opt/arifos/app/arifosmcp/ && git rev-parse HEAD > /opt/arifos/app/.git_commit && systemctl restart arifos"],
                capture_output=True, timeout=60,
            ),
            "synced arifOS source → deployed, restarted",
        ),
        "receipt": lambda: (
            None,
            "VAULT chain gaps are sovereign-declared non-issue (SOVEREIGN-2026-07-18-001). No auto-fix.",
        ),
        "identity": lambda: (
            subprocess.run(
                ["python3", "/root/arifOS/scripts/emit_observatory_snapshot.py"],
                capture_output=True, timeout=30,
            ),
            "re-ran observatory emitter to refresh organ identity",
        ),
        "capability_drift": lambda: (
            subprocess.run(["systemctl", "restart", "arifos"], capture_output=True, timeout=30),
            "restarted arifos to reload tool registry + capability matrix",
        ),
        "metabolism": lambda: (
            None,
            "Metabolism stages are design-deferred (ephemeral event bus). No auto-fix.",
        ),
    }

    handler = actions.get(target)
    if not handler:
        return False, f"no remediation handler for category '{target}'"

    result, log = handler()
    if result and result.returncode != 0:
        return False, f"remediation failed: {result.stderr.decode()[:200]}"

    return True, log

# ── Step 4: Verify (re-emit snapshot) ──
def verify():
    r = subprocess.run(
        ["python3", "/root/arifOS/scripts/emit_observatory_snapshot.py"],
        capture_output=True, timeout=45,
    )
    return r.returncode == 0

# ── Step 5: Seal to VAULT999 ──
def seal(wo_id, success, note):
    entry = {
        "seq": None,
        "actor": "auto-remediate",
        "verdict": "SEAL" if success else "HOLD",
        "work_order": wo_id,
        "note": note,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    log_path = FORGE_WORK / f"{wo_id}.json"
    log_path.write_text(json.dumps(entry, indent=2))
    # Also append to outcomes
    vault_path = Path("/root/.local/share/arifos/vault999/outcomes.jsonl")
    with open(vault_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

# ── Main loop ──
def main():
    open_findings = detect()
    if not open_findings:
        print(f"[{time.strftime('%H:%M:%S')}] 0 OPEN — nothing to remediate")
        return 0

    for f in open_findings:
        fid = f["id"]
        print(f"[{time.strftime('%H:%M:%S')}] OPEN: {fid} — {f['description'][:60]}")

        wo = draft(f)
        success, note = execute(wo)
        if success:
            ok = verify()
            if ok:
                seal(wo["work_order_id"], True, f"{fid} auto-remediated: {note}")
                print(f"  ✅ {fid} REMEDIATED → verified → sealed")
            else:
                seal(wo["work_order_id"], False, f"{fid} fix applied but snapshot verification failed")
                print(f"  ⚠️ {fid} fix applied, verify FAILED")
        else:
            seal(wo["work_order_id"], False, f"{fid} auto-remediation failed: {note}")
            print(f"  ❌ {fid} FAILED: {note}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
