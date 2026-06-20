import pytest

# Mocks of the ledgers and organs for the loop
class MockCoolingLedger:
    def __init__(self):
        self.entries = {}
    def record_sabar(self, intent, recheck_condition):
        if not recheck_condition:
            raise ValueError("Recheck condition required.")
        cid = f"cooling-{len(self.entries)+1}"
        self.entries[cid] = {"intent": intent, "condition": recheck_condition, "status": "COOLING"}
        return cid
    def satisfy_condition(self, cid):
        if cid in self.entries:
            self.entries[cid]["status"] = "RELEASED"

class MockVault999:
    def __init__(self):
        self.seals = {}
    def seal(self, event_data):
        seal_id = f"vault-receipt-{len(self.seals)+1}"
        self.seals[seal_id] = {"data": event_data, "mutable": False}
        return seal_id
    def edit_seal(self, seal_id, new_data):
        raise PermissionError("VAULT999 event cannot be edited.")

class MockRealityLedger:
    def __init__(self):
        self.lessons = {}
    def learn(self, vault_receipt, prediction, outcome):
        lesson_id = f"lesson-{len(self.lessons)+1}"
        # Does not mutate vault_receipt!
        self.lessons[lesson_id] = {
            "vault_ref": vault_receipt,
            "prediction": prediction,
            "outcome": outcome,
            "lesson_learned": True
        }
        return lesson_id

def test_full_substrate_loop():
    # 1. Initialize Ledgers
    cooling_ledger = MockCoolingLedger()
    vault = MockVault999()
    reality = MockRealityLedger()

    # Step 1 & 2: Proposal triggers SABAR/HOLD
    intent = "Deploy untested patch to production"
    recheck_condition = "Operator reviewed and tests passed"
    
    # Step 3: Cooling Ledger records recheck condition
    cooling_id = cooling_ledger.record_sabar(intent, recheck_condition)
    assert cooling_ledger.entries[cooling_id]["status"] == "COOLING"

    # Step 4: Satisfy recheck condition
    cooling_ledger.satisfy_condition(cooling_id)
    assert cooling_ledger.entries[cooling_id]["status"] == "RELEASED"

    # Step 5 & 6: arifOS issues SEAL and Vault records it
    vault_receipt_id = vault.seal({"action": intent, "status": "AUTHORIZED"})
    assert vault_receipt_id in vault.seals

    # Step 7: A-FORGE performs mocked action
    action_executed = True

    # Step 8, 9, 10: Reality Ledger records outcome and learns
    prediction = "Latency drops by 10ms"
    outcome = "Latency increased by 50ms"
    
    lesson_id = reality.learn(vault_receipt_id, prediction, outcome)
    assert lesson_id in reality.lessons
    
    # Assertions
    # VAULT999 immutable
    with pytest.raises(PermissionError):
        vault.edit_seal(vault_receipt_id, {"action": intent, "status": "TAMPERED"})
        
    print("\\n--- LOOP RESULT ---")
    result = {
      "cooling_created": cooling_id is not None,
      "recheck_condition_required": True,
      "vault999_sealed": vault_receipt_id in vault.seals,
      "vault999_immutable": True,
      "reality_ledger_linked": vault_receipt_id == reality.lessons[lesson_id]["vault_ref"],
      "lesson_created": reality.lessons[lesson_id]["lesson_learned"],
      "loop_complete": action_executed
    }
    for k, v in result.items():
        print(f"{k}: {v}")
    
    assert all(result.values())
