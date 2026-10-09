#!/usr/bin/env python3
"""
clarity_carry.py dict-guard regression tests (2026-09-12 canary event).

The bug: emit_carry_forward() treated any non-list payload on CARRY_PATH as
"corrupted" and replaced it with a fresh one-element array — destroying the
v2 generational dict (arifos.carry_forward.v2) on every arif_seal. Fired
twice on 2026-09-12 (08:28Z quarantined manually, 09:14:13Z witnessed live).

The guard: dict payload → entry diverted to sidecar JSONL ledger, canonical
file byte-untouched.

Import is by file-path (importlib) so no arifosmcp package side-effects.
Run: python3 /root/arifOS/tests/runtime/test_clarity_carry.py  (or via pytest)
"""

import importlib.util
import json
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "clarity_carry_under_test", "/root/arifOS/arifosmcp/runtime/clarity_carry.py"
)
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)

V2_DICT = {
    "schema": "arifos.carry_forward.v2",
    "generation": {"gen_id": "gen-test"},
    "sessions": [{"session_id": "s1", "open_loops": []}],
    "open_loops": [],
}


def _patch(tmp: str):
    cc.CARRY_PATH = os_path = f"{tmp}/carry_forward.json"
    cc.CLARITY_LEDGER_PATH = f"{tmp}/carry_forward.clarity_ledger.jsonl"
    return os_path


def test_dict_guard_preserves_v2_and_diverts():
    with tempfile.TemporaryDirectory() as tmp:
        cf = _patch(tmp)
        Path(cf).write_text(json.dumps(V2_DICT), encoding="utf-8")
        before = Path(cf).read_bytes()

        ret = cc.emit_carry_forward(
            "arif_vault_seal", "SEAL-testdict00", "tester", "L1-L2", {"entry_id": "e-dict"}
        )

        assert ret == cc.CLARITY_LEDGER_PATH, f"expected sidecar path, got {ret}"
        assert Path(cf).read_bytes() == before, "canonical v2 dict was MODIFIED — guard failed"
        lines = Path(cc.CLARITY_LEDGER_PATH).read_text().strip().splitlines()
        assert len(lines) == 1, f"sidecar lines={len(lines)}"
        entry = json.loads(lines[0])
        assert entry["action"] == "arif_vault_seal" and entry["receipt"]["entry_id"] == "e-dict"


def test_list_format_still_appends():
    with tempfile.TemporaryDirectory() as tmp:
        cf = _patch(tmp)
        Path(cf).write_text(json.dumps([{"ts": 1.0, "action": "old"}]), encoding="utf-8")

        ret = cc.emit_carry_forward(
            "arif_vault_seal", "SEAL-testlist00", "tester", "L1", {"entry_id": "e-list"}
        )

        assert ret == cf, f"expected canonical path, got {ret}"
        data = json.loads(Path(cf).read_text())
        assert isinstance(data, list) and len(data) == 2
        assert data[-1]["receipt"]["entry_id"] == "e-list"
        backups = list(Path(tmp, "carry_forward_backups").glob("carry_forward-*.json"))
        assert backups, "stamped backup not written on list-path write"


def test_missing_file_creates_list():
    with tempfile.TemporaryDirectory() as tmp:
        cf = _patch(tmp)
        ret = cc.emit_carry_forward("arif_init", "SEAL-testnew000", "tester", "L1", {"entry_id": "e-new"})
        assert ret == cf
        data = json.loads(Path(cf).read_text())
        assert isinstance(data, list) and len(data) == 1


def test_malformed_file_never_destroyed():
    with tempfile.TemporaryDirectory() as tmp:
        cf = _patch(tmp)
        Path(cf).write_text("{not json", encoding="utf-8")
        before = Path(cf).read_bytes()
        ret = cc.emit_carry_forward("arif_seal", "SEAL-testbad000", "tester", "L1", {"entry_id": "e-bad"})
        assert ret == "carry_forward_failed"
        assert Path(cf).read_bytes() == before, "malformed file was modified"


if __name__ == "__main__":
    import sys

    cases = [
        test_dict_guard_preserves_v2_and_diverts,
        test_list_format_still_appends,
        test_missing_file_creates_list,
        test_malformed_file_never_destroyed,
    ]
    failed = 0
    for fn in cases:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {fn.__name__}: {exc}")
    print(f"{len(cases) - failed}/{len(cases)} pass")
    sys.exit(1 if failed else 0)
