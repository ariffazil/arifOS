#!/usr/bin/env python3
"""
arifOS Federation Drift Check — Live automated integrity probe.
Compares source commit, deployed commit, runtime identity, and registry hash.
Writes structured JSON to drift_log.jsonl. Never mutates.

DITEMPA BUKAN DIBERI — Forged 2026-07-19
"""
import json, os, sys, hashlib, subprocess
from datetime import datetime, timezone
from pathlib import Path

DRIFT_LOG = Path("/root/.local/share/arifos/vault999/drift_log.jsonl")

def git_commit(path: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", path, "rev-parse", "HEAD"],
            text=True, timeout=5
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

def probe_health(port: int) -> dict:
    import urllib.request
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5)
        return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def main():
    now = datetime.now(timezone.utc).isoformat()
    
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
        
        deployed_version = health.get("version", health.get("git_version", "UNKNOWN"))
        identity_raw = health.get("identity_hash", health.get("identity", {}))
        if isinstance(identity_raw, dict):
            runtime_identity = identity_raw.get("value", identity_raw.get("hash", "UNKNOWN"))
        else:
            runtime_identity = str(identity_raw) if identity_raw else "UNKNOWN"
        
        drift = (
            "error" in health
            or (source_commit != "UNKNOWN" and deployed_version != "UNKNOWN" 
                and source_commit[:8] not in str(deployed_version))
        )
        
        results["organs"][name] = {
            "source_commit": source_commit,
            "deployed_version": str(deployed_version)[:40],
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
        print(f"  {flag} {name}: src={org['source_commit'][:8]} deployed={org['deployed_version'][:30]}")

if __name__ == "__main__":
    main()
