"""Unit tests for M1 (_envelope_has_evidence on flat top-level judge/seal envelopes)."""

from __future__ import annotations

import ast
from pathlib import Path

TOOLS_PY = Path(__file__).resolve().parents[1] / "arifosmcp" / "runtime" / "tools.py"


def _load_envelope_has_evidence():
    """Extract and compile _envelope_has_evidence directly without importing heavy runtime."""
    source = TOOLS_PY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_envelope_has_evidence":
            mod = ast.Module(body=[node], type_ignores=[])
            ns = {"Any": object}
            exec(compile(mod, str(TOOLS_PY), "exec"), ns)
            return ns["_envelope_has_evidence"]
    raise AssertionError("_envelope_has_evidence not found in tools.py")


def test_flat_arif_judge_envelope_counts_as_has_evidence() -> None:
    fn = _load_envelope_has_evidence()
    assert fn(
        {
            "verdict": "HOLD",
            "trace_id": "trc-123",
            "constitutional_check": {"hold_required": True, "failed_floors": []},
        }
    ) is True


def test_flat_arif_seal_envelope_counts_as_has_evidence() -> None:
    fn = _load_envelope_has_evidence()
    assert fn({"verdict": "SEAL", "receipt_hash": "sha256:abc"}) is True
    assert fn({"entry_hash": "sha256:def"}) is True
    assert fn({"provenance": {"source": "vault999"}}) is True


def test_nested_result_envelope_preserved() -> None:
    fn = _load_envelope_has_evidence()
    assert fn({"result": {"evidence": ["fact"]}}) is True
    assert fn({"result": {"verdict": "SEAL"}}) is True


def test_naked_error_or_empty_envelope_still_false() -> None:
    fn = _load_envelope_has_evidence()
    assert fn({}) is False
    assert fn({"status": "ERROR", "error": "boom", "result": {}}) is False
    assert fn({"verdict": "HOLD"}) is False
    assert fn("not-a-dict") is False
