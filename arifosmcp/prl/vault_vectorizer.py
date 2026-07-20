"""
vault_vectorizer.py — PRL Phase 1: VAULT999 → Qdrant Vector Index
═══════════════════════════════════════════════════════════════════

Reads the VAULT999 outcomes.jsonl ledger, embeds sealed verdict payloads
with BAAI/bge-m3, and stores them in Qdrant collection ``arifos_precedent``.

Each Qdrant point carries payload fields for the Dual-Gate:
  - blast_radius: L1_LOCAL | L2_SYSTEM | L3_CRITICAL
  - seal_id: VAULT999 entry_id
  - timestamp: ISO 8601 seal timestamp
  - payload_summary: truncated verdict payload (≤512 chars)
  - session_id: governing session

Backfill mode: reads ALL historical entries.  Historical entries without
blast_radius tags default to L2_SYSTEM (safety-first — assume higher risk).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────
COLLECTION_NAME = "arifos_precedent"
VECTOR_SIZE = 1024  # BAAI/bge-m3 — aligned with arifOS L3 semantic memory
EMBEDDING_MODEL = "BAAI/bge-m3"
PRL_TAU_THRESHOLD = 0.95  # Default cosine threshold for precedent match

_VAULT_PATH = os.getenv(
    "VAULT999_PATH",
    os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl",
)
DEFAULT_QDRANT_URL = "http://localhost:6333"


# ── Blast Radius Tags ─────────────────────────────────────────────────────
BLAST_RADIUS_VALUES = {"L1_LOCAL", "L2_SYSTEM", "L3_CRITICAL"}
DEFAULT_BLAST_RADIUS = "L2_SYSTEM"  # Safety-first for unclassified historical entries


class PrecedentVectorizer:
    """Create, seed, and search the VAULT999 precedent vector index in Qdrant."""

    def __init__(self, qdrant_url: str = DEFAULT_QDRANT_URL) -> None:
        self.client = QdrantClient(url=qdrant_url)
        self._encoder = None

    # ── Embedding Model ──────────────────────────────────────────────────

    def _get_encoder(self):
        """Lazy-load SentenceTransformer (BAAI/bge-m3)."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model %s ...", EMBEDDING_MODEL)
            self._encoder = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
        return self._encoder

    # ── Collection Management ────────────────────────────────────────────

    def create_collection(self, recreate: bool = False) -> bool:
        """Ensure ``arifos_precedent`` collection exists in Qdrant.

        Returns True if collection was created (or already existed).
        """
        if recreate:
            self.client.delete_collection(COLLECTION_NAME)
            logger.info("Recreated Qdrant collection: %s", COLLECTION_NAME)

        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection: %s", COLLECTION_NAME)
            return True
        return False

    # ── VAULT999 Reading ─────────────────────────────────────────────────

    def _read_vault_entries(self) -> list[dict[str, Any]]:
        """Read all entries from VAULT999 outcomes.jsonl."""
        vault_path = Path(_VAULT_PATH)
        if not vault_path.exists():
            logger.warning("VAULT999 path not found: %s", vault_path)
            return []

        entries: list[dict[str, Any]] = []
        try:
            with open(vault_path) as f:
                for lineno, line in enumerate(f, 1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        entry = json.loads(stripped)
                        entry["_line"] = lineno
                        entries.append(entry)
                    except json.JSONDecodeError:
                        logger.warning("Skipping non-JSON line %d in %s", lineno, vault_path)
        except OSError as exc:
            logger.error("Failed to read vault: %s", exc)
            return []

        logger.info("Read %d entries from VAULT999", len(entries))
        return entries

    # ── Text Construction for Embedding ───────────────────────────────────

    @staticmethod
    def _build_embedding_text(entry: dict[str, Any]) -> str:
        """Build a canonical text representation for embedding.

        Format: ``verdict: <verdict> | payload: <payload> | domain: <domain>``
        This mirrors the query text format used by prl_gate.py for matching.
        """
        payload = entry.get("payload", "") or ""
        verdict = entry.get("verdict", "SEAL")
        domain = entry.get("domain", "") or entry.get("tool", "") or ""

        parts = [f"verdict: {verdict}"]
        if payload:
            parts.append(f"payload: {payload[:1024]}")
        if domain:
            parts.append(f"domain: {domain}")
        return " | ".join(parts)

    # ── Payload Construction ─────────────────────────────────────────────

    @staticmethod
    def _extract_blast_radius(entry: dict[str, Any]) -> str:
        """Extract blast_radius from vault entry, defaulting to L2_SYSTEM."""
        br = entry.get("blast_radius", "")
        if isinstance(br, str) and br in BLAST_RADIUS_VALUES:
            return br
        # Check nested result dict (SealOutput shape)
        result = entry.get("result", {})
        if isinstance(result, dict):
            br = result.get("blast_radius", "")
            if isinstance(br, str) and br in BLAST_RADIUS_VALUES:
                return br
        return DEFAULT_BLAST_RADIUS

    @staticmethod
    def _build_payload(entry: dict[str, Any], point_id: int) -> dict[str, Any]:
        """Build Qdrant payload for a vault entry."""
        payload_raw = entry.get("payload", "") or ""
        return {
            "seal_id": entry.get("entry_id", f"legacy_{point_id}"),
            "blast_radius": PrecedentVectorizer._extract_blast_radius(entry),
            "timestamp": entry.get("timestamp", ""),
            "verdict": entry.get("verdict", "SEAL"),
            "payload_summary": payload_raw[:512] if isinstance(payload_raw, str) else "",
            "session_id": entry.get("session_id", ""),
            "actor_id": entry.get("actor_id", ""),
            "vault_line": entry.get("_line", 0),
        }

    # ── Backfill ─────────────────────────────────────────────────────────

    def backfill(self, batch_size: int = 128) -> dict[str, Any]:
        """Read all VAULT999 entries and upsert into Qdrant.

        Returns a report with counts and any errors.
        """
        self.create_collection()

        entries = self._read_vault_entries()
        if not entries:
            return {"status": "EMPTY_VAULT", "indexed": 0, "note": "No entries in vault"}

        encoder = self._get_encoder()
        total_indexed = 0
        errors: list[str] = []

        # Process in batches to avoid memory pressure
        for batch_start in range(0, len(entries), batch_size):
            batch = entries[batch_start : batch_start + batch_size]

            try:
                # Build embedding texts
                texts = [self._build_embedding_text(e) for e in batch]
                embeddings = encoder.encode(texts, show_progress_bar=False)

                # Build Qdrant points
                points = []
                for idx, entry in enumerate(batch):
                    global_idx = batch_start + idx
                    points.append(
                        PointStruct(
                            id=global_idx,
                            vector=embeddings[idx].tolist(),
                            payload=self._build_payload(entry, global_idx),
                        )
                    )

                self.client.upsert(collection_name=COLLECTION_NAME, points=points)
                total_indexed += len(points)

            except Exception as exc:
                errors.append(f"Batch {batch_start}-{batch_start + batch_size}: {exc}")
                logger.error("Backfill batch failed: %s", exc)

        report = {
            "status": "OK" if not errors else "PARTIAL",
            "indexed": total_indexed,
            "total_entries": len(entries),
            "errors": errors[:10],
        }

        # Breakdown by blast_radius
        try:
            count_result = self.client.count(collection_name=COLLECTION_NAME)
            report["collection_size"] = count_result.count
        except Exception:
            report["collection_size"] = total_indexed

        logger.info("Backfill complete: %s", {k: v for k, v in report.items() if k != "errors"})
        return report

    # ── Single Entry Upsert (post-seal hook) ─────────────────────────────

    def index_entry(
        self,
        entry: dict[str, Any],
        point_id: int | None = None,
    ) -> bool:
        """Index a single sealed entry into Qdrant (post-seal hook).

        Args:
            entry: VAULT999 entry dict with at minimum: payload, verdict, timestamp
            point_id: Qdrant point ID.  Auto-generated if None.

        Returns True on success.
        """
        self.create_collection()

        encoder = self._get_encoder()
        text = self._build_embedding_text(entry)
        embedding = encoder.encode([text], show_progress_bar=False)[0]

        if point_id is None:
            # Generate from existing collection size
            try:
                point_id = self.client.count(collection_name=COLLECTION_NAME).count
            except Exception:
                point_id = int(datetime.now(timezone.utc).timestamp() * 1000)

        payload = self._build_payload(entry, point_id)

        try:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding.tolist(),
                        payload=payload,
                    )
                ],
            )
            logger.info("Indexed entry %s as point %d", entry.get("entry_id", "?"), point_id)
            return True
        except Exception as exc:
            logger.error("Failed to index entry: %s", exc)
            return False

    # ── Query ─────────────────────────────────────────────────────────────

    def search(
        self,
        query_text: str,
        blast_radius: str | None = None,
        score_threshold: float = PRL_TAU_THRESHOLD,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for precedents matching the query.

        Args:
            query_text: Natural language query (same format as _build_embedding_text)
            blast_radius: Optional payload filter.  If set, only matches entries
                          with the exact blast_radius value.
            score_threshold: Minimum cosine similarity (0-1).  Default 0.95.
            limit: Maximum results to return.

        Returns list of matching precedent payloads, ranked by similarity.
        """
        encoder = self._get_encoder()
        query_vector = encoder.encode([query_text], show_progress_bar=False)[0].tolist()

        # Build optional payload filter
        query_filter = None
        if blast_radius and blast_radius in BLAST_RADIUS_VALUES:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="blast_radius",
                        match=MatchValue(value=blast_radius),
                    )
                ]
            )

        try:
            response = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
            )
        except Exception as exc:
            logger.error("PRL search failed: %s", exc)
            return []

        results = []
        for point in response.points:
            results.append({
                "score": round(point.score, 4),
                "seal_id": point.payload.get("seal_id", ""),
                "blast_radius": point.payload.get("blast_radius", ""),
                "verdict": point.payload.get("verdict", ""),
                "timestamp": point.payload.get("timestamp", ""),
                "payload_summary": point.payload.get("payload_summary", "")[:256],
                "session_id": point.payload.get("session_id", ""),
            })

        return results

    def collection_stats(self) -> dict[str, Any]:
        """Return collection statistics."""
        try:
            count = self.client.count(collection_name=COLLECTION_NAME).count
            return {
                "collection": COLLECTION_NAME,
                "vector_size": VECTOR_SIZE,
                "model": EMBEDDING_MODEL,
                "point_count": count,
                "tau_threshold": PRL_TAU_THRESHOLD,
            }
        except Exception as exc:
            return {"error": str(exc), "collection": COLLECTION_NAME}
