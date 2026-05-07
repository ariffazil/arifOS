import json
from model_factory import get_arif_model

# --- A-RIF M1: INTAKE MODULE (INTENT NORMALIZATION) ---


class M1Intake:
    """
    Intake Module (M1): Responsible for normalizing, interpreting, and
    bounding raw user intent before it enters the A-RIF pipeline.
    """

    def __init__(self):
        self.model = get_arif_model()
        # Initialize the normalization prompt based on APEX_THEORY axioms
        self.normalization_prompt = """
        You are the A-RIF M1 Normalizer.
        Your mission is to transform raw USER_INPUT into a structured SOVEREIGN_MANDATE.

        RULES:
        1. Remove conversational noise (e.g., "Hey", "Can you please", "Thanks").
        2. Identify the core 'Action' and 'Entity'.
        3. Assign a 'Priority' based on the 13 Floors (e.g., high for F1/F2).
        4. Detect the 'Context' (e.g., infrastructure, theory, wealth).
        5. If the input is ambiguous or violates sovereignty, flag as 'INPUT_AMBIGUOUS'.

        OUTPUT FORMAT (JSON ONLY):
        {
            "action": "...",
            "entity": "...",
            "priority": "low | medium | high",
            "context": "...",
            "normalized_intent": "...",
            "status": "APPROVED | AMBIGUOUS"
        }
        """

    def normalize(self, raw_input: str) -> dict:
        """
        Normalizes raw text into a structured JSON mandate.
        """
        # We leverage the model for semantic normalization while maintaining structural rigidity.
        messages = [
            {"role": "system", "content": self.normalization_prompt},
            {"role": "user", "content": f"RAW_INPUT: {raw_input}"},
        ]

        # In a real system, we'd use a light model (like smollm2) for M1 speed.
        response = self.model(messages)

        try:
            # Clean possible markdown wrap from the LLM response
            clean_json = response.strip("```json").strip("```").strip()
            mandate = json.loads(clean_json)
            return mandate
        except Exception as e:
            return {
                "status": "INPUT_AMBIGUOUS",
                "error": f"Normalization failed: {str(e)}",
                "raw_input": raw_input,
            }


if __name__ == "__main__":
    # Test M1
    m1 = M1Intake()
    test_inputs = [
        "Hey assistant, can you tell me what the truth floor says about hallucinations?",
        "Move the backup file to the vault now please.",
        "What is the meaning of life?",
    ]

    print("--- A-RIF M1 TEST ---")
    for inp in test_inputs:
        mandate = m1.normalize(inp)
        print(f"\nRaw: {inp}\nNormalized: {json.dumps(mandate, indent=2)}")
