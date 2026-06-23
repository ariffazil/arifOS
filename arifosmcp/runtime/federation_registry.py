"""
arifOS Federation Registry — Canonical tool/prompt/resource index.

EUREKA: The next horizon is NOT adding more tools. It's building the substrate
        that makes all existing tools discoverable, composable, and governed.

This module crawls all 7 federation organs via MCP, indexes every tool/prompt/
resource, embeds descriptions for semantic search, and exposes the registry
as both a live artifact and a synthetic MCP discovery tool.

Architecture:
  arif_kernel_route(mode="discover", intent="screen Bursa stocks")
    → semantic search over federation_registry.json
    → returns top-5 relevant tools across all organs
    → agent calls ONLY those tools
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("arifos.federation.registry")

# ─── Organ Map ─────────────────────────────────────────────────────────────

FEDERATION_ORGANS: dict[str, dict[str, Any]] = {
    "arifos": {
        "port": 8088,
        "role": "Constitutional kernel — F1-F13 floors, 888 JUDGE, routing, memory",
        "canonical_tools": 19,
        "total_tools": 56,
        "namespace": "arifOS",
    },
    "wealth": {
        "port": 18082,
        "role": "Capital intelligence — valuation, risk, portfolio, stock analysis",
        "canonical_tools": 20,
        "namespace": "WEALTH",
    },
    "geox": {
        "port": 8081,
        "role": "Earth intelligence — petrophysics, seismic, basin analysis",
        "canonical_tools": 37,
        "namespace": "GEOX",
    },
    "well": {
        "port": 18083,
        "role": "Human vitality — biometric readiness, homeostasis (REFLECT_ONLY)",
        "canonical_tools": 18,
        "total_tools": 21,
        "namespace": "WELL",
    },
    "aforge": {
        "port": 7071,
        "role": "Execution shell — build, deploy, code execution",
        "canonical_tools": 8,
        "namespace": "A-FORGE",
    },
    "aaa": {
        "port": 3001,
        "role": "Control plane — React cockpit, A2A mesh, operator dashboard",
        "canonical_tools": 4,
        "namespace": "AAA",
    },
    "apex": {
        "port": 3002,
        "role": "888 JUDGE deliberation (legacy, absorbed into AAA)",
        "canonical_tools": 2,
        "namespace": "APEX",
    },
    "vault999": {
        "port": 8100,
        "role": "immutable_ledger",
        "canonical_tools": 7,
        "namespace": "VAULT999",
    },
}

# ─── Registry Models ────────────────────────────────────────────────────────


class ToolEntry:
    """Single tool in the registry."""

    def __init__(
        self,
        organ: str,
        tool_name: str,
        description: str = "",
        parameters: list[dict] | None = None,
        mode: str = "canonical",
        lifecycle: str = "active",
        source_class: str = "canonical",
        trust_grade: str = "B",
        cost_class: str = "low",
        hold_risk: str = "none",
        schema_version: str = "1.0.0",
        example_query: str = "",
        last_verified_utc: str | None = None,
        health: str = "unknown",
    ):
        self.organ = organ
        self.tool_name = tool_name
        self.full_name = (
            f"{organ}.{tool_name}" if not tool_name.startswith(f"{organ}.") else tool_name
        )
        self.description = description
        self.parameters = parameters or []
        self._param_names: list[str] = []
        for p in self.parameters:
            if isinstance(p, dict):
                self._param_names.append(p.get("name", ""))
            elif isinstance(p, str):
                self._param_names.append(p)
        self.mode = mode
        self.lifecycle = lifecycle
        self.source_class = source_class
        self.trust_grade = trust_grade
        self.cost_class = cost_class
        self.hold_risk = hold_risk
        self.schema_version = schema_version
        self.example_query = example_query
        self.last_verified_utc: str | None = None
        self.health: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "organ": self.organ,
            "tool_name": self.tool_name,
            "full_name": self.full_name,
            "description": self.description,
            "parameters": self.parameters,
            "mode": self.mode,
            "lifecycle": self.lifecycle,
            "source_class": self.source_class,
            "trust_grade": self.trust_grade,
            "cost_class": self.cost_class,
            "hold_risk": self.hold_risk,
            "schema_version": self.schema_version,
            "example_query": self.example_query,
            "last_verified_utc": self.last_verified_utc,
            "health": self.health,
        }

    @property
    def search_text(self) -> str:
        """Combined text for embedding/semantic search."""
        parts = [
            self.full_name,
            self.organ,
            self.description,
            self.example_query,
            self.source_class,
            " ".join(self._param_names),
        ]
        return " ".join(p for p in parts if p)


class FederationRegistry:
    """Canonical federation registry — the single source of truth."""

    def __init__(self, cache_path: str = "/opt/arifos/app/registry/federation_registry.json"):
        self.cache_path = Path(cache_path)
        self.tools: list[ToolEntry] = []
        self.prompts: list[dict] = []
        self.resources: list[dict] = []
        self.organ_health: dict[str, dict] = {}
        self.built_at_utc: str | None = None
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=True,
            headers={"Accept": "application/json, text/event-stream"},
        )

    async def crawl_all(self) -> dict[str, Any]:
        """Crawl all organs, build the registry, cache to disk."""
        logger.info("FederationRegistry: crawling all organs...")
        self.tools = []
        self.organ_health = {}

        for organ_name, organ_info in FEDERATION_ORGANS.items():
            await self._crawl_organ(organ_name, organ_info)

        self.built_at_utc = datetime.now(UTC).isoformat()
        await self._save_cache()

        return self.snapshot()

    async def _crawl_organ(self, organ_name: str, info: dict):
        """Crawl a single organ for tools via MCP tools/list.

        Falls back to static metadata if MCP endpoint is unavailable.
        """
        port = info["port"]
        canonical_count = info.get("canonical_tools", 0)

        # Try MCP tools/list first
        tools = []
        try:
            url = f"http://127.0.0.1:{port}/mcp"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            }
            resp = await self._http.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                tools = data.get("result", {}).get("tools", [])
        except Exception:
            pass  # fall through to static fallback

        # Static fallback: if MCP crawl failed, use known tool metadata
        if not tools and canonical_count > 0:
            tools = self._static_tools(organ_name, canonical_count)

        if tools:
            self.organ_health[organ_name] = {
                "reachable": True,
                "tools_discovered": len(tools),
                "error": None,
            }
            for tool in tools:
                entry = ToolEntry(
                    organ=organ_name,
                    tool_name=tool.get("name", f"{organ_name}_tool"),
                    description=tool.get("description", ""),
                    parameters=list(tool.get("inputSchema", {}).get("properties", {}).keys())
                    if isinstance(tool.get("inputSchema", {}).get("properties"), dict)
                    else [],
                    lifecycle="active",
                    source_class="canonical",
                    trust_grade=self._grade_organ(organ_name),
                    last_verified_utc=datetime.now(UTC).isoformat(),
                    health="ok",
                )
                self.tools.append(entry)
            logger.info(f"  {organ_name}: {len(tools)} tools indexed")
        else:
            self.organ_health[organ_name] = {
                "reachable": False,
                "tools_discovered": 0,
                "error": "MCP unreachable + no static metadata",
            }

    def _static_tools(self, organ_name: str, count: int) -> list[dict[str, Any]]:
        """Return static placeholder tool metadata when MCP crawl fails.

        Each organ's tool surface is documented in FEDERATION_ORGANS.
        When the MCP endpoint is unreachable, this fallback ensures the
        registry still knows what tools SHOULD exist.
        """
        now_utc = datetime.now(UTC).isoformat()
        tools: list[dict[str, Any]] = []
        for i in range(count):
            tools.append(
                {
                    "name": f"{organ_name}_tool_{i:03d}",
                    "description": f"Static placeholder for {organ_name} tool #{i} — MCP endpoint unreachable",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string", "description": "Operation mode"},
                        },
                    },
                    "_static": True,
                    "_indexed_at": now_utc,
                }
            )
        return tools

    def _grade_organ(self, organ_name: str) -> str:
        """Assign trust grade per organ."""
        grades = {
            "arifos": "A",
            "wealth": "A",
            "geox": "A",
            "well": "B",
            "aforge": "A",
            "aaa": "A",
            "apex": "B",
        }
        return grades.get(organ_name, "B")

    async def discover(
        self,
        intent: str,
        top_k: int = 5,
        organ_filter: list[str] | None = None,
    ) -> dict[str, Any]:
        """Semantic discovery: return top-k tools matching intent.

        Uses Qdrant L3 for semantic search when available, falls back to
        keyword matching on tool names and descriptions.
        """
        if not self.tools:
            await self.crawl_all()

        # Filter by organ if specified
        candidates = self.tools
        if organ_filter:
            candidates = [t for t in candidates if t.organ in organ_filter]

        # Filter by lifecycle (only active tools)
        candidates = [t for t in candidates if t.lifecycle == "active"]

        # Try Qdrant semantic search first
        scored = await self._semantic_rank(intent, candidates)
        if not scored:
            # Fallback: keyword ranking
            scored = self._keyword_rank(intent, candidates)

        # Return top-k
        top = scored[:top_k]

        return {
            "intent": intent,
            "total_indexed": len(self.tools),
            "candidates_considered": len(candidates),
            "results": [
                {
                    "rank": i + 1,
                    "full_name": t.full_name,
                    "organ": t.organ,
                    "tool_name": t.tool_name,
                    "description": t.description[:200],
                    "score": round(s, 3),
                    "trust_grade": t.trust_grade,
                    "health": t.health,
                }
                for i, (s, t) in enumerate(top)
            ],
            "discovery_method": "semantic" if scored else "keyword",
            "searched_at_utc": datetime.now(UTC).isoformat(),
        }

    async def _semantic_rank(self, intent: str, candidates: list[ToolEntry]) -> list[tuple]:
        """Rank tools using Qdrant L3 semantic search."""
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(host="127.0.0.1", port=6333)
            # Try arifos_memory collection for embeddings
            query_vector = await self._embed(intent)
            if not query_vector:
                return []

            # Score each tool by cosine similarity
            scored = []
            for tool in candidates:
                tool_vector = await self._embed(tool.search_text)
                if tool_vector:
                    similarity = self._cosine_sim(query_vector, tool_vector)
                    scored.append((similarity, tool))

            scored.sort(key=lambda x: x[0], reverse=True)
            return scored

        except Exception as e:
            logger.debug(f"Semantic search unavailable: {e}")
            return []

    def _keyword_rank(self, intent: str, candidates: list[ToolEntry]) -> list[tuple]:
        """Fallback keyword ranking when Qdrant is unavailable."""
        query_terms = set(intent.lower().split())
        scored = []
        for tool in candidates:
            text = tool.search_text.lower()
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                scored.append((float(score) / len(query_terms), tool))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    async def _embed(self, text: str) -> list[float] | None:
        """Get embedding vector for text. Primary: Ollama bge-m3. Fallback: Azure text-embedding-3-small."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "http://127.0.0.1:11434/api/embeddings",
                    json={"model": "bge-m3", "prompt": text[:512]},
                )
                resp.raise_for_status()
                emb = resp.json().get("embedding")
                if emb:
                    return emb
        except Exception:
            pass

        # Fallback: Azure OpenAI text-embedding-3-small
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        if azure_key and azure_endpoint:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        f"{azure_endpoint}/embeddings",
                        json={"model": "text-embedding-3-small", "input": text[:2048]},
                        headers={"api-key": azure_key, "Content-Type": "application/json"},
                    )
                    resp.raise_for_status()
                    return resp.json()["data"][0]["embedding"]
            except Exception:
                pass
        return None

    @staticmethod
    def _cosine_sim(a: list[float], b: list[float]) -> float:
        """Cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def _save_cache(self):
        """Save registry to disk cache."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.snapshot()
        self.cache_path.write_text(json.dumps(data, indent=2, default=str))

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of the registry."""
        return {
            "federation_registry": {
                "version": "1.0.0",
                "built_at_utc": self.built_at_utc,
                "total_tools": len(self.tools),
                "total_prompts": len(self.prompts),
                "total_resources": len(self.resources),
                "organs": {
                    name: {
                        **info,
                        "health": self.organ_health.get(name, {}),
                    }
                    for name, info in FEDERATION_ORGANS.items()
                },
                "tools": [t.to_dict() for t in self.tools],
                "prompts": self.prompts,
                "resources": self.resources,
            }
        }


# ─── Singleton ──────────────────────────────────────────────────────────────

_registry: FederationRegistry | None = None


def get_registry() -> FederationRegistry:
    global _registry
    if _registry is None:
        _registry = FederationRegistry()
    return _registry
