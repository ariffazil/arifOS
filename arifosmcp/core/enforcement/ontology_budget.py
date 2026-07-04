# arifOS — Ontology Budget Gate v0.1 (pre-verdict enforcement)
# Forged 2026-07-03 | session: wisdom-compression
#
# Design constraints:
#   - No new floor. Enforces existing F4 CLARITY + F8 LAW + F13 SOVEREIGN.
#   - Advisory gate — flags DRAFT_ONLY, never blocks categorically.
#   - Invariant 11 enforcement: reuse existing architecture before creating new categories.
#   - Wired into judge pipeline (pre-verdict) + available for forge_evaluate.
#
# Motivation:
#   FORGE overproduces ontology. Every new category, name, taxonomy must first
#   attempt to route through existing organs, floors, verdicts, memory classes.
#   If existing architecture can hold it → reuse. If not → DRAFT_ONLY.

"""
ontology_budget: gate against ontology inflation.

Checks whether a proposed new concept can be expressed using existing
federation architecture before allowing canonical status.

Gate logic:
  1. Can this be expressed using existing organs?
  2. Can this be expressed using existing floors?
  3. Can this be expressed using existing verdicts?
  4. Can this be expressed using existing memory classes?
  5. Can this be expressed using existing autonomy bands / MCP primitives?

→ ALL YES: REUSE_EXISTING (do not create new category)
→ ANY NO:  DRAFT_ONLY (not canonical; requires F13 ratification to promote)
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re as _re

# ── Existing architecture reference (canonical surface) ─────────────────
_EXISTING_ORGANS: frozenset[str] = frozenset(
    {
        "arifos",
        "aforge",
        "a-forge",
        "geox",
        "wealth",
        "well",
        "aaa",
        "vault999",
        "reality",
        "governance",
        "memory",
        "meaning",
        "execution",
        "civilization",
        "witness",
    }
)
_EXISTING_FLOORS: frozenset[str] = frozenset(
    {
        "f1",
        "f2",
        "f3",
        "f4",
        "f5",
        "f6",
        "f7",
        "f8",
        "f9",
        "f10",
        "f11",
        "f12",
        "f13",
        "amanah",
        "truth",
        "witness",
        "clarity",
        "peace",
        "maruah",
        "empathy",
        "humility",
        "genius",
        "antihantu",
        "ontology",
        "auth",
        "resilience",
        "sovereign",
    }
)
_EXISTING_VERDICTS: frozenset[str] = frozenset(
    {
        "seal",
        "hold",
        "sabar",
        "void",
        "draft_only",
        "review",
        "proceed",
        "block",
        "escalate",
        "report",
        "lower_confidence",
    }
)
_EXISTING_MEMORY_CLASSES: frozenset[str] = frozenset(
    {
        "ksr",
        "vault",
        "ledger",
        "federation",
        "telemetry",
        "kernel_state",
        "vault999",
        "memory",
        "context",
        "session_state",
    }
)
_EXISTING_AUTONOMY_BANDS: frozenset[str] = frozenset(
    {
        "observe",
        "suggest",
        "simulate",
        "draft",
        "queue",
        "execute_reversible",
        "execute_high_impact",
        "irreversible",
        "t1",
        "t2",
        "t3",
    }
)
_EXISTING_MCP_PRIMITIVES: frozenset[str] = frozenset(
    {
        "tool",
        "resource",
        "prompt",
        "session",
        "lease",
        "receipt",
        "schema",
        "transport",
        "server",
    }
)


# ── Patterns for detecting new-category proposals ───────────────────────
# Triggers that suggest an agent is trying to mint new ontology
_NEW_CATEGORY_PATTERNS: tuple[_re.Pattern[str], ...] = (
    _re.compile(
        r"\bnew\s+(organ|floor|verdict|status|layer|category|taxonomy|concept|class|type|primitive)\b",
        _re.IGNORECASE,
    ),
    _re.compile(
        r"\b(introduce|create|mint|define|establish)\s+(a|new)\s+(organ|floor|verdict|category|taxonomy)\b",
        _re.IGNORECASE,
    ),
    _re.compile(
        r"\bwe\s+need\s+(a|an)\s+(new|additional|separate)\s+(organ|floor|layer|category|taxonomy|status)\b",
        _re.IGNORECASE,
    ),
    _re.compile(r"\bpropose\s+(a|an)\s+(new|additional)\s+(organ|floor|verdict)\b", _re.IGNORECASE),
)


# ── Output schema ───────────────────────────────────────────────────────
@dataclass
class OntologyBudgetIssue:
    check: str  # "organ" | "floor" | "verdict" | "memory" | "primitive"
    proposed: str  # what was proposed
    existing_match: str  # which existing structure could hold it
    verdict: str  # "REUSE" | "DRAFT_ONLY"


@dataclass
class OntologyBudgetVerdict:
    ok: bool  # True = all concepts map to existing architecture
    issues: list[OntologyBudgetIssue] = field(default_factory=list)
    reuse_count: int = 0
    draft_count: int = 0
    notes: str = ""


def check_ontology_budget(
    proposed_text: str,
    context: dict | None = None,
) -> OntologyBudgetVerdict:
    """Check if a proposed concept can be expressed using existing architecture.

    Scans proposed_text for new-category signals and checks against
    the 5-level reuse hierarchy (Invariant 11).

    Returns OntologyBudgetVerdict with per-concept routing.
    """
    if not proposed_text:
        return OntologyBudgetVerdict(ok=True, notes="empty proposal — no check needed")

    issues: list[OntologyBudgetIssue] = []
    reuse_count = 0
    draft_count = 0
    lower = proposed_text.lower()

    # Detect new-category proposals via regex
    for pattern in _NEW_CATEGORY_PATTERNS:
        for match in pattern.finditer(proposed_text):
            proposed = match.group(0)
            # Try to route to existing architecture
            route = _route_to_existing(proposed, context or {})
            if route:
                issues.append(
                    OntologyBudgetIssue(
                        check=route["level"],
                        proposed=proposed,
                        existing_match=route["match"],
                        verdict="REUSE",
                    )
                )
                reuse_count += 1
            else:
                issues.append(
                    OntologyBudgetIssue(
                        check="unknown",
                        proposed=proposed,
                        existing_match="none found",
                        verdict="DRAFT_ONLY",
                    )
                )
                draft_count += 1

    # Also check for standalone new-term introductions (not caught by regex)
    # by looking for capitalized new terms that aren't in existing sets
    standalone_terms = _re.findall(r'\b"([A-Z][a-zA-Z\s]+)"\b', proposed_text)
    for term in standalone_terms:
        if not _matches_existing(term.lower()):
            route = _route_to_existing(term, context or {})
            if not route:
                issues.append(
                    OntologyBudgetIssue(
                        check="term",
                        proposed=term,
                        existing_match="none found",
                        verdict="DRAFT_ONLY",
                    )
                )
                draft_count += 1

    return OntologyBudgetVerdict(
        ok=draft_count == 0,
        issues=issues,
        reuse_count=reuse_count,
        draft_count=draft_count,
        notes=f"v0.1 ontology budget: {reuse_count} reusable, {draft_count} DRAFT_ONLY",
    )


def _route_to_existing(proposed: str, context: dict) -> dict | None:
    """Try to route a proposed concept through the 5-level reuse hierarchy.

    Returns {"level": str, "match": str} if a match is found, else None.
    """
    lower = proposed.lower()

    # Level 1: Can an existing organ hold this?
    organ_keywords = {
        "reality": ["ground", "evidence", "observe", "sense", "fact", "signal", "data"],
        "governance": ["rule", "policy", "constrain", "limit", "bound", "permit", "allow"],
        "memory": ["remember", "record", "ledger", "store", "recall", "archive", "history"],
        "meaning": ["purpose", "goal", "intent", "direction", "why", "mission"],
        "execution": ["act", "build", "deploy", "run", "execute", "forge", "do"],
        "civilization": ["sync", "coordinate", "notify", "update", "social", "share"],
        "witness": ["verify", "check", "prove", "audit", "confirm", "attest", "witness"],
    }
    for organ, keywords in organ_keywords.items():
        if any(kw in lower for kw in keywords):
            return {"level": "organ", "match": organ}

    # Level 2: Can an existing floor handle this?
    for floor in _EXISTING_FLOORS:
        if floor in lower:
            return {"level": "floor", "match": floor}

    # Level 3: Can an existing verdict express this?
    for verdict in _EXISTING_VERDICTS:
        if verdict in lower:
            return {"level": "verdict", "match": verdict}

    # Level 4: Can an existing memory class hold this?
    for mem_class in _EXISTING_MEMORY_CLASSES:
        if mem_class in lower:
            return {"level": "memory", "match": mem_class}

    # Level 5: Can an existing MCP primitive express this?
    for primitive in _EXISTING_MCP_PRIMITIVES:
        if primitive in lower:
            return {"level": "primitive", "match": primitive}

    # Level 6: Autonomy band
    for band in _EXISTING_AUTONOMY_BANDS:
        if band in lower:
            return {"level": "autonomy_band", "match": band}

    return None


def _matches_existing(term: str) -> bool:
    """Check if a term matches any existing architectural element."""
    all_existing = (
        _EXISTING_ORGANS
        | _EXISTING_FLOORS
        | _EXISTING_VERDICTS
        | _EXISTING_MEMORY_CLASSES
        | _EXISTING_MCP_PRIMITIVES
        | _EXISTING_AUTONOMY_BANDS
    )
    return term in all_existing


def is_ontology_proposal(text: str) -> bool:
    """Quick check: does this text propose creating new architectural categories?"""
    if not text:
        return False
    for pattern in _NEW_CATEGORY_PATTERNS:
        if pattern.search(text):
            return True
    return False


def self_audit() -> dict:
    """Return invariants for forge witness protocol."""
    return {
        "module": "ontology_budget",
        "version": "0.1.0",
        "wired": True,
        "wire_path": "arifosmcp/tools/judge.py → arif_judge() pre-verdict + forge_evaluate",
        "pattern_count": len(_NEW_CATEGORY_PATTERNS),
        "existing_organs": sorted(_EXISTING_ORGANS),
        "existing_floors": sorted(_EXISTING_FLOORS),
        "existing_verdicts": sorted(_EXISTING_VERDICTS),
        "depends_on_llm": False,
        "depends_on_network": False,
        "floor_count_delta": 0,
        "design_intent": "gate against ontology inflation — reuse existing architecture first",
        "session_of_birth": "2026-07-03-wisdom-compression",
        "blocks_output": False,
        "advisory_only": True,
        "invariant": 11,
    }
