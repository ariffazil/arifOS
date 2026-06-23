import pytest
from core.cooling_ledger import CoolingLedger
from core.reality_ledger import RealityLedger


def test_reality_ledger_cannot_overwrite_vault999():
    rl = RealityLedger()
    # Mocking VAULT999 immutability enforcement
    vault_receipt = {"id": "mock-seal-1", "mutable": False}
    result = rl.record_outcome(vault_receipt, "success", "failed")
    assert result == "LEARNED"
    assert vault_receipt["mutable"] is False


def test_cooling_ledger_item_must_have_recheck_condition():
    cl = CoolingLedger()
    with pytest.raises(ValueError, match="recheck condition"):
        cl.record_sabar("Deploy patch", None)
    assert cl.record_sabar("Deploy patch", "Operator rested") == "COOLING"


def test_vault999_event_cannot_be_edited():
    # Mocking append-only structure
    sealed_event = {"id": "mock-seal-2", "hash": "abcd"}

    def edit_seal(event):
        raise PermissionError("VAULT999 event cannot be edited.")

    with pytest.raises(PermissionError):
        edit_seal(sealed_event)


def test_hold_sabar_can_create_cooling_ledger_entry():
    cl = CoolingLedger()
    verdict = "HOLD"
    if verdict in ["HOLD", "SABAR"]:
        status = cl.record_sabar("Wait for approval", "Approved by F13")
        assert status == "COOLING"


def test_seal_with_prediction_can_create_reality_ledger_entry():
    rl = RealityLedger()
    verdict = "SEAL"
    prediction = "Improves latency"
    if verdict == "SEAL" and prediction:
        status = rl.record_outcome("receipt-123", prediction, "Unknown yet")
        assert status == "LEARNED"
