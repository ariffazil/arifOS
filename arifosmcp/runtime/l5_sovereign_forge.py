"""
arifosmcp/runtime/l5_sovereign_forge.py
═══════════════════════════════════════════════════════════════════════════
555_MEMORY → L5 (Sovereign Knowledge Graph Forge)

PURPOSE
-------
Replaces l5_graphiti_bridge.py with a pure-sovereign pipeline:
  Ollama (local LLM) → structured JSON extraction → Pydantic validation
  → deterministic Cypher MERGE → FalkorDB (RedisGraph)

PHILOSOPHY
----------
- Zero external dependencies. Zero API keys. Zero black boxes.
- F1 (Reversibility): MERGE is idempotent. Re-running = zero duplicates.
- F2 (Truth): Pydantic guardrails + temperature=0 retry loop reject
  hallucinations. Corrupted extractions are logged, never written.
- Non-blocking. L5 is enrichment. L3/L4 success is never gated on L5.
- Deterministic UUIDs derived from (actor_id, session_id, timestamp,
  content_hash) ensure the same memory always maps to the same graph node.

CALLER
------
memory_store.store() calls forge_l5() after successful Qdrant + Postgres
writes. The call is wrapped in try/except and swallowed — fire-and-forget.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_L5_MODEL", "qwen2.5:3b")
_FALKORDB_HOST = os.getenv("FALKORDB_HOST", "localhost")
# FalkorDB now runs standalone on 6380 (regular Redis owns 6379)
_FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6380"))
_FALKORDB_GRAPH = os.getenv("FALKORDB_GRAPH", "arifos")
_L5_ENABLED = os.getenv("L5_SOVEREIGN_ENABLED", "true").lower() == "true"
_L5_TIMEOUT_S = float(os.getenv("L5_SOVEREIGN_TIMEOUT_S", "180.0"))
_L5_MAX_RETRIES = int(os.getenv("L5_SOVEREIGN_MAX_RETRIES", "2"))
_L5_ASYNC = os.getenv("L5_SOVEREIGN_ASYNC", "true").lower() == "true"

# Substrate selection (F1 reversibility, sovereign substrate freedom)
# Order of preference: FalkorDB > Qdrant graph-on-payload > none
# Detected once, then cached. See _execute_cypher for the routing logic.
_SUBSTRATE: str | None = None  # 'falkordb' | 'qdrant' | 'none' | None (undetected)
_QDRANT_L5_COLLECTION = os.getenv("QDRANT_L5_COLLECTION", "arifos_l5_graph")
_QDRANT_CLIENT: Any = None  # lazy-init; reused across calls

# ── Pydantic Schemas (F2 Truth Guardrails) ─────────────────────────────────

try:
    from pydantic import BaseModel, Field, ValidationError
except ImportError:
    # F2 HARD REQUIREMENT: pydantic is mandatory for the F2 truth guardrail.
    # We do NOT silently fall back to no-op validation. If pydantic is
    # missing, the daemon refuses to start. This is intentional.
    raise RuntimeError(
        "L5 Sovereign Forge REQUIRES pydantic. Install with: "
        "pip install 'pydantic>=2.13'. The F2 truth guardrail cannot "
        "be opt-out — corrupted extractions would corrupt the graph."
    )


class ExtractedEntity(BaseModel):
    """A node in the knowledge graph."""

    name: str = Field(..., min_length=1, max_length=128)
    type: str = Field(..., min_length=1, max_length=64)
    role: str | None = Field(default=None, max_length=128)
    properties: dict[str, Any] = Field(default_factory=dict)


class ExtractedEdge(BaseModel):
    """A relationship between two nodes."""

    source: str = Field(..., min_length=1, max_length=128)
    target: str = Field(..., min_length=1, max_length=128)
    relation: str = Field(..., min_length=1, max_length=64)
    properties: dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """Structured output from the sovereign LLM extractor."""

    episode_name: str = Field(..., min_length=1, max_length=256)
    episode_properties: dict[str, Any] = Field(default_factory=dict)
    entities: list[ExtractedEntity] = Field(default_factory=list, max_length=50)
    edges: list[ExtractedEdge] = Field(default_factory=list, max_length=100)


# ── System Prompt (Strict Sovereign Prompt Engineering) ────────────────────

_SYSTEM_PROMPT = """You are a sovereign knowledge-graph extractor. Your job is to read a memory text and emit a STRICT JSON object containing nodes and edges for a graph database.

RULES (violation = rejection):
1. Output MUST be valid JSON only. No markdown, no explanations, no preamble.
2. All strings MUST be ASCII-safe. Escape newlines as \\n.
3. Episode node represents the memory event itself.
4. Entity nodes are the "nouns" (people, files, locations, concepts, agents).
5. Edge relations MUST be verbs in SCREAMING_SNAKE_CASE (e.g., CREATED_BY, FIXED, MODIFIED, REMOVED, EXECUTED_ON, MENTIONS).
6. If extraction is uncertain, emit fewer entities rather than hallucinate.
7. Maximum 25 entities, 50 edges.

JSON SCHEMA:
{
  "episode_name": "short event name",
  "episode_properties": {"summary": "...", "session_id": "...", "actor_id": "...", "tier": "..."},
  "entities": [
    {"name": "EntityName", "type": "Person|Agent|Document|Location|Directory|Concept|Event", "role": "...", "properties": {}}
  ],
  "edges": [
    {"source": "SourceName", "target": "TargetName", "relation": "RELATION_NAME", "properties": {}}
  ]
}

EXAMPLE INPUT:
"Agent alpha fixed test_foo.py and removed build/ on host-01 for user bob."

EXAMPLE OUTPUT:
{
  "episode_name": "Alpha fix session",
  "episode_properties": {"summary": "Agent alpha fixed test_foo.py and removed build/"},
  "entities": [
    {"name": "alpha", "type": "Agent", "role": "instrument"},
    {"name": "bob", "type": "Person", "role": "sovereign"},
    {"name": "test_foo.py", "type": "Document", "role": "test_file"},
    {"name": "build/", "type": "Directory", "role": "removed_artifact"},
    {"name": "host-01", "type": "Location", "role": "vps_host"}
  ],
  "edges": [
    {"source": "Alpha fix session", "target": "test_foo.py", "relation": "FIXED"},
    {"source": "Alpha fix session", "target": "build/", "relation": "REMOVED"},
    {"source": "Alpha fix session", "target": "host-01", "relation": "EXECUTED_ON"},
    {"source": "alpha", "target": "bob", "relation": "ACTS_ON_BEHALF_OF"}
  ]
}

Now extract from the following memory text:
"""


# ── Core Pipeline ──────────────────────────────────────────────────────────


def _generate_deterministic_uuid(
    actor_id: str | None,
    session_id: str | None,
    memory_id: str,
    content_hash: str,
) -> str:
    """Generate a deterministic UUIDv4-like string from attestation fields.

    Using BLAKE2b-128 so the same memory always hashes to the same graph node.

    F1 FIX 2026-09-13 (session SEAL-64d8d16afb864e0d): the seed previously
    included the wall-clock `timestamp`, which guaranteed a FRESH uuid on
    every re-forge of the same memory — MERGE could never match, so replays
    duplicated episodes (reproduced in acceptance A2: replay Δnodes=+6).
    Identity is now the memory lineage (memory_id + content_hash); the
    wall-clock remains a node PROPERTY (created_at = learned-at), not identity.
    """
    seed = f"{actor_id or 'anonymous'}:{session_id or 'none'}:{memory_id}:{content_hash}"
    digest = hashlib.blake2b(seed.encode(), digest_size=16).hexdigest()
    # Format as UUID: 8-4-4-4-12
    return f"{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}"


def _episode_exists(episode_uuid: str) -> bool:
    """F1 idempotency short-circuit: is this episode UUID already in the graph?

    Probes FalkorDB only (primary substrate). uuid is hex+dash — no injection
    surface. Any failure → False (fail open to the normal MERGE path, which is
    itself idempotent by uuid once the substrate routing runs).
    """
    try:
        import redis as _redis

        r = _redis.Redis(
            host=_FALKORDB_HOST,
            port=_FALKORDB_PORT,
            socket_connect_timeout=2,
            socket_timeout=3,
        )
        res = r.execute_command(
            "GRAPH.RO_QUERY",
            _FALKORDB_GRAPH,
            f"MATCH (e:Episode {{uuid: '{episode_uuid}'}}) RETURN count(e)",
        )
        node = res[1] if isinstance(res, (list, tuple)) and len(res) > 1 else None
        while isinstance(node, (list, tuple)):
            if not node:
                return False
            node = node[0]
        return int(node) > 0
    except Exception:
        return False


def _call_ollama_extract(
    text: str,
    max_retries: int = _L5_MAX_RETRIES,
) -> ExtractionResult | None:
    """Send text to local Ollama and return validated ExtractionResult.

    Retry loop enforces F2 (Truth):
      - Attempt 1: temperature=0.2 (slight creativity for entity typing)
      - Attempt 2+: temperature=0.0 (forced determinism)
      - If all retries fail → return None (corrupted data is NOT written)
    """
    if BaseModel is None:
        logger.warning("L5 Sovereign Forge: pydantic unavailable — skipping extraction")
        return None

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": text[:4000]},  # Guard context window
    ]

    for attempt in range(1, max_retries + 1):
        temperature = 0.0 if attempt > 1 else 0.2
        payload = {
            "model": _OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2048,
            },
            "format": "json",
        }

        try:
            import httpx  # noqa: PLC0415

            with httpx.Client(timeout=_L5_TIMEOUT_S) as client:
                r = client.post(
                    f"{_OLLAMA_URL}/v1/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                r.raise_for_status()
                data = r.json()

            raw_content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            parsed = json.loads(raw_content)
            result = ExtractionResult.model_validate(parsed)

            # F2 sanity check: episode_name must not be empty
            if not result.episode_name or not result.entities:
                logger.warning(
                    "L5 extraction attempt %d returned empty entities — retrying",
                    attempt,
                )
                continue

            logger.info(
                "L5 extraction succeeded on attempt %d: %d entities, %d edges",
                attempt,
                len(result.entities),
                len(result.edges),
            )
            return result

        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning(
                "L5 extraction attempt %d validation failed (%s) — retrying",
                attempt,
                type(exc).__name__,
            )
        except Exception as exc:
            logger.warning(
                "L5 extraction attempt %d failed (%s) — retrying",
                attempt,
                type(exc).__name__,
            )

    logger.error(
        "L5 extraction FAILED after %d attempts. Corrupted data NOT written to graph.",
        max_retries,
    )
    return None


def _build_cypher(
    result: ExtractionResult,
    episode_uuid: str,
    memory_id: str,
    session_id: str | None,
    actor_id: str | None,
    tier: str | None,
    content_hash: str,
    l3_point_id: str | None,
    l4_row_id: str | None,
    lineage: dict[str, Any] | None = None,
) -> str:
    """Construct a single atomic Cypher MERGE statement.

    All nodes and edges are MERGE'd so re-running is idempotent (F1).
    Variable names are collision-resistant: a `name -> var` registry tracks
    every entity's first-seen variable, and duplicates get a numeric suffix
    (e.g. "build/" -> n_build_1, "build." -> n_build_2). This prevents the
    F2/Cypher breakage that would occur if two entities sanitized to the
    same identifier.
    """

    # Sanitize helper (string literals only — variable names use a separate
    # collision-resistant mapping).
    def _s(v: str) -> str:
        # F2 FIX 2026-09-13 (session SEAL-64d8d16afb864e0d): single quotes were
        # NOT escaped, but all property literals are single-quoted — any
        # apostrophe in content (e.g. "Claude's") broke the whole Cypher
        # statement (reproduced in acceptance test A1b: cypher_failed).
        return (
            v.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )

    def _var_token(name: str) -> str:
        """Sanitize a name for use as a Cypher variable token."""
        out = []
        for ch in name:
            if ch.isalnum() or ch == "_":
                out.append(ch)
            else:
                out.append("_")
        token = "".join(out).strip("_") or "X"
        if token[0].isdigit():
            token = "n_" + token
        return token

    lines: list[str] = []
    var_registry: dict[str, str] = {}  # name -> unique var token
    var_counter: dict[str, int] = {}  # base var token -> count seen

    def _resolve_var(name: str) -> str:
        """Return a unique Cypher variable token for `name`, registering it
        on first use. Subsequent uses of the same name return the same token
        UNLESS another entity with the same sanitized token appears, in
        which case a new suffixed token is allocated.
        """
        base = _var_token(name)
        if name in var_registry:
            return var_registry[name]
        if base not in var_counter:
            var_counter[base] = 0
            var_registry[name] = base
            return base
        var_counter[base] += 1
        new_token = f"{base}_{var_counter[base]}"
        var_registry[name] = new_token
        return new_token

    # Episode node
    ep_props = {
        "uuid": episode_uuid,
        "name": result.episode_name,
        "memory_id": memory_id,
        "session_id": session_id or "",
        "actor_id": actor_id or "",
        "tier": tier or "session",
        "content_hash": content_hash,
        "l3_point_id": l3_point_id or "",
        "l4_row_id": l4_row_id or "",
        "created_at": datetime.now(UTC).isoformat(),
        "forge_source": "l5_sovereign_forge",
    }
    # F2 FIX 2026-09-13 (session SEAL-64d8d16afb864e0d): the LLM extractor's
    # episode_properties may echo keys the kernel sets authoritatively —
    # observed live: extractor wrote actor "FI-008" into BOTH session_id and
    # actor_id, overwriting kernel provenance (accept-ep1 dump). Untrusted
    # extraction must never overwrite kernel-set provenance keys.
    # R2 (same session): belief-chain coordinates are kernel-authoritative.
    if lineage and lineage.get("seq") is not None:
        ep_props["seq"] = lineage["seq"]
        ep_props["prev_hash"] = lineage["prev_hash"]
        ep_props["lineage_hash"] = lineage["lineage_hash"]
    _RESERVED_EPISODE_PROPS = frozenset(ep_props)
    ep_props.update(
        {
            k: v
            for k, v in result.episode_properties.items()
            if k not in _RESERVED_EPISODE_PROPS
        }
    )
    prop_str = ", ".join(f"e.{_s(k)} = '{_s(str(v))}'" for k, v in ep_props.items())
    lines.append(f'MERGE (e:Episode {{uuid: "{_s(episode_uuid)}"}})')
    lines.append(f"ON CREATE SET {prop_str}")
    lines.append(f"ON MATCH SET {prop_str}")
    # Reserve the episode variable for the episode name so edge resolution
    # can detect "this is the episode node" without a string compare.
    var_registry[result.episode_name] = "e"

    # Entity nodes
    for ent in result.entities:
        ent_uuid = hashlib.blake2b(
            f"entity:{ent.name}:{ent.type}".encode(), digest_size=16
        ).hexdigest()
        ent_uuid = (
            f"{ent_uuid[:8]}-{ent_uuid[8:12]}-{ent_uuid[12:16]}-{ent_uuid[16:20]}-{ent_uuid[20:32]}"
        )
        var = _resolve_var(ent.name)
        e_props = {
            "uuid": ent_uuid,
            "name": ent.name,
            "type": ent.type,
            "role": ent.role or "",
        }
        e_props.update(ent.properties)
        e_prop_str = ", ".join(f"{var}.{_s(k)} = '{_s(str(v))}'" for k, v in e_props.items())
        lines.append(f'MERGE ({var}:Entity {{uuid: "{_s(ent_uuid)}"}})')
        lines.append(f"ON CREATE SET {e_prop_str}")
        lines.append(f"ON MATCH SET {e_prop_str}")

    # Edges
    for edge_idx, edge in enumerate(result.edges):
        rel = edge.relation
        if not rel.replace("_", "").isalnum() and not rel.isidentifier():
            # F2 guardrail: relation labels in FalkorDB must be valid identifiers.
            # Skip this edge (and log) rather than emit invalid Cypher.
            logger.warning("L5: dropping edge with invalid relation label: %r", rel)
            continue
        # F2 FIX 2026-09-13: unique edge variable per MERGE. Reusing `r` across
        # multiple edges in one statement triggered FalkorDB
        # "The bound variable 'r' can't be redeclared in a MERGE clause"
        # (reproduced in acceptance test A1a: cypher_failed).
        evar = f"rel_{edge_idx}"
        # Resolve source / target through the registry
        if edge.source in var_registry:
            src_node = var_registry[edge.source]
        else:
            # Source not declared as an entity — declare it as an Entity on
            # the fly (defensive: LLM may emit edges whose endpoints are
            # not in the entities list). Use a unique name.
            src_node = _resolve_var(edge.source)
            ent_uuid_seed = f"entity:{edge.source}:Unknown"
            ent_uuid = hashlib.blake2b(ent_uuid_seed.encode(), digest_size=16).hexdigest()
            ent_uuid = f"{ent_uuid[:8]}-{ent_uuid[8:12]}-{ent_uuid[12:16]}-{ent_uuid[16:20]}-{ent_uuid[20:32]}"
            decl_prop = f"{src_node}.uuid = \"{_s(ent_uuid)}\", {src_node}.name = '{_s(edge.source)}', {src_node}.type = 'Unknown', {src_node}.role = 'undeclared_endpoint'"
            lines.append(
                f'MERGE ({src_node}:Entity {{uuid: "{_s(ent_uuid)}"}}) '
                f"ON CREATE SET {decl_prop} ON MATCH SET {decl_prop}"
            )

        if edge.target in var_registry:
            tgt_node = var_registry[edge.target]
        else:
            tgt_node = _resolve_var(edge.target)
            ent_uuid_seed = f"entity:{edge.target}:Unknown"
            ent_uuid = hashlib.blake2b(ent_uuid_seed.encode(), digest_size=16).hexdigest()
            ent_uuid = f"{ent_uuid[:8]}-{ent_uuid[8:12]}-{ent_uuid[12:16]}-{ent_uuid[16:20]}-{ent_uuid[20:32]}"
            decl_prop = f"{tgt_node}.uuid = \"{_s(ent_uuid)}\", {tgt_node}.name = '{_s(edge.target)}', {tgt_node}.type = 'Unknown', {tgt_node}.role = 'undeclared_endpoint'"
            lines.append(
                f'MERGE ({tgt_node}:Entity {{uuid: "{_s(ent_uuid)}"}}) '
                f"ON CREATE SET {decl_prop} ON MATCH SET {decl_prop}"
            )

        edge_prop_str = (
            ", ".join(f"{evar}.{_s(k)} = '{_s(str(v))}'" for k, v in edge.properties.items())
            if edge.properties
            else f"{evar}.forge_ts = timestamp()"
        )
        # R2: every edge remembers which belief-seq asserted it — makes
        # "reconstruct state at seq N" a single filterable traversal.
        if lineage and lineage.get("seq") is not None:
            edge_prop_str += f", {evar}.belief_seq = {lineage['seq']}"
        # R2b (P1 requirement 5): edges carry WHO asserted the relation —
        # provenance on relations, not just on episodes.
        edge_prop_str += (
            f", {evar}.actor_id = '{_s(actor_id or '')}'"
            f", {evar}.session_id = '{_s(session_id or '')}'"
        )
        lines.append(
            f"MERGE ({src_node})-[{evar}:{rel}]->({tgt_node})"
            f" ON CREATE SET {edge_prop_str}"
            f" ON MATCH SET {edge_prop_str}"
        )

    lines.append("RETURN e.uuid AS episode_uuid, count(e) AS episode_count")
    return " ".join(lines)


def _execute_cypher(
    cypher: str, episode_uuid: str, result: ExtractionResult, memory_id: str, content_hash: str
) -> bool:
    """Execute Cypher against the chosen L5 substrate.

    Substrate detection (F1 reversibility, sovereign):
      1. Try FalkorDB first via redis-py GRAPH.QUERY (preferred per contract)
      2. Fall back to Qdrant graph-on-payload (entities as points, relations
         as payload fields). Same wire contract, different substrate.
      3. If both unavailable, defer to 888 (return False; L3/L4 still succeeded).

    The decision is logged once and cached (no re-detection per call).
    """
    global _SUBSTRATE
    if _SUBSTRATE is not None:
        # Already determined — route accordingly
        if _SUBSTRATE == "falkordb":
            return _execute_falkordb(cypher)
        elif _SUBSTRATE == "qdrant":
            return _execute_qdrant_graph(result, episode_uuid, memory_id, content_hash)
        else:
            return False

    # First call: detect substrate
    if _try_falkordb():
        _SUBSTRATE = "falkordb"
        logger.info("L5 substrate: FalkorDB (preferred per contract)")
        return _execute_falkordb(cypher)
    elif _try_qdrant_graph():
        _SUBSTRATE = "qdrant"
        logger.info(
            "L5 substrate: Qdrant (FalkorDB unavailable — fallback to "
            "graph-on-payload collection '%s')",
            _QDRANT_L5_COLLECTION,
        )
        return _execute_qdrant_graph(result, episode_uuid, memory_id, content_hash)
    else:
        _SUBSTRATE = "none"
        logger.warning(
            "L5 substrate: NONE (FalkorDB + Qdrant both unavailable). "
            "Deferring to 888 manual injection."
        )
        return False


def _try_falkordb() -> bool:
    """Check if FalkorDB is reachable at the configured endpoint."""
    try:
        import redis  # noqa: PLC0415

        r = redis.Redis(
            host=_FALKORDB_HOST,
            port=_FALKORDB_PORT,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        r.ping()
        # FalkorDB adds GRAPH.QUERY. Plain Redis does not.
        r.execute_command("GRAPH.QUERY", _FALKORDB_GRAPH, "MATCH (n) RETURN n LIMIT 1")
        return True
    except Exception:
        return False


def _try_qdrant_graph() -> bool:
    """Check if Qdrant is reachable. If yes, ensure the L5 graph collection exists."""
    global _QDRANT_CLIENT
    try:
        from qdrant_client import QdrantClient  # noqa: PLC0415
        from qdrant_client.models import Distance, VectorParams  # noqa: PLC0415

        if _QDRANT_CLIENT is None:
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            _QDRANT_CLIENT = QdrantClient(url=qdrant_url, timeout=5)

        # Ensure the L5 graph collection exists
        existing = {c.name for c in _QDRANT_CLIENT.get_collections().collections}
        if _QDRANT_L5_COLLECTION not in existing:
            _QDRANT_CLIENT.create_collection(
                collection_name=_QDRANT_L5_COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logger.info(
                "Created Qdrant L5 graph collection: %s (384-dim cosine)",
                _QDRANT_L5_COLLECTION,
            )
        return True
    except Exception as exc:
        logger.debug("Qdrant graph substrate unavailable: %s", exc)
        return False


def _execute_falkordb(cypher: str) -> bool:
    """Execute Cypher against FalkorDB via redis-py GRAPH.QUERY."""
    try:
        import redis  # noqa: PLC0415

        r = redis.Redis(
            host=_FALKORDB_HOST,
            port=_FALKORDB_PORT,
            socket_timeout=10,
        )
        result = r.execute_command("GRAPH.QUERY", _FALKORDB_GRAPH, cypher)
        if isinstance(result, list) and len(result) >= 1:
            logger.info(
                "L5 Cypher executed on FalkorDB: %d columns", len(result[0]) if result else 0
            )
            return True
        return False
    except Exception as exc:
        logger.warning("FalkorDB GRAPH.QUERY failed: %s", exc)
        return False


def _execute_qdrant_graph(
    result: ExtractionResult,
    episode_uuid: str,
    memory_id: str,
    content_hash: str,
) -> bool:
    """Store L5 entities + edges in Qdrant as graph-on-payload.

    Schema:
      - Point id = deterministic UUID (matches what FalkorDB would use)
      - Vector = deterministic 384-dim vector (BLAKE2b expanded)
      - Payload = { name, type, role, properties, edges_out, edges_in,
                    episode_uuid, memory_id, content_hash, forge_ts }
    """
    try:
        from qdrant_client.models import PointStruct  # noqa: PLC0415

        if _QDRANT_CLIENT is None:
            return False

        points: list[PointStruct] = []

        # Episode node (anchor for the graph)
        ep_uuid = episode_uuid.replace("-", "")
        ep_vector = _deterministic_vector(ep_uuid, dim=384)
        points.append(
            PointStruct(
                id=ep_uuid,
                vector=ep_vector,
                payload={
                    "kind": "Episode",
                    "name": result.episode_name,
                    "uuid": episode_uuid,
                    "memory_id": memory_id,
                    "content_hash": content_hash,
                    "entity_count": len(result.entities),
                    "edge_count": len(result.edges),
                    "forge_source": "l5_sovereign_forge",
                    "forge_ts": datetime.now(UTC).isoformat(),
                    "edges_out": [
                        e.relation + "→" + e.target
                        for e in result.edges
                        if e.source == result.episode_name
                    ],
                    "edges_in": [
                        e.source + "→" + e.relation
                        for e in result.edges
                        if e.target == result.episode_name
                    ],
                },
            )
        )

        # Entity nodes
        for ent in result.entities:
            ent_uuid_seed = f"entity:{ent.name}:{ent.type}"
            ent_uuid = hashlib.blake2b(ent_uuid_seed.encode(), digest_size=16).hexdigest()
            ent_vector = _deterministic_vector(ent_uuid, dim=384)
            ent_uuid_fmt = f"{ent_uuid[:8]}-{ent_uuid[8:12]}-{ent_uuid[12:16]}-{ent_uuid[16:20]}-{ent_uuid[20:32]}"

            # Find edges touching this entity
            edges_out = [e.relation + "→" + e.target for e in result.edges if e.source == ent.name]
            edges_in = [e.source + "→" + e.relation for e in result.edges if e.target == ent.name]

            points.append(
                PointStruct(
                    id=ent_uuid,
                    vector=ent_vector,
                    payload={
                        "kind": "Entity",
                        "name": ent.name,
                        "type": ent.type,
                        "role": ent.role or "",
                        "uuid": ent_uuid_fmt,
                        "properties": ent.properties,
                        "edges_out": edges_out,
                        "edges_in": edges_in,
                        "episode_uuid": episode_uuid,
                        "memory_id": memory_id,
                        "forge_ts": datetime.now(UTC).isoformat(),
                    },
                )
            )

        _QDRANT_CLIENT.upsert(
            collection_name=_QDRANT_L5_COLLECTION,
            points=points,
        )
        logger.info(
            "L5 graph-on-Qdrant upsert: %d points (1 Episode + %d Entity)",
            len(points),
            len(result.entities),
        )
        return True
    except Exception as exc:
        logger.warning("Qdrant graph substrate failed: %s", exc)
        return False


def _deterministic_vector(seed: str, dim: int = 384) -> list[float]:
    """Build a deterministic unit vector from a string seed.

    Uses BLAKE2b in counter mode so the same seed always produces the same
    vector. Not semantically meaningful (we're not embedding), but stable for
    graph-on-payload storage where vector similarity isn't the query pattern.

    CRITICAL: struct.unpack('f') from random hash bytes can produce NaN/Inf,
    which Qdrant rejects. We map each byte pair to a finite float in [-1,1]
    via integer division, guaranteeing no NaN/Inf.
    """
    raw = bytearray()
    counter = 0
    while len(raw) < dim * 2:
        raw.extend(hashlib.blake2b(f"{seed}:{counter}".encode(), digest_size=32).digest())
        counter += 1

    # Map each pair of bytes to a float in [-1, 1] using signed 16-bit int.
    # This guarantees finite values — no NaN, no Inf.
    vals = []
    for i in range(dim):
        b1, b2 = raw[i * 2], raw[i * 2 + 1]
        signed = (b1 << 8) | b2
        if signed > 32767:
            signed -= 65536
        vals.append(signed / 32768.0)

    norm = sum(v * v for v in vals) ** 0.5
    if norm == 0:
        norm = 1.0
    return [v / norm for v in vals]


_GENESIS = "0" * 64


def _allocate_lineage(content_hash: str) -> dict[str, Any]:
    """R2 (2026-09-13, session SEAL-64d8d16afb864e0d): belief-chain position.

    seq          := INCR on a FalkorDB redis key (monotonic per graph)
    prev_hash    := lineage_hash of the current chain tip (GENESIS if none)
    lineage_hash := blake2b(prev_hash ':' content_hash)

    Single-writer v1: concurrent forges may read the same tip and fork the
    chain — that fork is DETECTABLE (two episodes sharing prev_hash) and is
    exactly the anomaly class the contradiction membrane (R4) will adjudicate.
    Forks are visible, never silent. Allocation failure returns Nones
    (declared absent, not faked) — the episode still forges, unchained.
    """
    try:
        import redis as _redis

        r = _redis.Redis(
            host=_FALKORDB_HOST,
            port=_FALKORDB_PORT,
            socket_connect_timeout=2,
            socket_timeout=3,
        )
        seq = int(r.incr(f"l5:{_FALKORDB_GRAPH}:seq"))
        tip = r.execute_command(
            "GRAPH.RO_QUERY",
            _FALKORDB_GRAPH,
            "MATCH (e:Episode) WHERE e.lineage_hash IS NOT NULL "
            "RETURN e.lineage_hash ORDER BY toInteger(e.seq) DESC LIMIT 1",
        )
        prev = _GENESIS
        node = tip[1] if isinstance(tip, (list, tuple)) and len(tip) > 1 else None
        while isinstance(node, (list, tuple)):
            if not node:
                break
            node = node[0]
        if node:
            prev = node.decode() if isinstance(node, bytes) else str(node)
        lineage = hashlib.blake2b(f"{prev}:{content_hash}".encode(), digest_size=32).hexdigest()
        return {"seq": seq, "prev_hash": prev, "lineage_hash": lineage}
    except Exception as exc:
        logger.warning("L5 lineage allocation failed (episode forges unchained): %s", exc)
        return {"seq": None, "prev_hash": None, "lineage_hash": None}


# ── Public API ─────────────────────────────────────────────────────────────


def forge_l5(
    *,
    memory_id: str,
    content: str,
    summary: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    tier: str | None = None,
    tags: list[str] | None = None,
    l3_point_id: str | None = None,
    l4_row_id: str | None = None,
    content_hash: str | None = None,
) -> dict[str, Any]:
    """Sovereign L5 forge — Ollama → Pydantic → Cypher → FalkorDB.

    Fire-and-forget. NEVER raises. Returns status dict.
    """
    if not _L5_ENABLED:
        return {"federation_leg": "L5", "status": "disabled", "memory_id": memory_id}

    if not content:
        return {"federation_leg": "L5", "status": "skipped", "reason": "empty_content"}

    start_ts = time.time()
    _content_hash = content_hash or hashlib.blake2b(content.encode(), digest_size=16).hexdigest()

    # 1. Deterministic UUID (F1 idempotency — memory lineage, not wall clock)
    episode_uuid = _generate_deterministic_uuid(
        actor_id=actor_id,
        session_id=session_id,
        memory_id=memory_id,
        content_hash=_content_hash,
    )

    # 1b. F1 short-circuit: if this episode already exists, do NOT re-run the
    # Ollama extraction (saves ~50s and guarantees zero replay duplicates —
    # extraction variance can never fork the episode node).
    if _episode_exists(episode_uuid):
        return {
            "federation_leg": "L5",
            "status": "already_forged",
            "memory_id": memory_id,
            "episode_uuid": episode_uuid,
            "elapsed_ms": round((time.time() - start_ts) * 1000, 2),
        }

    # 1c. R2 belief-chain position — allocated only for genuinely new beliefs
    # (replays short-circuit above and never consume a seq).
    lineage = _allocate_lineage(_content_hash)

    # 2. LLM extraction (F2 truth guardrails)
    extraction = _call_ollama_extract(content)
    if extraction is None:
        return {
            "federation_leg": "L5",
            "status": "extraction_failed",
            "reason": "ollama_validation_failed_after_retries",
            "memory_id": memory_id,
            "episode_uuid": episode_uuid,
        }

    # 3. Cypher generation (F1 MERGE idempotency)
    cypher = _build_cypher(
        result=extraction,
        episode_uuid=episode_uuid,
        memory_id=memory_id,
        session_id=session_id,
        actor_id=actor_id,
        tier=tier,
        content_hash=_content_hash,
        l3_point_id=l3_point_id,
        l4_row_id=l4_row_id,
        lineage=lineage,
    )

    # 4. FalkorDB injection
    ok = _execute_cypher(
        cypher,
        episode_uuid=episode_uuid,
        result=extraction,
        memory_id=memory_id,
        content_hash=_content_hash,
    )
    elapsed_ms = round((time.time() - start_ts) * 1000, 2)

    return {
        "lineage": lineage,
        "federation_leg": "L5",
        "status": "forged" if ok else "cypher_failed",
        "memory_id": memory_id,
        "episode_uuid": episode_uuid,
        "episode_name": extraction.episode_name,
        "entity_count": len(extraction.entities),
        "edge_count": len(extraction.edges),
        "elapsed_ms": elapsed_ms,
    }


# ── Back-compat alias (drop-in replacement for l5_graphiti_bridge) ─────────


def bridge_forge_episode(
    *,
    memory_id: str,
    content: str,
    summary: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    tier: str | None = None,
    tags: list[str] | None = None,
    l3_point_id: str | None = None,
    l4_row_id: str | None = None,
    phoenix_id: str | None = None,
    entity_tags: list[str] | None = None,
    phoenix_state: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Backwards-compatible wrapper that delegates to forge_l5.

    Allows memory_store.py to switch imports without code changes.
    """
    # Build a rich content block from all available metadata
    rich_content = content or summary or ""
    if entity_tags:
        rich_content += f"\n[entity_tags: {', '.join(entity_tags)}]"
    if phoenix_state:
        rich_content += f"\n[phoenix_state: {phoenix_state}]"

    return forge_l5(
        memory_id=memory_id,
        content=rich_content,
        summary=summary,
        session_id=session_id,
        actor_id=actor_id,
        tier=tier,
        tags=tags,
        l3_point_id=l3_point_id,
        l4_row_id=l4_row_id,
    )


def bridge_search(
    query: str,
    *,
    group_ids: list[str] | None = None,
    max_nodes: int = 10,
) -> dict[str, Any]:
    """Search L5 graph via raw Cypher. Drop-in replacement for Graphiti search."""
    try:
        import subprocess  # noqa: S404

        # Simple keyword search across Episode + Entity names
        cypher = (
            f'MATCH (n) WHERE n.name CONTAINS "{query.replace('"', '\\"')}" '
            f"RETURN n.name AS name, labels(n)[0] AS type, n.uuid AS uuid "
            f"LIMIT {max_nodes}"
        )
        cmd = [
            "docker",
            "exec",
            "falkordb",
            "redis-cli",
            "-p",
            "6379",
            "GRAPH.QUERY",
            _FALKORDB_GRAPH,
            cypher,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {
            "status": "ok" if result.returncode == 0 else "degraded",
            "raw": result.stdout[:800],
            "query": query,
        }
    except Exception as exc:
        return {"status": "skipped", "reason": f"{type(exc).__name__}: {exc}"}


# ── Async Wrapper (sovereign non-blocking) ─────────────────────────────────
# When L5_SOVEREIGN_ASYNC=true, forge_l5 schedules the extraction in a
# background thread and returns immediately. The store() caller does NOT
# wait for qwen2.5:7b cold start (~120s on CPU) or LLM inference.
# This keeps the L3/L4 fast path responsive.

import threading  # noqa: E402


def _run_in_thread(target, *args, **kwargs):
    """Schedule target in a daemon thread. Returns the thread handle."""
    t = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t


def forge_l5_async(
    *,
    memory_id: str,
    content: str,
    summary: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    tier: str | None = None,
    tags: list[str] | None = None,
    l3_point_id: str | None = None,
    l4_row_id: str | None = None,
    content_hash: str | None = None,
) -> dict[str, Any]:
    """Async L5 forge — schedules extraction in background thread.

    Returns immediately with status='queued'. The actual L5 result lands
    in the substrate a few seconds (or minutes on cold start) later.
    Use forge_l5() for the synchronous variant (debugging only).
    """
    if not _L5_ASYNC:
        return forge_l5(
            memory_id=memory_id,
            content=content,
            summary=summary,
            session_id=session_id,
            actor_id=actor_id,
            tier=tier,
            tags=tags,
            l3_point_id=l3_point_id,
            l4_row_id=l4_row_id,
            content_hash=content_hash,
        )

    def _worker():
        try:
            result = forge_l5(
                memory_id=memory_id,
                content=content,
                summary=summary,
                session_id=session_id,
                actor_id=actor_id,
                tier=tier,
                tags=tags,
                l3_point_id=l3_point_id,
                l4_row_id=l4_row_id,
                content_hash=content_hash,
            )
            _persist_l5_status(memory_id, result)
        except Exception as exc:
            logger.warning("L5 async worker failed for %s: %s", memory_id, exc)
            _persist_l5_status(memory_id, {"status": f"error:{type(exc).__name__}"})

    _run_in_thread(_worker)
    return {
        "federation_leg": "L5",
        "status": "queued_async",
        "memory_id": memory_id,
        "mode": "background_thread",
    }


def _persist_l5_status(memory_id: str, result: dict[str, Any] | None) -> None:
    """F2 loudness (2026-09-13): persist the FINAL L5 forge outcome into the
    memory JSON index so inspect/audit can see L5_SKIPPED / L5 errors instead
    of a permanent 'queued_async'. Fire-and-forget is fine; silent is not.

    Lazy import of memory_store (never at module load) avoids an import cycle:
    memory_store calls forge_l5_async from inside store(), not at import time.
    """
    if not memory_id:
        return
    status = result.get("status", "unknown") if isinstance(result, dict) else "unknown"
    reason = result.get("reason") if isinstance(result, dict) else None
    try:
        from arifosmcp.runtime import memory_store as _ms

        idx = _ms._index_read()
        entry = idx.get(memory_id)
        if entry is not None:
            entry["l5_status"] = status
            if reason:
                entry["l5_reason"] = reason
            entry["l5_finalized_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            _ms._index_write(idx)
            logger.info("L5 final status persisted for %s: %s", memory_id, status)
    except Exception as exc:
        # Persistence is best-effort; the log line below is the floor guarantee.
        logger.warning(
            "L5 final status=%s (reason=%s) for memory %s — index persist failed: %s",
            status,
            reason,
            memory_id,
            exc,
        )
