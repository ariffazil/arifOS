#!/usr/bin/env python3
"""
Migrate arifOS embeddings from BGE-small (384-dim) to BGE-M3 (1024-dim).

This script:
1. Re-creates arifos_constitutional collection at 1024-dim
2. Re-embeds all 7,706 constitutional documents
3. Creates vault_precedent_memory collection at 1024-dim

F2 Truth + F6 Empathy: Enables Malay, English, and Manglish precedent retrieval.

Usage:
    python scripts/migrate_to_bge_m3.py

Requires:
    - Qdrant running at QDRANT_URL (default: http://localhost:6333)
    - BGE-M3 model downloaded (~570MB)
"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Try to import required packages
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Error: Missing dependency {e}")
    print("Install with: pip install qdrant-client sentence-transformers")
    sys.exit(1)

# Configuration
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
OLD_DIM = 384
NEW_DIM = 1024
OLD_MODEL = "BAAI/bge-small-en-v1.5"
NEW_MODEL = "BAAI/bge-m3"

# Collection names
CONSTITUTIONAL_COLLECTION = "arifos_constitutional"
PRECEDENT_COLLECTION = "vault_precedent_memory"

# Path to constitutional docs
DOCS_PATH = Path("000_THEORY")


def load_bge_m3() -> SentenceTransformer:
    """Load BGE-M3 model (570MB download on first run)."""
    print(f"Loading {NEW_MODEL}...")
    print("  (First run: downloading ~570MB model)")
    model = SentenceTransformer(NEW_MODEL)
    print(f"  ✓ Loaded: {NEW_DIM} dimensions, multilingual support")
    return model


def recreate_collection(client: QdrantClient, name: str, dim: int) -> bool:
    """Delete and recreate collection at new dimension."""
    print(f"\nRecreating collection: {name}")

    # Check if exists
    collections = client.get_collections().collections
    exists = any(c.name == name for c in collections)

    if exists:
        print(f"  Deleting old {name} ({OLD_DIM}-dim)...")
        client.delete_collection(name)
        print("  ✓ Deleted")

    # Create new
    print(f"  Creating {name} ({dim}-dim, Cosine)...")
    client.create_collection(
        collection_name=name, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
    )
    print("  ✓ Created")
    return True


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)

    return chunks


def load_constitutional_docs() -> list[dict[str, Any]]:
    """Load all markdown files from 000_THEORY."""
    print(f"\nScanning {DOCS_PATH}...")

    docs = []
    if not DOCS_PATH.exists():
        print(f"  Warning: {DOCS_PATH} not found")
        return docs

    for md_file in DOCS_PATH.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")

            # Chunk large files
            chunks = chunk_text(content, chunk_size=512, overlap=50)

            for i, chunk in enumerate(chunks):
                doc_id = hashlib.sha256(f"{md_file}:{i}".encode()).hexdigest()[:16]

                docs.append(
                    {
                        "id": doc_id,
                        "file": str(md_file),
                        "chunk_index": i,
                        "content": chunk,
                        "title": md_file.stem,
                    }
                )
        except Exception as e:
            print(f"  Error reading {md_file}: {e}")

    print(f"  ✓ Found {len(docs)} chunks from markdown files")
    return docs


def embed_and_upsert(
    client: QdrantClient,
    model: SentenceTransformer,
    collection: str,
    docs: list[dict],
    batch_size: int = 32,
) -> int:
    """Embed documents and upsert to Qdrant."""
    print(f"\nEmbedding {len(docs)} documents...")

    total = 0
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]

        # Embed
        texts = [d["content"] for d in batch]
        embeddings = model.encode(texts, show_progress_bar=False)

        # Create points
        points = []
        for doc, embedding in zip(batch, embeddings):
            points.append(
                PointStruct(
                    id=doc["id"],
                    vector=embedding.tolist(),
                    payload={
                        "file": doc["file"],
                        "title": doc["title"],
                        "chunk_index": doc["chunk_index"],
                        "content_preview": doc["content"][:500],
                        "embedding_model": NEW_MODEL,
                        "vector_dim": NEW_DIM,
                        "embedded_at": datetime.utcnow().isoformat(),
                    },
                )
            )

        # Upsert
        client.upsert(collection_name=collection, points=points)

        total += len(batch)
        if (i // batch_size + 1) % 10 == 0:
            print(f"  Progress: {total}/{len(docs)} documents")

    print(f"  ✓ Embedded {total} documents")
    return total


def verify_migration(client: QdrantClient) -> dict[str, Any]:
    """Verify both collections are correct."""
    print("\nVerifying migration...")

    results = {}

    for collection in [CONSTITUTIONAL_COLLECTION, PRECEDENT_COLLECTION]:
        try:
            info = client.get_collection(collection)
            results[collection] = {
                "exists": True,
                "vector_size": info.config.params.vectors.size,
                "points_count": info.points_count,
                "status": "OK" if info.config.params.vectors.size == NEW_DIM else "WRONG_DIM",
            }
        except Exception as e:
            results[collection] = {"exists": False, "error": str(e)}

    return results


def main():
    """Main migration function."""
    print("=" * 60)
    print("arifOS BGE-M3 Migration Script")
    print("F2 Truth + F6 Empathy: Multilingual constitutional memory")
    print("=" * 60)

    # Connect to Qdrant
    print(f"\nConnecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(QDRANT_URL)
    print("  ✓ Connected")

    # Load BGE-M3
    model = load_bge_m3()

    # Step 1: Recreate arifos_constitutional
    recreate_collection(client, CONSTITUTIONAL_COLLECTION, NEW_DIM)

    # Step 2: Load and embed constitutional docs
    docs = load_constitutional_docs()
    if docs:
        embed_and_upsert(client, model, CONSTITUTIONAL_COLLECTION, docs)

    # Step 3: Create vault_precedent_memory (empty, ready for seals)
    recreate_collection(client, PRECEDENT_COLLECTION, NEW_DIM)

    # Step 4: Verify
    results = verify_migration(client)

    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)

    all_ok = True
    for collection, status in results.items():
        print(f"\n{collection}:")
        if status.get("exists"):
            print(f"  Status: {status['status']}")
            print(f"  Dimensions: {status['vector_size']}")
            print(f"  Points: {status['points_count']}")
            if status["status"] != "OK":
                all_ok = False
        else:
            print(f"  Status: FAILED - {status.get('error')}")
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("✓ Migration complete!")
        print(f"✓ {CONSTITUTIONAL_COLLECTION}: Constitutional docs at {NEW_DIM}-dim")
        print(f"✓ {PRECEDENT_COLLECTION}: Ready for governance precedents")
        print("\nNext steps:")
        print("  1. Update Docker image with BGE-M3 model")
        print("  2. Restart arifOS services")
        print("  3. seal_vault will auto-embed to precedent memory")
    else:
        print("✗ Migration had issues. Check logs above.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
