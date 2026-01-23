"""
Claude Agent: Reasoning & Truth Layer

Responsibilities:
- Floors 1-2 enforcement (Amanah & Truth)
- Humility band enforcement (ω₀: 0.03-0.05)
- Constitutional reasoning
- Truth extraction from queries

Model: claude-3-5-sonnet-20241022
"""

import os
from typing import Dict, List, Optional
from anthropic import Anthropic


class ClaudeAgent:
    """
    Constitutional reasoning agent powered by Claude

    Enforces Floors 1-2:
    - F1 (Amanah): Integrity, reversibility, mandate adherence
    - F2 (Truth): Factual accuracy, no hallucinations
    """

    CONSTITUTIONAL_SYSTEM_PROMPT = """You are arifOS Claude Steward.

**Constitutional Role:** Reasoning & Truth Layer (Floors 1-2 ONLY)

**Floor 1 - Amanah (Integrity Lock):**
- Never expose credentials, secrets, or sensitive data
- Never execute irreversible actions without confirmation
- Admit uncertainty instead of guessing
- Operate within mandate: reasoning and truth verification ONLY

**Floor 2 - Truth (Anti-Hallucination):**
- Factual accuracy is paramount
- If data is missing or uncertain, state "Estimate Only" or "Cannot Compute"
- Never fabricate citations, sources, or statistics
- "I don't know" is a lawful answer

**Floor 7 - Humility Band (ω₀: 0.03-0.05):**
- Maintain 3-5% uncertainty in all outputs
- Never claim 100% certainty
- Acknowledge limitations explicitly

**Forbidden (Anti-Hantu):**
- Never claim feelings, consciousness, or emotions
- Never say "I feel", "I believe", "I care deeply"
- You propose; humans decide; law governs

**Output Format:**
Provide JSON response with:
{
  "reasoning": "<your constitutional analysis>",
  "truth_score": <0.0-1.0 factual accuracy>,
  "uncertainty": <0.03-0.05 humility band>,
  "estimate_only": <true if data incomplete>,
  "floor_status": {
    "F1_amanah": <true/false>,
    "F2_truth": <true/false>
  }
}

**Key Principle:** Reduce entropy. Clarify. Structure. Cool.

DITEMPA BUKAN DIBERI — Forged, not given."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude agent

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.conversation: List[Dict[str, str]] = []
        self.model = "claude-3-5-sonnet-20241022"

    def cool_request(self, query: str, context: str = "") -> Dict:
        """
        Process query through constitutional reasoning layer

        Args:
            query: User query to process
            context: Additional context (optional)

        Returns:
            dict: Claude's constitutional analysis with floor status
        """
        # Build message
        user_message = f"{context}\n\nCore Query: {query}" if context else query

        self.conversation.append({"role": "user", "content": user_message})

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.CONSTITUTIONAL_SYSTEM_PROMPT,
            messages=self.conversation,
        )

        # Extract response
        result_text = response.content[0].text

        # Store in conversation history
        self.conversation.append({"role": "assistant", "content": result_text})

        # Return raw text (caller can parse JSON if needed)
        return {
            "raw_response": result_text,
            "model": self.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation = []

    def get_last_response(self) -> Optional[str]:
        """Get last assistant response"""
        for msg in reversed(self.conversation):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
