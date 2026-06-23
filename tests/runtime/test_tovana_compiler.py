"""
tests/runtime/test_tovana_compiler.py — Tovana belief compiler tests

Phase 3 (2026-06-17): conservative belief compiler for arifOS.

All tests use a temporary memory dir to avoid touching real /root/.arifos/memory.
belief_propose tests require MINIMAX_API_KEY (and use real LLM calls).

DITEMPA BUKAN BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest


def _minimax_key_present() -> bool:
    return bool(os.getenv("MINIMAX_API_KEY"))


_HAS_LLM = _minimax_key_present()


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def temp_memory_dir(monkeypatch, tmp_path):
    """Redirect tovana memory writes to a temp dir."""
    monkeypatch.setenv("TOVANA_MEMORY_DIR", str(tmp_path))
    # Reimport to pick up new env var
    import importlib
    import arifosmcp.runtime.tovana_compiler as tc

    importlib.reload(tc)
    return tmp_path, tc


# ─── Bridge imports ──────────────────────────────────────────────────


class TestBridgeImports:
    def test_compiler_imports(self, temp_memory_dir):
        _, tc = temp_memory_dir
        assert tc.tovana_compiler is not None
        assert hasattr(tc.tovana_compiler, "propose")
        assert hasattr(tc.tovana_compiler, "list")
        assert hasattr(tc.tovana_compiler, "forget")


# ─── Fail-closed tests (no LLM, no network) ──────────────────────────


class TestFailClosed:
    def test_propose_empty_user_id(self, temp_memory_dir):
        _, tc = temp_memory_dir
        result = run(tc.tovana_compiler.propose(user_id="", message="hello"))
        assert result["status"] == "error"
        assert result["verdict"] == "SABAR"

    def test_propose_empty_message(self, temp_memory_dir):
        _, tc = temp_memory_dir
        result = run(tc.tovana_compiler.propose(user_id="arif", message=""))
        assert result["status"] == "error"

    def test_list_no_memories(self, temp_memory_dir):
        _, tc = temp_memory_dir
        result = run(tc.tovana_compiler.list(user_id="nobody"))
        assert result["status"] == "success"
        assert result["verdict"] == "SABAR"
        assert result["memories"] == {}
        assert result["beliefs"] is None

    def test_forget_no_memories(self, temp_memory_dir):
        _, tc = temp_memory_dir
        result = run(tc.tovana_compiler.forget(user_id="nobody"))
        assert result["status"] == "success"
        assert result["deleted"] is False


# ─── File-level behavior (no LLM) ───────────────────────────────────


class TestFileLevel:
    def test_list_returns_stored_memories(self, temp_memory_dir):
        tmp_path, tc = temp_memory_dir
        # Use a simple business name to avoid sanitization issues
        mem_path = tmp_path / "test" / "arif.json"
        mem_path.parent.mkdir(parents=True, exist_ok=True)
        mem_path.write_text(
            json.dumps(
                {
                    "location": "Penang",
                    "preferences": {"favorite_food": "nasi lemak"},
                    "beliefs": "User is based in Penang, Malaysia",
                    "last_updated": "2026-06-17T00:00:00",
                }
            )
        )
        result = run(tc.tovana_compiler.list(user_id="arif", business_description="test"))
        assert result["status"] == "success", f"got {result}"
        assert result["verdict"] == "SEAL", f"got {result}"
        assert result["memories"]["location"] == "Penang"
        assert "Penang" in (result["beliefs"] or "")

    def test_list_triggers_decay_when_ttl_expired(self, temp_memory_dir, monkeypatch):
        monkeypatch.setenv("TOVANA_BELIEF_TTL_DAYS", "0")
        import importlib
        import arifosmcp.runtime.tovana_compiler as tc2

        importlib.reload(tc2)

        tmp_path = Path(os.getenv("TOVANA_MEMORY_DIR", "/tmp"))
        mem_path = tmp_path / "test" / "arif.json"
        mem_path.parent.mkdir(parents=True, exist_ok=True)
        mem_path.write_text(
            json.dumps(
                {
                    "location": "Penang",
                    "beliefs": "stale",
                    "last_updated": "2026-01-01T00:00:00",
                }
            )
        )
        result = run(tc2.tovana_compiler.list(user_id="arif", business_description="test"))
        assert result["status"] == "success"
        assert result["verdict"] == "SABAR"
        assert result.get("decay") is True
        assert result["memories"] == {}

    def test_forget_deletes_file(self, temp_memory_dir):
        tmp_path, tc = temp_memory_dir
        mem_path = tmp_path / "test" / "arif.json"
        mem_path.parent.mkdir(parents=True, exist_ok=True)
        mem_path.write_text(json.dumps({"location": "Penang"}))
        result = run(tc.tovana_compiler.forget(user_id="arif", business_description="test"))
        assert result["status"] == "success", f"got {result}"
        assert result["deleted"] is True
        assert not mem_path.exists()

    def test_user_id_sanitization_blocks_traversal(self, temp_memory_dir):
        tmp_path, tc = temp_memory_dir
        # ../../etc/passwd should be neutralized to a safe path under tmp_path
        result = run(tc.tovana_compiler.list(user_id="../../etc/passwd"))
        # Should not raise, just return empty (no file at the sanitized path)
        assert result["status"] == "success"
        assert result["verdict"] == "SABAR"
        # Should NOT have touched /etc/passwd
        assert Path("/etc/passwd").exists()


# ─── Path-traversal protection ───────────────────────────────────────


class TestUserIdSanitization:
    def test_special_chars_become_underscore(self, temp_memory_dir):
        tmp_path, tc = temp_memory_dir
        # Special chars in user_id should be neutralized
        result = run(tc.tovana_compiler.list(user_id="arif!@#$%^&*()"))
        # The resulting path should be under tmp_path
        assert result["status"] == "success"
        if result.get("memory_path"):
            assert str(Path(result["memory_path"])).startswith(str(tmp_path))


# ─── Live test (LLM extraction, requires MINIMAX_API_KEY) ────────────


@pytest.mark.skipif(not _HAS_LLM, reason="MINIMAX_API_KEY not set")
@pytest.mark.slow
class TestLivePropose:
    """End-to-end: extract memories + beliefs from a real message.
    The tovana_compiler now monkey-patches langchain's JsonOutputParser
    to strip <think> blocks, so this should work with minimax models.
    """

    def test_propose_extracts_location(self, temp_memory_dir):
        _, tc = temp_memory_dir
        result = run(
            tc.tovana_compiler.propose(
                user_id="arif",
                message="I just moved from Penang to KL for work.",
            )
        )
        assert result["status"] == "success", f"got {result}"
        # Tovana should extract at least one memory
        assert result["memories"]
        # At least one of location, previous_location should be present
        assert any(
            k in result["memories"] for k in ("location", "previous_location", "pets", "work")
        )
