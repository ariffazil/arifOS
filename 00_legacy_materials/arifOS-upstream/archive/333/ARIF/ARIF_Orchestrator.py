import json

# --- A-RIF: CENTRAL ORCHESTRATOR ---

# Importing the M-Modules
from M1_intake import M1Intake
from M2_governance import M2GovernanceGate
from M3_interpretation import M3Interpretation
from M4_M5_retrieval_validation import M4M5RetrievalValidation
from M6_M7_inference_engine import M6M7InferenceEngine
from M8_M9_M10_decider_audit import ARIFDeciderAudit
from M11_table_qa import M11TableQA
from M12_doc_qa import M12DocQA


class ARIFOrchestrator:
    """
    The central coordinator for the A-RIF pipeline.
    It executes M1-M10 sequentially to produce a governed outcome.
    """

    def __init__(self):
        self.m1 = M1Intake()
        self.m2 = M2GovernanceGate()
        self.m3 = M3Interpretation()
        self.m4m5 = M4M5RetrievalValidation()
        self.m6m7 = M6M7InferenceEngine()
        self.m8m9m10 = ARIFDeciderAudit()

        self.m11 = M11TableQA()
        self.m12 = M12DocQA()

    def process_sovereign_intent(self, raw_input: str, sensory_context: dict = None) -> dict:
        """
        Executes the full A-RIF pipeline for a given input.
        """
        print(f"\n[A-RIF] START: Processing intent: '{raw_input[:50]}...'")

        # M1: Intake & Normalization
        mandate = self.m1.normalize(raw_input)
        print(f"[A-RIF] M1: Normalized Intent: {mandate.get('normalized_intent')}")

        # M2: Governance Gate (Triage)
        triage_report = self.m2.triage(mandate)
        print(f"[A-RIF] M2: Governance Decision: {triage_report.get('decision')}")

        if triage_report.get("decision") == "REJECT":
            return {"status": "REJECTED", "reason": triage_report.get("rejection_reason")}

        # M3: Query Interpretation
        interpretation = self.m3.interpret(mandate.get("normalized_intent"))
        print(f"[A-RIF] M3: Generated {len(interpretation.get('queries', []))} search queries.")

        # M4/M5: Retrieval & Evidence Validation
        results = self.m4m5.search_and_retrieve(interpretation.get("queries", []))
        validation = self.m4m5.validate_evidence(results, mandate.get("normalized_intent"))
        print(
            f"[A-RIF] M4/M5: Evidence Sufficiency Score: {validation.get('sufficiency_score', 0.0)}"
        )

        if validation.get("sufficiency_score", 0.0) < 0.5:
            # M9 Early rejection at decision gate
            print("[A-RIF] M9 Error: Evidence Insufficient. Aborting Inference.")
            return {"status": "VOID", "reason": "Insufficient evidence segments found."}

        # M6/M7: Assembly & Inference
        context = self.m6m7.assemble(mandate, validation)
        inference_result = self.m6m7.infer(context)
        print(f"[A-RIF] M6/M7: Inference Status: {inference_result.get('status')}")

        # M8/M9/M10: Verification, Decision & Audit
        verification = self.m8m9m10.verify_response(inference_result, validation)
        decision = self.m8m9m10.decide(mandate, verification, inference_result)

        # Final Audit
        self.m8m9m10.audit_trail(
            mandate,
            decision,
            {
                "triage": triage_report,
                "interpretation": interpretation,
                "verification": verification,
            },
        )

        print(f"[A-RIF] M9/M10: FINAL DECISION: {decision.get('final_status')}")
        return decision


if __name__ == "__main__":
    # Test Full A-RIF Flow
    orchestrator = ARIFOrchestrator()

    # Example input
    raw_query = "What do the 13 constitutional floors say about truth and witness?"

    final_outcome = orchestrator.process_sovereign_intent(raw_query)

    print("\n" + "=" * 40)
    print("FINAL A-RIF RESULT")
    print("=" * 40)
    print(json.dumps(final_outcome, indent=2))
