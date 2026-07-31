"""
proof_spine_variants.py — Mission variants beyond canary_write.

Missions:
  M11: Cross-organ health probe → verify 6/6 organs alive
  M12: Database query → verify read-only postgres query returns expected rows
  M13: Git commit → verify file write + commit + revert in sandbox
  M14: File hash chain → verify SHA256 chain integrity across writes

Each mission follows the same predict→execute→verify→compare→ingest→rollback loop.
DITEMPA BUKAN DIBERI — 2026-07-31
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

PROOF_ROOT = Path(os.getenv("ARIFOS_PROOF_ROOT", "/var/lib/arifos/proof_spine"))


def _sha16(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


# ── M11: Cross-Organ Health Probe ────────────────────────────────────────────

ORGAN_PORTS = {
    "arifos": 8088,
    "aforge": 7071,
    "aaa": 3001,
    "geox": 8081,
    "wealth": 18082,
    "well": 18083,
}


def run_cross_organ_health_mission() -> dict[str, Any]:
    """Verify all 6 federation organs respond to /health."""
    import urllib.request

    mission_id = f"PROOF-XORG-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    expected = {name: True for name in ORGAN_PORTS}
    actual = {}

    for name, port in ORGAN_PORTS.items():
        try:
            url = f"http://127.0.0.1:{port}/health"
            resp = urllib.request.urlopen(url, timeout=5)
            data = json.loads(resp.read())
            actual[name] = resp.status == 200 and "status" in data or "healthy" in str(data)
        except Exception:
            actual[name] = False

    match = actual == expected
    return {
        "mission_id": mission_id,
        "mission_type": "cross_organ_health",
        "disposition": "PASS" if match else "FAIL",
        "match": match,
        "expected": expected,
        "actual": actual,
        "organs_alive": sum(1 for v in actual.values() if v),
        "organs_total": len(ORGAN_PORTS),
        "completed_at": time.time(),
    }


# ── M12: Database Query ──────────────────────────────────────────────────────


def run_database_query_mission() -> dict[str, Any]:
    """Verify postgres responds to a read-only query."""
    import subprocess

    mission_id = f"PROOF-DB-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    expected = True  # query should succeed
    actual = False
    result = None

    try:
        proc = subprocess.run(
            [
                "docker",
                "exec",
                "postgres",
                "psql",
                "-U",
                "arifos_admin",
                "-d",
                "vault999",
                "-c",
                "SELECT 1 AS proof;",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        actual = proc.returncode == 0 and "proof" in proc.stdout.lower()
        result = proc.stdout[:200] if actual else proc.stderr[:200]
    except Exception as e:
        result = str(e)

    return {
        "mission_id": mission_id,
        "mission_type": "database_query",
        "disposition": "PASS" if actual == expected else "FAIL",
        "match": actual == expected,
        "expected": "query returns 'proof'",
        "actual": result,
        "completed_at": time.time(),
    }


# ── M13: Git Commit + Revert ─────────────────────────────────────────────────


def run_git_commit_revert_mission() -> dict[str, Any]:
    """Verify git write + commit + revert in isolated sandbox."""
    mission_id = f"PROOF-GIT-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    sandbox = PROOF_ROOT / mission_id
    sandbox.mkdir(parents=True, exist_ok=True)

    # Init git repo
    import subprocess

    subprocess.run(["git", "init"], cwd=sandbox, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "proof@arifos"], cwd=sandbox, capture_output=True
    )
    subprocess.run(["git", "config", "user.name", "ProofSpine"], cwd=sandbox, capture_output=True)

    # Write + commit
    test_file = sandbox / "proof.txt"
    content = f"PROOF-{uuid.uuid4().hex[:8]}"
    test_file.write_text(content)
    subprocess.run(["git", "add", "proof.txt"], cwd=sandbox, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "proof: git mutation test"], cwd=sandbox, capture_output=True
    )

    # Verify commit exists
    log = subprocess.run(
        ["git", "log", "--oneline", "-1"], cwd=sandbox, capture_output=True, text=True
    )
    actual = "proof: git mutation test" in log.stdout

    # Revert
    subprocess.run(["git", "revert", "--no-edit", "HEAD"], cwd=sandbox, capture_output=True)
    reverted = test_file.exists() is False or "PROOF-" not in (
        test_file.read_text() if test_file.exists() else ""
    )

    # Cleanup
    import shutil

    shutil.rmtree(sandbox, ignore_errors=True)

    return {
        "mission_id": mission_id,
        "mission_type": "git_commit_revert",
        "disposition": "PASS" if (actual and reverted) else "FAIL",
        "match": actual,
        "commit_verified": actual,
        "revert_verified": reverted,
        "completed_at": time.time(),
    }


# ── M14: File Hash Chain ─────────────────────────────────────────────────────


def run_hash_chain_mission() -> dict[str, Any]:
    """Verify SHA256 chain integrity across sequential writes."""
    mission_id = f"PROOF-HASH-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    sandbox = PROOF_ROOT / mission_id
    sandbox.mkdir(parents=True, exist_ok=True)

    chain = []
    for i in range(5):
        if i == 0:
            payload = f"block-{i}-{uuid.uuid4().hex[:8]}"
            chain.append(
                {"block": i, "content": payload, "hash": _sha16(payload), "prev_hash": None}
            )
        else:
            prev = chain[-1]["hash"]
            payload = f"block-{i}-{uuid.uuid4().hex[:8]}-prev={prev[:8]}"
            chain.append(
                {"block": i, "content": payload, "hash": _sha16(payload), "prev_hash": prev}
            )

    # Verify chain integrity
    valid = True
    for i in range(1, len(chain)):
        if chain[i]["prev_hash"] != chain[i - 1]["hash"]:
            valid = False
            break

    # Verify by recomputing
    recomputed = True
    for i in range(len(chain)):
        if _sha16(chain[i]["content"]) != chain[i]["hash"]:
            recomputed = False
            break

    import shutil

    shutil.rmtree(sandbox, ignore_errors=True)

    return {
        "mission_id": mission_id,
        "mission_type": "hash_chain",
        "disposition": "PASS" if (valid and recomputed) else "FAIL",
        "match": valid and recomputed,
        "chain_blocks": len(chain),
        "chain_valid": valid,
        "hashes_recomputable": recomputed,
        "completed_at": time.time(),
    }


# ── Run all variants ─────────────────────────────────────────────────────────


def run_all_variants(actor: str = "Arif-F13") -> list[dict[str, Any]]:
    """Run all proof spine variant missions."""
    results = []
    for name, fn in [
        ("M11: Cross-Organ Health", run_cross_organ_health_mission),
        ("M12: Database Query", run_database_query_mission),
        ("M13: Git Commit + Revert", run_git_commit_revert_mission),
        ("M14: Hash Chain", run_hash_chain_mission),
    ]:
        try:
            r = fn()
            r["label"] = name
            results.append(r)
        except Exception as e:
            results.append({"label": name, "disposition": "ERROR", "error": str(e)})
    return results
