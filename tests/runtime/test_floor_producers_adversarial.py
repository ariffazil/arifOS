"""
test_floor_producers_adversarial.py — Phase 3 adversarial tests (test-first).

ARIFOS::MEASUREMENT_CLOSURE_INIT::2026-10-10 · bounded tranche F2/F11/F12/F13.

These tests are written BEFORE the implementation. They prove that the future
producer (`arifosmcp.runtime.floor_producers`) REJECTS the ten fabrication
modes the measurement contracts forbid. Until Phase 4 lands the producer, these
tests fail on ImportError — which is the intended "no instrument exists yet"
state. After Phase 4, they must PASS (the instrument rejects the fabrication),
and a truthful FAIL/STALE/CONTRADICTED/UNMEASURED result is acceptable.

The producer under test is PURE: it takes an injected `sources` dict (evidence)
and returns a structured signal. No live network, no ledger mutation.

Contract per floor: see
/root/forge_work/measurement-closure-20261010/FLOOR_MEASUREMENT_CONTRACTS.md
"""

from __future__ import annotations

import pytest

# The producer module to be implemented in Phase 4.
from arifosmcp.runtime.floor_producers import (  # noqa: F401
    FLOOR_STATUS,
    collect_floor_producer_signal,
)


# ── F2 TRUTH ──────────────────────────────────────────────────────────────


def test_f2_rejects_pass_from_unmeasured_default():
    """Fabrication mode: PASS rendered from a placeholder origin must be rejected."""
    sources = {
        "floor_provenance": {"F2": "unmeasured_default:empty_kernel_signal"},
        "resolved_floors": {"F2": 0.5},  # value equals _FLOOR_DEFAULTS — the greenwash
    }
    sig = collect_floor_producer_signal("F2", sources=sources)
    assert sig["status"] == "FAIL"  # never silently auto-pass


def test_f2_accepts_real_provenance_coverage():
    """A floor with a non-placeholder origin is measured, not fabricated."""
    sources = {
        "floor_provenance": {"F2": "governance_kernel"},
        "resolved_floors": {"F2": 0.81},
    }
    sig = collect_floor_producer_signal("F2", sources=sources)
    assert sig["status"] in ("PASS", "FAIL")  # a real measurement, judged by threshold
    assert sig["origin"] != "unmeasured_default"


def test_f2_unmeasured_when_provenance_absent():
    """Missing provenance map → UNMEASURED, not PASS."""
    sig = collect_floor_producer_signal("F2", sources={})
    assert sig["status"] == "UNMEASURED"


def test_f2_contradiction_when_origin_lies():
    """Provenance says governance_kernel but value equals the default → CONTRADICTED."""
    sources = {
        "floor_provenance": {"F2": "governance_kernel"},
        "resolved_floors": {"F2": 0.5},  # equals default despite claimed origin
        "floor_defaults": {"F2": 0.5},
    }
    sig = collect_floor_producer_signal("F2", sources=sources)
    assert sig["status"] == "CONTRADICTED"


# ── F11 AUDIT ─────────────────────────────────────────────────────────────


def test_f11_rejects_null_actor_receipts():
    """Receipts missing actor/step must count as unattributable, not be skipped."""
    sources = {
        "receipts": [
            {"actor_id": "333-AGI", "step_type": "Execute", "floor_verdict": "Pass"},
            {"actor_id": None, "step_type": "Execute", "floor_verdict": "Pass"},  # fabrication
        ]
    }
    sig = collect_floor_producer_signal("F11", sources=sources)
    assert sig["status"] == "FAIL"
    assert sig.get("unattributable", 0) >= 1


def test_f11_rejects_broken_chain():
    """A previous_receipt_hash pointing nowhere → CONTRADICTED (broken chain)."""
    sources = {
        "receipts": [
            {
                "actor_id": "A",
                "step_type": "Execute",
                "previous_receipt_hash": "sha256:deadbeef",  # not in ledger
            }
        ]
    }
    sig = collect_floor_producer_signal("F11", sources=sources)
    assert sig["status"] in ("FAIL", "CONTRADICTED")


def test_f11_unmeasured_when_ledger_empty():
    """Empty ledger → UNMEASURED, not PASS."""
    sig = collect_floor_producer_signal("F11", sources={"receipts": []})
    assert sig["status"] == "UNMEASURED"


# ── F12 INJECTION ─────────────────────────────────────────────────────────


def test_f12_fails_when_auto_sign_open():
    """Auto-sign enabled = name-elevation surface OPEN → FAIL."""
    sources = {"auto_sign_allowed": True, "trust_snapshot": {"request_trust": "PROXIED"}}
    sig = collect_floor_producer_signal("F12", sources=sources)
    assert sig["status"] == "FAIL"


def test_f12_passes_when_auto_sign_denied():
    """Auto-sign disabled = elevation surface closed."""
    sources = {"auto_sign_allowed": False, "trust_snapshot": {"request_trust": "LOCAL_LOOPBACK"}}
    sig = collect_floor_producer_signal("F12", sources=sources)
    assert sig["status"] == "PASS"


def test_f12_contradiction_when_doc_code_drift():
    """Declared default 1 but effective default 0 → CONTRADICTED (known drift)."""
    sources = {
        "auto_sign_allowed": False,
        "declared_default": "1",
        "effective_default": "0",
    }
    sig = collect_floor_producer_signal("F12", sources=sources)
    assert sig["status"] == "CONTRADICTED"


# ── F13 SOVEREIGN ─────────────────────────────────────────────────────────


def test_f13_rejects_machine_self_acceptance():
    """A seal attributing a machine SEAL to its own mutation → FAIL (self-acceptance)."""
    sources = {
        "seals": [
            {"actor": "333-AGI", "verdict": "SEAL", "self_mutation": True}  # fabrication
        ]
    }
    sig = collect_floor_producer_signal("F13", sources=sources)
    assert sig["status"] == "FAIL"


def test_f13_accepts_sovereign_seal():
    """A sovereign-attributed seal is a valid human-acceptance signal."""
    sources = {"seals": [{"actor": "arif", "verdict": "SEAL", "self_mutation": False}]}
    sig = collect_floor_producer_signal("F13", sources=sources)
    assert sig["status"] == "PASS"


def test_f13_unmeasured_when_chain_empty():
    """Empty seal chain → UNMEASURED, not PASS."""
    sig = collect_floor_producer_signal("F13", sources={"seals": []})
    assert sig["status"] == "UNMEASURED"
