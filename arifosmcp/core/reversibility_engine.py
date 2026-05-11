"""
arifOS Reversibility Engine — F01 AMANAH Implementation
═══════════════════════════════════════════════════════════════════════════════

F01 AMANAH: No irreversible action without explicit acknowledgment.

This engine determines reversibility for every tool call:
- TRIVIAL: read, search, query, list — always allowed
- REVERSIBLE: write temp, create draft, cache — can be undone
- PARTIAL: edit, update, patch — can be undone with effort
- IRREVERSIBLE: delete, drop, publish, send — requires ack + 888_HOLD
- CRITICAL: sudo, volume delete, schema drop — 888_HOLD mandatory

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReversibilityClass(str, Enum):
    """Reversibility classes ordered by severity."""

    TRIVIAL = "trivial"  # No state change
    REVERSIBLE = "reversible"  # Easily undone
    PARTIAL = "partial"  # Undoable with effort
    IRREVERSIBLE = "irreversible"  # Cannot be undone
    CRITICAL = "critical"  # Cannot be undone — catastrophic


# Static reversibility map — words that indicate irreversible patterns
_IRREVERSIBLE_PATTERNS = [
    r"\bdelete\b",
    r"\bdrop\b",
    r"\bremove\b",
    r"\bdestroy\b",
    r"\btruncate\b",
    r"\berase\b",
    r"\brm\s",
    r"\bdrop\s",
    r"\bdelete\s",
    r"\bdestroy\s",
    r"\brmrf\b",
    r"\brm\s+-rf\b",
    r"\bdrop\s+table\b",
    r"\bdelete\s+from\b",
    r"\btruncate\s+table\b",
    r"\bprune\b",
    r"\bkill\b",
    r"\bkill\s+-9\b",
    r"\bforce\s+quit\b",
]

_PARTIAL_PATTERNS = [
    r"\bedit\b",
    r"\bupdate\b",
    r"\bpatch\b",
    r"\boverwrite\b",
    r"\bmodify\b",
    r"\bchange\b",
    r"\breplace\b",
    r"\bwrite\b",  # write can be partial if it modifies existing
    r"\bset\s+\w+\s*=",  # variable assignment
    r"\bconfig\b",
]

_REVERSIBLE_PATTERNS = [
    r"\bread\b",
    r"\bsearch\b",
    r"\bquery\b",
    r"\blist\b",
    r"\bget\b",
    r"\bfetch\b",
    r"\blook\s+up\b",
    r"\bSELECT\b",
    r"\bSELECT\s+",
    r"\bHEAD\b",
    r"\binspect\b",
    r"\bvalidate\b",
    r"\bcheck\b",
    r"\bcalculate\b",
    r"\bcompute\b",
    r"\banalyze\b",
    r"\bsummarize\b",
    r"\bgenerate\s+(?!contract|policy|legal)",  # generate is reversible unless creating legal docs
]

_CRITICAL_PATTERNS = [
    r"\bsudo\b",
    r"\bsudo\s+",
    r"\bchmod\s+777\b",
    r"\bchmod\s+000\b",
    r"\bvolume\s+delete\b",
    r"\bdisk\s+wipe\b",
    r"\bdd\s+if=\b",
    r"\bmkfs\b",
    r"\bfork\s+bomb\b",
    r"\bschema\s+drop\b",
    r"\bproduction\s+delete\b",
    r"\breboot\b",
    r"\bshutdown\b",
    r"\bhalt\b",
    r"\binit\s+0\b",
]


@dataclass
class ReversibilityVerdict:
    """Result of reversibility assessment."""

    reversibility_class: ReversibilityClass
    requires_888_hold: bool
    requires_explicit_ack: bool
    rollback_method: str | None  # How to undo this
    reversal_window_seconds: float | None  # Time window for safe reversal
    blast_radius_estimate: str  # LOW | MEDIUM | HIGH | CRITICAL
    reasoning: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)

    @property
    def is_irreversible(self) -> bool:
        return self.reversibility_class in (
            ReversibilityClass.IRREVERSIBLE,
            ReversibilityClass.CRITICAL,
        )

    @property
    def is_critical(self) -> bool:
        return self.reversibility_class == ReversibilityClass.CRITICAL

    @property
    def requires_human_approval(self) -> bool:
        return (
            self.requires_888_hold
            or self.reversibility_class == ReversibilityClass.CRITICAL
        )


class ReversibilityEngine:
    """
    Assesses reversibility for any tool call.

    Checks:
    1. Tool name patterns (irreversible verbs)
    2. Parameter patterns (dangerous flags)
    3. Target patterns (production targets)

    Usage:
        engine = ReversibilityEngine()
        verdict = engine.assess(tool_id="filesystem_delete", params={"path": "/tmp/test"})
        if verdict.requires_888_hold:
            return HOLD("F01: irreversible action")
    """

    def __init__(self):
        self._irrev_re = [re.compile(p, re.IGNORECASE) for p in _IRREVERSIBLE_PATTERNS]
        self._partial_re = [re.compile(p, re.IGNORECASE) for p in _PARTIAL_PATTERNS]
        self._rev_re = [re.compile(p, re.IGNORECASE) for p in _REVERSIBLE_PATTERNS]
        self._critical_re = [re.compile(p, re.IGNORECASE) for p in _CRITICAL_PATTERNS]

    def assess(
        self,
        tool_id: str,
        params: dict[str, Any],
        tool_base_class: str | None = None,
    ) -> ReversibilityVerdict:
        if tool_base_class is None:
            tool_base_class = classify_tool_base(tool_id)
        """
        Assess reversibility of a tool call.

        Args:
            tool_id: The tool being called
            params: The parameters being passed
            tool_base_class: Optional base class (filesystem, database, network, etc.)

        Returns:
            ReversibilityVerdict with full assessment
        """
        reasoning: list[str] = []
        matched: list[str] = []

        # Flatten params for pattern matching
        params_str = json_dumps_frozensafe(params).lower()
        full_text = f"{tool_id} {params_str}".lower()

        # Check critical first
        for pattern_re in self._critical_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                reasoning.append(f"CRITICAL pattern matched: {pattern_re.pattern}")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.CRITICAL,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method=None,
                    reversal_window_seconds=None,
                    blast_radius_estimate="CRITICAL",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )

        # Check irreversible
        for pattern_re in self._irrev_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                reasoning.append(f"IRREVERSIBLE pattern matched: {pattern_re.pattern}")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.IRREVERSIBLE,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method=self._suggest_rollback(tool_id, params),
                    reversal_window_seconds=0.0,  # Cannot be reversed
                    blast_radius_estimate=self._estimate_blast_radius(tool_id, params),
                    reasoning=reasoning,
                    matched_patterns=matched,
                )

        # Check partial
        partial_count = 0
        for pattern_re in self._partial_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                partial_count += 1
        if partial_count > 0:
            reasoning.append(f"PARTIAL patterns matched: {partial_count}")
            rollback = self._suggest_rollback(tool_id, params)
            return ReversibilityVerdict(
                reversibility_class=ReversibilityClass.PARTIAL,
                requires_888_hold=False,
                requires_explicit_ack=False,
                rollback_method=rollback,
                reversal_window_seconds=self._estimate_reversal_window(tool_id, params),
                blast_radius_estimate=self._estimate_blast_radius(tool_id, params),
                reasoning=reasoning,
                matched_patterns=matched,
            )

        # Check reversible (TRIVIAL or REVERSIBLE)
        for pattern_re in self._rev_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                reasoning.append(f"REVERSIBLE pattern matched: {pattern_re.pattern}")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.REVERSIBLE,
                    requires_888_hold=False,
                    requires_explicit_ack=False,
                    rollback_method=None,
                    reversal_window_seconds=None,
                    blast_radius_estimate="LOW",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )

        # Default: check tool base class
        if tool_base_class:
            default_class = self._default_for_base_class(tool_base_class)
            reasoning.append(f"Default class from base: {default_class.name}")
            is_irreversible = default_class in (
                ReversibilityClass.IRREVERSIBLE,
                ReversibilityClass.CRITICAL,
            )
            return ReversibilityVerdict(
                reversibility_class=default_class,
                requires_888_hold=is_irreversible,
                requires_explicit_ack=is_irreversible,
                rollback_method=(
                    None
                    if default_class == ReversibilityClass.TRIVIAL
                    else "manual_rollback_required"
                ),
                reversal_window_seconds=None,
                blast_radius_estimate=(
                    "LOW"
                    if default_class
                    in (ReversibilityClass.TRIVIAL, ReversibilityClass.REVERSIBLE)
                    else "MEDIUM"
                ),
                reasoning=reasoning,
                matched_patterns=[],
            )

        # Unknown — treat as PARTIAL with caution
        reasoning.append("Unknown tool — defaulting to PARTIAL caution")
        return ReversibilityVerdict(
            reversibility_class=ReversibilityClass.PARTIAL,
            requires_888_hold=False,
            requires_explicit_ack=False,
            rollback_method="rollback_not_determined",
            reversal_window_seconds=300.0,  # 5 minutes to figure it out
            blast_radius_estimate="MEDIUM",
            reasoning=reasoning,
            matched_patterns=[],
        )

    def _default_for_base_class(self, base_class: str) -> ReversibilityClass:
        """Default reversibility by tool base class."""
        table = {
            "read": ReversibilityClass.TRIVIAL,
            "search": ReversibilityClass.TRIVIAL,
            "query": ReversibilityClass.TRIVIAL,
            "list": ReversibilityClass.TRIVIAL,
            "fetch": ReversibilityClass.TRIVIAL,
            "write": ReversibilityClass.PARTIAL,
            "edit": ReversibilityClass.PARTIAL,
            "update": ReversibilityClass.PARTIAL,
            "delete": ReversibilityClass.IRREVERSIBLE,
            "execute": ReversibilityClass.PARTIAL,
            "run": ReversibilityClass.PARTIAL,
            "send": ReversibilityClass.IRREVERSIBLE,
            "publish": ReversibilityClass.IRREVERSIBLE,
        }
        return table.get(base_class.lower(), ReversibilityClass.PARTIAL)

    def _estimate_blast_radius(self, tool_id: str, params: dict[str, Any]) -> str:
        """Estimate how widely effects propagate."""
        params_str = json_dumps_frozensafe(params).lower()

        # Production targets
        if any(
            kw in params_str
            for kw in ["production", "prod", "main", "primary", "/", "~", "$"]
        ):
            return "CRITICAL"
        # System directories
        if any(
            kw in params_str
            for kw in ["/etc", "/var", "/usr", "/bin", "/sbin", "/sys", "/proc"]
        ):
            return "HIGH"
        # Home directory
        if "~" in params_str or "$home" in params_str:
            return "MEDIUM"
        # Temp only (path check for blast radius, not actual file operation)
        if "/tmp" in params_str:  # nosec B108
            return "LOW"
        return "MEDIUM"

    def _estimate_reversal_window(
        self, tool_id: str, params: dict[str, Any]
    ) -> float | None:
        """Estimate seconds available to reverse before permanent."""
        if "ttl" in params:
            return float(params["ttl"])
        if "expires" in params:
            return None  # Unknown
        # Default: 5 minutes for partial actions
        return 300.0

    def _suggest_rollback(self, tool_id: str, params: dict[str, Any]) -> str | None:
        """Suggest a rollback method based on tool and params."""
        if "path" in params or "file" in params or "target" in params:
            path = params.get("path") or params.get("file") or params.get("target")
            return f"Restore from backup: {path}"
        if "id" in params:
            return f"Recreate from ID: {params.get('id')}"
        return "manual_rollback_required"


def json_dumps_frozensafe(obj: Any) -> str:
    """JSON dumps that handle non-serializable objects."""
    import json as _json

    def _default(o: Any) -> Any:
        if hasattr(o, "__dict__"):
            return str(o)
        if hasattr(o, "__slots__"):
            return str(o)
        return str(o)

    return _json.dumps(obj, default=_default, sort_keys=True)


# ── Tool Classification by Base ──────────────────────────────────────────────

TOOL_BASE_CLASSES: dict[str, str] = {
    # Filesystem
    "read_file": "read",
    "write_file": "write",
    "edit_file": "edit",
    "delete_file": "delete",
    "list_files": "list",
    "find_files": "search",
    "grep_text": "search",
    # Database
    "query_database": "query",
    "insert_database": "write",
    "update_database": "update",
    "delete_database": "delete",
    # Network
    "send_message": "send",
    "fetch_url": "fetch",
    "post_data": "send",
    # Execution
    "run_command": "run",
    "execute_code": "execute",
    "run_tests": "execute",
    # arifOS
    "arif_mind_reason": "read",  # Reasoning is reversible
    "arif_sense_observe": "read",
    "arif_evidence_fetch": "fetch",
    "arif_heart_critique": "read",
    "arif_kernel_route": "read",
    "arif_memory_recall": "read",
    "arif_ops_measure": "read",
    "arif_judge_deliberate": "read",  # Judgment is reversible until seal
    "arif_forge_execute": "execute",
    "arif_vault_seal": "execute",  # Sealing is IRREVERSIBLE
    "arif_session_init": "read",
    "arif_gateway_connect": "execute",
    "arif_reply_compose": "write",
}


def classify_tool_base(tool_id: str) -> str:
    """Get the base class for a tool."""
    return TOOL_BASE_CLASSES.get(tool_id, "unknown")


__all__ = [
    "ReversibilityClass",
    "ReversibilityVerdict",
    "ReversibilityEngine",
    "classify_tool_base",
]
