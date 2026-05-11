from __future__ import annotations

from core.shared import floor_audit


def test_ml_floor_runtime_disabled(monkeypatch) -> None:
    monkeypatch.delenv("ARIFOS_ML_FLOORS", raising=False)
    floor_audit._probe_ml_embedding_runtime.cache_clear()
    floor_audit._load_sbert_runtime.cache_clear()

    runtime = floor_audit.get_ml_floor_runtime()

    assert runtime["ml_floors_enabled"] is False
    assert runtime["ml_hold_state"] == "disabled"
    assert runtime["ml_dependency_status"] == "disabled"


def test_ml_floor_runtime_hold_when_dependencies_missing(monkeypatch) -> None:
    monkeypatch.setenv("ARIFOS_ML_FLOORS", "1")
    floor_audit._probe_ml_embedding_runtime.cache_clear()
    floor_audit._load_sbert_runtime.cache_clear()
    monkeypatch.setattr(
        floor_audit,
        "_missing_ml_dependencies",
        lambda: ["sentence_transformers", "torch"],
    )

    runtime = floor_audit.get_ml_floor_runtime()

    assert runtime["ml_floors_enabled"] is True
    assert runtime["ml_runtime_ready"] is False
    assert runtime["ml_hold_state"] == "hold"
    assert runtime["ml_dependency_status"] == "missing_dependencies"
    assert runtime["ml_missing_dependencies"] == ["sentence_transformers", "torch"]
