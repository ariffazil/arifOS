"""
tests/test_item2_invert_verify_gate.py — Item 2 acceptance tests.

Forged 2026-07-18 by kimi-code (FI-008) per sovereign (888) directive.

Acceptance tests (per sovereign ruling, 2026-07-18):
  1. Anonymous caller can invoke arif_seal mode=verify → ADMIT.
  2. Anonymous caller can invoke arif_seal mode=chain → ADMIT.
  3. Anonymous caller can invoke arif_seal mode=list → ADMIT.
  4. Anonymous caller can invoke arif_seal mode=dry_run → ADMIT.
  5. Anonymous caller CANNOT invoke arif_seal mode=seal → HOLD_888.
  6. Anonymous caller CANNOT invoke arif_seal mode=unknown → HOLD_888.
  7. Presentation modes (seal_card, render) → ADMIT for anonymous.
  8. SOVEREIGN caller invoking seal → ADMIT (unchanged behavior).

The fix inverts the verify gate:
  read modes (verify/chain/list/dry_run) → LOW authority, NONE mutation,
  no 888_hold required.
  presentation modes (seal_card/render) → MEDIUM.
  write mode (seal) → unchanged: SOVEREIGN + IRREVERSIBLE.

DITEMPA BUKAN DIBERI — forged, not given.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from arifosmcp.kernel.interceptor import (
    _effective_arif_seal_flags,
)
from arifosmcp.kernel.models import (
    AuthorityTier,
    MutationClass,
)


# ─── fixtures ────────────────────────────────────────────────────────────────


@dataclass
class FakeCap:
    """Mirror of CapabilityNode for the arif_seal profile."""

    capability_id: str = "kernel.seal"
    tool_name: str = "arif_seal"
    authority_required: AuthorityTier = AuthorityTier.SOVEREIGN
    irreversible: bool = True
    requires_888_hold: bool = True
    mutation_class: MutationClass = MutationClass.IRREVERSIBLE
    blast_radius: object = None
    resource_class: object = None
    organ_id: str = "arifOS"


@dataclass
class FakeReq:
    arguments: dict
    tool_name: str = "arif_seal"
    actor_id: str | None = None
    session_id: str | None = None


@pytest.fixture
def cap():
    return FakeCap()


# ─── Acceptance Test 1: helper logic for each mode ──────────────────────────


class TestEffectiveArifSealFlags:
    """The mode-aware override returns the right effective profile."""

    @pytest.mark.parametrize(
        "mode,expected_auth,expected_irr,expected_888,expected_mut",
        [
            # Read modes → LOW authority, NONE mutation, no 888_hold
            ("verify", AuthorityTier.LOW, False, False, MutationClass.NONE),
            ("chain", AuthorityTier.LOW, False, False, MutationClass.NONE),
            ("list", AuthorityTier.LOW, False, False, MutationClass.NONE),
            ("dry_run", AuthorityTier.LOW, False, False, MutationClass.NONE),
            # Presentation modes → MEDIUM authority
            ("seal_card", AuthorityTier.MEDIUM, False, False, MutationClass.NONE),
            ("render", AuthorityTier.MEDIUM, False, False, MutationClass.NONE),
            # Write mode → unchanged (SOVEREIGN + IRREVERSIBLE)
            ("seal", AuthorityTier.SOVEREIGN, True, True, MutationClass.IRREVERSIBLE),
            # Unknown mode → defaults to write profile (safe)
            ("unknown", AuthorityTier.SOVEREIGN, True, True, MutationClass.IRREVERSIBLE),
            ("", AuthorityTier.SOVEREIGN, True, True, MutationClass.IRREVERSIBLE),
        ],
    )
    def test_each_mode_returns_correct_profile(
        self, cap, mode, expected_auth, expected_irr, expected_888, expected_mut
    ):
        req = FakeReq(arguments={"mode": mode})
        auth, irr, h888, mut = _effective_arif_seal_flags(req, cap)

        assert auth == expected_auth, (
            f"mode={mode!r}: expected {expected_auth.value}, got {auth.value}"
        )
        assert irr is expected_irr, (
            f"mode={mode!r}: expected irreversible={expected_irr}, got {irr}"
        )
        assert h888 is expected_888, (
            f"mode={mode!r}: expected requires_888_hold={expected_888}, got {h888}"
        )
        assert mut == expected_mut, (
            f"mode={mode!r}: expected mutation_class={expected_mut.value}, got {mut.value}"
        )

    def test_missing_mode_defaults_to_seal_profile(self, cap):
        """If mode is not passed at all, default to seal profile (safe)."""
        req = FakeReq(arguments={})
        auth, irr, h888, mut = _effective_arif_seal_flags(req, cap)

        assert auth == AuthorityTier.SOVEREIGN
        assert irr is True
        assert h888 is True
        assert mut == MutationClass.IRREVERSIBLE

    def test_non_arif_seal_capability_passes_through(self, cap):
        """Non-arif_seal tools should not be affected by the helper."""
        cap.tool_name = "other_tool"
        req = FakeReq(arguments={"mode": "verify"})
        auth, irr, h888, mut = _effective_arif_seal_flags(req, cap)

        # Should return capability's declared values, not the mode override
        assert auth == AuthorityTier.SOVEREIGN
        assert irr is True
        assert h888 is True


# ─── Acceptance Test 2: FLOOR gate integration (anonymity) ─────────────────


class TestAnonymousReadModesAdmitted:
    """An anonymous caller should be admitted for read modes.

    We verify this by checking that the EFFECTIVE authority_required is LOW
    for read modes. An anonymous caller's resolved authority tier is MEDIUM
    (per the existing transport-verification floor in _resolve_authority),
    which is >= LOW — so the FLOOR 7 authority check passes.

    Note: full integration test of the interceptor requires the full
    _resolve_authority setup, which is exercised in the live kernel. The
    helper-level test below proves the FLOOR 7 prerequisite is met.
    """

    @pytest.mark.parametrize(
        "mode",
        ["verify", "chain", "list", "dry_run"],
    )
    def test_read_mode_effective_authority_is_low(self, cap, mode):
        """LOW authority requirement means anonymous (MEDIUM-tier) can pass FLOOR 7."""
        req = FakeReq(arguments={"mode": mode})
        auth, _, _, _ = _effective_arif_seal_flags(req, cap)
        assert auth == AuthorityTier.LOW

    def test_presentation_mode_effective_authority_is_medium(self, cap):
        """MEDIUM authority requirement means anonymous can pass FLOOR 7."""
        for mode in ["seal_card", "render"]:
            req = FakeReq(arguments={"mode": mode})
            auth, _, _, _ = _effective_arif_seal_flags(req, cap)
            assert auth == AuthorityTier.MEDIUM


# ─── Acceptance Test 3: write mode stays gated ─────────────────────────────


class TestWriteModeStillGated:
    """mode=seal (and unknown) must keep SOVEREIGN gate."""

    @pytest.mark.parametrize("mode", ["seal", "unknown", ""])
    def test_seal_mode_requires_sovereign(self, cap, mode):
        """Anonymous cannot write the vault; SOVEREIGN required."""
        req = FakeReq(arguments={"mode": mode})
        auth, irr, h888, mut = _effective_arif_seal_flags(req, cap)

        # Write profile: SOVEREIGN + IRREVERSIBLE + 888_hold + IRREVERSIBLE mutation
        assert auth == AuthorityTier.SOVEREIGN
        assert irr is True
        assert h888 is True
        assert mut == MutationClass.IRREVERSIBLE

    def test_sovereign_actor_can_still_seal(self, cap):
        """SOVEREIGN actor + seal mode = ADMIT (unchanged behavior)."""
        req = FakeReq(
            arguments={"mode": "seal"},
            actor_id="arif",
        )
        auth, irr, h888, mut = _effective_arif_seal_flags(req, cap)

        # Effective requirements match declared SOVEREIGN — SOVEREIGN actor passes
        assert auth == AuthorityTier.SOVEREIGN


# ─── Acceptance Test 4: case-insensitivity ──────────────────────────────────


class TestModeCaseInsensitivity:
    """Mode matching should be case-insensitive (per vault.py L26 literal)."""

    @pytest.mark.parametrize(
        "mode",
        ["VERIFY", "Chain", "LIST", "Dry_Run", "Seal_Card"],
    )
    def test_uppercase_modes_still_resolve(self, cap, mode):
        req = FakeReq(arguments={"mode": mode})
        auth, _, _, _ = _effective_arif_seal_flags(req, cap)
        # Should NOT be the seal profile (SOVEREIGN)
        assert auth != AuthorityTier.SOVEREIGN, (
            f"Uppercase mode {mode!r} should resolve to read/presentation, "
            f"not default to seal profile."
        )
