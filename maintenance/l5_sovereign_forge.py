#!/usr/bin/env python3
"""
l5_sovereign_forge.py — Native L5 Knowledge Graph Ingestion
============================================================
Bypasses Graphiti entirely. Uses local Ollama (qwen2.5:7b) for entity
extraction, Pydantic validation with T=0 retry, and direct Cypher MERGE
into FalkorDB via deterministic UUIDs.

Architecture:
  Session text → Ollama qwen2.5:7b (T=0, structured JSON)
              → Pydantic KnowledgeGraph validation
              → Retry on validation failure
              → Cypher MERGE into FalkorDB (uuid5 deterministic)

Idempotency:   uuid.uuid5(UUID.NAMESPACE_DNS, entity_name) ensures
               the same entity name always maps to the same node UUID.
               MERGE (not CREATE) prevents duplicates.

F1 Reversibility: Dry-run mode, MERGE-only (no DELETE), idempotent UUIDs.

Usage:
  python3 l5_sovereign_forge.py                        # Process session dump
  python3 l5_sovereign_forge.py --text "arifOS runs on..."  # Single text
  python3 l5_sovereign_forge.py --dry-run              # Preview only
  python3 l5_sovereign_forge.py --source redis         # Read from Redis sessions

Author: Omega (arifOS Forge Agent), corrected per 888 SOVEREIGN OVERRIDE
Sovereign: Muhammad Arif bin Fazil (F13)
Motto: DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import requests
from pydantic import BaseModel, ValidationError

# ── CONFIG ──────────────────────────────────────────────────
# Primary: SEA-LION (27B-70B, free tier, SEA-focused, 10 RPM)
SEA_LION_API_KEY = os.environ.get("SEA_LION_API_KEY", "")
SEA_LION_BASE_URL = os.environ.get("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
SEA_LION_MODEL = "aisingapore/Gemma-SEA-LION-v4-27B-IT"

# Fallback: ILMU (free tier, nano model, fast)
ILMU_API_KEY = os.environ.get("ILMU_API_KEY", "")
ILMU_BASE_URL = os.environ.get("ILMU_BASE_URL", "https://api.ilmu.ai/v1")
ILMU_MODEL = "ilmu-nemo-nano"
FALKORDB_HOST = "localhost"
FALKORDB_PORT = 6380  # FalkorDB exposed on 6380
FALKORDB_GRAPH = "arif_l5_knowledge"
MAX_RETRIES = 3  # T=0 retry loop
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

# ── PYDANTIC SCHEMAS ────────────────────────────────────────


class Entity(BaseModel):
    name: str
    label: str  # e.g., "Person", "Organ", "Service", "Concept", "Event"


class Relationship(BaseModel):
    source_entity: str
    target_entity: str
    relation_type: str  # e.g., "OWNS", "DEPENDS_ON", "EXECUTES", "GOVERNS"


class KnowledgeGraph(BaseModel):
    entities: list[Entity]
    relationships: list[Relationship]


# ── UTILITIES ────────────────────────────────────────────────


def deterministic_uuid(name: str) -> str:
    """uuid5 ensures same name → same UUID every time. F1 idempotency."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))


def falkordb_query(cypher: str) -> list:
    """Execute Cypher query against FalkorDB via Docker exec + redis-cli."""
    # Escape single quotes in Cypher
    safe_cypher = cypher.replace("'", "'\"'\"'")
    cmd = [
        "docker",
        "exec",
        "falkordb",
        "redis-cli",
        "-p",
        "6379",
        "GRAPH.QUERY",
        FALKORDB_GRAPH,
        cypher,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ❌ FalkorDB error: {result.stderr.strip()}", file=sys.stderr)
            return []
        return _parse_falkordb_output(result.stdout)
    except subprocess.TimeoutExpired:
        print(f"  ❌ FalkorDB timeout", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  ❌ FalkorDB error: {e}", file=sys.stderr)
        return []


def _parse_falkordb_output(raw: str) -> list:
    """Parse FalkorDB redis-cli table output to list of dicts."""
    lines = raw.strip().split("\n")
    if len(lines) < 2:
        return []
    # First line is header, rest are data
    headers = [h.strip() for h in lines[0].split(",")]
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        values = [v.strip() for v in line.split(",")]
        if len(values) == len(headers):
            rows.append(dict(zip(headers, values)))
    return rows


def _call_llm_api(
    api_url: str, api_key: str, model: str, prompt: str, timeout: int = 30
) -> Optional[str]:
    """Generic OpenAI-compatible API call. Returns response content or None."""
    resp = requests.post(
        f"{api_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a knowledge graph extraction engine. Output ONLY valid JSON. No markdown, no explanation.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": 1000,
            "response_format": {"type": "json_object"},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


def extract_kg(text: str) -> Optional[KnowledgeGraph]:
    """Extract knowledge graph using SEA-LION primary, ILMU fallback.
    Both are OpenAI-compatible, free tier, no Ollama dependency."""
    prompt = f"""Extract all entities and relationships from this text as a knowledge graph.

Return ONLY valid JSON matching this exact schema:
{{
  "entities": [
    {{"name": "Entity Name", "label": "Person|Organ|Service|Concept|Event|Document|Tool|Repository|Infrastructure|Data_Product|Metric|Domain|Decision"}}
  ],
  "relationships": [
    {{"source_entity": "Entity A", "target_entity": "Entity B", "relation_type": "RUNS_ON|COMPUTES|CALCULATES|SEALS|GOVERNS|DEPENDS_ON|APPLIES_TO|ARCHITECT_OF|MONITORS|OWNS|WRITES_TO|READS_FROM"}}
  ]
}}

Rules:
- Entity names must be unique and descriptive (e.g., "arifOS MCP Server" not "server")
- Only extract entities that are explicitly mentioned
- relation_type must be a short verb phrase in UPPER_SNAKE_CASE
- If no relationships exist, return empty arrays

TEXT TO ANALYZE:
{text[:4000]}"""

    # Providers in priority order
    providers = []
    if SEA_LION_API_KEY:
        providers.append(("SEA-LION", SEA_LION_BASE_URL, SEA_LION_API_KEY, SEA_LION_MODEL, 45))
    if ILMU_API_KEY:
        providers.append(("ILMU", ILMU_BASE_URL, ILMU_API_KEY, ILMU_MODEL, 30))

    if not providers:
        print(f"  ❌ No LLM API keys configured (SEA_LION or ILMU)", file=sys.stderr)
        return None

    for provider_name, url, key, model, timeout in providers:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                content = _call_llm_api(url, key, model, prompt, timeout=timeout)
                if not content:
                    print(
                        f"  ⚠️  {provider_name} attempt {attempt}: empty response", file=sys.stderr
                    )
                    if attempt < MAX_RETRIES:
                        time.sleep(1)
                    continue

                raw = json.loads(content)
                kg = KnowledgeGraph.model_validate(raw)
                print(
                    f"  ✅ {provider_name}/{model} — {len(kg.entities)} entities, {len(kg.relationships)} rels",
                    file=sys.stderr,
                )
                return kg

            except (json.JSONDecodeError, ValidationError) as e:
                print(
                    f"  ⚠️  {provider_name} attempt {attempt}/{MAX_RETRIES}: {type(e).__name__}",
                    file=sys.stderr,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(1)
            except requests.exceptions.Timeout:
                print(
                    f"  ⚠️  {provider_name} attempt {attempt}: timeout ({timeout}s)", file=sys.stderr
                )
                if attempt < MAX_RETRIES:
                    time.sleep(2)
            except Exception as e:
                print(f"  ❌ {provider_name} error (attempt {attempt}): {e}", file=sys.stderr)
                break  # Don't retry hard errors, try next provider

        print(f"  ⚠️  {provider_name} failed all attempts, trying next provider...", file=sys.stderr)

    print(f"  ❌ All providers exhausted", file=sys.stderr)
    return None


def merge_entities(kg: KnowledgeGraph, dry_run: bool = False) -> dict:
    """Merge entities and relationships into FalkorDB via Cypher."""
    stats = {"nodes_created": 0, "edges_created": 0, "nodes_existing": 0, "edges_existing": 0}

    for entity in kg.entities:
        node_uuid = deterministic_uuid(entity.name)
        safe_name = entity.name.replace("'", "''")
        safe_label = entity.label.replace("'", "''")
        cypher = (
            f"MERGE (n:{safe_label} {{id: '{node_uuid}'}}) "
            f"ON CREATE SET n.name = '{safe_name}', n.created_at = timestamp() "
            f"ON MATCH SET n.updated_at = timestamp() "
            f"RETURN n.id, n.name"
        )

        if dry_run:
            print(f"  🔍 [DRY] MERGE node: {entity.label}('{entity.name}')", file=sys.stderr)
            stats["nodes_created"] += 1
        else:
            result = falkordb_query(cypher)
            if result:
                stats["nodes_created"] += 1 if len(result) > 0 else 0

    for rel in kg.relationships:
        source_uuid = deterministic_uuid(rel.source_entity)
        target_uuid = deterministic_uuid(rel.target_entity)
        safe_rel = rel.relation_type.replace("'", "''")
        cypher = (
            f"MATCH (a {{id: '{source_uuid}'}}) "
            f"MATCH (b {{id: '{target_uuid}'}}) "
            f"MERGE (a)-[r:{safe_rel}]->(b) "
            f"ON CREATE SET r.created_at = timestamp() "
            f"RETURN type(r)"
        )

        if dry_run:
            print(
                f"  🔍 [DRY] MERGE edge: {rel.source_entity} -[{rel.relation_type}]-> {rel.target_entity}",
                file=sys.stderr,
            )
            stats["edges_created"] += 1
        else:
            result = falkordb_query(cypher)
            if result:
                stats["edges_created"] += 1

    return stats


def read_redis_sessions() -> list[str]:
    """Read session texts from Redis (federation:hermes:session_telemetry)."""
    key = "federation:hermes:session_telemetry"
    try:
        cmd = [
            "docker",
            "exec",
            "redis",
            "redis-cli",
            "-a",
            REDIS_PASSWORD,
            "--no-auth-warning",
            "GET",
            key,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            # Return as single text blob for now
            return [json.dumps(data)]
    except Exception as e:
        print(f"  ⚠️  Redis read failed: {e}", file=sys.stderr)
    return []


def read_session_files() -> list[str]:
    """Read recent Hermes session summaries from disk."""
    texts = []
    session_dir = "/root/HERMES/sessions"
    if not os.path.isdir(session_dir):
        # Try archive
        archive_dir = "/root/HERMES/sessions_archive_2026-06-02"
        if os.path.isdir(archive_dir):
            session_dir = archive_dir

    if os.path.isdir(session_dir):
        files = sorted(
            [f for f in os.listdir(session_dir) if f.endswith(".json")],
            reverse=True,
        )[:5]  # Last 5 sessions
        for fname in files:
            try:
                with open(os.path.join(session_dir, fname)) as f:
                    data = json.load(f)
                # Extract meaningful text
                messages = data.get("messages", [])
                text = " ".join(
                    m.get("content", "")[:500]
                    for m in messages
                    if isinstance(m.get("content"), str)
                )
                if text.strip():
                    texts.append(text)
            except Exception:
                continue
    return texts


def ingest(
    dry_run: bool = False,
    text: Optional[str] = None,
    source: str = "session_files",
) -> dict:
    """Main ingestion loop."""
    t0 = time.time()

    print(f"═══ L5 SOVEREIGN FORGE START ═══", file=sys.stderr)
    primary = "SEA-LION" if SEA_LION_API_KEY else "ILMU" if ILMU_API_KEY else "none"
    print(f"  LLM:      primary={primary}", file=sys.stderr)
    print(f"  FalkorDB: {FALKORDB_HOST}:{FALKORDB_PORT}/{FALKORDB_GRAPH}", file=sys.stderr)
    print(f"  Dry-run:  {dry_run}", file=sys.stderr)

    # Gather texts
    texts: list[str] = []
    if text:
        texts = [text]
    elif source == "redis":
        texts = read_redis_sessions()
    else:
        texts = read_session_files()

    if not texts:
        print(f"  ⚠️  No texts found (source={source})", file=sys.stderr)
        return {"error": "no_texts", "source": source}

    print(f"  📄 Processing {len(texts)} text chunks", file=sys.stderr)

    # Verify FalkorDB is reachable
    if not dry_run:
        ping = falkordb_query("MATCH (n) RETURN count(n) as node_count")
        if not ping:
            print(f"  ❌ FalkorDB unreachable", file=sys.stderr)
            return {"error": "falkordb_unreachable"}

    # Process each text
    total_stats = {"nodes_created": 0, "edges_created": 0, "chunks": 0, "failures": 0}

    for i, chunk in enumerate(texts):
        print(f"  🧠 Chunk {i + 1}/{len(texts)} ({len(chunk)} chars)", file=sys.stderr)
        kg = extract_kg(chunk)
        if kg is None:
            total_stats["failures"] += 1
            continue

        print(
            f"     Entities: {len(kg.entities)}, Relationships: {len(kg.relationships)}",
            file=sys.stderr,
        )

        stats = merge_entities(kg, dry_run=dry_run)
        total_stats["nodes_created"] += stats["nodes_created"]
        total_stats["edges_created"] += stats["edges_created"]
        total_stats["chunks"] += 1

    elapsed = time.time() - t0

    # Final graph state
    if not dry_run:
        count_result = falkordb_query("MATCH (n) RETURN count(n) as node_count")
        node_count = count_result[0].get("node_count", "?") if count_result else "?"
    else:
        node_count = "N/A (dry-run)"

    summary = {
        "chunks_processed": total_stats["chunks"],
        "chunks_failed": total_stats["failures"],
        "nodes_created": total_stats["nodes_created"],
        "edges_created": total_stats["edges_created"],
        "graph_nodes_total": node_count,
        "dry_run": dry_run,
        "elapsed_seconds": round(elapsed, 1),
    }

    print(f"═══ L5 SOVEREIGN FORGE DONE ═══", file=sys.stderr)
    print(
        f"  Chunks:   {total_stats['chunks']} ok / {total_stats['failures']} fail", file=sys.stderr
    )
    print(f"  Nodes:    +{total_stats['nodes_created']}", file=sys.stderr)
    print(f"  Edges:    +{total_stats['edges_created']}", file=sys.stderr)
    print(f"  Graph:    {node_count} total nodes", file=sys.stderr)
    print(f"  Time:     {elapsed:.1f}s", file=sys.stderr)

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="L5 Sovereign Forge — Native FalkorDB ingestion")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--text", type=str, default=None, help="Single text to process")
    parser.add_argument(
        "--source",
        type=str,
        default="session_files",
        choices=["session_files", "redis"],
        help="Where to read texts from",
    )
    args = parser.parse_args()

    result = ingest(dry_run=args.dry_run, text=args.text, source=args.source)
    print(json.dumps(result, indent=2))
