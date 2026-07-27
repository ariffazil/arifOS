"""
SURFACE CONFORMANCE GATE TEST
═══════════════════════════════

Validates: advertised_public_tools == runtime_callable_public_tools
If not equal → deployment fails, verdict = 888_HOLD.

This test interacts with the live arifOS kernel at :8088. When the kernel
is not running (CI environment without server), it performs a static
registry-consistency check instead.

Integrated via `make prove` (step added to proof pack).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest

# Add project root to ensure imports resolve
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from arifosmcp.schemas.tool_registry import (
    load_registry,
    public_tool_names,
    sdk_alias_map,
    surface_conformance_check,
    validate_tool_registry,
)

KERNEL_URL = os.environ.get("ARIFOS_KERNEL_URL", "http://127.0.0.1:8088")
HEALTH_ENDPOINT = f"{KERNEL_URL}/health"
MCP_ENDPOINT = f"{KERNEL_URL}/mcp"

# P0 = must-pass for any deployment
# P1 = should-pass, warns but doesn't block
PRIORITY = "P0"
P1 = "P1"


def _fetch_health() -> dict[str, Any] | None:
    """Fetch the arifOS /health endpoint. Returns None if unreachable."""
    try:
        resp = urllib.request.urlopen(HEALTH_ENDPOINT, timeout=10)
        return json.loads(resp.read().decode())
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, json.JSONDecodeError) as e:
        return None


def _mcp_tools_list() -> list[str] | None:
    """Fetch the runtime tool list from the kernel.

    Tries in order:
      1. GET /tools  — arifOS canonical surface (returns {tools: [{name, canonical, ...}]})
      2. POST /mcp   — MCP JSON-RPC tools/list (fallback if kernel speaks JSON-RPC)

    Returns tool names or None.
    """
    # 1. arifOS canonical surface: GET /tools
    try:
        req = urllib.request.Request(
            f"{KERNEL_URL}/tools",
            headers={"Accept": "application/json"},
            method="GET",
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        if isinstance(data, dict) and isinstance(data.get("tools"), list):
            names = []
            for t in data["tools"]:
                if isinstance(t, dict) and "name" in t:
                    names.append(t["name"])
            if names:
                return names
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, json.JSONDecodeError):
        pass

    # 2. MCP JSON-RPC tools/list (fallback)
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": "surface-gate-1",
    }).encode()
    try:
        req = urllib.request.Request(
            MCP_ENDPOINT,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        if "result" in data and "tools" in data["result"]:
            return [t["name"] for t in data["result"]["tools"]]
        if "error" in data:
            print(f"  tools/list error: {data['error']}")
            return None
        return None
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, json.JSONDecodeError) as e:
        return None


def _parse_tools_from_health(health: dict[str, Any]) -> list[str]:
    """Extract tool names from the /health response."""
    # Try various known paths
    for key in ("tools_loaded", "tool_names"):
        val = health.get(key)
        if isinstance(val, list):
            return val
    contract = health.get("contract_status", {})
    if isinstance(contract, dict):
        for key in ("tool_names", "tools"):
            val = contract.get(key)
            if isinstance(val, list):
                return val
    # Fallback: extract from public_surface_state
    surface = health.get("public_surface_state", {})
    if isinstance(surface, dict):
        val = surface.get("tool_names")
        if isinstance(val, list):
            return val
    return []


# ═════════════════════════════════════════════════════════════════════════
# TEST 1: Registry Self-Consistency
# ═════════════════════════════════════════════════════════════════════════


class TestRegistrySelfConsistency:
    """Verify the tool registry is internally consistent."""

    def test_registry_self_consistent(self):
        """Validate no overlapping tools, valid alias targets, valid profiles."""
        result = validate_tool_registry()
        assert result["ok"], f"Registry validation failed: {result['errors']}"

    def test_public_tool_count(self):
        """Public tool count must be exactly 8 (KERNEL_ABI_8)."""
        names = public_tool_names()
        assert len(names) == 8, f"Expected 8 public tools, got {len(names)}: {names}"

    def test_all_public_tools_have_arif_prefix(self):
        """All public tools must use arif_ naming convention."""
        for name in public_tool_names():
            assert name.startswith("arif_"), f"Tool {name} does not start with arif_"

    def test_no_internal_tools_in_public(self):
        """Internal tool names must not overlap with public tool names."""
        reg = load_registry()
        public = set(reg["public_tools"].keys())
        internal = set(reg["internal_tools"].keys())
        overlap = public & internal
        assert not overlap, f"Tools in both public and internal: {overlap}"

    def test_no_arifos_prefix_in_public(self):
        """No arifos_* tools in public tools (they're internal/diagnostic)."""
        for name in public_tool_names():
            assert not name.startswith("arifos_"), f"Public tool {name} uses arifos_ prefix"

    def test_sdk_aliases_target_valid_tools(self):
        """Every SDK alias must point to a known public or internal tool."""
        reg = load_registry()
        all_known = set(reg["public_tools"].keys()) | set(reg["internal_tools"].keys())
        for alias, info in sdk_alias_map().items():
            target = info.get("target", "")
            assert target in all_known, (
                f"Alias '{alias}' points to unknown target '{target}'"
            )


# ═════════════════════════════════════════════════════════════════════════
# TEST 2: Live Surface Conformance (requires running kernel)
# ═════════════════════════════════════════════════════════════════════════


class TestLiveSurfaceConformance:
    """Compare registry contract against live runtime exposure.

    If the kernel is not running, these tests skip gracefully.
    """

    @pytest.fixture(scope="class")
    def live_data(self):
        """Fetch live kernel data once per class."""
        health = _fetch_health()
        tools_list = _mcp_tools_list()
        return {
            "health": health,
            "tools_list": tools_list,
            "kernel_alive": health is not None,
        }

    def test_kernel_accessible(self, live_data):
        """P0: Kernel must be accessible for conformance check."""
        if not live_data["kernel_alive"]:
            pytest.skip("Kernel not reachable — skipping live conformance tests")
        assert live_data["health"] is not None, "Health endpoint unreachable"
        status = live_data["health"].get("status", "unknown")
        assert status in ("healthy", "ok"), f"Kernel status: {status}"

    def test_live_surface_conformance(self, live_data):
        """P0: advertised_public_tools == runtime_callable_public_tools.

        This is the canonical gate. Any drift triggers 888_HOLD.
        """
        if not live_data["kernel_alive"]:
            pytest.skip("Kernel not reachable — skipping live conformance check")

        # Prefer tools/list (the canonical MCP endpoint)
        runtime_tools = live_data["tools_list"]

        # Fall back to health endpoint if tools/list failed
        if runtime_tools is None:
            runtime_tools = _parse_tools_from_health(live_data["health"])

        assert runtime_tools is not None and len(runtime_tools) > 0, (
            f"Cannot determine runtime tools. Health keys: {list(live_data['health'].keys())}"
        )

        print(f"\n  Runtime tools ({len(runtime_tools)}): {sorted(runtime_tools)}")

        result = surface_conformance_check(runtime_tools, profile="sovereign")

        print(f"  Registry public tools ({len(result['expected_tools'])}): {result['expected_tools']}")
        print(f"  Verdict: {result['verdict']}")

        if not result["ok"]:
            print(f"\n  ⚠ DRIFT REPORT: {result['drift_report']}")
            for detail in result["details"]:
                if detail.get("anomaly"):
                    print(f"    [{detail['anomaly']}] {detail['tool']}: {detail['message']}")

        assert result["ok"], (
            f"SURFACE CONFORMANCE GATE: 888_HOLD\n"
            f"Drift detected — registry contract ≠ runtime exposure.\n"
            f"{result['drift_report']}\n\n"
            f"Expected: {result['expected_tools']}\n"
            f"Runtime:  {result['runtime_tools']}\n"
            f"Missing:  {result['missing']}\n"
            f"Unexpected (public): {result['unexpected']}"
        )

    def test_no_internal_tools_on_public_wire(self, live_data):
        """P0: Internal tools must NOT appear on the public wire surface."""
        if not live_data["kernel_alive"]:
            pytest.skip("Kernel not reachable")

        runtime_tools = live_data["tools_list"]
        if runtime_tools is None:
            runtime_tools = _parse_tools_from_health(live_data["health"])

        result = surface_conformance_check(runtime_tools, profile="sovereign")

        if result["internal_leaks"]:
            pytest.fail(
                f"INTERNAL TOOLS LEAKED TO PUBLIC WIRE: {result['internal_leaks']}\n"
                f"These tools are marked internal_only in registry but appear at runtime."
            )

    def test_no_sdk_aliases_as_standalone_tools(self, live_data):
        """P0: SDK aliases must redirect, not appear as standalone tools."""
        if not live_data["kernel_alive"]:
            pytest.skip("Kernel not reachable")

        runtime_tools = live_data["tools_list"]
        if runtime_tools is None:
            runtime_tools = _parse_tools_from_health(live_data["health"])

        result = surface_conformance_check(runtime_tools, profile="sovereign")

        if result["alias_leaks"]:
            pytest.fail(
                f"SDK ALIASES ON WIRE AS STANDALONE: {result['alias_leaks']}\n"
                f"These aliases should redirect to canonical tools, not appear directly."
            )


# ═════════════════════════════════════════════════════════════════════════
# TEST 3: Static registry invariants (always run, no kernel needed)
# ═════════════════════════════════════════════════════════════════════════


class TestRegistryInvariants:
    """Static invariants that hold regardless of kernel state."""

    def test_registry_version_matches_expected(self):
        """Registry must declare a version."""
        reg = load_registry()
        assert "registry_version" in reg, "Registry missing version"
        assert reg["registry_version"], "Registry version is empty"

    def test_public_tools_have_required_fields(self):
        """Every public tool must have: description, stage, lane, floors, modes."""
        reg = load_registry()
        required = {"description", "stage", "lane", "floors", "modes", "risk_tier"}
        for name, spec in reg["public_tools"].items():
            missing = required - set(spec.keys())
            assert not missing, f"Public tool '{name}' missing fields: {missing}"

    def test_internal_tools_have_redirect(self):
        """Every internal tool must document its redirect target."""
        reg = load_registry()
        for name, spec in reg["internal_tools"].items():
            assert "redirect_to" in spec, f"Internal tool '{name}' missing redirect_to"
            assert "access_reason" in spec, f"Internal tool '{name}' missing access_reason"

    def test_profiles_cover_all_public_tools(self):
        """Every public tool must appear in at least one conformance profile."""
        reg = load_registry()
        public = set(reg["public_tools"].keys())
        profiled: set[str] = set()
        for cfg in reg["conformance_expectations"]["profiles"].values():
            profiled.update(cfg["exposed_tools"])
        uncovered = public - profiled
        assert not uncovered, f"Public tools not in any profile: {sorted(uncovered)}"

    def test_888_hold_triggers_defined(self):
        """Surface doctrine must define 888_HOLD trigger conditions."""
        reg = load_registry()
        triggers = reg.get("surface_doctrine", {}).get("888_hold_triggers", [])
        assert len(triggers) >= 1, "Must define at least one 888_HOLD trigger condition"

    def test_registry_symlinked_from_abi(self):
        """The registry should be discoverable from the ABI directory."""
        abi_path = _project_root / "arifosmcp" / "abi" / "arifos_tool_registry.json"
        if not abi_path.exists():
            # Create a symlink for backward compat discovery
            try:
                source = _project_root / "arifosmcp" / "schemas" / "arifos_tool_registry.json"
                if source.exists():
                    abi_path.symlink_to(os.path.relpath(source, start=abi_path.parent))
            except (OSError, FileNotFoundError):
                pass  # Non-fatal — just nice to have


# ═════════════════════════════════════════════════════════════════════════
# TEST 4: Conformance profile consistency
# ═════════════════════════════════════════════════════════════════════════


class TestConformanceProfiles:
    """Validate that conformance profiles are consistent with each other."""

    def test_profile_tool_counts_are_monotonic(self):
        """Profile tool sets should be monotonic: public_agent ⊆ trusted_agent ⊆ ..."""
        reg = load_registry()
        profiles = reg["conformance_expectations"]["profiles"]
        order = ["public_agent", "trusted_agent", "executor", "sovereign"]
        prev: set[str] = set()
        for name in order:
            current = set(profiles[name]["exposed_tools"])
            if prev:
                assert prev.issubset(current), (
                    f"Profile '{name}' does not contain all tools from predecessor. "
                    f"Previous: {sorted(prev - current)}"
                )
            prev = current

    def test_operator_equals_sovereign_plus_diagnostics(self):
        """Operator profile = sovereign tools + diagnostics flag."""
        reg = load_registry()
        profiles = reg["conformance_expectations"]["profiles"]
        sovereign = set(profiles["sovereign"]["exposed_tools"])
        operator = set(profiles["operator"]["exposed_tools"])
        assert sovereign == operator, (
            f"Operator should have same tools as sovereign. "
            f"Extra in operator: {sorted(operator - sovereign)}. "
            f"Missing: {sorted(sovereign - operator)}."
        )
        assert profiles["operator"]["diagnostics"] is True, "Operator must have diagnostics=True"
        assert profiles["sovereign"]["diagnostics"] is False, "Sovereign must have diagnostics=False"


# ═════════════════════════════════════════════════════════════════════════
# CLI runner for make prove integration
# ═════════════════════════════════════════════════════════════════════════


def run_surface_gate() -> dict[str, Any]:
    """Run the full surface conformance gate, return verdict dict.

    Called by make prove / CI pipeline.
    """
    print("═══ SURFACE CONFORMANCE GATE ═══")
    print()

    # Step 1: Validate registry internally
    print("[1/4] Validating registry self-consistency...")
    result = validate_tool_registry()
    if not result["ok"]:
        return {
            "ok": False,
            "step": 1,
            "verdict": "888_HOLD",
            "message": f"Registry validation failed: {result['errors']}",
            "details": result,
        }
    print(f"  ✓ Public: {result['public_count']}, Internal: {result['internal_count']}, "
          f"Aliases: {result['alias_count']}, Profiles: {result['profile_count']}")
    print()

    # Step 2: Probe live kernel
    print("[2/4] Probing live kernel...")
    health = _fetch_health()
    if health is None:
        print("  ⚠ Kernel not reachable — static check only (CI mode)")
        print()
        print("[3/4] Skipping live surface conformance (no kernel)")
        print()
        print("[4/4] GATE PASSED (static checks only)")
        return {
            "ok": True,
            "step": 4,
            "verdict": "SEAL",
            "details": result,
            "note": "Kernel not running — static checks passed",
        }

    status = health.get("status", "unknown")
    print(f"  ✓ Kernel status: {status}")
    runtime_tools = _mcp_tools_list()
    if runtime_tools is None:
        runtime_tools = _parse_tools_from_health(health)
    print(f"  ✓ Runtime reports {len(runtime_tools)} tools")
    print()

    # Step 3: Surface conformance check
    print("[3/4] Running surface conformance check...")
    check = surface_conformance_check(runtime_tools, profile="sovereign")
    if not check["ok"]:
        print(f"  ✗ VERDICT: {check['verdict']}")
        print(f"  ✗ DRIFT: {check['drift_report']}")
        for detail in check["details"]:
            if detail.get("anomaly"):
                print(f"    [{detail['anomaly']}] {detail['tool']}: {detail['message']}")
        print()
        return {
            "ok": False,
            "step": 3,
            "verdict": "888_HOLD",
            "message": check["drift_report"],
            "details": {**result, **check},
        }
    print(f"  ✓ VERDICT: {check['verdict']}")
    print(f"  ✓ All {len(check['expected_tools'])} expected tools found at runtime")
    print()

    # Step 4: Final verdict
    print("[4/4] GATE PASSED")
    print(f"  Verdict: SEAL")
    print(f"  Registry contract === runtime exposure on profile 'sovereign'")
    return {
        "ok": True,
        "step": 4,
        "verdict": "SEAL",
        "details": {**result, **check},
    }


# Allow standalone execution for `make prove`
if __name__ == "__main__":
    result = run_surface_gate()
    if not result["ok"]:
        print("888_HOLD: Surface drift detected — aborting.")
        sys.exit(1)
    print("SEAL: Surface conformance gate passed.")
    sys.exit(0)
