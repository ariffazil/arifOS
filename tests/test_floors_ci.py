"""
arifOS Constitutional Floor CI Gate
====================================
Fails any merge to main if:
  1. fastmcp.json or mcp.json is empty/zero-bytes
  2. Manifest tool count != 11 canonical public tools
  3. Any public tool from tool_specs.py is missing from manifests
  4. More than one pyproject.toml exists at root level

Run: pytest tests/test_floors_ci.py -v
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TOOL_SPECS = ROOT / "arifosmcp/runtime/tool_specs.py"
FASTMCP_JSON = ROOT / "arifosmcp/fastmcp.json"
MCP_JSON = ROOT / "arifosmcp/mcp.json"
TOOL_REGISTRY = ROOT / "arifosmcp/tool_registry.json"


class TestManifestIntegrity:
    """F1: No empty manifests."""

    def test_fastmcp_not_empty(self):
        assert FASTMCP_JSON.exists(), "fastmcp.json missing"
        size = FASTMCP_JSON.stat().st_size
        assert size > 100, f"fastmcp.json is {size} bytes — looks empty"

    def test_mcp_not_empty(self):
        assert MCP_JSON.exists(), "mcp.json missing"
        size = MCP_JSON.stat().st_size
        assert size > 50, f"mcp.json is {size} bytes — looks empty"


class TestCanonicalSurface:
    """F2: Public surface is exactly 11 tools from tool_specs.py."""

    def _public_tools_from_spec(self):
        content = TOOL_SPECS.read_text()
        public = []
        blocks = re.split(r"(?=    ToolSpec\()", content)
        for block in blocks:
            name_m = re.search(r'name="(arifos_\w+)"', block)
            if not name_m:
                continue
            name = name_m.group(1)
            if 'visibility="public"' in block:
                public.append(name)
        return public

    def _tools_from_manifest(self, path):
        with open(path) as f:
            data = json.load(f)
        tools = data if isinstance(data, list) else data.get("tools", [])
        return [t.get("name") or (t.get("function", {}) or {}).get("name") for t in tools]

    def _tools_from_registry(self):
        with open(TOOL_REGISTRY) as f:
            data = json.load(f)
        return [t["function"]["name"] for t in data.get("tools", [])]

    def test_public_count_is_11(self):
        public = self._public_tools_from_spec()
        assert len(public) == 11, f"Expected 11 public tools in spec, got {len(public)}: {public}"
        print(f"  public tools in spec: {public}")

    def test_fastmcp_has_11(self):
        tools = self._tools_from_manifest(FASTMCP_JSON)
        assert len(tools) == 11, f"fastmcp.json has {len(tools)} tools, want 11: {tools}"

    def test_mcp_has_11(self):
        tools = self._tools_from_manifest(MCP_JSON)
        assert len(tools) == 11, f"mcp.json has {len(tools)} tools, want 11: {tools}"

    def test_manifests_match_spec(self):
        public = sorted(self._public_tools_from_spec())
        for manifest_path in [FASTMCP_JSON, MCP_JSON]:
            manifest_tools = sorted(self._tools_from_manifest(manifest_path))
            missing = [t for t in public if t not in manifest_tools]
            extra = [t for t in manifest_tools if t not in public]
            assert not missing, f"{manifest_path.name} missing tools: {missing}"
            assert not extra, f"{manifest_path.name} extra tools: {extra}"


class TestRepoHygiene:
    """F3: Runtime artefacts are not tracked in source."""

    TRACKED_ARTEFACTS = [
        ROOT / "arifosmcp/test.txt",
        ROOT / "arifosmcp/test_write.tmp",
        ROOT / "pytest_output.txt",
    ]

    def test_no_test_artifacts_tracked(self):
        git_root = ROOT
        # Check git ls-files for these
        import subprocess
        result = subprocess.run(
            ["git", "-C", str(git_root), "ls-files", "--"," ".join(str(a) for a in self.TRACKED_ARTEFACTS)],
            capture_output=True, text=True
        )
        tracked = [l for l in result.stdout.strip().split("\n") if l]
        assert not tracked, f"These runtime artefacts are still git-tracked: {tracked}"

    def test_no_extra_pyproject_toml(self):
        """Only one authoritative pyproject.toml at project root."""
        root_pyproject = ROOT / "pyproject.toml"
        assert root_pyproject.exists(), "Root pyproject.toml missing"
        # Count how many .toml files at root level
        tomls = list(ROOT.glob("pyproject*.toml"))
        assert len(tomls) == 1, f"Multiple pyproject files: {[t.name for t in tomls]}"
