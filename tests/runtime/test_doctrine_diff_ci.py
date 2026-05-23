from __future__ import annotations
from pathlib import Path

import pytest

from commands.scripts.doctrine_diff_ci import run_checks


def test_k013_doctrine_runtime_parity() -> None:
    """Verify doctrine files match runtime. Skip if K013 charter file is absent (deployment gap)."""
    if not Path("000/ROOT/K013_LANGUAGE_GOVERNANCE.md").exists():
        pytest.skip(
            "000/ROOT/K013_LANGUAGE_GOVERNANCE.md not found — constitutional charter file missing"
        )
    errors = run_checks()
    assert errors == []
