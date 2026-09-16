"""G1 release attestation gate.

The latest attestation in /opt/arifos/releases/attestations/ must verify:
valid Ed25519 signature over the JCS body, coherent tree hash, wheel sha
matching the release manifest, capability hash matching the committed
witness at the attested commit, and stamp alignment. CI environments
without the release plane skip; the VPS runs the full verification.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
LEDGER = Path("/opt/arifos/releases/attestations/latest.json")
EMITTER = REPO / "scripts" / "emit_release_attestation.py"

pytestmark = pytest.mark.skipif(
    not LEDGER.exists(), reason="no release plane on this host (CI)"
)


def test_latest_attestation_verifies():
    r = subprocess.run(
        [sys.executable, str(EMITTER), "--verify"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_attestation_binds_full_chain():
    att = json.loads(LEDGER.read_text())
    for section in ("source", "build", "governance", "runtime_witnessed"):
        assert section in att, f"missing chain section: {section}"
    assert att["build"]["wheel_sha256"].startswith("sha256:") or len(
        att["build"]["wheel_sha256"]
    ) == 64
    assert att["governance"]["capability_hash"].startswith("sha256:")
    assert att["signature"]["algorithm"] == "Ed25519"
    assert att["source"]["commit"]
