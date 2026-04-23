import asyncio
import logging
import sys
import os

# Ensure the correct path for arifOS core
sys.path.append("/root/arifOS")

from core.kernel.planner import Planner
from core.kernel.loop_controller import SabarLoopController
from core.shared.types import Verdict

# Setup Logging to show the Real Metabolism
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("arifOS.Ignition")

async def ignition():
    print("\n--- 🚀 ARF-FORGE: REAL METABOLIC IGNITION (000-999) ---")
    
    # 1. Initialize Planner
    planner = Planner()
    
    # 2. Create a Real Sovereign Goal
    goal = "Synthesize a constitutional amendment proposal for the F7 Humility floor."
    plan = planner.create_plan(goal)
    plan_id = plan.id
    
    # Add a high-stakes reasoning task
    planner.add_task(
        plan_id, 
        "Draft the amendment text for F7 (Humility) to include Ω₀ sliding window detection."
    )
    
    # 3. Initialize the ACTUAL SabarLoopController
    # (No mocks, no stubs. Real physics thresholds.)
    controller = SabarLoopController(
        max_iterations=2, 
        entropy_threshold=0.05, 
        budget=10.0
    )
    
    # 4. RUN THE LOOP
    print(f"Goal: {goal}")
    print("Executing Real Metabolic Cycle...")
    
    result = await controller.run(plan, planner)
    
    print("\n--- 🏁 IGNITION RESULT ---")
    print(f"Status: {result.status}")
    print(f"Iterations: {result.iterations}")
    print(f"Final Entropy: {result.final_entropy:.4f}")
    
    # 5. Check Vault for the Seal
    print("\n--- 📜 VAULT AUDIT ---")
    # We check if a vault seal was created in the expected directory
    vault_dir = "/root/arifOS/VAULT999/seals"
    if os.path.exists(vault_dir):
        seals = os.listdir(vault_dir)
        print(f"Verified Seals in Vault: {len(seals)}")
        for s in seals[:5]:
            print(f" - {s}")
    else:
        print("Warning: VAULT999/seals directory not found.")

if __name__ == "__main__":
    asyncio.run(ignition())
