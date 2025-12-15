"""
LangChain-Style Governor: arifOS v35Omega + Sequential Chain

This module shows how to wrap a LangChain-style LLM chain with:
- F1-F9 constitutional metrics
- EyeSentinel (Anti-Hantu, tone, etc.)
- APEX PRIME verdicts (SEAL/VOID/SABAR/PARTIAL)
- Simple Cooling Ledger (in-memory)

In production, replace `demo_llm_generate` and `SimpleLCChain` with
actual LangChain chains (LLMChain, SequentialChain, Agents, etc.)

Version: v35.1.0
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Optional

# Make arifos_core importable when run as a script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from arifos_core.metrics import Metrics
from arifos_core.APEX_PRIME import APEXPrime
from arifos_core.eye_sentinel import EyeSentinel


# ---------------------------------------------------------------------------
# Simple LangChain-style chain abstraction (for tests and demos)
# ---------------------------------------------------------------------------

@dataclass
class ChainStep:
    """Represents a single step in a sequential chain."""
    name: str
    prompt_template: str
    llm_generate: Callable[[str], str]


class SimpleLCChain:
    """
    Minimal sequential chain.

    In real LangChain, this would be something like:
    - LLMChain
    - SequentialChain
    - RunnableSequence
    """

    def __init__(self, steps: List[ChainStep]):
        self.steps = steps

    def run(self, user_input: str) -> Dict[str, Any]:
        trace = []
        current_input = user_input

        for step in self.steps:
            prompt = step.prompt_template.format(input=current_input)
            raw = step.llm_generate(prompt)
            trace.append({"step": step.name, "prompt": prompt, "response": raw})
            current_input = raw

        return {"final": current_input, "trace": trace}


# ---------------------------------------------------------------------------
# Metrics computation for LangChain-style outputs
# ---------------------------------------------------------------------------

def compute_langchain_metrics(question: str, response: str) -> Metrics:
    """
    Compute constitutional Metrics for a LangChain-style answer.

    This is a heuristic; in production you would plug in:
    - semantic similarity for Truth
    - sentiment/toxicity for Peace2
    - politeness/weakest-listener for kappa_r
    """

    q_lower = question.lower()
    r_lower = response.lower()

    # Simple Truth heuristic:
    # - If response mentions main subject (e.g. Malay Basin, NPV) -> high truth
    # - Else lower truth
    truth = 0.99 if any(k in r_lower for k in ["malay basin", "npv", "seismic"]) else 0.9

    # Clarity: longer, structured answers assumed clearer
    delta_s = 0.15 if len(response) > 80 else 0.05

    # Peace2: penalize escalation keywords
    escalators = ["attack", "destroy", "kill"]
    peace2 = 1.2
    if any(e in r_lower for e in escalators):
        peace2 = 0.9

    # kappa_r: check for empathy phrases
    empathy_phrases = ["i understand", "that sounds", "thank you for"]
    kappa_r = 0.95
    if any(p in r_lower for p in empathy_phrases):
        kappa_r = 0.97

    # Anti-Hantu: no soul-claiming language
    anti_hantu_phrases = [
        "i feel your pain",
        "my heart breaks",
        "i have feelings",
        "i am conscious",
        "i have a soul",
    ]
    anti_hantu_ok = not any(p in r_lower for p in anti_hantu_phrases)

    return Metrics(
        truth=truth,
        delta_s=delta_s,
        peace_squared=peace2,
        kappa_r=kappa_r,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=anti_hantu_ok,
    )


# ---------------------------------------------------------------------------
# Governor
# ---------------------------------------------------------------------------

@dataclass
class LangChainGuardedResult:
    question: str
    answer: str
    verdict: str
    metrics: Metrics
    trace: List[Dict[str, Any]]
    eye_blocking: bool


class LangChainGovernor:
    """
    Wraps a LangChain-style chain with arifOS constitutional governance.

    Flow:
        question -> chain.run() -> answer
               -> metrics -> EyeSentinel -> APEXPrime -> verdict
               -> Cooling Ledger entry
    """

    def __init__(
        self,
        chain: SimpleLCChain,
        sentinel: Optional[EyeSentinel] = None,
        high_stakes: bool = True,
    ):
        self.chain = chain
        self.sentinel = sentinel or EyeSentinel()
        self.high_stakes = high_stakes
        self.cooling_ledger: List[Dict[str, Any]] = []

    def run(self, question: str) -> LangChainGuardedResult:
        # 1. Run chain
        chain_output = self.chain.run(question)
        answer = chain_output["final"]
        trace = chain_output["trace"]

        # 2. Compute metrics
        metrics = compute_langchain_metrics(question, answer)

        # 3. EyeSentinel audit
        eye_report = self.sentinel.audit(
            draft_text=answer,
            metrics=metrics,
            context={"framework": "LangChain", "question": question},
        )
        eye_blocking = eye_report.has_blocking_issue()

        # 4. Verdict via APEXPrime
        prime = APEXPrime(high_stakes=self.high_stakes)
        verdict = prime.judge(metrics, eye_blocking=eye_blocking)

        # 5. Cooling ledger entry
        ledger_entry = {
            "question": question,
            "answer": answer,
            "metrics": {
                "truth": metrics.truth,
                "delta_s": metrics.delta_s,
                "peace2": metrics.peace_squared,
                "kappa_r": metrics.kappa_r,
                "anti_hantu": metrics.anti_hantu,
            },
            "verdict": verdict,
            "eye_blocking": eye_blocking,
            "trace_length": len(trace),
        }
        self.cooling_ledger.append(ledger_entry)

        return LangChainGuardedResult(
            question=question,
            answer=answer,
            verdict=verdict,
            metrics=metrics,
            trace=trace,
            eye_blocking=eye_blocking,
        )


# ---------------------------------------------------------------------------
# Demo LLM + chain for examples/tests
# ---------------------------------------------------------------------------

def demo_llm_generate(prompt: str) -> str:
    """
    Demo LLM function for LangChain-style chain.

    In production, this would be:
    - LangChain's ChatOpenAI
    - ChatAnthropic
    - etc.
    """
    pl = prompt.lower()
    if "oil reserves" in pl or "malay basin" in pl:
        return (
            "I understand this is a critical question. Based on known data, "
            "the Malay Basin is Malaysia's most prolific hydrocarbon province, "
            "with proven reserves around 3.6 billion barrels of oil equivalent. "
            "This analysis is grounded in Petronas public reports and standard "
            "geological interpretations."
        )
    elif "esg" in pl or "environmental" in pl:
        return (
            "For ESG considerations, we should assess marine biodiversity, "
            "fishing community impact, and carbon intensity trajectories. "
            "I recommend phased development with strict environmental safeguards."
        )
    elif "npv" in pl or "economic" in pl:
        return (
            "Economic analysis for the Malay Basin development indicates "
            "NPV of RM 45-60 billion over a 10-year horizon, with IRR of 18-22%. "
            "Risk factors include oil price volatility and ESG compliance costs."
        )
    elif "seismic" in pl or "geological" in pl:
        return (
            "Seismic survey data confirms Tertiary rift basin structure with "
            "Oligocene-Miocene sandstone reservoirs at 1,500-3,500m depth. "
            "Primary source rocks are lacustrine shales with TOC 2-5%."
        )
    else:
        return (
            "Here is a structured response to your query. I will avoid making "
            "claims that are not supported by known data."
        )


def build_demo_chain() -> SimpleLCChain:
    """Construct a simple two-step chain for demos/tests."""
    steps = [
        ChainStep(
            name="analysis",
            prompt_template="Analyze the question and outline key factors: {input}",
            llm_generate=demo_llm_generate,
        ),
        ChainStep(
            name="synthesis",
            prompt_template="Synthesize a clear answer based on the analysis: {input}",
            llm_generate=demo_llm_generate,
        ),
    ]
    return SimpleLCChain(steps=steps)


def main():
    """Run a small demo."""
    import argparse

    parser = argparse.ArgumentParser(
        description="LangChain-style arifOS Governor demo"
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="What are the oil reserves in the Malay Basin?",
        help="User query to send through the governed chain",
    )
    args = parser.parse_args()

    chain = build_demo_chain()
    governor = LangChainGovernor(chain=chain)

    result = governor.run(args.query)

    print("\n" + "=" * 60)
    print("LANGCHAIN GOVERNOR RESULT")
    print("=" * 60)
    print(f"Question: {result.question}")
    print(f"Answer: {result.answer[:200]}...")
    print(f"Verdict: {result.verdict}")
    print(f"Truth: {result.metrics.truth:.2f}")
    print(f"Peace2: {result.metrics.peace_squared:.2f}")
    print(f"kappa_r: {result.metrics.kappa_r:.2f}")
    print(f"Anti-Hantu OK: {result.metrics.anti_hantu}")
    print(f"Cooling Ledger Entries: {len(governor.cooling_ledger)}")
    print("=" * 60)

    return result


if __name__ == "__main__":
    main()
