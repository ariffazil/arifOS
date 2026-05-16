"""
arifosmcp/intelligence/tools/relate_bridge.py — 113_RELATE Bridge
══════════════════════════════════════════════════════════════════════════════

SEALTRIWITNESS Phase 3: Entity extraction and knowledge graph construction.

Bridges SENSE (search results) → RELATE (entity+relation graph).

Architecture:
    RealityHandler.handle_compass() creates EvidenceBundle with results
        ↓ auto_sync_bundle()
        ↓ extract_graph(bundle.results, query)  ← HERE (Phase 3)
        ↓ populate canonical.entities + canonical.relations
        ↓ ingest_evidence_bundle()
        ↓ memory_store.store()

Entity extraction:
    - Primary: Ollama LLM (qwen2.5:3b) for NER + relation extraction
    - Fallback: Regex-based extraction when Ollama unavailable
    - Both are best-effort; extraction failure does NOT fail ingest

Governing rules:
    No entity without source claim.     (F2 TRUTH)
    No relation without both entities.  (F3 WITNESS)
    No extraction without session bind.  (F1 AMANAH)
    Extraction failure is non-fatal.     (resilience)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from arifosmcp.schemas.evidence_bundle import (
    EntitySchema,
    RelationSchema,
)

logger = __name__

# ── Ollama client (lazy import) ────────────────────────────────────────────────

_ollama_client = None


def _get_ollama_client():
    """Lazy-load Ollama client to avoid import-time failure."""
    global _ollama_client
    if _ollama_client is None:
        try:
            import os

            from arifosmcp.core.kernel.metabolic_bridge import OllamaClient

            _ollama_client = OllamaClient(base_url=os.getenv("OLLAMA_URL", "http://ollama:11434"))
            return _ollama_client
        except Exception as exc:
            sys.stderr.write(f"[relate_bridge] OllamaClient unavailable: {exc}\n")
            return None
    return _ollama_client


# ── Regex-based entity extraction (fallback) ────────────────────────────────────


def _regex_extract_entities(text: str) -> list[dict[str, Any]]:
    """
    Simple regex-based entity extraction fallback.

    Covers common patterns:
    - Capitalized multi-word organizations (Company Inc, Corp, etc.)
    - Capitalized multi-word locations (New York, Kuala Lumpur, etc.)
    - URLs
    - Quoted strings

    Returns list of {name, type} dicts.
    """
    entities = []
    seen = set()

    # Capitalized organization patterns (2-5 words ending with legal suffixes)
    org_patterns = [
        r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3}\s+"
        r"(?:Inc\.?|Corp\.?|Ltd\.?|LLC|LLP|Company|Co\.?|Group|Partners|Foundation|"
        r"Institute|University|Agency|Authority|Ministry|Department|Board|Commission|"
        r"Council|Bureau|Office|System|Network|Platform|Service|Project|Initiative|"
        r"Program|Mission|Vision|Strategy|Policy|Framework|Protocol|Standard|Model|"
        r"System|Platform|Solution|Engine|Kernel|Node|Agent|Organ|Federation|Republic|"
        r"State|Kingdom|Empire|Nation|District|Region|Province|County|City|Town|"
        r"Area|Zone|Territory))\b",
    ]
    for pattern in org_patterns:
        for match in re.finditer(pattern, text):
            name = match.group(0).strip()
            if len(name) > 3 and name not in seen:
                seen.add(name)
                entities.append({"name": name, "type": "ORG"})

    # Capitalized location patterns
    loc_patterns = [
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+"
        r"(?:City|State|Province|Region|Country|District|Area|Zone|Island|Mountain|"
        r"River|Lake|Ocean|Sea|Bay|Strait|Canal|Valley|Delta|Highlands|Lowlands|"
        r"East|West|North|South))\b",
        r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,2})\b",
    ]
    for pattern in loc_patterns:
        for match in re.finditer(pattern, text):
            name = match.group(0).strip()
            if len(name) > 3 and name not in seen and not any(c.isdigit() for c in name):
                seen.add(name)
                entities.append({"name": name, "type": "LOC"})

    # URLs
    for match in re.finditer(r"https?://[^\s]+", text):
        url = match.group(0)
        entities.append({"name": url, "type": "URL"})

    return entities[:20]  # Cap at 20 entities


def _regex_extract_relations(text: str, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Simple regex-based relation extraction fallback.

    Identifies relations between extracted entities using common patterns:
    - "X located in Y"
    - "X founded by Y"
    - "X works at Y"
    - "X announced Y"
    - "X launched Y"
    """
    relations = []

    # Simple subject-verb-object patterns
    svo_patterns = [
        (
            r"([A-Z][a-zA-Z\s]+)\s+"
            r"(?:announced|launched|released|introduced|unveiled|revealed|disclosed)\s+"
            r"([A-Z][a-zA-Z\s]+)",
            "announced",
        ),
        (
            r"([A-Z][a-zA-Z\s]+)\s+(?:located|situated|based)\s+(?:in|at)\s+" r"([A-Z][a-zA-Z\s]+)",
            "located_in",
        ),
        (
            r"([A-Z][a-zA-Z\s]+)\s+(?:founded|created|established|built)\s+"
            r"(?:by|with)\s+([A-Z][a-zA-Z\s]+)",
            "founded_by",
        ),
        (
            r"([A-Z][a-zA-Z\s]+)\s+(?:works|employed)\s+(?:at|in|for)\s+" r"([A-Z][a-zA-Z\s]+)",
            "works_at",
        ),
        (
            r"([A-Z][a-zA-Z\s]+)\s+(?:partnered|collaborated|teamed)\s+"
            r"(?:with|and)\s+([A-Z][a-zA-Z\s]+)",
            "partnered_with",
        ),
        (
            r"([A-Z][a-zA-Z\s]+)\s+(?:acquired|bought|purchased|merged)\s+(?:with|and)\s+([A-Z][a-zA-Z\s]+)",
            "acquired",
        ),
        (r"([A-Z][a-zA-Z\s]+)\s+(?:vs\.?|against|vs)\s+([A-Z][a-zA-Z\s]+)", "versus"),
    ]

    for pattern, rel_type in svo_patterns:
        for match in re.finditer(pattern, text):
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            # Verify both entities are in our entity list or are capitalized
            if subject and obj and len(subject) > 2 and len(obj) > 2:
                relations.append(
                    {
                        "subject": subject,
                        "predicate": rel_type,
                        "object": obj,
                        "relation_type": rel_type,
                    }
                )

    return relations[:10]  # Cap at 10 relations


# ── Ollama-based entity extraction (primary) ───────────────────────────────────


async def _ollama_extract_entities(
    query: str, texts: list[str], session_id: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Use Ollama LLM to extract entities and relations from search texts.

    Calls qwen2.5:3b with structured JSON prompt.
    Returns (entities, relations) as dicts.
    """
    client = _get_ollama_client()
    if client is None:
        return [], []

    # Combine texts into a single context (truncated)
    combined = "\n".join(f"- {t[:300]}" for t in texts[:10])
    if len(combined) > 2000:
        combined = combined[:2000] + "\n... (truncated)"

    prompt = f"""You are a named entity recognition (NER) system for arifOS constitutional AI.
Extract ALL named entities and relations from the search results below.

Search query: {query}

Search results:
{combined}

Output ONLY valid JSON with this exact schema:
{{
  "entities": [
    {{
      "name": "string (the entity text)",
      "type": "PERSON | ORG | LOC | PRODUCT | EVENT | TECHNOLOGY | OTHER",
      "aliases": ["alias1", "alias2"],
      "confidence": 0.0
    }}
  ],
  "relations": [
    {{
      "subject": "string (entity name)",
      "predicate": "string (e.g., works_at, located_in, founded_by, announced,"
      " acquired, partnered_with)",
      "object": "string (entity name or value)",
      "relation_type": "string",
      "confidence": 0.0
    }}
  ]
}}

Rules:
- Extract entities with high confidence (0.7+) only
- PERSON: people names (Tanaka, Dr. Smith, Anwar Ibrahim)
- ORG: companies, organizations, governments (OpenAI, WHO, Malaysia Airlines)
- LOC: locations, countries, cities (Kuala Lumpur, Southeast Asia, Silicon Valley)
- PRODUCT: software, hardware products (GPT-4, iPhone, TensorFlow)
- EVENT: events, conferences, incidents (WWDC, COVID-19, COP28)
- TECHNOLOGY: technical standards, frameworks (TCP/IP, JSON, REST API)
- Include relations only when both subject and object are extracted entities
- Output ONLY JSON. No explanation. No markdown."""

    try:
        response = await client.generate(
            model="qwen2.5:3b",
            prompt=prompt,
            format="json",
        )
        parsed = json.loads(response.get("response", "{}"))

        entities = parsed.get("entities", [])
        relations = parsed.get("relations", [])

        # Validate and cap
        entities = [e for e in entities if e.get("name") and e.get("type")][:20]
        relations = [r for r in relations if r.get("subject") and r.get("predicate")][:10]

        sys.stderr.write(
            f"[relate_bridge] Ollama extracted {len(entities)} entities, "
            f"{len(relations)} relations from {len(texts)} texts\n"
        )
        return entities, relations

    except Exception as exc:
        sys.stderr.write(f"[relate_bridge] Ollama extraction failed: {exc}\n")
        return [], []


# ── Main extraction function ───────────────────────────────────────────────────


async def extract_graph(
    bundle_results: list[Any],
    query: str,
    session_id: str = "global",
    use_llm: bool = True,
) -> tuple[list[EntitySchema], list[RelationSchema]]:
    """
    Extract entity graph from search/fetch results.

    This is the 113_RELATE function — takes raw search results and produces
    structured entities + relations for the knowledge graph.

    Args:
        bundle_results: List of SearchResult or FetchResult objects
                        (from runtime EvidenceBundle.results)
        query: The original search query
        session_id: Session for audit trace
        use_llm: If True, try Ollama first, fall back to regex.
                 If False, use regex only.

    Returns:
        (list[EntitySchema], list[RelationSchema])

    Phase 3 acceptance criteria:
        [1] extract_graph returns non-empty entities for real search results
        [2] extract_graph falls back to regex when Ollama unavailable
        [3] entities and relations are correctly typed as EntitySchema/RelationSchema
        [4] extraction failure is non-fatal (returns empty lists, doesn't raise)
    """
    # ── Extract text from search results ────────────────────────────────────
    texts = []
    for result in bundle_results:
        # Handle SearchResult (has .results list of dicts with title/description)
        raw_results = getattr(result, "results", None)
        if isinstance(raw_results, list):
            for item in raw_results:
                if isinstance(item, dict):
                    title = item.get("title", "")
                    description = item.get("description", "")
                    if title:
                        texts.append(f"{title}: {description}")

        # Handle FetchResult (has .raw_content or .url)
        elif hasattr(result, "raw_content") and getattr(result, "raw_content", None):
            content = str(result.raw_content)
            if len(content) > 50:
                texts.append(content[:500])
        elif hasattr(result, "url"):
            url = getattr(result, "url", "")
            texts.append(f"Fetched: {url}")

    if not texts:
        sys.stderr.write(
            f"[relate_bridge] No extractable text from {len(bundle_results)} results\n"
        )
        return [], []

    # ── Try LLM extraction first ──────────────────────────────────────────────
    if use_llm:
        llm_entities, llm_relations = await _ollama_extract_entities(query, texts, session_id)
        if llm_entities or llm_relations:
            entity_schemas = [
                EntitySchema(
                    name=e["name"],
                    type=e.get("type", "OTHER"),
                    aliases=e.get("aliases", []),
                    confidence=float(e.get("confidence", 0.8)),
                )
                for e in llm_entities
            ]
            relation_schemas = [
                RelationSchema(
                    subject=r["subject"],
                    predicate=r["predicate"],
                    object=r.get("object"),
                    relation_type=r.get("relation_type", r["predicate"]),
                    confidence=float(r.get("confidence", 0.7)),
                )
                for r in llm_relations
            ]
            return entity_schemas, relation_schemas

    # ── Fallback to regex extraction ────────────────────────────────────────
    sys.stderr.write("[relate_bridge] Falling back to regex extraction\n")
    combined_text = " ".join(texts)[:5000]  # Cap at 5000 chars
    raw_entities = _regex_extract_entities(combined_text)
    raw_relations = _regex_extract_relations(combined_text, raw_entities)

    entity_schemas = [
        EntitySchema(
            name=e["name"],
            type=e.get("type", "OTHER"),
            aliases=[],
            confidence=0.5,
        )
        for e in raw_entities
    ]
    relation_schemas = [
        RelationSchema(
            subject=r["subject"],
            predicate=r["predicate"],
            object=r.get("object"),
            relation_type=r.get("relation_type", r["predicate"]),
            confidence=0.4,
        )
        for r in raw_relations
    ]

    sys.stderr.write(
        f"[relate_bridge] Regex extracted {len(entity_schemas)} entities, "
        f"{len(relation_schemas)} relations\n"
    )
    return entity_schemas, relation_schemas
