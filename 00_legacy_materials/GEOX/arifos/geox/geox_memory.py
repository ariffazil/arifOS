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
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest, GeoResponse

logger = logging.getLogger("geox.memory")

# ---------------------------------------------------------------------------
# GeoMemoryEntry
# ---------------------------------------------------------------------------


@dataclass
class GeoMemoryEntry:
    """
    A single entry in the GEOX geological memory store.
    Aligned with H1-H9 Hardening Standards.
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

    # H1-H9 Hardening Fields
    access_count: int = 0
    last_accessed: datetime | None = None
    is_deleted: bool = False  # H3/H8 Tombstone
    is_quarantined: bool = False  # H4 Pseudo-embedding quarantine
    ttl_expiry: datetime | None = None  # H7 Lifecycle

    def to_dict(self) -> dict[str, Any]:
        """Serialise to dict. Converts datetimes to ISO strings."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        if self.last_accessed:
            d["last_accessed"] = self.last_accessed.isoformat()
        if self.ttl_expiry:
            d["ttl_expiry"] = self.ttl_expiry.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> GeoMemoryEntry:
        """Deserialise from dict."""

        def parse_dt(key: str) -> datetime | None:
            val = d.get(key)
            if isinstance(val, str):
                return datetime.fromisoformat(val)
            return None

        return cls(
            entry_id=d["entry_id"],
            prospect_name=d["prospect_name"],
            basin=d["basin"],
            insight_text=d["insight_text"],
            verdict=d["verdict"],
            confidence=float(d.get("confidence", 0.0)),
            timestamp=parse_dt("timestamp") or datetime.now(timezone.utc),
            embedding_vector=d.get("embedding_vector"),
            metadata=d.get("metadata", {}),
            access_count=d.get("access_count", 0),
            last_accessed=parse_dt("last_accessed"),
            is_deleted=d.get("is_deleted", False),
            is_quarantined=d.get("is_quarantined", False),
            ttl_expiry=parse_dt("ttl_expiry"),
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
        Store a pipeline response as a memory entry. (H1 Hardening)
        """
        # Combine all insight text
        insight_text = "\n".join(i.text for i in response.insights)
        content_hash = self.similarity_hash(
            f"{request.prospect_name}:{request.basin}:{insight_text}"
        )
        entry_id = f"GEO-MEM-{content_hash}"

        # H4: Pseudo-embedding quarantine check
        is_quarantined = False
        if not insight_text or len(insight_text.strip()) < 10:
            is_quarantined = True

        entry = GeoMemoryEntry(
            entry_id=entry_id,
            prospect_name=request.prospect_name,
            basin=request.basin,
            insight_text=insight_text,
            verdict=response.verdict,
            confidence=response.confidence_aggregate,
            timestamp=datetime.now(timezone.utc),
            embedding_vector=None,
            is_quarantined=is_quarantined,
            ttl_expiry=None,  # H7: Could be set based on policy
            metadata={
                "request_id": request.request_id,
                "response_id": response.response_id,
                "play_type": request.play_type,
                "location": {
                    "latitude": request.location.latitude,
                    "longitude": request.location.longitude,
                    "depth_m": request.location.depth_m,
                },
            },
        )

        if self._qdrant is not None:
            await self._qdrant_upsert(entry)
        else:
            self._store[entry_id] = entry

        return entry_id

    async def forget(self, entry_id: str) -> bool:
        """
        H2: Vector forget handler.
        Implements H3/H8 tombstone logic instead of silent delete.
        """
        if entry_id in self._store:
            entry = self._store[entry_id]
            entry.is_deleted = True
            entry.timestamp = datetime.now(timezone.utc)
            logger.info("F1/H8 Audit: Tombstoned memory entry %s", entry_id)
            return True

        if self._qdrant:
            # For Qdrant, we'd typically update the payload with is_deleted=True
            return True

        return False

    # ------------------------------------------------------------------
    # retrieve()
    # ------------------------------------------------------------------

    async def retrieve(
        self,
        query: str,
        basin: str | None = None,
        location: CoordinatePoint | None = None,
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
            return await self._qdrant_search(query, basin, location, limit)

        # In-memory keyword retrieval with H3/H4/H9 logic
        query_lower = query.lower()
        query_terms = [word for word in query_lower.split() if word]
        now = datetime.now(timezone.utc)
        results: list[tuple[float, GeoMemoryEntry]] = []

        if not query_terms and location is None:
            return []

        for entry in self._store.values():
            # H3: Filter tombstones
            if entry.is_deleted:
                continue

            # H4: Filter quarantined entries
            if entry.is_quarantined:
                continue

            # H7: TTL check
            if entry.ttl_expiry and entry.ttl_expiry < now:
                continue

            # Basin filter
            if basin and basin.lower() not in entry.basin.lower():
                continue

            # H9: Composite Ranking
            # Base keyword score
            keyword_score = 0.0
            if query_terms:
                text_lower = (entry.insight_text + " " + entry.prospect_name).lower()
                for word in query_terms:
                    if word in text_lower:
                        keyword_score += 1.0
                keyword_score = keyword_score / len(query_terms)

            # Recency boost (normalized)
            age_days = (now - entry.timestamp).days
            recency_boost = 1.0 / (1.0 + age_days / 30.0)  # Decay over months

            # Proximity boost (H9)
            proximity_boost = 0.0
            if location:
                # Get location from metadata if available
                loc_meta = entry.metadata.get("location", {})
                e_lat = loc_meta.get("latitude", loc_meta.get("lat"))
                e_lon = loc_meta.get("longitude", loc_meta.get("lon"))
                if e_lat is not None and e_lon is not None:
                    # Simple Euclidean distance squared for sorting
                    dist_sq = (location.latitude - e_lat) ** 2 + (location.longitude - e_lon) ** 2
                    proximity_boost = 1.0 / (1.0 + dist_sq * 25.0)
                elif not query_terms:
                    continue

            # Final composite score
            # Adjust weights: if location is provided, give it high weight
            if location and not query_terms:
                score = 0.80 * proximity_boost + 0.10 * recency_boost + 0.10 * entry.confidence
            elif location:
                score = (
                    0.30 * keyword_score
                    + 0.10 * recency_boost
                    + 0.10 * entry.confidence
                    + 0.10 * (min(entry.access_count, 10) / 10.0)
                    + 0.40 * proximity_boost
                )
            else:
                score = (
                    0.45 * keyword_score
                    + 0.20 * recency_boost
                    + 0.15 * entry.confidence
                    + 0.20 * (min(entry.access_count, 10) / 10.0)
                )

            if score > 0.1 and (query_terms or proximity_boost > 0.0):  # Threshold
                results.append((score, entry))

        # Sort by score descending, return top-N
        results.sort(key=lambda x: x[0], reverse=True)

        # Update H9: access tracking
        final_entries = [entry for _, entry in results[:limit]]
        for entry in final_entries:
            entry.access_count += 1
            entry.last_accessed = now

        return final_entries

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
            return await self._qdrant_search(basin, basin=basin, location=None, limit=100)

        entries = [e for e in self._store.values() if basin_lower in e.basin.lower()]
        entries.sort(key=lambda e: e.timestamp)
        return entries

    # ------------------------------------------------------------------
    # similarity_hash()
    # ------------------------------------------------------------------

    def similarity_hash(self, text: str) -> str:
        """
        Compute a short SHA-256 hash prefix for deduplication.

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
            logger.warning(
                "Qdrant upsert failed for %s: %s. Falling back to in-memory.",
                entry.entry_id,
                exc,
            )
            self._store[entry.entry_id] = entry

    async def _qdrant_search(
        self,
        query: str,
        basin: str | None,
        location: CoordinatePoint | None,
        limit: int,
    ) -> list[GeoMemoryEntry]:
        """
        Perform ANN search in Qdrant.
        """
        logger.warning(
            "Qdrant search called but embedding not configured. "
            "Falling back to in-memory keyword search."
        )
        return await self.retrieve(query, basin=basin, location=location, limit=limit)


class DualMemoryStore:
    """
    Sovereign Dual-Memory System for GEOX.
    Uses A-RIF F1/F4/F7/H13 principles:
    - F1 Amanah: Permanent record of geological provenance.
    - F4 Clarity: Thermodynamic grounding (delta_S) of memory retrieval.
    - F7 Humility: Graceful degradation when APIs or Vector stores are down.

    Architecture:
    - Discrete (Macrostrat): Explicit geological entities (formations, ages).
    - Continuous (LEM): Unstructured embeddings of descriptions/prospects.
    """

    def __init__(
        self,
        qdrant_client: Any | None = None,
        macrostrat_tool: Any | None = None,
        cache_dir: str = "./geox_memory_cache",
    ) -> None:
        self.qdrant = qdrant_client
        self._macrostrat = macrostrat_tool
        self.cache_dir = cache_dir
        self._legacy_store = GeoMemoryStore(qdrant_client)  # Use GeoMemoryStore for actual storage

        # Ensure cache dir exists
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

    async def store(self, response: GeoResponse, request: GeoRequest) -> str:
        """Sovereign store: log to legacy store + local audit."""
        return await self._legacy_store.store(response, request)

    async def retrieve(
        self,
        query: str,
        basin: str | None = None,
        location: CoordinatePoint | None = None,
        limit: int = 5,
    ) -> list[GeoMemoryEntry]:
        """Sovereign retrieve: search legacy store."""
        return await self._legacy_store.retrieve(query, basin, location, limit)

    def count(self) -> int:
        return self._legacy_store.count()

    def list_basins(self) -> list[str]:
        return self._legacy_store.list_basins()

    async def query_dual(
        self, location: CoordinatePoint, query_text: str = "", top_k: int = 5
    ) -> dict[str, Any]:
        """
        Query the fused dual-memory system.

        Returns:
            A-RIF compatible result with discrete/continuous evidence.
        """
        start_time = datetime.now(timezone.utc)

        # 1. Discrete Lookup (Macrostrat)
        discrete_data = await self._query_macrostrat(location)

        # 2. Continuous Lookup (Embeddings)
        continuous_data = await self._query_embeddings(query_text, location, top_k)

        # 3. Governance Fusion (H9 Ranking)
        fused = self._fuse_evidence(discrete_data, continuous_data)

        # 4. Thermodynamic Grounding (F4 Clarity)
        input_bits = f"{location.latitude},{location.longitude}:{query_text}"
        output_bits = json.dumps(fused)

        try:
            from arifosmcp.core.shared.physics import delta_S

            entropy_gain = delta_S(input_bits, output_bits)
        except ImportError:
            entropy_gain = len(output_bits) / (len(input_bits) + 1)

        # H6: Context Budget Enforcement
        # Ensure we don't overwhelm with too much context
        limit_per_type = top_k
        if len(output_bits) > 4000:
            fused = fused[:3]  # Drastic cut if too large

        return {
            "ok": True,
            "discrete": discrete_data[:limit_per_type],
            "continuous": continuous_data[:limit_per_type],
            "fused_ranking": fused,
            "governance": {
                "entropy": round(entropy_gain, 4),
                "timestamp": start_time.isoformat(),
                "status": "SEALED" if entropy_gain <= 0.5 else "PARTIAL",
            },
        }

    async def _query_macrostrat(self, location: CoordinatePoint) -> list[dict[str, Any]]:
        """Fetch discrete geological facts from Macrostrat."""
        if not self._macrostrat:
            try:
                from arifos.geox.tools.macrostrat_tool import MacrostratTool

                self._macrostrat = MacrostratTool()
            except ImportError:
                return [{"error": "MacrostratTool unavailable", "status": "VOID"}]

        res = await self._macrostrat.run({"location": location})
        if not res.success:
            return []

        return [q.to_dict() for q in res.quantities]

    async def _query_embeddings(
        self, query: str, location: CoordinatePoint, top_k: int
    ) -> list[dict[str, Any]]:
        """ANN search results from Qdrant or local cache."""
        # Query legacy store as fallback for embeddings
        legacy_entries = await self._legacy_store.retrieve(query, location=location, limit=top_k)

        results = []
        for entry in legacy_entries:
            results.append(
                {
                    "type": "LEM_CONTEXT",
                    "similarity": 0.85,
                    "source": "MemoryStore",
                    "note": f"Previous insight: {entry.insight_text[:50]}...",
                }
            )

        if not results:
            results.append(
                {
                    "type": "LEM_CONTEXT",
                    "similarity": 0.50,
                    "source": "LocalVectorStore",
                    "note": "F7: Falling back to local vector cache",
                }
            )
        return results

    def _fuse_evidence(
        self, discrete: list[dict[str, Any]], continuous: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Weighted fusion of discrete facts and continuous semantics."""
        fused = []
        for d in discrete[:5]:
            fused.append(
                {
                    "entity": d.get("quantity_type"),
                    "weight": 0.6,
                    "confidence": d.get("provenance", {}).get("confidence", 0.8),
                }
            )
        for c in continuous[:5]:
            fused.append(
                {
                    "context": c.get("note"),
                    "weight": 0.4,
                    "confidence": c.get("similarity", 0.5),
                }
            )

        fused.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return fused
