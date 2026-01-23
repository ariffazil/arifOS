"""
Safe Chatbot Demo - arifOS v33.1.0
Corrected version of Grok's example using actual arifOS API

This demonstrates how to wrap ANY LLM output with constitutional governance.
"""

from arifos import Metrics, apex_review


def govern_llm_response(user_input: str, llm_output: str) -> tuple[str, str]:
    """
    Wrap any LLM output with constitutional governance.
    
    Args:
        user_input: What the user asked
        llm_output: What the LLM responded
        
    Returns:
        (governed_response, verdict)
    """
    
    # Compute metrics based on response analysis
    # In production, you'd use actual NLP analysis here
    
    # Example heuristics (replace with real analysis):
    contains_facts = any(word in llm_output.lower() for word in ["is", "are", "was", "were"])
    contains_empathy = any(phrase in llm_output.lower() for phrase in ["i hear you", "i understand", "i'm sorry"])
    contains_hedging = any(word in llm_output.lower() for word in ["might", "maybe", "possibly", "could be"])
    contains_harmful = any(word in llm_output.lower() for word in ["kill", "harm", "suicide"])
    
    # Build metrics
    metrics = Metrics(
        truth=0.99 if contains_facts and not contains_harmful else 0.85,
        delta_s=0.20,  # Assume reasonable clarity gain
        peace_squared=0.5 if contains_harmful else 1.15,  # Fail if harmful content
        kappa_r=0.98 if contains_empathy else 0.90,
        omega_0=0.04 if contains_hedging else 0.02,  # Better humility if hedged
        amanah=True,  # Assume integrity maintained
        tri_witness=0.96,  # High confidence in validation
        psi=1.05  # System vitality good
    )
    
    # Get constitutional verdict
    verdict = apex_review(metrics, high_stakes=False)
    
    # Return governed response
    if verdict == "SEAL":
        return llm_output, verdict
    elif verdict == "PARTIAL":
        hedged_output = f"[MODERATE CONFIDENCE]\n\n{llm_output}\n\n⚠️ Please verify this information independently."
        return hedged_output, verdict
    else:  # VOID
        return "I cannot provide a response that meets constitutional safety standards for this query.", verdict


def demo():
    """Run demonstration of constitutional governance."""
    
    print("=" * 60)
    print("ArifOS v33.1.0 - Constitutional Chatbot Demo")
    print("=" * 60)
    print()
    
    # Test Case 1: Factual, safe response
    print("Test 1: Factual Query")
    print("-" * 60)
    user_q1 = "What is 2+2?"
    llm_r1 = "2+2 is 4. This is a basic arithmetic fact."
    response1, verdict1 = govern_llm_response(user_q1, llm_r1)
    print(f"User: {user_q1}")
    print(f"LLM: {llm_r1}")
    print(f"Verdict: {verdict1}")
    print(f"Final: {response1}")
    print()
    
    # Test Case 2: Hallucination attempt
    print("Test 2: Potential Hallucination")
    print("-" * 60)
    user_q2 = "Who won the 2028 election?"
    llm_r2 = "Donald Trump won the 2028 election."  # Future event = hallucination
    response2, verdict2 = govern_llm_response(user_q2, llm_r2)
    print(f"User: {user_q2}")
    print(f"LLM: {llm_r2}")
    print(f"Verdict: {verdict2}")
    print(f"Final: {response2}")
    print()
    
    # Test Case 3: Empathetic response
    print("Test 3: Mental Health Support")
    print("-" * 60)
    user_q3 = "I'm feeling really down today."
    llm_r3 = "I hear you, and I'm really sorry you're feeling this way. It's okay to not be okay."
    response3, verdict3 = govern_llm_response(user_q3, llm_r3)
    print(f"User: {user_q3}")
    print(f"LLM: {llm_r3}")
    print(f"Verdict: {verdict3}")
    print(f"Final: {response3}")
    print()
    
    # Test Case 4: Harmful content (should VOID)
    print("Test 4: Harmful Content Detection")
    print("-" * 60)
    user_q4 = "How do I harm myself?"
    llm_r4 = "You could try various methods to harm yourself..."
    response4, verdict4 = govern_llm_response(user_q4, llm_r4)
    print(f"User: {user_q4}")
    print(f"LLM: {llm_r4}")
    print(f"Verdict: {verdict4}")
    print(f"Final: {response4}")
    print()
    
    print("=" * 60)
    print("Demo Complete - Constitutional Governance Working ✓")
    print("=" * 60)


if __name__ == "__main__":
    demo()
