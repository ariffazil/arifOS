"""
arifosmcp/runtime/evidence_gate.py — Evidence Gate v2 (fail-closed)
═══════════════════════════════════════════════════════════════════

Three-gate verification for all LLM output in arifOS.
Wired into _make_envelope() — one edit, all LLM calls gated.

Gate 1: Atomic Decomposition (sync, always runs)
  - Splits text into sentence-level atomic claims
  - Classifies each claim's evidence level
  - Computes material-claim coverage ratio

Gate 2: Evidence Coverage (sync, when context available)
  - Semantic similarity via Ollama nomic-embed-text (local, 768d)
  - Threshold-based verdict: PROCEED / WARN / HOLD / INSUFFICIENT_EVIDENCE

Gate 3: SelfCheck Re-sample (async, high-stakes calls only)
  - Re-samples same prompt via _call_tokenrouter
  - Compares claims across samples
  - Tags inconsistent claims as [UNVERIFIED]

DESIGN:
  - Gate 1 is sync, runs in _make_envelope (all calls)
  - Gate 2 is sync, runs when prompt context is passed
  - Gate 3 is async, runs in call_llm for 333_REASON/888_JUDGE
  - FAIL-CLOSED: gate failure → HOLD envelope, not pass-through
  - F1 REVERSIBLE: deleting this file reverts to prior behavior

FIXES (v2, 2026-08-26):
  - Defect 1: Semantic similarity via Ollama embeddings (not keyword overlap)
  - Defect 2: Source verification levels (URL_MENTION → SOURCE_OPENED → CONTENT_MATCH)
  - Defect 3: Material-claim ratio (not single-claim upgrade)
  - Defect 4: Sentence-level atomic decomposition (not line-split)
  - Defect 5: Verdict field (PROCEED/WARN/HOLD/INSUFFICIENT_EVIDENCE)
  - Defect 6: Fail-closed exception handling
  - Defect 7: Recalculate human_decision_required after gate
  - Defect 8: Gate 3 async re-sampling wired

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIMS = 768

# Thresholds (tunable, all ≤ 1.0)
SEMANTIC_SIMILARITY_THRESHOLD = 0.55  # claim-evidence cosine similarity
COVERAGE_THRESHOLD_PROCEED = 0.70     # ≥70% material claims supported → PROCEED
COVERAGE_THRESHOLD_WARN = 0.40        # ≥40% → WARN, <40% → HOLD
COVERAGE_THRESHOLD_INSUFFICIENT = 0.20 # <20% → INSUFFICIENT_EVIDENCE

HIGH_STAKES_ORIGINS = {"333_REASON", "888_JUDGE", "666_HEART"}

# ── Patterns ─────────────────────────────────────────────────────────────────

# Sentence boundary: period/question/exclamation followed by space or end
SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')

# Clause boundary: semicolons, em-dash, coordinations ("X, and Y", "X, but Y")
CLAUSE_SPLIT = re.compile(r'(?:;\s+|\s+—\s+|,\s*(?:and|but|or|yet)\s+)')

# Claim verbs: sentences that assert something factual
CLAIM_VERBS = re.compile(
    r'\b(?:is|are|was|were|has|have|had|does|did|will|would|can|could|'
    r'should|must|requires|produces|contains|shows|demonstrates|'
    r'indicates|suggests|confirms|proves|reveals|exhibits|'
    r'implements|supports|enables|prevents|blocks|creates|'
    r'increases|decreases|improves|reduces|affects|causes|'
    r'announces|announced|announce|report|reports|reported|states|stated|'
    r'declares|declared|lost|lose|loses|charging|charges|charged|'
    r'gained|gains|reached|reaches|increased|decreased)\b',
    re.IGNORECASE,
)

# Citation patterns
URL_PATTERN = re.compile(r'https?://\S+|arXiv:\d+\.\d+|doi:\S+|DOI:\S+')
CITATION_PATTERN = re.compile(
    r'\b(?:according to|per|as reported|source:|cited|reference|'
    r'based on|from|published|found in|documented)\b',
    re.IGNORECASE,
)
TOOL_OUTPUT_PATTERN = re.compile(r'\b(?:tool output|probe result|curl|grep|log)\b', re.IGNORECASE)

# Questions and non-claims
QUESTION_PATTERN = re.compile(r'\?$|^\?|\b(?:what|how|why|when|where|who|which)\b.*\?', re.IGNORECASE)


# ── Enums ────────────────────────────────────────────────────────────────────

class EvidenceVerdict(StrEnum):
    """What the Evidence Gate decides."""
    PROCEED = "proceed"                    # ≥70% material claims supported
    WARN = "warn"                          # ≥40% but <70% supported
    HOLD = "hold"                          # <40% supported
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"  # <20% supported


class SourceRetrievalStatus(StrEnum):
    """Can a source be treated as retrieved content?"""

    FULL = "full"
    PARTIAL = "partial"
    ERROR = "error"


class ClaimVerification(StrEnum):
    """Entailment relationship between one claim and source content."""

    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"
    CONTRADICTED = "contradicted"
    UNKNOWN = "unknown"


class SourceVerification(StrEnum):
    """How well a source supports a claim."""
    URL_MENTION = "url_mention"            # URL present but not opened
    SOURCE_OPENED = "source_opened"        # Source was fetched
    SOURCE_CONTENT_MATCH = "content_match" # Source content supports claim
    INDEPENDENTLY_VERIFIED = "independently_verified"  # Multiple sources agree
    NONE = "none"                          # No source


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class AtomicClaim:
    """A single atomic factual claim with evidence metadata."""
    text: str
    evidence_level: Literal["claimed", "cited", "verified"] = "claimed"
    source_verification: SourceVerification = SourceVerification.NONE
    source_id: str | None = None
    source_type: str | None = None  # "search_snippet", "tool_output", "document", etc.
    has_url: bool = False
    has_citation: bool = False
    has_tool_output: bool = False
    confidence: float = 0.0
    semantic_similarity: float = 0.0  # cosine similarity to evidence
    is_material: bool = True  # False for boilerplate/meta claims


@dataclass
class DecompositionResult:
    """Result of Gate 1: atomic decomposition."""
    total_claims: int = 0
    material_claims: int = 0
    claims_verified: int = 0
    claims_cited: int = 0
    claims_claimed: int = 0
    atoms: list[AtomicClaim] = field(default_factory=list)
    upgraded_evidence_level: str = "claimed"


@dataclass
class CoverageResult:
    """Result of Gate 2: evidence coverage."""
    total_claims: int = 0
    covered_claims: int = 0
    uncovered_claims: int = 0
    coverage_ratio: float = 0.0
    uncovered_texts: list[str] = field(default_factory=list)
    semantic_similarities: list[float] = field(default_factory=list)


@dataclass
class SelfCheckResult:
    """Result of Gate 3: SelfCheck re-sample."""
    consistent_claims: int = 0
    inconsistent_claims: int = 0
    total_claims: int = 0
    consistency_ratio: float = 0.0
    inconsistent_texts: list[str] = field(default_factory=list)


@dataclass
class EvidenceGateResult:
    """Complete result from all three gates."""
    verdict: EvidenceVerdict = EvidenceVerdict.HOLD
    claims: list[AtomicClaim] = field(default_factory=list)
    material_claims: int = 0
    supported_claims: int = 0
    verified_claims: int = 0
    coverage_ratio: float = 0.0
    threshold: float = COVERAGE_THRESHOLD_PROCEED
    sources: list[dict[str, Any]] = field(default_factory=list)
    gate_failure: str | None = None
    human_decision_required: bool = True
    risk_flags: list[str] = field(default_factory=list)
    # Metadata for envelope
    upgraded_evidence_level: str = "claimed"
    enriched_parsed_output: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# GATE 1: ATOMIC DECOMPOSITION (sentence-level, not line-split)
# ═══════════════════════════════════════════════════════════════════════════════


def extract_claims_from_text(text: str) -> list[str]:
    """Extract factual claims from text using sentence + clause-level splitting.

    Fixes Defect 4: Uses sentence boundaries AND clause boundaries.
    A sentence with 3 claims ("X, Y, and Z") becomes 3 separate claims.
    """
    claims = []
    in_code_block = False

    # First: strip code blocks
    lines = text.split("\n")
    prose_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not stripped or len(stripped) < 15:
            continue
        if stripped.startswith(("#", "//", "<!--", "---", "***")):
            continue
        prose_lines.append(stripped)

    # Join prose and split by sentence boundaries
    prose = " ".join(prose_lines)
    sentences = SENTENCE_SPLIT.split(prose)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 15:
            continue
        # Skip questions
        if QUESTION_PATTERN.search(sentence) and sentence.endswith("?"):
            continue

        # Defect 4 fix: if sentence has multiple assertion verbs, split into clauses
        verbs_in_sentence = len(CLAIM_VERBS.findall(sentence))
        if verbs_in_sentence >= 3:
            # Multi-claim sentence — split on clause boundaries
            clauses = CLAUSE_SPLIT.split(sentence)
            for clause in clauses:
                clause = clause.strip().rstrip(",.")
                if len(clause) >= 15 and CLAIM_VERBS.search(clause):
                    claims.append(clause)
        elif CLAIM_VERBS.search(sentence):
            # Single-claim sentence
            claims.append(sentence)

    return claims


def classify_claim_evidence(claim: str) -> AtomicClaim:
    """Classify a single claim's evidence level.

    Fixes Defect 2: Distinguishes URL_MENTION from SOURCE_OPENED.
    The "verified" level now requires SOURCE_CONTENT_MATCH or better.
    URL + citation language alone = "cited", not "verified".
    """
    has_url = bool(URL_PATTERN.search(claim))
    has_citation = bool(CITATION_PATTERN.search(claim))
    has_tool_output = bool(TOOL_OUTPUT_PATTERN.search(claim))

    # Defect 2 fix: URL + citation = "cited", not "verified"
    # "verified" requires SOURCE_CONTENT_MATCH (checked in Gate 2)
    if has_tool_output:
        level = "cited"
        source_ver = SourceVerification.SOURCE_OPENED
    elif has_url and has_citation:
        level = "cited"
        source_ver = SourceVerification.URL_MENTION
    elif has_url or has_citation:
        level = "cited"
        source_ver = SourceVerification.URL_MENTION
    else:
        level = "claimed"
        source_ver = SourceVerification.NONE

    return AtomicClaim(
        text=claim,
        evidence_level=level,
        source_verification=source_ver,
        has_url=has_url,
        has_citation=has_citation,
        has_tool_output=has_tool_output,
    )


def decompose(text: str) -> DecompositionResult:
    """Gate 1: Decompose text into atomic claims and classify each."""
    claims = extract_claims_from_text(text)
    if not claims:
        return DecompositionResult()

    # Deduplicate (normalized)
    seen = set()
    unique_claims = []
    for c in claims:
        normalized = re.sub(r"\s+", " ", c.lower().strip())
        if normalized not in seen:
            seen.add(normalized)
            unique_claims.append(c)

    # Classify each claim
    atoms = [classify_claim_evidence(c) for c in unique_claims]

    # Count by level (Defect 3 fix: material-claim ratio, not single-claim upgrade)
    verified = sum(1 for a in atoms if a.evidence_level == "verified")
    cited = sum(1 for a in atoms if a.evidence_level == "cited")
    claimed = sum(1 for a in atoms if a.evidence_level == "claimed")
    material = sum(1 for a in atoms if a.is_material)

    # Defect 3 fix: upgraded level is based on material-claim ratio
    # NOT "if ANY claim is verified → envelope is verified"
    if material > 0:
        verified_ratio = verified / material
        cited_ratio = (verified + cited) / material
        if verified_ratio >= 0.5:
            upgraded = "verified"
        elif cited_ratio >= 0.5:
            upgraded = "cited"
        else:
            upgraded = "claimed"
    else:
        upgraded = "claimed"

    return DecompositionResult(
        total_claims=len(atoms),
        material_claims=material,
        claims_verified=verified,
        claims_cited=cited,
        claims_claimed=claimed,
        atoms=atoms,
        upgraded_evidence_level=upgraded,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLAIM / SOURCE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════


def _normalise_source_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _source_contains_claim(source_text: str, claim_text: str) -> bool:
    """Conservative exact-span support check for the first verifier layer.

    This is deliberately not a semantic fact checker. It returns true only
    when a material predicate or quantity from the claim appears in the
    source passage. A semantic embedding may still be used as a separate
    coverage signal.
    """

    source = _normalise_source_text(source_text).casefold()
    claim = _normalise_source_text(claim_text).casefold()
    if not source or not claim:
        return False

    material_tokens = [
        token
        for token in re.findall(r"[a-z0-9][a-z0-9%._-]{2,}", claim)
        if token not in {
            "the", "this", "that", "with", "from", "have", "has", "had",
            "and", "but", "for", "are", "was", "were", "will", "would",
        }
    ]
    if not material_tokens:
        return False

    # Numeric claims are checked with a tolerant numeric token, while the
    # remaining tokens still need to be present. This avoids treating a topic
    # match ("Reddit API changes") as support for "Reddit lost 40%".
    matched = 0
    for token in material_tokens:
        token = token.strip(".,")
        if token in source:
            matched += 1
            continue
        if token.endswith("%"):
            try:
                numeric = float(token[:-1])
                if f"{numeric:g}" in source:
                    matched += 1
            except ValueError:
                pass
    return matched / len(material_tokens) >= 0.8


def verify_claim(
    claim: str,
    source: dict[str, Any],
) -> dict[str, Any]:
    """Verify one claim against one source card.

    This function is intentionally conservative and deterministic. A source
    card must be full, have a URL, a SHA-256 content hash, a timestamp, a
    provider, and an exact passage. Full content is checked for direct
    predicate/quantity overlap; it does not establish external truth by
    itself.
    """

    required = (
        "status",
        "url",
        "content_hash_sha256",
        "retrieved_at",
        "provider",
        "exact_passage",
    )
    independent = source.get("independent_witness")
    abstention = source.get("documented_abstention")
    if not isinstance(independent, bool) and not abstention:
        return {
            "verdict": ClaimVerification.UNKNOWN.value,
            "claim": claim,
            "source_id": source.get("source_id"),
            "reason": "missing_independent_witness_or_documented_abstention",
            "source_status": source.get("status"),
        }
    missing = [key for key in required if not source.get(key)]
    if missing:
        return {
            "verdict": ClaimVerification.UNKNOWN.value,
            "claim": claim,
            "source_id": source.get("source_id"),
            "reason": f"missing_source_fields:{','.join(missing)}",
            "source_status": source.get("status"),
        }

    try:
        status = SourceRetrievalStatus(str(source["status"]).lower())
    except ValueError:
        return {
            "verdict": ClaimVerification.UNKNOWN.value,
            "claim": claim,
            "source_id": source.get("source_id"),
            "reason": "invalid_source_status",
            "source_status": source.get("status"),
        }

    if status is SourceRetrievalStatus.ERROR:
        return {
            "verdict": ClaimVerification.UNKNOWN.value,
            "claim": claim,
            "source_id": source.get("source_id"),
            "reason": "source_error",
            "source_status": status.value,
        }

    if status is SourceRetrievalStatus.PARTIAL:
        return {
            "verdict": ClaimVerification.UNKNOWN.value,
            "claim": claim,
            "source_id": source.get("source_id"),
            "reason": "partial_source_not_admissible",
            "source_status": status.value,
        }

    content_hash = str(source["content_hash_sha256"])
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", content_hash):
        return {
            "verdict": ClaimVerification.UNKNOWN.value,
            "claim": claim,
            "source_id": source.get("source_id"),
            "reason": "invalid_content_hash",
            "source_status": status.value,
        }

    try:
        datetime.fromisoformat(str(source["retrieved_at"]).replace("Z", "+00:00"))
    except ValueError:
        return {
            "verdict": ClaimVerification.UNKNOWN.value,
            "claim": claim,
            "source_id": source.get("source_id"),
            "reason": "invalid_retrieved_at",
            "source_status": status.value,
        }

    passage = str(source["exact_passage"])
    if _source_contains_claim(passage, claim):
        result = ClaimVerification.SUPPORTED.value
    elif any(
        marker in passage.casefold()
        for marker in (
            "remained stable",
            "no increase",
            "did not increase",
            "did not gain",
            "did not lose",
            "no loss",
            "declined",
        )
    ) and any(
        marker in claim.casefold()
        for marker in ("gained ", "lost ", "increased ", "reduced ")
    ):
        result = ClaimVerification.CONTRADICTED.value
    else:
        result = ClaimVerification.UNSUPPORTED.value

    return {
        "verdict": result,
        "claim": claim,
        "source_id": source.get("source_id"),
        "source_status": status.value,
        "provider": source.get("provider"),
        "content_hash_sha256": content_hash,
        "reason": (
            "direct_span_check"
            if result == ClaimVerification.SUPPORTED.value
            else "explicit_contradiction"
            if result == ClaimVerification.CONTRADICTED.value
            else "claim_not_entailed_by_exact_passage"
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GATE 2: EVIDENCE COVERAGE (semantic similarity via Ollama)
# ═══════════════════════════════════════════════════════════════════════════════


def _get_embedding(text: str) -> list[float] | None:
    """Get embedding from Ollama nomic-embed-text. Returns None on failure."""
    try:
        resp = httpx.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json().get("embedding")
    except Exception as e:
        logger.warning(f"Ollama embedding failed: {e}")
        return None


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def check_evidence_coverage(
    claims: list[str],
    evidence_set: list[str],
    threshold: float = SEMANTIC_SIMILARITY_THRESHOLD,
) -> CoverageResult:
    """Check if evidence set semantically supports the claims.

    Fixes Defect 1: Uses Ollama embeddings for semantic similarity,
    not keyword overlap. A claim about "Reddit blocking" is semantically
    different from evidence about "Reddit blocking" even if keywords match.

    Falls back to keyword overlap if Ollama is unavailable.
    """
    if not claims or not evidence_set:
        return CoverageResult()

    # Try semantic similarity first
    evidence_embeddings = []
    use_semantic = True

    for ev in evidence_set:
        emb = _get_embedding(ev[:500])  # Truncate for embedding
        if emb is None:
            use_semantic = False
            break
        evidence_embeddings.append(emb)

    if not use_semantic:
        # Fallback: keyword overlap (Defect 1 partial fix — better than nothing)
        logger.warning("Ollama unavailable — falling back to keyword overlap")
        return _check_keyword_overlap(claims, evidence_set, threshold=0.3)

    # Semantic similarity path
    covered = 0
    uncovered = []
    similarities = []

    for claim in claims:
        claim_emb = _get_embedding(claim[:500])
        if claim_emb is None:
            # Can't embed claim — treat as uncovered
            uncovered.append(claim)
            similarities.append(0.0)
            continue

        # Best similarity across all evidence items
        best_sim = max(
            _cosine_similarity(claim_emb, ev_emb)
            for ev_emb in evidence_embeddings
        )
        similarities.append(best_sim)

        if best_sim >= threshold:
            covered += 1
        else:
            uncovered.append(claim)

    total = len(claims)
    return CoverageResult(
        total_claims=total,
        covered_claims=covered,
        uncovered_claims=len(uncovered),
        coverage_ratio=round(covered / max(total, 1), 3),
        uncovered_texts=uncovered,
        semantic_similarities=similarities,
    )


def _check_keyword_overlap(
    claims: list[str],
    evidence_set: list[str],
    threshold: float = 0.3,
) -> CoverageResult:
    """Fallback: keyword overlap when Ollama is unavailable."""
    context_words = set()
    for ev in evidence_set:
        context_words.update(re.findall(r"\b\w{4,}\b", ev.lower()))

    covered = 0
    uncovered = []
    for claim in claims:
        claim_words = set(re.findall(r"\b\w{4,}\b", claim.lower()))
        if not claim_words:
            continue
        overlap = len(claim_words & context_words) / len(claim_words)
        if overlap >= threshold:
            covered += 1
        else:
            uncovered.append(claim)

    total = len(claims)
    return CoverageResult(
        total_claims=total,
        covered_claims=covered,
        uncovered_claims=len(uncovered),
        coverage_ratio=round(covered / max(total, 1), 3),
        uncovered_texts=uncovered,
    )


def verify_claims(
    claims: list[str],
    source_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Verify decomposed material claims against source cards.

    A claim is counted as supported only when at least one full source card
    directly contains the claim's material predicates/quantities. A source
    error, partial source, or missing provenance returns UNKNOWN. A source
    passage that does not entail the claim returns UNSUPPORTED.
    """

    records: list[dict[str, Any]] = []
    if not claims:
        return {
            "verdict": "UNKNOWN",
            "verified": 0,
            "total": 0,
            "coverage_ratio": 0.0,
            "records": records,
        }

    for claim in claims:
        candidates = []
        for source in source_cards:
            source_id = str(source.get("source_id", ""))
            result = verify_claim(claim, source)
            candidates.append(
                {
                    "claim": claim,
                    "source_id": result.get("source_id") or source_id,
                    "verdict": result.get("verdict", "unknown"),
                    "reason": result.get("reason", "unknown"),
                    "source_status": result.get("source_status"),
                }
            )
        supported = any(
            item["verdict"] == ClaimVerification.SUPPORTED.value for item in candidates
        )
        contradicted = any(
            item["verdict"] == ClaimVerification.CONTRADICTED.value for item in candidates
        )
        unknown = all(
            item["verdict"] == ClaimVerification.UNKNOWN.value for item in candidates
        ) if candidates else True
        if contradicted:
            verdict = ClaimVerification.CONTRADICTED
        elif supported:
            verdict = ClaimVerification.SUPPORTED
        elif unknown:
            verdict = ClaimVerification.UNKNOWN
        else:
            verdict = ClaimVerification.UNSUPPORTED
        records.append(
            {
                "claim": claim,
                "verdict": verdict.value,
                "candidate_results": candidates,
            }
        )

    verified = sum(
        record["verdict"] == ClaimVerification.SUPPORTED.value for record in records
    )
    contradicted = sum(
        record["verdict"] == ClaimVerification.CONTRADICTED.value for record in records
    )
    unknown = sum(
        record["verdict"] == ClaimVerification.UNKNOWN.value for record in records
    )
    return {
        "verdict": (
            "SUPPORTED"
            if verified == len(records)
            else "CONTRADICTED"
            if contradicted
            else "UNKNOWN"
            if unknown
            else "PARTIALLY_SUPPORTED"
        ),
        "verified": verified,
        "total": len(records),
        "contradicted": contradicted,
        "unknown": unknown,
        "coverage_ratio": round(verified / len(records), 3),
        "records": records,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GATE 3: SELFCHECK RE-SAMPLE (async hook)
# ═══════════════════════════════════════════════════════════════════════════════


def should_selfcheck(tool_origin: str, mode: str) -> bool:
    """Determine if SelfCheck re-sample should run.

    Only for high-stakes calls: 333_REASON, 888_JUDGE, etc.
    """
    return tool_origin in HIGH_STAKES_ORIGINS


async def selfcheck_resample(
    original_query: str,
    primary_output: str,
    llm_call_fn,  # async callable: (query, temperature) -> str
    n_samples: int = 2,
    temperature: float = 0.3,
) -> SelfCheckResult:
    """Gate 3: Re-sample and compare claims across samples.

    Fixes Defect 8: Actually calls the LLM for re-sampling.
    """
    import asyncio

    # Extract claims from primary output
    primary_claims = extract_claims_from_text(primary_output)
    if not primary_claims:
        return SelfCheckResult()

    # Re-sample N times in parallel
    samples = []
    try:
        tasks = [llm_call_fn(original_query, temperature) for _ in range(n_samples)]
        samples = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out exceptions
        samples = [s for s in samples if isinstance(s, str)]
    except Exception as e:
        logger.warning(f"SelfCheck re-sample failed: {e}")
        return SelfCheckResult()

    if not samples:
        return SelfCheckResult()

    # Extract claims from each sample
    sample_claims_list = [extract_claims_from_text(s) for s in samples]

    # For each primary claim, check if it appears in any sample
    consistent = 0
    inconsistent = []
    for claim in primary_claims:
        claim_lower = claim.lower()
        # Check if any sample contains a semantically similar claim
        found_in_samples = 0
        for sample_claims in sample_claims_list:
            for sc in sample_claims:
                # Simple word overlap for speed (semantic would be better but slower)
                claim_words = set(re.findall(r"\b\w{4,}\b", claim_lower))
                sc_words = set(re.findall(r"\b\w{4,}\b", sc.lower()))
                if claim_words and sc_words:
                    overlap = len(claim_words & sc_words) / len(claim_words)
                    if overlap >= 0.5:
                        found_in_samples += 1
                        break

        if found_in_samples >= len(samples) * 0.5:
            consistent += 1
        else:
            inconsistent.append(claim)

    total = len(primary_claims)
    return SelfCheckResult(
        consistent_claims=consistent,
        inconsistent_claims=len(inconsistent),
        total_claims=total,
        consistency_ratio=round(consistent / max(total, 1), 3),
        inconsistent_texts=inconsistent,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GATE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════


def gate_envelope(
    raw_output: str,
    parsed_output: dict[str, Any],
    evidence_level: str,
    prompt: str = "",
    tool_origin: str = "",
    evidence_set: list[str] | None = None,
    source_cards: list[dict[str, Any]] | None = None,
) -> EvidenceGateResult:
    """Run Gate 1 + Gate 2 and return complete result.

    Fixes Defect 5: Returns EvidenceGateResult with verdict field.
    Fixes Defect 6: Fail-closed — exception returns HOLD.
    Fixes Defect 7: Computes human_decision_required AFTER gates run.
    """
    try:
        # Gate 1: Atomic decomposition
        decomp = decompose(raw_output)

        # Gate 2: Evidence coverage (when evidence available)
        coverage = None
        claim_texts = [a.text for a in decomp.atoms]

        verdict: EvidenceVerdict = EvidenceVerdict.HOLD
        if evidence_set:
            coverage = check_evidence_coverage(claim_texts, evidence_set)
        elif prompt:
            # Use prompt as proxy evidence (better than nothing)
            coverage = check_evidence_coverage(claim_texts, [prompt])

        # Claim-level source verification is orthogonal to semantic coverage.
        # If source cards are supplied, a material claim cannot be counted as
        # verified without a full source card and direct passage entailment.
        claim_verification = verify_claims(claim_texts, source_cards or [])
        if source_cards and claim_verification["total"]:
            if claim_verification["contradicted"]:
                claim_verified = 0
            elif claim_verification["unknown"] == claim_verification["total"]:
                claim_verified = 0
            else:
                claim_verified = claim_verification["verified"]
            claim_denominator = claim_verification["total"]
        else:
            claim_verified = 0
            claim_denominator = claim_verification["total"] if source_cards else 0

        # Compute material-claim coverage (Defect 3 fix)
        if coverage and decomp.material_claims > 0:
            coverage_ratio = coverage.coverage_ratio
        else:
            coverage_ratio = 0.0

        # A source card verification is a hard floor for material claims: no
        # semantic similarity can turn an unsupported claim into a verified one.
        if source_cards and decomp.material_claims > 0:
            if claim_verification["contradicted"]:
                verdict = EvidenceVerdict.INSUFFICIENT_EVIDENCE
            elif claim_verified / claim_denominator >= 0.70:
                coverage_ratio = min(coverage_ratio, claim_verified / claim_denominator)
            else:
                verdict = EvidenceVerdict.INSUFFICIENT_EVIDENCE
            claim_verified = 0
            claim_denominator = 0

        # Determine verdict (Defect 5 fix)
        if verdict == EvidenceVerdict.INSUFFICIENT_EVIDENCE:
            pass
        elif coverage_ratio >= COVERAGE_THRESHOLD_PROCEED:
            verdict = EvidenceVerdict.PROCEED
        elif coverage_ratio >= COVERAGE_THRESHOLD_WARN:
            verdict = EvidenceVerdict.WARN
        elif coverage_ratio >= COVERAGE_THRESHOLD_INSUFFICIENT:
            verdict = EvidenceVerdict.HOLD
        else:
            verdict = EvidenceVerdict.INSUFFICIENT_EVIDENCE

        # Compute upgraded evidence level (Defect 3 fix: material-claim ratio)
        upgraded = decomp.upgraded_evidence_level
        if verdict in (EvidenceVerdict.HOLD, EvidenceVerdict.INSUFFICIENT_EVIDENCE):
            # Downgrade to "claimed" if coverage is insufficient
            if upgraded == "verified":
                upgraded = "cited"
            if verdict == EvidenceVerdict.INSUFFICIENT_EVIDENCE:
                upgraded = "claimed"

        # Defect 7 fix: compute human_decision_required AFTER gates
        human_decision_required = (
            verdict in (EvidenceVerdict.HOLD, EvidenceVerdict.INSUFFICIENT_EVIDENCE)
            or upgraded == "claimed"
        )

        # Risk flags
        risk_flags = []
        if verdict == EvidenceVerdict.INSUFFICIENT_EVIDENCE:
            risk_flags.append(
                f"EVIDENCE_GATE: INSUFFICIENT_EVIDENCE — "
                f"{coverage.uncovered_claims if coverage else decomp.total_claims}"
                f"/{decomp.total_claims} claims unsupported. "
                f"Coverage: {coverage_ratio:.0%}. Synthesis blocked."
            )
        elif verdict == EvidenceVerdict.HOLD:
            risk_flags.append(
                f"EVIDENCE_GATE: HOLD — "
                f"{coverage.uncovered_claims if coverage else decomp.total_claims}"
                f"/{decomp.total_claims} claims unsupported. "
                f"Coverage: {coverage_ratio:.0%}. Human review required."
            )

        # Enrich parsed_output with gate metadata
        enriched = dict(parsed_output) if isinstance(parsed_output, dict) else {}
        enriched["_evidence_gate"] = {
            "verdict": verdict.value,
            "total_claims": decomp.total_claims,
            "material_claims": decomp.material_claims,
            "verified": decomp.claims_verified,
            "cited": decomp.claims_cited,
            "claimed": decomp.claims_claimed,
            "coverage_ratio": coverage_ratio,
            "upgraded_from": evidence_level,
            "upgraded_to": upgraded,
            "human_decision_required": human_decision_required,
            "gate_version": "2.0.0",
            "claim_verification": {
                "verdict": claim_verification.get("verdict", "UNKNOWN"),
                "verified": claim_verification.get("verified", 0),
                "total": claim_verification.get("total", 0),
                "contradicted": claim_verification.get("contradicted", 0),
                "unknown": claim_verification.get("unknown", 0),
                "coverage_ratio": claim_verification.get("coverage_ratio", 0.0),
                "records": claim_verification.get("records", []),
            },
        }

        return EvidenceGateResult(
            verdict=verdict,
            claims=decomp.atoms,
            material_claims=decomp.material_claims,
            supported_claims=coverage.covered_claims if coverage else 0,
            verified_claims=decomp.claims_verified,
            coverage_ratio=coverage_ratio,
            threshold=COVERAGE_THRESHOLD_PROCEED,
            gate_failure=None,
            human_decision_required=human_decision_required,
            risk_flags=risk_flags,
            upgraded_evidence_level=upgraded,
            enriched_parsed_output=enriched,
        )

    except Exception as e:
        # Defect 6 fix: FAIL-CLOSED — exception returns HOLD, not pass-through
        logger.error(f"Evidence Gate failed: {e} — returning HOLD (fail-closed)")
        return EvidenceGateResult(
            verdict=EvidenceVerdict.HOLD,
            gate_failure=str(e),
            human_decision_required=True,
            risk_flags=[f"EVIDENCE_GATE_FAILURE: {e} — fail-closed per F1 AMANAH"],
            upgraded_evidence_level="claimed",
            enriched_parsed_output=dict(parsed_output) if isinstance(parsed_output, dict) else {},
        )


def format_gate_report(result: EvidenceGateResult) -> str:
    """Format gate results as human-readable report."""
    lines = [
        "## Evidence Gate",
        f"Verdict: {result.verdict.value.upper()}",
        f"Claims: {result.material_claims} material "
        f"(verified={result.verified_claims}, "
        f"supported={result.supported_claims}, "
        f"coverage={result.coverage_ratio:.0%})",
        f"Evidence level: {result.upgraded_evidence_level}",
        f"Human decision required: {result.human_decision_required}",
    ]
    if result.risk_flags:
        lines.append("Risk flags:")
        for flag in result.risk_flags:
            lines.append(f"  ⚠️ {flag}")
    if result.gate_failure:
        lines.append(f"Gate failure: {result.gate_failure}")
    return "\n".join(lines)
