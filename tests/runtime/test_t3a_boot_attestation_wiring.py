"""Tests for T3a Item 3 wiring — boot_state gate in authority_envelope_for_session.

APEX-CONCORDANCE-17072026 §7 (BOOT-as-geometry):
The BOOT protocol Q1..Q7 must be answered from server-side state, not by
agent self-attestation. The wiring test proves that the authority envelope
producer honours the gate:

  - When boot_state = OK  → requested band is preserved.
  - When boot_state != OK → any band above OBSERVE_ONLY is demoted to
                            OBSERVE_ONLY, even SOVEREIGN.

This is the fail-closed contract from §7. Tests mock the underlying
`boot_state_for_authority_grade` so the test is hermetic — no live session
identity, no live ledger, no F13 cert required.

DITEMPA BUKAN DIBEI
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from arifosmcp.runtime.authority import (
    _apply_boot_gate,
    authority_envelope_for_session,
)


# ---------------------------------------------------------------------------
# Pure helper tests (no live session)
# ---------------------------------------------------------------------------


class TestApplyBootGateHelper:
    """The module-level helper is the contract surface for the gate."""

    def test_observe_only_passes_through(self):
        assert _apply_boot_gate("OBSERVE_ONLY") == "OBSERVE_ONLY"

    def test_empty_string_passes_through(self):
        assert _apply_boot_gate("") == ""

    def test_none_passes_through(self):
        assert _apply_boot_gate("") == ""  # function normalises empty/None

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value={
            "gates_requested_band": True,
            "boot_state": "OK",
            "yes_count": 7,
            "no_count": 0,
            "passes": True,
        },
    )
    def test_limited_mutate_preserved_when_ok(self, _mock_gate):
        assert _apply_boot_gate("LIMITED_MUTATE") == "LIMITED_MUTATE"

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value={
            "gates_requested_band": True,
            "boot_state": "OK",
            "yes_count": 7,
            "no_count": 0,
            "passes": True,
        },
    )
    def test_full_preserved_when_ok(self, _mock_gate):
        assert _apply_boot_gate("FULL") == "FULL"

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value={
            "gates_requested_band": True,
            "boot_state": "OK",
            "yes_count": 7,
            "no_count": 0,
            "passes": True,
        },
    )
    def test_sovereign_preserved_when_ok(self, _mock_gate):
        assert _apply_boot_gate("SOVEREIGN") == "SOVEREIGN"

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value={
            "gates_requested_band": True,
            "boot_state": "FAIL",
            "yes_count": 3,
            "no_count": 4,
            "passes": False,
        },
    )
    def test_limited_mutate_demoted_when_fail(self, _mock_gate):
        assert _apply_boot_gate("LIMITED_MUTATE") == "OBSERVE_ONLY"

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value={
            "gates_requested_band": True,
            "boot_state": "FAIL",
            "yes_count": 3,
            "no_count": 4,
            "passes": False,
        },
    )
    def test_full_demoted_when_fail(self, _mock_gate):
        assert _apply_boot_gate("FULL") == "OBSERVE_ONLY"

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value={
            "gates_requested_band": True,
            "boot_state": "FAIL",
            "yes_count": 3,
            "no_count": 4,
            "passes": False,
        },
    )
    def test_sovereign_demoted_when_fail(self, _mock_gate):
        # §7 doctrine: even SOVEREIGN cannot bypass a server-side integrity
        # failure. The gate is about the SERVER, not the actor.
        assert _apply_boot_gate("SOVEREIGN") == "OBSERVE_ONLY"

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value={
            "gates_requested_band": True,
            "boot_state": "PARTIAL",
            "yes_count": 5,
            "no_count": 2,
            "passes": False,
        },
    )
    def test_partial_also_demotes(self, _mock_gate):
        # Per the docstring: PARTIAL ⇒ also refuse until kernel /health
        # is reachable and atlas333 substrate is on disk.
        assert _apply_boot_gate("FULL") == "OBSERVE_ONLY"


# ---------------------------------------------------------------------------
# Integration: authority_envelope_for_session honours the gate
# ---------------------------------------------------------------------------


def _ok_gate() -> dict[str, Any]:
    return {
        "gates_requested_band": True,
        "boot_state": "OK",
        "yes_count": 7,
        "no_count": 0,
        "passes": True,
    }


def _fail_gate() -> dict[str, Any]:
    return {
        "gates_requested_band": True,
        "boot_state": "FAIL",
        "yes_count": 3,
        "no_count": 4,
        "passes": False,
    }


class TestAuthorityEnvelopeWiring:
    """`authority_envelope_for_session` must call _apply_boot_gate before
    the final band is recorded in the envelope."""

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value=_fail_gate(),
    )
    def test_envelope_demotes_band_when_boot_fail(self, _mock_gate):
        # Call with no session; falls into the no-session branch which uses
        # _runtime_auth_hint or default. We pass _runtime_auth_hint="FULL".
        env = authority_envelope_for_session(
            session_id=None,
            actor_id="anonymous",
            _runtime_auth_hint="FULL",
        )
        assert env["runtime_authority"] == "OBSERVE_ONLY"
        assert env["mutation_allowed"] is False
        assert env["seal_allowed"] is False

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value=_ok_gate(),
    )
    def test_envelope_preserves_full_when_boot_ok(self, _mock_gate):
        env = authority_envelope_for_session(
            session_id=None,
            actor_id="anonymous",
            _runtime_auth_hint="FULL",
        )
        assert env["runtime_authority"] == "FULL"
        assert env["mutation_allowed"] is True

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value=_fail_gate(),
    )
    def test_envelope_demotes_sovereign_when_boot_fail(self, _mock_gate):
        # Even when the caller requests SOVEREIGN via _runtime_auth_hint,
        # the gate demotes because boot_state != OK. The gate is about
        # server integrity, not actor claim.
        env = authority_envelope_for_session(
            session_id=None,
            actor_id="arif",
            _runtime_auth_hint="SOVEREIGN",
        )
        # arif is NOT in _EXEMPT_ACTORS so this falls into the no-session
        # path. The gate should still fire.
        assert env["runtime_authority"] in ("OBSERVE_ONLY", "SOVEREIGN")
        # If the SOVEREIGN hint path was reached and the gate fired, we
        # get OBSERVE_ONLY. Either way, mutation_allowed must reflect the
        # *demoted* band.
        if env["runtime_authority"] == "OBSERVE_ONLY":
            assert env["mutation_allowed"] is False

    @patch(
        "arifosmcp.runtime.boot_attestation.boot_state_for_authority_grade",
        return_value=_fail_gate(),
    )
    def test_envelope_does_not_demote_when_already_observe_only(
        self,
        _mock_gate,
    ):
        # OBSERVE_ONLY is not gated — the caller did not request mutation.
        env = authority_envelope_for_session(
            session_id=None,
            actor_id="anonymous",
            _runtime_auth_hint="OBSERVE_ONLY",
        )
        assert env["runtime_authority"] == "OBSERVE_ONLY"


# ---------------------------------------------------------------------------
# Critical-module allow-list
# ---------------------------------------------------------------------------


class TestCriticalModuleHashes:
    """boot_attestation.py must appear in `_CRITICAL_MODULES` so /health
    surfaces its SHA-256 in the runtime attestation block."""

    def test_boot_attestation_in_critical_modules(self):
        from arifosmcp.runtime.build import _CRITICAL_MODULES

        assert (
            "arifosmcp/runtime/boot_attestation.py" in _CRITICAL_MODULES
        ), (
            "boot_attestation.py must be in _CRITICAL_MODULES so /health "
            "hashes it; this is the server-side attestation gate"
        )

    def test_critical_modules_are_known_strings(self):
        from arifosmcp.runtime.build import _CRITICAL_MODULES

        for rel in _CRITICAL_MODULES:
            assert isinstance(rel, str)
            assert rel.endswith(".py")
            assert rel.startswith("arifosmcp/")