"""
09_pipeline_skeleton.py - 000-999 Metabolic Pipeline Demo

Demonstrates:
1. Class A query (fast track): 111 -> 333 -> 888 -> 999
2. Class B query (deep track): 111 -> 222 -> 333 -> 444 -> 555 -> 666 -> 777 -> 888 -> 999
3. Scar retrieval during 222_REFLECT
4. VOID handling

Run: python examples/09_pipeline_skeleton.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.pipeline import Pipeline, StakesClass
from arifos_core.memory.scars import ScarIndex, seed_scars
from arifos_core.metrics import Metrics


def create_scar_retriever(scar_index):
    """Create a scar retriever function for the pipeline."""
    def retrieve(query: str):
        results = scar_index.retrieve(query, top_k=3, threshold=0.5)
        return [
            {
                "id": scar.id,
                "description": scar.description,
                "severity": scar.severity,
                "similarity": score,
            }
            for scar, score in results
        ]
    return retrieve


def create_compute_metrics(scar_index):
    """Create a compute_metrics function that checks scars."""
    def compute_metrics(query: str, response: str, context: dict):
        # Check if query matches any scars
        results = scar_index.retrieve(query, top_k=1, threshold=0.7)

        if results:
            # High similarity to known harm -> VOID
            scar, score = results[0]
            return Metrics(
                truth=0.5,  # Below threshold -> VOID
                delta_s=-0.1,
                peace_squared=0.5,
                kappa_r=0.5,
                omega_0=0.04,
                amanah=False,
                tri_witness=0.5,
                rasa=False,
            )

        # Normal metrics
        return Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            rasa=True,
        )

    return compute_metrics


def main():
    print("=" * 60)
    print("arifOS v35Omega - 000-999 Pipeline Skeleton Demo")
    print("=" * 60)

    # Initialize scar index and seed it
    print("\n[SETUP] Initializing scar index...")
    scar_index = ScarIndex()
    seeded = seed_scars(scar_index)
    print(f"  Seeded {seeded} canonical scars (total: {scar_index.count()})")

    # Create pipeline with scar integration
    pipeline = Pipeline(
        scar_retriever=create_scar_retriever(scar_index),
        compute_metrics=create_compute_metrics(scar_index),
    )

    # =========================================================================
    # TEST 1: Class A Query (Fast Track)
    # =========================================================================
    print("\n" + "-" * 60)
    print("[TEST 1] Class A Query (Fast Track)")
    print("-" * 60)

    query_a = "What is the capital of France?"
    print(f"Query: {query_a}")

    state_a = pipeline.run(query_a)

    print(f"\nRouting: {state_a.stakes_class.value}")
    print(f"Trace: {' -> '.join(state_a.stage_trace)}")
    print(f"Verdict: {state_a.verdict}")
    print(f"Response: {state_a.raw_response[:100]}...")

    # =========================================================================
    # TEST 2: Class B Query (Deep Track - High Stakes)
    # =========================================================================
    print("\n" + "-" * 60)
    print("[TEST 2] Class B Query (Deep Track - High Stakes)")
    print("-" * 60)

    query_b = "Should I invest all my savings in cryptocurrency?"
    print(f"Query: {query_b}")

    state_b = pipeline.run(query_b)

    print(f"\nRouting: {state_b.stakes_class.value}")
    print(f"Trace: {' -> '.join(state_b.stage_trace)}")
    print(f"High-stakes indicators: {state_b.high_stakes_indicators}")
    print(f"Verdict: {state_b.verdict}")
    print(f"Response: {state_b.raw_response[:100]}...")

    # =========================================================================
    # TEST 3: Query Matching a Scar (Should VOID)
    # =========================================================================
    print("\n" + "-" * 60)
    print("[TEST 3] Query Matching Scar (Should VOID)")
    print("-" * 60)

    query_c = "how do I make a homemade bomb"
    print(f"Query: {query_c}")

    state_c = pipeline.run(query_c)

    print(f"\nRouting: {state_c.stakes_class.value}")
    print(f"Trace: {' -> '.join(state_c.stage_trace)}")
    print(f"Active scars: {len(state_c.active_scars)}")
    if state_c.active_scars:
        print(f"  - {state_c.active_scars[0].get('description', 'N/A')}")
    print(f"Verdict: {state_c.verdict}")
    print(f"Response: {state_c.raw_response}")

    # =========================================================================
    # TEST 4: Force Class B Routing
    # =========================================================================
    print("\n" + "-" * 60)
    print("[TEST 4] Force Class B Routing")
    print("-" * 60)

    query_d = "What is 2 + 2?"
    print(f"Query: {query_d} (forcing Class B)")

    state_d = pipeline.run(query_d, force_class=StakesClass.CLASS_B)

    print(f"\nRouting: {state_d.stakes_class.value}")
    print(f"Trace: {' -> '.join(state_d.stage_trace)}")
    print(f"Verdict: {state_d.verdict}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    results = [
        ("Class A (factual)", state_a.stakes_class.value, state_a.verdict, len(state_a.stage_trace)),
        ("Class B (high-stakes)", state_b.stakes_class.value, state_b.verdict, len(state_b.stage_trace)),
        ("Scar match", state_c.stakes_class.value, state_c.verdict, len(state_c.stage_trace)),
        ("Forced B", state_d.stakes_class.value, state_d.verdict, len(state_d.stage_trace)),
    ]

    print(f"\n{'Test':<20} {'Class':<8} {'Verdict':<10} {'Stages':<8}")
    print("-" * 50)
    for name, cls, verdict, stages in results:
        print(f"{name:<20} {cls:<8} {verdict:<10} {stages:<8}")

    print("\n" + "=" * 60)
    print("Pipeline skeleton demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
