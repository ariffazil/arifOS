import json
from model_factory import get_arif_model

# --- A-RIF M3: QUERY INTERPRETATION ---

class M3Interpretation:
    """
    Query Interpretation (M3): Decomposes the normalized intent 
    into a set of queries optimized for retrieval from the APEX_THEORY canon.
    """
    
    def __init__(self):
        self.model = get_arif_model()
        # Interpretation prompt using the ARIF context
        self.interpretation_prompt = """
        You are the A-RIF M3 Interpreter.
        Your mission is to decompose a SOVEREIGN_MANDATE into 1-3 distinct SEARCH_QUERIES 
        optimized for retrieval from the 'ariffazil/APEX_THEORY' Hugging Face dataset.
        
        Axioms to consider:
        - 13 Constitutional Floors
        - ΔΩΨ Invariants
        - Truth-Gated Inference
        
        OUTPUT FORMAT (JSON ONLY):
        {
            "queries": ["query1", "query2", ...],
            "topical_clusters": ["..."],
            "depth": "surface | deep | exhaustive"
        }
        """

    def interpret(self, normalized_intent: str) -> dict:
        """
        Decomposes text into structural search queries.
        """
        messages = [
            {"role": "system", "content": self.interpretation_prompt},
            {"role": "user", "content": f"INTENT: {normalized_intent}"}
        ]
        
        response = self.model(messages)
        
        try:
            clean_json = response.strip('```json').strip('```').strip()
            interpretation = json.loads(clean_json)
            return interpretation
        except Exception as e:
            # Fallback to direct intent
            return {
                "queries": [normalized_intent],
                "error": str(e)
            }

if __name__ == "__main__":
    # Test M3
    m3 = M3Interpretation()
    test_intent = "Retrieve APEX_THEORY on how to prevent hallucinations using constitutional floors."
    
    print("--- A-RIF M3 TEST ---")
    interpretation = m3.interpret(test_intent)
    print(f"Intent: {test_intent}")
    print(f"Queries: {json.dumps(interpretation['queries'], indent=2)}")
