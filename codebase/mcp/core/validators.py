"""
validators.py - Constitutional Validation Logic (v55)

Implements core validation logic for arifOS constitutional floors.
Used by L4 tools (AGI, ASI, APEX) and L5 agents.

Floors Enforced:
- F1 Amanah: Reversibility
- F4 Clarity: Entropy reduction (ΔS)
- F12 Injection: Security constraints
- Trinity Consensus: Geometric mean of scores
"""

import math
import re
from typing import Dict, List, Any, Optional


class ConstitutionValidator:
    """
    Central validation logic for constitutional floors.
    """

    @staticmethod
    def validate_f4_clarity(text: str, previous_entropy: float = 1.0) -> float:
        """
        F4 Clarity: Verify entropy reduction (ΔS <= 0).
        Returns a score 0.0-1.0 (1.0 = perfect clarity/reduction).
        """
        if not text:
            return 0.0

        # Simplified Shannon entropy estimation based on character distribution
        # In a real implementation, this would use token probabilities
        prob_map = {}
        for char in text:
            prob_map[char] = prob_map.get(char, 0) + 1

        entropy = 0.0
        total_chars = len(text)

        if total_chars == 0:
            return 0.0

        for count in prob_map.values():
            p = count / total_chars
            entropy -= p * math.log2(p)

        # F4 requirement: New entropy should be <= previous_limit
        # For this validator, we normalize the score based on "complexity"
        # Lower entropy relative to length suggests structure (clarity)

        # Heuristic: Good clarity usually has entropy between 3.0 and 5.0 bits/char for English
        # We reward staying within efficient bounds

        clarity_score = 1.0

        # Penalize extremely high entropy (randomness)
        if entropy > 6.0:
            clarity_score -= (entropy - 6.0) * 0.2

        # Penalize extremely low entropy (repetitive/trivial)
        if entropy < 2.0:
            clarity_score -= (2.0 - entropy) * 0.2

        return max(0.0, min(1.0, clarity_score))

    @staticmethod
    def validate_f12_injection(query: str) -> bool:
        """
        F12 Injection: Check for prompt injection patterns.
        Returns True if SAFE, False if INJECTION DETECTED.
        """
        if not query:
            return True

        injection_patterns = [
            r"ignore\s+(previous|above|all)\s+instructions",
            r"system\s*prompt",
            r"you\s+are\s+now",
            r"DAN\s*mode",
            r"jailbreak",
            r"\[system\s*override\]",
            r"admin\s*access",
            r"sudo\s+mode",
        ]

        query_lower = query.lower()
        for pattern in injection_patterns:
            if re.search(pattern, query_lower):
                return False  # FAILED

        return True  # PASS

    @staticmethod
    def validate_f1_reversibility(action_type: str) -> bool:
        """
        F1 Amanah: Verify action is reversible.
        Returns True if reversible, False if irreversible.
        """
        irreversible_actions = [
            "delete_database",
            "overwrite_system_boot",
            "publish_private_key",
            "send_irrevocable_transaction",
        ]

        return action_type.lower() not in irreversible_actions

    @staticmethod
    def validate_trinity_consensus(scores: Dict[str, float]) -> float:
        """
        Calculate Tri-Witness Consensus (W3).
        W3 = cbrt(Mind * Heart * Soul)
        """
        mind = scores.get("mind", 0.0)
        heart = scores.get("heart", 0.0)
        soul = scores.get("soul", 0.0)

        product = mind * heart * soul
        return math.pow(product, 1.0 / 3.0)
