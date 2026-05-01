import os
import uuid
import logging
import asyncio
from typing import Any, List, Optional
import httpx
import asyncpg

logger = logging.getLogger("memory_engine")

try:
    from supabase import create_client as supabase_create_client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class MemoryEngine:
    def __init__(
        self,
        postgres_url: str,
        qdrant_url: str = "http://qdrant:6333",
        ollama_url: str = "http://ollama:11434",
        embedding_model: str = "bge-m3",
        supabase_url: str | None = None,
        supabase_key: str | None = None,
    ):
        self.postgres_url = postgres_url
        self.qdrant_url = os.getenv("QDRANT_URL", qdrant_url)
        self.ollama_url = os.getenv("OLLAMA_URL", ollama_url)
        self.embedding_model = os.getenv("EMBEDDING_MODEL", embedding_model)
        self._pg_pool = None

        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self._supabase_client = None
        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            try:
                self._supabase_client = supabase_create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.warning(f"Supabase init failed: {e}")

        self._qdrant_client = None
        if QDRANT_AVAILABLE:
            try:
                self._qdrant_client = QdrantClient(url=self.qdrant_url)
            except Exception as e:
                logger.warning(f"Qdrant init failed: {e}")

        self._http_client = httpx.AsyncClient(timeout=30.0)

    async def _get_pg_pool(self):
        if self._pg_pool is None:
            self._pg_pool = await asyncpg.create_pool(self.postgres_url)
        return self._pg_pool

    async def get_embedding(self, text: str) -> List[float]:
        """Call Ollama BGE-M3 to get embedding vector."""
        try:
            response = await self._http_client.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise

    async def _write_supabase_memory(
        self,
        memory_id: str,
        tier: str,
        content: str,
        metadata: dict[str, Any],
        session_id: str | None,
        qdrant_id: str,
        vector: List[float] | None,
    ) -> None:
        """Write memory record to Supabase arifosmcp_memory_records.

        Dual-write target: Supabase is canonical cloud store.
        Local postgres + Qdrant remain as VPS air-gap fallback.
        Failures are logged but do not block the operation.
        """
        if not self._supabase_client:
            logger.debug("Supabase client not configured, skipping cloud write")
            return

        try:
            record = {
                "memory_id": memory_id,
                "type": tier,
                "subject": content[:200] if content else "",
                "content": content,
                "confidence": 1.0,
                "source": "memory_engine",
                "session_id": session_id,
                "status": "active",
                "version": 1,
                "revocation_possible": tier not in ("sacred", "canon"),
            }
            self._supabase_client.table("arifosmcp_memory_records").insert(record).execute()
            logger.info(f"Supabase memory write OK: {memory_id}")
        except Exception as e:
            logger.warning(f"Supabase memory write failed (non-fatal): {e}")

    async def execute(self, operation: str, memory: dict[str, Any], tier: str) -> dict[str, Any]:
        """Execute memory operation."""
        if operation == "store":
            return await self.store(memory, tier)
        elif operation == "retrieve":
            return await self.retrieve(memory.get("query", ""), tier, memory.get("limit", 5))
        elif operation == "forget":
            return await self.forget(memory.get("id"), tier)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def store(self, memory: dict[str, Any], tier: str) -> dict[str, Any]:
        """Store memory in local Postgres + Qdrant (primary), Supabase (cloud dual-write)."""
        text = memory.get("text", "")
        metadata = memory.get("metadata", {})
        session_id = memory.get("session_id")
        memory_id = str(uuid.uuid4())
        qdrant_id = str(uuid.uuid4())

        vector = None
        try:
            vector = await self.get_embedding(text)
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")

        pool = await self._get_pg_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO memory_store (id, tier, text, metadata, qdrant_id, session_id)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, epoch, created_at
                """,
                uuid.UUID(memory_id),
                tier,
                text,
                metadata,
                uuid.UUID(qdrant_id) if vector else None,
                session_id,
            )
            pg_id = str(row["id"])

        if vector and self._qdrant_client:
            asyncio.create_task(
                self._upsert_qdrant(
                    tier,
                    qdrant_id,
                    vector,
                    {"text": text, "pg_id": pg_id, "tier": tier, "metadata": metadata},
                )
            )

        asyncio.create_task(
            self._write_supabase_memory(
                memory_id, tier, text, metadata, session_id, qdrant_id, vector
            )
        )

        return {"status": "success", "postgres_id": pg_id, "qdrant_id": qdrant_id, "tier": tier}

    async def _upsert_qdrant(
        self, tier: str, qdrant_id: str, vector: List[float], payload: dict[str, Any]
    ):
        if not self._qdrant_client:
            return
        try:
            collection_name = f"arifos_vault_{tier}"
            self._qdrant_client.upsert(
                collection_name=collection_name,
                points=[qmodels.PointStruct(id=qdrant_id, vector=vector, payload=payload)],
            )
        except Exception as e:
            logger.warning(f"Qdrant upsert failed for tier {tier}: {e}")

    async def retrieve(
        self, query: str, tier: Optional[str] = None, limit: int = 5
    ) -> dict[str, Any]:
        """Retrieve memories via semantic search (Qdrant primary, Postgres fallback)."""
        if not query:
            return {"memories": []}

        all_results = []

        if self._qdrant_client:
            try:
                vector = await self.get_embedding(query)
            except Exception as e:
                logger.warning(f"Embedding failed for retrieve: {e}")
                return {"memories": [], "error": str(e)}

            tiers_to_search = (
                [tier] if tier else ["ephemeral", "working", "canon", "sacred", "quarantine"]
            )

            for t in tiers_to_search:
                try:
                    collection_name = f"arifos_vault_{t}"
                    search_result = self._qdrant_client.query_points(
                        collection_name=collection_name, query=vector, limit=limit
                    )
                    for res in search_result.points:
                        all_results.append(
                            {
                                "qdrant_id": res.id,
                                "score": res.score,
                                "pg_id": res.payload.get("pg_id"),
                                "tier": t,
                            }
                        )
                except Exception as e:
                    logger.warning(f"Qdrant search failed for tier {t}: {e}")

        if not all_results:
            pool = await self._get_pg_pool()
            async with pool.acquire() as conn:
                query_text = "SELECT id, tier, text, metadata, epoch, created_at FROM memory_store WHERE deleted_at IS NULL"
                args = []
                if tier:
                    query_text += " AND tier = $1"
                    args.append(tier)
                query_text += " ORDER BY created_at DESC LIMIT $%d" % (len(args) + 1)
                rows = await conn.fetch(query_text, *args)
                return {
                    "memories": [
                        {
                            "id": str(row["id"]),
                            "tier": row["tier"],
                            "text": row["text"],
                            "metadata": row["metadata"],
                            "epoch": row["epoch"],
                            "created_at": row["created_at"].isoformat()
                            if row["created_at"]
                            else None,
                        }
                        for row in rows[:limit]
                    ]
                }

        all_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = all_results[:limit]

        pg_ids = [uuid.UUID(res["pg_id"]) for res in top_results if res.get("pg_id")]
        if not pg_ids:
            return {"memories": []}

        pool = await self._get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, tier, text, metadata, epoch, created_at FROM memory_store WHERE id = ANY($1) AND deleted_at IS NULL",
                pg_ids,
            )
            pg_records = {str(row["id"]): dict(row) for row in rows}

            final_memories = []
            for res in top_results:
                pid = res["pg_id"]
                if pid in pg_records:
                    record = pg_records[pid]
                    record["created_at"] = record["created_at"].isoformat()
                    record["score"] = res["score"]
                    final_memories.append(record)

        return {"memories": final_memories}

    async def forget(self, memory_id: str, tier: str) -> dict[str, Any]:
        """Soft-delete memory in Postgres, quarantine in Qdrant, update Supabase."""
        if tier == "sacred":
            return {
                "status": "888_HOLD",
                "reason": "Sacred memories require human confirmation for forget operation",
                "memory_id": memory_id,
            }

        pool = await self._get_pg_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE memory_store SET deleted_at = NOW() WHERE id = $1 RETURNING qdrant_id",
                uuid.UUID(memory_id),
            )
            if not row:
                return {"status": "error", "message": "Memory not found"}
            qdrant_id = str(row["qdrant_id"])

        if qdrant_id and self._qdrant_client:
            asyncio.create_task(self._quarantine_qdrant(tier, qdrant_id))

        if self._supabase_client:
            asyncio.create_task(self._supabase_soft_delete_memory(memory_id))

        return {"status": "success", "message": f"Memory {memory_id} moved to quarantine"}

    async def _supabase_soft_delete_memory(self, memory_id: str) -> None:
        if not self._supabase_client:
            return
        try:
            self._supabase_client.table("arifosmcp_memory_records").update(
                {"status": "quarantined"}
            ).eq("memory_id", memory_id).execute()
        except Exception as e:
            logger.warning(f"Supabase memory soft-delete failed (non-fatal): {e}")

    async def _quarantine_qdrant(self, old_tier: str, qdrant_id: str):
        if not self._qdrant_client:
            return
        try:
            old_collection = f"arifos_vault_{old_tier}"
            points = self._qdrant_client.retrieve(collection_name=old_collection, ids=[qdrant_id])
            if not points:
                return
            point = points[0]
            self._qdrant_client.upsert(
                collection_name="arifos_vault_quarantine",
                points=[
                    qmodels.PointStruct(
                        id=qdrant_id,
                        vector=point.vector,
                        payload={**point.payload, "original_tier": old_tier},
                    )
                ],
            )
            self._qdrant_client.delete(
                collection_name=old_collection,
                points_selector=qmodels.PointIdsList(points=[qdrant_id]),
            )
        except Exception as e:
            logger.warning(f"Qdrant quarantine move failed: {e}")

    async def close(self):
        if self._pg_pool:
            await self._pg_pool.close()
        await self._http_client.aclose()
