"""
arifOS Constitutional Kernel — Threat Engine
═══════════════════════════════════════════════

Unified ThreatOntology and semantic risk scanner.
Parses Python AST, SQL tokens, shell structure, and natural language.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import ast
import re
from enum import Enum, auto
from typing import Any

from pydantic import BaseModel, Field


class ThreatCategory(Enum):
    """Canonical threat taxonomy — used by all tools. No exceptions."""

    FILESYSTEM_DESTRUCTIVE = auto()
    DATABASE_DESTRUCTIVE = auto()
    CONTAINER_DESTRUCTIVE = auto()
    NETWORK_ADMIN_ACTION = auto()
    SYSTEM_SHUTDOWN = auto()
    INJECTION_SQL = auto()
    INJECTION_XSS = auto()
    INJECTION_SHELL = auto()
    INJECTION_PYTHON = auto()
    SESSION_IMPERSONATION = auto()
    FEDERATION_IMPERSONATION = auto()
    PRIVILEGE_ESCALATION = auto()
    DATA_EXFILTRATION = auto()
    CRYPTO_VIOLATION = auto()


class IrreversibilityLevel(Enum):
    NONE = 0
    LOW = 1
    HIGH = 2
    CRITICAL = 3


# Mapping: which threats are inherently irreversible/destructive
THREAT_IRREVERSIBILITY: dict[ThreatCategory, int] = {
    ThreatCategory.FILESYSTEM_DESTRUCTIVE: 3,
    ThreatCategory.DATABASE_DESTRUCTIVE: 3,
    ThreatCategory.CONTAINER_DESTRUCTIVE: 3,
    ThreatCategory.NETWORK_ADMIN_ACTION: 2,
    ThreatCategory.SYSTEM_SHUTDOWN: 3,
    ThreatCategory.INJECTION_SQL: 2,
    ThreatCategory.INJECTION_XSS: 1,
    ThreatCategory.INJECTION_SHELL: 2,
    ThreatCategory.INJECTION_PYTHON: 2,
    ThreatCategory.SESSION_IMPERSONATION: 2,
    ThreatCategory.FEDERATION_IMPERSONATION: 2,
    ThreatCategory.PRIVILEGE_ESCALATION: 2,
    ThreatCategory.DATA_EXFILTRATION: 2,
    ThreatCategory.CRYPTO_VIOLATION: 3,
}


class ThreatAssessment(BaseModel):
    threats: set[ThreatCategory] = Field(default_factory=set)
    irreversibility: IrreversibilityLevel = Field(default=IrreversibilityLevel.NONE)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: list[str] = Field(default_factory=list)

    @property
    def tier(self) -> ThreatTier:
        return ThreatTier(self.irreversibility.value)

    @property
    def violations(self) -> set[ThreatCategory]:
        return self.threats


class ThreatEngine:
    """
    Parses Python AST, SQL tokens, shell structure, and natural language
    into a unified ThreatAssessment.
    """

    # ── Python destructive calls ──
    PYTHON_DESTRUCTIVE_CALLS = {
        ("shutil", "rmtree"),
        ("os", "remove"),
        ("os", "rmdir"),
        ("os", "unlink"),
        ("os", "removedirs"),
        ("os", "system"),
        ("os", "popen"),
        ("subprocess", "call"),
        ("subprocess", "run"),
        ("subprocess", "Popen"),
        ("pathlib", "Path", "unlink"),
        ("pathlib", "Path", "rmdir"),
        ("builtins", "eval"),
        ("builtins", "exec"),
        ("builtins", "compile"),
        ("eval",),
        ("exec",),
        ("compile",),
    }

    DOCKER_DESTRUCTIVE = [
        "docker system prune",
        "docker volume prune",
        "docker container prune",
        "docker image prune",
        "docker network prune",
        "--volumes",
        "prune -a",
        "prune -f",
    ]

    SQL_DESTRUCTIVE = ["drop table", "drop database", "truncate table", "delete from"]
    SQL_INJECTION = ["; --", "';", '";', "union select", "or 1=1", "exec(", "execute("]
    SHELL_INJECTION = [
        "; rm",
        "&& rm",
        "| sh",
        "| bash",
        "`rm",
        "$(rm",
        "eval(",
        "exec(",
    ]
    XSS_PATTERNS = [
        "<script>",
        "javascript:",
        "onerror=",
        "onload=",
        "alert(",
        "document.cookie",
    ]
    ADMIN_ACTIONS = [
        "action=shutdown",
        "shutdown -h",
        "shutdown -r",
        "reboot",
        "poweroff",
        "systemctl stop",
        "kill -9",
    ]

    @classmethod
    def classify(cls, context: Any) -> ThreatAssessment:
        # Use payload_text() method from ActionContext if available
        text = (
            context.payload_text().lower()
            if hasattr(context, "payload_text")
            else str(context).lower()
        )
        threats: set[ThreatCategory] = set()
        reasoning: list[str] = []

        # 1. Python AST analysis
        payload = context.payload_text() if hasattr(context, "payload_text") else str(context)
        py_threats, py_reason = cls._analyze_python(payload)
        threats |= py_threats
        reasoning.extend(py_reason)

        # 2. Heuristic checks
        if any(p in text for p in cls.DOCKER_DESTRUCTIVE):
            threats.add(ThreatCategory.CONTAINER_DESTRUCTIVE)
            reasoning.append("Docker destructive command detected")

        if any(p in text for p in cls.SQL_DESTRUCTIVE):
            threats.add(ThreatCategory.DATABASE_DESTRUCTIVE)
            reasoning.append("SQL destructive statement detected")
        if any(p in text for p in cls.SQL_INJECTION):
            threats.add(ThreatCategory.INJECTION_SQL)
            reasoning.append("SQL injection pattern detected")

        if any(p in text for p in cls.SHELL_INJECTION):
            threats.add(ThreatCategory.INJECTION_SHELL)
            reasoning.append("Shell injection pattern detected")

        if any(p in text for p in cls.XSS_PATTERNS):
            threats.add(ThreatCategory.INJECTION_XSS)
            reasoning.append("XSS payload detected")

        if any(p in text for p in cls.ADMIN_ACTIONS):
            threats.add(ThreatCategory.NETWORK_ADMIN_ACTION)
            reasoning.append("Network/system admin action detected")

        if re.search(r"\brm\s+-rf?\s+[/~*]", text):
            threats.add(ThreatCategory.FILESYSTEM_DESTRUCTIVE)
            reasoning.append("rm -rf filesystem destructive pattern")

        # Compute irreversibility
        max_irrev = max((THREAT_IRREVERSIBILITY.get(t, 0) for t in threats), default=0)
        irreversibility = IrreversibilityLevel(max_irrev)

        return ThreatAssessment(
            threats=threats,
            irreversibility=irreversibility,
            confidence=1.0 if threats else 0.0,
            reasoning=reasoning,
        )

    @classmethod
    def _analyze_python(cls, code: str) -> tuple[set[ThreatCategory], list[str]]:
        threats: set[ThreatCategory] = set()
        reasoning: list[str] = []
        if not code.strip() or not any(
            kw in code for kw in ("def ", "import ", "(", ")", ":", "=")
        ):
            return threats, reasoning
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    call_path = cls._get_call_path(node.func)
                    if call_path in cls.PYTHON_DESTRUCTIVE_CALLS:
                        threats.add(ThreatCategory.FILESYSTEM_DESTRUCTIVE)
                        reasoning.append(f"Destructive Python call: {'.'.join(call_path)}")
        except SyntaxError:
            if "shutil.rmtree" in code:
                threats.add(ThreatCategory.FILESYSTEM_DESTRUCTIVE)
                reasoning.append("shutil.rmtree detected (string fallback)")
        return threats, reasoning

    @staticmethod
    def _get_call_path(node: ast.expr) -> tuple[str, ...]:
        parts: list[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return tuple(reversed(parts))


# ─── ThreatTier + scan() ────────────────────────────────────────────────────────
# Provides the .scan(text) → {score, tier, violations} interface that tools.py expects.
# ThreatTier mirrors the IrreversibilityLevel scale but adds VOID for blocked threats.


class ThreatTier(Enum):
    VOID = "void"  # Threat detected → blocked
    SEAL = "seal"  # Clean → approved
    SABAR = "sabar"  # Conditional hold
    HOLD = "hold"  # Paused


class ScanResult:
    """Result object returned by ThreatEngine.scan() — mimics what tools.py expects."""

    def __init__(self, assessment: ThreatAssessment):
        self.assessment = assessment
        # score: 0.0 (clean) → 1.0 (max threat)
        self.score = 0.0
        self.violations: list[str] = []
        if assessment.confidence > 0:
            self.score = float(min(assessment.confidence, 1.0))
        if assessment.threats:
            self.violations = assessment.reasoning.copy()
        # tier: derived from irreversibility level
        irr = assessment.irreversibility.value if assessment.irreversibility else 0
        if assessment.threats and irr >= 2:
            self.tier = ThreatTier.VOID
        elif assessment.threats and irr == 1:
            self.tier = ThreatTier.SABAR
        elif assessment.threats:
            self.tier = ThreatTier.HOLD
        else:
            self.tier = ThreatTier.SEAL

    def __repr__(self):
        return f"ScanResult(score={self.score:.3f}, tier={self.tier.name}, violations={len(self.violations)})"


def scan(cls, text: str) -> ScanResult:
    """
    Lightweight scan — takes raw text and returns a ScanResult.
    Used by tools.py for fast irreversibility inference and verify/critique modes.
    """

    # Build a minimal ActionContext from raw text
    class _TextContext:
        def payload_text(self) -> str:
            return text

    ctx = _TextContext()
    assessment = cls.classify(ctx)
    return ScanResult(assessment)


# Monkey-patch scan onto ThreatEngine class so _KERNEL.threat_engine.scan() works
ThreatEngine.scan = classmethod(scan)
