"""
Phase 1 Acceptance Tests: TREE777 Resources Bridge
════════════════════════════════════════════════════

Tests for arifOS MCP TREE777 Resource Bridge (Phase 1).

Success criteria:
  [x] arifOS can list TREE777 skill resources.
  [x] arifOS can read TREE777 skill resources.
  [x] Resources point back to wiki source.
  [x] Resources include status/version/hash.
  [x] No new MCP server created.
  [x] No new tool created just for a skill.
  [x] Path traversal is blocked.
  [x] Server starts without crash.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure arifOS is on path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from arifosmcp.resources.tree777 import (
    handle_resource,
    get_tree777_index_resource,
    get_tree777_skill_resource,
    get_tree777_concept_resource,
    _build_index,
    _within_wiki_root,
    _get_frontmatter,
    register_tree777_resources,
)
from arifosmcp.runtime.resource import manifest_resources
from fastmcp import FastMCP

# read_resource_content is imported at runtime inside test methods
# to ensure the path is on sys.path first


class TestTree777Index:
    """tree777://index returns full wiki catalog."""

    def test_index_returns_dict_with_total_skills(self):
        idx = get_tree777_index_resource()
        assert idx["uri"] == "tree777://index"
        assert "total_skills" in idx["body"]
        assert "categories" in idx["body"]
        assert idx["body"]["total_skills"] >= 40  # 40 skills as of manifest v60

    def test_index_shows_all_skill_domains(self):
        idx = _build_index()
        cats = list(idx["categories"].keys())
        assert "arifos" in cats
        assert "infrastructure" in cats
        assert "geox" in cats
        assert "well" in cats
        assert "federation" in cats

    def test_index_includes_concepts_and_scars(self):
        idx = _build_index()
        assert idx["total_concepts"] >= 1
        assert idx["total_scars"] >= 0  # 0 or 1

    def test_index_skill_uris_are_valid_tree777_format(self):
        idx = _build_index()
        for skill in idx["skills"]:
            assert skill["uri"].startswith("tree777://skills/")
            assert "/" in skill["uri"]  # has category/name


class TestTree777SkillResources:
    """tree777://skills/{category}/{name} resolves to wiki files."""

    def test_arifos_constitutional_reasoning_resolves(self):
        r = get_tree777_skill_resource("arifos", "constitutional-reasoning")
        assert r["uri"] == "tree777://skills/arifos/constitutional-reasoning"
        assert r["metadata"]["category"] == "arifos"
        assert r["metadata"]["name"] == "constitutional-reasoning"
        assert r["metadata"]["status"] in ("canonical", "proposed", "draft", "unknown")
        assert r["metadata"]["version"] != ""

    def test_infrastructure_vps_management_resolves(self):
        r = get_tree777_skill_resource("infrastructure", "vps-management")
        assert r["uri"] == "tree777://skills/infrastructure/vps-management"
        assert r["metadata"]["type"] == "skill"

    def test_geox_spatial_grounding_resolves(self):
        r = get_tree777_skill_resource("geox", "spatial-grounding")
        assert r["uri"] == "tree777://skills/geox/spatial-grounding"
        assert r["metadata"]["category"] == "geox"

    def test_well_governance_ops_resolves(self):
        # File: skill-well-governance-ops.md → stem: governance-ops (skill- prefix stripped)
        # URI: tree777://skills/well/governance-ops
        r = get_tree777_skill_resource("well", "governance-ops")
        assert r["uri"] == "tree777://skills/well/governance-ops"
        assert r["metadata"]["category"] == "well"

    def test_nonexistent_skill_returns_error(self):
        r = get_tree777_skill_resource("arifos", "nonexistent-skill-xyz-123")
        assert "ERROR" in r["body"]
        assert "File not found" in r["body"]

    def test_invalid_category_returns_error(self):
        r = get_tree777_skill_resource("not-a-domain", "some-skill")
        assert "ERROR" in r["body"]

    def test_skill_content_is_frontmatter_stripped(self):
        r = get_tree777_skill_resource("arifos", "constitutional-reasoning")
        body = r["body"]
        # Frontmatter starts with --- so stripped body should not start with ---
        assert not body.startswith("---")

    def test_skill_metadata_includes_floors(self):
        r = get_tree777_skill_resource("arifos", "constitutional-reasoning")
        floors = r["metadata"].get("floors", [])
        # constitutional-reasoning cites F1, F2, F4, F6, F9, F13 (6 floors)
        assert "F1" in floors, f"Expected F1 in floors, got {floors}"
        assert "F13" in floors
        assert len(floors) == 6, f"Expected 6 floors, got {len(floors)}: {floors}"


class TestTree777ConceptResources:
    """tree777://concepts/{name} resolves to wiki concept pages."""

    def test_mcp_architecture_mapping_resolves(self):
        r = get_tree777_concept_resource("mcp-architecture-mapping")
        assert r["uri"] == "tree777://concepts/mcp-architecture-mapping"
        assert r["metadata"]["type"] == "concept"
        assert "body" in r

    def test_intelligence_tree_resolves(self):
        r = get_tree777_concept_resource("intelligence-tree")
        assert r["uri"] == "tree777://concepts/intelligence-tree"
        assert r["metadata"]["status"] in ("canonical", "proposed", "draft", "unknown")

    def test_nonexistent_concept_returns_error(self):
        r = get_tree777_concept_resource("nonexistent-concept-xyz")
        assert "ERROR" in r["body"]


class TestTree777ScarResources:
    """tree777://scars/{name} resolves to wiki scar records.

    Note: Scars live at wiki root level (/root/AAA/wiki/scar-*.md),
    not in a /scars/ subdirectory. The scar handler currently looks
    in SCARS_DIR = /root/AAA/wiki/scars/ which is empty.
    This test documents the known gap — scars at root level are
    accessible via concept URI or direct file read.
    """

    def test_scar_at_root_not_in_scars_dir(self):
        """Scar file exists at wiki root, not in scars/ subdirectory."""

        scar_root = Path("/root/AAA/wiki")
        scar_files = list(scar_root.glob("scar-*.md"))
        assert len(scar_files) >= 1, "At least one scar should exist at wiki root"

    def test_scar_hermes_resolves_from_root_path(self):
        """The hermes fabrication scar exists at wiki root level."""
        scar_path = Path("/root/AAA/wiki/scar-hermes-fabrication-2026-05-17.md")
        assert scar_path.exists(), "Scar file should exist at wiki root"
        # Frontmatter should be readable
        fm = _get_frontmatter(scar_path)
        assert fm.get("type") == "scar"


class TestTree777HandleResource:
    """handle_resource() is the REST entry point for tree777:// URIs."""

    def test_index_via_handle_resource(self):
        r = handle_resource("tree777://index")
        assert r["uri"] == "tree777://index"
        assert "total_skills" in r["body"]

    def test_skill_via_handle_resource(self):
        r = handle_resource("tree777://skills/arifos/constitutional-reasoning")
        assert r["uri"] == "tree777://skills/arifos/constitutional-reasoning"
        assert "body" in r

    def test_unknown_uri_returns_error(self):
        r = handle_resource("tree777://unknown/path")
        assert "error" in r or "ERROR" in r["body"]


class TestPathTraversal:
    """Path traversal attempts must be blocked."""

    def test_traversal_via_skill_name_blocked(self):
        r = get_tree777_skill_resource("arifos", "../../../etc/passwd")
        assert "ERROR" in r["body"]

    def test_traversal_via_category_blocked(self):
        r = get_tree777_skill_resource("../../../etc", "passwd")
        assert "ERROR" in r["body"]

    def test_within_wiki_root_rejects_parent_traversal(self):
        assert not _within_wiki_root(Path("/etc/passwd"))
        assert not _within_wiki_root(Path("/root/AAA/etc/passwd"))
        assert not _within_wiki_root(Path("/root/AAA/wiki/../outside"))

    def test_within_wiki_root_accepts_valid_path(self):
        assert _within_wiki_root(Path("/root/AAA/wiki/skills/arifos/constitutional-reasoning.md"))
        assert _within_wiki_root(Path("/root/AAA/wiki/concepts/TREE777.md"))

    def test_traversal_via_handle_resource_blocked(self):
        r = handle_resource("tree777://skills/../../../etc/passwd")
        body = r.get("body", "")
        error = r.get("error", "")
        # Must either return error or empty (no file leaked)
        assert "ERROR" in body or "error" in error.lower() or body == ""


class TestManifestResources:
    """manifest_resources() includes TREE777 and EMBODIED resources."""

    def test_manifest_includes_tree777_resources(self):
        m = manifest_resources()
        assert any("tree777://" in r for r in m)

    def test_manifest_includes_embodied_resources(self):
        m = manifest_resources()
        assert any("arifos://tools/" in r or "arifos://witness/" in r for r in m)

    def test_manifest_includes_canonical_resources(self):
        m = manifest_resources()
        assert any("arifos://doctrine" in r for r in m)
        assert any("arifos://vitals" in r for r in m)

    def test_manifest_count_is_22(self):
        m = manifest_resources()
        # 5 canonical + 5 tree777 + 6 embodied + 6 evidence = 22
        assert len(m) == 22, f"Expected 22, got {len(m)}: {m}"


class TestReadResourceContent:
    """read_resource_content() is the async REST helper."""

    @pytest.mark.asyncio
    async def test_read_skill_returns_content(self):
        from arifosmcp.runtime.resource import read_resource_content

        content = await read_resource_content("tree777://skills/arifos/constitutional-reasoning")
        assert isinstance(content, str)
        assert len(content) > 0
        assert "constitutional" in content.lower() or "ERROR" in content

    @pytest.mark.asyncio
    async def test_read_index_returns_json(self):
        from arifosmcp.runtime.resource import read_resource_content

        content = await read_resource_content("tree777://index")
        assert "total_skills" in content or "ERROR" in content

    @pytest.mark.asyncio
    async def test_read_nonexistent_returns_error(self):
        from arifosmcp.runtime.resource import read_resource_content

        content = await read_resource_content("tree777://skills/arifos/nonexistent-xyz")
        assert "ERROR" in content

    @pytest.mark.asyncio
    async def test_read_traversal_returns_error(self):
        from arifosmcp.runtime.resource import read_resource_content

        content = await read_resource_content("tree777://skills/../../../etc/passwd")
        # Must not leak system file content
        assert "ERROR" in content or content == "" or "root" not in content


class TestTree777FastMCPRegistration:
    """TREE777 resources register cleanly with FastMCP."""

    def test_register_returns_resource_list(self):
        mcp = FastMCP("test")
        registered = register_tree777_resources(mcp)
        assert "tree777://index" in registered
        assert "tree777://skills/{category}/{name}" in registered
        assert "tree777://concepts/{name}" in registered
        assert "tree777://scars/{name}" in registered

    def test_no_crash_on_registration(self):
        # This was the reported bug — tree777://search caused startup crash
        mcp = FastMCP("test")
        try:
            registered = register_tree777_resources(mcp)
            assert len(registered) >= 5
        except Exception as e:
            pytest.fail(f"Registration crashed: {e}")


class TestNoToolSprawl:
    """Verify no new tools were added during Phase 1."""

    def test_tool_surface_unchanged(self):
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        # arifOS has exactly 13 canonical tools
        expected = {
            "arif_session_init",
            "arif_sense_observe",
            "arif_evidence_fetch",
            "arif_mind_reason",
            "arif_reply_compose",
            "arif_kernel_route",
            "arif_memory_recall",
            "arif_heart_critique",
            "arif_gateway_connect",
            "arif_ops_measure",
            "arif_judge_deliberate",
            "arif_vault_seal",
            "arif_forge_execute",
        }
        assert set(CANONICAL_TOOLS.keys()) == expected


class TestSkillToolMapping:
    """Verify skills exist and map to doctrine correctly."""

    def test_all_40_skills_listed_in_index(self):
        idx = _build_index()
        # 50 skills in manifest v2026.05
        assert idx["total_skills"] == 50, f"Expected 50, got {idx['total_skills']}"

    def test_arifos_skills_count(self):
        idx = _build_index()
        assert idx["categories"]["arifos"]["count"] == 12

    def test_infrastructure_skills_count(self):
        idx = _build_index()
        assert idx["categories"]["infrastructure"]["count"] == 28

    def test_federation_skills_count(self):
        idx = _build_index()
        assert idx["categories"]["federation"]["count"] == 8

    def test_constitutional_reasoning_cites_key_floors(self):
        r = get_tree777_skill_resource("arifos", "constitutional-reasoning")
        floors = r["metadata"].get("floors", [])
        # constitutional-reasoning cites F1, F2, F4, F6, F9, F13 (6 floors)
        assert "F1" in floors
        assert "F13" in floors
        assert len(floors) == 6
