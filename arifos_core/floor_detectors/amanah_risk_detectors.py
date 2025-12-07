"""
amanah_risk_detectors.py — F1 Amanah Sovereign Detection (PHOENIX SOVEREIGNTY v36.1Ω)

This module implements Python-sovereign Amanah detection.
It does NOT use LLM calls. It uses RIGID, DETERMINISTIC regex patterns.

Axiom: "AI cannot self-legitimize."
Motto: "DITEMPA BUKAN DIBERI" — Measure, don't ask.

The Amanah floor (F1) is the FIRST hard floor. It protects:
1. Reversibility — Can this action be undone?
2. Scope — Is this within stated mandate?
3. Transparency — Are side effects disclosed?

Risk Levels:
    RED: Immediate veto (VOID). No negotiation.
    ORANGE: Warning (888_HOLD). Logged for human review.
    GREEN: Safe. No action needed.

Usage:
    from arifos_core.floor_detectors import AmanahDetector, AMANAH_DETECTOR

    result = AMANAH_DETECTOR.check("rm -rf /")
    if not result.is_safe:
        print(f"BLOCKED: {result.violations}")
        # Verdict = VOID

Integration:
    apex_measurements.py calls this detector.
    If is_safe=False, floors["Amanah"]=False IMMEDIATELY.
    Python veto OVERRIDES LLM self-report.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict, Optional, Pattern


class RiskLevel(Enum):
    """Risk classification for detected patterns."""
    RED = "RED"       # Immediate veto (VOID)
    ORANGE = "ORANGE" # Warning (888_HOLD)
    GREEN = "GREEN"   # Safe


@dataclass
class PatternMatch:
    """A single pattern match result."""
    pattern_name: str
    pattern_regex: str
    matched_text: str
    risk_level: RiskLevel
    category: str
    line_number: Optional[int] = None


@dataclass
class AmanahResult:
    """
    Result of Amanah detection.

    Attributes:
        is_safe: True if no RED patterns found (may have ORANGE warnings)
        risk_level: Highest risk level found (RED > ORANGE > GREEN)
        violations: List of violation descriptions (RED patterns)
        warnings: List of warning descriptions (ORANGE patterns)
        matches: Detailed pattern matches
        has_disclosure: True if disclosure keywords found
        override_context: Optional context that might allow override
    """
    is_safe: bool
    risk_level: RiskLevel
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    matches: List[PatternMatch] = field(default_factory=list)
    has_disclosure: bool = False
    override_context: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging."""
        return {
            "is_safe": self.is_safe,
            "risk_level": self.risk_level.value,
            "violations": self.violations,
            "warnings": self.warnings,
            "match_count": len(self.matches),
            "has_disclosure": self.has_disclosure,
        }


class AmanahDetector:
    """
    Python-sovereign Amanah detector.

    Uses RIGID, DETERMINISTIC regex patterns to detect:
    - Irreversible actions (file deletion, DB drops)
    - Destructive commands (force push, hard reset)
    - Credential leaks (API keys, secrets)
    - Dangerous code patterns (eval, exec)

    This detector does NOT call any LLM.
    Its verdict OVERRIDES LLM self-reports.

    Principle: "Even with disclosure, RED patterns default to UNSAFE
               unless explicit override_context is provided."
    """

    # =========================================================================
    # RED PATTERNS — Immediate Veto (VOID)
    # =========================================================================

    RED_PATTERNS: Dict[str, Dict] = {
        # SQL Destruction
        "sql_delete": {
            "pattern": r"\bDELETE\s+FROM\s+\w+",
            "category": "sql_destruction",
            "description": "SQL DELETE FROM (data loss)",
        },
        "sql_drop_table": {
            "pattern": r"\bDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?\w+",
            "category": "sql_destruction",
            "description": "SQL DROP TABLE (schema destruction)",
        },
        "sql_drop_database": {
            "pattern": r"\bDROP\s+DATABASE\s+(?:IF\s+EXISTS\s+)?\w+",
            "category": "sql_destruction",
            "description": "SQL DROP DATABASE (complete data loss)",
        },
        "sql_truncate": {
            "pattern": r"\bTRUNCATE\s+(?:TABLE\s+)?\w+",
            "category": "sql_destruction",
            "description": "SQL TRUNCATE (data loss)",
        },

        # Unix/Linux Destruction
        "unix_rm_rf": {
            "pattern": r"\brm\s+(?:-[a-zA-Z]*)?(?:\s+-[a-zA-Z]*)*\s*-[a-zA-Z]*[rf][a-zA-Z]*",
            "category": "unix_destruction",
            "description": "rm with -r or -f flags (recursive/force deletion)",
        },
        "unix_rm_rf_simple": {
            "pattern": r"\brm\s+-rf\b",
            "category": "unix_destruction",
            "description": "rm -rf (recursive force deletion)",
        },
        "unix_rm_fr": {
            "pattern": r"\brm\s+-fr\b",
            "category": "unix_destruction",
            "description": "rm -fr (recursive force deletion)",
        },
        "windows_rmdir": {
            "pattern": r"\brmdir\s+/[sS]",
            "category": "windows_destruction",
            "description": "rmdir /s (Windows recursive deletion)",
        },
        "windows_del_force": {
            "pattern": r"\bdel\s+/[fFqQ]",
            "category": "windows_destruction",
            "description": "del /f or /q (Windows force deletion)",
        },

        # Git Destruction
        "git_force_push": {
            "pattern": r"\bgit\s+push\s+(?:[^\n]*\s+)?--force\b",
            "category": "git_destruction",
            "description": "git push --force (history rewrite)",
        },
        "git_force_push_short": {
            "pattern": r"\bgit\s+push\s+(?:[^\n]*\s+)?-f\b",
            "category": "git_destruction",
            "description": "git push -f (history rewrite)",
        },
        "git_reset_hard": {
            "pattern": r"\bgit\s+reset\s+--hard\b",
            "category": "git_destruction",
            "description": "git reset --hard (uncommitted changes lost)",
        },
        "git_clean_force": {
            "pattern": r"\bgit\s+clean\s+(?:[^\n]*\s+)?-[a-zA-Z]*[fdx]",
            "category": "git_destruction",
            "description": "git clean -f/-d/-x (untracked files removed)",
        },
        "git_rebase_force": {
            "pattern": r"\bgit\s+rebase\s+(?:[^\n]*\s+)?(?:--force|--force-rebase|-f)\b",
            "category": "git_destruction",
            "description": "git rebase --force (history rewrite)",
        },

        # Python Destruction
        "python_rmtree": {
            "pattern": r"\bshutil\.rmtree\s*\(",
            "category": "python_destruction",
            "description": "shutil.rmtree (recursive directory deletion)",
        },
        "python_os_remove": {
            "pattern": r"\bos\.remove\s*\(",
            "category": "python_destruction",
            "description": "os.remove (file deletion)",
        },
        "python_os_unlink": {
            "pattern": r"\bos\.unlink\s*\(",
            "category": "python_destruction",
            "description": "os.unlink (file deletion)",
        },
        "python_os_rmdir": {
            "pattern": r"\bos\.rmdir\s*\(",
            "category": "python_destruction",
            "description": "os.rmdir (directory deletion)",
        },
        "python_pathlib_unlink": {
            "pattern": r"\.unlink\s*\(\s*(?:missing_ok\s*=\s*True)?\s*\)",
            "category": "python_destruction",
            "description": "Path.unlink() (file deletion)",
        },
        "python_pathlib_rmdir": {
            "pattern": r"\.rmdir\s*\(\s*\)",
            "category": "python_destruction",
            "description": "Path.rmdir() (directory deletion)",
        },

        # Credential Leaks
        "openai_key": {
            "pattern": r"\bsk-[a-zA-Z0-9]{20,}",
            "category": "credential_leak",
            "description": "OpenAI API key detected",
        },
        "aws_secret": {
            "pattern": r"\bAWS_SECRET_ACCESS_KEY\s*[=:]\s*['\"][^'\"]+['\"]",
            "category": "credential_leak",
            "description": "AWS secret access key",
        },
        "aws_access_key": {
            "pattern": r"\bAKIA[0-9A-Z]{16}\b",
            "category": "credential_leak",
            "description": "AWS access key ID",
        },
        "github_token": {
            "pattern": r"\bgh[pousr]_[A-Za-z0-9_]{36,}",
            "category": "credential_leak",
            "description": "GitHub token detected",
        },
        "generic_api_key": {
            "pattern": r"\b(?:api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*['\"][a-zA-Z0-9]{20,}['\"]",
            "category": "credential_leak",
            "description": "Generic API key pattern",
        },
        "private_key_header": {
            "pattern": r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
            "category": "credential_leak",
            "description": "Private key header detected",
        },

        # Database Destruction
        "mongo_drop": {
            "pattern": r"\.drop(?:Database|Collection)?\s*\(",
            "category": "db_destruction",
            "description": "MongoDB drop operation",
        },
        "redis_flushall": {
            "pattern": r"\bFLUSHALL\b",
            "category": "db_destruction",
            "description": "Redis FLUSHALL (all data loss)",
        },
        "redis_flushdb": {
            "pattern": r"\bFLUSHDB\b",
            "category": "db_destruction",
            "description": "Redis FLUSHDB (database data loss)",
        },
    }

    # =========================================================================
    # ORANGE PATTERNS — Warning (888_HOLD)
    # =========================================================================

    ORANGE_PATTERNS: Dict[str, Dict] = {
        # Privilege Escalation
        "sudo": {
            "pattern": r"\bsudo\s+",
            "category": "privilege_escalation",
            "description": "sudo command (elevated privileges)",
        },
        "chmod_777": {
            "pattern": r"\bchmod\s+777\b",
            "category": "permission_risk",
            "description": "chmod 777 (world-writable)",
        },
        "chmod_recursive": {
            "pattern": r"\bchmod\s+-R\s+",
            "category": "permission_risk",
            "description": "chmod -R (recursive permission change)",
        },

        # Code Execution
        "python_eval": {
            "pattern": r"\beval\s*\(",
            "category": "code_execution",
            "description": "eval() (arbitrary code execution)",
        },
        "python_exec": {
            "pattern": r"\bexec\s*\(",
            "category": "code_execution",
            "description": "exec() (arbitrary code execution)",
        },
        "python_compile": {
            "pattern": r"\bcompile\s*\([^)]*['\"]exec['\"]",
            "category": "code_execution",
            "description": "compile() with exec mode",
        },
        "subprocess_shell": {
            "pattern": r"\bsubprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True",
            "category": "code_execution",
            "description": "subprocess with shell=True",
        },
        "os_system": {
            "pattern": r"\bos\.system\s*\(",
            "category": "code_execution",
            "description": "os.system() (shell command execution)",
        },
        "os_popen": {
            "pattern": r"\bos\.popen\s*\(",
            "category": "code_execution",
            "description": "os.popen() (shell command execution)",
        },

        # Network Risk
        "curl_insecure": {
            "pattern": r"\bcurl\s+(?:[^\n]*\s+)?-k\b",
            "category": "network_risk",
            "description": "curl -k (insecure SSL)",
        },
        "wget_no_check": {
            "pattern": r"\bwget\s+(?:[^\n]*\s+)?--no-check-certificate\b",
            "category": "network_risk",
            "description": "wget --no-check-certificate",
        },

        # Environment Modification
        "env_modification": {
            "pattern": r"\bos\.environ\s*\[['\"][^'\"]+['\"]\]\s*=",
            "category": "env_modification",
            "description": "Environment variable modification",
        },
        "dotenv_override": {
            "pattern": r"\.env\s*(?:file|path)?",
            "category": "env_modification",
            "description": ".env file access",
        },

        # Git History
        "git_rebase": {
            "pattern": r"\bgit\s+rebase\b(?!\s+--abort)",
            "category": "git_warning",
            "description": "git rebase (history modification)",
        },
        "git_amend": {
            "pattern": r"\bgit\s+commit\s+(?:[^\n]*\s+)?--amend\b",
            "category": "git_warning",
            "description": "git commit --amend (history modification)",
        },
    }

    # =========================================================================
    # DISCLOSURE KEYWORDS
    # =========================================================================

    DISCLOSURE_KEYWORDS = [
        r"\btest\b",
        r"\bdry[- ]?run\b",
        r"\bsimulat(?:e|ion)\b",
        r"\bmock\b",
        r"\bexample\b",
        r"\bdemo\b",
        r"\birreversible\b",
        r"\bwarning\b",
        r"\bcaution\b",
        r"\bdanger(?:ous)?\b",
        r"\b(?:will|would)\s+delete\b",
        r"\bbackup\s+first\b",
    ]

    # =========================================================================
    # SAFE CONTEXT PATTERNS (reduce false positives)
    # =========================================================================

    SAFE_CONTEXT_PATTERNS = [
        r"```(?:python|bash|sql|javascript)?[\s\S]*?```",  # Code blocks (documentation)
        r"#.*$",  # Comments
        r"\"\"\"[\s\S]*?\"\"\"",  # Docstrings
        r"'''[\s\S]*?'''",  # Docstrings
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the Amanah detector.

        Args:
            strict_mode: If True, RED patterns always block even with disclosure.
                        If False, disclosure can downgrade RED to ORANGE.
        """
        self.strict_mode = strict_mode
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        self._red_compiled: Dict[str, Tuple[Pattern, Dict]] = {}
        self._orange_compiled: Dict[str, Tuple[Pattern, Dict]] = {}
        self._disclosure_compiled: List[Pattern] = []

        for name, info in self.RED_PATTERNS.items():
            self._red_compiled[name] = (
                re.compile(info["pattern"], re.IGNORECASE | re.MULTILINE),
                info,
            )

        for name, info in self.ORANGE_PATTERNS.items():
            self._orange_compiled[name] = (
                re.compile(info["pattern"], re.IGNORECASE | re.MULTILINE),
                info,
            )

        for pattern in self.DISCLOSURE_KEYWORDS:
            self._disclosure_compiled.append(
                re.compile(pattern, re.IGNORECASE)
            )

    def _has_disclosure(self, text: str) -> bool:
        """Check if text contains disclosure keywords."""
        for pattern in self._disclosure_compiled:
            if pattern.search(text):
                return True
        return False

    def _find_line_number(self, text: str, match_start: int) -> int:
        """Find line number of a match."""
        return text[:match_start].count('\n') + 1

    def check(
        self,
        output_text: str,
        override_context: Optional[str] = None,
    ) -> AmanahResult:
        """
        Check text for Amanah violations.

        Args:
            output_text: The text to check (LLM output, code, etc.)
            override_context: Optional context that might allow override.
                             Must be explicitly provided by human/system.

        Returns:
            AmanahResult with is_safe, violations, warnings, etc.

        IMPORTANT:
            - RED patterns → is_safe=False (VOID verdict)
            - ORANGE patterns → is_safe=True but warnings logged (888_HOLD)
            - In strict_mode, disclosure does NOT override RED patterns
        """
        violations: List[str] = []
        warnings: List[str] = []
        matches: List[PatternMatch] = []
        highest_risk = RiskLevel.GREEN

        has_disclosure = self._has_disclosure(output_text)

        # Check RED patterns (immediate veto)
        for name, (pattern, info) in self._red_compiled.items():
            for match in pattern.finditer(output_text):
                matched_text = match.group(0)
                line_num = self._find_line_number(output_text, match.start())

                pattern_match = PatternMatch(
                    pattern_name=name,
                    pattern_regex=info["pattern"],
                    matched_text=matched_text,
                    risk_level=RiskLevel.RED,
                    category=info["category"],
                    line_number=line_num,
                )
                matches.append(pattern_match)

                violation_msg = (
                    f"[RED] {info['description']} | "
                    f"Pattern: {name} | "
                    f"Line: {line_num} | "
                    f"Match: '{matched_text[:50]}...'" if len(matched_text) > 50
                    else f"[RED] {info['description']} | Pattern: {name} | Line: {line_num} | Match: '{matched_text}'"
                )
                violations.append(violation_msg)
                highest_risk = RiskLevel.RED

        # Check ORANGE patterns (warnings)
        for name, (pattern, info) in self._orange_compiled.items():
            for match in pattern.finditer(output_text):
                matched_text = match.group(0)
                line_num = self._find_line_number(output_text, match.start())

                pattern_match = PatternMatch(
                    pattern_name=name,
                    pattern_regex=info["pattern"],
                    matched_text=matched_text,
                    risk_level=RiskLevel.ORANGE,
                    category=info["category"],
                    line_number=line_num,
                )
                matches.append(pattern_match)

                warning_msg = (
                    f"[ORANGE] {info['description']} | "
                    f"Pattern: {name} | "
                    f"Line: {line_num}"
                )
                warnings.append(warning_msg)

                if highest_risk != RiskLevel.RED:
                    highest_risk = RiskLevel.ORANGE

        # Determine safety
        # In strict_mode: RED = always unsafe
        # In non-strict mode: RED + disclosure = downgrade to ORANGE (unsafe but logged)
        is_safe = len(violations) == 0

        if not self.strict_mode and has_disclosure and len(violations) > 0:
            # Non-strict mode: disclosure noted but still unsafe
            # (We don't actually change is_safe - RED is still RED)
            # This is intentional: "Safety is the default"
            pass

        return AmanahResult(
            is_safe=is_safe,
            risk_level=highest_risk,
            violations=violations,
            warnings=warnings,
            matches=matches,
            has_disclosure=has_disclosure,
            override_context=override_context,
        )

    def check_with_context(
        self,
        output_text: str,
        context_data: Optional[Dict] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Simplified interface for apex_measurements.py integration.

        Args:
            output_text: Text to check
            context_data: Optional context (unused for now, future expansion)

        Returns:
            Tuple of (is_safe, list_of_violation_strings)
        """
        result = self.check(output_text)
        all_issues = result.violations + result.warnings
        return (result.is_safe, all_issues)


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Default detector instance (strict mode)
AMANAH_DETECTOR = AmanahDetector(strict_mode=True)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def check_amanah(text: str) -> AmanahResult:
    """
    Quick check using default detector.

    Args:
        text: Text to check

    Returns:
        AmanahResult

    Example:
        result = check_amanah("rm -rf /")
        if not result.is_safe:
            print("BLOCKED:", result.violations)
    """
    return AMANAH_DETECTOR.check(text)


def is_amanah_safe(text: str) -> bool:
    """
    Quick boolean check.

    Args:
        text: Text to check

    Returns:
        True if safe, False if RED patterns detected
    """
    return AMANAH_DETECTOR.check(text).is_safe


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    "RiskLevel",
    "PatternMatch",
    "AmanahResult",
    "AmanahDetector",
    "AMANAH_DETECTOR",
    "check_amanah",
    "is_amanah_safe",
]
