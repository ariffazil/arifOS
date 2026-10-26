"""Capability matrix: schema-hash match must be TRI-STATE (2026-10-26).

Measured defect: `input_schema_hash_match`/`output_schema_hash_match` were
booleans computed as `observed is not None and registry is not None and
observed == registry`. Two different realities collapsed into `false`:

  * both sides present and DIFFERENT   → a real mismatch (act on it)
  * observed side missing              → never measured (run a test)

Live evidence 2026-10-26, /var/lib/arifos/observatory/capability-test-cache.json:
every public verb except arif_init carried `input_schema_hash: null`, so every
row published `*_hash_match: false` — the surface said "capability DRIFTED"
about measurements nobody had taken. `false` is a claim; `null` is the truth.
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime import capability_drift as cd


def _registry() -> dict[str, dict[str, Any]]:
    schema = {"type": "object", "properties": {"x": {"type": "string"}}}
    return {
        "arif_init": {"input_schema": schema, "output_schema": schema},
        "arif_judge": {"input_schema": schema, "output_schema": schema},
        "arif_think": {"input_schema": schema, "output_schema": schema},
    }


def _matrix(monkeypatch, cache: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    monkeypatch.setattr(cd, "_load_test_cache", lambda: cache)
    monkeypatch.setattr(cd, "hydrate_test_cache_from_durable_bus", lambda **_: 0)
    reg = _registry()
    names = set(reg)
    out = cd.compute_capability_matrix(
        None, None, registry_index=reg, registered_tools=names, live_exposed=names
    )
    return {row["name"]: row for row in out["matrix"]}


def test_missing_observed_hash_is_unknown_not_mismatch(monkeypatch) -> None:
    rows = _matrix(monkeypatch, {"arif_init": {"last_pass": True, "last_invocation_at": 0}})
    row = rows["arif_init"]
    assert row["input_schema_hash_match"] is None
    assert row["output_schema_hash_match"] is None


def test_recorded_equal_hash_is_true(monkeypatch) -> None:
    reg = _registry()
    h = cd._schema_hash(reg["arif_judge"]["input_schema"])
    rows = _matrix(
        monkeypatch,
        {
            "arif_judge": {
                "last_pass": True,
                "input_schema_hash": h,
                "output_schema_hash": h,
            }
        },
    )
    row = rows["arif_judge"]
    assert row["input_schema_hash_match"] is True
    assert row["output_schema_hash_match"] is True


def test_recorded_different_hash_is_false(monkeypatch) -> None:
    rows = _matrix(
        monkeypatch,
        {
            "arif_think": {
                "last_pass": True,
                "input_schema_hash": "sha256:deadbeefdeadbeef",
                "output_schema_hash": "sha256:deadbeefdeadbeef",
            }
        },
    )
    row = rows["arif_think"]
    assert row["input_schema_hash_match"] is False
    assert row["output_schema_hash_match"] is False


def test_unknown_match_still_cannot_reach_pass(monkeypatch) -> None:
    """Fail-closed is unchanged: unknown is not a pass."""
    rows = _matrix(monkeypatch, {"arif_init": {"last_pass": True, "last_invocation_at": 0}})
    assert rows["arif_init"]["capability_truth"] != "PASS"
