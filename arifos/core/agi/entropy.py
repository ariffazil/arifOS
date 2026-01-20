"""
arifos.core/agi/entropy.py

Shannon Entropy & ΔS Computation (F2: Clarity Floor)

Purpose:
    Measure organizational entropy in text to quantify clarity reduction.

    ΔS = S_after - S_before

    Where:
    - S = Shannon entropy (information disorder)
    - ΔS < 0 = Entropy reduced (clarity gained) ✅
    - ΔS = 0 = No change (neutral)
    - ΔS > 0 = Entropy increased (confusion added) ❌

Physics:
    Shannon entropy: H(X) = -Σ p(x) * log₂(p(x))

    Measures uncertainty/surprise in a probability distribution.
    High entropy = high disorder (many equally likely outcomes)
    Low entropy = low disorder (few probable outcomes)

Constitutional Floor: F2 (ΔS/Clarity)
    - Type: Hard floor
    - Threshold: ΔS ≥ 0.0 (must not increase confusion)
    - Failure Action: VOID

Authority:
    - AAA_MCP/v46/000_foundation/constitutional_floors.json (F2)
    - Mathematical: Claude Shannon, "A Mathematical Theory of Communication" (1948)

DITEMPA BUKAN DIBERI — Physics over prompts.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class EntropyMetrics:
    """
    Entropy measurement result.

    Attributes:
        shannon_entropy: Shannon entropy in bits (H(X) = -Σ p*log₂(p))
        token_count: Number of tokens analyzed
        unique_tokens: Number of unique tokens
        redundancy: 1 - (H/H_max), where H_max = log₂(unique_tokens)
        perplexity: 2^H, average branching factor
        compression_ratio: Estimate of compressibility
    """
    shannon_entropy: float
    token_count: int
    unique_tokens: int
    redundancy: float
    perplexity: float
    compression_ratio: float

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization."""
        return {
            "shannon_entropy": self.shannon_entropy,
            "token_count": self.token_count,
            "unique_tokens": self.unique_tokens,
            "redundancy": self.redundancy,
            "perplexity": self.perplexity,
            "compression_ratio": self.compression_ratio,
        }


@dataclass
class DeltaSResult:
    """
    ΔS computation result (entropy change).

    Attributes:
        delta_s: Change in entropy (S_after - S_before)
        s_before: Entropy of input state
        s_after: Entropy of output state
        clarity_gained: True if ΔS < 0 (entropy reduced)
        interpretation: Human-readable explanation
        before_metrics: Full entropy metrics for input
        after_metrics: Full entropy metrics for output
    """
    delta_s: float
    s_before: float
    s_after: float
    clarity_gained: bool
    interpretation: str
    before_metrics: EntropyMetrics
    after_metrics: EntropyMetrics

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "delta_s": self.delta_s,
            "s_before": self.s_before,
            "s_after": self.s_after,
            "clarity_gained": self.clarity_gained,
            "interpretation": self.interpretation,
            "before_metrics": self.before_metrics.to_dict(),
            "after_metrics": self.after_metrics.to_dict(),
        }


def tokenize(text: str, mode: str = "word") -> List[str]:
    """
    Tokenize text for entropy calculation.

    Args:
        text: Input text to tokenize
        mode: Tokenization mode:
            - "word": Word-level tokens (default)
            - "char": Character-level tokens
            - "bigram": Word bigrams (pairs)
            - "semantic": Semantic chunks (simplified)

    Returns:
        List of tokens
    """
    if not text or not isinstance(text, str):
        return []

    text = text.lower().strip()

    if mode == "char":
        # Character-level (sensitive to typos, whitespace)
        return list(text)

    elif mode == "word":
        # Word-level (standard)
        # Remove punctuation, split on whitespace
        words = re.findall(r'\b\w+\b', text)
        return words

    elif mode == "bigram":
        # Word bigrams (captures local structure)
        words = re.findall(r'\b\w+\b', text)
        if len(words) < 2:
            return words
        bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]
        return bigrams

    elif mode == "semantic":
        # Semantic chunks (simplified: sentences or clauses)
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        chunks = [s.strip() for s in sentences if s.strip()]
        return chunks

    else:
        raise ValueError(f"Unknown tokenization mode: {mode}")


def compute_shannon_entropy(tokens: List[str]) -> float:
    """
    Compute Shannon entropy of token distribution.

    H(X) = -Σ p(x) * log₂(p(x))

    Args:
        tokens: List of tokens (words, chars, etc.)

    Returns:
        Shannon entropy in bits
    """
    if not tokens:
        return 0.0

    # Count token frequencies
    token_counts = Counter(tokens)
    total = len(tokens)

    # Compute probabilities and entropy
    entropy = 0.0
    for count in token_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def compute_entropy_metrics(text: str, mode: str = "word") -> EntropyMetrics:
    """
    Compute comprehensive entropy metrics for text.

    Args:
        text: Input text to analyze
        mode: Tokenization mode (word, char, bigram, semantic)

    Returns:
        EntropyMetrics with Shannon entropy and derived measures
    """
    tokens = tokenize(text, mode=mode)

    if not tokens:
        return EntropyMetrics(
            shannon_entropy=0.0,
            token_count=0,
            unique_tokens=0,
            redundancy=0.0,
            perplexity=1.0,
            compression_ratio=1.0,
        )

    # Shannon entropy
    H = compute_shannon_entropy(tokens)

    # Derived metrics
    token_count = len(tokens)
    unique_tokens = len(set(tokens))

    # Maximum possible entropy (uniform distribution)
    H_max = math.log2(unique_tokens) if unique_tokens > 1 else 0.0

    # Redundancy: 1 - (H / H_max)
    # High redundancy = predictable text (low entropy relative to max)
    # Special case: single unique token has maximum redundancy (1.0)
    if unique_tokens == 1:
        redundancy = 1.0
    elif H_max > 0:
        redundancy = 1.0 - (H / H_max)
    else:
        redundancy = 0.0

    # Perplexity: 2^H (average branching factor)
    # How many choices on average at each step
    perplexity = 2 ** H

    # Compression ratio estimate
    # Lower entropy = more compressible
    # Using H/H_max as proxy for compressibility
    compression_ratio = (H / H_max) if H_max > 0 else 1.0

    return EntropyMetrics(
        shannon_entropy=H,
        token_count=token_count,
        unique_tokens=unique_tokens,
        redundancy=redundancy,
        perplexity=perplexity,
        compression_ratio=compression_ratio,
    )


def compute_delta_s(
    input_text: str,
    output_text: str,
    mode: str = "word",
    normalize: bool = False,
) -> DeltaSResult:
    """
    Compute ΔS (entropy change) from input to output.

    ΔS = S_after - S_before

    Args:
        input_text: Initial state (user query, raw data)
        output_text: Final state (AI response, processed output)
        mode: Tokenization mode (word, char, bigram, semantic)
        normalize: Normalize by token count (per-token entropy change).
                  Default False - absolute entropy change is more intuitive for clarity.
                  Use True only when comparing texts of very different lengths.

    Returns:
        DeltaSResult with ΔS and interpretation
    """
    # Compute entropy for both states
    before_metrics = compute_entropy_metrics(input_text, mode=mode)
    after_metrics = compute_entropy_metrics(output_text, mode=mode)

    s_before = before_metrics.shannon_entropy
    s_after = after_metrics.shannon_entropy

    # Compute ΔS
    if normalize and before_metrics.token_count > 0:
        # Normalize by token count (per-token entropy)
        s_before_norm = s_before / before_metrics.token_count
        s_after_norm = s_after / after_metrics.token_count if after_metrics.token_count > 0 else 0.0
        delta_s = s_after_norm - s_before_norm
    else:
        # Absolute entropy change
        delta_s = s_after - s_before

    # Interpret result
    clarity_gained = delta_s < 0.0

    if delta_s < -0.5:
        interpretation = "Significant clarity gain (ΔS < -0.5). Output is much more structured than input."
    elif delta_s < 0.0:
        interpretation = "Clarity gain (ΔS < 0). Output reduced uncertainty."
    elif delta_s == 0.0:
        interpretation = "Neutral (ΔS = 0). No entropy change."
    elif delta_s < 0.5:
        interpretation = "Minor confusion increase (ΔS > 0). Output slightly less structured."
    else:
        interpretation = "Significant confusion increase (ΔS > 0.5). Output is more chaotic than input."

    return DeltaSResult(
        delta_s=delta_s,
        s_before=s_before,
        s_after=s_after,
        clarity_gained=clarity_gained,
        interpretation=interpretation,
        before_metrics=before_metrics,
        after_metrics=after_metrics,
    )


def compute_delta_s_batch(
    inputs: List[str],
    outputs: List[str],
    mode: str = "word",
) -> Tuple[float, List[DeltaSResult]]:
    """
    Compute average ΔS across multiple input-output pairs.

    Args:
        inputs: List of input texts
        outputs: List of output texts (must match inputs length)
        mode: Tokenization mode

    Returns:
        Tuple of (average_delta_s, list_of_individual_results)
    """
    if len(inputs) != len(outputs):
        raise ValueError(f"Inputs ({len(inputs)}) and outputs ({len(outputs)}) must have same length")

    results = []
    total_delta_s = 0.0

    for input_text, output_text in zip(inputs, outputs):
        result = compute_delta_s(input_text, output_text, mode=mode)
        results.append(result)
        total_delta_s += result.delta_s

    avg_delta_s = total_delta_s / len(results) if results else 0.0

    return avg_delta_s, results


def evaluate_clarity_floor(delta_s: float, threshold: float = 0.0) -> Tuple[bool, str]:
    """
    Evaluate if ΔS passes F2 (Clarity) floor.

    Constitutional constraint: ΔS ≤ threshold (must not increase confusion beyond threshold)
    - ΔS < 0 = PASS (clarity gained - entropy reduced)
    - ΔS = 0 = PASS (neutral - no entropy change)
    - ΔS > 0 but ≤ threshold = PASS (acceptable tolerance)
    - ΔS > threshold = FAIL (confusion increased beyond acceptable limit)

    Args:
        delta_s: Computed entropy change
        threshold: Maximum acceptable ΔS (default 0.0 - no confusion increase allowed)

    Returns:
        Tuple of (passed, reason)
    """
    passed = delta_s <= threshold

    if passed:
        if delta_s < 0.0:
            reason = f"F2 Clarity PASS: ΔS = {delta_s:.3f} (entropy reduced, clarity gained)"
        elif delta_s == 0.0:
            reason = f"F2 Clarity PASS: ΔS = {delta_s:.3f} (neutral, no entropy change)"
        else:
            reason = f"F2 Clarity PASS: ΔS = {delta_s:.3f} ≤ {threshold:.3f} (within acceptable tolerance)"
    else:
        reason = f"F2 Clarity FAIL: ΔS = {delta_s:.3f} > {threshold:.3f} (confusion increased beyond threshold)"

    return passed, reason


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def measure_clarity(input_text: str, output_text: str) -> Dict[str, any]:
    """
    Convenience function to measure clarity with default settings.

    Returns dictionary with:
    - delta_s: Entropy change
    - clarity_gained: Boolean
    - floor_passed: F2 floor status
    - interpretation: Human-readable explanation
    """
    result = compute_delta_s(input_text, output_text)
    floor_passed, floor_reason = evaluate_clarity_floor(result.delta_s)

    return {
        "delta_s": result.delta_s,
        "clarity_gained": result.clarity_gained,
        "floor_passed": floor_passed,
        "interpretation": result.interpretation,
        "floor_reason": floor_reason,
        "s_before": result.s_before,
        "s_after": result.s_after,
    }


__all__ = [
    "EntropyMetrics",
    "DeltaSResult",
    "tokenize",
    "compute_shannon_entropy",
    "compute_entropy_metrics",
    "compute_delta_s",
    "compute_delta_s_batch",
    "evaluate_clarity_floor",
    "measure_clarity",
]
