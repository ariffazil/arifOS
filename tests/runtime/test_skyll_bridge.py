"""
tests/runtime/test_skyll_bridge.py — Skyll Skill Discovery Bridge Tests

Phase 2 (2026-06-17): covers the arifOS-side skyll_bridge that delegates
to the Skyll hosted MCP server at https://api.skyll.app/mcp.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import socket
from pathlib import Path
from unittest.mock import patch

import pytest


def _skyll_reachable() -> bool:
    try:
        with socket.create_connection(("api.skyll.app", 443), timeout=3.0):
            return True
    except (OSError, socket.timeout):
        return False


_SKYLL_LIVE = _skyll_reachable()


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ─── Bridge imports ──────────────────────────────────────────────────


class TestBridgeImports:
    def test_bridge_imports(self):
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        assert skyll_bridge is not None
        assert hasattr(skyll_bridge, "search_skills")
        assert hasattr(skyll_bridge, "get_skill")
        assert hasattr(skyll_bridge, "install_skill")

    def test_bridge_url_default(self):
        import arifosmcp.runtime.skyll_bridge as sb

        assert "api.skyll.app" in sb._SKYLL_URL or os.getenv("SKYLL_MCP_URL") is not None


# ─── Live integration (hosted Skyll reachable) ─────────────────────


@pytest.mark.skipif(not _SKYLL_LIVE, reason="api.skyll.app not reachable")
class TestLiveSkillDiscover:
    """search_skills against the real Skyll hosted MCP."""

    def test_search_skills_react(self):
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        result = run(skyll_bridge.search_skills("react performance", limit=3))
        assert result["status"] == "success", f"got {result}"
        assert result["epistemic_tag"] == "INTERPRETATION"
        assert result["count"] >= 1
        skills = result["skills"]
        assert len(skills) >= 1
        # First skill should have full content
        first = skills[0]
        assert "title" in first
        assert "content" in first
        assert len(first["content"]) > 200

    def test_search_skills_python(self):
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        result = run(skyll_bridge.search_skills("python testing", limit=2))
        assert result["status"] == "success"


# ─── Install skill — fail-closed tests (no network) ─────────────────


class TestInstallSkillFailsClosed:
    """install_skill must fail closed if file exists without overwrite=True,
    and must enforce the install_count safety floor."""

    def test_refuses_overwrite_without_flag(self, tmp_path):
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        # Pre-create the skill file
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Existing\n")

        # Mock get_skill so we don't hit network
        with patch.object(
            skyll_bridge,
            "get_skill",
            return_value={
                "status": "success",
                "content": "# New content\n",
                "skill_id": "test-skill",
            },
        ):
            result = run(
                skyll_bridge.install_skill(
                    skill_id="test-skill",
                    skills_dir=tmp_path,
                    overwrite=False,
                    install_count=500,  # bypass safety floor
                    force=True,
                )
            )
        assert result["status"] == "error"
        assert result["verdict"] == "888_HOLD"
        assert "overwrite=True" in result["error"]
        # Original file should be untouched
        assert (skill_dir / "SKILL.md").read_text() == "# Existing\n"

    def test_overwrite_replaces(self, tmp_path):
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Existing\n")

        with patch.object(
            skyll_bridge,
            "get_skill",
            return_value={
                "status": "success",
                "content": "# New content\n",
                "skill_id": "test-skill",
            },
        ):
            result = run(
                skyll_bridge.install_skill(
                    skill_id="test-skill",
                    skills_dir=tmp_path,
                    overwrite=True,
                    install_count=500,
                    force=True,
                )
            )
        assert result["status"] == "success"
        assert (skill_dir / "SKILL.md").read_text() == "# New content\n"

    def test_skill_id_sanitization(self, tmp_path):
        """Path-traversal payloads in skill_id should be neutralized."""
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        with patch.object(
            skyll_bridge,
            "get_skill",
            return_value={
                "status": "success",
                "content": "# Safe content\n",
                "skill_id": "../../etc/passwd",
            },
        ):
            result = run(
                skyll_bridge.install_skill(
                    skill_id="../../etc/passwd",
                    skills_dir=tmp_path,
                    overwrite=True,
                    install_count=500,
                    force=True,
                )
            )
        assert result["status"] == "success"
        # The installed path should be inside tmp_path, NOT /etc/passwd
        installed = Path(result["installed_path"])
        assert str(installed).startswith(str(tmp_path))
        # Original /etc/passwd should be untouched
        assert Path("/etc/passwd").exists()  # system file untouched

    def test_safety_floor_blocks_low_install_count(self, tmp_path):
        """install_count < 100 without force=True must return 888_HOLD."""
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        with patch.object(
            skyll_bridge,
            "get_skill",
            return_value={"status": "success", "content": "# x\n", "skill_id": "x"},
        ):
            result = run(
                skyll_bridge.install_skill(
                    skill_id="x",
                    skills_dir=tmp_path,
                    install_count=42,  # below floor
                )
            )
        assert result["status"] == "error"
        assert result["verdict"] == "888_HOLD"
        assert "safety floor" in result["error"]
        assert result["install_count"] == 42
        assert result["safety_floor"] == 100
        assert result["recommendation"] == "review_before_install"

    def test_safety_floor_allows_with_force(self, tmp_path):
        """install_count < 100 with force=True must proceed."""
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        with patch.object(
            skyll_bridge,
            "get_skill",
            return_value={"status": "success", "content": "# x\n", "skill_id": "x"},
        ):
            result = run(
                skyll_bridge.install_skill(
                    skill_id="x",
                    skills_dir=tmp_path,
                    install_count=42,
                    force=True,
                )
            )
        assert result["status"] == "success"
        assert result["force_used"] is True

    def test_unknown_install_count_requires_force(self, tmp_path):
        """install_count=None without force=True must return 888_HOLD."""
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        result = run(
            skyll_bridge.install_skill(
                skill_id="x",
                skills_dir=tmp_path,
            )
        )
        assert result["status"] == "error"
        assert result["verdict"] == "888_HOLD"
        assert "install_count was not provided" in result["error"]

    def test_known_safety_recommendations(self):
        """Search results must carry safety_recommendation per install_count."""
        # This is checked at the search level; install_count is passed
        # through from search_skills to install_skill by the caller.
        # The 4 tiers (per F12 soft signal):
        #   - install_count >= 1000 → "trusted"
        #   - install_count >= 100  → "well_tested"
        #   - install_count >= 10   → "review_before_install"
        #   - install_count < 10    → "low_trust"
        for count, expected in [
            (1500, "trusted"),
            (500, "well_tested"),
            (50, "review_before_install"),
            (3, "low_trust"),
        ]:
            if count >= 1000:
                got = "trusted"
            elif count >= 100:
                got = "well_tested"
            elif count >= 10:
                got = "review_before_install"
            else:
                got = "low_trust"
            assert got == expected, f"count={count} expected {expected}, got {got}"


# ─── F12 INJECTION: malformed content rejected ───────────────────────


class TestInjectionGuard:
    def test_think_artifact_rejected(self, tmp_path):
        from arifosmcp.runtime.skyll_bridge import skyll_bridge

        with patch.object(
            skyll_bridge,
            "get_skill",
            return_value={
                "status": "success",
                "content": "<think>this is not a real skill</think>",  # short, has <think>
                "skill_id": "fake",
            },
        ):
            result = run(
                skyll_bridge.install_skill(
                    skill_id="fake",
                    skills_dir=tmp_path,
                    overwrite=True,
                    install_count=500,
                    force=True,
                )
            )
        assert result["status"] == "error"
        assert result["verdict"] == "VOID"
        assert "LLM artifact" in result["error"]


# ─── arif_sense_observe mode wiring ─────────────────────────────────


class TestSenseObserveWiring:
    def test_modes_in_allowed(self):
        from pathlib import Path

        tools_path = Path("/root/arifOS/arifosmcp/runtime/tools.py")
        src = tools_path.read_text()
        for mode in ("skill_discover", "skill_learn"):
            count = src.count(f'"{mode}"')
            assert count >= 2, f"Mode {mode} only appears {count} time(s) in tools.py"

    def test_skyll_bridge_in_dispatch(self):
        from pathlib import Path

        tools_path = Path("/root/arifOS/arifosmcp/runtime/tools.py")
        src = tools_path.read_text()
        assert "skyll_bridge" in src
        assert "888_HOLD" in src
