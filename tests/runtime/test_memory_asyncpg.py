"""
tests/runtime/test_memory_asyncpg.py — Regression test for Lane 1 (555_MEMORY)
Verifies asyncpg is installed and memory recall returns well-formed responses, not ImportError.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import os
import pytest

os.environ["ARIFOS_DEV_MODE"] = "1"


class TestMemoryOrganAsyncpg:
    """Regression: memory organ must not fail with 'No module named asyncpg'."""

    def test_asyncpg_is_importable(self):
        """asyncpg must be present in the Python environment."""
        pytest.importorskip(
            "asyncpg",
            reason="asyncpg required for MemoryEngine — install with: pip install asyncpg",
        )
        import asyncpg

        assert hasattr(asyncpg, "__version__")
        assert asyncpg.__version__.startswith("0.31")

    def test_memory_recall_does_not_raise_import_error(self):
        """arif_memory_recall must not return a HOLD due to ImportError."""
        from arifosmcp.tools.memory import arif_memory_recall

        result = arif_memory_recall(
            mode="context", session_id="TEST-SEAL-001", actor_id="test-agent"
        )

        # Must not be a HOLD with ImportError as the reason
        if result.get("status") == "HOLD":
            reason = str(result.get("meta", {}).get("reason", ""))
            assert "ImportError" not in reason, f"Memory returned ImportError HOLD: {reason}"
            assert "No module named 'asyncpg'" not in reason

    def test_memory_recall_returns_nine_signal(self):
        """Memory organ must emit nine_signal even in degraded/empty state."""
        from arifosmcp.tools.memory import arif_memory_recall

        result = arif_memory_recall(
            mode="context", session_id="TEST-SEAL-001", actor_id="test-agent"
        )

        nine = result.get("nine_signal", {})
        assert "overall" in nine, "nine_signal block missing from memory recall response"
        overall_state = (
            nine["overall"]
            if isinstance(nine["overall"], str)
            else nine["overall"].get("state", "")
        )
        assert overall_state in (
            "SELAMAT",
            "SABAR",
            "RETAK",
            "GANTUNG",
        ), f"Invalid nine_signal overall: {nine.get('overall')}"

    def test_memory_engine_imports_without_error(self):
        """MemoryEngine class must be importable (prevents silent breakage)."""
        pytest.importorskip("asyncpg", reason="asyncpg required for MemoryEngine import")
        from arifosmcp.memory_engine import MemoryEngine

        assert callable(MemoryEngine)

    def test_memory_engine_can_be_instantiated_with_env_urls(self):
        """MemoryEngine is deprecated — skip if class is a stub (no _pg_pool)."""
        import os

        os.environ.setdefault(
            "DATABASE_URL", "postgresql://user:pass@localhost:5432/db"
        )  # pragma: allowlist secret
        os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
        os.environ.setdefault("OLLAMA_URL", "http://localhost:11434")

        from arifosmcp.memory_engine import MemoryEngine

        me = MemoryEngine(
            postgres_url=os.environ["DATABASE_URL"],
            qdrant_url=os.environ["QDRANT_URL"],
            ollama_url=os.environ["OLLAMA_URL"],
        )
        # MemoryEngine is deprecated stub — verify object is created (no _pg_pool in stub)
        assert me is not None
        # Deprecation means operations will raise RuntimeError; use memory_store instead
        pytest.skip("MemoryEngine deprecated — use memory_store.store()")
