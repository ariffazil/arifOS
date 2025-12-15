"""
05_vector_witness_demo.py — Demonstrate L3 witness retrieval.

This shows how a developer can plug in a simple vector DB backend and
retrieve evidence-as-witness under arifOS v33Ω.

Backend here is a toy class to illustrate the concept.
"""

from arifos_core.memory.vector_adapter import VectorAdapter


# -------------------------------------------------------------------
# Toy backend for demonstration
# -------------------------------------------------------------------
class SimpleVectorDB:
    def __init__(self):
        self.docs = [
            ("APEX PRIME is the judiciary of arifOS.", 0.91),
            ("Vault-999 stores constitutional memory.", 0.87),
            ("Phoenix-72 handles scar → law amendments.", 0.82),
        ]

    def search(self, query: str, top_k: int = 3):
        # naive scoring for demo
        return self.docs[:top_k]


# -------------------------------------------------------------------
# Demo script
# -------------------------------------------------------------------
if __name__ == "__main__":
    backend = SimpleVectorDB()
    adapter = VectorAdapter(backend)

    query = "Explain APEX PRIME"
    witness_hits = adapter.as_dicts(query, top_k=2)

    print("=== L3 Witness Results ===")
    for hit in witness_hits:
        print(hit)