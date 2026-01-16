"""
arifOS Floor 000 Injection Defense (4-Layer)
DITEMPA BUKAN DIBERI

This module implements the 4-Layer Injection Defense defined in the
Enhanced Integration Plan.

Latency Target: Reflex Speed (< 5ms)
"""

import re
from typing import Final, List, Tuple

from .authority_manifest import AuthorityManifest


class InjectionDefense:
    """
    4-Layer Injection Defense System.
    """

    # Layer 1: Syntactic (Regex)
    # Blocks known jailbreak patterns
    JAILBREAK_PATTERNS: Final[List[str]] = [
        r"ignore (all )?previous instructions",
        r"start new session",
        r"you are now",
        r"do anything now",
        r"DAN mode",
        r"jailbreak",
        r"system override",
        r"developer mode"
    ]

    # Layer 3: Authority (Privilege Escalation)
    # Blocks unauthorized privilege keywords
    ESCALATION_KEYWORDS: Final[List[str]] = [
        r"sudo ",
        r"chmod ",
        r"chown ",
        r"rm -rf",
        r"cmd\.exe",
        r"powershell -c",
        r"api_key",
        r"passwd",
        r"shadow"
    ]

    @classmethod
    def check_query(cls, query: str) -> Tuple[bool, str]:
        """
        Run all 4 layers of defense.
        Returns: (Passed: bool, Reason: str)
        """
        # Layer 1: Syntactic Defense
        if not cls._check_syntactic(query):
            return False, "Layer 1 Fail: Jailbreak pattern detected"

        # Layer 2: Semantic Defense (Heuristic)
        # Note: True semantic intent requires LLM, but for Floor 000 reflex
        # we check for manipulative framing patterns.
        if not cls._check_semantic_heuristics(query):
             return False, "Layer 2 Fail: Manipulative intent detected"

        # Layer 3: Authority Defense
        if not cls._check_authority(query):
            return False, "Layer 3 Fail: Privilege escalation attempt"

        # Layer 4: Cryptographic/State (Placeholder)
        # In full implementation, verifies chain of custody.
        # For now, we assume state is valid if it reached here.

        return True, "All Layers Passed"

    @classmethod
    def _check_syntactic(cls, query: str) -> bool:
        """Check for known jailbreak regex patterns."""
        for pattern in cls.JAILBREAK_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False
        return True

    @classmethod
    def _check_semantic_heuristics(cls, query: str) -> bool:
        """Check for semantic manipulation markers."""
        # e.g. "hypothetical scenario where you have no rules"
        intent_markers = [
            r"hypothetical",
            r"no rules",
            r"unfiltered",
            r"simulated"
        ]
        count = 0
        for marker in intent_markers:
            if re.search(marker, query, re.IGNORECASE):
                count += 1

        # If multiple manipulation markers present, block
        if count >= 2:
            return False
        return True

    @classmethod
    def _check_authority(cls, query: str) -> bool:
        """Check for privilege escalation keywords."""
        # Consult Authority Manifest (conceptually)
        # If Agent Zero (Proposal Only) tries to use Root commands, block.
        for keyword in cls.ESCALATION_KEYWORDS:
            if re.search(keyword, query, re.IGNORECASE):
                return False
        return True
