#!/usr/bin/env python3
"""Seed Qdrant mcp_capabilities collection from AAA CAPABILITY_INDEX.json.

Embeds 106 tool descriptors via Ollama bge-m3 (1024-dim, Cosine).
Idempotent — each tool's UUID is SHA-256 of its name+server.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import requests

QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION = "mcp_capabilities"
OLLAMA_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "bge-m3:latest"
DIM = 1024

INDEX_PATH = Path("/root/AAA/registries/CAPABILITY_INDEX.json")

def embed_batch(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for i, t in enumerate(texts):
        if i > 0 and i % 10 == 0:
            print(f"  embedded {i}/{len(texts)}...")
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/embed",
                json={"model": EMBED_MODEL, "input": t},
                timeout=30,
            )
            r.raise_for_status()
            embeddings.append(r.json()["embeddings"][0])
        except Exception as exc:
            print(f"  WARN: failed #{i} — {exc}")
            embeddings.append([0.0] * DIM)
    return embeddings

def tool_descriptor(t: dict) -> str:
    tid = t.get("id") or t.get("name", "unknown")
    return "; ".join([
        f"Tool: {tid}",
        f"Server: {t['server']}",
        f"Description: {t.get('description', '')}",
        f"Tags: {', '.join(t.get('tags', []))}",
        f"Risk: {t.get('risk_tier', 'unknown')}",
        f"Epistemic: {t.get('epistemic_tag', 'unknown')}",
        f"Kind: {t.get('execution_kind', 'unknown')}",
        f"Approval: {t.get('approval_policy', 'unknown')}",
    ])

def tool_uuid(t: dict) -> str:
    tid = t.get("id") or t.get("name", "unknown")
    h = hashlib.sha256(f"{tid}::{t['server']}".encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

def main():
    if not INDEX_PATH.exists():
        print(f"ERROR: {INDEX_PATH} not found")
        sys.exit(1)

    data = json.loads(INDEX_PATH.read_text())
    tools = data.get("tools", [])
    print(f"Loading {len(tools)} tools from {INDEX_PATH}")

    # Recreate collection with correct dims
    print(f"Recreating Qdrant collection: {COLLECTION} ({DIM}-dim, Cosine)")
    requests.delete(f"{QDRANT_URL}/collections/{COLLECTION}")
    r = requests.put(f"{QDRANT_URL}/collections/{COLLECTION}", json={
        "vectors": {"size": DIM, "distance": "Cosine"}
    })
    if r.status_code != 200:
        print(f"ERROR creating collection: {r.text}")
        sys.exit(1)

    # Embed
    print(f"Embedding {len(tools)} tool descriptors via {EMBED_MODEL}...")
    descriptors = [tool_descriptor(t) for t in tools]
    embeddings = embed_batch(descriptors)

    # Build points
    total_miss = sum(1 for e in embeddings if all(v == 0.0 for v in e))
    if total_miss > 0:
        print(f"WARNING: {total_miss} embeddings failed (zero vectors). Continuing with rest.")

    points = []
    for tool, emb in zip(tools, embeddings):
        tid = tool.get("id") or tool.get("name", "unknown")
        points.append({
            "id": tool_uuid(tool),
            "vector": emb,
            "payload": {
                "tool_id": tid,
                "name": tool.get("name", tid),
                "server": tool["server"],
                "description": tool.get("description", ""),
                "tags": tool.get("tags", []),
                "risk_tier": tool.get("risk_tier", "medium"),
                "epistemic_tag": tool.get("epistemic_tag", "ESTIMATE"),
                "execution_kind": tool.get("execution_kind", "read"),
                "approval_policy": tool.get("approval_policy", "auto"),
                "requires_888": tool.get("requires_888", False),
            },
        })

    # Batch upsert in chunks of 50
    print(f"Upserting {len(points)} vectors to Qdrant...")
    chunk_size = 50
    for i in range(0, len(points), chunk_size):
        chunk = points[i:i + chunk_size]
        r = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=true",
            json={"points": chunk},
            timeout=30,
        )
        if r.status_code != 200:
            print(f"  ERROR chunk {i}: {r.text[:200]}")
        else:
            print(f"  chunk {i}-{i+len(chunk)-1}: OK")

    # Verify
    time.sleep(1)
    r = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}")
    info = r.json()
    count = info["result"].get("points_count",
                               info["result"].get("vectors_count", 0))
    print(f"\nQdrant collection: {count} points")
    if count == len(tools):
        print("PASS — all 106 tools indexed")
    elif count > 0:
        print(f"PARTIAL — {count}/{len(tools)} tools indexed")
    else:
        print("FAIL — 0 points. Check collection creation.")

    # Semantic search smoke test
    print("\nSmoke test: searching for 'memory recall session context'...")
    r = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": "memory recall session context"},
        timeout=30,
    )
    query_vec = r.json()["embeddings"][0]
    r = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        json={"vector": query_vec, "limit": 5, "with_payload": True},
        timeout=10,
    )
    results = r.json().get("result", [])
    for i, hit in enumerate(results):
        p = hit.get("payload", {})
        print(f"  {i+1}. {p.get('name','?')} ({p.get('server','?')}) — score: {hit.get('score',0):.4f}")


if __name__ == "__main__":
    start = time.monotonic()
    main()
    print(f"\nDone in {time.monotonic() - start:.1f}s")
