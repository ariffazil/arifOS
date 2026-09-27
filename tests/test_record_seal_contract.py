"""RECORD_SEAL contract tests — red before the class exists, green after.

F13 build order 2026-09-27 ("bina RECORD_SEAL"). Contract:
/root/forge_work/2026-09-27-RECORD-SEAL-CONTRACT.md

A bounded grant level that lets a registered, cryptographically-bound
non-sovereign actor append a RECORD to VAULT999 under a sovereign-issued
verdict — without gaining arif_forge, arif_judge, or any floor waiver.

Test discipline (scar SCAR-2026-09-27-AFORGE-SENSOR-TAMPER-001, C6): a gate
counts only once a negative control proves it can fail. Tests marked RED must
fail today; if one passes today, the property already holds and it is reported
as pre-existing rather than counted as delivered.
"""

from __future__ import annotations

import pytest

from arifosmcp.schemas.kernel_envelope import RuntimeGrantLevel
from arifosmcp.runtime.act_token import compute_authority_state, identity_band_authority

RECORD_SEAL = "RECORD_SEAL"


def _grant(band: str | None) -> dict:
    """A verified, non-sovereign harness session (the fi-003 shape measured live
    on 2026-09-27), with an optional pre-selected authority band.
    compute_authority_state returns a dict, not the AuthorityState model."""
    state = compute_authority_state(
        actor_id="fi-003",
        actor_verified=True,
        signature_verified=True,
        is_sovereign_principal=False,
        session_id="SEAL-contract-test",
        session_bound=True,
        actor_bound=True,
        authority_band=band,
        verification_method="ed25519",
        verification_reason="key_pairs_with_registry",
    )
    return state["runtime_grant"]


# ── RED: the class does not exist yet ───────────────────────────────────────


def test_record_seal_is_a_first_class_grant_level():
    """RECORD_SEAL must be in the canonical ontology, not a string that appears
    in one file and is rejected by the validator in another."""
    assert RECORD_SEAL in {m.value for m in RuntimeGrantLevel}, (
        "RuntimeGrantLevel has no RECORD_SEAL — a band string accepted by one "
        "gate and rejected by another is the dual-source-envelope defect of "
        "STAB-2026-08-09 repeating."
    )


def test_record_seal_may_seal_records():
    grant = _grant(RECORD_SEAL)
    assert grant["level"] == RECORD_SEAL, (
        f"band {RECORD_SEAL} did not survive derivation: got {grant['level']!r}"
    )
    assert grant["seal_allowed"] is True, "RECORD_SEAL must allow arif_seal"


def test_record_seal_verbs_are_strictly_narrower_than_limited_mutate():
    """The point of the class: append without the actuator and without the bench.
    LIMITED_MUTATE already lists arif_forge and arif_judge, so RECORD_SEAL must
    be a narrower verb set with only seal widened — otherwise it is FULL renamed."""
    limited = set(_grant(None)["allowed_verbs"])
    grant = set(_grant(RECORD_SEAL)["allowed_verbs"])
    assert "arif_seal" in grant
    leaked = {"arif_forge", "arif_judge", "arif_act"} & grant
    assert not leaked, f"RECORD_SEAL must not grant {sorted(leaked)}"
    assert grant < limited, (
        f"RECORD_SEAL verbs {sorted(grant)} are not a strict subset of LIMITED_MUTATE"
    )


# ── GREEN now and after: non-regression invariants ─────────────────────────


def test_identity_alone_never_reaches_full():
    """STAB-2026-08-09: verified non-sovereign stays bounded. A verified key is
    identity, not authority."""
    assert identity_band_authority(
        actor_verified=True, signature_verified=True, is_sovereign_principal=False
    ) != "FULL"


def test_record_seal_is_not_reachable_by_identity_alone():
    """RECORD_SEAL must come from a registry grant, never from presenting a good
    signature. Otherwise every registered warga key self-issues permanence."""
    band = identity_band_authority(
        actor_verified=True, signature_verified=True, is_sovereign_principal=False
    )
    assert band != RECORD_SEAL, (
        "identity verification alone granted RECORD_SEAL — the class has no "
        "admission control"
    )


def test_unverified_actor_still_cannot_seal_under_record_seal():
    """An unverified actor requesting RECORD_SEAL must land OBSERVE_ONLY: the
    band is a ceiling, and the gate is still identity-bound."""
    grant = compute_authority_state(
        actor_id="fi-003",
        actor_verified=False,
        signature_verified=False,
        is_sovereign_principal=False,
        session_id="SEAL-contract-test",
        session_bound=True,
        actor_bound=True,
        authority_band=RECORD_SEAL,
    )["runtime_grant"]
    assert grant["seal_allowed"] is False, (
        "an unverified session was granted append authority"
    )


def test_unknown_band_does_not_silently_widen_to_mutable():
    """C2 in the grant layer: an unrecognised band string is unknown, and unknown
    must not resolve to a capability. Measured 2026-09-27: authority_band
    "RECORD_SEAL" (nonexistent at the time) normalized to LIMITED_MUTATE, which
    carries arif_forge — a typo in a band name yielded mutation authority."""
    grant = _grant("NOT_A_REAL_BAND")
    assert grant["level"] not in ("LIMITED_MUTATE", "FULL"), (
        f"unknown band silently widened to {grant['level']!r}"
    )
    assert grant["mutation_allowed"] is False and grant["seal_allowed"] is False


@pytest.mark.skip(reason="T4-T8 (verdict-store validation, payload binding, single-use, "
                         "self_deploy rejection) land with the authority-site map; the "
                         "band gate preempts every external probe today — measured "
                         "2026-09-27: all four fabricated-reference seals refused with "
                         "\"not allowed for authority level 'OBSERVE_ONLY'\"")
def test_fabricated_verdict_reference_is_refused_for_the_right_reason():
    raise NotImplementedError
