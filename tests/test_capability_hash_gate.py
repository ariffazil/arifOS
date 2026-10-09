"""G0.6 semantic capability hash gates.

CapabilityHash = SHA256(JCS(sorted semantic records)). Drift in any semantic
field (name, stage, risk, floors, modes, schema content) changes the hash;
prose/formatting churn does not. The hash is witnessed in
capability_hash.json + peer-contract, and CI fails on unregenerated drift.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HASH_SCRIPT = REPO / "scripts" / "compute_capability_hash.py"
STATE = REPO / "static" / ".well-known" / "capability_hash.json"
PEER = REPO / "static" / ".well-known" / "peer-contract.json"

sys.path.insert(0, str(REPO / "scripts"))
from compute_capability_hash import (  # noqa: E402
    build_records,
    capability_hash,
)


def _run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HASH_SCRIPT), *args],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
    )


def test_hash_deterministic():
    a = capability_hash(build_records())
    b = capability_hash(build_records())
    assert a == b


def test_semantic_field_change_flips_hash():
    records = build_records()
    h0 = capability_hash(records)
    mutated = copy.deepcopy(records)
    for r in mutated:
        if r["canonical_name"] == "arif_seal":
            r["risk_tier"] = "critical" if r["risk_tier"] != "critical" else "high"
    assert capability_hash(mutated) != h0


def test_schema_content_change_flips_hash_but_formatting_does_not():
    records = build_records()
    h0 = capability_hash(records)
    # formatting-only: re-serialize one schema with different indentation —
    # hash is computed over the PARSE (JCS), so it must NOT change.
    import rfc8785

    rec = next(r for r in records if r["canonical_name"] == "arif_judge")
    schema_path = next(
        REPO.glob("arifosmcp/schema/registry/tools/arifos.judge*"),
    )
    parsed = json.loads(schema_path.read_text())
    assert rec["schema_sha256"] == "sha256:" + __import__("hashlib").sha256(
        rfc8785.dumps(parsed)
    ).hexdigest()
    # content change: add a property → must flip
    parsed2 = copy.deepcopy(parsed)
    parsed2.setdefault("properties", {})["__gatetest__"] = {"type": "string"}
    mutated = copy.deepcopy(records)
    next(
        r for r in mutated if r["canonical_name"] == "arif_judge"
    )["schema_sha256"] = "sha256:" + __import__("hashlib").sha256(
        rfc8785.dumps(parsed2)
    ).hexdigest()
    assert capability_hash(mutated) != h0


def test_state_and_peer_carry_current_hash():
    r = _run("--check")
    assert r.returncode == 0, r.stdout + r.stderr
    state = json.loads(STATE.read_text())
    peer = json.loads(PEER.read_text())
    assert state["record_count"] == 8
    assert (peer["capability_card"]["semantic_capability_hash"]
            == state["capability_hash"])
