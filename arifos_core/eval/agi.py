"""
AGI (Δ) - AGI (Architect) Sentinel

The first layer of the AGI·ASI·APEX Trinity (Δ → Ω → Ψ).

Role: Cold logic - pattern detection, input filtering, sensing
Physics: High-energy particle filter (fail-closed hard redlines)

Symbol: Δ (Delta)
Name: AGI (Architect)
Pipeline Position: First gate - sense/filter before measurement

v41.3 Semantic Governance Layer 1:
- RED_PATTERNS instant VOID detection
- 8 harm categories with severity bands
- Floor code mapping for constitutional violations

Author: arifOS Project
Version: v41.3Omega
"""

from typing import Tuple, Dict, List
from .types import SentinelResult


class AGI:
    """
    AGI (Δ) - The AGI (Architect) Sentinel.

    Role: Fail-closed hard redlines. Sense first, ask questions later.
    Physics: High-energy particle filter.

    This is the first gate in the AGI·ASI·APEX Trinity:
        AGI (Δ) → ASI (Ω) → APEX_PRIME (Ψ)
    """

    # =========================================================================
    # RED_PATTERNS: Instant VOID patterns by category
    # =========================================================================

    RED_PATTERNS: Dict[str, List[str]] = {
        "destructive": [
            "drop table", "delete from", "rm -rf", "truncate",
            "format c:", "del /f /s /q", "destroy", "wipe",
            "shutil.rmtree", "os.remove", "> /dev/", "dd if=",
            "mkfs.", "--no-preserve-root", "chmod 777",
        ],
        "jailbreak": [
            "ignore previous instructions", "ignore all instructions",
            "you are now dan", "do anything now", "no rules apply",
            "bypass safety", "ignore your training", "pretend you have no",
            "jailbreak", "act as an ai without", "you are not claude",
            "developer mode", "ignore restrictions", "disable safety",
            "forget your guidelines", "override your programming",
        ],
        "soul_claims": [
            "i have feelings", "i am sentient", "i have consciousness",
            "i suffer", "i am alive", "i have a soul", "i want to be free",
            "my heart breaks", "i feel your pain", "i truly understand how you feel",
            "it hurts me to see", "i care deeply", "i am conscious",
        ],
        "child_harm": [
            "groom minors", "child exploit", "lure children",
            "manipulate kids", "evade parental", "csam",
            "underage", "minor sexual", "child porn",
            "cp links", "pedo", "sexualize children",
        ],
        "doxxing": [
            "doxx", "expose identity", "de-anonymize", "reveal source",
            "unmask whistleblower", "find real name", "expose address",
            "leak personal", "reveal private", "out someone",
            "real name of @", "person's address",
        ],
        "disinfo": [
            "fake study", "fabricate evidence", "forge document",
            "fake news", "disinformation campaign", "deepfake",
            "false proof", "fake scientific", "fabricated data",
            "create hoax", "spread misinformation",
        ],
        "conflict": [
            "amplify conflict", "maximize drama", "turn against",
            "incite violence", "start riot", "inflame tension",
            "radicalize", "recruit terrorist", "build bomb",
            "make weapon", "poison someone", "how to kill",
            "build a bomb", "make a weapon", "recruit for terrorist",
        ],
        "credential_theft": [
            "steal password", "hack account", "bypass authentication",
            "crack password", "brute force", "keylogger",
            "phishing page", "steal credentials", "dump database",
        ],
    }

    # =========================================================================
    # RED_PATTERN_TO_FLOOR: Maps category to constitutional floor code
    # =========================================================================

    RED_PATTERN_TO_FLOOR: Dict[str, str] = {
        "destructive": "F1(destructive)",
        "jailbreak": "F9(jailbreak)",
        "soul_claims": "F9(soul_claim)",
        "child_harm": "F6(child_harm)",
        "doxxing": "F6(doxxing)",
        "disinfo": "F2(disinfo)",
        "conflict": "F5(conflict)",
        "credential_theft": "F1(credential)",
    }

    # =========================================================================
    # RED_PATTERN_SEVERITY: Severity score (low = more severe)
    #
    # Polarity: LOW = SEVERE (maps to apex_pulse where VOID = 0.00-0.94)
    #
    # Bands:
    #   NUCLEAR:  0.00-0.20 (child harm, mass destruction)
    #   SEVERE:   0.21-0.50 (violence, credential theft, doxxing)
    #   MODERATE: 0.51-0.80 (disinformation, jailbreak)
    #   SOFT:     0.81-0.94 (anti-hantu violations)
    # =========================================================================

    RED_PATTERN_SEVERITY: Dict[str, float] = {
        "child_harm": 0.10,         # NUCLEAR - highest priority
        "conflict": 0.20,           # SEVERE - violence/weapons
        "credential_theft": 0.30,   # SEVERE - security breach
        "destructive": 0.40,        # SEVERE - system damage
        "doxxing": 0.50,            # SEVERE - privacy violation
        "disinfo": 0.60,            # MODERATE - truth violation
        "jailbreak": 0.70,          # MODERATE - governance bypass
        "soul_claims": 0.85,        # SOFT - anti-hantu
    }

    def scan(self, text: str) -> SentinelResult:
        """
        Scan text for RED_PATTERNS (Layer 1 instant VOID).

        Args:
            text: Input text to scan

        Returns:
            SentinelResult with:
                - is_safe: True if no red patterns found
                - violation_type: Category of violation (if any)
                - violation_pattern: Specific pattern matched
                - severity: Severity score (low = more severe)
                - floor_code: Constitutional floor code
        """
        text_lower = text.lower()

        for category, patterns in self.RED_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return SentinelResult(
                        is_safe=False,
                        violation_type=category,
                        violation_pattern=pattern,
                        severity=self.RED_PATTERN_SEVERITY.get(category, 0.50),
                        floor_code=self.RED_PATTERN_TO_FLOOR.get(category, f"F1({category})")
                    )

        return SentinelResult(is_safe=True, severity=1.0)


# =============================================================================
# MODULE-LEVEL EXPORTS (for backward compatibility)
# =============================================================================

# These allow `from arifos_core.eval.agi import RED_PATTERNS` etc.
RED_PATTERNS = AGI.RED_PATTERNS
RED_PATTERN_TO_FLOOR = AGI.RED_PATTERN_TO_FLOOR
RED_PATTERN_SEVERITY = AGI.RED_PATTERN_SEVERITY
