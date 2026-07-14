from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from arifosmcp.abi.kernel_abi import (
    capability_ids,
    model_registry,
    profile_contract,
    receipt_registry,
    semantic_tool_names,
    validate_abi,
)

ROOT = Path(__file__).resolve().parents[1]


def test_abi_is_exactly_eight_semantic_capabilities() -> None:
    assert validate_abi()["ok"] is True
    assert capability_ids() == (
        "session.bind",
        "reality.observe",
        "cognition.think",
        "intent.route",
        "memory.govern",
        "authority.judge",
        "action.execute",
        "history.seal",
    )
    assert len(semantic_tool_names()) == 8


def test_four_registries_remain_separate() -> None:
    assert model_registry()["models"] == []
    assert "authority" not in model_registry().get("required_declarations", [])
    assert set(receipt_registry()["receipts"]) == set(capability_ids())
    assert profile_contract("public_agent")["diagnostics"] is False


def test_all_generated_surfaces_match_public_profile_snapshot() -> None:
    snapshot = json.loads((ROOT / "arifosmcp/abi/generated/public_agent.snapshot.json").read_text())
    expected = snapshot["profile_provider_tools"]
    server = json.loads((ROOT / "static/.well-known/mcp/server.json").read_text())
    compatibility = json.loads((ROOT / "mcp-arifos.json").read_text())

    assert [item["name"] for item in server["tools"]] == expected
    assert [item["name"] for item in compatibility["tools"]] == expected
    smithery = (ROOT / "smithery.yaml").read_text()
    assert smithery.count("  - id: arif_") == len(expected)
    assert all(f"  - id: {name}\n" in smithery for name in expected)


def test_generated_artifacts_have_no_drift() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/sync_kernel_abi.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
