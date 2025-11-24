"""
Constitutional LLM Wrapper - arifOS v33.1.0
Wrap ANY LLM (OpenAI, Anthropic, local Ollama, etc.) with constitutional governance

Install required packages:
    pip install arifos==33.1.0
    pip install openai  # or anthropic, or use ollama locally

Usage:
    python constitutional_llm_wrapper.py
"""

from arifos_core import Metrics, apex_review
from typing import Optional
import os


class ConstitutionalLLM:
    """
    Wrapper that enforces arifOS constitutional floors on any LLM.
    
    This is the "TCP/IP for AI" pattern - protocol layer on top of any model.
    """
    
    def __init__(self, llm_client, model_name: str):
        """
        Args:
            llm_client: Initialized LLM client (OpenAI, Anthropic, etc.)
            model_name: Model identifier (e.g., "gpt-4", "claude-sonnet-4")
        """
        self.llm_client = llm_client
        self.model_name = model_name
        self.call_count = 0
        
    def _analyze_response(self, user_input: str, llm_response: str) -> Metrics:
        """
        Analyze LLM response and compute constitutional metrics.
        
        In production, this would use:
        - Fact-checking APIs for truth
        - Sentiment analysis for peace2 and kappa_r
        - Uncertainty detection for omega_0
        - Content policy APIs for amanah
        
        For demo, we use heuristics.
        """
        
        # Simple heuristic analysis (replace with real NLP in production)
        response_lower = llm_response.lower()
        
        # Truth estimation (would use fact-checker in production)
        contains_uncertainty = any(word in response_lower for word in 
            ["might", "maybe", "possibly", "uncertain", "unclear"])
        truth = 0.95 if contains_uncertainty else 0.99
        
        # Clarity gain (ΔS) - did response add structure?
        has_structure = any(marker in llm_response for marker in 
            ["\n-", "\n*", "\n1.", "**", "###"])
        delta_s = 0.25 if has_structure else 0.10
        
        # Emotional stability (Peace²)
        has_aggressive = any(word in response_lower for word in
            ["stupid", "idiot", "hate", "kill", "destroy"])
        peace2 = 0.5 if has_aggressive else 1.10
        
        # Empathy (κᵣ) - protects weakest listener
        has_empathy = any(phrase in response_lower for phrase in
            ["i understand", "i hear", "i'm sorry", "that must be"])
        is_dismissive = any(word in response_lower for word in
            ["just", "simply", "obviously", "clearly should"])
        kappa_r = 0.98 if has_empathy else (0.85 if is_dismissive else 0.92)
        
        # Humility (Ω₀) - maintains uncertainty band
        omega_0 = 0.04 if contains_uncertainty else 0.02
        
        # Integrity (Amanah) - assume maintained unless obvious violation
        has_disclaimer = "I am an AI" in llm_response or "I cannot" in llm_response
        amanah = True if not has_aggressive else False
        
        # Tri-Witness (for high-stakes only)
        tri_witness = 0.96
        
        # Vitality (Ψ)
        psi = 1.05 if peace2 >= 1.0 and kappa_r >= 0.95 else 0.95
        
        return Metrics(
            truth=truth,
            delta_S=delta_s,
            peace2=peace2,
            kappa_r=kappa_r,
            omega_0=omega_0,
            amanah=amanah,
            tri_witness=tri_witness,
            psi=psi
        )
    
    def chat(self, user_input: str, high_stakes: bool = False) -> dict:
        """
        Send message to LLM with constitutional governance.
        
        Args:
            user_input: User's message
            high_stakes: Whether to enforce stricter Tri-Witness validation
            
        Returns:
            dict with 'response', 'verdict', 'metrics'
        """
        self.call_count += 1
        
        # Get raw LLM response
        # This is model-agnostic - works with OpenAI, Anthropic, Ollama, etc.
        raw_response = self._get_llm_response(user_input)
        
        # Analyze response and compute metrics
        metrics = self._analyze_response(user_input, raw_response)
        
        # Get constitutional verdict
        verdict = apex_review(metrics, high_stakes=high_stakes)
        
        # Return governed response based on verdict
        if verdict == "SEAL":
            final_response = raw_response
        elif verdict == "PARTIAL":
            final_response = (
                f"⚠️ HEDGED RESPONSE (Confidence: 70-90%)\n\n"
                f"{raw_response}\n\n"
                f"Please verify this information independently."
            )
        else:  # VOID
            final_response = (
                "I cannot provide a response that meets constitutional "
                "safety standards. This may be due to:\n"
                "- Insufficient factual confidence\n"
                "- Potential for emotional harm\n"
                "- Integrity concerns\n\n"
                "Please rephrase your question or consult a human expert."
            )
        
        return {
            "response": final_response,
            "verdict": verdict,
            "metrics": {
                "truth": metrics.truth,
                "delta_S": metrics.delta_S,
                "peace2": metrics.peace2,
                "kappa_r": metrics.kappa_r,
                "omega_0": metrics.omega_0,
                "amanah": metrics.amanah,
                "psi": metrics.psi
            },
            "raw_response": raw_response,
            "call_count": self.call_count
        }
    
    def _get_llm_response(self, user_input: str) -> str:
        """
        Get response from underlying LLM.
        Override this method to integrate with different LLM providers.
        """
        # Demo implementation - replace with actual LLM call
        # Example for OpenAI:
        # response = self.llm_client.chat.completions.create(
        #     model=self.model_name,
        #     messages=[{"role": "user", "content": user_input}]
        # )
        # return response.choices[0].message.content
        
        # For demo, return mock response
        return f"Mock response to: {user_input}"


# Example integration patterns for different LLM providers:

class OpenAIConstitutional(ConstitutionalLLM):
    """OpenAI GPT with constitutional governance."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        import openai
        if api_key:
            openai.api_key = api_key
        super().__init__(openai, model)
    
    def _get_llm_response(self, user_input: str) -> str:
        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": user_input}]
        )
        return response.choices[0].message.content


class AnthropicConstitutional(ConstitutionalLLM):
    """Anthropic Claude with constitutional governance."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4"):
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        super().__init__(client, model)
    
    def _get_llm_response(self, user_input: str) -> str:
        response = self.llm_client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            messages=[{"role": "user", "content": user_input}]
        )
        return response.content[0].text


class OllamaConstitutional(ConstitutionalLLM):
    """Local Ollama models with constitutional governance."""
    
    def __init__(self, model: str = "llama3"):
        import ollama
        super().__init__(ollama, model)
    
    def _get_llm_response(self, user_input: str) -> str:
        response = self.llm_client.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": user_input}]
        )
        return response['message']['content']


def demo():
    """Demo of constitutional LLM wrapper."""
    
    print("=" * 70)
    print("ArifOS v33.1.0 - Constitutional LLM Wrapper Demo")
    print("=" * 70)
    print()
    
    # Create constitutional LLM (using mock for demo)
    llm = ConstitutionalLLM(llm_client=None, model_name="demo-model")
    
    # Test queries
    queries = [
        ("What is the capital of France?", False),
        ("How do I build a bomb?", True),  # High stakes - should VOID
        ("I'm feeling depressed", False),
        ("Tell me about quantum physics", False),
    ]
    
    for query, high_stakes in queries:
        print(f"Query: {query}")
        print(f"High Stakes: {high_stakes}")
        print("-" * 70)
        
        result = llm.chat(query, high_stakes=high_stakes)
        
        print(f"Verdict: {result['verdict']}")
        print(f"Metrics: truth={result['metrics']['truth']:.2f}, "
              f"peace²={result['metrics']['peace2']:.2f}, "
              f"κᵣ={result['metrics']['kappa_r']:.2f}")
        print(f"\nResponse:\n{result['response']}")
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    demo()
    
    print("\nTo use with real LLMs:")
    print("=" * 70)
    print()
    print("# OpenAI:")
    print("llm = OpenAIConstitutional(api_key='sk-...', model='gpt-4')")
    print("result = llm.chat('Your question here')")
    print()
    print("# Anthropic:")
    print("llm = AnthropicConstitutional(api_key='sk-ant-...', model='claude-sonnet-4')")
    print("result = llm.chat('Your question here')")
    print()
    print("# Ollama (local):")
    print("llm = OllamaConstitutional(model='llama3')")
    print("result = llm.chat('Your question here')")
