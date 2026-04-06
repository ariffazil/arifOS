#!/usr/bin/env python3
"""
arifOS RAG Pipeline — Constitutional Knowledge Retrieval

Provides RAG (Retrieval Augmented Generation) for arifOS agents.
Agents can query the constitutional knowledge base and retrieve relevant context.

Usage:
    from arifos_rag import ConstitutionalRAG

    rag = ConstitutionalRAG()
    context = rag.retrieve("What is F2 floor?")
    augmented_prompt = rag.augment_prompt(original_prompt, query)

API Endpoints (via FastAPI):
    POST /rag/query
    POST /rag/augment
    GET /rag/health
"""

import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct
from sentence_transformers import SentenceTransformer

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
COLLECTION_NAME = os.environ.get("RAG_COLLECTION", "arifos_constitutional")
EMBEDDING_MODEL = os.environ.get("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
DEFAULT_TOP_K = int(os.environ.get("RAG_TOP_K", "5"))


@dataclass
class RetrievedContext:
    source: str
    path: str
    content: str
    score: float
    metadata: dict

    def to_context_string(self) -> str:
        return f"[{self.source}/{self.path}] (relevance: {self.score:.3f})\n{self.content}"


@dataclass
class RAGResponse:
    query: str
    contexts: list[RetrievedContext]
    total_chunks: int
    augmented_prompt: str | None = None


class ConstitutionalRAG:
    def __init__(
        self,
        qdrant_url: str = QDRANT_URL,
        qdrant_api_key: str | None = QDRANT_API_KEY,
        collection_name: str = COLLECTION_NAME,
        embedding_model: str = EMBEDDING_MODEL,
    ):
        if not qdrant_api_key:
            raise ValueError("QDRANT_API_KEY environment variable is required")
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.collection = collection_name
        self.model = SentenceTransformer(embedding_model)
        self.model_name = embedding_model

    def _jaccard_similarity(self, query: str, document: str) -> float:
        """
        Simple Jaccard similarity between two strings based on lowercase word tokens.
        """

        def get_tokens(text: str) -> set[str]:
            tokens = re.findall(r"\w+", text.lower())
            return set(tokens)

        query_tokens = get_tokens(query)
        doc_tokens = get_tokens(document)

        if not query_tokens and not doc_tokens:
            return 1.0
        if not query_tokens or not doc_tokens:
            return 0.0

        intersection = len(query_tokens.intersection(doc_tokens))
        union = len(query_tokens.union(doc_tokens))
        return intersection / union

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        source_filter: str | None = None,
        min_score: float = 0.0,
        hybrid_alpha: float = 0.3,  # Weight for Jaccard (0.0 = embeddings only)
    ) -> list[RetrievedContext]:
        """
        Hybrid retrieval: Jaccard (Tokens) + Cosine (Embeddings).
        """
        embedding = self.model.encode(query, normalize_embeddings=True)

        query_filter = None
        if source_filter:
            query_filter = Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=source_filter))]
            )

        # We query more than top_k to allow reranking by Jaccard
        try:
            results = self.client.query_points(
                collection_name=self.collection,
                query=embedding.tolist(),
                query_filter=query_filter,
                limit=top_k * 2,  # Oversample for reranking
                score_threshold=min_score,
                with_payload=True,
            )
        except Exception as e:
            print(f"RAG Retrieval Error: {e}")
            return []

        contexts = []
        for point in results.points:
            payload = point.payload or {}
            content = payload.get("content", "")

            # Compute Jaccard
            jaccard = self._jaccard_similarity(query, content)

            # Combine scores
            # Cosine similarity from Qdrant is in [0, 1] for normalized embeddings
            cosine = point.score
            hybrid_score = (hybrid_alpha * jaccard) + ((1 - hybrid_alpha) * cosine)

            ctx = RetrievedContext(
                source=payload.get("source", "unknown"),
                path=payload.get("path", "unknown"),
                content=content,
                score=hybrid_score,
                metadata={
                    **(payload.get("metadata", {})),
                    "cosine_score": cosine,
                    "jaccard_score": jaccard,
                },
            )
            contexts.append(ctx)

        # Sort by hybrid score and return top_k
        contexts.sort(key=lambda x: x.score, reverse=True)
        return contexts[:top_k]

    def index_memory(
        self,
        session_id: str,
        content: str,
        source: str = "session_history",
        metadata: dict | None = None,
    ) -> bool:
        """
        Index a new memory into the constitutional RAG.
        """
        try:
            embedding = self.model.encode(content, normalize_embeddings=True)

            point_id = str(uuid.uuid4())
            payload = {
                "source": source,
                "path": session_id,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat() if "datetime" in globals() else "",
            }

            self.client.upsert(
                collection_name=self.collection,
                points=[PointStruct(id=point_id, vector=embedding.tolist(), payload=payload)],
            )
            return True
        except Exception as e:
            print(f"Error indexing memory: {e}")
            return False

    def retrieve_as_text(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        source_filter: str | None = None,
        min_score: float = 0.0,
    ) -> str:
        contexts = self.retrieve(query, top_k, source_filter, min_score)
        if not contexts:
            return "No relevant context found in the constitutional knowledge base."

        context_strings = [ctx.to_context_string() for ctx in contexts]
        return "\n\n---\n\n".join(context_strings)

    def augment_prompt(
        self,
        original_prompt: str,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        context_prefix: str = "Relevant context from arifOS constitutional knowledge base:",
        source_filter: str | None = None,
    ) -> str:
        context = self.retrieve_as_text(query, top_k, source_filter)

        return f"""{original_prompt}

{context_prefix}

{context}

Answer based on the context above, citing sources when appropriate."""

    def query_with_metadata(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> dict:
        contexts = self.retrieve(query, top_k)

        sources = {}
        floors_mentioned = set()
        stages_mentioned = set()

        for ctx in contexts:
            source_key = f"{ctx.source}/{ctx.path}"
            sources[source_key] = ctx.score

            if "floors" in ctx.metadata:
                floors_mentioned.update(ctx.metadata["floors"])
            if "stages" in ctx.metadata:
                stages_mentioned.update(ctx.metadata["stages"])

        return {
            "query": query,
            "contexts": [
                {
                    "source": ctx.source,
                    "path": ctx.path,
                    "content": ctx.content[:500] + "..." if len(ctx.content) > 500 else ctx.content,
                    "score": ctx.score,
                }
                for ctx in contexts
            ],
            "sources": sources,
            "floors_mentioned": list(floors_mentioned),
            "stages_mentioned": list(stages_mentioned),
            "total_chunks": len(contexts),
        }

    def health_check(self) -> dict:
        try:
            collection_info = self.client.get_collection(self.collection)
            return {
                "status": "healthy",
                "collection": self.collection,
                "points_count": collection_info.points_count,
                "embedding_model": self.model_name,
                "qdrant_url": QDRANT_URL,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "collection": self.collection,
                "embedding_model": self.model_name,
            }


rag = ConstitutionalRAG()

__all__ = ["ConstitutionalRAG", "RetrievedContext", "RAGResponse"]
