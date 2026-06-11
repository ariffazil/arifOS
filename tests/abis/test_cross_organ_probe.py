"""
tests/abis/test_cross_organ_probe.py — Unit tests for the cross-organ probe primitive.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json

import pytest

from arifosmcp.abi.cross_organ_probe import (
    OrganStatus,
    fetch_federation_probe,
    probe_receipt,
)


class TestOrganStatus:
    def test_frozen_dataclass(self) -> None:
        s = OrganStatus(organ="arifOS", status="up", http_status=200, latency_ms=6)
        assert s.organ == "arifOS"
        assert s.status == "up"
        assert s.http_status == 200
        assert s.latency_ms == 6


class TestFetchFederationProbe:
    def test_fetch_live_a_forge(self) -> None:
        # A-FORGE is running on the local VPS at :7071.
        probe = fetch_federation_probe("http://127.0.0.1:7071", timeout_s=4.0)
        assert probe.a_forge_ok, f"A-FORGE fetch failed: {probe.a_forge_error}"
        assert probe.n_up >= 5, f"expected at least 5 up organs, got {probe.n_up}"
        # All organs with status=up should have http_status=200
        for o in probe.organs:
            if o.status == "up":
                assert o.http_status == 200, f"{o.organ} up but http={o.http_status}"

    def test_fetch_unreachable_returns_clean_error(self) -> None:
        # No service at :1 — connection refused.
        probe = fetch_federation_probe("http://127.0.0.1:1", timeout_s=1.0)
        assert not probe.a_forge_ok
        assert probe.a_forge_error is not None
        assert (
            "refused" in probe.a_forge_error.lower()
            or "errno" in probe.a_forge_error.lower()
            or "timeout" in probe.a_forge_error.lower()
        )
        assert probe.organs == ()
        assert probe.n_up == 0

    def test_fetch_bad_scheme_rejected(self) -> None:
        probe = fetch_federation_probe("ftp://nope", timeout_s=1.0)
        assert not probe.a_forge_ok
        assert "scheme" in (probe.a_forge_error or "").lower()


class TestProbeReceipt:
    def test_receipt_contains_probe_hash(self) -> None:
        probe = fetch_federation_probe("http://127.0.0.1:7071", timeout_s=4.0)
        if not probe.a_forge_ok:
            pytest.skip("A-FORGE not reachable; skipping receipt test")
        r = probe_receipt(probe, session_id="SEAL-probe-test", actor_id="arif-888")
        assert r["event"] == "CROSS_ORGAN_FEDERATION_PROBE"
        assert r["session_id"] == "SEAL-probe-test"
        assert r["actor_id"] == "arif-888"
        assert "probe_hash_sha256" in r
        # The hash must be 64 hex chars
        h = r["probe_hash_sha256"]
        assert len(h) == 64
        int(h, 16)  # parses as hex

    def test_receipt_deterministic_with_same_inputs(self) -> None:
        """The probe_hash must change if the inputs change."""
        probe = fetch_federation_probe("http://127.0.0.1:7071", timeout_s=4.0)
        if not probe.a_forge_ok:
            pytest.skip("A-FORGE not reachable")
        r1 = probe_receipt(probe, session_id="A")
        r2 = probe_receipt(probe, session_id="B")
        # Different session_id → different hash
        assert r1["probe_hash_sha256"] != r2["probe_hash_sha256"]

    def test_receipt_to_dict_serializable(self) -> None:
        probe = fetch_federation_probe("http://127.0.0.1:7071", timeout_s=4.0)
        if not probe.a_forge_ok:
            pytest.skip("A-FORGE not reachable")
        r = probe_receipt(probe, session_id="x", actor_id="y", extra={"note": "test"})
        # Must serialize cleanly
        text = json.dumps(r, default=str)
        roundtrip = json.loads(text)
        assert roundtrip["session_id"] == "x"
        assert roundtrip["extra"]["note"] == "test"
