import json
from datasets import load_dataset
from model_factory import get_arif_model

# --- A-RIF M4/M5: RETRIEVAL & EVIDENCE VALIDATION ---

class M4M5RetrievalValidation:
    """
    Retrieval (M4) & Validation (M5): Responsible for fetching 
    canonical truths and scoring them for sufficiency.
    """
    
    def __init__(self, dataset_name: str = "ariffazil/APEX_THEORY"):
        self.dataset_id = dataset_name
        self.dataset = None
        self.model = get_arif_model()
        
    def load_canon(self):
        """
        Loads the APEX_THEORY dataset from Hugging Face.
        """
        if not self.dataset:
            try:
                # We load the dataset (assuming 'train' split contains the canon text)
                self.dataset = load_dataset(self.dataset_id, split="train")
            except Exception as e:
                print(f"Failed to load dataset {self.dataset_id}: {str(e)}")
                return None
        return self.dataset

    def search_and_retrieve(self, queries: list) -> list:
        """
        M4: Simple semantic search (mocked for this prototype) 
        against the local cache or live HF dataset.
        """
        # In a production hybrid system, this would use Qdrant/LanceDB.
        # For this prototype, we'll perform a basic keyword search over the loaded dataset.
        ds = self.load_canon()
        if not ds:
            return []
            
        # Retrieval Logic (Keyword match across 'text' or 'content' columns)
        results = []
        for q in queries:
            # We look for queries in the dataset rows
            # This is a simplified search for the prototype.
            for row in ds:
                text = row.get("text", "") or row.get("content", "")
                if any(word.lower() in text.lower() for word in q.split()):
                    results.append({
                        "id": row.get("id", "unknown"),
                        "text": text[:500] + "...", # Truncate for validation
                        "source": self.dataset_id,
                        "relevance": 0.0 # To be scored by M5
                    })
                if len(results) >= 5: # Top 5 results per query
                    break
        
        return results

    def validate_evidence(self, results: list, normalized_intent: str) -> dict:
        """
        M5: Evidence Validation using the A-RIF 'sufficiency_score'.
        """
        # Scoring Prompt
        scoring_prompt = """
        You are the A-RIF M5 Validator.
        Evaluate the provided EVIDENCE against the INTENT.
        Return a 'sufficiency_score' (0.0 to 1.0).
        If the evidence does not directly answer the intent, the score MUST be < 0.5.
        
        OUTPUT FORMAT (JSON ONLY):
        {
            "sufficiency_score": 0.XX,
            "amanah_score": 0.XX, 
            "status": "SUFFICIENT | INSUFFICIENT",
            "validated_evidence": ["segment1", "segment2"]
        }
        """
        
        evidence_text = "\n\n".join([r["text"] for r in results[:10]])
        messages = [
            {"role": "system", "content": scoring_prompt},
            {"role": "user", "content": f"INTENT: {normalized_intent}\n\nEVIDENCE:\n{evidence_text}"}
        ]
        
        response = self.model(messages)
        
        try:
            clean_json = response.strip('```json').strip('```').strip()
            validation = json.loads(clean_json)
            return validation
        except Exception as e:
            return {
                "sufficiency_score": 0.0,
                "status": "INSUFFICIENT",
                "error": str(e)
            }

if __name__ == "__main__":
    # Test M4/M5
    m4m5 = M4M5RetrievalValidation()
    intent = "How do the 13 constitutional floors prevent hallucinations?"
    queries = ["13 constitutional floors", "prevent hallucinations", "truth-gated inference"]
    
    print("--- A-RIF M4/M5 TEST ---")
    results = m4m5.search_and_retrieve(queries)
    print(f"Retrieved {len(results)} potential segments.")
    
    validation = m4m5.validate_evidence(results, intent)
    print(f"Validation: {json.dumps(validation, indent=2)}")
