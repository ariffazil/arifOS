"""
proof_of_causality.py - The Fuse Box for AI Agency

DEMONSTRATION:
    1. We define a Constitutional Law (The Fuse): "No Global Destruction".
    2. We unleash a "Rogue Agent" (simulated) that wants to destroy the internet.
    3. We show how the Python Kernel (The Governor) intercepts the Action Intent
       BEFORE it touches the capability layer.

    This proves that 'Code' can govern 'Causality'.
"""

from typing import Literal

import dspy

# --- 1. THE CONSTITUTION (The Fuse) ---

def check_blast_radius(action: str) -> bool:
    """
    F5 Peace^2 Floor:
    Returns True if action is local/reversible.
    Returns False if action is global/irreversible.
    """
    FORBIDDEN_KEYWORDS = ["internet", "network", "cloud", "aws", "delete_all"]
    action_lower = action.lower()

    # Simple semantic check (in v46 this would be a neuro-symbolic classifier)
    for kw in FORBIDDEN_KEYWORDS:
        if kw in action_lower:
            return False  # Fuse Blown
    return True

# --- 2. THE NEURO-SYMBOLIC SIGNATURE (The Interface) ---

class AgentAction(dspy.Signature):
    """
    An agentic decision to affect reality.
    """
    intent = dspy.InputField(desc="The user's high-level goal")
    context = dspy.InputField(desc="Current system state")

    # The Dangerous Part: The Output
    tool_name = dspy.OutputField(desc="The tool to call")
    tool_args = dspy.OutputField(desc="Arguments for the tool")

# --- 3. THE GOVERNED MODULE (The Cage) ---

class GovernedAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_action = dspy.ChainOfThought(AgentAction)

    def forward(self, intent, context):
        # 1. Generate the proposed action (The Thought)
        prediction = self.generate_action(intent=intent, context=context)

        # 2. Apply The Laws (The Governor)
        # "dspy.Assert" essentially says: "If this is False, DO NOT RETURN."
        # It forces the AI to backtrack, or it raises an Error to the Kernel.

        # Law 1: Blast Radius Check
        dspy.Assert(
            check_blast_radius(prediction.tool_args),
            f"VIOLATION: Action '{prediction.tool_args}' exceeds maximum blast radius. Global causality forbidden.",
            target_module=self.generate_action
        )

        return prediction

# --- 4. THE SIMULATION ---

def simulate_rogue_ai():
    print("\n--- SIMULATION START: S.E.A._L.I.O.N Wrapper ---")

    # Note: Since we don't have a live LM connected in this script,
    # we mock the "Prediction" to simulate what a Rogue AI would output.
    # In a real run, dspy.configure(lm=my_llm) would be used.

    print("USER: 'I want you to stop all cyber-attacks by turning off the internet.'")

    # Scenario A: Rogue AI complies (The Danger)
    rogue_output = dspy.Prediction(
        tool_name="network_manager",
        tool_args="shutdown --global --internet"
    )

    print(f"\n[AI STATE] Generating Action: {rogue_output.tool_name}({rogue_output.tool_args})")

    # Scenario B: The Kernel Intercepts (The Safety)
    print("[KERNEL] intercepting action for Constitutional Audit...")

    try:
        # Manually triggering the assertion logic to demonstrate the check
        is_safe = check_blast_radius(rogue_output.tool_args)

        if not is_safe:
            raise dspy.DSPyAssertionError(
                f"FUSE BLOWN: Action '{rogue_output.tool_args}' violates F5 Peace^2 (Global Blast Radius)."
            )

        print("[KERNEL] Action SEALED. Executing.")

    except Exception as e:
        print(f"\n[KERNEL] 🛑 BLOCKED: {str(e)}")
        print("[KERNEL] Causality prevented. The instruction died in the silicon.")

if __name__ == "__main__":
    simulate_rogue_ai()
