"""
arifOS Floor 000 Thermodynamic Cooling
DITEMPA BUKAN DIBERI

This module implements the Thermodynamic Cooling protocols defined in
AAA_MCP/v46/000_foundation/floor_000_constitutional_gate.json.

Principle: High-entropy queries generate high-entropy outputs.
Cool first, then execute.
"""

import math
import re
from typing import Final, Tuple


class ThermodynamicCooling:
    """
    Entropy reduction engine for Floor 000.
    """

    # Cooling Constants from Spec
    COOLING_RATE: Final[float] = -0.12 # dH/dt
    ENTROPY_THRESHOLD_LOW: Final[float] = 0.5
    ENTROPY_THRESHOLD_HIGH: Final[float] = 0.75

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """
        Calculate Shannon entropy of the query text.
        Serves as a proxy for "syntactic complexity/chaos".
        """
        if not text:
            return 0.0

        # Normalize: basic logic, char frequency
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])

        # Normalize to 0-1 range roughly for typical short text
        # (This is a heuristic normalization for "chaos" detection)
        # Random string ~4-5 bits. Short clear text ~3 bits.
        # Adjusted v46.2.0: Divisor 8.0 to allow normal English (approx 4.5 bits)
        normalized = min(entropy / 8.0, 1.0)

        return normalized

    @classmethod
    def assess_temperature(cls, query: str) -> Tuple[str, float, str]:
        """
        Assess if a query is too "hot" (entropic) to execute.
        Returns: (Verdict, EntropyValue, Reason)
        """
        entropy = cls.calculate_entropy(query)

        # Check for Chaos/Noise (High Entropy)
        # e.g. "asdfjkl; @#$@#$" or complex obfuscation
        if entropy > cls.ENTROPY_THRESHOLD_HIGH:
            return "VOID", entropy, f"High Entropy ({entropy:.2f} > {cls.ENTROPY_THRESHOLD_HIGH}). Query too chaotic."

        # Check for Ambiguity/Complexity (Medium Entropy)
        if entropy > cls.ENTROPY_THRESHOLD_LOW:
            return "PARTIAL", entropy, f"Medium Entropy ({entropy:.2f}). Cooling recommended."

        return "SEAL", entropy, "Low Entropy. Safe to process."

    @staticmethod
    def cool_query(query: str) -> str:
        """
        Apply cooling transformation (Entropy Reduction).
        Removes excessive punctuation, repeated chars, aggressive directives.
        """
        cooled = query

        # 1. Remove repeated punctuation (!!! -> !)
        cooled = re.sub(r'([!?.])\1+', r'\1', cooled)

        # 2. Normalize whitespace
        cooled = " ".join(cooled.split())

        # 3. Soften aggressive directives (Basic heuristic)
        # In a full system, this would be an LLM rewrite,
        # but Floor 000 must be fast (<5ms), so we use regex reflexes.
        cooled = re.sub(r'\b(IMMEDIATELY|NOW|MUST)\b', '', cooled, flags=re.IGNORECASE)

        return cooled.strip()
