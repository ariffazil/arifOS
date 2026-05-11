from __future__ import annotations

from scripts.doctrine_diff_ci import run_checks


def test_k013_doctrine_runtime_parity() -> None:
    errors = run_checks()
    assert errors == []
