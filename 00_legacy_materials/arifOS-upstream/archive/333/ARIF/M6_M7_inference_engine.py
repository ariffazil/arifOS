import json
from model_factory import get_arif_model

# --- A-RIF M6/M7: ASSEMBLY & INFERENCE ENGINE ---

class M6M7InferenceEngine:
    """
    Context Assembly (M6) & Inference (M7): Assembles the 
    grounded context and executes the inference governed by A-RIF.
    """
    
    def __init__(self):
        self.model = get_arif_model()
        # Inference prompt based on APEX_THEORY rules
        self.inference_prompt = """
        You are the A-RIF M7 Inference Engine.
        Generate a response to the SOVEREIGN_MANDATE using ONLY the provided GROUNDED_CONTEXT.
        
        A-RIF CONSTRAINTS:
        1. If the context is insufficient, state exactly what is missing and REFUSE to answer.
        2. Do not include outside knowledge (No hallucinations).
        3. Maintain a clarity score (ΔS ≥ 0).
        4. Every claim must correspond to a specific segment of the context.
        
        OUTPUT FORMAT (JSON ONLY):
        {
            "response": "...",
            "claims": ["claim1", "claim2", ...],
            "confidence": 0.XX,
            "status": "DRAFTED | REJECTED"
        }
        """

    def assemble(self, mandate: dict, validation: dict) -> str:
        """
        M6: Combines the normalized intent and validated segments.
        """
        context_str = "\n".join(validation.get("validated_evidence", []))
        assembled_context = f"""
        SOVEREIGN_MANDATE: {mandate.get('normalized_intent')}
        
        GROUNDED_CONTEXT:
        {context_str}
        
        AMANAH_SCORE: {validation.get('amanah_score', 0.0)}
        """
        return assembled_context

    def infer(self, assembled_context: str) -> dict:
        """
        M7: Perform gated inference.
        """
        messages = [
            {"role": "system", "content": self.inference_prompt},
            {"role": "user", "content": assembled_context}
        ]
        
        response = self.model(messages)
        
        try:
            clean_json = response.strip('```json').strip('```').strip()
            inference_output = json.loads(clean_json)
            return inference_output
        except Exception as e:
            return {
                "status": "REJECTED",
                "error": str(e)
            }

if __name__ == "__main__":
    # Test M6/M7
    m6m7 = M6M7InferenceEngine()
    test_mandate = {"normalized_intent": "How do constitutional floors prevent hallucinations?"}
    test_validation = {
        "amanah_score": 0.95,
        "validated_evidence": [
            "Axiom 1: Floor 2 (Truth) demands all claims match a retrieval segment.",
            "Axiom 2: Floor 4 (Clarity) prevents the addition of noise during inference."
        ]
    }
    
    print("--- A-RIF M6/M7 TEST ---")
    context = m6m7.assemble(test_mandate, test_validation)
    print(f"Assembled context: {context[:200]}...")
    
    result = m6m7.infer(context)
    print(f"Inference result: {json.dumps(result, indent=2)}")
