#!/usr/bin/env python3
"""Seed Qdrant mcp_capabilities collection from AAA CAPABILITY_INDEX.json.

Embeds 106 tool descriptors via Ollama bge-m3 (1024-dim, Cosine).
Idempotent — each tool's UUID is SHA-256 of its id+server.
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

INDEX_PATH = Path("/root/AAA/registries/CAPABILITY_INDEX.json")


def embed(text: str) -> list[float]:
    r = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=30,
    )
    r.raise_for_status()
    emb = r.json()["embeddings"][0]
    return emb


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Process one at a time to respect Ollama memory."""
    embeddings = []
    for i, t in enumerate(texts):
        if i > 0 and i % 10 == 0:
            print(f"  embedded {i}/{len(texts)}...")
        try:
            embeddings.append(embed(t))
        except Exception as exc:
            print(f"  WARN: failed {texts[i][:60]}… — {exc}")
            embeddings.append([0.0] * 1024)
    return embeddings


def tool_descriptor(t: dict) -> str:
    """Rich text for semantic embedding."""
    tid = t.get("id") or t.get("name", "unknown")
    parts = [
        f"Tool: {tid}",
        f"Server: {t['server']}",
        f"Description: {t.get('description', '')}",
        f"Tags: {', '.join(t.get('tags', []))}",
        f"Risk: {t.get('risk_tier', 'unknown')}",
        f"Epistemic: {t.get('epistemic_tag', 'unknown')}",
        f"Kind: {t.get('execution_kind', 'unknown')}",
        f"Approval: {t.get('approval_policy', 'unknown')}",
    ]
    return "; ".join(parts)


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

    print("Embedding tool descriptors via bge-m3...")
    descriptors = [tool_descriptor(t) for t in tools]
    embeddings = embed_batch(descriptors)

    print(f"Upserting {len(embeddings)} vectors to Qdrant...")
    points = []
    for tool, emb in zip(tools, embeddings):
        uid = tool_uuid(tool)
        points.append(
            {
                "id": uid,
                "vector": emb,
                "payload": {
                    "tool_id": tool.get("id", tool.get("name", "unknown")),
                    "name": tool.get("name", tool.get("id", "unknown")),
                    "server": tool["server"],
                    "description": tool.get("description", ""),
                    "tags": tool.get("tags", []),
                    "risk_tier": tool.get("risk_tier", "medium"),
                    "epistemic_tag": tool.get("epistemic_tag", "ESTIMATE"),
                    "execution_kind": tool.get("execution_kind", "read"),
                    "approval_policy": tool.get("approval_policy", "auto"),
                    "requires_888": tool.get("requires_888", False),
                },
            }
        )

    r = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points",
        json={"points": points},
        timeout=30,
    )
    r.raise_for_status()
    result = r.json()
    print(f"Upserted: {result.get('result', {}).get('operation_id', 'ok')}")

    # Verify
    r2 = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}")
    info = r2.json()
    count = info.get("result", {}).get("vectors_count", 0)
    print(f"Collection vectors: {count}")
    if count == len(tools):
        print("PASS — all 106 tools indexed")
    else:
        print(f"WARN — expected {len(tools)}, got {count}")


if __name__ == "__main__":
    start = time.monotonic()
    main()
    elapsed = time.monotonic() - start
    print(f"Done in {elapsed:.1f}s")
