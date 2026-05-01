import asyncio
import json
import logging
import os
import uuid
from typing import Any, cast

import asyncpg
import httpx

logger = logging.getLogger("memory_engine")

try:
    from supabase import create_client as supabase_create_client  # type: ignore[attr-defined]

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


# ── Graphiti MCP Client ──────────────────────────────────────────────────
class GraphitiClient:
    """Minimal MCP SSE client for Graphiti temporal memory."""

    def __init__(self, endpoint: str, host_header: str = "localhost:8000"):
        self.endpoint = endpoint
        self.host_header = host_header
        self.mcp_session_id: str | None = None
        self._http = httpx.AsyncClient(timeout=30.0)
        self._initialized = False

    async def initialize(self) -> bool:
        if self._initialized:
            return True
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "arifosmcp-memory-engine", "version": "2026.4.30"},
                },
            }
            resp = await self._http.post(
                self.endpoint,
                json=payload,
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Host": self.host_header,
                },
            )
            self.mcp_session_id = resp.headers.get("mcp-session-id")
            if not self.mcp_session_id:
                return False
            for line in resp.text.split("\n"):
                line = line.strip()
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if "result" in data:
                        self._initialized = True
                        return True
            return False
        except Exception as e:
            logger.warning(f"Graphiti initialize failed: {e}")
            return False

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self._initialized:
            if not await self.initialize():
                return {"error": "Graphiti not initialized"}
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": self.mcp_session_id or "",
                "Host": self.host_header,
            }
            resp = await self._http.post(self.endpoint, json=payload, headers=headers)
            for line in resp.text.split("\n"):
                line = line.strip()
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if "result" in data:
                        return data["result"]
                    elif "error" in data:
                        return {"error": data["error"]}
            return {"error": "No data in SSE stream"}
        except Exception as e:
            logger.warning(f"Graphiti call_tool {name} failed: {e}")
            return {"error": str(e)}

    async def close(self):
        await self._http.aclose()


# ── Langfuse REST Trace (lightweight, no SDK dependency) ─────────────────
class LangfuseTrace:
    """Lightweight Langfuse v2 REST ingester using httpx."""

    def __init__(self, base_url: str | None = None):
        # Use env var if provided, else default to Cloud if keys look like cloud keys,
        # or local if running in the federation.
        self.base_url = (
            base_url or os.getenv("LANGFUSE_BASE_URL") or "http://langfuse-web:3000"
        ).rstrip("/")
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.enabled = bool(self.public_key and self.secret_key)
        self._http = httpx.AsyncClient(timeout=15.0)

    async def _ingest(self, batch: list[dict[str, Any]]) -> None:
        if not self.enabled:
            return
        try:
            # Langfuse expects /api/public/ingestion for batch uploads
            await self._http.post(
                f"{self.base_url}/api/public/ingestion",
                json={"batch": batch},
                auth=(self.public_key, self.secret_key),
            )
        except Exception as e:
            logger.debug(f"Langfuse ingestion failed (non-fatal): {e}")

    async def trace(
        self,
        name: str,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ):
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()
        trace_id = str(uuid.uuid4())
        if self.enabled:
            body: dict[str, Any] = {
                "id": trace_id,
                "name": name,
                "metadata": metadata or {},
                "timestamp": ts,
            }
            if session_id:
                # Group traces into a Langfuse Session
                body["sessionId"] = session_id
            if tags:
                body["tags"] = tags

            await self._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "trace",
                        "body": body,
                        "timestamp": ts,
                    }
                ]
            )
        return LangfuseSpan(self, trace_id)

    async def close(self):
        await self._http.aclose()


class LangfuseSpan:
    def __init__(
        self, tracer: LangfuseTrace, trace_id: str, parent_observation_id: str | None = None
    ):
        self.tracer = tracer
        self.trace_id = trace_id
        self.parent_observation_id = parent_observation_id

    async def span(self, name: str, input: Any = None, metadata: dict[str, Any] | None = None):
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()
        span_id = str(uuid.uuid4())

        if self.tracer.enabled:
            body: dict[str, Any] = {
                "id": span_id,
                "traceId": self.trace_id,
                "name": name,
                "startTime": ts,
                "input": input,
                "metadata": metadata or {},
            }
            if self.parent_observation_id:
                body["parentObservationId"] = self.parent_observation_id

            await self.tracer._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "span",
                        "body": body,
                        "timestamp": ts,
                    }
                ]
            )
        return LangfuseSpan(self.tracer, self.trace_id, span_id)

    async def generation(
        self,
        name: str,
        model: str | None = None,
        input: Any = None,
        output: Any = None,
        usage: dict[str, int] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()
        gen_id = str(uuid.uuid4())

        if self.tracer.enabled:
            body: dict[str, Any] = {
                "id": gen_id,
                "traceId": self.trace_id,
                "name": name,
                "startTime": ts,
                "model": model,
                "input": input,
                "output": output,
                "usage": usage or {},
                "metadata": metadata or {},
            }
            if self.parent_observation_id:
                body["parentObservationId"] = self.parent_observation_id

            await self.tracer._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "generation",
                        "body": body,
                        "timestamp": ts,
                    }
                ]
            )
        return LangfuseSpan(self.tracer, self.trace_id, gen_id)

    async def update(self, output: Any = None, metadata: dict[str, Any] | None = None):
        """Update the current span/observation with output and final metadata."""
        if not self.parent_observation_id:
            return  # Trace updates not handled here yet

        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()

        if self.tracer.enabled:
            await self.tracer._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "span-patch" if self.parent_observation_id else "trace-patch",
                        "body": {
                            "id": self.parent_observation_id,
                            "endTime": ts,
                            "output": output,
                            "metadata": metadata or {},
                        },
                        "timestamp": ts,
                    }
                ]
            )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.parent_observation_id:
            await self.update()


class MemoryEngine:
    def __init__(
        self,
        postgres_url: str,
        qdrant_url: str = "http://qdrant:6333",
        ollama_url: str = "http://ollama:11434",
        embedding_model: str = "bge-m3",
        supabase_url: str | None = None,
        supabase_key: str | None = None,
        graphiti_url: str = "http://graphiti-mcp:8000/mcp",
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
        self._graphiti = GraphitiClient(os.getenv("GRAPHITI_URL", graphiti_url))
        self._langfuse = LangfuseTrace()

    async def _get_pg_pool(self):
        if self._pg_pool is None:
            self._pg_pool = await asyncpg.create_pool(self.postgres_url)
        return self._pg_pool

    async def get_embedding(self, text: str) -> list[float]:
        """Call Ollama BGE-M3 to get embedding vector."""
        try:
            response = await self._http_client.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            return cast(list[float], data["embedding"])
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
        vector: list[float] | None,
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

        # ── Langfuse Trace ───────────────────────────────────────────────
        trace = await self._langfuse.trace(
            name="memory:store",
            session_id=session_id,
            metadata={"tier": tier, "memory_id": memory_id, "text_len": len(text)},
        )

        import json as _json

        vector = None
        try:
            vector = await self.get_embedding(text)
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")

        _metadata = _json.dumps(metadata) if isinstance(metadata, dict) else metadata

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
                _metadata,
                uuid.UUID(qdrant_id) if vector else None,
                session_id,
            )
            pg_id = str(row["id"])

        # ── Graphiti Temporal Write (fire-and-forget) ────────────────────
        asyncio.create_task(self._graphiti_add(memory_id, text, session_id, tier))

        if vector and self._qdrant_client:
            asyncio.create_task(
                self._upsert_qdrant(
                    tier,
                    qdrant_id,
                    vector,
                    {"text": text, "pg_id": pg_id, "tier": tier, "metadata": metadata},
                )
            )
            # Dual-write to federation_shared so ASI_arifos_bot can read it
            asyncio.create_task(
                self._upsert_federation(
                    qdrant_id,
                    vector,
                    {
                        "text": text,
                        "pg_id": pg_id,
                        "original_tier": tier,
                        "writer_bot": "arifOS_MCP",
                        "session_id": session_id,
                        "metadata": metadata,
                    },
                )
            )

        asyncio.create_task(
            self._write_supabase_memory(
                memory_id, tier, text, metadata, session_id, qdrant_id, vector
            )
        )

        res = {"status": "success", "postgres_id": pg_id, "qdrant_id": qdrant_id, "tier": tier}

        # Patch trace with result
        if self._langfuse.enabled:
            from datetime import datetime, timezone

            ts = datetime.now(timezone.utc).isoformat()
            await self._langfuse._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "trace-patch",
                        "body": {"id": trace.trace_id, "output": res, "endTime": ts},
                        "timestamp": ts,
                    }
                ]
            )

        return res

    async def _upsert_qdrant(
        self, tier: str, qdrant_id: str, vector: list[float], payload: dict[str, Any]
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

    async def _upsert_federation(
        self, qdrant_id: str, vector: list[float], payload: dict[str, Any]
    ):
        """Write to the shared federation collection — visible to both bots."""
        if not self._qdrant_client:
            return
        try:
            self._qdrant_client.upsert(
                collection_name="federation_shared",
                points=[qmodels.PointStruct(id=qdrant_id, vector=vector, payload=payload)],
            )
        except Exception as e:
            logger.warning(f"Federation shared upsert failed: {e}")

    async def _graphiti_add(
        self, memory_id: str, text: str, session_id: str | None, tier: str
    ) -> None:
        """Best-effort temporal graph write; failures are logged but non-blocking."""
        try:
            result = await self._graphiti.call_tool(
                "add_memory",
                {
                    "name": f"memory-{memory_id[:8]}",
                    "episode_body": text,
                    "group_id": session_id or "global",
                    "source": "arifosmcp",
                    "source_description": f"tier:{tier}",
                },
            )
            if isinstance(result, dict) and "error" in result:
                logger.warning(f"Graphiti add_memory error: {result['error']}")
        except Exception as e:
            logger.warning(f"Graphiti add_memory failed: {e}")

    async def retrieve(
        self, query: str, tier: str | None = None, limit: int = 5, session_id: str | None = None
    ) -> dict[str, Any]:
        """Retrieve memories via semantic search (Qdrant) + temporal graph (Graphiti)."""
        if not query:
            return {"memories": []}

        # ── Langfuse Trace ───────────────────────────────────────────────
        trace = await self._langfuse.trace(
            name="memory:retrieve",
            session_id=session_id,
            metadata={"tier": tier, "limit": limit, "query": query},
        )

        all_results = []
        graph_facts: list[dict[str, Any]] = []

        # ── Graphiti Temporal Search ─────────────────────────────────────
        try:
            graph_resp = await self._graphiti.call_tool(
                "search_memory_facts",
                {
                    "query": query,
                    "group_ids": [session_id] if session_id else None,
                    "max_facts": limit,
                },
            )
            if isinstance(graph_resp, dict):
                sc = graph_resp.get("structuredContent")
                if isinstance(sc, dict) and "facts" in sc:
                    graph_facts = sc["facts"]
                elif isinstance(sc, list):
                    graph_facts = sc
                elif "content" in graph_resp:
                    for item in graph_resp["content"]:
                        if item.get("type") == "text":
                            try:
                                parsed = json.loads(item["text"])
                                if isinstance(parsed, list):
                                    graph_facts.extend(parsed)
                                else:
                                    graph_facts.append(parsed)
                            except json.JSONDecodeError:
                                graph_facts.append({"text": item["text"]})
        except Exception as e:
            logger.warning(f"Graphiti search failed: {e}")

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

            # Also search the shared federation collection for cross-bot memory
            try:
                search_result = self._qdrant_client.query_points(
                    collection_name="federation_shared", query=vector, limit=limit
                )
                for res in search_result.points:
                    all_results.append(
                        {
                            "qdrant_id": res.id,
                            "score": res.score,
                            "pg_id": res.payload.get("pg_id"),
                            "tier": res.payload.get("original_tier", "shared"),
                            "writer_bot": res.payload.get("writer_bot", "unknown"),
                            "source": "federation_shared",
                        }
                    )
            except Exception as e:
                logger.warning(f"Federation shared search failed: {e}")

        if not all_results:
            pool = await self._get_pg_pool()
            async with pool.acquire() as conn:
                query_text = (
                    "SELECT id, tier, text, metadata, epoch, created_at "
                    "FROM memory_store WHERE deleted_at IS NULL"
                )
                args = []
                if tier:
                    query_text += " AND tier = $1"
                    args.append(tier)
                query_text += f" ORDER BY created_at DESC LIMIT {len(args) + 1}"
                rows = await conn.fetch(query_text, *args)

                res = {
                    "memories": [
                        {
                            "id": str(row["id"]),
                            "tier": row["tier"],
                            "text": row["text"],
                            "metadata": row["metadata"],
                            "epoch": row["epoch"],
                            "created_at": (
                                row["created_at"].isoformat() if row["created_at"] else None
                            ),
                        }
                        for row in rows[:limit]
                    ],
                    "graph_facts": graph_facts,
                }

                # Patch trace with result
                if self._langfuse.enabled:
                    from datetime import datetime, timezone

                    ts = datetime.now(timezone.utc).isoformat()
                    await self._langfuse._ingest(
                        [
                            {
                                "id": str(uuid.uuid4()),
                                "type": "trace-patch",
                                "body": {
                                    "id": trace.trace_id,
                                    "output": {
                                        "memories_count": len(res["memories"]),
                                        "graph_facts_count": len(graph_facts),
                                    },
                                    "endTime": ts,
                                },
                                "timestamp": ts,
                            }
                        ]
                    )

                return res

        all_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = all_results[:limit]

        # pg_id should be a valid UUID. Non-UUID pg_ids are tolerated but skip
        # Postgres enrichment (F4 clarity, F9 anti-hantu: no crash on malformed data).
        valid_pg_ids = []
        for res in top_results:
            raw_pid = res.get("pg_id")
            if not raw_pid:
                logger.warning(
                    f"Qdrant point {res.get('qdrant_id')} has no pg_id "
                    "— skipping Postgres enrichment"
                )
                continue
            try:
                valid_pg_ids.append(uuid.UUID(str(raw_pid)))
            except (ValueError, AttributeError):
                logger.warning(
                    f"Qdrant point {res.get('qdrant_id')} has malformed pg_id "
                    f"'{raw_pid}' — skipping Postgres enrichment"
                )

        if not valid_pg_ids:
            # No valid Postgres IDs — return Qdrant-only results with a warning
            res = {
                "memories": [
                    {"qdrant_id": res["qdrant_id"], "score": res["score"], "tier": res.get("tier")}
                    for res in top_results
                ],
                "warning": (
                    "No valid pg_ids found; "
                    "returning Qdrant-only results without Postgres enrichment"
                ),
                "graph_facts": graph_facts,
            }

            # Patch trace with result
            if self._langfuse.enabled:
                from datetime import datetime, timezone

                ts = datetime.now(timezone.utc).isoformat()
                await self._langfuse._ingest(
                    [
                        {
                            "id": str(uuid.uuid4()),
                            "type": "trace-patch",
                            "body": {
                                "id": trace.trace_id,
                                "output": {
                                    "memories_count": len(res["memories"]),
                                    "graph_facts_count": len(graph_facts),
                                    "qdrant_only": True,
                                },
                                "endTime": ts,
                            },
                            "timestamp": ts,
                        }
                    ]
                )

            return res

        pool = await self._get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, tier, text, metadata, epoch, created_at "
                "FROM memory_store WHERE id = ANY($1) AND deleted_at IS NULL",
                valid_pg_ids,
            )
            pg_records = {str(row["id"]): dict(row) for row in rows}

            final_memories = []
            for res in top_results:
                raw_pid = res.get("pg_id")
                if not raw_pid:
                    continue
                try:
                    pid = str(uuid.UUID(str(raw_pid)))
                except (ValueError, AttributeError):
                    continue  # already warned above
                if pid in pg_records:
                    record = pg_records[pid]
                    ca = record["created_at"]
                    record["created_at"] = ca.isoformat() if hasattr(ca, "isoformat") else str(ca)
                    record["score"] = res["score"]
                    final_memories.append(record)

        res = {"memories": final_memories, "graph_facts": graph_facts}

        # Patch trace with result
        if self._langfuse.enabled:
            from datetime import datetime, timezone

            ts = datetime.now(timezone.utc).isoformat()
            await self._langfuse._ingest(
                [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "trace-patch",
                        "body": {
                            "id": trace.trace_id,
                            "output": {
                                "memories_count": len(final_memories),
                                "graph_facts_count": len(graph_facts),
                            },
                            "endTime": ts,
                        },
                        "timestamp": ts,
                    }
                ]
            )

        return res

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
        await self._graphiti.close()
        await self._langfuse.close()


_global_langfuse = None


def get_langfuse_tracer() -> LangfuseTrace:
    global _global_langfuse
    if _global_langfuse is None:
        _global_langfuse = LangfuseTrace()
    return _global_langfuse
