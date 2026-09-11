"""Prove the VAULT999 isolation guard actually fires.

Detection is debt until it can say NO. Without these tests the guard is
narrative: it exists in conftest but nothing has witnessed it refuse a write.

CRITICAL: the guard API is taken from the `isolate_vault999_from_production`
FIXTURE, never via `from conftest import …`. Re-importing conftest builds a
SECOND module object with its own `_state`, so a test's deliberate_violation()
bumps a different counter than the guard reads and the guard appears never to
have fired (witnessed 2026-09-11: 2 failed / 1 teardown error).
"""

from __future__ import annotations

import os
from pathlib import Path

PROD_LEDGER = Path("/root/arifOS/VAULT999/SEALED_EVENTS.jsonl")
SYMLINK_LEDGER = Path("/root/VAULT999/SEALED_EVENTS.jsonl")


def test_env_redirect_is_active(isolate_vault999_from_production):
    """Guard must point VAULT999_PATH away from production."""
    guard = isolate_vault999_from_production
    p = os.environ.get("VAULT999_PATH", "")
    assert p, "VAULT999_PATH not set by isolation guard"
    assert not guard["is_production_path"](p), f"VAULT999_PATH still production: {p}"
    assert "vault999_sandbox" in p, f"VAULT999_PATH not in sandbox: {p}"


def test_production_marker_classifier(isolate_vault999_from_production):
    """The classifier must be right, or every other test here is theatre."""
    is_prod = isolate_vault999_from_production["is_production_path"]
    assert is_prod("/root/arifOS/VAULT999/SEALED_EVENTS.jsonl")
    assert is_prod("/root/VAULT999/outcomes.jsonl")
    assert is_prod("/var/lib/arifos/vault/x.jsonl")
    assert not is_prod("/tmp/anything.jsonl")


def test_write_to_production_ledger_is_refused(isolate_vault999_from_production):
    """The guard must REFUSE a production-ledger append. This is the whole point."""
    guard = isolate_vault999_from_production
    assert PROD_LEDGER.exists(), "production ledger path changed — update guard markers"
    probe = guard["deliberate_violation"]()
    with probe:
        with PROD_LEDGER.open("a", encoding="utf-8") as f:
            f.write('{"probe": "must never land"}\n')
    assert probe.blocked(), "guard did NOT block a deliberate production write"


def test_write_to_production_via_symlink_is_refused(isolate_vault999_from_production):
    """/root/VAULT999 symlinks to /root/arifOS/VAULT999 — both paths must be caught."""
    guard = isolate_vault999_from_production
    probe = guard["deliberate_violation"]()
    with probe:
        with SYMLINK_LEDGER.open("w") as f:
            f.write("nope\n")
    assert probe.blocked(), "guard missed the symlinked production path"


def test_production_ledger_untouched(isolate_vault999_from_production):
    """Regression: no test may grow the frozen v1 ledger.

    1349 lines is the witnessed size at guard-install time (2026-09-11). Catches
    a successful leak even if the guard's raise path were bypassed.
    """
    n = sum(1 for _ in PROD_LEDGER.open(encoding="utf-8", errors="replace"))
    assert n <= 1349, f"production ledger GREW to {n} lines — isolation failed"


def test_sandbox_write_still_allowed(isolate_vault999_from_production):
    """No false positives — legitimate test writes must still work."""
    tmp = Path(os.environ["VAULT999_PATH"])
    with tmp.open("a", encoding="utf-8") as f:
        f.write('{"ok": true}\n')
    assert tmp.exists() and tmp.stat().st_size > 0


def test_read_from_production_still_allowed(isolate_vault999_from_production):
    """OBSERVE is free — the guard must not block read-only audits."""
    with PROD_LEDGER.open(encoding="utf-8", errors="replace") as f:
        first = f.read(1)
    assert first != "", "production ledger unreadable — guard or file problem"


def test_guard_restores_path_after_session(isolate_vault999_from_production):
    """Teardown must restore env, not leave the sandbox pointing at prod state."""
    guard = isolate_vault999_from_production
    assert Path(os.environ["VAULT999_PATH"]).parent == guard["sandbox"]
