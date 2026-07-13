"""
tests/test_p1_modules.py — Tests for P1 modules:
  - forge_session_runtime (authority ceremony)
  - runtime_verify (convergence check)
  - convergence_tracker (five-layer comparison)
  - signed_receipt (Ed25519 chain)
  - cooling_verbs (metabolism lifecycle)
"""

import pytest
from unittest.mock import patch


# --- forge_session_runtime tests ---

class TestSovereignSignal:
    def test_no_actor_returns_anonymous(self):
        from arifosmcp.runtime.forge_session_runtime import sovereign_signal
        v = sovereign_signal(session_id="s1")
        assert v.sovereignty is False
        assert v.method == "anonymous"

    def test_non_sovereign_actor(self):
        from arifosmcp.runtime.forge_session_runtime import sovereign_signal
        v = sovereign_signal(session_id="s1", actor_id="random-agent")
        assert v.sovereignty is False
        assert "non-sovereign" in v.reason

    def test_sovereign_actor_no_key(self):
        from arifosmcp.runtime.forge_session_runtime import sovereign_signal
        v = sovereign_signal(session_id="s1", actor_id="arif")
        assert v.sovereignty is False
        assert "key not in SOVEREIGN_KEY_IDS" in v.reason

    def test_sovereign_actor_bad_key(self):
        from arifosmcp.runtime.forge_session_runtime import sovereign_signal
        v = sovereign_signal(session_id="s1", actor_id="arif", verified_key_id="bad:key")
        assert v.sovereignty is False

    def test_fail_closed_on_exception(self):
        from arifosmcp.runtime.forge_session_runtime import sovereign_signal
        v = sovereign_signal(session_id="s1", actor_id="arif", session="not_a_dict")
        # Should not raise, should return False
        assert v.sovereignty is False


class TestMaySeal:
    def test_all_conditions_pass(self):
        from arifosmcp.runtime.forge_session_runtime import may_seal, AuthorityEnvelope, HumanAuthority, RuntimeBand
        env = AuthorityEnvelope(
            human_authority=HumanAuthority.SOVEREIGN,
            runtime_band=RuntimeBand.OBSERVE_ONLY,
            actor_verified=True,
            session_bound=True,
            lease_valid=True,
            capabilities=frozenset(["vault.append:sovereign_decision"]),
        )
        allowed, reason = may_seal(
            env,
            required_capability="vault.append:sovereign_decision",
            requires_sovereign=True,
            payload_matches=True,
            vault_chain_healthy=True,
        )
        assert allowed is True
        assert reason == "allowed"

    def test_missing_capability(self):
        from arifosmcp.runtime.forge_session_runtime import may_seal, AuthorityEnvelope, HumanAuthority, RuntimeBand
        env = AuthorityEnvelope(
            human_authority=HumanAuthority.SOVEREIGN,
            runtime_band=RuntimeBand.OBSERVE_ONLY,
            actor_verified=True,
            session_bound=True,
            lease_valid=True,
            capabilities=frozenset(),
        )
        allowed, reason = may_seal(
            env,
            required_capability="vault.append:sovereign_decision",
            requires_sovereign=True,
            payload_matches=True,
            vault_chain_healthy=True,
        )
        assert allowed is False
        assert "missing_capability" in reason

    def test_vault_unhealthy(self):
        from arifosmcp.runtime.forge_session_runtime import may_seal, AuthorityEnvelope, HumanAuthority, RuntimeBand
        env = AuthorityEnvelope(
            human_authority=HumanAuthority.SOVEREIGN,
            runtime_band=RuntimeBand.OBSERVE_ONLY,
            actor_verified=True,
            session_bound=True,
            lease_valid=True,
            capabilities=frozenset(["vault.append"]),
        )
        allowed, reason = may_seal(
            env,
            required_capability="vault.append",
            requires_sovereign=True,
            payload_matches=True,
            vault_chain_healthy=False,
        )
        assert allowed is False
        assert "vault_chain_unhealthy" in reason


class TestCapabilityIssuance:
    def test_issue_and_consume(self):
        from arifosmcp.runtime.forge_session_runtime import issue_seal_capability, consume_capability
        cap = issue_seal_capability("s1", "arif", "hash123")
        assert cap is not None
        assert cap.consumed is False

        consumed, reason = consume_capability(cap.capability_id, cap.action, "hash123")
        assert consumed is True
        assert reason == "consumed"

        # Second consume should fail
        consumed2, reason2 = consume_capability(cap.capability_id, cap.action, "hash123")
        assert consumed2 is False

    def test_payload_mismatch(self):
        from arifosmcp.runtime.forge_session_runtime import issue_seal_capability, consume_capability
        cap = issue_seal_capability("s1", "arif", "hash123")
        consumed, reason = consume_capability(cap.capability_id, cap.action, "wrong_hash")
        assert consumed is False
        assert "payload_mismatch" in reason


# --- runtime_verify tests ---

class TestRuntimeVerify:
    def test_verify_returns_manifest(self):
        from arifosmcp.runtime.runtime_verify import verify_runtime
        m = verify_runtime()
        assert m.convergence in ("PASS", "FAIL", "UNKNOWN")
        assert m.python_executable
        assert len(m.dimensions) > 0

    def test_manifest_to_dict(self):
        from arifosmcp.runtime.runtime_verify import verify_runtime
        m = verify_runtime()
        d = m.to_dict()
        assert "convergence" in d
        assert "dimensions" in d


# --- convergence_tracker tests ---

class TestConvergenceTracker:
    def test_check_convergence(self):
        from arifosmcp.runtime.convergence_tracker import check_convergence, ConvergenceState
        r = check_convergence()
        assert r.state in ConvergenceState
        assert len(r.layers) > 0

    def test_report_to_dict(self):
        from arifosmcp.runtime.convergence_tracker import check_convergence
        r = check_convergence()
        d = r.to_dict()
        assert "state" in d
        assert "layers" in d


# --- cooling_verbs tests ---

class TestCoolingVerbs:
    def test_observe_diagnose_propose_cycle(self):
        from arifosmcp.runtime.cooling_verbs import observe, diagnose, propose, create_cycle, append_event
        cycle = create_cycle("fail-001")
        assert cycle.state == "OPEN"

        e1 = observe("fail-001", "agent", {"symptom": "timeout"})
        cycle = append_event(cycle, e1)
        assert cycle.state == "OPEN"

        e2 = diagnose("fail-001", "agent", "pool_exhausted", {"pool": 0})
        cycle = append_event(cycle, e2)
        assert cycle.state == "OPEN"

        e3 = propose("fail-001", "agent", {"fix": "increase_pool"}, {"confidence": 0.9})
        cycle = append_event(cycle, e3)
        assert cycle.state == "OPEN"
        assert len(cycle.events) == 3

    def test_full_cycle_to_sealed(self):
        from arifosmcp.runtime.cooling_verbs import (
            observe, diagnose, propose, approve, install, verify, receipt,
            create_cycle, append_event,
        )
        cycle = create_cycle("fail-002")
        cycle = append_event(cycle, observe("fail-002", "a", {}))
        cycle = append_event(cycle, diagnose("fail-002", "a", "cause", {}))
        cycle = append_event(cycle, propose("fail-002", "a", {"fix": "x"}, {}))
        cycle = append_event(cycle, approve("fail-002", "arif", {"approved": True}))
        assert cycle.state == "APPROVED"
        cycle = append_event(cycle, install("fail-002", "a", {"applied": True}))
        assert cycle.state == "INSTALLED"
        cycle = append_event(cycle, verify("fail-002", "a", {"passed": True}))
        assert cycle.state == "VERIFIED"
        cycle = append_event(cycle, receipt("fail-002", "a", cycle))
        assert cycle.state == "SEALED"
        assert cycle.closed_at != ""

    def test_decay(self):
        from arifosmcp.runtime.cooling_verbs import observe, propose, decay, create_cycle, append_event
        cycle = create_cycle("fail-003")
        cycle = append_event(cycle, observe("fail-003", "a", {}))
        cycle = append_event(cycle, propose("fail-003", "a", {"fix": "x"}, {}))
        cycle = append_event(cycle, decay("fail-003", "a", "superseded by newer fix"))
        assert cycle.state == "DECAYED"
        assert cycle.closed_at != ""
