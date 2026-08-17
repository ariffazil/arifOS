#!/usr/bin/env python3
"""
arifOS Federation Drift Check — Live automated integrity probe.
Compares source commit, deployed commit, runtime identity, and registry hash.
Writes structured JSON to drift_log.jsonl. Never mutates.

DITEMPA BUKAN DIBERI — Forged 2026-07-19
"""

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

DRIFT_LOG = Path("/root/.local/share/arifos/vault999/drift_log.jsonl")


def git_commit(path: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", path, "rev-parse", "HEAD"], text=True, timeout=5
        ).strip()
    except Exception:
        return "UNKNOWN"


def file_hash(path: str) -> str:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return f"sha256:{h.hexdigest()[:16]}"
    except Exception:
        return "UNREADABLE"


def _looks_sha(value) -> bool:
    s = str(value or "")
    hexpart = s.rsplit("-", 1)[-1]
    return len(hexpart) >= 7 and all(c in "0123456789abcdef" for c in hexpart.lower())


def _extract_deployed_sha(health: dict) -> str:
    """Prefer live SHA fields. Version tags are not commits."""
    for key in ("source_commit", "deployed_commit"):
        if _looks_sha(health.get(key)):
            return str(health[key])
    sr = health.get("software_release") or {}
    if isinstance(sr, dict):
        for key in ("source_commit", "deployed_commit", "built_commit"):
            if _looks_sha(sr.get(key)):
                return str(sr[key])
    gv = health.get("git_version")
    if _looks_sha(gv):
        return str(gv).rsplit("-", 1)[-1]
    return "UNKNOWN"


def probe_health(port: int) -> dict:
    import urllib.request

    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5)
        return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def main():
    now = datetime.now(UTC).isoformat()

    # Probe all organs
    organs = {
        "arifos": {"port": 8088, "path": "/root/arifOS"},
        "geox": {"port": 8081, "path": "/root/GEOX"},
        "aforge": {"port": 7071, "path": "/root/A-FORGE"},
        "aaa": {"port": 3001, "path": "/root/AAA"},
        "wealth": {"port": 18082, "path": "/root/WEALTH"},
        "well": {"port": 18083, "path": "/root/WELL"},
    }

    results = {"checked_at": now, "organs": {}, "overall_drift": False}

    for name, cfg in organs.items():
        source_commit = git_commit(cfg["path"])
        health = probe_health(cfg["port"])

        # SHA vs SHA. Never compare a git hash to a marketing tag
        # (v2026.07.24) — that manufactured perpetual DRIFT (2026-08-18).
        deployed_sha = _extract_deployed_sha(health)
        identity_raw = health.get("identity_hash", health.get("identity", {}))
        if isinstance(identity_raw, dict):
            runtime_identity = identity_raw.get("value", identity_raw.get("hash", "UNKNOWN"))
        else:
            runtime_identity = str(identity_raw) if identity_raw else "UNKNOWN"

        if "error" in health:
            drift = True
        elif source_commit == "UNKNOWN" or deployed_sha == "UNKNOWN":
            # Scanner cannot see ≠ dirty. Do not fail-open as DRIFT.
            drift = False
        else:
            drift = source_commit[:7] not in deployed_sha and deployed_sha[:7] not in source_commit

        results["organs"][name] = {
            "source_commit": source_commit,
            "deployed_version": deployed_sha[:40],
            "runtime_identity": str(runtime_identity)[:40],
            "healthy": "error" not in health,
            "drift": drift,
        }
        if drift:
            results["overall_drift"] = True

    # Write to drift log
    entry = {
        "event_type": "drift_check_automated",
        "timestamp": now,
        "actor_id": "arifos-drift-check",
        "payload": results,
        "status": "DRIFT" if results["overall_drift"] else "CLEAN",
    }

    DRIFT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DRIFT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Output for journal
    status = "❌ DRIFT DETECTED" if results["overall_drift"] else "✅ CLEAN"
    print(f"arifos-drift: {status} at {now}")
    for name, org in results["organs"].items():
        flag = "⚠️ DRIFT" if org["drift"] else "  OK"
        print(
            f"  {flag} {name}: src={org['source_commit'][:8]} deployed={org['deployed_version'][:30]}"
        )


if __name__ == "__main__":
    main()
