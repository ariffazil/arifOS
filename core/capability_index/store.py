"""Qdrant-backed store for the Capability Index with local in-memory fallback.

Uses sentence-transformers (BAAI/bge-m3 or all-MiniLM-L6-v2) for embeddings.
Lightweight, local, resilient.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from capability_index.models import CapabilityRecord
import numpy as np

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mcp_capabilities"
VECTOR_SIZE = 1024  # BAAI/bge-m3 — aligned with arifOS L3 semantic memory
EMBEDDING_MODEL = "BAAI/bge-m3"
REGISTRY_JSON = Path("/root/AAA/registries/CAPABILITY_INDEX.json")


class CapabilityStore:
    """Create, seed, and search the capability index in Qdrant with local fallback."""

    def __init__(self, qdrant_url: str = "http://localhost:6333") -> None:
        self.qdrant_url = qdrant_url
        self._client = None
        self._encoder = None
        self._cached_records: list[CapabilityRecord] = []
        self._cached_embeddings: Optional[np.ndarray] = None

    @property
    def client(self):
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
                self._client = QdrantClient(url=self.qdrant_url, timeout=2.0)
            except Exception as e:
                logger.warning("Could not initialize QdrantClient: %s", e)
        return self._client

    def _get_encoder(self):
        """Lazy-load the embedding model so import is fast."""
        if self._encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading embedding model %s ...", EMBEDDING_MODEL)
                self._encoder = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
            except Exception as e:
                logger.warning("SentenceTransformer failed to load (%s), using lightweight lexical fallback", e)
        return self._encoder

    def _load_local_records(self) -> list[CapabilityRecord]:
        """Load records from registry JSON."""
        if self._cached_records:
            return self._cached_records

        if REGISTRY_JSON.exists():
            try:
                with open(REGISTRY_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cached_records = [
                        CapabilityRecord(**t) if isinstance(t, dict) else t
                        for t in data.get("tools", [])
                    ]
            except Exception as e:
                logger.warning("Failed reading %s: %s", REGISTRY_JSON, e)

        if not self._cached_records:
            try:
                from capability_index.seed import SEED_CAPABILITIES
                self._cached_records = list(SEED_CAPABILITIES)
            except Exception:
                pass

        return self._cached_records

    def create_collection(self, recreate: bool = False) -> None:
        """Ensure the Qdrant collection exists."""
        if not self.client:
            return
        from qdrant_client.models import Distance, VectorParams
        try:
            if recreate:
                self.client.delete_collection(COLLECTION_NAME)
            if not self.client.collection_exists(COLLECTION_NAME):
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                )
                logger.info("Created Qdrant collection: %s", COLLECTION_NAME)
        except Exception as e:
            logger.warning("Qdrant collection creation skipped: %s", e)

    def upsert(self, records: Sequence[CapabilityRecord]) -> None:
        """Embed and store capability records."""
        self._cached_records = list(records)
        encoder = self._get_encoder()
        if encoder is not None:
            texts = [r.to_embedding_text() for r in records]
            self._cached_embeddings = np.array(encoder.encode(texts, show_progress_bar=False))

        if not self.client:
            return

        try:
            from qdrant_client.models import PointStruct
            points = [
                PointStruct(
                    id=idx,
                    vector=self._cached_embeddings[idx].tolist(),
                    payload=records[idx].model_dump(),
                )
                for idx in range(len(records))
            ]
            self.client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info("Upserted %d capabilities into %s", len(points), COLLECTION_NAME)
        except Exception as e:
            logger.warning("Qdrant upsert failed (operating in local fallback mode): %s", e)

    def search(
        self,
        query: str,
        limit: int = 10,
        action_class: Optional[str] = None,
        server: Optional[str] = None,
    ) -> list[CapabilityRecord]:
        """Return the top-k capabilities matching the query with optional filters."""
        # Try Qdrant search first
        if self.client:
            try:
                encoder = self._get_encoder()
                if encoder:
                    vector = encoder.encode([query], show_progress_bar=False)[0].tolist()
                    response = self.client.query_points(
                        collection_name=COLLECTION_NAME,
                        query=vector,
                        limit=limit * 2,
                    )
                    results = [CapabilityRecord(**r.payload) for r in response.points]
                    filtered = self._apply_filters(results, action_class, server)
                    if filtered:
                        return filtered[:limit]
            except Exception as e:
                logger.debug("Qdrant search fallback: %s", e)

        # Fallback: Local semantic / lexical ranking
        records = self._load_local_records()
        if not records:
            return []

        filtered_records = self._apply_filters(records, action_class, server)
        if not filtered_records:
            return []

        encoder = self._get_encoder()
        if encoder is not None:
            try:
                query_vec = encoder.encode([query], show_progress_bar=False)[0]
                texts = [r.to_embedding_text() for r in filtered_records]
                record_vecs = encoder.encode(texts, show_progress_bar=False)
                
                # Cosine similarity
                scores = np.dot(record_vecs, query_vec) / (
                    np.linalg.norm(record_vecs, axis=1) * np.linalg.norm(query_vec) + 1e-9
                )
                ranked_indices = np.argsort(-scores)[:limit]
                return [filtered_records[idx] for idx in ranked_indices]
            except Exception as e:
                logger.warning("Local semantic search failed, using lexical match: %s", e)

        # Lexical fallback
        q_tokens = set(query.lower().split())
        scored = []
        for r in filtered_records:
            text = f"{r.tool_name} {r.server} {r.description} {' '.join(r.tags)}".lower()
            score = sum(1 for tok in q_tokens if tok in text)
            scored.append((score, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for score, r in scored[:limit]]

    def _apply_filters(
        self,
        records: list[CapabilityRecord],
        action_class: Optional[str] = None,
        server: Optional[str] = None,
    ) -> list[CapabilityRecord]:
        out = records
        if action_class:
            out = [r for r in out if r.effective_class == action_class or r.action_class == action_class]
        if server:
            out = [r for r in out if r.server.lower() == server.lower()]
        return out

    def count(self) -> int:
        """Number of indexed capabilities."""
        if self.client:
            try:
                return self.client.count(collection_name=COLLECTION_NAME).count
            except Exception:
                pass
        return len(self._load_local_records())
