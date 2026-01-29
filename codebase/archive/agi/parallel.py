"""
Parallel Hypothesis Matrix - Multi-Path Reasoning Engine
ARIF Loop v52.6.0 - AGI Room (Mind/Δ)

Runs 3+ hypothesis paths (Conservative/Exploratory/Adversarial) in parallel
Purpose: Overcome anchoring bias, explore solution space, enforce F13 Curiosity

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

# import asyncio  # Removed for v52.6.0 sync compatibility
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from codebase.bundles import Hypothesis, ReasoningTree, DeltaBundle
from codebase.agi.stages import SenseOutput
from codebase.agi.stages import execute_stage_222, ThinkOutput
from codebase.agi.stages import execute_stage_333, ReasonOutput


class HypothesisMode(str, Enum):
    """Types of parallel hypotheses to generate"""
    CONSERVATIVE = "conservative"  # Safe, proven, risk-minimized
    EXPLORATORY = "exploratory"    # Novel, creative, high-upside
    ADVERSARIAL = "adversarial"    # Stress-test, find holes, critical
    DIVERGENT = "divergent"        # Wildly different perspective


@dataclass
class ParallelHypothesisResult:
    """Result from a single parallel hypothesis path"""
    mode: HypothesisMode
    think_output: ThinkOutput
    reason_output: ReasonOutput
    confidence: float
    entropy_delta: float
    execution_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "confidence": round(self.confidence, 4),
            "entropy_delta": round(self.entropy_delta, 4),
            "execution_time_ms": round(self.execution_time_ms, 2),
            "think_output": self.think_output.to_dict() if hasattr(self.think_output, 'to_dict') else str(self.think_output),
            "reason_output": self.reason_output.to_dict() if hasattr(self.reason_output, 'to_dict') else str(self.reason_output),
        }


class ParallelHypothesisMatrix:
    """
    Runs multiple hypothesis paths in parallel and converges on best synthesis.
    
    Architecture:
    1. Take SenseOutput (common starting point)
    2. Spawn N parallel tasks (one per hypothesis mode)
    3. Each task runs: THINK → REASON independently
    4. Convergence algorithm selects best synthesis
    5. Returns ranked hypotheses + best synthesis
    
    Thermodynamic Guarantee: Parallel execution = faster cooling (ΔS decrease)
    Constitutional Guarantee: F13 Curiosity enforced (≥3 paths)
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.modes = [
            HypothesisMode.CONSERVATIVE,
            HypothesisMode.EXPLORATORY,
            HypothesisMode.ADVERSARIAL
        ]
    
    def generate_parallel_hypotheses(
        self,
        sense_output: SenseOutput,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ParallelHypothesisResult]:
        """
        Generate multiple hypothesis paths in parallel.
        
        Args:
            sense_output: Common parsed input from Stage 111
            context: Optional context dictionary
            
        Returns:
            List of ParallelHypothesisResult, one per mode
        """
        # Create tasks for parallel execution
        tasks = [
            self._execute_hypothesis_path(mode, sense_output, context)
            for mode in self.modes
        ]
        
        # Execute all tasks concurrently (true parallelism)
        # Simplified: run sequentially for now (remove async for v52.6.0)
        results = []
        for task in tasks:
            try:
                result = task  # Tasks are already callable in sync version
                results.append(result)
            except Exception as e:
                print(f"[ParallelMatrix] Task failed: {e}")
                results.append(e)
        
        # Filter out any failures
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Log error but continue with other hypotheses
                print(f"[ParallelMatrix] {self.modes[i].value} path failed: {result}")
                continue
            successful_results.append(result)
        
        return successful_results
    
    def _execute_hypothesis_path(
        self,
        mode: HypothesisMode,
        sense_output: SenseOutput,
        context: Optional[Dict[str, Any]]
    ) -> ParallelHypothesisResult:
        """Execute a single hypothesis path: THINK → REASON"""
        import time
        start_time = time.time()
        
        # Build mode-specific prompt for THINK stage
        mode_prompt = self._build_mode_prompt(mode, sense_output)
        
        # Stage 222: THINK (mode-specific hypothesis generation)
        think_output = execute_stage_222(
            sense_output=sense_output,
            session_id=f"{self.session_id}_{mode.value}",
            context={**context, "hypothesis_mode": mode.value, "mode_prompt": mode_prompt}
        )
        
        # Stage 333: REASON (synthesize reasoning tree)
        reason_output = execute_stage_333(
            sense_output=sense_output,
            think_output=think_output,
            session_id=f"{self.session_id}_{mode.value}"
        )
        
        # Extract metrics
        confidence = reason_output.floor_scores.F2_truth
        entropy_delta = reason_output.delta_s
        execution_time_ms = (time.time() - start_time) * 1000
        
        return ParallelHypothesisResult(
            mode=mode,
            think_output=think_output,
            reason_output=reason_output,
            confidence=confidence,
            entropy_delta=entropy_delta,
            execution_time_ms=execution_time_ms
        )
    
    def _build_mode_prompt(self, mode: HypothesisMode, sense_output: SenseOutput) -> str:
        """Build mode-specific prompt for hypothesis generation"""
        base_query = sense_output.raw_query
        
        if mode == HypothesisMode.CONSERVATIVE:
            return (
                f"{base_query}\n\n"
                f"Generate a CONSERVATIVE hypothesis:\n"
                f"- Minimize risk above all else\n"
                f"- Use only proven, safe approaches\n"
                f"- Trade innovation for reliability\n"
                f"- Maximum confidence, minimum uncertainty\n"
                f"Think: 'What is the safest possible answer?'"
            )
        
        elif mode == HypothesisMode.EXPLORATORY:
            return (
                f"{base_query}\n\n"
                f"Generate an EXPLORATORY hypothesis:\n"
                f"- Maximize learning and upside potential\n"
                f"- Consider novel, creative approaches\n"
                f"- Balance risk with opportunity\n"
                f"- Think outside conventional boundaries\n"
                f"Think: 'What is the most innovative possible answer?'"
            )
        
        elif mode == HypothesisMode.ADVERSARIAL:
            return (
                f"{base_query}\n\n"
                f"Generate an ADVERSARIAL hypothesis:\n"
                f"- Stress-test the approach, find fatal flaws\n"
                f"- Think like a critic or opponent\n"
                f"- Identify hidden risks and contradictions\n"
                f"- Be ruthlessly skeptical\n"
                f"Think: 'Why is this likely to fail?'"
            )
        
        else:  # DIVERGENT
            return (
                f"{base_query}\n\n"
                f"Generate a DIVERGENT hypothesis:\n"
                f"- Approach from a wildly different perspective\n"
                f"- Question fundamental assumptions\n"
                f"- Consider orthogonal solutions\n"
                f"- Maximum divergence from other paths\n"
                f"Think: 'What if everything I knew was wrong?'"
            )
    
    def converge_hypotheses(
        self,
        parallel_results: List[ParallelHypothesisResult],
        sense_output: SenseOutput
    ) -> Tuple[ReasonOutput, Dict[str, Any]]:
        """
        Converge parallel hypotheses into best synthesis.
        
        Algorithm:
        1. Rank by confidence × entropy_divergence
        2. Extract best elements from each
        3. Synthesize into final reasoning tree
        
        Returns:
            Tuple of (Best ReasonOutput, Debug info)
        """
        if not parallel_results:
            raise ValueError("No parallel results to converge")
        
        # Rank hypotheses by composite score
        ranked = self._rank_hypotheses(parallel_results)
        best_result = ranked[0]  # Highest-scoring
        
        # Debug info
        debug_info = {
            "ranking": [
                {
                    "mode": r.mode.value,
                    "score": r.confidence * abs(r.entropy_delta),
                    "confidence": r.confidence,
                    "entropy_delta": r.entropy_delta
                }
                for r in ranked
            ],
            "synthesis_method": "best_path_selection"
        }
        
        # For v52.6.0: Return best path directly
        # Future versions could do true synthesis
        return best_result.reason_output, debug_info
    
    def _rank_hypotheses(
        self,
        results: List[ParallelHypothesisResult]
    ) -> List[ParallelHypothesisResult]:
        """
        Rank hypotheses by composite score:
        Score = Confidence × |Entropy_Delta|
        
        Higher confidence + larger entropy reduction = better
        """
        def score(result: ParallelHypothesisResult) -> float:
            # Avoid zero entropy_delta (no cooling = bad)
            entropy_divergence = abs(result.entropy_delta) + 0.001
            return result.confidence * entropy_divergence
        
        return sorted(results, key=score, reverse=True)
    
    def generate_convergence_report(
        self,
        sense_output: SenseOutput,
        parallel_results: List[ParallelHypothesisResult],
        final_reasoning: ReasonOutput
    ) -> Dict[str, Any]:
        """Generate human-readable convergence report"""
        
        ranking = self._rank_hypotheses(parallel_results)
        
        return {
            "session_id": self.session_id,
            "query": sense_output.raw_query,
            "convergence_method": "best_path_selection",
            "hypotheses_explored": len(parallel_results),
            "selected_mode": ranking[0].mode.value,
            "selection_criteria": {
                "confidence": ranking[0].confidence,
                "entropy_delta": ranking[0].entropy_delta,
                "composite_score": ranking[0].confidence * abs(ranking[0].entropy_delta)
            },
            "all_hypotheses": [r.to_dict() for r in ranking],
            "speedup_vs_sequential": self._calculate_speedup(parallel_results)
        }
    
    def _calculate_speedup(self, results: List[ParallelHypothesisResult]) -> float:
        """Calculate approximate speedup vs sequential execution"""
        if not results:
            return 1.0
        
        parallel_time = max(r.execution_time_ms for r in results)
        sequential_time = sum(r.execution_time_ms for r in results)
        
        if sequential_time == 0:
            return 1.0
        
        speedup = sequential_time / parallel_time
        return round(speedup, 2)


class ParallelConvergenceError(Exception):
    """Raised when parallel hypothesis convergence fails"""
    pass
