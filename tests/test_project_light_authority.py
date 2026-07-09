"""
test_project_light_authority.py — amanah single-source authority at session birth.

Guards the dual-source bug where session_birth.authority_mode was SOVEREIGN
whenever actor_verified=True while top-level authority stayed LIMITED_MUTATE.
Also guards arif_act leak into allowed_next_verbs (public name is arif_forge).

DITEMPA BUKAN DIBERI — 2026-07-09.
"""

from __future__ import annotations

from arifosmcp.tools.session import _project_light


def _components() -> dict:
    return {
        "alignment_profile": {"loaded": True},
        "adversarial_profile": {"loaded": True},
        "belief": {"intent_model": {"status": "ok"}},
        "next": {"recommended_next": "arif_observe"},
    }


def test_unverified_birth_matches_observe_only():
    header = _project_light(
        _components(),
        sid="SEAL-test-unverified",
        actor_id="anon",
        constitution_hash="sha256:deadbeef",
        actor_verified=False,
    )
    birth = header["session_birth"]
    assert header["authority"] == "OBSERVE_ONLY"
    assert birth["authority_mode"] == header["authority"]
    assert birth["verdict"] == header["authority"]
    assert birth["actor_verified"] is False
    assert birth["mutation_allowed"] is False
    assert "arif_act" not in header["allowed_next_verbs"]
    assert "arif_forge" not in header["allowed_next_verbs"]
    assert "arif_seal" not in header["allowed_next_verbs"]


def test_verified_without_override_is_limited_not_sovereign():
    """actor_verified alone must NOT mint SOVEREIGN/FULL on session_birth."""
    header = _project_light(
        _components(),
        sid="SEAL-test-limited",
        actor_id="arif",
        constitution_hash="sha256:deadbeef",
        actor_verified=True,
        # no authority_override → LIMITED_MUTATE
    )
    birth = header["session_birth"]
    assert header["authority"] == "LIMITED_MUTATE"
    assert birth["authority_mode"] == "LIMITED_MUTATE"
    assert birth["verdict"] == "LIMITED_MUTATE"
    assert birth["authority_mode"] != "SOVEREIGN"
    assert birth["mutation_allowed"] is True
    assert "arif_forge" in header["allowed_next_verbs"]
    assert "arif_act" not in header["allowed_next_verbs"]
    assert "arif_seal" not in header["allowed_next_verbs"]


def test_full_override_projects_full_and_forge_seal():
    header = _project_light(
        _components(),
        sid="SEAL-test-full",
        actor_id="arif",
        constitution_hash="sha256:deadbeef",
        actor_verified=True,
        authority_override="FULL",
    )
    birth = header["session_birth"]
    assert header["authority"] == "FULL"
    assert birth["authority_mode"] == "FULL"
    assert birth["verdict"] == "FULL"
    assert "arif_forge" in header["allowed_next_verbs"]
    assert "arif_seal" in header["allowed_next_verbs"]
    assert "arif_act" not in header["allowed_next_verbs"]


def test_sovereign_override_gets_full_verb_set():
    header = _project_light(
        _components(),
        sid="SEAL-test-sovereign",
        actor_id="arif",
        constitution_hash="sha256:deadbeef",
        actor_verified=True,
        authority_override="SOVEREIGN",
    )
    birth = header["session_birth"]
    assert header["authority"] == "SOVEREIGN"
    assert birth["authority_mode"] == "SOVEREIGN"
    assert "arif_forge" in header["allowed_next_verbs"]
    assert "arif_seal" in header["allowed_next_verbs"]
    assert "arif_act" not in header["allowed_next_verbs"]
