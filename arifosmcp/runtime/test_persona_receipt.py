"""
test_persona_receipt.py — backward-compat test for persona-tagged receipts.

Verifies that:
  1. Legacy receipts (no persona fields) still sign + verify correctly
  2. New receipts (with persona_id, persona_evidence_standard, authority_boundary) sign + verify correctly
  3. Schema version bumped from v1 to v2
"""

import sys
from pathlib import Path

# Add runtime dir to path
sys.path.insert(0, str(Path(__file__).parent))

from signed_receipt import (
    SignedReceipt,
    sign_receipt,
    verify_receipt_signature,
    RECEIPT_SCHEMA_VERSION,
)


def test_legacy_receipt():
    """Receipt without persona fields — backward compat."""
    print("\n[TEST 1] Legacy receipt (no persona fields)")
    receipt = sign_receipt(
        event_type="cooling.receipt",
        payload={"event": "test", "value": 42},
        previous_hash="sha256:0000000000000000",
        writer_identity="test-actor",
    )
    assert receipt is not None, "Legacy signing failed"
    assert receipt.persona_id is None, "persona_id should be None for legacy"
    assert receipt.schema_version == "v2", "Schema version should be v2"

    result = verify_receipt_signature(receipt)
    assert result.valid, f"Legacy verification failed: {result.reason}"
    print(f"  ✓ Signed + verified. ID={receipt.receipt_id[:16]}...")


def test_persona_tagged_receipt():
    """Receipt with persona fields — new schema."""
    print("\n[TEST 2] Persona-tagged receipt (with persona_id, evidence standard, authority boundary)")
    # Use service key (sovereign key not available in test env)
    receipt = sign_receipt(
        event_type="makcik.publish",
        payload={"article_slug": "bang-non-pergi-kuching", "claim_count": 16},
        previous_hash="sha256:1111111111111111",
        writer_identity="arif-fazil",
        key_id="service",
        persona_id="Makcik",
        persona_evidence_standard="OBS",
        authority_boundary="Cannot issue sovereign verdicts; cannot mutate production without SEAL",
    )
    assert receipt is not None, "Persona signing failed"
    assert receipt.persona_id == "Makcik", f"persona_id mismatch: {receipt.persona_id}"
    assert receipt.persona_evidence_standard == "OBS"
    assert receipt.authority_boundary is not None
    assert receipt.schema_version == "v2"

    result = verify_receipt_signature(receipt)
    assert result.valid, f"Persona verification failed: {result.reason}"
    print(f"  ✓ Signed + verified. ID={receipt.receipt_id[:16]}...")
    print(f"  ✓ persona_id={receipt.persona_id}, evidence={receipt.persona_evidence_standard}")


def test_signature_payload_diff():
    """Legacy and persona-tagged receipts produce different signature_payload strings."""
    print("\n[TEST 3] signature_payload differs when persona fields set")
    legacy = SignedReceipt(
        receipt_id="rcpt-test",
        event_type="test.event",
        payload_hash="sha256:abc",
        previous_hash="sha256:000",
        writer_identity="test",
        key_id="service",
        timestamp="2026-09-17T00:00:00Z",
        schema_version="v2",
        signature="dummy",
    )
    persona = SignedReceipt(
        receipt_id="rcpt-test",
        event_type="test.event",
        payload_hash="sha256:abc",
        previous_hash="sha256:000",
        writer_identity="test",
        key_id="service",
        timestamp="2026-09-17T00:00:00Z",
        schema_version="v2",
        signature="dummy",
        persona_id="Makcik",
        persona_evidence_standard="OBS",
    )
    assert "persona_id=" not in legacy.signature_payload(), "Legacy should not contain persona lines"
    assert "persona_id=Makcik" in persona.signature_payload(), "Persona should contain persona lines"
    assert legacy.signature_payload() != persona.signature_payload(), "Signatures should differ"
    print("  ✓ Legacy signature_payload has no persona lines")
    print("  ✓ Persona signature_payload contains persona lines")
    print("  ✓ Signatures correctly differ")


def test_schema_version():
    """Schema version is v2."""
    print("\n[TEST 4] Schema version bumped to v2")
    assert RECEIPT_SCHEMA_VERSION == "v2", f"Expected v2, got {RECEIPT_SCHEMA_VERSION}"
    print(f"  ✓ RECEIPT_SCHEMA_VERSION = {RECEIPT_SCHEMA_VERSION}")


if __name__ == "__main__":
    print("=" * 60)
    print("PERSONA-TAGGED RECEIPT BACKWARD-COMPAT TEST")
    print("=" * 60)
    test_legacy_receipt()
    test_persona_tagged_receipt()
    test_signature_payload_diff()
    test_schema_version()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
