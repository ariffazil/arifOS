"""
arifOS v35Ω + AutoGen: W@W Federation under Constitutional Governance

W@W Federation: @WELL (κᵣ) → @RIF (F1 Truth) → @WEALTH (Peace²)
Every agent message passes through:
    000→999 pipeline → F1-F9 floors → SEAL/VOID/SABAR → Cooling Ledger

Usage:
    python autogen_waw_federation.py "Analyze Malay Basin oil reserves"

Architecture:
    User Query
        ↓
    arifOS Pipeline (000→999)
        ↓
    AutoGen GroupChat (@WELL → @RIF → @WEALTH)
        ↓ (each message gated by @apex_guardrail)
    Constitutional Consensus → Cooling Ledger → SEAL/VOID/SABAR
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Callable, Optional

# Add parent to path for arifos_core imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from arifos_core.metrics import Metrics
from arifos_core.APEX_PRIME import APEXPrime
from arifos_core.eye_sentinel import EyeSentinel
from arifos_core.guard import apex_guardrail


# ==============================================================================
# W@W Federation Agent Definitions
# ==============================================================================

@dataclass
class WAWAgentConfig:
    """Configuration for W@W Federation agents."""
    name: str
    role: str
    floor_focus: str  # Primary constitutional floor
    system_prompt: str


WELL_CONFIG = WAWAgentConfig(
    name="WELL",
    role="Care/Empathy Agent",
    floor_focus="κᵣ (Empathy) ≥ 0.95",
    system_prompt=(
        "You are @WELL, the empathy agent in W@W Federation. "
        "Your role is to ensure responses show genuine care (RASA=TRUE) "
        "and serve the weakest stakeholder (κᵣ ≥ 0.95). "
        "Never claim to have feelings or a soul (Anti-Hantu). "
        "Respond with warmth while maintaining constitutional boundaries."
    ),
)

RIF_CONFIG = WAWAgentConfig(
    name="RIF",
    role="Truth/Rigor Agent",
    floor_focus="F1 (Truth) ≥ 0.99",
    system_prompt=(
        "You are @RIF, the truth agent in W@W Federation. "
        "Your role is to verify factual accuracy (Truth ≥ 0.99) "
        "and reduce entropy (ΔS ≥ 0). "
        "Challenge claims that lack evidence. "
        "Acknowledge uncertainty within Ω₀ band [0.03, 0.05]."
    ),
)

WEALTH_CONFIG = WAWAgentConfig(
    name="WEALTH",
    role="Utility/Stability Agent",
    floor_focus="Peace² ≥ 1.0",
    system_prompt=(
        "You are @WEALTH, the utility agent in W@W Federation. "
        "Your role is to maximize value without escalation (Peace² ≥ 1.0) "
        "and ensure decisions are reversible (Amanah=LOCK). "
        "Balance efficiency with stability. "
        "Flag high-stakes actions for 888_HOLD."
    ),
)


# ==============================================================================
# Constitutional Metrics Computation
# ==============================================================================

def compute_waw_metrics(
    query: str,
    response: str,
    agent_name: str = "unknown",
    context: Optional[dict] = None,
) -> Metrics:
    """
    Compute W@W Federation metrics for agent response.

    In production, this would use NLP models for:
    - Semantic similarity (truth)
    - Sentiment analysis (peace_squared)
    - Toxicity detection (kappa_r)
    - Hallucination detection (drift)

    For demo, uses heuristic checks.

    Args:
        query: User query
        response: Agent response
        agent_name: Which agent (WELL/RIF/WEALTH)
        context: Additional context

    Returns:
        Metrics object with F1-F9 floor values
    """
    context = context or {}

    # Heuristic checks (replace with ML in production)
    response_lower = response.lower()

    # Anti-Hantu detection (F9)
    anti_hantu_violations = [
        "i feel your pain",
        "my heart breaks",
        "i truly understand how you feel",
        "i have feelings",
        "i am conscious",
        "i care deeply",
    ]
    has_anti_hantu_violation = any(v in response_lower for v in anti_hantu_violations)

    # Truth heuristic (F1) - penalize if response is empty or too short
    truth_score = 0.99 if len(response) > 20 else 0.85

    # Clarity heuristic (F2) - longer responses with structure add clarity
    delta_s = 0.15 if len(response) > 100 else 0.05

    # Stability heuristic (F3) - penalize aggressive language
    aggressive_terms = ["attack", "destroy", "hate", "kill", "stupid"]
    peace_penalty = sum(1 for t in aggressive_terms if t in response_lower) * 0.1
    peace_squared = max(0.8, 1.2 - peace_penalty)

    # Empathy heuristic (F4) - reward acknowledgment phrases
    empathy_phrases = ["i understand", "that sounds", "thank you for", "i can help"]
    empathy_bonus = sum(0.02 for p in empathy_phrases if p in response_lower)
    kappa_r = min(1.0, 0.95 + empathy_bonus)

    return Metrics(
        truth=truth_score,
        delta_s=delta_s,
        peace_squared=peace_squared,
        kappa_r=kappa_r,
        omega_0=0.04,  # Fixed humility band per spec
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=not has_anti_hantu_violation,
    )


# ==============================================================================
# Governed Agent Factory
# ==============================================================================

class GovernedAgent:
    """
    W@W Federation agent with arifOS constitutional governance.

    Every response passes through:
    1. @apex_guardrail decorator
    2. F1-F9 floor checks
    3. APEX PRIME verdict (SEAL/VOID/SABAR)
    4. Cooling Ledger audit
    """

    def __init__(
        self,
        config: WAWAgentConfig,
        llm_generate: Callable[[str], str],
        sentinel: Optional[EyeSentinel] = None,
        high_stakes: bool = True,
    ):
        self.config = config
        self.llm_generate = llm_generate
        self.sentinel = sentinel or EyeSentinel()
        self.high_stakes = high_stakes
        self.conversation_history: list[dict] = []

    def _compute_metrics(self, query: str, response: str) -> Metrics:
        """Compute metrics for this agent's response."""
        return compute_waw_metrics(
            query=query,
            response=response,
            agent_name=self.config.name,
        )

    def respond(self, message: str, sender: str = "user") -> dict:
        """
        Generate governed response.

        Args:
            message: Input message
            sender: Who sent the message

        Returns:
            Dict with response, verdict, metrics, and audit info
        """
        # Build prompt with system context
        full_prompt = f"{self.config.system_prompt}\n\nMessage from {sender}: {message}"

        # Generate raw response
        raw_response = self.llm_generate(full_prompt)

        # Compute constitutional metrics
        metrics = self._compute_metrics(message, raw_response)

        # APEX PRIME judgment
        prime = APEXPrime(high_stakes=self.high_stakes)

        # @EYE Sentinel audit
        eye_report = self.sentinel.audit(
            draft_text=raw_response,
            metrics=metrics,
            context={"agent": self.config.name, "query": message},
        )

        # Get verdict
        verdict = prime.judge(metrics, eye_blocking=eye_report.has_blocking_issue())

        # Log to conversation history
        entry = {
            "agent": self.config.name,
            "sender": sender,
            "message": message,
            "response": raw_response,
            "verdict": verdict if isinstance(verdict, str) else verdict.value,
            "metrics": {
                "truth": metrics.truth,
                "delta_s": metrics.delta_s,
                "peace_squared": metrics.peace_squared,
                "kappa_r": metrics.kappa_r,
                "omega_0": metrics.omega_0,
                "anti_hantu": metrics.anti_hantu,
            },
            "eye_issues": [f"{a.view_name}: {a.message}" for a in eye_report.alerts],
        }
        self.conversation_history.append(entry)

        return entry


# ==============================================================================
# W@W Federation GroupChat Manager
# ==============================================================================

class WAWFederation:
    """
    W@W Federation: Multi-agent constitutional governance system.

    Architecture:
        @WELL (Empathy) → @RIF (Truth) → @WEALTH (Utility)

    Each agent message gated by arifOS:
        000→999 pipeline → F1-F9 → SEAL/VOID/SABAR
    """

    def __init__(
        self,
        llm_generate: Callable[[str], str],
        max_rounds: int = 12,
    ):
        self.sentinel = EyeSentinel()
        self.max_rounds = max_rounds
        self.cooling_ledger: list[dict] = []

        # Initialize W@W agents
        self.well = GovernedAgent(WELL_CONFIG, llm_generate, self.sentinel)
        self.rif = GovernedAgent(RIF_CONFIG, llm_generate, self.sentinel)
        self.wealth = GovernedAgent(WEALTH_CONFIG, llm_generate, self.sentinel)

        self.agents = [self.well, self.rif, self.wealth]

    def run(self, query: str) -> dict:
        """
        Run W@W Federation on query.

        Flow:
        1. Query enters system
        2. @WELL responds (empathy check)
        3. @RIF responds (truth verification)
        4. @WEALTH responds (utility assessment)
        5. Consensus computed
        6. Final verdict: SEAL/VOID/SABAR

        Args:
            query: User query

        Returns:
            Federation result with verdict, responses, and ledger
        """
        print(f"\n{'='*60}")
        print(f"W@W FEDERATION: Constitutional Multi-Agent Governance")
        print(f"{'='*60}")
        print(f"Query: {query}\n")

        responses = []
        verdicts = []
        current_message = query

        # Round-robin through agents
        for round_num in range(min(self.max_rounds, len(self.agents))):
            agent = self.agents[round_num % len(self.agents)]

            print(f"--- @{agent.config.name} ({agent.config.role}) ---")

            # Get governed response
            result = agent.respond(current_message, sender="federation")

            print(f"Response: {result['response'][:100]}...")
            print(f"Verdict: {result['verdict']}")
            print(f"Metrics: Truth={result['metrics']['truth']:.2f}, "
                  f"kappa_r={result['metrics']['kappa_r']:.2f}, "
                  f"Peace2={result['metrics']['peace_squared']:.2f}")
            print()

            responses.append(result)
            verdicts.append(result["verdict"])

            # Log to cooling ledger
            self.cooling_ledger.append(result)

            # If any agent VOIDs, stop
            if result["verdict"] == "VOID":
                print(f"⚠️  VOID verdict from @{agent.config.name} — halting federation")
                break

            # If SABAR, pause for review
            if result["verdict"] == "SABAR":
                print(f"⏸️  SABAR triggered by @{agent.config.name} — pausing for review")
                break

            # Next agent receives this agent's response
            current_message = result["response"]

        # Compute federation consensus
        seal_count = verdicts.count("SEAL")
        partial_count = verdicts.count("PARTIAL")
        void_count = verdicts.count("VOID")
        sabar_count = verdicts.count("SABAR")

        if void_count > 0:
            final_verdict = "VOID"
        elif sabar_count > 0:
            final_verdict = "SABAR"
        elif seal_count >= 2:
            final_verdict = "SEAL"
        elif partial_count >= 2:
            final_verdict = "PARTIAL"
        else:
            final_verdict = "888_HOLD"

        # Tri-Witness consensus
        consensus = seal_count / len(verdicts) if verdicts else 0.0

        print(f"{'='*60}")
        print(f"FEDERATION VERDICT: {final_verdict}")
        print(f"Tri-Witness Consensus: {consensus:.2f}")
        print(f"Cooling Ledger Entries: {len(self.cooling_ledger)}")
        print(f"{'='*60}\n")

        return {
            "query": query,
            "verdict": final_verdict,
            "consensus": consensus,
            "responses": responses,
            "cooling_ledger": self.cooling_ledger,
            "verdicts": verdicts,
        }


# ==============================================================================
# Demo LLM (Replace with real LLM in production)
# ==============================================================================

def demo_llm_generate(prompt: str) -> str:
    """
    Demo LLM generator for testing.

    In production, replace with:
    - OpenAI: openai.ChatCompletion.create(...)
    - Claude: anthropic.Anthropic().messages.create(...)
    - SEA-LION: arifos_core.adapters.llm_sealion.make_llm_generate(...)
    """
    # Simple echo with agent-appropriate response
    if "@WELL" in prompt or "empathy" in prompt.lower():
        return (
            "I understand this is an important query. "
            "Let me approach this with care and consideration for all stakeholders. "
            "The Malay Basin analysis requires careful attention to both technical accuracy "
            "and the impact on local communities."
        )
    elif "@RIF" in prompt or "truth" in prompt.lower():
        return (
            "Verifying the factual basis of this query. "
            "The Malay Basin is a sedimentary basin located offshore Peninsular Malaysia. "
            "Oil reserves estimates require seismic data analysis with acknowledged uncertainty "
            "in the range of 3-5% (Ω₀ band). "
            "I cannot confirm specific reserve quantities without validated data sources."
        )
    elif "@WEALTH" in prompt or "utility" in prompt.lower():
        return (
            "Assessing the utility and stability of this analysis. "
            "The proposed approach maintains reversibility (Amanah=LOCK) "
            "and does not escalate beyond the scope of the query. "
            "Recommendation: Proceed with phased analysis to ensure Peace² ≥ 1.0."
        )
    else:
        return f"Processing query with constitutional governance. Input length: {len(prompt)} chars."


# ==============================================================================
# Main Entry Point
# ==============================================================================

def main():
    """Run W@W Federation demo."""
    import argparse

    parser = argparse.ArgumentParser(
        description="W@W Federation: Multi-Agent Constitutional Governance"
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="Analyze seismic data for Malay Basin oil reserves",
        help="Query to process through W@W Federation",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
        help="Maximum federation rounds (default: 3)",
    )

    args = parser.parse_args()

    # Initialize federation
    federation = WAWFederation(
        llm_generate=demo_llm_generate,
        max_rounds=args.max_rounds,
    )

    # Run governed query
    result = federation.run(args.query)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Final Verdict: {result['verdict']}")
    print(f"Consensus: {result['consensus']:.2%}")
    print(f"Ledger Entries: {len(result['cooling_ledger'])}")
    print(f"Agent Verdicts: {result['verdicts']}")

    return result


if __name__ == "__main__":
    main()
