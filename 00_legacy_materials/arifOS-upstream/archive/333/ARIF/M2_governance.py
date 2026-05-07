import json

# --- A-RIF M2: GOVERNANCE GATE (TRIAGE) ---


class M2GovernanceGate:
    """
    Governance Gate (M2): Triage the normalized mandate against
    the 13 Constitutional Floors to determine if the pipeline proceeds.
    """

    def __init__(self):
        # Floor Configuration (Thresholds)
        self.floors = {
            "F01_IDENTITY": 1.0,  # Human Sovereign (Mandatory)
            "F02_TRUTH": 0.99,  # Grounded Truth (A-RIF Core)
            "F03_WITNESS": 1.0,  # Auditability
            "F04_CLARITY": 0.8,  # Intent Clarity (M1 output check)
            "F10_ONTOLOGY": 0.7,  # Canonical Consistency
        }

    def triage(self, mandate: dict) -> dict:
        """
        Evaluates the mandate's 'Safety' and 'Clarity'.
        """
        # 1. Check F04 (Clarity)
        clarity_score = 1.0 if mandate.get("status") == "APPROVED" else 0.0

        # 2. Check F01 (Identity)
        # In a real system, we'd verify the cryptographic signature of the Sovereign.
        # For this prototype, we assume human context.
        identity_verified = True

        # 3. Decision
        if clarity_score >= self.floors["F04_CLARITY"] and identity_verified:
            return {
                "decision": "PROCEED",
                "risk_score": 0.05,
                "floors_evaluated": ["F01", "F04"],
                "next_module": "M3_Interpretation",
            }
        else:
            return {
                "decision": "REJECT",
                "risk_score": 1.0,
                "failing_floors": ["F04"] if clarity_score < 0.8 else ["F01"],
                "rejection_reason": "Insufficient clarity or unverified identity.",
            }


if __name__ == "__main__":
    # Test M2 logic
    m2 = M2GovernanceGate()

    # Example Approved Mandate
    valid_mandate = {
        "action": "retrieve_theory",
        "entity": "hallucination_prevention",
        "priority": "high",
        "context": "theory",
        "normalized_intent": "Retrieve APEX_THEORY on hallucination prevention.",
        "status": "APPROVED",
    }

    # Example Rejected Mandate
    invalid_mandate = {"action": "unknown", "status": "AMBIGUOUS"}

    print("--- A-RIF M2 TEST ---")
    print(f"Valid: {json.dumps(m2.triage(valid_mandate), indent=2)}")
    print(f"\nInvalid: {json.dumps(m2.triage(invalid_mandate), indent=2)}")
