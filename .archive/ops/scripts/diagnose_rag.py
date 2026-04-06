import os
import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(os.getcwd()) / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from arifos_rag import ConstitutionalRAG

    rag = ConstitutionalRAG()
    print("Connecting to Qdrant...")
    health = rag.health_check()
    print(f"Health Check: {health}")

    print("\nAttempting retrieval for 'test'...")
    results = rag.retrieve(query="test", top_k=1)
    print(f"Results: {len(results)}")
    for r in results:
        print(f" - {r.source}/{r.path} (score: {r.score})")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
