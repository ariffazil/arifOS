"""S3 regression — ONE response, ONE meaning for allowed_next_verbs (2026-09-22).

Defect pinned (live, OBS 2026-09-22 ~21:00 MYT, session via arif_init+arif_judge):

    result.seal_allowed             = False
    result.allowed_next_verbs       = [6 verbs — no forge/seal/stage]   (state view)
    allowed_next_verbs (root)       = [9 verbs — incl arif_seal]        (band view)

One envelope, two authorities for the same field name. An agent reading the root
advertises arif_seal while the same envelope says seal_allowed=false — the S4
"verb admitted whose precondition is false" seam.

The law after the fix:
  * `allowed_next_verbs` (root AND result) = the session-state view.
  * The band REPETOIRE stays available in the signed token's act_claims.allowed —
    AUTHORITY_VERBS[LIMITED_MUTATE] legitimately contains arif_seal (safe modes
    OBSERVE; mode=seal gates at L6 inside the tool). Repertoire ≠ next-verbs.
  * When the result carries no state view, the band fill remains (unchanged).
  * Empty state view ([] = nothing allowed) must propagate as [], not resurrect
    the band list — fail-closed, never fail-open.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from arifosmcp.runtime.act_token import derive_verbs, echo_canonical_session

BAND = "LIMITED_MUTATE"
BAND_VERBS = derive_verbs(BAND)
STATE_VERBS = ["arif_init", "arif_observe", "arif_think", "arif_route", "arif_memory", "arif_judge"]


def _echo(response: dict) -> dict:
    return echo_canonical_session(
        response,
        session_id="SEAL-s3-regression",
        actor_id="FI-003",
        autonomy_band=BAND,
    )


def test_root_mirrors_state_view_when_result_carries_one():
    resp = {
        "result": {
            "seal_allowed": False,
            "mutation_allowed": False,
            "allowed_next_verbs": list(STATE_VERBS),
        }
    }
    out = _echo(resp)
    assert out["allowed_next_verbs"] == STATE_VERBS
    # the contradiction must not survive: no arif_seal advertised while sealed=false
    assert "arif_seal" not in out["allowed_next_verbs"]
    assert out["result"]["allowed_next_verbs"] == out["allowed_next_verbs"]


def test_root_falls_back_to_band_when_result_has_no_state_view():
    resp = {"result": {"seal_allowed": False}}
    out = _echo(resp)
    assert out["allowed_next_verbs"] == BAND_VERBS


def test_preexisting_root_is_preserved_when_result_has_no_state_view():
    pre = ["arif_init", "arif_observe"]
    resp = {"allowed_next_verbs": list(pre), "result": {"note": "no verbs here"}}
    out = _echo(resp)
    assert out["allowed_next_verbs"] == pre


def test_empty_state_view_propagates_fail_closed():
    """[] means nothing is allowed next — the band list must not resurrect."""
    resp = {"result": {"allowed_next_verbs": []}}
    out = _echo(resp)
    assert out["allowed_next_verbs"] == []


def test_band_repertoire_still_reachable_in_claims():
    """Repertoire is NOT deleted — it lives in the signed claims."""
    assert "arif_seal" in BAND_VERBS  # AUTHORITY_VERBS[LIMITED_MUTATE] design intact


if __name__ == "__main__":  # pragma: no cover
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
