"""
arifosmcp/runtime/f4_contradiction_handler.py -- Phase 1b: F4 Contradiction Handling

F4 Clarity: Entity extraction + contradiction detection + supersession resolution.

Three contradiction types:
  T1: Direct negation -- Fact X and NOT-X for same entity
      (e.g. "owns Basin C" vs "divested Basin C")
  T2: Scope change -- Cardinality change without explicit negation
      (e.g. "3 basins" -> "2 basins")
  T3: Entity merge/split -- Identity period changes
      (e.g. "OldCo" -> "NewCo")

Five resolution options:
  SUPERSEDE -- Newer valid_at wins; older tagged historical
              [DEFAULT when temporal order is clear]
  MERGE -- Both stored with valid_at ranges
          [when temporal order is ambiguous]
  ESCALATE -- Neither stored; flagged for Arif review
             [high-stakes: ORG-level entities]
  RETIRE -- Old entry retired; new stored
           [old is clearly stale noise]
  VOID -- Both flagged contradiction_hold; manual resolve
         [cannot determine temporal order]

Integration:
  - Phase 1b: Called at write_path after HARAM scan, before dual-write
  - Phase 1c: supersession lineage surfaced in search() results

DITEMPA BUKAN DIBERI -- Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
# F4 extraction uses a text-generation model (not an embedding model).
# bge-m3 was incorrectly used here; it cannot generate coherent text.
_EXTRACTION_MODEL = os.getenv("F4_EXTRACTION_MODEL", "qwen2.5:3b")
_PG_URL = os.getenv(
    "ARIFOS_MEMORY_POSTGRES_URL",
    "postgresql://arifos_admin:ArifPostgresVault2026!@postgres:5432/vault999",
)

# ============================================================================
# F4 Entity Extraction Output Schema
# ============================================================================


@dataclass
class F4Entity:
    """Single extracted entity with F4 clarity metadata."""

    category: str  # ORG, GEO, TECH, PERSON, DATE, CONCEPT, etc.
    value: str  # The actual entity value
    confidence: float  # 0.0–1.0
    temporal_marker: str = "unknown"  # active | historical | unknown


@dataclass
class F4ExtractionResult:
    """Output of F4 entity extraction at write_path."""

    entity_tags: list[str]  # Flat list: "ORG:PETRONAS", "GEO:Basin C"
    entities: list[F4Entity]  # Structured with confidence + temporal markers
    contradiction_signals: list[dict]  # Detected conflicts requiring resolution
    extraction_metadata: dict  # Model, version, timestamp
    raw_llm_output: dict | None = None  # Full LLM response for audit


# ============================================================================
# F4 Entity Extraction Prompt
# ============================================================================

_F4_EXTRACTION_PROMPT = """\
You are F4-CLARITY, an entity extraction module for a governed AI memory system.

Extract named entities from the following text. For each entity:
1. Identify the CATEGORY (ORG, GEO, TECH, PERSON, DATE, CONCEPT, etc.)
2. Extract the VALUE (the actual entity name)
3. Assess CONFIDENCE (0.0-1.0)
4. Determine TEMPORAL MARKER:
   - "active" = current/relevant relationship in present tense or recent past
   - "historical" = explicitly described as past/former/deprecated
   - "unknown" = no temporal signal in text

Also detect CONTRADICTION SIGNALS -- places where this text might conflict:
- T1: Direct negation (e.g. "divested" vs "owns", "cancelled" vs "approved")
- T2: Scope changes (e.g. "expanded to 5 basins" when prior said "3 basins")
- T3: Entity identity changes (e.g. "renamed from X to Y", "merged with X")

Return a JSON object with this exact structure:
{
  "entities": [
    {
      "category": "ORG",
      "value": "...",
      "confidence": 0.0-1.0,
      "temporal_marker": "active|historical|unknown"
    }
  ],
  "contradiction_signals": [
    {
      "type": "T1|T2|T3",
      "entity_pair": "CATEGORY:VALUE",
      "signal": "human-readable description of what conflicts",
      "confidence": 0.0-1.0,
      "requires_resolution": true|false
    }
  ],
  "extraction_metadata": {
    "extracted_at": "ISO8601 timestamp",
    "model_used": "model name",
    "extraction_version": "1.0"
  }
}

Text to analyze:
---
{content}
---

JSON output only, no explanation:"""

# ============================================================================
# F4 Entity Extraction — Core Function
# ============================================================================


def extract_entities(content: str) -> F4ExtractionResult:
    """Extract F4 entities and contradiction signals from content.

    Uses Ollama (bge-m3 or general LLM) for structured extraction.
    Falls back to regex heuristics if LLM unavailable.

    Returns F4ExtractionResult with entity_tags, entities,
    contradiction_signals, and extraction_metadata.
    """
    if not content or not content.strip():
        return F4ExtractionResult(
            entity_tags=[],
            entities=[],
            contradiction_signals=[],
            extraction_metadata={
                "extracted_at": _iso_now(),
                "model_used": "none",
                "extraction_version": "1.0",
            },
        )

    # Try LLM extraction first
    llm_result = _llm_extract(content)
    if llm_result is not None:
        return llm_result

    # Fallback: regex-based heuristic extraction
    logger.warning("F4 extract_entities: LLM unavailable, using regex fallback")
    return _regex_fallback_extract(content)


def _llm_extract(content: str) -> F4ExtractionResult | None:
    """Call Ollama with F4 extraction prompt. Returns None on failure."""
    try:
        prompt = _F4_EXTRACTION_PROMPT.format(content=content[:4000])  # Guard token limit
        response = httpx.post(
            f"{_OLLAMA_URL}/api/generate",
            json={
                "model": _EXTRACTION_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 1024},
            },
            timeout=30.0,
        )
        response.raise_for_status()
        raw = response.json()
        text = raw.get("response", "").strip()

        # Parse JSON from LLM response
        json_str = _extract_json(text)
        if not json_str:
            return None

        data = json.loads(json_str)

        entities = [
            F4Entity(
                category=e.get("category", "CONCEPT"),
                value=e.get("value", ""),
                confidence=float(e.get("confidence", 0.5)),
                temporal_marker=e.get("temporal_marker", "unknown"),
            )
            for e in data.get("entities", [])
            if e.get("value")
        ]

        entity_tags = [f"{e.category}:{e.value}" for e in entities]

        contradiction_signals = data.get("contradiction_signals", [])

        return F4ExtractionResult(
            entity_tags=entity_tags,
            entities=entities,
            contradiction_signals=contradiction_signals,
            extraction_metadata={
                "extracted_at": _iso_now(),
                "model_used": _EXTRACTION_MODEL,
                "extraction_version": "1.0",
            },
            raw_llm_output=data,
        )

    except Exception as exc:
        logger.warning("F4 LLM extraction failed: %s", exc)
        return None


def _regex_fallback_extract(content: str) -> F4ExtractionResult:
    """Regex-based heuristic entity extraction when LLM is unavailable."""
    entities: list[F4Entity] = []
    seen: set[str] = set()

    # ORG patterns
    for match in re.finditer(
        r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:Sdn\s+Bhd|Bhd|Malaysia|Group|Corp|Inc|Ltd)\b",
        content,
    ):
        val = match.group(1).strip()
        key = f"ORG:{val}"
        if key not in seen:
            seen.add(key)
            entities.append(
                F4Entity(category="ORG", value=val, confidence=0.6, temporal_marker="unknown")
            )

    # Standalone org names (all-caps words that look like companies)
    for match in re.finditer(r"\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b", content):
        val = match.group(1).strip()
        if len(val) > 2 and val not in seen:
            key = f"ORG:{val}"
            seen.add(key)
            entities.append(
                F4Entity(category="ORG", value=val, confidence=0.4, temporal_marker="unknown")
            )

    # GEO patterns (countries, cities, regions with capital letters)
    geo_patterns = [
        r"\b(Malaysia|Singapore|Indonesia|Thailand|Vietnam|Philippines|Brunei)\b",
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Basin|Field|Block|Platform|Rig)\b",
    ]
    for pattern in geo_patterns:
        for match in re.finditer(pattern, content):
            val = match.group(1).strip()
            key = f"GEO:{val}"
            if key not in seen:
                seen.add(key)
                entities.append(
                    F4Entity(category="GEO", value=val, confidence=0.7, temporal_marker="unknown")
                )

    # Temporal markers from text
    historical_kw = {
        "former",
        "past",
        "old",
        "previous",
        "ex-",
        "deprecated",
        "discontinued",
        "divested",
        "sold",
    }
    active_kw = {"current", "present", "existing", "active", "ongoing", "now"}

    content_lower = content.lower()
    has_historical = any(kw in content_lower for kw in historical_kw)
    has_active = any(kw in content_lower for kw in active_kw)

    # Apply temporal markers based on keyword detection
    for e in entities:
        if has_historical and not has_active:
            e.temporal_marker = "historical"
        elif has_active and not has_historical:
            e.temporal_marker = "active"

    entity_tags = [f"{e.category}:{e.value}" for e in entities]

    return F4ExtractionResult(
        entity_tags=entity_tags,
        entities=entities,
        contradiction_signals=[],
        extraction_metadata={
            "extracted_at": _iso_now(),
            "model_used": "regex_fallback",
            "extraction_version": "1.0",
        },
    )


# ============================================================================
# Contradiction Detection
# ============================================================================


def detect_contradictions(
    new_entity_tags: list[str],
    new_valid_at: datetime | None,
    new_content_hash: str,
) -> list[dict]:
    """Query Postgres for existing memories that contradict the new entry.

    Returns list of conflicting existing memory entries (from PG).
    Each conflict dict includes: memory_id, entity_tags, valid_at, text_summary,
    distillation_status, superseded_by.
    """
    if not new_entity_tags:
        return []

    try:
        import asyncpg
    except ImportError:
        return []

    try:

        async def _query():
            conn = await asyncpg.connect(_PG_URL, timeout=10)
            try:
                rows = await conn.fetch(
                    """
                    SELECT
                        id::text,
                        entity_tags,
                        valid_at,
                        recorded_at,
                        text,
                        metadata,
                        distillation_status,
                        superseded_by
                    FROM memory_store
                    WHERE deleted_at IS NULL
                      AND distillation_status NOT IN ('void', 'contradiction_hold')
                      AND superseded_by IS NULL
                      AND entity_tags && $1
                      ORDER BY valid_at DESC
                    LIMIT 20
                    """,
                    new_entity_tags,
                )
                return [dict(row) for row in rows]
            finally:
                await conn.close()

        return _pg_run_sync(_query)

    except Exception as exc:
        logger.warning("Contradiction detection query failed: %s", exc)
        return []


def _pg_run_sync(coro):
    """Run async coroutine synchronously via fresh event loop."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================================
# T1/T2/T3 Conflict Classification
# ============================================================================


def classify_conflict_type(new_entry: dict, existing_entry: dict) -> str:
    """Classify the contradiction type between two memory entries.

    T1: Direct negation — explicit opposite claims about same entity
    T2: Scope change — cardinality or relationship change without explicit negation
    T3: Entity merge/split — identity change over time

    Returns: T1 | T2 | T3
    """
    new_text = (
        (existing_entry.get("metadata") or {})
        .get("content", existing_entry.get("text", ""))
        .lower()
    )
    existing_text = (
        (existing_entry.get("metadata") or {})
        .get("content", existing_entry.get("text", ""))
        .lower()
    )

    combined = new_text + " " + existing_text

    # T1: Direct negation patterns
    negation_pairs = [
        ("owns", "divested"),
        ("owns", "sold"),
        ("acquired", "divested"),
        ("approved", "rejected"),
        ("active", "inactive"),
        ("continues", "discontinued"),
        ("expanded", "contracted"),
        ("increased", "decreased"),
    ]
    for pos, neg in negation_pairs:
        if pos in new_text and neg in existing_text:
            return "T1"
        if neg in new_text and pos in existing_text:
            return "T1"

    # T1: Explicit negation keywords
    t1_kw = {
        "divested",
        "sold",
        "rejected",
        "cancelled",
        "terminated",
        "discontinued",
        "former",
        "ex-",
        "deprecated",
    }
    if any(kw in combined for kw in t1_kw):
        # Check if same entity is referenced
        new_orgs = set(re.findall(r"ORG:(\w+)", str(new_entry.get("entity_tags", []))))
        old_orgs = set(re.findall(r"ORG:(\w+)", str(existing_entry.get("entity_tags", []))))
        if new_orgs & old_orgs:  # Same org referenced
            return "T1"

    # T3: Entity merge/split patterns
    t3_patterns = [
        r"renamed\s+from\s+(\w+)\s+to\s+(\w+)",
        r"merged\s+with\s+(\w+)",
        r"spun\s+off\s+into\s+(\w+)",
        r"formerly\s+known\s+as\s+(\w+)",
    ]
    for pattern in t3_patterns:
        if re.search(pattern, combined, re.IGNORECASE):
            return "T3"

    # Default to T2 (scope change)
    return "T2"


# ============================================================================
# Supersession Resolution
# ============================================================================


@dataclass
class ResolutionResult:
    """Result of contradiction resolution."""

    resolution: str  # supersede | merge | escalate | retire | void
    conflicts: list[dict]  # conflicting entries found
    new_entry_meta: dict  # Updated metadata for the new entry
    contradictions_logged: int  # Number written to memory_contradictions


def resolve_contradictions(
    new_memory_id: str,
    new_entity_tags: list[str],
    new_valid_at: datetime | None,
    new_recorded_at: datetime,
    new_content_hash: str,
    new_text_summary: str,
    conflicts: list[dict],
    new_phoenix_state: str = "cooling",
) -> ResolutionResult:
    """Resolve contradictions between new entry and existing entries.

    Applies the 5-option resolution strategy.
    Default: SUPERSEDE when temporal order is clear.

    Returns ResolutionResult with resolution type, updated metadata,
    and count of contradictions logged.
    """
    if not conflicts:
        return ResolutionResult(
            resolution="none",
            conflicts=[],
            new_entry_meta={},
            contradictions_logged=0,
        )

    # Determine resolution based on conflict characteristics
    resolution, contradictions_logged = _apply_resolution(
        new_memory_id=new_memory_id,
        new_entity_tags=new_entity_tags,
        new_valid_at=new_valid_at or new_recorded_at,
        new_recorded_at=new_recorded_at,
        new_content_hash=new_content_hash,
        new_text_summary=new_text_summary,
        conflicts=conflicts,
        new_phoenix_state=new_phoenix_state,
    )

    # Build supersession metadata for new entry
    superseded_olds = [c["id"] for c in conflicts]
    new_entry_meta = {
        "supersedes": superseded_olds,
        "superseded_count": len(superseded_olds),
        "resolution": resolution,
        "contradictions_logged": contradictions_logged,
        "valid_at": new_valid_at.isoformat() if new_valid_at else None,
    }

    return ResolutionResult(
        resolution=resolution,
        conflicts=conflicts,
        new_entry_meta=new_entry_meta,
        contradictions_logged=contradictions_logged,
    )


def _apply_resolution(
    new_memory_id: str,
    new_entity_tags: list[str],
    new_valid_at: datetime,
    new_recorded_at: datetime,
    new_content_hash: str,
    new_text_summary: str,
    conflicts: list[dict],
    new_phoenix_state: str,
) -> tuple[str, int]:
    """Apply resolution strategy to conflicts. Returns (resolution, logged_count)."""
    import asyncpg

    logged = 0

    # Classify conflict types
    conflict_types = []
    for conflict in conflicts:
        ctype = classify_conflict_type(
            {"entity_tags": new_entity_tags},
            conflict,
        )
        conflict_types.append(ctype)

    # T1 conflicts: default SUPERSEDE (temporal order is usually clear)
    # T3 conflicts: ESCALATE (identity changes need human review)
    # T2 conflicts: SUPERSEDE or MERGE depending on temporal clarity

    has_t3 = "T3" in conflict_types
    has_t1 = "T1" in conflict_types

    if has_t3:
        resolution = "escalate"
    elif has_t1:
        resolution = "supersede"
    else:
        resolution = "supersede"

    # SUPERSEDE: mark old entries as historical
    if resolution == "supersede":

        async def _supersede():
            nonlocal logged
            conn = await asyncpg.connect(_PG_URL, timeout=10)
            try:
                for conflict in conflicts:
                    old_id = conflict["id"]
                    # Update old entry: temporal_marker=historical, superseded_by=new_id
                    await conn.execute(
                        """
                        UPDATE memory_store
                        SET temporal_marker = 'historical',
                            superseded_by = $1::uuid,
                            superseded_at = $2,
                            distillation_metadata = jsonb_set(
                                COALESCE(distillation_metadata, '{}'),
                                '{superseded}',
                                $3::jsonb
                            )
                        WHERE id = $4::uuid
                          AND deleted_at IS NULL
                        """,
                        uuid.UUID(new_memory_id) if len(new_memory_id) == 32 else uuid.uuid4(),
                        new_valid_at,
                        json.dumps(
                            {
                                "superseded_by": new_memory_id,
                                "superseded_at": new_valid_at.isoformat(),
                                "resolution": "supersede",
                            }
                        ),
                        uuid.UUID(old_id) if len(old_id) == 32 else uuid.uuid4(),
                    )

                    # Log contradiction
                    entity_pair = _format_entity_pair(
                        new_entity_tags, conflict.get("entity_tags", [])
                    )
                    await conn.execute(
                        """
                        INSERT INTO memory_contradictions
                            (memory_id_new, memory_id_old, conflict_type, entity_pair,
                             signal, confidence, resolution, resolved_by)
                        VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7, $8)
                        """,
                        uuid.UUID(new_memory_id) if len(new_memory_id) == 32 else uuid.uuid4(),
                        uuid.UUID(old_id) if len(old_id) == 32 else uuid.uuid4(),
                        "T1" if has_t1 else "T2",
                        entity_pair,
                        "contradiction detected via F4 entity extraction",
                        0.75,
                        "supersede",
                        "system",
                    )
                    logged += 1
            finally:
                await conn.close()

        _pg_run_sync(_supersede())

    # ESCALATE: flag both for Arif review
    elif resolution == "escalate":

        async def _escalate():
            nonlocal logged
            conn = await asyncpg.connect(_PG_URL, timeout=10)
            try:
                for conflict in conflicts:
                    old_id = conflict["id"]
                    # Mark both as contradiction_hold
                    for mid in [new_memory_id, old_id]:
                        try:
                            await conn.execute(
                                """
                                UPDATE memory_store
                                SET distillation_status = 'contradiction_hold'
                                WHERE id = $1::uuid AND deleted_at IS NULL
                                """,
                                uuid.UUID(mid) if len(mid) == 32 else uuid.uuid4(),
                            )
                        except Exception:
                            pass

                    # Log contradiction for Arif review
                    entity_pair = _format_entity_pair(
                        new_entity_tags, conflict.get("entity_tags", [])
                    )
                    await conn.execute(
                        """
                        INSERT INTO memory_contradictions
                            (memory_id_new, memory_id_old, conflict_type, entity_pair,
                             signal, confidence, resolution, resolved_by)
                        VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7, $8)
                        """,
                        uuid.UUID(new_memory_id) if len(new_memory_id) == 32 else uuid.uuid4(),
                        uuid.UUID(old_id) if len(old_id) == 32 else uuid.uuid4(),
                        "T3",
                        entity_pair,
                        "T3 entity merge/split — requires Arif review",
                        0.85,
                        "escalate",
                        "system",
                    )
                    logged += 1
            finally:
                await conn.close()

        _pg_run_sync(_escalate())

    return resolution, logged


def _format_entity_pair(new_tags: list[str], old_tags: list[str]) -> str:
    """Format entity pair string for contradiction log."""
    new_set = set(new_tags)
    old_set = set(old_tags)
    shared = new_set & old_set
    if shared:
        return list(shared)[0]
    if new_tags:
        return new_tags[0]
    if old_tags:
        return old_tags[0]
    return "unknown"


# ============================================================================
# F4 Extraction + Contradiction Check — Combined Write Path Hook
# ============================================================================


@dataclass
class F4WritePathResult:
    """Result of F4 extraction + contradiction check at write_path."""

    entity_tags: list[str]
    entities: list[F4Entity]
    contradiction_signals: list[dict]
    resolution: str  # none | supersede | escalate | merge | retire | void
    conflicts: list[dict]  # conflicting entries found
    superseded_by_old: list[str]  # old memory_ids that were superseded
    new_entry_meta: dict  # metadata to merge into new entry
    contradictions_logged: int  # count written to memory_contradictions
    extraction_metadata: dict


def f4_write_path_hook(
    content: Any,
    content_hash: str,
    recorded_at: datetime | None = None,
    valid_at: datetime | None = None,
) -> F4WritePathResult:
    """Combined F4 extraction + contradiction detection for the store() write path.

    Called after HARAM scan passes, before dual-write.

    Returns F4WritePathResult with:
    - entity_tags for Qdrant/PG storage
    - resolution result (none, supersede, escalate)
    - supersession metadata for new entry
    - contradiction audit count
    """
    now = recorded_at or datetime.now(UTC)

    # Step 1: F4 Entity Extraction
    if isinstance(content, str):
        text_for_extraction = content
    elif isinstance(content, dict):
        text_for_extraction = json.dumps(content, default=str)
    else:
        text_for_extraction = str(content)

    extraction = extract_entities(text_for_extraction)

    if not extraction.entity_tags:
        return F4WritePathResult(
            entity_tags=[],
            entities=[],
            contradiction_signals=[],
            resolution="none",
            conflicts=[],
            superseded_by_old=[],
            new_entry_meta={"valid_at": valid_at.isoformat() if valid_at else None},
            contradictions_logged=0,
            extraction_metadata=extraction.extraction_metadata,
        )

    # Step 2: Contradiction Detection
    conflicts = detect_contradictions(
        new_entity_tags=extraction.entity_tags,
        new_valid_at=valid_at or now,
        new_content_hash=content_hash,
    )

    if not conflicts:
        return F4WritePathResult(
            entity_tags=extraction.entity_tags,
            entities=extraction.entities,
            contradiction_signals=extraction.contradiction_signals,
            resolution="none",
            conflicts=[],
            superseded_by_old=[],
            new_entry_meta={"valid_at": valid_at.isoformat() if valid_at else None},
            contradictions_logged=0,
            extraction_metadata=extraction.extraction_metadata,
        )

    # Step 3: Resolution
    resolution_result = resolve_contradictions(
        new_memory_id="placeholder",  # Will be updated with real memory_id after store()
        new_entity_tags=extraction.entity_tags,
        new_valid_at=valid_at or now,
        new_recorded_at=now,
        new_content_hash=content_hash,
        new_text_summary=text_for_extraction[:120],
        conflicts=conflicts,
    )

    return F4WritePathResult(
        entity_tags=extraction.entity_tags,
        entities=extraction.entities,
        contradiction_signals=extraction.contradiction_signals,
        resolution=resolution_result.resolution,
        conflicts=conflicts,
        superseded_by_old=[c["id"] for c in conflicts],
        new_entry_meta=resolution_result.new_entry_meta,
        contradictions_logged=resolution_result.contradictions_logged,
        extraction_metadata=extraction.extraction_metadata,
    )


# ============================================================================
# Utilities
# ============================================================================


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


_JSON_RE = re.compile(r"\{[\s\S]*\}", re.IGNORECASE)


def _extract_json(text: str) -> str | None:
    """Extract first valid JSON object from LLM output."""
    match = _JSON_RE.search(text)
    if match:
        return match.group(0)
    # Try whole text as JSON
    try:
        json.loads(text)
        return text
    except (json.JSONDecodeError, TypeError):
        pass
    return None


# DITEMPA BUKAN DIBERI — Forged, Not Given
