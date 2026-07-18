"""The external emitter must delegate to the canonical snapshot builder."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "emit_observatory_snapshot.py"
SPEC = importlib.util.spec_from_file_location("emit_observatory_snapshot", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_emitter_uses_canonical_builder_with_public_registration_set() -> None:
    expected = {"snapshot_id": "obs_test", "signature": {"state": "signed"}}
    with patch.object(MODULE, "build_snapshot", return_value=expected) as builder:
        actual = MODULE.build_observatory()

    assert actual is expected
    assert builder.call_args.args == (None,)
    assert builder.call_args.kwargs["registered_tools"] == set(MODULE.PUBLIC_CANONICAL_TOOLS)
