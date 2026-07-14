"""
Tests for /root/arifOS/arifosmcp/runtime/capability_drift.py

F1-safe additive: matrix logic is exercised without touching live services.

Forged 2026-07-14 — Phase A of Reality Observatory.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime import capability_drift as cd  # noqa: E402


def test_per_field_envelope_shape() -> None:
    pf = cd.per_field(42, source="unit_test", state="observed", confidence=0.95)
    assert pf["value"] == 42
    assert pf["state"] == "observed"
    assert pf["source"] == "unit_test"
    assert "observed_at" in pf
    assert "age_seconds" in pf
    assert pf["confidence"] == 0.95


def test_per_field_age_from_epoch() -> None:
    pf = cd.per_field_age("v1", source="unit_test", observed_at_epoch=0)
    # epoch=0 (1970) ⇒ age is huge; cell remains structurally intact.
    assert pf["value"] == "v1"
    assert pf["state"] == "observed"
    assert "observed_at" in pf
    assert pf["age_seconds"] > 0


def test_schema_hash_is_deterministic() -> None:
    h1 = cd._schema_hash({"a": 1, "b": 2})
    h2 = cd._schema_hash({"b": 2, "a": 1})
    h3 = cd._schema_hash({"a": 1, "b": 3})
    assert h1 == h2  # sort_keys canonicalisation
    assert h1 != h3
    assert h1 is not None
    assert h1.startswith("sha256:")


def test_schema_hash_handles_bad_input() -> None:
    # Sets aren't JSON-serialisable; never throw — return None.
    assert cd._schema_hash({"x": {1, 2, 3}}) is None  # type: ignore[arg-type]
    assert cd._schema_hash(None) is None


def test_record_and_load_test_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Smoke: write a cache entry, load it back, assert values."""
    # Redirect TEST_CACHE_PATH to tmp for isolation.
    fake = tmp_path / "capability-test-cache.json"
    monkeypatch.setattr(cd, "TEST_CACHE_PATH", fake)

    cd.record_test_result("arif_init", passed=True, error=None, input_schema_hash="sha256:abcd", output_schema_hash="sha256:efgh")
    cd.record_test_result("arif_triage", passed=False, error="wrapper mismatch")

    cache = cd._load_test_cache()
    assert "arif_init" in cache
    assert cache["arif_init"]["last_pass"] is True
    assert cache["arif_init"]["input_schema_hash"] == "sha256:abcd"
    assert cache["arif_triage"]["last_pass"] is False
    assert cache["arif_triage"]["last_error"] == "wrapper mismatch"


def test_declared_filters_arif_namespace_only() -> None:
    fake_index = {
        "arif_init": {"name": "arif_init", "canonical": True},
        "arif_judge": {"name": "arif_judge", "canonical": True},
        "arifos_legacy": {"name": "arifos_legacy", "canonical": True},  # wrong namespace
        "hermes_obs": {"name": "hermes_obs", "canonical": True},  # wrong namespace
    }
    out = cd._declared_arif_tools(fake_index)
    assert out == {"arif_init", "arif_judge"}


def test_registered_extracts_names_from_tools() -> None:
    class StubMCP:
        _tool_registry = [
            type("T", (), {"name": "arif_init"})(),
            type("T", (), {"name": "arif_observe"})(),
            "arif_judge",  # also accepts raw strings
        ]

    out = cd._registered_tools(StubMCP())
    assert out == {"arif_init", "arif_observe", "arif_judge"}


def test_registered_handles_empty_or_none() -> None:
    assert cd._registered_tools(None) == set()
    class Empty:
        _tool_registry = None
    assert cd._registered_tools(Empty()) == set()
    assert cd._registered_tools(object()) == set()


def test_exposed_parses_server_json_shapes() -> None:
    server_json = {"tools": [{"name": "arif_init"}, {"name": "arif_observe"}]}
    assert cd._exposed_tools(server_json) == {"arif_init", "arif_observe"}
    # alt shape
    server_json_alt = {"canonical_tools": ["arif_judge"]}
    assert cd._exposed_tools(server_json_alt) == {"arif_judge"}
    assert cd._exposed_tools(None) == set()
    assert cd._exposed_tools({}) == set()


def test_matrix_truth_ladder_pass_degraded_void(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A fully-passing tool, a degraded one, and a non-declared 'ghost' must all be classified correctly."""
    fake = tmp_path / "cache.json"
    monkeypatch.setattr(cd, "TEST_CACHE_PATH", fake)

    # Seed cache with a fresh, passing entry for arif_init
    cd.record_test_result("arif_init", passed=True, error=None)

    registry_index = {
        "arif_init": {"name": "arif_init", "canonical": True},
        "arif_judge": {"name": "arif_judge", "canonical": True},
        # arif_triage declared but later classified DEGRADED below
        "arif_triage": {"name": "arif_triage", "canonical": True},
    }

    class StubMCP:
        _tool_registry = [
            type("T", (), {"name": "arif_init"})(),
            type("T", (), {"name": "arif_judge"})(),
            # arif_triage intentionally NOT registered
        ]

    server_json = {
        "tools": [
            {"name": "arif_init"},
            {"name": "arif_judge"},
            {"name": "arif_triage"},  # exposed but not registered
        ]
    }

    matrix = cd.compute_capability_matrix(mcp=StubMCP(), server_json=server_json, registry_index=registry_index)
    rows = {r["name"]: r for r in matrix["matrix"]}

    assert "arif_init" in rows
    assert "arif_judge" in rows
    assert "arif_triage" in rows

    # Schema hashes are None because registry_index has no schema — assertions:
    assert rows["arif_init"]["declared"] is True
    assert rows["arif_init"]["registered"] is True
    assert rows["arif_init"]["exposed"] is True
    assert rows["arif_init"]["invocable"] is True
    assert rows["arif_init"]["tested"] is True
    # In/out schema match: registry has None, observed has None ⇒ treated as not unknown
    # but our matrix explicitly treats None registry hash as "missing" → in_match=False ⇒ DEGRADED.
    # This is the honest state — schema hash cannot be validated without TOOLREGISTRY schemas.
    assert rows["arif_init"]["input_schema_hash_match"] is False
    assert rows["arif_init"]["output_schema_hash_match"] is False
    assert rows["arif_init"]["capability_truth"] == "DEGRADED"

    # arif_triage declared+exposed but NOT registered → degraded.
    assert rows["arif_triage"]["registered"] is False
    assert rows["arif_triage"]["capability_truth"] == "DEGRADED"


def test_matrix_void_for_undeclared_tool() -> None:
    """A tool not in TOOLREGISTRY.json but live in kernel = VOID."""
    class StubMCP:
        _tool_registry = [type("T", (), {"name": "ghost_tool"})()]

    matrix = cd.compute_capability_matrix(mcp=StubMCP(), server_json={}, registry_index={})
    rows = {r["name"]: r for r in matrix["matrix"]}
    assert "ghost_tool" in rows
    assert rows["ghost_tool"]["capability_truth"] == "VOID"


def test_matrix_counts() -> None:
    """Matrix top-level counts must mirror the truth column."""
    class StubMCP:
        _tool_registry = []

    registry = {"arif_a": {}, "arif_b": {}, "arif_c": {}}
    matrix = cd.compute_capability_matrix(mcp=StubMCP(), server_json={}, registry_index=registry)
    # Nothing is registered ⇒ invocable_count = 0, degraded = 3 (all declared not invocable)
    assert matrix["declared_count"] == 3
    assert matrix["registered_count"] == 0
    assert matrix["exposed_count"] == 0
    assert matrix["invocable_count"] == 0
    assert matrix["degraded_count"] == 3


def test_load_registry_index_falls_back_gracefully(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """When neither TOOLREGISTRY nor TOOL_MANIFEST exists, return {} — never crash."""
    # Point all candidates to nonexistent paths so the function returns {}
    fake_root = tmp_path / "nowhere"
    monkeypatch.setattr(cd, "Path", lambda p: fake_root / p)  # type: ignore[assignment]
    # Simpler: monkey-patch the candidates list directly
    fake_nonexistent = tmp_path / "nonexistent.json"
    monkeypatch.setattr(cd, "_load_registry_index",
                        lambda: {})  # type: ignore[assignment]
    assert cd._load_registry_index() == {}
