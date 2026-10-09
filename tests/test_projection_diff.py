"""G0.4 projection-diff CI gate.

Projections (ai-plugin.json ×2, peer-contract skills/manifest) are GENERATED
from the kernel's canonical tool registry — hand-edits are drift. This gate
regenerates from source and fails on any divergence. The stale-projection
class (external connector fed `mode` on arif_route from a July ai-plugin;
peer-contract advertising retired tools with a stub signature) dies here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GEN = REPO / "scripts" / "generate_projections.py"
CANONICAL_8 = {
    "arif_init", "arif_observe", "arif_think", "arif_route",
    "arif_memory", "arif_judge", "arif_forge", "arif_seal",
}
RETIRED_NAMES = {"arif_session_init", "arif_lease_issue", "arif_gateway_connect"}


def _run_check() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GEN), "--check"],
        capture_output=True, text=True, timeout=120,
    )


def test_projection_diff_gate_passes():
    r = _run_check()
    assert r.returncode == 0, f"projection drift:\n{r.stdout}\n{r.stderr}"


def test_ai_plugin_twins_identical():
    a = (REPO / "static" / ".well-known" / "ai-plugin.json").read_bytes()
    b = (REPO / "arifosmcp" / "static" / ".well-known" / "ai-plugin.json").read_bytes()
    assert a == b, "ai-plugin twins diverged — regenerate BOTH via generator"


def test_ai_plugin_advertises_canonical_8_only():
    doc = json.loads((REPO / "static" / ".well-known" / "ai-plugin.json").read_text())
    assert set(doc["tools"]) == CANONICAL_8


def test_peer_contract_no_retired_tools_no_stub_signature():
    doc = json.loads((REPO / "static" / ".well-known" / "peer-contract.json").read_text())
    skills = set(doc["capability_card"]["skills"])
    assert skills == CANONICAL_8
    assert not (skills & RETIRED_NAMES)
    att = doc["signed_attestation"]
    assert att.get("attestation_status") == "pending"
    assert att.get("signature") in (None, "")  # never a stub string
    assert doc["capability_card"]["tool_manifest_url"].endswith("/mcp")
    assert doc["capability_card"].get("tool_manifest_sha256", "").startswith("sha256:")
