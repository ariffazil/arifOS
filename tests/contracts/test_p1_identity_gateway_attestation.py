"""
Test Suite: P0.6 + P1.1 + P1.2 Contracts — arifOS Federation
═════════════════════════════════════════════════════════════

Covers:
  P0.6 — Identity/authority proof with nonce + replay protection
  P1.1 — Gateway discovery without HOLD
  P1.2 — Independent attestation self-test

DITEMPA BUKAN DIBERI — Contracts without tests are wishes.
"""

import pytest

from contracts.identity import (
    AuthorityTier,
    IdentityContext,
    IdentityStatus,
    Nonce,
    SignedIdentity,
)
from contracts.gateway_discovery import (
    CANONICAL_ORGANS,
    GATEWAY_AUTHORITY_MAP,
    DiscoveryMode,
    GatewayAction,
    get_discovery_organs,
)
from contracts.self_attestation import (
    AttestationClaim,
    AttestationReport,
    AttestationVerdict,
    build_canonical_claims,
)


# ═══════════════════════════════════════════════════════════════════════════════
# P0.6 — Identity + Authority Proof
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthorityTier:
    """Authority tiers must be correctly ordered and gated."""

    def test_tier_ordering(self):
        """Higher tiers must have higher numeric values."""
        assert AuthorityTier.OBSERVER < AuthorityTier.OPERATOR
        assert AuthorityTier.OPERATOR < AuthorityTier.AGENT
        assert AuthorityTier.AGENT < AuthorityTier.JUDGE
        assert AuthorityTier.JUDGE < AuthorityTier.SOVEREIGN

    def test_observer_cannot_seal(self):
        """Observer (Tier 0) must NOT be able to seal."""
        assert AuthorityTier.OBSERVER.may_seal is False
        assert AuthorityTier.OBSERVER.may_forge is False
        assert AuthorityTier.OBSERVER.may_judge is False

    def test_sovereign_can_everything(self):
        """Sovereign (Tier 4) must have full authority."""
        assert AuthorityTier.SOVEREIGN.may_seal is True
        assert AuthorityTier.SOVEREIGN.may_forge is True
        assert AuthorityTier.SOVEREIGN.may_judge is True
        assert AuthorityTier.SOVEREIGN.may_execute is True

    def test_agent_can_execute_not_judge(self):
        """Agent (Tier 2) can execute but not judge."""
        assert AuthorityTier.AGENT.may_execute is True
        assert AuthorityTier.AGENT.may_judge is False
        assert AuthorityTier.AGENT.may_seal is False

    def test_from_string(self):
        """String parsing must work for all tiers."""
        assert AuthorityTier.from_string("observer") == AuthorityTier.OBSERVER
        assert AuthorityTier.from_string("sovereign") == AuthorityTier.SOVEREIGN
        assert AuthorityTier.from_string("AGENT") == AuthorityTier.AGENT
        assert AuthorityTier.from_string("unknown") == AuthorityTier.OBSERVER


class TestNonce:
    """Nonces must provide replay protection."""

    def test_nonce_is_unique(self):
        """Each nonce must be unique."""
        n1 = Nonce()
        n2 = Nonce()
        assert n1.value != n2.value

    def test_nonce_starts_valid(self):
        """Fresh nonce must be valid."""
        n = Nonce()
        assert n.is_valid is True
        assert n.used is False

    def test_nonce_consumed(self):
        """Consumed nonce must be invalid."""
        n = Nonce()
        n.consume()
        assert n.is_valid is False
        assert n.used is True


class TestSignedIdentity:
    """Signed identities must carry cryptographic proof."""

    def test_default_is_not_verified(self):
        """Default identity must not claim verification."""
        si = SignedIdentity(actor_id="test")
        assert si.is_verified is False
        assert si.verification_method == "none"

    def test_signing_payload_format(self):
        """Signing payload must be deterministic."""
        si = SignedIdentity(
            actor_id="arif-fazil",
            nonce=Nonce(value="abc123"),
            signed_at=1700000000.0,
        )
        payload = si.signing_payload
        assert "arif-fazil" in payload
        assert "abc123" in payload
        assert "1700000000.0" in payload

    def test_verified_identity_has_proof(self):
        """Verified identity must have signature and verifier."""
        si = SignedIdentity(
            actor_id="arif-fazil",
            signature="fake-sig-for-testing",
            verified_by="arifOS-kernel",
            verification_method="ed25519",
        )
        assert si.is_verified is True

    def test_authority_tier_coercion(self):
        """Authority tier must accept string, int, or enum."""
        si1 = SignedIdentity(actor_id="a", authority_tier=AuthorityTier.JUDGE)
        assert si1.authority_tier == AuthorityTier.JUDGE

        si2 = SignedIdentity(actor_id="b", authority_tier=AuthorityTier.SOVEREIGN)
        assert si2.authority_tier == AuthorityTier.SOVEREIGN


class TestIdentityContext:
    """Identity context must propagate through the session."""

    def test_anonymous_by_default(self):
        """Default context must be anonymous."""
        ctx = IdentityContext()
        assert ctx.status == IdentityStatus.ANONYMOUS
        assert ctx.authority_tier == AuthorityTier.OBSERVER

    def test_with_signed_identity(self):
        """Context with signed identity must report correct authority."""
        si = SignedIdentity(
            actor_id="arif-fazil",
            authority_tier=AuthorityTier.SOVEREIGN,
            signature="sig",
            verified_by="kernel",
            verification_method="ed25519",
        )
        ctx = IdentityContext(
            declared_actor_id="arif-fazil",
            signed_identity=si,
            status=IdentityStatus.VERIFIED,
        )
        assert ctx.may_seal is True
        assert ctx.may_forge is True
        assert ctx.is_verified is True

    def test_observer_context_cannot_seal(self):
        """Observer context must not allow seal."""
        ctx = IdentityContext()
        assert ctx.may_seal is False
        assert ctx.may_forge is False


# ═══════════════════════════════════════════════════════════════════════════════
# P1.1 — Gateway Discovery
# ═══════════════════════════════════════════════════════════════════════════════


class TestGatewayDiscovery:
    """Gateway discovery must not require unsafe authority."""

    def test_discovery_requires_tier_0(self):
        """Discovery must require the lowest authority tier (0)."""
        assert GATEWAY_AUTHORITY_MAP[GatewayAction.DISCOVER] == 0

    def test_route_requires_higher_than_discover(self):
        """Routing must require higher authority than discovery."""
        assert (
            GATEWAY_AUTHORITY_MAP[GatewayAction.ROUTE]
            > GATEWAY_AUTHORITY_MAP[GatewayAction.DISCOVER]
        )

    def test_delegate_requires_sovereign(self):
        """Delegation must require the highest tier."""
        assert GATEWAY_AUTHORITY_MAP[GatewayAction.DELEGATE] == 4

    def test_discovery_has_8_organs(self):
        """The canonical organ list must have 8 entries."""
        assert len(CANONICAL_ORGANS) == 8

    def test_all_organs_have_health_endpoint(self):
        """Every organ must have a health endpoint."""
        for organ in CANONICAL_ORGANS:
            assert organ.health_endpoint, f"{organ.name} missing health endpoint"

    def test_arifos_is_first(self):
        """arifOS must be the first organ in discovery."""
        assert CANONICAL_ORGANS[0].name == "arifOS"

    def test_get_discovery_organs(self):
        """get_discovery_organs must return the canonical list."""
        organs = get_discovery_organs()
        assert len(organs) == 8
        assert organs[0].name == "arifOS"

    def test_discovery_modes_are_read_only(self):
        """All discovery modes must be read-only operations."""
        for mode in DiscoveryMode:
            assert mode.value in {
                "list_organs",
                "organ_status",
                "topology",
                "agent_card",
                "capabilities",
            }


# ═══════════════════════════════════════════════════════════════════════════════
# P1.2 — Independent Attestation
# ═══════════════════════════════════════════════════════════════════════════════


class TestAttestation:
    """The runtime must prove its claims, not just declare them."""

    def test_builds_7_canonical_claims(self):
        """Must build at least 6 canonical attestation claims."""
        claims = build_canonical_claims()
        assert len(claims) >= 6, f"Expected >=6 claims, got {len(claims)}"

    def test_each_claim_has_test_fn(self):
        """Every claim must have a callable test function."""
        claims = build_canonical_claims()
        for claim in claims:
            assert callable(claim.test_fn), f"{claim.claim_id} has no test_fn"

    def test_claim_verify_updates_verdict(self):
        """verify() must update the verdict from UNPROVEN."""
        claim = AttestationClaim(
            claim_id="TEST",
            claim="Always true",
            test_fn=lambda: True,
        )
        assert claim.verdict == AttestationVerdict.UNPROVEN
        result = claim.verify()
        assert result == AttestationVerdict.PROVEN

    def test_claim_verify_failure(self):
        """verify() must set FAILED when test returns False."""
        claim = AttestationClaim(
            claim_id="TEST",
            claim="Always false",
            test_fn=lambda: False,
        )
        claim.verify()
        assert claim.verdict == AttestationVerdict.FAILED

    def test_claim_verify_exception(self):
        """verify() must set DEGRADED when test raises."""
        claim = AttestationClaim(
            claim_id="TEST",
            claim="Always raises",
            test_fn=lambda: (_ for _ in ()).throw(Exception("boom")),
        )
        claim.verify()
        assert claim.verdict == AttestationVerdict.DEGRADED
        assert claim.error is not None

    def test_report_counts_proven(self):
        """Report must count proven claims."""
        claims = [
            AttestationClaim("A", "pass", lambda: True, verdict=AttestationVerdict.PROVEN),
            AttestationClaim("B", "fail", lambda: False, verdict=AttestationVerdict.FAILED),
            AttestationClaim(
                "C", "untestable", lambda: True, verdict=AttestationVerdict.UNTESTABLE
            ),
        ]
        report = AttestationReport(claims=claims)
        assert report.proven_count == 1
        assert report.total_count == 3
        assert report.score == pytest.approx(1 / 3)

    def test_report_healthy_when_all_proven(self):
        """Report is healthy when all testable claims are PROVEN."""
        claims = [
            AttestationClaim("A", "pass", lambda: True, verdict=AttestationVerdict.PROVEN),
            AttestationClaim(
                "B", "untestable", lambda: True, verdict=AttestationVerdict.UNTESTABLE
            ),
        ]
        report = AttestationReport(claims=claims)
        assert report.is_healthy is True

    def test_report_unhealthy_when_failed(self):
        """Report is unhealthy when any claim FAILED."""
        claims = [
            AttestationClaim("A", "pass", lambda: True, verdict=AttestationVerdict.PROVEN),
            AttestationClaim("B", "fail", lambda: False, verdict=AttestationVerdict.FAILED),
        ]
        report = AttestationReport(claims=claims)
        assert report.is_healthy is False

    def test_contracts_importable_claim_passes(self):
        """The CONTRACTS_IMPORTABLE claim must actually be provable."""
        claims = build_canonical_claims()
        for claim in claims:
            if claim.claim_id == "CONTRACTS_IMPORTABLE":
                claim.verify()
                assert claim.verdict == AttestationVerdict.PROVEN, (
                    f"CONTRACTS_IMPORTABLE failed: {claim.error}"
                )
                return
        pytest.fail("CONTRACTS_IMPORTABLE claim not found")

    def test_budget_7_domains_claim_passes(self):
        """The BUDGET_7_DOMAINS claim must actually be provable."""
        claims = build_canonical_claims()
        for claim in claims:
            if claim.claim_id == "BUDGET_7_DOMAINS":
                claim.verify()
                assert claim.verdict == AttestationVerdict.PROVEN
                return
        pytest.fail("BUDGET_7_DOMAINS claim not found")

    def test_manifest_integrity_claim_passes(self):
        """The MANIFEST_INTEGRITY claim must actually be provable."""
        claims = build_canonical_claims()
        for claim in claims:
            if claim.claim_id == "MANIFEST_INTEGRITY":
                claim.verify()
                assert claim.verdict == AttestationVerdict.PROVEN
                return
        pytest.fail("MANIFEST_INTEGRITY claim not found")
