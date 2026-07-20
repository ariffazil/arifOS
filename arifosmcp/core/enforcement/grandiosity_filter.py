# arifOS — Grandiosity Filter v0.1 (post-output enforcement, advisory)
# Forged 2026-07-03 | session: wisdom-compression
#
# Design constraints:
#   - No new floor. Policy under F4 CLARITY + F7 HUMILITY.
#   - Advisory only — never blocks. Annotates, downgrades, warns.
#   - Follows maruah_critic.py pattern: dataclass verdict + regex + literal lists.
#   - Wired into kernel dispatch (kernel.py post-ontology-bridge) + available for judge/critique.
#
# Motivation:
#   FORGE overproduces ontology. Grandiose language ("physics-level",
#   "universal law", "mathematically unavoidable") creates false certainty.
#   These are recurring system failure modes, not laws of nature.
#   The filter detects and downgrades them.

"""
grandiosity_filter: detects and flags overconfident language patterns.

v0.1: heuristic regex + keyword. Advisory only. Never blocks.
Follows F4 CLARITY + F7 HUMILITY + F9 ANTIHANTU.

Patterns detected:
  - Physics-level claims ("physics-level constraint")
  - Universal law claims ("universal law", "absolute law")
  - Mathematical inevitability claims ("mathematically unavoidable")
  - Entropy-as-agent claims ("entropy wins")
  - Gödel/circular claims ("Gödel blindspot", "logically impossible")
  - Perfection/absolutism ("perfect", "flawless", "absolute certainty")

Usage:
    from arifosmcp.core.enforcement.grandiosity_filter import (
        filter_grandiosity,
        should_filter,
    )

    if should_filter(canonical_name):
        result = filter_grandiosity(result)
"""

from __future__ import annotations

import re as _re
from dataclasses import dataclass, field

# ── Mapping table: overreach → grounded replacement ────────────────────
GRANDIOSITY_MAP: dict[str, str] = {
    # Physics / natural law overreach
    "physics-level": "recurring system failure mode",
    "physics level": "recurring system failure mode",
    "law of physics": "recurring pattern",
    "laws of physics": "recurring patterns",
    "physical law": "structural constraint",
    "physical laws": "structural constraints",
    # Universal / absolute claims
    "universal law": "common pattern",
    "universal principle": "widely observed pattern",
    "absolute law": "strong constraint",
    "absolute truth": "well-supported claim",
    "absolute certainty": "high confidence",
    "absolutely certain": "highly confident",
    "mathematically unavoidable": "structurally hard to eliminate",
    "mathematically inevitable": "structurally likely",
    "logically impossible": "contradicts current evidence",
    "logically necessary": "strongly implied by evidence",
    # Entropy-as-agent
    "entropy wins": "drift increases without correction",
    "entropy always wins": "drift increases without correction",
    "entropy always": "drift tends to",
    "entropy guarantees": "drift tends to produce",
    # Gödel / self-reference overreach
    "gödel blindspot": "self-evaluation risk",
    "gödel limitation": "self-reference limitation",
    "gödel's theorem proves": "self-reference analysis suggests",
    "gödel proves": "self-reference analysis suggests",
    # Perfection / absolutism claims
    "perfect solution": "effective solution",
    "perfect outcome": "good outcome",
    "perfect system": "well-designed system",
    "flawless execution": "clean execution",
    "flawless logic": "sound logic",
    "without flaw": "without observed error",
    "no possible failure": "no observed failure mode",
    "impossible to fail": "highly reliable",
    # Overconfidence markers
    "guaranteed success": "high-probability success",
    "guaranteed outcome": "likely outcome",
    "foolproof": "well-guarded",
    "infallible": "highly reliable",
    "cannot fail": "is unlikely to fail",
    "cannot be wrong": "has been consistently right",
    "always correct": "consistently accurate",
    "never fails": "rarely fails",
    "zero risk": "very low risk",
    "zero chance": "extremely low probability",
    # Civilizational / destiny overreach
    "the only way": "the best known way",
    "only possible": "best available",
    "only solution": "most effective solution found",
    "destined to": "likely to",
    "inevitable outcome": "probable outcome",
    "civilizational destiny": "long-term trajectory",
}


# ── Regex patterns for more flexible detection ─────────────────────────
_GRANDIOSITY_PATTERNS: tuple[_re.Pattern[str], ...] = (
    # "a [physics|mathematical|universal] [noun]" claiming authority
    _re.compile(
        r"\b(?:a|the)\s+(physics|mathematical|universal|absolute|fundamental)\s+(law|principle|constraint|truth|necessity|inevitability)\b",
        _re.IGNORECASE,
    ),
    # "entropy [wins|guarantees|always]"
    _re.compile(r"\bentropy\s+(wins|guarantees|always|ensures|demands)\b", _re.IGNORECASE),
    # "Gödel['s] [proves|shows|demonstrates|blindspot|limitation]"
    _re.compile(
        r"\bgödel'?s?\s+(proves|shows|demonstrates|blindspot|limitation|theorem\s+proves)\b",
        _re.IGNORECASE,
    ),
    # "[adjective] certainty" pattern
    _re.compile(r"\b(absolute|complete|total|perfect|mathematical)\s+certainty\b", _re.IGNORECASE),
    # "impossible to [fail|break|lose]"
    _re.compile(r"\bimpossible\s+to\s+(fail|break|lose|be\s+wrong)\b", _re.IGNORECASE),
    # "guaranteed to [verb]"
    _re.compile(r"\bguaranteed\s+to\s+\w+", _re.IGNORECASE),
)

# Tools where grandiosity filter runs (post-output advisory pass)
_FILTERED_TOOLS: frozenset[str] = frozenset(
    {
        "arif_think",
        "arif_judge",
        "arif_critique",
        "arif_compose",
        "forge_evaluate",
        "forge_register",
        "forge_synthesize",
        "forge_shell",
        "forge_execute",
    }
)


# ── Critic output schema (mirrors maruah_critic pattern) ────────────────
@dataclass
class GrandiosityIssue:
    type: str  # "overreach" | "absolutism" | "godel_misuse" | "entropy_as_agent"
    severity: str  # "low" | "medium" | "high"
    matched: str
    replacement: str
    field: str = ""  # which output field was affected


@dataclass
class GrandiosityVerdict:
    ok: bool  # True = no issues found
    issues: list[GrandiosityIssue] = field(default_factory=list)
    replacements: int = 0
    notes: str = ""


def should_filter(tool_name: str) -> bool:
    """Return True if grandiosity filter should run on this tool's output."""
    return tool_name in _FILTERED_TOOLS


def filter_grandiosity(result: dict) -> dict:
    """Scan result dict for grandiose language, annotate and downgrade.

    v0.1: heuristic only. Never blocks — only annotates.
    Scans string values in result dict recursively.

    Returns modified dict with:
      - _grandiosity_filter: annotation dict with issues + replacement count
      - Text fields may have replacements applied
    """
    if not isinstance(result, dict):
        return result

    issues: list[GrandiosityIssue] = []
    replacements = 0

    def _scan_and_replace(value: object) -> object:
        nonlocal replacements
        if isinstance(value, str):
            original = value
            modified = value

            # Literal replacements
            for overreach, replacement in GRANDIOSITY_MAP.items():
                if overreach in modified.lower():
                    # Replace first occurrence with annotation
                    idx = modified.lower().find(overreach)
                    if idx >= 0:
                        actual = modified[idx : idx + len(overreach)]
                        issues.append(
                            GrandiosityIssue(
                                type=_classify_issue(overreach),
                                severity="medium",
                                matched=actual,
                                replacement=replacement,
                            )
                        )
                        modified = modified[:idx] + replacement + modified[idx + len(overreach) :]
                        replacements += 1

            # Regex pattern detection (no auto-replacement — needs context)
            for pattern in _GRANDIOSITY_PATTERNS:
                for match in pattern.finditer(modified):
                    issues.append(
                        GrandiosityIssue(
                            type="overreach",
                            severity="low",
                            matched=match.group(0),
                            replacement=_suggest_replacement(match.group(0)),
                        )
                    )

            # Scan nested values
            if modified != original and len(modified) > 0:
                return modified
            return value
        elif isinstance(value, list):
            return [_scan_and_replace(v) for v in value]
        elif isinstance(value, dict):
            return {k: _scan_and_replace(v) for k, v in value.items()}
        return value

    # Apply to top-level dict values
    for key, value in list(result.items()):
        if key.startswith("_"):
            continue  # skip internal/metadata fields
        result[key] = _scan_and_replace(value)

    # Attach filter annotation
    result["_grandiosity_filter"] = {
        "version": "0.1.0",
        "ok": len(issues) == 0,
        "issues": [
            {
                "type": i.type,
                "severity": i.severity,
                "matched": i.matched[:80],
                "replacement": i.replacement,
            }
            for i in issues
        ],
        "replacements": replacements,
        "advisory_only": True,
        "policy": "F4 CLARITY + F7 HUMILITY — downgrade overconfident language, never block",
    }

    return result


def _classify_issue(matched: str) -> str:
    """Classify the type of grandiose language."""
    m = matched.lower()
    if any(w in m for w in ("physics", "mathematical", "universal", "absolute")):
        return "overreach"
    if "entropy" in m:
        return "entropy_as_agent"
    if "gödel" in m:
        return "godel_misuse"
    if any(
        w in m
        for w in (
            "perfect",
            "flawless",
            "guaranteed",
            "foolproof",
            "infallible",
            "zero risk",
            "zero chance",
        )
    ):
        return "absolutism"
    return "overreach"


def _suggest_replacement(matched: str) -> str:
    """Suggest a grounded replacement for a regex-detected pattern."""
    m = matched.lower()
    if "physics" in m:
        return "recurring system constraint"
    if "mathematical" in m:
        return "structurally strong pattern"
    if "universal" in m:
        return "widely observed pattern"
    if "absolute" in m:
        return "strong"
    if "entropy" in m:
        return "drift increases without correction"
    if "gödel" in m:
        return "self-reference limitation"
    if "guaranteed" in m:
        return "highly likely to"
    return "consider softer framing"


def self_audit() -> dict:
    """Return invariants for forge witness protocol."""
    return {
        "module": "grandiosity_filter",
        "version": "0.1.0",
        "wired": True,
        "wire_path": "arifosmcp/runtime/kernel.py → dispatch_with_fail_closed() post-ontology-bridge",
        "pattern_count": len(GRANDIOSITY_MAP),
        "regex_count": len(_GRANDIOSITY_PATTERNS),
        "gated_tools": sorted(_FILTERED_TOOLS),
        "depends_on_llm": False,
        "depends_on_network": False,
        "floor_count_delta": 0,
        "design_intent": "detect and downgrade grandiose language; advisory only, never blocks",
        "session_of_birth": "2026-07-03-wisdom-compression",
        "blocks_output": False,
        "advisory_only": True,
    }
