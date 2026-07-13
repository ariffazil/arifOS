#!/usr/bin/env python3
"""
verify_attestation.py — Independent Proof Executor

Verifies the arifOS runtime release attestation independently of the server.
Can run against a live :8088/health endpoint or a saved attestation snapshot.

Usage:
    python3 verify_attestation.py                         # live :8088
    python3 verify_attestation.py --host localhost:8088   # explicit host
    python3 verify_attestation.py --snapshot file.json    # saved snapshot
    python3 verify_attestation.py --strict                # fail on any warning

Returns exit code 0 (PASS), 1 (WARN), or 2 (FAIL).
"""

import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ── Invariant checks ────────────────────────────────────────────────
REQUIRED_RELEASE_FIELDS = frozenset(
    {
        "release_id",
        "source_commit",
        "wheel_hash",
        "runtime_manifest_hash",
        "service_pid",
        "service_started_at",
    }
)

CRITICAL_MODULES = frozenset(
    {
        "arifosmcp/tools/session.py",
        "arifosmcp/runtime/crypto_auth.py",
        "arifosmcp/runtime/convergence_tracker.py",
        "arifosmcp/runtime/cooling_verbs.py",
        "arifosmcp/runtime/forge_session_runtime.py",
        "arifosmcp/runtime/governance_identity.py",
        "arifosmcp/runtime/rest_routes/rest_routes.py",
    }
)

HEALTH_INVARIANTS = frozenset(
    {
        "status",
        "service",
        "version",
        "git_commit",
        "build_time",
        "floors_active",
        "runtime_drift",
        "software_release",
    }
)


def _check(val: bool, msg: str, fail: bool = False) -> int:
    """Print check result and return severity."""
    if val:
        print(f"  ✅ {msg}")
        return 0
    else:
        print(f"  {'❌' if fail else '⚠️'} {msg}")
        return 2 if fail else 1


def verify_health_payload(payload: dict, strict: bool = False) -> int:
    """Run invariant checks against the /health payload."""
    score = 0
    print("\n📋 Health Envelope Invariants:")

    # 1. Status must be healthy
    score += _check(payload.get("status") == "healthy", "status = healthy", fail=True)

    # 2. Required top-level fields
    missing = HEALTH_INVARIANTS - set(payload.keys())
    score += _check(
        not missing,
        f"all health invariants present (missing: {sorted(missing) or 'none'})",
        fail=bool(missing),
    )

    # 3. Floors must be 13
    score += _check(
        payload.get("floors_active") == 13,
        f"floors_active = {payload.get('floors_active')} (expected 13)",
        fail=True,
    )

    # 4. Runtime drift must be false
    score += _check(
        payload.get("runtime_drift") is False,
        f"runtime_drift = {payload.get('runtime_drift')} (expected false)",
        fail=True,
    )

    # 5. Contract drift must be false
    contract_drift = payload.get(
        "contract_drift", payload.get("contract_status", {}).get("contract_drift")
    )
    score += _check(
        contract_drift is False, f"contract_drift = {contract_drift} (expected false)", fail=True
    )

    # 6. software_release attestation
    release = payload.get("software_release", {})
    missing_rel = REQUIRED_RELEASE_FIELDS - set(release.keys())
    score += _check(
        not missing_rel,
        f"software_release fields present (missing: {sorted(missing_rel) or 'none'})",
        fail=bool(missing_rel),
    )

    # 7. release_id must not be "unknown"
    rid = release.get("release_id", "")
    score += _check(
        rid and rid != "unknown", f"release_id = {rid}", fail=(not rid or rid == "unknown")
    )

    # 8. source_commit must not be "unknown"
    sc = release.get("source_commit", "")
    score += _check(
        sc and sc != "unknown", f"source_commit = {sc}", fail=(not sc or sc == "unknown")
    )

    # 9. critical_module_hashes must include all CRITICAL_MODULES
    cmh = release.get("critical_module_hashes", {})
    missing_mods = CRITICAL_MODULES - set(cmh.keys())
    score += _check(
        not missing_mods,
        f"critical_module_hashes covers all modules (missing: {sorted(missing_mods) or 'none'})",
        fail=bool(missing_mods),
    )

    # 10. runtime_manifest_hash must be a valid sha256: prefix
    rmh = release.get("runtime_manifest_hash", "")
    score += _check(
        rmh.startswith("sha256:") and len(rmh) == 71,
        f"runtime_manifest_hash format valid (len={len(rmh)})",
        fail=(not rmh.startswith("sha256:")),
    )

    # 11. Build attribution
    score += _check(
        bool(payload.get("source_repo")),
        f"source_repo = {payload.get('source_repo', 'MISSING')}",
        fail=(not payload.get("source_repo")),
    )

    # 12. PID must be positive int
    pid = release.get("service_pid", 0)
    score += _check(
        isinstance(pid, int) and pid > 0,
        f"service_pid = {pid}",
        fail=(not isinstance(pid, int) or pid <= 0),
    )

    verdict = "PASS" if score == 0 else ("WARN" if score <= 2 else "FAIL")
    print(f"\n🏁 VERDICT: {verdict} (score={score}, strict={strict})")
    if strict and score > 0:
        return 2
    return 0 if score == 0 else (1 if score <= 2 else 2)


def fetch_health(host: str) -> dict:
    """Fetch /health from live arifOS."""
    url = f"http://{host}/health"
    print(f"\n🌐 Fetching {url} ...")
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"  ❌ Failed to fetch health: {e}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON response: {e}")
        sys.exit(2)


def main():
    host = "127.0.0.1:8088"
    snapshot = None
    strict = False

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--host" and i + 1 < len(args):
            host = args[i + 1]
        elif arg == "--snapshot" and i + 1 < len(args):
            snap_path = args[i + 1]
            with open(snap_path) as f:
                snapshot = json.load(f)
        elif arg == "--strict":
            strict = True
        elif arg == "--help":
            print(__doc__)
            sys.exit(0)

    if snapshot:
        print(f"📄 Using snapshot: {snap_path if 'snap_path' in dir() else '(inline)'}")
        payload = snapshot
    else:
        payload = fetch_health(host)

    exit_code = verify_health_payload(payload, strict=strict)
    print(f"\n{'=' * 50}")
    print(f"Exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
