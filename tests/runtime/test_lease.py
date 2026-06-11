"""
tests/runtime/test_lease.py — Unit tests for the lease primitive.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import time

import pytest

from arifosmcp.runtime.lease import (
    Lease,
    LeaseRejection,
    LeaseScope,
    LeaseSpec,
    LeaseStore,
    verify_lease,
)


# ──────────────────────────────────────────────────────────────────────
# Scope subsumption
# ──────────────────────────────────────────────────────────────────────


class TestScopeSubsumes:
    def test_execute_subsumes_write_and_read(self) -> None:
        assert LeaseScope.subsumes(LeaseScope.EXECUTE, LeaseScope.WRITE)
        assert LeaseScope.subsumes(LeaseScope.EXECUTE, LeaseScope.READ)
        assert LeaseScope.subsumes(LeaseScope.EXECUTE, LeaseScope.EXECUTE)

    def test_write_subsumes_read(self) -> None:
        assert LeaseScope.subsumes(LeaseScope.WRITE, LeaseScope.READ)
        assert LeaseScope.subsumes(LeaseScope.WRITE, LeaseScope.WRITE)

    def test_write_does_not_subsume_execute(self) -> None:
        assert not LeaseScope.subsumes(LeaseScope.WRITE, LeaseScope.EXECUTE)

    def test_read_does_not_subsume_write_or_execute(self) -> None:
        assert not LeaseScope.subsumes(LeaseScope.READ, LeaseScope.WRITE)
        assert not LeaseScope.subsumes(LeaseScope.READ, LeaseScope.EXECUTE)


# ──────────────────────────────────────────────────────────────────────
# Issue and basic lease state
# ──────────────────────────────────────────────────────────────────────


class TestIssue:
    def test_issue_returns_lease(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="did:web:arif-fazil.com:000",
            organ="arifos",
            tool="arif_sense_observe",
            scope=LeaseScope.READ,
            ttl_s=60,
        )
        lease = store.issue(spec)
        assert lease.lease_id.startswith("lease-")
        assert len(lease.lease_id) == len("lease-") + 32
        assert lease.spec == spec
        assert lease.invocations_used == 0
        assert lease.revoked is False
        assert lease.is_expired is False

    def test_issue_rejects_zero_ttl(self) -> None:
        store = LeaseStore()
        with pytest.raises(ValueError):
            store.issue(
                LeaseSpec(
                    actor_did="x",
                    organ="x",
                    tool="x",
                    scope=LeaseScope.READ,
                    ttl_s=0,
                )
            )

    def test_issue_rejects_zero_max_invocations(self) -> None:
        store = LeaseStore()
        with pytest.raises(ValueError):
            store.issue(
                LeaseSpec(
                    actor_did="x",
                    organ="x",
                    tool="x",
                    scope=LeaseScope.READ,
                    ttl_s=60,
                    max_invocations=0,
                )
            )

    def test_issue_rejects_blank_fields(self) -> None:
        store = LeaseStore()
        with pytest.raises(ValueError):
            store.issue(
                LeaseSpec(
                    actor_did="",
                    organ="x",
                    tool="x",
                    scope=LeaseScope.READ,
                    ttl_s=60,
                )
            )


# ──────────────────────────────────────────────────────────────────────
# Verify (does not consume)
# ──────────────────────────────────────────────────────────────────────


class TestVerify:
    def test_no_lease_id_rejected(self) -> None:
        r = verify_lease(None, LeaseScope.READ)
        assert not r.granted
        assert r.reason_code == "UNKNOWN"

    def test_unknown_lease_rejected(self) -> None:
        r = verify_lease("lease-deadbeef", LeaseScope.READ)
        assert not r.granted
        assert r.reason_code == "UNKNOWN"

    def test_valid_lease_accepted(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=60,
        )
        lease = store.issue(spec)
        r = verify_lease(lease.lease_id, LeaseScope.READ, store=store)
        assert r.granted
        assert r.reason_code == "OK"
        assert r.lease_state is not None
        assert r.lease_state["invocations_remaining"] == 1

    def test_scope_insufficient_rejected(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=60,
        )
        lease = store.issue(spec)
        r = verify_lease(lease.lease_id, LeaseScope.EXECUTE, store=store)
        assert not r.granted
        assert r.reason_code == "SCOPE_INSUFFICIENT"

    def test_revoked_lease_rejected(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=60,
        )
        lease = store.issue(spec)
        store.revoke(lease.lease_id, "F11 violation")
        r = verify_lease(lease.lease_id, LeaseScope.READ, store=store)
        assert not r.granted
        assert r.reason_code == "REVOKED"

    def test_expired_lease_rejected(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=1,
        )
        lease = store.issue(spec)
        time.sleep(1.1)
        r = verify_lease(lease.lease_id, LeaseScope.READ, store=store)
        assert not r.granted
        assert r.reason_code == "EXPIRED"

    def test_exhausted_lease_rejected(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=60,
            max_invocations=1,
        )
        lease = store.issue(spec)
        store.consume(lease.lease_id, LeaseScope.READ)
        r = verify_lease(lease.lease_id, LeaseScope.READ, store=store)
        assert not r.granted
        assert r.reason_code == "EXHAUSTED"


# ──────────────────────────────────────────────────────────────────────
# Consume (does consume one invocation)
# ──────────────────────────────────────────────────────────────────────


class TestConsume:
    def test_consume_decrements_invocations(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=60,
            max_invocations=2,
        )
        lease = store.issue(spec)
        store.consume(lease.lease_id, LeaseScope.READ)
        after = store.get(lease.lease_id)
        assert after is not None
        assert after.invocations_used == 1

    def test_consume_invalid_returns_none(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=60,
        )
        lease = store.issue(spec)
        result = store.consume(lease.lease_id, LeaseScope.EXECUTE)
        assert result is None
        # The lease was NOT decremented because the consume was rejected
        after = store.get(lease.lease_id)
        assert after is not None
        assert after.invocations_used == 0

    def test_consume_then_verify_exhausted(self) -> None:
        store = LeaseStore()
        spec = LeaseSpec(
            actor_did="x",
            organ="x",
            tool="x",
            scope=LeaseScope.READ,
            ttl_s=60,
            max_invocations=1,
        )
        lease = store.issue(spec)
        store.consume(lease.lease_id, LeaseScope.READ)
        r = verify_lease(lease.lease_id, LeaseScope.READ, store=store)
        assert not r.granted
        assert r.reason_code == "EXHAUSTED"


# ──────────────────────────────────────────────────────────────────────
# List active + purge
# ──────────────────────────────────────────────────────────────────────


class TestListAndPurge:
    def test_list_active_excludes_revoked_and_expired(self) -> None:
        store = LeaseStore()
        active = store.issue(
            LeaseSpec(
                actor_did="x",
                organ="x",
                tool="x",
                scope=LeaseScope.READ,
                ttl_s=60,
            )
        )
        revoked = store.issue(
            LeaseSpec(
                actor_did="x",
                organ="x",
                tool="x",
                scope=LeaseScope.READ,
                ttl_s=60,
            )
        )
        store.revoke(revoked.lease_id, "test")
        expired = store.issue(
            LeaseSpec(
                actor_did="x",
                organ="x",
                tool="x",
                scope=LeaseScope.READ,
                ttl_s=1,
            )
        )
        time.sleep(1.1)
        actives = store.list_active()
        ids = {l.lease_id for l in actives}
        assert active.lease_id in ids
        assert revoked.lease_id not in ids
        assert expired.lease_id not in ids

    def test_purge_removes_revoked_and_expired(self) -> None:
        store = LeaseStore()
        store.issue(
            LeaseSpec(
                actor_did="x",
                organ="x",
                tool="x",
                scope=LeaseScope.READ,
                ttl_s=60,
            )
        )
        revoked = store.issue(
            LeaseSpec(
                actor_did="x",
                organ="x",
                tool="x",
                scope=LeaseScope.READ,
                ttl_s=60,
            )
        )
        store.revoke(revoked.lease_id, "test")
        purged = store.purge_expired()
        assert purged == 1
        actives = store.list_active()
        assert all(l.lease_id != revoked.lease_id for l in actives)
