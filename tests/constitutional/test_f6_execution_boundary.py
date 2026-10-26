"""F6 P0/P3 — execution-boundary authority guard tests (2026-10-26).

Proves the guard added to `_arif_forge_execute_tool`:
  1. observation modes are out of scope (never blocked),
  2. observe-only (flag off) never blocks but still reports the decision,
  3. enforcing mode blocks a mutating call with no binding (bypass),
  4. enforcing mode blocks a widened scope AFTER approval,
  5. enforcing mode blocks when no state guard exists (UNKNOWN, fail-closed),
  6. enforcing mode blocks when the manifest changed after approval,
  7. enforcing mode allows a binding that passes every execution-time check.

Bounded fixtures; no live surface touched.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

KERNEL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KERNEL_ROOT))

from arifosmcp.runtime.f6.authority_binding import BindingStore, AuthorityBinding  # noqa: E402
from arifosmcp.runtime.f6.execution_boundary import guard_forge_call  # noqa: E402


def _iso(delta_hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=delta_hours)).isoformat(timespec="seconds")


def _binding(scope: str = "repo") -> AuthorityBinding:
    return AuthorityBinding(
        binding_id="bind-1",
        actor_id="333-AGI",
        authority="LIMITED_MUTATE",
        scope=scope,
        allowed_actions=["write:file"],
        resource_patterns=["repo/*"],
        param_constraints={},
        not_before=_iso(-1),
        not_after=_iso(1),
    )


def _manifest(**overrides) -> str:
    data = {
        "f6_binding_id": "bind-1",
        "f6_action": "write:file",
        "f6_resource": "repo/a.py",
        "f6_scope": "repo",
    }
    data.update(overrides)
    return json.dumps(data)


class TestExecutionBoundaryGuard(unittest.TestCase):
    def _store(self, tmp: str) -> BindingStore:
        store = BindingStore(Path(tmp) / "bindings.db")
        store.save(_binding())
        return store

    def test_observation_mode_out_of_scope(self) -> None:
        out = guard_forge_call(mode="query", manifest="", enforce=True)
        self.assertEqual(out["decision"], "NOT_APPLICABLE")
        self.assertFalse(out["blocked"])

    def test_observe_only_never_blocks_missing_binding(self) -> None:
        out = guard_forge_call(mode="write", manifest="{}", enforce=False)
        self.assertEqual(out["decision"], "REJECT_BYPASS")
        self.assertFalse(out["blocked"])
        self.assertFalse(out["enforced"])
        self.assertIn("observe-only", out["reason"])

    def test_enforcing_blocks_missing_binding(self) -> None:
        out = guard_forge_call(mode="write", manifest='{"path": "x"}', enforce=True)
        self.assertEqual(out["decision"], "REJECT_BYPASS")
        self.assertTrue(out["blocked"])

    def test_enforcing_blocks_widened_scope_after_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = guard_forge_call(
                mode="write",
                manifest=_manifest(f6_scope="other-lane"),
                actor_id="333-AGI",
                store=self._store(tmp),
                enforce=True,
            )
            self.assertEqual(out["decision"], "REJECT_SCOPE")
            self.assertTrue(out["blocked"])

    def test_enforcing_blocks_without_state_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = guard_forge_call(
                mode="write",
                manifest=_manifest(),
                actor_id="333-AGI",
                store=self._store(tmp),
                enforce=True,
            )
            self.assertEqual(out["decision"], "UNKNOWN")
            self.assertTrue(out["blocked"])

    def test_enforcing_blocks_manifest_changed_after_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest()
            wrong_hash = hashlib.sha256(b"a different action").hexdigest()
            out = guard_forge_call(
                mode="write",
                manifest=manifest,
                actor_id="333-AGI",
                approved_action_hash=wrong_hash,
                store=self._store(tmp),
                enforce=True,
            )
            self.assertEqual(out["decision"], "REJECT_STATE")
            self.assertTrue(out["blocked"])

    def test_enforcing_allows_bound_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest()
            good_hash = hashlib.sha256(manifest.encode()).hexdigest()
            out = guard_forge_call(
                mode="write",
                manifest=manifest,
                actor_id="333-AGI",
                approved_action_hash=good_hash,
                store=self._store(tmp),
                enforce=True,
            )
            self.assertEqual(out["decision"], "ALLOW")
            self.assertFalse(out["blocked"])
            self.assertTrue(out["enforced"])


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=False)
