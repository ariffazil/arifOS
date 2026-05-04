from __future__ import annotations

from typing import Any

from arifosmcp.intelligence.embeddings import embed


def query_memory(
    query: str,
    collection: str = "default",
    n_results: int = 5,
    where: dict[str, Any] | None = None,
    include_embeddings: bool = False,
    _chroma_path: str | None = None,
) -> dict[str, Any]:
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(path=_chroma_path) if _chroma_path else QdrantClient()
        vector = embed(query)
        response = client.query_points(
            collection_name=collection,
            query=vector,
            limit=n_results,
            query_filter=where,
            with_payload=True,
            with_vectors=include_embeddings,
        )
        points = getattr(response, "points", response or [])
        results = []
        for point in points:
            payload = getattr(point, "payload", {}) or {}
            item = {
                "id": getattr(point, "id", None),
                "score": getattr(point, "score", None),
                "content": payload.get("content"),
                "payload": payload,
            }
            if include_embeddings:
                item["embedding"] = getattr(point, "vector", None)
            results.append(item)
        return {"results": results, "collection": collection, "query": query}
    except Exception as exc:
        return {"error": str(exc), "results": [], "collection": collection, "query": query}


def list_collections(_chroma_path: str | None = None) -> dict[str, Any]:
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(path=_chroma_path) if _chroma_path else QdrantClient()
        collections = client.get_collections()
        items = getattr(collections, "collections", collections or [])
        names = [getattr(item, "name", item) for item in items]
        return {"collections": names}
    except Exception as exc:
        return {"error": str(exc), "collections": []}
