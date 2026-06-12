"""Qdrant-backed store for the Capability Index.

Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings.
Lightweight, local, no API keys.
"""

from __future__ import annotations

import logging
from typing import Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from capability_index.models import CapabilityRecord

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mcp_capabilities"
VECTOR_SIZE = 1024  # BAAI/bge-m3 — aligned with arifOS L3 semantic memory
EMBEDDING_MODEL = "BAAI/bge-m3"


class CapabilityStore:
    """Create, seed, and search the capability index in Qdrant."""

    def __init__(self, qdrant_url: str = "http://localhost:6333") -> None:
        self.client = QdrantClient(url=qdrant_url)
        self._encoder = None

    def _get_encoder(self):
        """Lazy-load the embedding model so import is fast."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model %s ...", EMBEDDING_MODEL)
            self._encoder = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
        return self._encoder

    def create_collection(self, recreate: bool = False) -> None:
        """Ensure the Qdrant collection exists."""
        if recreate:
            self.client.delete_collection(COLLECTION_NAME)
        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection: %s", COLLECTION_NAME)

    def upsert(self, records: Sequence[CapabilityRecord]) -> None:
        """Embed and store capability records."""
        encoder = self._get_encoder()
        texts = [r.to_embedding_text() for r in records]
        embeddings = encoder.encode(texts, show_progress_bar=False)

        points = [
            PointStruct(
                id=idx,
                vector=emb.tolist(),
                payload=records[idx].model_dump(),
            )
            for idx, emb in enumerate(embeddings)
        ]
        self.client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info("Upserted %d capabilities into %s", len(points), COLLECTION_NAME)

    def search(self, query: str, limit: int = 10) -> list[CapabilityRecord]:
        """Return the top-k capabilities matching the query."""
        encoder = self._get_encoder()
        vector = encoder.encode([query], show_progress_bar=False)[0].tolist()
        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=limit,
        )
        return [CapabilityRecord(**r.payload) for r in response.points]

    def count(self) -> int:
        """Number of indexed capabilities."""
        return self.client.count(collection_name=COLLECTION_NAME).count
