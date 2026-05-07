"""
GEOX Memory Layer — Geological Context Store
DITEMPA BUKAN DIBERI

Wraps arifOS M4 Qdrant memory for geological context persistence.
Default backend is in-memory dict (no external dependencies).
Production mode: inject qdrant_client for vector similarity search.

Features:
  - Store GeoResponse + GeoRequest as searchable memory entries
  - Retrieve by basin, query similarity, or time range
  - SHA256-based deduplication
  - JSONL export for HuggingFace Dataset upload
  - Optional Qdrant vector backend (injected at construction time)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest, GeoResponse

# ---------------------------------------------------------------------------
# GeoMemoryEntry
# ---------------------------------------------------------------------------


@dataclass
class GeoMemoryEntry:
    """
    A single entry in the GEOX geological memory store.

    Attributes:
        entry_id:         Unique ID for this memory entry.
        prospect_name:    Name of the prospect.
        basin:            Sedimentary basin.
        insight_text:     Combined text of all insights (for retrieval).
        verdict:          GEOX verdict string (SEAL/PARTIAL/SABAR/VOID).
        confidence:       Aggregate confidence from the pipeline run.
        timestamp:        UTC timestamp of storage.
        embedding_vector: Float vector for similarity search (None = not embedded).
        metadata:         Arbitrary extra metadata.
    """

    entry_id: str
    prospect_name: str
    basin: str
    insight_text: str
    verdict: str
    confidence: float
    timestamp: datetime
    embedding_vector: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to dict. Converts datetime to ISO string."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> GeoMemoryEntry:
        """Deserialise from dict."""
        ts = d.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)
        return cls(
            entry_id=d["entry_id"],
            prospect_name=d["prospect_name"],
            basin=d["basin"],
            insight_text=d["insight_text"],
            verdict=d["verdict"],
            confidence=float(d.get("confidence", 0.0)),
            timestamp=ts,
            embedding_vector=d.get("embedding_vector"),
            metadata=d.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# GeoMemoryStore
# ---------------------------------------------------------------------------


class GeoMemoryStore:
    """
    Geological memory store with optional Qdrant backend.

    In-memory mode (default):
        Uses a Python dict keyed by entry_id. All retrieval is
        keyword/basin-based (no vector similarity).

    Qdrant mode (production):
        Inject a qdrant_client at construction. Stores vectors and
        performs ANN search for similarity retrieval.

    Usage:
        store = GeoMemoryStore()
        entry_id = await store.store(response, request)
        entries = await store.retrieve("porosity Malay Basin", basin="Malay Basin")
    """

    def __init__(
        self,
        qdrant_client: Any | None = None,
        collection: str = "geox_geological_memory",
    ) -> None:
        """
        Args:
            qdrant_client: Optional Qdrant client instance for vector backend.
                           If None, uses in-memory dict storage.
            collection:    Qdrant collection name (used only in Qdrant mode).
        """
        self._qdrant = qdrant_client
        self._collection = collection
        self._store: dict[str, GeoMemoryEntry] = {}

    # ------------------------------------------------------------------
    # store()
    # ------------------------------------------------------------------

    async def store(self, response: GeoResponse, request: GeoRequest) -> str:
        """
        Store a pipeline response as a memory entry.

        Deduplicates by content hash — if an entry with the same
        insight text hash already exists, updates it rather than
        creating a duplicate.

        Args:
            response: GeoResponse from evaluate_prospect().
            request:  Original GeoRequest.

        Returns:
            entry_id of the stored (or updated) memory entry.
        """
        # Combine all insight text
        insight_text = "\n".join(i.text for i in response.insights)
        content_hash = self.similarity_hash(
            f"{request.prospect_name}:{request.basin}:{insight_text}"
        )
        entry_id = f"GEO-MEM-{content_hash}"

        entry = GeoMemoryEntry(
            entry_id=entry_id,
            prospect_name=request.prospect_name,
            basin=request.basin,
            insight_text=insight_text,
            verdict=response.verdict,
            confidence=response.confidence_aggregate,
            timestamp=datetime.now(timezone.utc),
            embedding_vector=None,  # Embedding populated externally if needed
            metadata={
                "request_id": request.request_id,
                "response_id": response.response_id,
                "play_type": request.play_type,
                "risk_tolerance": request.risk_tolerance,
                "available_data": request.available_data,
                "location": {
                    "latitude": request.location.latitude,
                    "longitude": request.location.longitude,
                    "depth_m": request.location.depth_m,
                },
                "insight_count": len(response.insights),
                "human_signoff_required": response.human_signoff_required,
            },
        )

        if self._qdrant is not None:
            await self._qdrant_upsert(entry)
        else:
            self._store[entry_id] = entry

        return entry_id

    # ------------------------------------------------------------------
    # retrieve()
    # ------------------------------------------------------------------

    async def retrieve(
        self,
        query: str,
        basin: str | None = None,
        limit: int = 5,
    ) -> list[GeoMemoryEntry]:
        """
        Retrieve memory entries relevant to a query.

        In Qdrant mode: performs vector similarity search.
        In-memory mode: performs keyword substring matching on
        insight_text + prospect_name + basin.

        Args:
            query:  Search query string.
            basin:  Optional basin filter (exact match after .lower()).
            limit:  Maximum number of entries to return.

        Returns:
            List of GeoMemoryEntry objects, most relevant first.
        """
        if self._qdrant is not None:
            return await self._qdrant_search(query, basin, limit)

        # In-memory keyword retrieval
        query_lower = query.lower()
        results: list[tuple[float, GeoMemoryEntry]] = []

        for entry in self._store.values():
            # Basin filter
            if basin and basin.lower() not in entry.basin.lower():
                continue

            # Score by keyword overlap
            score = 0.0
            text_lower = (entry.insight_text + " " + entry.prospect_name).lower()
            for word in query_lower.split():
                if word in text_lower:
                    score += 1.0
            # Boost by confidence
            score += entry.confidence * 0.5

            if score > 0:
                results.append((score, entry))

        # Sort by score descending, return top-N
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    # ------------------------------------------------------------------
    # get_basin_history()
    # ------------------------------------------------------------------

    async def get_basin_history(self, basin: str) -> list[GeoMemoryEntry]:
        """
        Retrieve all memory entries for a given basin, sorted by timestamp.

        Args:
            basin: Basin name (case-insensitive substring match).

        Returns:
            List of GeoMemoryEntry objects sorted by timestamp ascending.
        """
        basin_lower = basin.lower()
        if self._qdrant is not None:
            return await self._qdrant_search(basin, basin=basin, limit=100)

        entries = [e for e in self._store.values() if basin_lower in e.basin.lower()]
        entries.sort(key=lambda e: e.timestamp)
        return entries

    # ------------------------------------------------------------------
    # similarity_hash()
    # ------------------------------------------------------------------

    def similarity_hash(self, text: str) -> str:
        """
        Compute a short SHA-256 hash prefix for deduplication.

        Uses the first 16 hex chars of SHA-256 of the UTF-8 encoded text.

        Args:
            text: Input string to hash.

        Returns:
            16-character hex string prefix.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    # ------------------------------------------------------------------
    # export_jsonl()
    # ------------------------------------------------------------------

    def export_jsonl(self, path: str) -> None:
        """
        Export all memory entries to a JSONL file.

        Each line is a JSON object representing one GeoMemoryEntry.
        Suitable for upload to HuggingFace Datasets.

        Args:
            path: File path to write (e.g. 'geox_memory_export.jsonl').

        Raises:
            IOError: If the file cannot be written.
        """
        entries = list(self._store.values())
        with open(path, "w", encoding="utf-8") as fh:
            for entry in entries:
                fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    # ------------------------------------------------------------------
    # In-memory utility methods
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return number of entries in the in-memory store."""
        return len(self._store)

    def clear(self) -> None:
        """Clear all in-memory entries (does NOT affect Qdrant)."""
        self._store.clear()

    def list_basins(self) -> list[str]:
        """Return sorted list of unique basin names in the store."""
        return sorted({e.basin for e in self._store.values()})

    # ------------------------------------------------------------------
    # Qdrant backend methods (stub — implement with qdrant_client)
    # ------------------------------------------------------------------

    async def _qdrant_upsert(self, entry: GeoMemoryEntry) -> None:
        """
        Upsert a memory entry into Qdrant.

        Requires the entry to have a non-None embedding_vector.
        Falls back to in-memory store if vector is missing.
        """
        if entry.embedding_vector is None:
            # No embedding available — fall back to in-memory
            self._store[entry.entry_id] = entry
            return

        try:
            from qdrant_client.models import PointStruct  # type: ignore

            point = PointStruct(
                id=self.similarity_hash(entry.entry_id),
                vector=entry.embedding_vector,
                payload=entry.to_dict(),
            )
            self._qdrant.upsert(
                collection_name=self._collection,
                points=[point],
            )
        except Exception as exc:
            # F9 Anti-Hantu: do not silently fail
            import logging

            logging.getLogger("geox.memory").warning(
                "Qdrant upsert failed for %s: %s. Falling back to in-memory.",
                entry.entry_id,
                exc,
            )
            self._store[entry.entry_id] = entry

    async def _qdrant_search(
        self, query: str, basin: str | None, limit: int
    ) -> list[GeoMemoryEntry]:
        """
        Perform ANN search in Qdrant.

        NOTE: In production, the query should be embedded using the same
        embedding model used for storage. This stub returns in-memory
        results if embedding is not available.
        """
        import logging

        logger = logging.getLogger("geox.memory")
        logger.warning(
            "Qdrant search called but embedding not configured. "
            "Falling back to in-memory keyword search."
        )
        return await self.retrieve(query, basin=basin, limit=limit)


class DualMemoryStore:
    """
    Dual-memory system combining:
    - Discrete: Macrostrat entities (units, columns, formations)
    - Continuous: EO embeddings from LEM
    """

    def __init__(
        self,
        qdrant_client: Any | None = None,
        macrostrat_cache_dir: str = "./macrostrat_cache",
    ) -> None:
        self.qdrant = qdrant_client
        self.cache_dir = macrostrat_cache_dir
        self._discrete_cache: dict[str, Any] = {}  # Macrostrat data
        self._continuous_cache: dict[str, Any] = {}  # Embeddings

    async def query_dual(
        self,
        location: CoordinatePoint,
        query_type: str = "analog_search",
        top_k: int = 5,
    ) -> dict[str, Any]:
        """
        Query both memories and return fused results.

        Returns:
            {
                "discrete": [...],  # Macrostrat units/columns
                "continuous": [...],  # Similar embeddings
                "fused_ranking": [...]  # Combined evidence
            }
        """
        # Query discrete memory (Macrostrat)
        # In a real implementation, this would look up the cache or call the tool
        discrete_results = await self._query_discrete(location, top_k)

        # Query continuous memory (embeddings)
        continuous_results = await self._query_continuous(location, top_k)

        # Fuse rankings
        fused = self._fuse_results(discrete_results, continuous_results)

        return {
            "discrete": discrete_results,
            "continuous": continuous_results,
            "fused_ranking": fused,
        }

    async def _query_discrete(self, location: CoordinatePoint, top_k: int) -> list[dict[str, Any]]:
        """Mock discrete query."""
        # This would normally interface with MacrostratTool or its results cache
        return [{"type": "unit", "name": "Formation A", "confidence": 0.85}]

    async def _query_continuous(
        self, location: CoordinatePoint, top_k: int
    ) -> list[dict[str, Any]]:
        """Mock continuous query."""
        # This would normally interface with Qdrant
        return [{"type": "embedding", "source": "TerraFM", "similarity": 0.92, "confidence": 0.75}]

    def _fuse_results(
        self, discrete: list[dict[str, Any]], continuous: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Merge discrete and continuous evidence into ranked hypotheses."""
        fused = []
        # Interleave based on confidence for now
        d_idx, c_idx = 0, 0
        while (d_idx < len(discrete) or c_idx < len(continuous)) and len(fused) < 10:
            d_val = discrete[d_idx] if d_idx < len(discrete) else None
            c_val = continuous[c_idx] if c_idx < len(continuous) else None

            if d_val and (not c_val or d_val.get("confidence", 0) >= c_val.get("confidence", 0)):
                fused.append({"origin": "discrete", "data": d_val})
                d_idx += 1
            elif c_val:
                fused.append({"origin": "continuous", "data": c_val})
                c_idx += 1

        return fused
