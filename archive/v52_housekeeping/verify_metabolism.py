import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from arifos.core.metabolizer import Metabolizer

def verify_orthogonal_loop():
    print("Initializing Metabolizer...")
    metabolizer = Metabolizer(enable_execution=True)
    
    print("Starting Stage 000 (VOID)...")
    metabolizer.initialize({"query": "Hello world check"})
    print(f"Stage 000 Context: {metabolizer.context}")
    
    stages = [111, 222, 333, 444, 555, 666, 777, 888, 889, 999]
    
    for stage in stages:
        print(f"\nTransitioning to Stage {stage}...")
        try:
            metabolizer.transition_to(stage)
            print(f"Stage {stage} Result Keys: {list(metabolizer.context.keys())}")
        except Exception as e:
            print(f"FAILED Stage {stage}: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    print("\n✅ Orthogonal Metabolic Loop Verified!")
    return True

if __name__ == "__main__":
    verify_orthogonal_loop()
