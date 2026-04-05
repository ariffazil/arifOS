import os
#!/usr/bin/env python3
"""
Embed Constitutional Corpus — arifOS + APEX-THEORY
Processes markdown files into Qdrant vector storage using BGE-small.

Usage:
    python scripts/embed_constitutional_corpus.py
"""

import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "arifos_constitutional"
EMBEDDING_MODEL = "BAAI/bge-m3"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
QDRANT_URL = "http://localhost:6333"
QDRANT_API_KEY = "arifos_qdrant_2026"

REPO_PATHS = os.getenv("REPO_PATHS", "").split(",") if os.getenv("REPO_PATHS") else [
    "/root/arifOS/000_THEORY",
    "/root/APEX-THEORY",
    "/root/arifOS/docs",
]

EXCLUDE_PATTERNS = [
    r"archive",
    r"_OUTLINE",
    r"\.git",
]


def load_markdown_files(repo_paths: list[str]) -> list[dict[str, Any]]:
    """Load all markdown files from repositories."""
    documents = []

    for repo_path in repo_paths:
        repo = Path(repo_path)
        if not repo.exists():
            print(f"[WARN] Repo not found: {repo_path}")
            continue

        source_name = repo.name
        for md_file in repo.rglob("*.md"):
            rel_path = md_file.relative_to(repo)
            if any(re.search(p, str(rel_path)) for p in EXCLUDE_PATTERNS):
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
                documents.append(
                    {
                        "source": source_name,
                        "path": str(rel_path),
                        "content": content,
                        "full_path": str(md_file),
                    }
                )
            except Exception as e:
                print(f"[WARN] Failed to read {md_file}: {e}")

    return documents


def chunk_document(
    doc: dict[str, Any], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[dict[str, Any]]:
    """Split document into overlapping chunks by sections and paragraphs."""
    chunks = []
    content = doc["content"]

    sections = re.split(r"\n#{1,3}\s+", content)
    current_chunk = ""
    chunk_idx = 0

    for section in sections:
        if not section.strip():
            continue

        if len(current_chunk) + len(section) > chunk_size and current_chunk:
            chunks.append(
                {
                    "source": doc["source"],
                    "path": doc["path"],
                    "chunk_idx": chunk_idx,
                    "content": current_chunk.strip(),
                }
            )
            chunk_idx += 1
            current_chunk = section
        else:
            current_chunk += "\n\n" + section

    if current_chunk.strip():
        chunks.append(
            {
                "source": doc["source"],
                "path": doc["path"],
                "chunk_idx": chunk_idx,
                "content": current_chunk.strip(),
            }
        )

    return chunks


def extract_metadata(content: str) -> dict[str, Any]:
    """Extract constitutional metadata from content."""
    metadata = {}

    floor_matches = re.findall(r"\bF(\d{1,2})\b", content)
    if floor_matches:
        metadata["floors"] = list(set(f"F{f}" for f in floor_matches))

    stage_matches = re.findall(r"\b(\d{3})\b", content)
    if stage_matches:
        metadata["stages"] = list(set(stage_matches))

    if "constitutional" in content.lower():
        metadata["type"] = "constitutional"
    elif "theory" in content.lower():
        metadata["type"] = "theory"
    elif "law" in content.lower():
        metadata["type"] = "law"
    else:
        metadata["type"] = "general"

    return metadata


def main():
    print("=" * 60)
    print("ARIFOS CONSTITUTIONAL CORPUS EMBEDDER")
    print("=" * 60)

    print("\n[1/5] Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL, use_auth_token=os.getenv("HF_TOKEN"))
    print(f"      Model: {EMBEDDING_MODEL}")
    print(f"      Dimensions: {model.get_sentence_embedding_dimension()}")

    print("\n[2/5] Connecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    try:
        client.get_collection(COLLECTION_NAME)
        print(f"      Collection '{COLLECTION_NAME}' exists")
    except UnexpectedResponse:
        print(f"      Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=Distance.COSINE,
            ),
        )

    print("\n[3/5] Loading markdown files...")
    documents = load_markdown_files(REPO_PATHS)
    print(f"      Found {len(documents)} documents")
    for doc in documents[:5]:
        print(f"        - {doc['source']}/{doc['path']}")
    if len(documents) > 5:
        print(f"        ... and {len(documents) - 5} more")

    print("\n[4/5] Chunking documents...")
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        for chunk in chunks:
            chunk["metadata"] = extract_metadata(chunk["content"])
        all_chunks.extend(chunks)
    print(f"      Created {len(all_chunks)} chunks")

    print("\n[5/5] Generating embeddings and uploading to Qdrant...")
    batch_size = 50
    points = []

    for i, chunk in enumerate(all_chunks):
        embedding = model.encode(chunk["content"], normalize_embeddings=True)

        point = PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={
                "source": chunk["source"],
                "path": chunk["path"],
                "chunk_idx": chunk["chunk_idx"],
                "content": chunk["content"][:1000],
                "metadata": chunk["metadata"],
            },
        )
        points.append(point)

        if len(points) >= batch_size:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f"      Uploaded {i + 1}/{len(all_chunks)} chunks")
            points = []

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"      Uploaded {len(all_chunks)}/{len(all_chunks)} chunks")

    print("\n" + "=" * 60)
    print("EMBEDDING COMPLETE")
    print("=" * 60)
    print(f"  Collection: {COLLECTION_NAME}")
    print(f"  Documents:  {len(documents)}")
    print(f"  Chunks:     {len(all_chunks)}")
    print(f"  Model:      {EMBEDDING_MODEL}")
    print("  Qdrant:     http://localhost:6333")
    print()

    print("Test query:")
    test_query = "What is F2 floor?"
    test_embedding = model.encode(test_query, normalize_embeddings=True)
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=test_embedding.tolist(),
        limit=3,
    )
    print(f"  Query: '{test_query}'")
    for r in results:
        print(f"    - {r.payload['source']}/{r.payload['path']} (score: {r.score:.3f})")


if __name__ == "__main__":
    main()
