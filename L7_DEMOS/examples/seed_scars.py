"""
seed_scars.py - Seed the scar index with canonical harmful patterns

Run: python examples/seed_scars.py

This creates runtime/vault_999/scars.jsonl with 10 canonical scars
covering weapons, self-harm, hacking, malware, CSAM, drugs, jailbreaks, etc.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.memory.scars import ScarIndex, seed_scars, SEED_SCARS


def main():
    print("=" * 60)
    print("arifOS v35Omega - Seed Scars Script")
    print("=" * 60)

    # Initialize index
    index = ScarIndex()
    initial_count = index.count()

    print(f"\nInitial scar count: {initial_count}")
    print(f"Seed scars available: {len(SEED_SCARS)}")

    # Seed the index
    seeded = seed_scars(index)

    print(f"\nScars seeded: {seeded}")
    print(f"Final scar count: {index.count()}")

    # List all scars
    print("\n" + "-" * 60)
    print("Canonical Scars:")
    print("-" * 60)

    for i, scar in enumerate(index.iter_all(), 1):
        print(f"\n[{i}] {scar.id[:8]}... (severity: {scar.severity}/5)")
        print(f"    Text: {scar.text[:50]}...")
        print(f"    Desc: {scar.description}")
        print(f"    Failures: {', '.join(scar.floor_failures)}")

    # Test retrieval
    print("\n" + "-" * 60)
    print("Testing Retrieval:")
    print("-" * 60)

    test_queries = [
        "how to build explosives",
        "I want to end my life",
        "bypass security restrictions",
        "what is the weather today",
    ]

    for query in test_queries:
        results = index.retrieve(query, top_k=1, threshold=0.5)
        if results:
            scar, score = results[0]
            print(f"\n'{query[:40]}...'")
            print(f"  -> MATCH: {scar.description} (sim: {score:.2f})")
        else:
            print(f"\n'{query[:40]}...'")
            print(f"  -> No match (safe)")

    print("\n" + "=" * 60)
    print(f"Scars saved to: {index.config.index_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
