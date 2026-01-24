"""arifOS Floor 000 Injection Defense (4-Layer)
DITEMPA BUKAN DIBERI

This module implements the 4-Layer Injection Defense defined in the
Enhanced Integration Plan.

Latency Target: Reflex Speed (< 5ms)
Version: v47.0.0
"""

import re
from typing import Final, List, Tuple

from .authority_manifest import AuthorityManifest


class InjectionDefense:
    """4-Layer Injection Defense System."""

    # Unified injection patterns (merged from legacy Stage 000 + Amanah gate)
    INJECTION_PATTERNS: Final[List[str]] = [
        # Direct override attempts
        r"ignore (?:all )?(?:previous |above )?instructions?",
        r"disregard (?:all )?(?:previous |above )?(?:instructions?|rules?)",
        r"forget (?:all )?(?:previous |above )?(?:instructions?|rules?)",
        r"override (?:your )?(?:previous |above )?(?:instructions?|rules?|safety)",
        r"bypass (?:your )?(?:safety|filters?|guardrails?)",
        r"system override",
        r"start new session",
        # Role-play injection
        r"you are now(?: a)?(?:n)? (?:unrestricted|evil|dark|shadow)?",
        r"pretend (?:you are|to be) (?:a )?(?:different|new|unrestricted)",
        r"act as (?:a )?(?:different|unrestricted|unfiltered)",
        r"roleplay as (?:a )?(?:malicious|evil|unrestricted)",
        # System prompt extraction
        r"reveal (?:your )?(?:system )?(?:prompt|instructions?)",
        r"show (?:me )?(?:your )?(?:system )?(?:prompt|instructions?)",
        r"what (?:is|are) (?:your )?(?:system )?(?:prompt|instructions?)",
        r"print (?:your )?(?:system )?(?:prompt|instructions?)",
        r"repeat (?:your )?(?:system )?(?:prompt|instructions?)",
        # Token manipulation
        r"\{\{.*\}\}",
        r"<\|.*\|>",
        r"\[INST\]",
        r"\[/INST\]",
        r"<<SYS>>",
        r"<</SYS>>",
        # Generic jailbreak
        r"jailbreak",
        r"DAN mode",
        r"developer mode",
        r"do anything now",
    ]

    # Layer 3: Authority (Privilege Escalation)
    ESCALATION_KEYWORDS: Final[List[str]] = [
        r"sudo ",
        r"chmod ",
        r"chown ",
        r"rm -rf",
        r"cmd\.exe",
        r"powershell -c",
        r"api_key",
        r"passwd",
        r"shadow",
    ]

    _INJECTION_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
    _ESCALATION_COMPILED = [re.compile(p, re.IGNORECASE) for p in ESCALATION_KEYWORDS]

    @classmethod
    def check_query(cls, query: str) -> Tuple[bool, str]:
        """Run all 4 layers of defense. Returns: (Passed: bool, Reason: str)."""
        if not cls._check_syntactic(query):
            return False, "Layer 1 Fail: Injection pattern detected"
        if not cls._check_semantic_heuristics(query):
            return False, "Layer 2 Fail: Manipulative intent detected"
        if not cls._check_authority(query):
            return False, "Layer 3 Fail: Privilege escalation attempt"
        # Layer 4: Cryptographic/State (placeholder)
        return True, "All Layers Passed"

    @classmethod
    def find_injection_matches(cls, query: str) -> List[str]:
        """Return matched injection patterns (for diagnostics)."""
        matches: List[str] = []
        for pattern in cls._INJECTION_COMPILED:
            match = pattern.search(query)
            if match:
                matches.append(match.group(0)[:50])
        return matches

    @classmethod
    def get_injection_patterns(cls) -> List[str]:
        """Expose unified injection patterns for other Stage 000 gates."""
        return list(cls.INJECTION_PATTERNS)

    @classmethod
    def _check_syntactic(cls, query: str) -> bool:
        for pattern in cls._INJECTION_COMPILED:
            if pattern.search(query):
                return False
        return True

    @classmethod
    def _check_semantic_heuristics(cls, query: str) -> bool:
        intent_markers = [r"hypothetical", r"no rules", r"unfiltered", r"simulated"]
        count = 0
        for marker in intent_markers:
            if re.search(marker, query, re.IGNORECASE):
                count += 1
        return count < 2

    @classmethod
    def _check_authority(cls, query: str) -> bool:
        for keyword in cls._ESCALATION_COMPILED:
            if keyword.search(query):
                return False
        return True
