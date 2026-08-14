"""
VAULT999 Notary — test suite
Tests:
  1. sign_outcome produces valid HMAC stub
  2. Clean chain → verification passes
  3. Tampered outcome → verification fails
  4. Chain break (missing prev_hash) → verification fails
  5. Key permission enforcement (0600 check)
"""

import hashlib
import hmac
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/root/arifOS")

from arifosmcp.runtime.vault999_notary import (
    sign_outcome,
    verify_chain,
    canonical,
    SPEC_VERSION,
    _ensure_key,
)

PASSED = "✅"
FAILED = "❌"
passed = 0
failed = 0


def assert_(condition: bool, msg: str) -> None:
    global passed, failed
    if condition:
        print(f"  {PASSED} {msg}")
        passed += 1
    else:
        print(f"  {FAILED} {msg}")
        failed += 1


def make_temp_env():
    """Create temp environment for isolated testing."""
    tmpdir = tempfile.mkdtemp(prefix="notary-test-")
    outcomes_path = Path(tmpdir) / "outcomes.jsonl"
    sig_path = Path(tmpdir) / "outcomes.sig.jsonl"
    key_path = Path(tmpdir) / "test.key"
    return tmpdir, outcomes_path, sig_path, key_path


def test_sign_and_verify_clean():
    print("\n[TEST 1] sign_outcome produces valid HMAC stub + clean chain passes")

    tmpdir, outcomes_path, sig_path, key_path = make_temp_env()
    try:
        # Patch paths
        import arifosmcp.runtime.vault999_notary as mod

        orig_outcomes = mod.OUTCOMES_PATH
        orig_sig = mod.SIG_PATH
        orig_key = mod.KEY_PATH
        mod.OUTCOMES_PATH = outcomes_path
        mod.SIG_PATH = sig_path
        mod.KEY_PATH = key_path

        # Write test outcomes
        outcomes = [
            {"decision_id": "d1", "verdict": "SEAL", "timestamp": "2026-08-14T00:00:00Z"},
            {"decision_id": "d2", "verdict": "HOLD", "timestamp": "2026-08-14T00:01:00Z"},
            {"decision_id": "d3", "verdict": "SEAL", "timestamp": "2026-08-14T00:02:00Z"},
        ]
        with outcomes_path.open("w") as f:
            for o in outcomes:
                f.write(json.dumps(o) + "\n")

        # Sign each
        for i, o in enumerate(outcomes):
            sig = sign_outcome(o, i + 1)
            assert_("signature" in sig, f"seq {i + 1}: signature present")
            assert_(len(sig["signature"]) == 64, f"seq {i + 1}: signature is 64 hex chars")
            assert_(sig["spec"] == SPEC_VERSION, f"seq {i + 1}: spec matches")

        # Verify clean chain
        valid, errors, warnings = verify_chain(1, 3)
        assert_(valid is True, f"clean chain is valid (errors={errors})")
        assert_(len(errors) == 0, f"no errors (got {len(errors)})")

        # Restore
        mod.OUTCOMES_PATH = orig_outcomes
        mod.SIG_PATH = orig_sig
        mod.KEY_PATH = orig_key
    finally:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)


def test_tampered_outcome():
    print("\n[TEST 2] Tampered outcome → verification fails")

    tmpdir, outcomes_path, sig_path, key_path = make_temp_env()
    try:
        import arifosmcp.runtime.vault999_notary as mod

        orig_outcomes = mod.OUTCOMES_PATH
        orig_sig = mod.SIG_PATH
        orig_key = mod.KEY_PATH
        mod.OUTCOMES_PATH = outcomes_path
        mod.SIG_PATH = sig_path
        mod.KEY_PATH = key_path

        # Write original outcomes and sign
        original = {"decision_id": "d1", "verdict": "SEAL"}
        with outcomes_path.open("w") as f:
            f.write(json.dumps(original) + "\n")

        sig = sign_outcome(original, 1)
        with sig_path.open("w") as f:
            f.write(json.dumps(sig) + "\n")

        # Verify — should pass
        valid, errors, _ = verify_chain(1, 1)
        assert_(valid is True, "original verifies")

        # Tamper with outcome
        tampered = {"decision_id": "d1", "verdict": "VOID"}  # Changed verdict
        with outcomes_path.open("w") as f:
            f.write(json.dumps(tampered) + "\n")

        # Verify — should fail
        valid, errors, _ = verify_chain(1, 1)
        assert_(valid is False, "tampered outcome fails verification")
        assert_(any("mismatch" in e for e in errors), f"error mentions mismatch: {errors}")

        mod.OUTCOMES_PATH = orig_outcomes
        mod.SIG_PATH = orig_sig
        mod.KEY_PATH = orig_key
    finally:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)


def test_chain_break():
    print("\n[TEST 3] Chain break (modified prev_hash) → verification fails")

    tmpdir, outcomes_path, sig_path, key_path = make_temp_env()
    try:
        import arifosmcp.runtime.vault999_notary as mod

        orig_outcomes = mod.OUTCOMES_PATH
        orig_sig = mod.SIG_PATH
        orig_key = mod.KEY_PATH
        mod.OUTCOMES_PATH = outcomes_path
        mod.SIG_PATH = sig_path
        mod.KEY_PATH = key_path

        # Write 2 outcomes and sign
        o1 = {"v": 1}
        o2 = {"v": 2}
        with outcomes_path.open("w") as f:
            f.write(json.dumps(o1) + "\n")
            f.write(json.dumps(o2) + "\n")

        s1 = sign_outcome(o1, 1)
        s2 = sign_outcome(o2, 2)

        # Tamper s2's prev_hash
        s2_bad = dict(s2)
        s2_bad["prev_hash"] = "deadbeef" * 8

        with sig_path.open("w") as f:
            f.write(json.dumps(s1) + "\n")
            f.write(json.dumps(s2_bad) + "\n")

        valid, errors, _ = verify_chain(1, 2)
        assert_(valid is False, "chain break detected")
        assert_(any("chain break" in e for e in errors), f"error mentions chain break: {errors}")

        mod.OUTCOMES_PATH = orig_outcomes
        mod.SIG_PATH = orig_sig
        mod.KEY_PATH = orig_key
    finally:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)


def test_key_permission():
    print("\n[TEST 4] Key permission enforcement (0600)")

    tmpdir = tempfile.mkdtemp(prefix="notary-key-test-")
    try:
        import arifosmcp.runtime.vault999_notary as mod

        orig_key = mod.KEY_PATH
        key_path = Path(tmpdir) / "bad.key"

        # Create key with wrong permissions
        key_path.write_text("testkey123")
        key_path.chmod(0o644)  # Wrong!

        mod.KEY_PATH = key_path

        try:
            _ensure_key()
            assert_(False, "should have raised PermissionError for 0644")
        except PermissionError as e:
            assert_("0o600" in str(e), f"permission error mentions 0600: {e}")

        # Fix permissions
        key_path.chmod(0o600)
        try:
            _ensure_key()
            assert_(True, "0600 permissions accepted")
        except PermissionError:
            assert_(False, "0600 should be accepted")

        mod.KEY_PATH = orig_key
    finally:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)


def test_canonical_deterministic():
    print("\n[TEST 5] canonical() is deterministic")

    obj = {"b": 2, "a": 1, "c": {"z": 3, "y": 4}}
    j1 = canonical(obj)
    j2 = canonical(obj)
    assert_(j1 == j2, "same object → same JSON")

    # Keys should be sorted
    assert_(j1.startswith('{"a":'), f"keys sorted: starts with 'a': {j1[:20]}")

    # Different insertion order → same result
    obj2 = {"c": {"y": 4, "z": 3}, "a": 1, "b": 2}
    j3 = canonical(obj2)
    assert_(j1 == j3, "different insertion order → same canonical JSON")


def main():
    global passed, failed
    print("=== VAULT999 Notary Tests ===")

    try:
        test_sign_and_verify_clean()
        test_tampered_outcome()
        test_chain_break()
        test_key_permission()
        test_canonical_deterministic()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\n=== RESULTS: {passed} passed, {failed} failed ===")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
