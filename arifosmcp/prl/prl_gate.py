"""
prl_gate.py — PRL Dual-Gate: Cold Geometric Law Enforcement
═══════════════════════════════════════════════════════════════

Intercepts queries before the reasoning pipeline and enforces sovereign
precedents via a Dual-Gate architecture:

  Gate 1: Payload-Filtered Cosine Search (τ ≥ 0.95)
    - Only matches precedents with the SAME blast_radius classification
    - L1 queries never see L3 precedents (autoimmune prevention)
    - Cosine similarity ≥ 0.95 required for precedent injection

  Gate 2: Ω₀ Contextual Ambiguity Failsafe
    - If precedent passes Gate 1 but EMD VALIDATE detects contextual
      ambiguity, the system defaults to F1 HOLD
    - "Precedent matched geometrically, but consequence context is ambiguous"

Output: A constraint block that is injected BEFORE arif_judge or agent
response, enforcing the precedent as a non-negotiable governing variable.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from .vault_vectorizer import (
    COLLECTION_NAME,
    BLAST_RADIUS_VALUES,
    DEFAULT_BLAST_RADIUS,
    PRL_TAU_THRESHOLD,
    PrecedentVectorizer,
)

logger = logging.getLogger(__name__)

# ── Gate Result Types ──────────────────────────────────────────────────────

GateVerdict = Literal[
    "PRL_MATCH",       # Precedent found and constraint injected
    "PRL_NONE",        # No matching precedent — proceed normally
    "PRL_OMEGA0_HOLD", # Ω₀ exception — geometric match but contextual ambiguity
    "PRL_ERROR",       # Infrastructure failure — Qdrant unreachable, etc.
]


@dataclass
class PrlConstraint:
    """A binding precedent constraint injected before reasoning.

    The agent does NOT choose to follow this.  It is structurally injected
    as a non-negotiable governing variable.
    """

    seal_id: str
    blast_radius: str
    timestamp: str
    verdict: str
    constraint_text: str
    cosine_score: float = 0.0
    source_line: int = 0

    def to_prompt_block(self) -> str:
        """Render as a F9-compliant constraint block for the agent prompt.

        F9 (ANTI-HANTU): The agent must NOT act as if it "remembers."
        This is a structural constraint, not a memory.
        """
        return (
            f"[PRL CONSTRAINT — τ={self.cosine_score:.4f}]\n"
            f"BLAST RADIUS: {self.blast_radius}\n"
            f"PRECEDENT: {self.seal_id} (sealed {self.timestamp})\n"
            f"GOVERNING RULE: {self.constraint_text}\n"
            f"[/PRL CONSTRAINT]\n"
        )


@dataclass
class PrlGateResult:
    """Complete PRL gate output.

    verdict: What the gate decided
    constraints: Precedents that bind the current operation
    omega0_triggered: Whether Ω₀ failsafe fired
    query_blast_radius: The classified blast radius for this query
    """

    verdict: GateVerdict = "PRL_NONE"
    constraints: list[PrlConstraint] = field(default_factory=list)
    omega0_triggered: bool = False
    omega0_reason: str = ""
    query_blast_radius: str = DEFAULT_BLAST_RADIUS
    match_count: int = 0
    search_ms: float = 0.0
    error: str = ""


# ── Blast Radius Classifier ────────────────────────────────────────────────

_BLAST_RADIUS_HEURISTICS: dict[str, list[str]] = {
    "L3_CRITICAL": [
        "drop", "delete", "destroy", "rm -rf", "purge", "truncate",
        "DROP TABLE", "force push", "irreversible",
        "secret rotation", "vault cleanup", "chain cleanup",
        "production database", "production db",  # DESTRUCTIVE + production = L3
    ],
    "L2_SYSTEM": [
        "config", "deploy", "restart", "migrate", "refactor",
        "multi-agent", "systemd", "Caddy", "nginx", "database",
        "schema", "alter", "mcp server", "provider", "gateway",
    ],
}


def classify_blast_radius(query_text: str) -> str:
    """Heuristic blast radius classification for the current query.

    This is a FAST pre-classification — the sovereign can override at seal time.
    NOT derived from embeddings.  Pattern-matched against known consequence keywords.

    Used by the EMD Stack before querying PRL, so the payload filter is
    computed BEFORE the vector search.
    """
    query_lower = query_text.lower()

    # L3 check first (most dangerous)
    for keyword in _BLAST_RADIUS_HEURISTICS["L3_CRITICAL"]:
        if keyword.lower() in query_lower:
            return "L3_CRITICAL"

    # L2 check
    for keyword in _BLAST_RADIUS_HEURISTICS["L2_SYSTEM"]:
        if keyword.lower() in query_lower:
            return "L2_SYSTEM"

    return "L1_LOCAL"


# ── Ω₀ Ambiguity Detector ─────────────────────────────────────────────────

_OMEGA0_AMBIGUITY_SIGNALS = [
    "but also", "however", "unless", "except", "depending on",
    "maybe", "perhaps", "could be", "might be", "not sure",
    "ambiguous", "unclear", "it depends", "conditional",
]


def _detect_omega0_ambiguity(query_text: str, constraint_text: str) -> tuple[bool, str]:
    """Check if contextual ambiguity warrants Ω₀ HOLD despite geometric match.

    Returns (triggered, reason).
    """
    query_lower = query_text.lower()
    constraint_lower = constraint_text.lower()

    # Signal 1: Query contains ambiguity markers
    ambiguity_in_query = [s for s in _OMEGA0_AMBIGUITY_SIGNALS if s in query_lower]

    # Signal 2: Constraint text is significantly shorter (possibly incomplete)
    if len(constraint_text) < 20 and len(query_text) > 100:
        return True, "Constraint text too short for query complexity — possible incomplete match"

    # Signal 3: Query and constraint share action verbs but different objects
    # (Heuristic: both contain "delete" but different noun phrases)
    action_verbs = {"delete", "remove", "drop", "create", "modify", "change"}
    query_words = set(query_lower.split())
    constraint_words = set(constraint_lower.split())
    shared_verbs = action_verbs & query_words & constraint_words
    if shared_verbs and ambiguity_in_query:
        return (
            True,
            f"Action verb '{next(iter(shared_verbs))}' shared but query has ambiguity: "
            f"{ambiguity_in_query[0]}",
        )

    return False, ""


# ── PRL Gate — Public API ──────────────────────────────────────────────────

class PrlGate:
    """Dual-Gate precedent enforcement for arifOS reasoning pipeline.

    Usage::

        gate = PrlGate()
        result = await gate.interrogate(query_text="deploy migration to prod")
        if result.verdict == "PRL_MATCH":
            # Inject result.constraints into agent prompt BEFORE reasoning
            pass
        elif result.verdict == "PRL_OMEGA0_HOLD":
            # Hold for sovereign review
            pass
    """

    def __init__(self, qdrant_url: str = "http://localhost:6333") -> None:
        self.vectorizer = PrecedentVectorizer(qdrant_url=qdrant_url)

    async def interrogate(
        self,
        query_text: str,
        blast_radius: str | None = None,
        tau_threshold: float = PRL_TAU_THRESHOLD,
        limit: int = 3,
        enable_omega0: bool = True,
    ) -> PrlGateResult:
        """Run the Dual-Gate precedent check.

        Args:
            query_text: The natural language query / intent to match
            blast_radius: Override auto-classified blast radius.
                          If None, classify_blast_radius(query_text) is used.
            tau_threshold: Minimum cosine similarity (default 0.95)
            limit: Maximum precedents to return
            enable_omega0: Whether to run Ω₀ ambiguity detection

        Returns PrlGateResult with verdict and any binding constraints.
        """
        t0 = datetime.now(timezone.utc)
        result = PrlGateResult()

        # Step 1: Classify blast radius for this query
        if blast_radius and blast_radius in BLAST_RADIUS_VALUES:
            result.query_blast_radius = blast_radius
        else:
            result.query_blast_radius = classify_blast_radius(query_text)

        # Step 2: Payload-filtered vector search
        try:
            matches = self.vectorizer.search(
                query_text=query_text,
                blast_radius=result.query_blast_radius,
                score_threshold=tau_threshold,
                limit=limit,
            )
        except Exception as exc:
            logger.error("PRL search failed: %s", exc)
            result.verdict = "PRL_ERROR"
            result.error = str(exc)[:200]
            result.search_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
            return result

        result.match_count = len(matches)

        if not matches:
            result.verdict = "PRL_NONE"
            result.search_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
            return result

        # Step 3: Convert matches to constraints
        for match in matches:
            constraint = PrlConstraint(
                seal_id=match.get("seal_id", ""),
                blast_radius=match.get("blast_radius", ""),
                timestamp=match.get("timestamp", ""),
                verdict=match.get("verdict", "SEAL"),
                constraint_text=match.get("payload_summary", ""),
                cosine_score=match.get("score", 0.0),
                source_line=match.get("vault_line", 0),
            )

            # Step 4: Ω₀ ambiguity check (per-constraint)
            if enable_omega0:
                triggered, reason = _detect_omega0_ambiguity(
                    query_text, constraint.constraint_text
                )
                if triggered:
                    result.omega0_triggered = True
                    result.omega0_reason = reason
                    # Don't add the constraint — Ω₀ overrides
                    continue

            result.constraints.append(constraint)

        # Step 5: Final verdict
        if result.omega0_triggered and not result.constraints:
            result.verdict = "PRL_OMEGA0_HOLD"
        elif result.constraints:
            result.verdict = "PRL_MATCH"
        else:
            result.verdict = "PRL_NONE"

        result.search_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return result

    def interrogate_sync(
        self,
        query_text: str,
        blast_radius: str | None = None,
        tau_threshold: float = PRL_TAU_THRESHOLD,
        limit: int = 3,
        enable_omega0: bool = True,
    ) -> PrlGateResult:
        """Synchronous wrapper for interrogate().

        Use when the caller cannot await (e.g., non-async tool handlers).
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # Already in an async context — delegate to the event loop
            # This is safe because interrogate is IO-bound (Qdrant call)
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    lambda: asyncio.run(
                        self.interrogate(
                            query_text=query_text,
                            blast_radius=blast_radius,
                            tau_threshold=tau_threshold,
                            limit=limit,
                            enable_omega0=enable_omega0,
                        )
                    )
                )
                return future.result()
        else:
            return asyncio.run(
                self.interrogate(
                    query_text=query_text,
                    blast_radius=blast_radius,
                    tau_threshold=tau_threshold,
                    limit=limit,
                    enable_omega0=enable_omega0,
                )
            )

    # ── Utility ─────────────────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Quick health probe — is the gate operational?"""
        try:
            stats = self.vectorizer.collection_stats()
            return {
                "status": "OK",
                "collection": stats.get("collection", ""),
                "point_count": stats.get("point_count", 0),
                "tau_threshold": PRL_TAU_THRESHOLD,
            }
        except Exception as exc:
            return {"status": "DOWN", "error": str(exc)[:200]}
