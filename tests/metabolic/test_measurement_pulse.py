"""
Thermodynamic pulse + SEAL_PROMPT enforcement — kernel tests.

Doctrine: LLM teka. Agentic uji. Lepas pintu, baru jadi.
Forged 2026-07-09 — Grok Build harden pass.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from arifosmcp.prompts import measurement as m


@pytest.fixture()
def isolated_registries(tmp_path, monkeypatch):
    """Redirect shadow + canon registries to tmp so tests never touch live files."""
    shadow = tmp_path / "entropy_registry.shadow.jsonl"
    canon = tmp_path / "entropy_registry.jsonl"
    monkeypatch.setattr(m, "SHADOW_REGISTRY_PATH", shadow)
    monkeypatch.setattr(m, "REGISTRY_PATH", canon)
    monkeypatch.setattr(m, "REGISTRY_DIR", tmp_path)
    monkeypatch.setenv("ARIFOS_DRY_RUN", "1")
    yield {"shadow": shadow, "canon": canon, "tmp": tmp_path}


def test_shannon_entropy_known():
    h = m.shannon_entropy(["SEAL", "SEAL", "HOLD", "SEAL", "VOID"])
    assert 1.3 < h < 1.5


def test_js_divergence_symmetric_bounded():
    p = {"SEAL": 0.8, "HOLD": 0.2}
    q = {"SEAL": 0.5, "HOLD": 0.5}
    js = m.js_divergence(p, q)
    assert 0.0 <= js <= 1.0
    assert abs(js - m.js_divergence(q, p)) < 1e-9


def test_tool_surface_hash_order_invariant():
    a = m.compute_tool_surface_hash(["b", "a", "c"])
    b = m.compute_tool_surface_hash(["c", "a", "b"])
    assert a == b
    assert len(a) == 64


def test_measure_seal_writes_shadow(isolated_registries):
    metrics = m.measure_seal(
        {
            "verdict": "SEAL",
            "session_id": "t-shadow",
            "actor": "test",
            "epoch": "2026-07-09T00:00:00Z",
            "violated_floors": [],
            "tool_surface_hash_start": "aa" * 32,
            "tool_surface_hash_end": "bb" * 32,
        },
        pre_state={"tools": ["x", "y", "x"]},
        post_state={"tools": ["x", "x", "x"]},
        dry_run=True,
    )
    assert metrics["dry_run"] is True
    assert metrics["delta_s"] < 0  # entropy reduced
    assert isolated_registries["shadow"].exists()
    lines = isolated_registries["shadow"].read_text().strip().splitlines()
    assert len(lines) == 1
    assert not isolated_registries["canon"].exists() or isolated_registries["canon"].read_text() == ""


def test_hold_without_violated_floors_f11(isolated_registries):
    metrics = m.measure_seal(
        {
            "verdict": "HOLD",
            "session_id": "t-hold",
            "actor": "test",
            "epoch": "2026-07-09T00:00:00Z",
            "violated_floors": [],
        },
        dry_run=True,
    )
    assert metrics["f11_breach"] == "violated_floors_required_for_HOLD"
    pulse = m.summary_line(metrics)
    assert "ΔS" in pulse or "DS" in pulse or "ΔS" in pulse or "[" in pulse


def test_promote_shadow_scar_matches_int_no_typeerror(isolated_registries):
    """Regression: scar_matches is int from measure_seal; promote must not len(int)."""
    shadow: Path = isolated_registries["shadow"]
    for i in range(3):
        entry = {
            "delta_s": -0.01,
            "js_vs_baseline": 0.02,
            "violated_floors": [],
            "scar_matches": 0,  # INT — the bug case
            "verdict": "SEAL",
        }
        with open(shadow, "a") as f:
            f.write(json.dumps(entry) + "\n")
    n = m.promote_shadow(force=False)
    assert n == 3
    assert not shadow.exists()
    assert isolated_registries["canon"].exists()
    assert len(isolated_registries["canon"].read_text().strip().splitlines()) == 3


def test_promote_blocked_wrong_count(isolated_registries):
    shadow: Path = isolated_registries["shadow"]
    with open(shadow, "w") as f:
        f.write(json.dumps({"delta_s": 0, "js_vs_baseline": 0, "violated_floors": [], "scar_matches": 0}) + "\n")
    assert m.promote_shadow(force=False) == 0
    assert shadow.exists()


def test_attach_thermodynamic_pulse_on_result(isolated_registries):
    result = {
        "status": "OK",
        "verdict": "SEAL",
        "session_id": "t-attach",
        "entry_id": "e1",
    }
    payload = json.dumps(
        {
            "verdict": "SEAL",
            "violated_floors": [],
            "tool_surface_hash_start": "a" * 64,
            "tool_surface_hash_end": "b" * 64,
            "pre_state": {"tools": ["t1", "t2"]},
            "post_state": {"tools": ["t1", "t1"]},
        }
    )
    out = m.attach_thermodynamic_pulse(
        result, session_id="t-attach", actor_id="grok", payload=payload, dry_run=True
    )
    assert "thermodynamic_pulse" in out
    assert "thermodynamic_metrics" in out
    assert out["thermodynamic_metrics"]["dry_run"] is True
    assert out.get("thermodynamic_pulse_error") is None


def test_seal_prompt_enforcement_blocks():
    """9 content checks on SEAL_PROMPT + INIT tool_surface_hash_start."""
    from arifosmcp.prompts import SEAL_PROMPT, INIT_PROMPT

    checks = {
        "violated_floors WAJIB": "violated_floors" in SEAL_PROMPT and "WAJIB" in SEAL_PROMPT,
        "tool_surface_hash_start": "tool_surface_hash_start" in SEAL_PROMPT,
        "tool_surface_hash_end": "tool_surface_hash_end" in SEAL_PROMPT,
        "THERMODYNAMIC PULSE": "THERMODYNAMIC PULSE" in SEAL_PROMPT,
        "measure_seal": "measure_seal" in SEAL_PROMPT,
        "F11 AUDIT": "F11" in SEAL_PROMPT,
        "shadow / DRY": "shadow" in SEAL_PROMPT or "ARIFOS_DRY_RUN" in SEAL_PROMPT,
        "ΔS or Shannon": "ΔS" in SEAL_PROMPT or "Shannon" in SEAL_PROMPT,
        "HOLD null reject": "HOLD" in SEAL_PROMPT and "null" in SEAL_PROMPT,
        "INIT hash start": "tool_surface_hash_start" in INIT_PROMPT,
    }
    failed = [k for k, v in checks.items() if not v]
    assert not failed, f"content checks failed: {failed}"
