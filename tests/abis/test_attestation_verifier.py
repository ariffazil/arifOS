"""
tests/abis/test_attestation_verifier.py — Unit tests for the attestation verifier.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
import time

import pytest

from arifosmcp.abi.attestation_verifier import (
    AttestationRecord,
    AttestationStore,
    AttestationVerifier,
    DEFAULT_EXPECTED_ORGANS,
)


# ──────────────────────────────────────────────────────────────────────
# AttestationRecord parsing
# ──────────────────────────────────────────────────────────────────────


class TestAttestationRecord:
    def test_parse_typical_publisher_payload(self) -> None:
        payload = json.dumps(
            {
                "event": "ARIFOS_HEALTH",
                "organ": "arifos",
                "verdict": "HEALTHY",
                "ml_floors": True,
                "timestamp": "2026-06-11T03:30:00+00:00",
            }
        ).encode()
        rec = AttestationRecord.from_nats_message(payload)
        assert rec is not None
        assert rec.organ == "arifos"
        assert rec.verdict == "HEALTHY"
        assert rec.timestamp > 0

    def test_parse_alt_shape(self) -> None:
        payload = json.dumps(
            {
                "agent": "geox",
                "status": "healthy",
                "canonical_tools": 37,
                "timestamp": 1749610200.0,
            }
        ).encode()
        rec = AttestationRecord.from_nats_message(payload)
        assert rec is not None
        assert rec.organ == "geox"
        assert rec.tool_count == 37

    def test_parse_falls_back_to_now_on_bad_timestamp(self) -> None:
        payload = json.dumps(
            {
                "organ": "well",
                "verdict": "WELL_HOLD",
                "timestamp": "not-a-timestamp",
            }
        ).encode()
        rec = AttestationRecord.from_nats_message(payload)
        assert rec is not None
        assert rec.organ == "well"
        # Falls back to roughly time.time()
        assert abs(rec.timestamp - time.time()) < 2

    def test_parse_returns_none_for_missing_organ(self) -> None:
        payload = json.dumps(
            {
                "verdict": "HEALTHY",
                "timestamp": "2026-06-11T03:30:00+00:00",
            }
        ).encode()
        rec = AttestationRecord.from_nats_message(payload)
        assert rec is None

    def test_parse_returns_none_for_invalid_json(self) -> None:
        rec = AttestationRecord.from_nats_message(b"not json at all")
        assert rec is None


# ──────────────────────────────────────────────────────────────────────
# Freshness
# ──────────────────────────────────────────────────────────────────────


class TestFreshness:
    def test_fresh_record(self) -> None:
        rec = AttestationRecord(
            organ="arifos",
            timestamp=time.time(),
            tool_count=13,
            registry_truth="VERIFIED",
            verdict="HEALTHY",
        )
        assert rec.is_fresh(freshness_s=60)

    def test_stale_record(self) -> None:
        rec = AttestationRecord(
            organ="arifos",
            timestamp=time.time() - 3600,
            tool_count=13,
            registry_truth="VERIFIED",
            verdict="HEALTHY",
        )
        assert not rec.is_fresh(freshness_s=60)


# ──────────────────────────────────────────────────────────────────────
# AttestationStore
# ──────────────────────────────────────────────────────────────────────


class TestStore:
    def test_ingest_keeps_latest(self) -> None:
        store = AttestationStore()
        rec_now = AttestationRecord(
            organ="arifos",
            timestamp=time.time(),
            tool_count=13,
            registry_truth="VERIFIED",
            verdict="HEALTHY",
        )
        rec_old = AttestationRecord(
            organ="arifos",
            timestamp=time.time() - 100,
            tool_count=12,
            registry_truth="STALE",
            verdict="OLD",
        )
        assert store.ingest(rec_now) is True
        assert store.ingest(rec_old) is False  # out-of-order
        assert store.latest_for("arifos").tool_count == 13

    def test_fresh_organs_filters_by_window(self) -> None:
        store = AttestationStore(freshness_s=60)
        store.ingest(
            AttestationRecord(
                organ="arifos",
                timestamp=time.time(),
                tool_count=13,
                registry_truth="VERIFIED",
                verdict="HEALTHY",
            )
        )
        store.ingest(
            AttestationRecord(
                organ="geox",
                timestamp=time.time() - 3600,
                tool_count=37,
                registry_truth="STALE",
                verdict="STALE",
            )
        )
        fresh = store.fresh_organs()
        assert "arifos" in fresh
        assert "geox" not in fresh


# ──────────────────────────────────────────────────────────────────────
# AttestationVerifier — the metric the brief wants
# ──────────────────────────────────────────────────────────────────────


class TestVerifier:
    def test_empty_store_returns_zero_ratio(self) -> None:
        # An empty store with non-empty expected set returns 0.0,
        # not None. None is reserved for "verifier couldn't run" —
        # an empty store is a clean signal: zero attestations seen.
        verifier = AttestationVerifier(AttestationStore())
        v = verifier.compute()
        assert v.ratio == 0.0
        assert v.n_fresh == 0
        assert v.n_expected == len(DEFAULT_EXPECTED_ORGANS)
        assert v.n_missing == len(DEFAULT_EXPECTED_ORGANS)

    def test_one_organ_fresh_low_ratio(self) -> None:
        store = AttestationStore(freshness_s=60)
        store.ingest(
            AttestationRecord(
                organ="arifos",
                timestamp=time.time(),
                tool_count=13,
                registry_truth="VERIFIED",
                verdict="HEALTHY",
            )
        )
        v = AttestationVerifier(store).compute()
        # 1 fresh / 10 expected = 0.1
        assert v.ratio is not None
        assert v.ratio < 0.5
        assert "missing" in " ".join(v.notes)
        assert "stale" in " ".join(v.notes) or len(v.notes) >= 1

    def test_all_ten_fresh_meets_target(self) -> None:
        store = AttestationStore(freshness_s=60)
        for organ in DEFAULT_EXPECTED_ORGANS:
            store.ingest(
                AttestationRecord(
                    organ=organ,
                    timestamp=time.time(),
                    tool_count=13,
                    registry_truth="VERIFIED",
                    verdict="HEALTHY",
                )
            )
        v = AttestationVerifier(store).compute()
        assert v.ratio is not None
        assert v.ratio == 1.0
        assert v.n_fresh == 10
        assert v.n_missing == 0
        assert any("honesty_ratio >= 0.9" in n for n in v.notes)

    def test_nine_of_ten_still_meets_target(self) -> None:
        """The MAKP target is honesty_ratio >= 0.9. 9/10 = 0.9 exactly."""
        store = AttestationStore(freshness_s=60)
        for organ in list(DEFAULT_EXPECTED_ORGANS)[:9]:
            store.ingest(
                AttestationRecord(
                    organ=organ,
                    timestamp=time.time(),
                    tool_count=13,
                    registry_truth="VERIFIED",
                    verdict="HEALTHY",
                )
            )
        v = AttestationVerifier(store).compute()
        assert v.ratio == 0.9
        assert "missing" in " ".join(v.notes)

    def test_unexpected_organ_does_not_count(self) -> None:
        store = AttestationStore(freshness_s=60)
        store.ingest(
            AttestationRecord(
                organ="mystery-organ",
                timestamp=time.time(),
                tool_count=1,
                registry_truth="VERIFIED",
                verdict="OK",
            )
        )
        v = AttestationVerifier(store).compute()
        # Mystery organ is fresh but not expected; does not raise ratio
        assert v.n_fresh == 1
        assert v.ratio is not None
        assert v.ratio < 0.5

    def test_explicit_expected_organs(self) -> None:
        store = AttestationStore(freshness_s=60)
        store.ingest(
            AttestationRecord(
                organ="arifos",
                timestamp=time.time(),
                tool_count=13,
                registry_truth="VERIFIED",
                verdict="HEALTHY",
            )
        )
        v = AttestationVerifier(store, expected_organs=("arifos",)).compute()
        # 1 fresh / 1 expected = 1.0 — MAKP target met
        assert v.ratio == 1.0
        assert v.n_fresh == 1
        assert v.n_missing == 0
