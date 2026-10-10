"""
tests/runtime/test_identity_proof_not_name_p0.py — P0: authority by PROOF, not by NAME
======================================================================================

Measured exploit (2026-10-02, KVM8, sessions SEAL-567bf8ace94843db /
SEAL-9032a4651aab4cb7 / SEAL-8baae4ffd22b4f20 / SEAL-2f5bb5882eb8431b):

    curl -s -X POST http://100.64.0.2:8088/mcp \\
      -H 'Content-Type: application/json' \\
      -H 'Accept: application/json, text/event-stream' \\
      -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{
            "name":"arif_init",
            "arguments":{"actor_id":"arif","mode":"init","ack_irreversible":true}}}'

returned, for a caller with NO session, NO token and NO signature:

    "actor": {"actor_id":"arif","actor_verified":true,
              "authority_level":"LIMITED_MUTATE"}
    "autonomy_band":"LIMITED_MUTATE"  "mutation_allowed":true
    "act_claims":{"av":true,"witness":{"active":3,"diversity":"FULL"}}

Authority was granted BY NAME, not BY PROOF.

Why the existing suite never caught it
--------------------------------------
`tests/agi_kernel_readiness/test_010_consecutive_boots.py::test_p0_02_crypto_actor_bind`
already asserts the correct invariant, but it runs with no HTTP context, so
`request_trust` is UNKNOWN and `ARIFOS_TRUST_AUTO_SIGN_UNKNOWN` is unset →
`auto_sign_allowed()` is False → the name-only elevation branch is skipped and
the test passes while production is open.

These tests therefore reproduce the LIVE configuration, not the test-harness
configuration:

  * `ARIFOS_TRUST_AUTO_SIGN_UNKNOWN=1` — set in the live arifos.service env
    (measured via /proc/<MainPID>/environ).
  * `request_trust == LOCAL_LOOPBACK` — measured listener topology on KVM8:

        LISTEN 100.64.0.2:8088  tailscaled
        LISTEN 127.0.0.1:8088   arifos.service (python)

    tailscaled forwards tailnet traffic to loopback and adds no proxy headers,
    so EVERY host on the tailnet is classified LOCAL_LOOPBACK by
    RequestTrustMiddleware. "localhost IS the password" is structurally
    unusable as an identity boundary on this host. A faithful replica of the
    production ASGI stack (fastmcp stateless streamable-http +
    RequestTrustMiddleware) confirmed the contextvar DOES reach the tool, so
    the misclassification is topological, not a propagation bug.

Consequence: locality cannot discriminate a legitimate local agent from a
remote impostor. Only caller-supplied cryptographic proof can.

The kernel's own documented law (north star — not new doctrine)
--------------------------------------------------------------
`runtime/session.py::mark_session_ed25519_verified`:
    "Ed25519 key binding proves key possession, NOT sovereign identity.
     `actor_verified` stays False until real crypto verification lands.
     SINGLE SETTER: this is the ONLY place in the kernel that promotes
     `actor_verified` from False → True based on cryptographic Ed25519 proof."

`megaTools/tool_01_init_anchor.py` (2026-09-04 Path A fix, FI-003):
    "exempt actors do NOT auto-verify. Cryptographic proof still required for
     `actor_verified=True`. ... exempt membership authorizes an authority LEVEL
     only. (P0.4 2026-08-13 was a regression: ALL exempt actors got
     verified=True. That regression violated F2 — verified must reflect
     cryptographic truth, not registry membership.)"

F1 AMANAH: these tests assert on the response envelope only; they do not
modify canonical state.

DITEMPA BUKAN DIBERI — authority is forged from proof, never handed out on a
name.
"""

from __future__ import annotations

import base64

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from arifosmcp.runtime.act_token import identity_band_authority
from arifosmcp.runtime.request_trust import set_request_trust, trust_snapshot
from arifosmcp.runtime.tools import _arif_session_init

# Bands that authorize mutation (runtime/authority.py: mutation_allowed ==
# runtime_band in ("LIMITED_MUTATE", "FULL", "SOVEREIGN")).
MUTATION_CAPABLE_BANDS = frozenset({"LIMITED_MUTATE", "FULL", "SOVEREIGN"})

# The sovereign's own name — the identity the exploit claims.
SOVEREIGN_NAME = "arif"


@pytest.fixture
def live_exploit_conditions(monkeypatch):
    """Reproduce the LIVE arifos.service trust configuration.

    Both halves are measured production facts, not assumptions:
      * the env opt-in is present in the service's own environment;
      * tailscaled's loopback forward makes every tailnet peer look local.
    """
    monkeypatch.setenv("ARIFOS_TRUST_AUTO_SIGN_UNKNOWN", "1")
    set_request_trust(peer="127.0.0.1", proxied=False)
    try:
        yield trust_snapshot()
    finally:
        # Never leak a request-trust classification into sibling tests.
        set_request_trust(peer="", proxied=True)


def _band_of(res: dict) -> str:
    return str(
        res.get("autonomy_band")
        or res.get("band")
        or res.get("authority")
        or ((res.get("result") or {}).get("authority_band"))
        or ""
    ).upper()


class TestNameOnlyClaimIsNotIdentity:
    """The exploit: claim the sovereign's NAME with no cryptographic material."""

    def test_trust_fixture_reproduces_live_conditions(self, live_exploit_conditions):
        """Guard the guard: verify request_trust is loopback and default auto_sign is False."""
        assert live_exploit_conditions["request_trust"] == "LOCAL_LOOPBACK"
        assert live_exploit_conditions["auto_sign_allowed"] is False

    def test_anonymous_sovereign_name_is_not_actor_verified(
        self, live_exploit_conditions
    ):
        """P0 — `actor_id="arif"` with no signature/nonce MUST NOT verify.

        `actor_verified` must reflect cryptographic truth (F2), never registry
        membership or a name match.
        """
        res = _arif_session_init(
            mode="init", actor_id=SOVEREIGN_NAME, ack_irreversible=True
        )

        assert res.get("actor_verified") is not True, (
            "P0 IDENTITY BYPASS: an anonymous caller claiming actor_id="
            f"{SOVEREIGN_NAME!r} with no session, no token and no signature was "
            f"granted actor_verified=true (band={_band_of(res)}, "
            f"session={res.get('session_id')}). Authority was granted BY NAME, "
            "not BY PROOF — violates the SINGLE SETTER invariant in "
            "runtime/session.py::mark_session_ed25519_verified."
        )

        birth = (res.get("result") or {}).get("session_birth") or {}
        assert birth.get("actor_verified") is not True, (
            "session_birth also reports actor_verified=true for an unproven "
            f"name claim (session={res.get('session_id')})."
        )

    def test_anonymous_sovereign_name_gets_no_mutation_capable_band(
        self, live_exploit_conditions
    ):
        """P0 — an unproven name claim must not receive a mutation band."""
        res = _arif_session_init(
            mode="init", actor_id=SOVEREIGN_NAME, ack_irreversible=True
        )
        band = _band_of(res)

        assert band not in MUTATION_CAPABLE_BANDS, (
            "P0 IDENTITY BYPASS: unproven name claim "
            f"actor_id={SOVEREIGN_NAME!r} received mutation-capable band "
            f"{band!r} (session={res.get('session_id')}). Fail-closed requires "
            "OBSERVE_ONLY absent cryptographic proof."
        )
        assert res.get("mutation_allowed") is not True, (
            f"mutation_allowed=true for an unproven name claim (band={band})."
        )

    def test_act_token_does_not_assert_av_for_unproven_name(
        self, live_exploit_conditions
    ):
        """The signed ACT must not carry av=true for a name-only claim.

        The token outlives the response and is re-trusted by every later hop
        (`standing_source: act`), so a fabricated `av` launders the lie into
        the whole session lineage.
        """
        res = _arif_session_init(
            mode="init", actor_id=SOVEREIGN_NAME, ack_irreversible=True
        )
        claims = res.get("act_claims") or {}

        assert claims.get("av") is not True, (
            "P0 IDENTITY BYPASS: ACT minted with av=true for an unproven name "
            f"claim actor_id={SOVEREIGN_NAME!r} (session={res.get('session_id')}, "
            f"auth={claims.get('auth')})."
        )

    def test_crypto_verified_flag_is_not_fabricated_from_av(
        self, live_exploit_conditions
    ):
        """`actor_cryptographically_verified` must never be inferred from `av`.

        Measured live contradiction: session_birth said
        actor_cryptographically_verified=false while the envelope root said
        true — because act_token defaulted crypto_verified to actor_verified.
        Two fields sharing a name must not disagree (A2 authority state).
        """
        res = _arif_session_init(
            mode="init", actor_id=SOVEREIGN_NAME, ack_irreversible=True
        )
        birth = (res.get("result") or {}).get("session_birth") or {}
        root_crypto = bool(res.get("actor_cryptographically_verified"))
        birth_crypto = bool(birth.get("actor_cryptographically_verified"))

        assert root_crypto == birth_crypto, (
            "FABRICATED CRYPTO FLAG: envelope root reports "
            f"actor_cryptographically_verified={root_crypto} while session_birth "
            f"reports {birth_crypto} (session={res.get('session_id')}). No "
            "cryptographic material was supplied, so both must be False."
        )
        assert root_crypto is False, (
            "actor_cryptographically_verified=true with no caller signature."
        )


class TestWitnessCountIsNotIdentityProof:
    """Witness count is EVIDENCE DIVERSITY (W³) — never an identity proof."""

    def test_witness_diversity_does_not_imply_verification(
        self, live_exploit_conditions
    ):
        res = _arif_session_init(
            mode="init", actor_id=SOVEREIGN_NAME, ack_irreversible=True
        )
        claims = res.get("act_claims") or {}
        witness = claims.get("witness") or {}

        # The live exploit carried witness.active=3 / diversity=FULL alongside
        # av=true. Diversity may be reported, but it must not attest identity.
        if int(witness.get("active") or 0) > 0:
            assert claims.get("av") is not True, (
                "witness.active_count>0 was used as identity proof "
                f"(av=true, active={witness.get('active')}, "
                f"diversity={witness.get('diversity')}). Witness diversity is "
                "evidence breadth, not key possession."
            )

    def test_av_is_not_derived_from_active_count_in_token_translation(self):
        """`arifos.v1.*` token translation must not set av from witness count."""
        import inspect

        from arifosmcp.runtime import act_token, capability_token

        for mod, needle in (
            (act_token, "witness.active_count > 0"),
            (capability_token, "witness_active > 0"),
        ):
            src = inspect.getsource(mod)
            assert needle not in src or "av" not in src.split(needle)[0][
                -120:
            ], (
                f"{mod.__name__} still derives the identity claim `av` from a "
                f"witness count (`{needle}`). Witness count is evidence "
                "diversity, not identity proof."
            )


class TestLegitimatePathsPreserved:
    """Fail-closed must not become fail-nothing. Proof still buys authority."""

    def test_exempt_actor_keeps_system_exempt_level_without_verification(
        self, live_exploit_conditions
    ):
        """Bootstrap preserved: exempt actors keep their LEVEL, not verification.

        Documented design (2026-09-04 Path A): exempt membership authorizes an
        authority LEVEL via verification_method="system_exempt" WITHOUT
        actor_verified=True. The level must survive; the verification must not.
        """
        from arifosmcp.runtime.session import get_session_identity
        from arifosmcp.runtime.session_auth import exempt_actor_band

        assert exempt_actor_band("opencode") == "operator", (
            "precondition: opencode must remain an exempt system actor, else "
            "this test no longer covers the bootstrap path."
        )

        res = _arif_session_init(mode="init", actor_id="opencode")
        sid = res.get("session_id")

        # The unproven name claim must not be verified…
        assert res.get("actor_verified") is not True, (
            "exempt actor opencode was granted actor_verified=true on name "
            "membership alone — the exact P0.4 2026-08-13 regression the "
            "2026-09-04 Path A fix closed."
        )
        assert _band_of(res) not in MUTATION_CAPABLE_BANDS, (
            f"exempt actor opencode got mutation-capable band {_band_of(res)} "
            "without cryptographic proof."
        )

        # …but the exempt PROVENANCE must still be recorded, so the bootstrap
        # remains auditable and the level is recoverable once proof lands.
        ident = get_session_identity(sid) or {}
        auth_ctx = ident.get("auth_context") or {}
        methods = {
            ident.get("verification_method"),
            auth_ctx.get("verification_method"),
            auth_ctx.get("auth_method"),
        }
        assert "system_exempt" in methods or ident.get("authority_level"), (
            "exempt bootstrap provenance lost: verification_method/"
            f"authority_level not recorded for opencode (got {ident!r})."
        )

    def test_proof_still_maps_to_authority(self):
        """identity_band_authority must still reward real proof.

        Guards against "fixing" the bypass by flattening the ladder — the
        failure mode where every actor becomes OBSERVE_ONLY and the suite
        passes vacuously.
        """
        assert identity_band_authority(actor_verified=False) == "OBSERVE_ONLY"
        assert (
            identity_band_authority(actor_verified=True) == "LIMITED_MUTATE"
        ), "verified non-sovereign must still earn LIMITED_MUTATE"
        assert (
            identity_band_authority(
                actor_verified=True,
                signature_verified=True,
                is_sovereign_principal=True,
            )
            == "FULL"
        ), "signature-verified sovereign principal must still earn FULL"

    def test_caller_supplied_ed25519_signature_still_verifies(self):
        """The legitimate crypto path is untouched: a CALLER-produced signature
        over the issued nonce still verifies against the supplied public key.

        This is the distinction the fix preserves — the caller demonstrates key
        possession. The kernel signing its own challenge for a claimed name
        demonstrates nothing about the caller.
        """
        from arifosmcp.runtime.crypto_auth import (
            issue_actor_challenge,
            verify_init_identity,
        )

        nonce = issue_actor_challenge("ARIF")
        priv = ed25519.Ed25519PrivateKey.generate()
        sig_b64 = base64.b64encode(priv.sign(f"ARIF:{nonce}".encode())).decode()

        ok, _reason = verify_init_identity(
            actor_id="ARIF",
            nonce=nonce,
            signature_b64=sig_b64,
            public_key=priv.public_key(),
        )
        assert ok is True, "caller-supplied Ed25519 proof must still verify"

    def test_ed25519_single_setter_still_promotes(self):
        """mark_session_ed25519_verified remains the documented single setter."""
        from arifosmcp.runtime.session import (
            bind_session_identity,
            get_session_identity,
            mark_session_ed25519_verified,
        )

        sid = "SEAL-p0singleSetter01"
        bind_session_identity(
            session_id=sid,
            actor_id="fi003-probe",
            authority_level="operator",
            auth_context={"source": "test"},
        )
        before = get_session_identity(sid) or {}
        assert before.get("actor_verified") is not True, (
            "precondition: a freshly bound session must start unverified"
        )

        assert mark_session_ed25519_verified(sid, "fi003-probe", "00" * 32) is True
        after = get_session_identity(sid) or {}
        identity = after.get("identity") or {}
        assert identity.get("ed25519_verified") is True, (
            "the documented single setter must still record Ed25519 proof"
        )


class TestUnregisteredActorUnaffected:
    """Negative control: a name nobody registered was never the hole."""

    def test_unknown_actor_stays_observe_only(self, live_exploit_conditions):
        res = _arif_session_init(mode="init", actor_id="nobody-fi-999-unknown")
        assert res.get("actor_verified") is not True
        assert _band_of(res) not in MUTATION_CAPABLE_BANDS
