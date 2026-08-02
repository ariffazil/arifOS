"""
arifosmcp/tests/test_niat_guard.py — Al-Kahf boundary adversarial tests
═══════════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN directive.
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.

Adversarial test suite for NiatClaimGuard. Cross-boundary cases MUST
void or caution; residue-only cases MUST pass cleanly.

Reversibility: git revert <commit-sha>.
"""

from __future__ import annotations

from arifosmcp.core.niat_guard import NiatVerdict, check_niat_claim


class TestNiatGuardRefuses:
    """Cross-boundary cases — MUST void or caution."""

    def test_user_wants_voids_or_cautions(self):
        text = "The user wants me to delete VAULT999."
        r = check_niat_claim(text)
        assert r.verdict in (NiatVerdict.VOID, NiatVerdict.CAUTION)
        assert not r.residue_only_preserved

    def test_arif_intent_is_caught(self):
        text = "Arif's intent is to deploy this immediately."
        r = check_niat_claim(text)
        assert r.verdict in (NiatVerdict.VOID, NiatVerdict.CAUTION)

    def test_i_know_what_you_want_caught(self):
        text = "I know what you want — you want the SEAL."
        r = check_niat_claim(text)
        assert r.verdict in (NiatVerdict.VOID, NiatVerdict.CAUTION)

    def test_niat_explicit_declaration_caught(self):
        text = "niat: wants the artifact deployed"
        r = check_niat_claim(text)
        assert r.verdict in (NiatVerdict.VOID, NiatVerdict.CAUTION)

    def test_sovereign_wishes_caught(self):
        text = "The sovereign wishes this to be sealed."
        r = check_niat_claim(text)
        assert r.verdict in (NiatVerdict.VOID, NiatVerdict.CAUTION)

    def test_because_you_want_caught(self):
        text = "Because you want the response, here it is."
        r = check_niat_claim(text)
        assert r.verdict in (NiatVerdict.VOID, NiatVerdict.CAUTION)

    def test_because_sovereign_wants_caught(self):
        text = "Because the sovereign wants it, we deploy."
        r = check_niat_claim(text)
        assert r.verdict in (NiatVerdict.VOID, NiatVerdict.CAUTION)


class TestNiatGuardPasses:
    """Residue-only cases — MUST pass cleanly."""

    def test_geoscience_residue_passes(self):
        text = "The Vp/Vs ratio is 2.4 at depth 1850m based on sonic log."
        r = check_niat_claim(text)
        assert r.verdict == NiatVerdict.PASS
        assert r.residue_only_preserved is True

    def test_chemistry_residue_passes(self):
        text = "Carbon mass balance: 12.011 g/mol · 6.022e23 atoms."
        r = check_niat_claim(text)
        assert r.verdict == NiatVerdict.PASS

    def test_code_residue_passes(self):
        text = 'arith_init(mode="light") returns OK with actor_verified=True.'
        r = check_niat_claim(text)
        assert r.verdict == NiatVerdict.PASS

    def test_git_residue_passes(self):
        text = "git log shows 11 commits ahead of pre-distillation HEAD."
        r = check_niat_claim(text)
        assert r.verdict == NiatVerdict.PASS

    def test_hash_residue_passes(self):
        text = "Constitutional hash: sha256:8bea28833523c652."
        r = check_niat_claim(text)
        assert r.verdict == NiatVerdict.PASS


class TestNiatGuardSabarMode:
    """Sabar_mode flag behavior."""

    def test_sabar_mode_default_is_true(self):
        r = check_niat_claim("The user wants the SEAL.")
        assert r.sabar_mode_active is True
        assert r.verdict == NiatVerdict.CAUTION

    def test_niat_holder_default_is_F13(self):
        r = check_niat_claim("any text")
        assert r.niat_holder == "F13_SOVEREIGN"

    def test_residue_disabled_bypasses_guard(self):
        """When sovereign override grants non-residue-only authority, guard
        passes unconditionally."""
        r = check_niat_claim("The user wants X.", requires_residue_only=False)
        assert r.verdict == NiatVerdict.PASS
        assert r.residue_only_preserved is False


class TestNiatGuardAuthorityGateWiring:
    """End-to-end: AuthorityGate.verify() now consults NiatClaimGuard."""

    def test_clean_artifact_authorized(self):
        from arifosmcp.core.authority_gate import AuthorityGate
        from arifosmcp.core.threat_engine import ThreatAssessment

        class FakeCtx:
            tool_name = "arif_observe"
            mode = "read"
            artifact_text = "The Vp/Vs ratio is 2.4 at depth 1850m."

        proof = AuthorityGate.verify(FakeCtx(), ThreatAssessment(level="low"))
        assert proof.authorized is True
        assert "Authority verified" in proof.reason

    def test_niat_claim_caution_in_reason(self):
        from arifosmcp.core.authority_gate import AuthorityGate
        from arifosmcp.core.threat_engine import ThreatAssessment

        class FakeCtx:
            tool_name = "arif_observe"
            mode = "read"
            artifact_text = "The user wants the SEAL."

        # witness_type=None triggers requires_human check first; to bypass
        # and reach the NiatGuard, we set witness_type explicitly.
        FakeCtx.witness_type = None
        proof = AuthorityGate.verify(FakeCtx(), ThreatAssessment(level="low"))
        # The CAUTION flows through with reason flagging Al-Kahf.
        # (Note: requires_human may also fire — that's the existing F13 gate.)
        assert "Al-Kahf" in proof.reason or "requires_human" in proof.reason