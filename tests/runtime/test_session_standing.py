"""Tests for the canonical SessionStanding composer (Epoch 1 / Item 1).

Proves the F13 audit exit condition at the schema level: the canonical
envelope has exactly the audit-specified fields and no legacy identity
fields leak.

These tests do not touch the live kernel. They prove the composer and
envelope are correct in isolation. Wiring `_wrap_handler` to consume
`compose_standing` is the next migration step (Item 1, integration).
"""

from __future__ import annotations

from typing import Any


def _flatten(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten a nested dict into dot-paths for field-name scanning."""
    out: dict[str, Any] = {}
    for k, v in d.items():
        path = k if not prefix else f"{prefix}.{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, path))
        else:
            out[path] = v
    return out


def test_session_standing_is_frozen():
    from arifosmcp.runtime.session_standing import (
        ActorStanding,
        AuthorityStanding,
        SESSION_STANDING_VERSION,
        SessionStanding,
    )

    s = SessionStanding(
        session_id="SEAL-test",
        actor=ActorStanding(
            "arif", "ARIF_FAZIL", True, "ed25519",
            evidence_ref="local://test/evidence",
        ),
        authority=AuthorityStanding("SOVEREIGN", True, True),
        issued_at="2026-07-17T00:00:00+00:00",
        expires_at="2026-07-18T00:00:00+00:00",
    )
    assert s.state_version == SESSION_STANDING_VERSION

    # Dataclass is frozen — mutation is forbidden.
    raised = False
    try:
        s.state_version = 99  # type: ignore[misc]
    except Exception:
        raised = True
    assert raised, "SessionStanding must be frozen"


def test_canonical_envelope_has_exactly_audit_fields():
    from arifosmcp.runtime.session_standing import (
        compose_standing,
        standing_to_envelope,
    )

    standing = compose_standing("anon-1", "anonymous")
    env = standing_to_envelope(standing)

    assert set(env.keys()) == {
        "session_id",
        "actor",
        "authority",
        "issued_at",
        "expires_at",
        "state_version",
    }
    assert set(env["actor"].keys()) == {
        "claimed_id",
        "canonical_id",
        "verified",
        "verification_method",
        "evidence_ref",
    }
    assert set(env["authority"].keys()) == {
        "band",
        "mutation_allowed",
        "seal_allowed",
    }


def test_canonical_envelope_emits_no_legacy_identity_fields():
    """Audit exit condition: no contradictory identity, authority, or verdict fields.

    The canonical envelope must not contain any of the seven legacy
    identity-bearing field names from identity_consistency.py.
    """
    from arifosmcp.runtime.session_standing import (
        compose_standing,
        standing_to_envelope,
    )

    standing = compose_standing("anon-1", "anonymous")
    env = standing_to_envelope(standing)
    flat = _flatten(env)

    banned = {
        "actor_verified",
        "authority_level",
        "human_authority",
        "runtime_authority",
        "claimed_id",  # now nested under actor
        "verification_method",  # now nested under actor
        "mutation_allowed",  # now nested under authority
        "seal_allowed",  # now nested under authority
    }
    leaked = banned & set(flat.keys())
    assert not leaked, f"Canonical envelope leaked legacy field names: {leaked}"


def test_compose_standing_anonymous_defaults_to_observe_only():
    from arifosmcp.runtime.session_standing import (
        BAND_OBSERVE_ONLY,
        compose_standing,
    )

    standing = compose_standing(None, "anonymous")
    assert standing.authority.band == BAND_OBSERVE_ONLY
    assert standing.authority.mutation_allowed is False
    assert standing.authority.seal_allowed is False
    assert standing.actor.verified is False
    assert standing.actor.verification_method is None
    assert standing.actor.claimed_id == "anonymous"
    assert standing.actor.canonical_id == "anonymous"


def test_compose_standing_is_deterministic_for_same_inputs():
    from arifosmcp.runtime.session_standing import compose_standing

    a = compose_standing("anon-1", "anonymous")
    b = compose_standing("anon-1", "anonymous")
    # Schema fields that must be stable across calls.
    assert a.actor.claimed_id == b.actor.claimed_id
    assert a.actor.canonical_id == b.actor.canonical_id
    assert a.actor.verified == b.actor.verified
    assert a.authority.band == b.authority.band
    assert a.authority.mutation_allowed == b.authority.mutation_allowed
    assert a.authority.seal_allowed == b.authority.seal_allowed


def test_authority_band_set_is_closed():
    """The four-band taxonomy is the only authority taxonomy the kernel emits."""
    from arifosmcp.runtime.session_standing import (
        BAND_FULL,
        BAND_LIMITED_MUTATE,
        BAND_OBSERVE_ONLY,
        BAND_SOVEREIGN,
        VALID_BANDS,
    )

    assert VALID_BANDS == frozenset(
        {BAND_OBSERVE_ONLY, BAND_LIMITED_MUTATE, BAND_FULL, BAND_SOVEREIGN}
    )
    assert len(VALID_BANDS) == 4


def test_band_normalization_collapses_legacy_tokens():
    """Legacy authority_level tokens map deterministically into the four bands."""
    from arifosmcp.runtime.session_standing import (
        BAND_FULL,
        BAND_LIMITED_MUTATE,
        BAND_OBSERVE_ONLY,
        BAND_SOVEREIGN,
        _normalize_band,
    )

    # SOVEREIGN path
    assert _normalize_band("SOVEREIGN") == BAND_SOVEREIGN
    assert _normalize_band("888") == BAND_SOVEREIGN
    # FULL path
    assert _normalize_band("FULL") == BAND_FULL
    # LIMITED_MUTATE path (legacy aliases map here)
    assert _normalize_band("OPERATOR") == BAND_LIMITED_MUTATE
    assert _normalize_band("OPERATOR_CLAIMED") == BAND_LIMITED_MUTATE
    assert _normalize_band("L4_WARGA") == BAND_LIMITED_MUTATE
    # OBSERVE_ONLY path
    assert _normalize_band("OBSERVER") == BAND_OBSERVE_ONLY
    assert _normalize_band("ANONYMOUS") == BAND_OBSERVE_ONLY
    assert _normalize_band("LOW") == BAND_OBSERVE_ONLY
    assert _normalize_band("garbage") == BAND_OBSERVE_ONLY
    assert _normalize_band(None) == BAND_OBSERVE_ONLY
    assert _normalize_band("") == BAND_OBSERVE_ONLY


def test_seal_allowed_only_for_sovereign():
    """F13 SOVEREIGN is the only band that may seal. Lower bands are read-only or mutate-only."""
    from arifosmcp.runtime.session_standing import (
        BAND_FULL,
        BAND_LIMITED_MUTATE,
        BAND_OBSERVE_ONLY,
        BAND_SOVEREIGN,
        AuthorityStanding,
    )

    assert AuthorityStanding(BAND_SOVEREIGN, True, True).seal_allowed is True
    assert AuthorityStanding(BAND_FULL, True, False).seal_allowed is False
    assert AuthorityStanding(BAND_LIMITED_MUTATE, True, False).seal_allowed is False
    assert AuthorityStanding(BAND_OBSERVE_ONLY, False, False).seal_allowed is False


def test_mutation_allowed_excludes_observe_only():
    """OBSERVE_ONLY is read-only by definition. No mutation, no seal."""
    from arifosmcp.runtime.session_standing import (
        BAND_FULL,
        BAND_LIMITED_MUTATE,
        BAND_OBSERVE_ONLY,
        BAND_SOVEREIGN,
        AuthorityStanding,
    )

    assert AuthorityStanding(BAND_OBSERVE_ONLY, False, False).mutation_allowed is False
    assert AuthorityStanding(BAND_LIMITED_MUTATE, True, False).mutation_allowed is True
    assert AuthorityStanding(BAND_FULL, True, False).mutation_allowed is True
    # seal_allowed=True requires SOVEREIGN band (T3a schema law)
    assert AuthorityStanding(BAND_SOVEREIGN, True, True).mutation_allowed is True


def test_state_version_is_one():
    """Schema version is part of the contract. Bumping it is a deliberate action."""
    from arifosmcp.runtime.session_standing import SESSION_STANDING_VERSION

    assert SESSION_STANDING_VERSION == 1


# ── Wrapper migration helper (Item 1 wiring) ──────────────────────────────


def test_attach_canonical_standing_strips_legacy_fields_at_top_level():
    """The wrapper helper must remove every legacy identity field name."""
    from arifosmcp.runtime.session_standing import attach_canonical_standing

    response = {
        "status": "ok",
        "tool": "arif_init",
        "actor_verified": True,
        "authority_level": "OPERATOR",
        "authority": "FULL",
        "human_authority": "SOVEREIGN",
        "runtime_authority": "FULL",
        "_identity_consistency_applied": True,
        "_identity_drift_count": 5,
    }
    out = attach_canonical_standing(response, session_id="SEAL-1", actor_id="arif")

    for legacy in (
        "actor_verified",
        "authority_level",
        "authority",
        "human_authority",
        "runtime_authority",
        "_identity_consistency_applied",
        "_identity_drift_count",
        "_identity_drift_first",
        "_identity_drift_violations",
        "authority_state",
    ):
        assert legacy not in out, f"Legacy field {legacy!r} was not stripped"


def test_attach_canonical_standing_strips_legacy_fields_in_nested_blocks():
    """Legacy fields live in meta, actor, authority_state, and result.* — all must be stripped."""
    from arifosmcp.runtime.session_standing import attach_canonical_standing

    response = {
        "status": "ok",
        "meta": {
            "actor_verified": True,
            "authority_level": "OPERATOR",
            "human_authority": "SOVEREIGN",
            "runtime_authority": "FULL",
            "_identity_drift_count": 5,
        },
        "actor": {
            "identity_verified": True,
            "authority_level": "OPERATOR",
            "claimed_id": "openclaw-anon",
        },
        "authority_state": {
            "actor": {"verified": True},
            "runtime_grant": {"level": "FULL"},
        },
        "result": {
            "actor_verified": True,
            "authority": {
                "RUNTIME_AUTHORITY": "FULL",
                "HUMAN_AUTHORITY": "SOVEREIGN",
                "ACTOR_VERIFIED": True,
            },
            "actor": {
                "identity_verified": True,
                "authority_level": "OPERATOR",
            },
            "authority_state": {
                "actor": {"verified": True},
                "runtime_grant": {"level": "FULL"},
            },
        },
    }
    out = attach_canonical_standing(response, session_id="SEAL-1", actor_id="arif")

    for legacy in (
        "actor_verified",
        "authority_level",
        "human_authority",
        "runtime_authority",
        "_identity_drift_count",
        "identity_verified",
    ):
        assert legacy not in out["meta"], f"meta.{legacy} was not stripped"
    # Legacy actor, authority_state, and result.{actor,authority,authority_state}
    # blocks all contained only identity fields. Stripping empties them,
    # so the empty blocks are removed entirely.
    for legacy_block in ("actor", "authority_state"):
        assert legacy_block not in out, (
            f"Legacy top-level {legacy_block} block was not removed"
        )
    for legacy_block in ("actor", "authority", "authority_state"):
        assert legacy_block not in out["result"], (
            f"Legacy result.{legacy_block} block was not removed"
        )


def test_attach_canonical_standing_adds_canonical_block():
    """The canonical `standing` block must be present after attach."""
    from arifosmcp.runtime.session_standing import attach_canonical_standing

    out = attach_canonical_standing(
        {"status": "ok", "tool": "arif_init"}, session_id="SEAL-9", actor_id="arif"
    )
    assert "standing" in out
    standing = out["standing"]
    assert set(standing.keys()) == {
        "session_id",
        "actor",
        "authority",
        "issued_at",
        "expires_at",
        "state_version",
    }
    assert standing["session_id"] == "SEAL-9"
    assert standing["actor"]["claimed_id"] == "arif"


def test_attach_canonical_standing_is_idempotent():
    """Calling attach twice produces the same canonical shape; no field growth."""
    from arifosmcp.runtime.session_standing import attach_canonical_standing

    response = {
        "status": "ok",
        "actor_verified": True,
        "authority_level": "OPERATOR",
        "result": {"actor_verified": True, "authority": {"RUNTIME_AUTHORITY": "FULL"}},
    }
    out1 = attach_canonical_standing(response, session_id="SEAL-1", actor_id="arif")
    out2 = attach_canonical_standing(out1, session_id="SEAL-1", actor_id="arif")

    assert set(out1.keys()) == set(out2.keys())
    assert out1["standing"] == out2["standing"]
    assert "actor_verified" not in out2
    assert "actor_verified" not in out2["result"]


def test_attach_canonical_standing_passes_through_non_dicts():
    """Non-dict responses (str, list, None) are returned unchanged."""
    from arifosmcp.runtime.session_standing import attach_canonical_standing

    assert attach_canonical_standing("plain string", session_id="S") == "plain string"
    assert attach_canonical_standing([1, 2, 3], session_id="S") == [1, 2, 3]
    assert attach_canonical_standing(None, session_id="S") is None


# ── attach_canonical — single-pass normalization (Item 1+3 combined) ─────


def test_attach_canonical_strips_identity_and_verdict_in_one_pass():
    """The one-call helper does both Item 1 (standing) and Item 3 (verdict) in one pass."""
    from arifosmcp.runtime.session_standing import attach_canonical

    response = {
        "status": "ok",
        "tool": "arif_init",
        # Legacy identity fields
        "actor_verified": True,
        "authority_level": "OPERATOR",
        "authority": "FULL",
        "human_authority": "SOVEREIGN",
        "runtime_authority": "FULL",
        # Legacy verdict fields
        "verdict": "SEAL",
        "verdict_code": "OK",
        "canonical_verdict": "SEAL",
        "reasoning_verdict": "OK",
        "nine_signal_aggregate": {"state": "GREEN"},
        # Nested legacy duplicates
        "meta": {
            "actor_verified": True,
            "verdict": "SEAL",
        },
    }
    out = attach_canonical(response, session_id="SEAL-X", actor_id="arif")

    # Identity legacy fields gone
    for legacy in (
        "actor_verified", "authority_level", "authority",
        "human_authority", "runtime_authority",
    ):
        assert legacy not in out
        assert legacy not in out.get("meta", {})
    # Verdict legacy fields gone
    for legacy in (
        "verdict", "verdict_code", "canonical_verdict",
        "reasoning_verdict", "nine_signal_aggregate",
    ):
        assert legacy not in out
        assert legacy not in out.get("meta", {})

    # Canonical blocks present
    assert "standing" in out
    assert "effective_verdict" in out
    assert "reason_code" in out
    assert "next_action" in out
    assert "status" in out

    # Verdict reducer honored the tool's SEAL
    assert out["effective_verdict"] in {"SEAL", "OBSERVE_ONLY", "HOLD"}


def test_attach_canonical_observes_only_downgrades_seal_in_one_pass():
    """F1 AMANAH: when authority is OBSERVE_ONLY, a tool's SEAL becomes OBSERVE_ONLY."""
    from arifosmcp.runtime.session_standing import attach_canonical
    from arifosmcp.runtime.verdict import attach_effective_verdict

    response = {"status": "ok", "tool": "arif_init", "verdict": "SEAL"}
    # No real session, so the canonical composer emits OBSERVE_ONLY.
    # The verdict reducer then downgrades the tool's SEAL to OBSERVE_ONLY.
    out = attach_canonical(response, session_id=None, actor_id="anonymous")
    assert out["effective_verdict"] == "OBSERVE_ONLY"
    assert out["standing"]["authority"]["band"] == "OBSERVE_ONLY"
    # Direct call to verdict composer: same outcome.
    out2 = attach_effective_verdict(
        {"status": "ok", "verdict": "SEAL"},
        inner_verdict="SEAL",
        session_authority_band="OBSERVE_ONLY",
    )
    assert out2["effective_verdict"] == "OBSERVE_ONLY"


def test_attach_canonical_passes_through_non_dict():
    """Non-dict inputs are wrapped, normalized, and unwrapped transparently."""
    from arifosmcp.runtime.session_standing import attach_canonical

    out = attach_canonical("plain string", session_id="S", actor_id="arif")
    assert out == "plain string"
    out = attach_canonical([1, 2, 3], session_id="S")
    assert out == [1, 2, 3]
    out = attach_canonical(None, session_id="S")
    assert out is None

def test_unverified_collapses_to_observe_only():
    """P0 AC: unverified identity must not receive mutation authority."""
    from arifosmcp.runtime.session_standing import (
        BAND_OBSERVE_ONLY,
        compose_standing,
    )

    standing = compose_standing("SEAL-unknown", "ARIF")
    assert standing.actor.verified is False
    assert standing.authority.band == BAND_OBSERVE_ONLY
    assert standing.authority.mutation_allowed is False
    assert standing.authority.seal_allowed is False


def test_verified_true_method_null_unrepresentable():
    """P0 AC: ActorStanding raises when verified without method+evidence."""
    from arifosmcp.runtime.session_standing import ActorStanding
    import pytest

    with pytest.raises(ValueError):
        ActorStanding("arif", "arif", True, None, None)
    with pytest.raises(ValueError):
        ActorStanding("arif", "arif", True, "ed25519", None)


def test_component_identity_cannot_absorb_human_claim(monkeypatch):
    """P0 identity: arif claim must not inherit conformance-spine standing."""
    from arifosmcp.runtime import session_standing as ss

    fake_record = {
        "session_id": "SEAL-component",
        "actor_id": "conformance-spine",
        "canonical_actor_id": "conformance-spine",
        "verified": True,
        "actor_verified": True,
        "authority_level": "FULL",
        "runtime_authority": "FULL",
        "verification_method": "ed25519",
        "evidence_ref": "session://SEAL-component",
        "auth_context": {
            "verification_method": "ed25519",
            "verified_key_id": "ed25519:sha256:deadbeef",
        },
        "created_at": "2026-07-17T00:00:00+00:00",
        "expires_at": "2026-07-18T00:00:00+00:00",
    }
    monkeypatch.setattr(ss, "_read_session_record", lambda sid: fake_record)
    standing = ss.compose_standing("SEAL-component", "ARIF")
    assert standing.actor.claimed_id == "ARIF"
    # Must not keep component as canonical
    assert standing.actor.canonical_id.lower() != "conformance-spine"
    # Authority collapsed (claim/session mismatch)
    assert standing.authority.band == ss.BAND_OBSERVE_ONLY
    assert standing.authority.mutation_allowed is False


def test_identity_claim_cannot_grant_mutation(monkeypatch):
    """Option B constraint: identity_claim is weak — no mutation."""
    from arifosmcp.runtime import session_standing as ss

    fake_record = {
        "session_id": "SEAL-arif",
        "actor_id": "arif",
        "canonical_actor_id": "arif",
        "verified": True,
        "actor_verified": True,
        "authority_level": "FULL",
        "runtime_authority": "FULL",
        "verification_method": "identity_claim",
        "evidence_ref": "session://SEAL-arif",
        "auth_context": {"verification_method": "identity_claim"},
        "created_at": "2026-07-17T00:00:00+00:00",
        "expires_at": "2026-07-18T00:00:00+00:00",
    }
    monkeypatch.setattr(ss, "_read_session_record", lambda sid: fake_record)
    standing = ss.compose_standing("SEAL-arif", "arif")
    assert standing.actor.verified is True
    assert standing.actor.verification_method == "identity_claim"
    assert standing.authority.band == ss.BAND_OBSERVE_ONLY
    assert standing.authority.mutation_allowed is False
    assert standing.authority.seal_allowed is False


def test_strong_method_can_grant_full(monkeypatch):
    """Strong verification methods may elevate band from the session record."""
    from arifosmcp.runtime import session_standing as ss

    fake_record = {
        "session_id": "SEAL-arif",
        "actor_id": "arif",
        "canonical_actor_id": "ARIF_FAZIL",
        "verified": True,
        "actor_verified": True,
        "authority_level": "FULL",
        "runtime_authority": "FULL",
        "verification_method": "ed25519",
        "evidence_ref": "key://ed25519:sha256:abcd",
        "auth_context": {
            "verification_method": "ed25519",
            "verified_key_id": "ed25519:sha256:abcd",
        },
        "created_at": "2026-07-17T00:00:00+00:00",
        "expires_at": "2026-07-18T00:00:00+00:00",
    }
    monkeypatch.setattr(ss, "_read_session_record", lambda sid: fake_record)
    standing = ss.compose_standing("SEAL-arif", "arif")
    assert standing.actor.verified is True
    assert standing.authority.band == ss.BAND_FULL
    assert standing.authority.mutation_allowed is True
    assert standing.authority.seal_allowed is False  # FULL ≠ SOVEREIGN


def test_attach_canonical_kills_session_birth_dual_claim():
    """P0: session_birth must not claim FULL while standing is OBSERVE_ONLY."""
    from arifosmcp.runtime.session_standing import attach_canonical

    response = {
        "session_id": "SEAL-sync-test",
        "actor_id": "ARIF",
        "actor_verified": True,
        "authority": "FULL",
        "authority_scope": "FULL",
        "session_birth": {
            "session_id": "SEAL-sync-test",
            "actor_id": "arif",
            "actor_verified": True,
            "authority_mode": "FULL",
            "verdict": "FULL",
            "mutation_allowed": True,
            "authority_source": "identity_band",
        },
        "clarity_contract": {
            "authority_band": "FULL",
            "mutation_allowed": True,
            "actor_bound": True,
            "evidence_honesty": "CLEAR",
        },
        "sct_claims": {"auth": "FULL", "av": True},
    }
    out = attach_canonical(response, session_id="SEAL-sync-test", actor_id="ARIF")
    st = out["standing"]
    assert st["authority"]["band"] == "OBSERVE_ONLY"
    assert st["authority"]["mutation_allowed"] is False
    assert out["session_birth"]["authority_mode"] == "OBSERVE_ONLY"
    assert out["session_birth"]["mutation_allowed"] is False
    assert out["session_birth"]["actor_verified"] is False
    assert out["session_birth"]["authority_source"] == "standing"
    assert out["clarity_contract"]["mutation_allowed"] is False
    assert out["clarity_contract"]["authority_band"] == "OBSERVE_ONLY"
    assert out.get("authority_scope") == "OBSERVE_ONLY"
    assert out["sct_claims"]["av"] is False
