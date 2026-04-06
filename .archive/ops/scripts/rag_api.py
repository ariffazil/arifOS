#!/usr/bin/env python3
"""
arifOS RAG API — FastAPI Endpoints for Agents

Provides REST API for agents (Kimi, OpenClaw, Claude Desktop, etc.) to query
the constitutional knowledge base via RAG.

Endpoints:
    POST /rag/query         — Query knowledge base, get contexts
    POST /rag/augment       — Get augmented prompt with context
    GET  /rag/health        — Health check
    POST /rag/search        — Semantic search with filters

Usage:
    curl -X POST http://localhost:8088/rag/query \
        -H "Content-Type: application/json" \
        -d '{"query": "What is F2 floor?", "top_k": 3}'
"""

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent))

from arifos_rag import ConstitutionalRAG

app = FastAPI(
    title="arifOS RAG API",
    description="Constitutional knowledge retrieval for AI agents",
    version="1.0.0",
)

rag = ConstitutionalRAG()


class QueryRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, ge=5, description="Number of results")
    source_filter: str | None = Field(None, description="Filter by source (arifOS, APEX-THEORY)")
    min_score: float = Field(0.0, ge=0.0, description="Minimum relevance score")


class AugmentRequest(BaseModel):
    original_prompt: str = Field(..., description="Original prompt to augment")
    query: str = Field(..., description="Query for context retrieval")
    top_k: int = Field(5, ge=5, description="Number of context chunks")
    source_filter: str | None = Field(None, description="Filter by source")
    context_prefix: str = Field(
        "Relevant context from arifOS constitutional knowledge base:",
        description="Prefix for context section",
    )


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(10, ge=10, description="Number of results")
    source: str | None = Field(None, description="Filter by source")
    min_score: float = Field(0.3, ge=0.3, description="Minimum score threshold")


@app.get("/rag/health")
async def health_check():
    return rag.health_check()


@app.post("/rag/query")
async def query_knowledge_base(request: QueryRequest):
    try:
        result = rag.query_with_metadata(
            query=request.query,
            top_k=request.top_k,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/augment")
async def augment_prompt(request: AugmentRequest):
    try:
        augmented = rag.augment_prompt(
            original_prompt=request.original_prompt,
            query=request.query,
            top_k=request.top_k,
            source_filter=request.source_filter,
            context_prefix=request.context_prefix,
        )
        contexts = rag.retrieve(request.query, request.top_k, request.source_filter)

        return {
            "original_prompt": request.original_prompt,
            "augmented_prompt": augmented,
            "contexts_count": len(contexts),
            "sources": {f"{c.source}/{c.path}": c.score for c in contexts},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/search")
async def semantic_search(request: SearchRequest):
    try:
        contexts = rag.retrieve(
            query=request.query,
            top_k=request.top_k,
            source_filter=request.source,
            min_score=request.min_score,
        )

        return {
            "query": request.query,
            "results": [
                {
                    "source": ctx.source,
                    "path": ctx.path,
                    "content": ctx.content[:1000],
                    "score": ctx.score,
                    "metadata": ctx.metadata,
                }
                for ctx in contexts
            ],
            "total": len(contexts),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rag/collections")
async def list_collections():
    try:
        collections = rag.client.get_collections()
        return {"collections": [{"name": c.name} for c in collections.collections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088)
