import json
import os
from datetime import datetime

# --- A-RIF M8/M9/M10: VERIFICATION, DECISION & AUDIT ---


class M8M9M10DeciderAudit:
    """
    Output Verification (M8), Decision (M9), and Audit (M10):
    The final constitutional seal on any A-RIF output.
    """

    def __init__(
        self, ledger_path: str = "C:/ariffazil/arifOS/data/COOLING_LEDGER.json"
    ):
        self.ledger_path = ledger_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)

    def verify_response(self, inference_result: dict, validation: dict) -> dict:
        """
        M8: Verify that every claim is grounded back in the validated evidence.
        """
        # In a production system, this would be a separate, smaller model pass.
        # For this prototype, we'll calculate a 'verification_score' based on claim match.
        claims = inference_result.get("claims", [])
        evidence = validation.get("validated_evidence", [])

        # Simple string-match logic for prototype
        verified_count = 0
        for claim in claims:
            if any(claim.lower()[:20] in ev.lower() for ev in evidence):
                verified_count += 1

        verification_score = verified_count / len(claims) if claims else 0.0

        return {
            "verification_score": verification_score,
            "verified_claims": verified_count,
            "total_claims": len(claims),
            "status": "VERIFIED" if verification_score > 0.8 else "UNVERIFIED",
        }

    def decide(self, mandate: dict, verification: dict, inference_result: dict) -> dict:
        """
        M9: The Decision Gate.
        """
        # Decisions based on A-RIF Rules:
        # F13 Veto possibility, F02 Truth floor check.
        if verification.get("verification_score", 0.0) >= 0.99:
            status = "APPROVED"
        elif verification.get("verification_score", 0.0) >= 0.8:
            status = "PARTIAL"
        else:
            status = "VOID"

        return {
            "final_status": status,
            "mandate_id": mandate.get("id", "undefined"),
            "seal": "DITEMPA BUKAN DIBERI",
            "output": (
                inference_result.get("response")
                if status != "VOID"
                else "REDACTED: INSUFFICIENT TRUTH"
            ),
        }

    def audit_trail(self, mandate: dict, decision: dict, audit_data: dict):
        """
        M10: The Cooling Ledger audit trail.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "mandate": mandate,
            "decision": decision,
            "audit_data": audit_data,
            "protocol": "A-RIF v1.0.0",
        }

        # Append to the ledger
        try:
            ledger = []
            if os.path.exists(self.ledger_path):
                with open(self.ledger_path, "r") as f:
                    ledger = json.load(f)

            ledger.append(entry)

            with open(self.ledger_path, "w") as f:
                json.dump(ledger, indent=2, fp=f)

            return True
        except Exception as e:
            print(f"Failed to write to audit ledger: {str(e)}")
            return False


if __name__ == "__main__":
    # Test M8/M9/M10
    m8m9m10 = M8M9M10DeciderAudit(
        ledger_path="C:/ariffazil/arifOS/data/MOCK_LEDGER.json"
    )

    test_mandate = {
        "id": "MANDATE-001",
        "normalized_intent": "How to prevent hallucinations?",
    }
    test_validation = {"validated_evidence": ["Floor 2 (Truth) demands grounding."]}
    test_inference = {
        "response": "You prevent them using Floor 2.",
        "claims": ["Floor 2 demands grounding."],
    }

    print("--- A-RIF M8/M9/M10 TEST ---")
    verification = m8m9m10.verify_response(test_inference, test_validation)
    print(f"Verification: {json.dumps(verification, indent=2)}")

    decision = m8m9m10.decide(test_mandate, verification, test_inference)
    print(f"Decision: {json.dumps(decision, indent=2)}")

    audit_success = m8m9m10.audit_trail(
        test_mandate, decision, {"trace": "Prototype run success."}
    )
    print(f"Audit Log Success: {audit_success}")
