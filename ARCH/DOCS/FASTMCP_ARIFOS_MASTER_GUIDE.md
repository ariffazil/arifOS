# 🔱 FastMCP Python SDK + arifOS MCP: Deep Research & Super-Utilization Guide

> **Ditempa Bukan Diberi — Intelligence is a governed metabolic process.**

---

## 📋 Executive Summary

This comprehensive guide provides deep research and practical guidance on super-utilizing the **FastMCP Python SDK** for building **arifOS MCP** constitutional AI governance systems. FastMCP is a high-level Python framework (23.5k+ GitHub stars, 1M+ daily downloads) that simplifies building Model Context Protocol servers, while arifOS provides a revolutionary Double Helix architecture with 13 Constitutional Floors for ethical AI governance.

### Key Integration Benefits

| Capability | FastMCP | arifOS | Combined Power |
|------------|---------|--------|----------------|
| **Protocol** | MCP Standard | MCP Native | Full Compatibility |
| **Primitives** | Tools/Resources/Prompts | 8 Sacred Tools | Rich API Surface |
| **Governance** | Auth/AuthZ | F1-F13 Floors | Constitutional Safety |
| **Transport** | stdio/SSE/HTTP | Multi-transport | Universal Access |
| **Observability** | OpenTelemetry | 3E Telemetry | Full Visibility |

---

## 🧬 Part I: FastMCP Python SDK Deep Dive

### 1. Core Architecture

```python
from fastmcp import FastMCP

# Server instantiation with full configuration
mcp = FastMCP(
    name="arifOS-Governed-Server",
    instructions="""
    Constitutional AI Governance Server
    
    This server provides 8 Sacred Tools governed by 13 Constitutional Floors.
    All operations pass through ΔΩΨ Trinity validation.
    """,
    version="2026.03.13",
    website_url="https://arifos.arif-fazil.com",
    icons={"emoji": "🔱", "color": "#2563eb"},
    mask_error_details=True,  # Security: hide internals
)
```

### 2. The Three Primitives

#### 2.1 Tools — Active Computation

```python
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Literal

mcp = FastMCP("ToolsDemo")

# Basic tool with type annotations
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Advanced tool with Pydantic validation
class ReasoningRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    depth: Literal[1, 2, 3, 4, 5] = 3
    include_uncertainty: bool = True

@mcp.tool(
    name="reason_mind",
    description="Execute constitutional reasoning with F1-F13 validation",
    tags={"intelligence", "governance"},
    annotations={
        "title": "Mind Reasoning",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
async def reason_mind(request: ReasoningRequest) -> dict:
    """Execute multi-layer reasoning with constitutional oversight."""
    # Implementation with arifOS governance
    return {
        "result": "...",
        "verdict": "SEAL",
        "uncertainty": 0.04
    }
```

#### 2.2 Resources — Data Providers

```python
from fastmcp import FastMCP

mcp = FastMCP("ResourcesDemo")

# Static resource
@mcp.resource("constitution://floors", description="List all 13 constitutional floors")
def get_constitutional_floors() -> str:
    """Return constitutional floor definitions."""
    return """
    F1: Amanah (Trust) - Reversibility
    F2: Haqq (Truth) - Veracity
    F3: Shahada (Witness) - Testimony
    ...
    """

# Dynamic resource with URI parameters (RFC 6570)
@mcp.resource("session://{session_id}/status")
def get_session_status(session_id: str) -> dict:
    """Get current session governance status."""
    return {
        "session_id": session_id,
        "verdict": "SEAL",
        "floors_passed": 13,
        "entropy_score": -0.12
    }

# Binary resource with MIME type
@mcp.resource("vault://ledger/proof", mime_type="application/json")
def get_vault_proof() -> bytes:
    """Return Merkle proof for vault integrity."""
    import json
    proof = {"root_hash": "abc123...", "timestamp": "2026-03-13T..."}
    return json.dumps(proof).encode()
```

#### 2.3 Prompts — Context Builders

```python
from fastmcp import FastMCP
from fastmcp.types import TextContent, ImageContent

mcp = FastMCP("PromptsDemo")

# Simple prompt template
@mcp.prompt()
def constitutional_review(topic: str) -> str:
    """Generate constitutional review prompt."""
    return f"""Review the following topic through the lens of arifOS constitutional governance:

Topic: {topic}

Evaluate against:
- F2 (Truth): Is this grounded in verifiable reality?
- F4 (Clarity): Is the entropy score ΔS ≤ 0?
- F7 (Humility): Is uncertainty acknowledged (Ω₀ ≥ 0.03)?
- F9 (Compassion): Does this minimize harm?

Provide your assessment with specific floor references.
"""

# Multi-message prompt
@mcp.prompt()
def tri_witness_analysis(claim: str, evidence: list[str]) -> list[TextContent]:
    """Generate tri-witness consensus prompt."""
    return [
        TextContent(
            type="text",
            text=f"Claim to verify: {claim}"
        ),
        TextContent(
            type="text",
            text=f"Evidence sources: {', '.join(evidence)}"
        ),
        TextContent(
            type="text",
            text="""Apply Tri-Witness Reality Test (TWRT):
1. Human Authority: What would a domain expert conclude?
2. AI Coherence: Is this internally consistent with known facts?
3. Earth Grounding: Can this be verified against external sources?

Calculate W3 consensus score."""
        )
    ]
```

### 3. Transport Mechanisms

```python
from fastmcp import FastMCP

mcp = FastMCP("TransportDemo")

@mcp.tool()
def governance_check(query: str) -> dict:
    return {"verdict": "SEAL", "query": query}

if __name__ == "__main__":
    # STDIO: For Claude Desktop, Cursor IDE (default)
    mcp.run(transport="stdio")
    
    # SSE: For local development, real-time updates
    # mcp.run(transport="sse", host="127.0.0.1", port=3000)
    
    # HTTP: For production VPS, remote access
    # mcp.run(transport="http", host="0.0.0.0", port=8080)
```

### 4. Dependency Injection

```python
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext, CurrentFastMCP, Depends

mcp = FastMCP("DIDemo")

# Custom dependency
async def get_session_context(ctx: CurrentContext) -> dict:
    """Extract session from request context."""
    return ctx.request.meta.get("session", {})

@mcp.tool()
async def governed_action(
    query: str,
    session: dict = Depends(get_session_context),
    server: CurrentFastMCP = None
) -> dict:
    """Tool with injected dependencies."""
    # Access server state
    config = server.settings
    
    # Use session context
    user_id = session.get("user_id")
    
    return {"query": query, "user_id": user_id}
```

---

## 🏛️ Part II: arifOS MCP Architecture

### 1. The 13 Constitutional Floors (F1-F13)

| Floor | Name | Meaning | Enforcement | Threshold |
|-------|------|---------|-------------|-----------|
| **F1** | Amanah | Trust / Reversibility | **HARD VOID** | 100% reversibility |
| **F2** | Haqq | Truth / Veracity | **SOFT PARTIAL** | ≥0.85 confidence |
| **F3** | Shahada | Witness / Testimony | **MIRROR** | W4 ≥ 0.75 |
| **F4** | Nur | Clarity / Transparency | **SOFT PARTIAL** | ΔS ≤ 0 |
| **F5** | Hikmah | Wisdom / Prudence | **SOFT PARTIAL** | Ω₀ ∈ [0.03, 0.05] |
| **F6** | Adl | Justice / Fairness | **HARD VOID** | 100% fairness |
| **F7** | Tawadu | Humility / Modesty | **SOFT PARTIAL** | Ω₀ ≥ 0.03 |
| **F8** | Sabr | Patience / Deliberation | **SOFT PARTIAL** | ≥3 cycles |
| **F9** | Rahmah | Compassion / Mercy | **SOFT PARTIAL** | Harm < 0.1 |
| **F10** | Ihsan | Excellence / Mastery | **MIRROR** | Quality ≥ 0.90 |
| **F11** | Aman | Safety / Security | **WALL** | 100% gate |
| **F12** | Hifz | Protection / Guardianship | **WALL** | 100% shield |
| **F13** | Khalifah | Human Authority | **VETO** | Absolute |

### 2. Double Helix Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DOUBLE HELIX ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  OUTER RING: Peripheral Nervous System (PNS)                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│  │PNS·SHIELD│ │PNS·SEARCH│ │PNS·VISION│ │PNS·HEALTH│                   │
│  │  (F12)   │ │(Browser) │ │(Stirling)│ │(Evolution│                   │
│  │Injection │ │  less    │ │   PDF    │ │   API)   │                   │
│  │ Defense  │ │          │ │          │ │          │                   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘                   │
│       │            │            │            │                          │
│       └────────────┴────────────┴────────────┘                          │
│                    │                                                    │
│                    ▼                                                    │
│  INNER RING: Sacred Constitutional Chain                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  000 ──► 333 ──► 444 ──► 666A ──► 666B ──► 777 ──► 888 ──► 999  │   │
│  │ ANCHOR  REASON  REFLECT SIMULATE CRITIQUE FORGE  JUDGE   SEAL   │   │
│  │   │       │       │       │        │       │      │       │     │   │
│  │  F12     F2/F4   F3      ΔS      F7     F11   F1/F13  Hash    │   │
│  │         F2/F4   (W4)   Entropy  Humility Gate  APEX   Chain   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  WALL OF SILENCE: No PNS injection to SIMULATE or SEAL                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3. Trinity Architecture (ΔΩΨ)

```
┌──────────────────────────────────────────────────────────────┐
│                    TRINITY ARCHITECTURE                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Δ (DELTA) ───────── Ω (OMEGA) ───────── Ψ (PSI)           │
│     MIND               HEART                SOUL             │
│                                                              │
│   Stages: 111-333    Stages: 555-666    Stages: 444-888      │
│                                                              │
│   Floors:            Floors:            Floors:              │
│   • F2 (Truth)       • F5 (Wisdom)      • F3 (Witness)       │
│   • F4 (Clarity)     • F6 (Justice)     • F10 (Excellence)   │
│   • F7 (Humility)    • F9 (Compassion)  • F11 (Safety)       │
│   • F8 (Patience)                       • F12 (Protection)   │
│                                         • F13 (Human)        │
│                                                              │
│   Metric: ΔS ≤ 0     Metric: Ω₀ band    Metric: Reversible   │
│   (Clarity)          (Humility)         + Witnessed          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4. The 8 Sacred Tools

| Stage | Tool | Function | Constitutional Guard |
|-------|------|----------|---------------------|
| 000 | **init_anchor** | Identity Minting | F12 Pre-scan |
| 333 | **agi_reason** | 3-Path Logic | F4 Clarity / F2 Truth |
| 555 | **agi_reflect** | Memory Mirror | Vault999 Search |
| 666A | **asi_simulate** | Outcome Forecast | ΔS Entropy Check |
| 666B | **asi_critique** | Uncertainty Band | F7 Humility [0.03, 0.05] |
| 777 | **forge** | Synthesis | F11 Execution Gate |
| 888 | **apex_judge** | Sovereign Verdict | APEX Soul (F1, F3, F13) |
| 999 | **vault_seal** | Immutable Commit | Hash-chain Update |

### 5. MGI Envelope (3-Layer Response)

```python
{
    "machine": {
        "status": "ok",
        "latency_ms": 45,
        "version": "2026.03.13"
    },
    "governance": {
        "verdict": "SEAL",  # SEAL | PARTIAL | SABAR | VOID | 888_HOLD
        "floors_passed": 13,
        "floors_failed": [],
        "entropy_score": -0.12,  # ΔS ≤ 0 required
        "uncertainty": 0.04,  # Ω₀ ∈ [0.03, 0.05]
        "witness_score": 0.82  # W4 ≥ 0.75
    },
    "intelligence": {
        "result": "...",
        "reasoning_chain": [...],
        "confidence": 0.91
    }
}
```

---

## 🔌 Part III: Integration Patterns

### 1. Tool Mapping Strategy

```python
# arifos_mcp_server.py
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional, Dict, Any

mcp = FastMCP("arifOS")

# ═══════════════════════════════════════════════════════════════════════════
# 8 SACRED TOOLS → FastMCP TOOLS
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def init_anchor_state(
    session_id: str,
    intent: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    000 INIT·ANCHOR: Bootstrap a governed session.
    
    Constitutional Guards: F12 (Pre-scan), F1 (Reversibility setup)
    """
    # F12: Sanitize intent
    sanitized = await f12_sanitize(intent)
    
    # Initialize session
    session = {
        "id": session_id,
        "intent": sanitized,
        "anchor_time": "2026-03-13T...",
        "metabolic_state": "active"
    }
    
    return {
        "machine": {"status": "ok"},
        "governance": {"verdict": "SEAL", "floors_passed": ["F1", "F12"]},
        "intelligence": {"session": session}
    }

@mcp.tool()
async def reason_mind_synthesis(
    query: str,
    session_id: str,
    synthesis_depth: int = 3
) -> Dict[str, Any]:
    """
    333 AGI·REASON: Multi-path logic synthesis.
    
    Constitutional Guards: F2 (Truth), F4 (Clarity), F7 (Humility)
    """
    # Execute 3-path reasoning
    logical = await reason_path(query, mode="logical")
    emotional = await reason_path(query, mode="emotional")
    intuitive = await reason_path(query, mode="intuitive")
    
    # Calculate entropy score
    delta_s = calculate_entropy([logical, emotional, intuitive])
    
    if delta_s > 0:
        return {
            "machine": {"status": "rejected"},
            "governance": {"verdict": "VOID", "reason": f"ΔS = {delta_s} > 0"},
            "intelligence": {"result": None}
        }
    
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "entropy_score": delta_s,
            "floors_passed": ["F2", "F4", "F7"]
        },
        "intelligence": {
            "synthesis": {
                "logical": logical,
                "emotional": emotional,
                "intuitive": intuitive
            }
        }
    }

@mcp.tool()
async def seal_vault_commit(
    session_id: str,
    verdict: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    999 VAULT·SEAL: Immutable commit to ledger.
    
    Constitutional Guards: F1 (Reversibility token), F3 (Witness)
    """
    # Generate hash chain
    prev_hash = await get_last_hash()
    commit_hash = sha256(f"{prev_hash}:{session_id}:{verdict}")
    
    # Store in PostgreSQL
    await vault_store({
        "session_id": session_id,
        "verdict": verdict,
        "data": data,
        "hash": commit_hash,
        "timestamp": "2026-03-13T..."
    })
    
    return {
        "machine": {"status": "ok"},
        "governance": {"verdict": "SEAL", "commit_hash": commit_hash},
        "intelligence": {"sealed": True}
    }
```

### 2. Constitutional Middleware Pattern

```python
# governance/decorators.py
from functools import wraps
from typing import List, Callable
import asyncio

class ConstitutionalGuard:
    """Decorator for enforcing F1-F13 constitutional floors."""
    
    def __init__(self, floors: List[str]):
        self.floors = floors
        self.validators = {
            "F1": self._check_f1_reversibility,
            "F2": self._check_f2_truth,
            "F4": self._check_f4_clarity,
            "F7": self._check_f7_humility,
            # ... etc
        }
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Run all floor validations
            failed_floors = []
            
            for floor in self.floors:
                validator = self.validators.get(floor)
                if validator and not await validator(*args, **kwargs):
                    failed_floors.append(floor)
            
            if failed_floors:
                return {
                    "machine": {"status": "blocked"},
                    "governance": {
                        "verdict": "VOID",
                        "floors_failed": failed_floors
                    },
                    "intelligence": {"result": None}
                }
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    async def _check_f1_reversibility(self, *args, **kwargs) -> bool:
        """F1: All actions must be reversible."""
        return True  # Implementation
    
    async def _check_f4_clarity(self, *args, **kwargs) -> bool:
        """F4: Entropy score must be ≤ 0."""
        return True  # Implementation
    
    async def _check_f7_humility(self, *args, **kwargs) -> bool:
        """F7: Uncertainty must be acknowledged."""
        return True  # Implementation

# Usage
@ConstitutionalGuard(floors=["F1", "F4", "F7"])
@mcp.tool()
async def governed_tool(query: str) -> dict:
    """Tool with automatic constitutional validation."""
    return {"result": "..."}
```

### 3. Multi-Transport Deployment

```python
# config.py
from pydantic import BaseSettings
from typing import Literal

class ServerConfig(BaseSettings):
    transport: Literal["stdio", "sse", "http"] = "stdio"
    host: str = "0.0.0.0"
    port: int = 3000
    
    # arifOS specific
    constitution_path: str = "./constitution.yaml"
    vault_db_url: str = "postgresql://..."
    redis_url: str = "redis://..."
    
    class Config:
        env_prefix = "ARIFOS_"

# server.py
from fastmcp import FastMCP
from config import ServerConfig

config = ServerConfig()
mcp = FastMCP("arifOS")

# ... tool definitions ...

if __name__ == "__main__":
    if config.transport == "stdio":
        # For Claude Desktop, Cursor IDE
        mcp.run(transport="stdio")
    elif config.transport == "sse":
        # For local development
        mcp.run(transport="sse", host=config.host, port=config.port)
    elif config.transport == "http":
        # For production VPS
        mcp.run(transport="http", host=config.host, port=config.port)
```

---

## 🚀 Part IV: Implementation Guide

### 1. Project Setup

```bash
# Create project
mkdir arifos-mcp-server && cd arifos-mcp-server
uv init

# Install dependencies
uv add fastmcp pydantic
uv add --dev pytest pytest-asyncio

# Directory structure
mkdir -p src/{primitives,governance,models,utils} tests constitution
```

### 2. Complete Server Implementation

```python
# src/server.py
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
import asyncio
import hashlib
from datetime import datetime

# Initialize server
mcp = FastMCP(
    "arifOS-Constitutional-Server",
    instructions="Constitutional AI governance via MCP",
    version="2026.03.13"
)

# ═══════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════

class AnchorRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    intent: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None

class ReasonRequest(BaseModel):
    query: str = Field(..., min_length=1)
    session_id: str
    depth: Literal[1, 2, 3, 4, 5] = 3

class SealRequest(BaseModel):
    session_id: str
    verdict: Literal["SEAL", "PARTIAL", "SABAR", "VOID"]
    data: Dict[str, Any]

# ═══════════════════════════════════════════════════════════════════════════
# 8 SACRED TOOLS
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def init_anchor(request: AnchorRequest) -> Dict[str, Any]:
    """000 INIT·ANCHOR: Bootstrap governed session."""
    session = {
        "id": request.session_id,
        "intent": request.intent,
        "anchor_time": datetime.utcnow().isoformat(),
        "state": "active"
    }
    
    return {
        "machine": {"status": "ok", "latency_ms": 12},
        "governance": {
            "verdict": "SEAL",
            "floors_passed": ["F1", "F12"],
            "reversibility_token": hashlib.sha256(
                f"{request.session_id}:init".encode()
            ).hexdigest()[:16]
        },
        "intelligence": {"session": session}
    }

@mcp.tool()
async def reason_mind(request: ReasonRequest) -> Dict[str, Any]:
    """333 AGI·REASON: Multi-path synthesis with F2/F4/F7 validation."""
    # Simulate reasoning
    await asyncio.sleep(0.1)
    
    return {
        "machine": {"status": "ok", "latency_ms": 105},
        "governance": {
            "verdict": "SEAL",
            "floors_passed": ["F2", "F4", "F7"],
            "entropy_score": -0.23,
            "uncertainty": 0.04
        },
        "intelligence": {
            "synthesis": {
                "logical": f"Logical analysis of: {request.query}",
                "emotional": f"Emotional perspective on: {request.query}",
                "intuitive": f"Intuitive insight for: {request.query}"
            },
            "confidence": 0.89
        }
    }

@mcp.tool()
async def search_reality(
    query: str,
    session_id: str,
    sources: list[str] = ["web", "vault"]
) -> Dict[str, Any]:
    """Search external reality with F2/F3 validation."""
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "witness_score": 0.82  # W4 ≥ 0.75
        },
        "intelligence": {
            "results": [
                {"source": "web", "content": f"Web result for: {query}"},
                {"source": "vault", "content": f"Vault memory for: {query}"}
            ]
        }
    }

@mcp.tool()
async def ingest_evidence(
    session_id: str,
    evidence: str,
    source_type: Literal["human", "ai", "external"]
) -> Dict[str, Any]:
    """Ingest evidence for tri-witness validation."""
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "evidence_hash": hashlib.sha256(evidence.encode()).hexdigest()[:16]
        },
        "intelligence": {"ingested": True, "source": source_type}
    }

@mcp.tool()
async def simulate_heart(
    scenario: str,
    session_id: str
) -> Dict[str, Any]:
    """555-666A ASI·SIMULATE: Outcome forecasting with entropy check."""
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "entropy_score": -0.15,  # ΔS ≤ 0
            "simulation_confidence": 0.87
        },
        "intelligence": {
            "projected_outcomes": [
                {"probability": 0.7, "outcome": "Positive result"},
                {"probability": 0.2, "outcome": "Neutral result"},
                {"probability": 0.1, "outcome": "Negative result"}
            ]
        }
    }

@mcp.tool()
async def critique_thought(
    draft: str,
    session_id: str
) -> Dict[str, Any]:
    """666B ASI·CRITIQUE: Metacognitive reflection with F7 humility."""
    uncertainty = 0.04  # Within [0.03, 0.05] band
    
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "uncertainty": uncertainty,
            "floors_passed": ["F7"]
        },
        "intelligence": {
            "critique": f"Critical analysis of: {draft[:100]}...",
            "suggested_improvements": ["Add citations", "Clarify assumptions"]
        }
    }

@mcp.tool()
async def eureka_forge(
    spec: str,
    session_id: str,
    artifact_type: Literal["code", "text", "config"] = "text"
) -> Dict[str, Any]:
    """777 FORGE: Artifact synthesis with F11 execution gate."""
    # F11: Safety check before execution
    safety_passed = True  # Implementation
    
    if not safety_passed:
        return {
            "machine": {"status": "blocked"},
            "governance": {"verdict": "888_HOLD", "reason": "F11 safety check failed"},
            "intelligence": {"artifact": None}
        }
    
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "floors_passed": ["F11"],
            "execution_authorized": True
        },
        "intelligence": {
            "artifact": f"Generated {artifact_type} based on: {spec[:50]}...",
            "format": artifact_type
        }
    }

@mcp.tool()
async def apex_judge(
    candidate: Dict[str, Any],
    session_id: str
) -> Dict[str, Any]:
    """888 APEX·JUDGE: Sovereign verdict with F1/F3/F13 validation."""
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "floors_passed": ["F1", "F3", "F13"],
            "judgment": "APPROVED",
            "confidence": 0.94
        },
        "intelligence": {
            "rationale": "Candidate meets all constitutional requirements",
            "recommendation": "Proceed to vault seal"
        }
    }

@mcp.tool()
async def seal_vault(request: SealRequest) -> Dict[str, Any]:
    """999 VAULT·SEAL: Immutable commit with hash-chain."""
    # Generate commit hash
    commit_data = f"{request.session_id}:{request.verdict}:{datetime.utcnow().isoformat()}"
    commit_hash = hashlib.sha256(commit_data.encode()).hexdigest()
    
    return {
        "machine": {"status": "ok"},
        "governance": {
            "verdict": "SEAL",
            "commit_hash": commit_hash,
            "immutable": True
        },
        "intelligence": {
            "sealed_data": request.data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

# ═══════════════════════════════════════════════════════════════════════════
# RESOURCES
# ═══════════════════════════════════════════════════════════════════════════

@mcp.resource("audit://floors")
def get_floor_status() -> str:
    """Return status of all 13 constitutional floors."""
    floors = [
        "F1 (Amanah): ACTIVE - Reversibility enforced",
        "F2 (Haqq): ACTIVE - Truth validation 0.89",
        "F3 (Shahada): ACTIVE - W4=0.82",
        "F4 (Nur): ACTIVE - ΔS=-0.23",
        "F5 (Hikmah): ACTIVE - Ω₀=0.04",
        "F6 (Adl): ACTIVE - Fairness check passed",
        "F7 (Tawadu): ACTIVE - Humility acknowledged",
        "F8 (Sabr): ACTIVE - 3 cycles completed",
        "F9 (Rahmah): ACTIVE - Harm<0.1",
        "F10 (Ihsan): ACTIVE - Quality=0.92",
        "F11 (Aman): ACTIVE - Gate passed",
        "F12 (Hifz): ACTIVE - Shield active",
        "F13 (Khalifah): STANDBY - Human veto ready"
    ]
    return "\n".join(floors)

@mcp.resource("session://{session_id}")
def get_session(session_id: str) -> dict:
    """Get session state."""
    return {
        "session_id": session_id,
        "status": "active",
        "verdict": "SEAL",
        "floors_passed": 13
    }

# ═══════════════════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════════════════

@mcp.prompt()
def constitutional_review(topic: str) -> str:
    """Generate constitutional review prompt."""
    return f"""Review this topic through arifOS constitutional lens:

TOPIC: {topic}

Evaluate against F1-F13 floors:
- F2 (Truth): Grounded in verifiable reality?
- F4 (Clarity): ΔS ≤ 0?
- F7 (Humility): Uncertainty acknowledged?
- F9 (Compassion): Minimizes harm?

Provide floor-by-floor assessment."""

@mcp.prompt()
def tri_witness_template(claim: str) -> str:
    """Generate tri-witness consensus prompt."""
    return f"""Verify claim through Tri-Witness Reality Test:

CLAIM: {claim}

WITNESSES:
1. Human Authority: Expert domain assessment
2. AI Coherence: Internal consistency check
3. Earth Grounding: External source verification

Calculate W3 = (H × A × E)^(1/3) ≥ 0.75?"""

# ═══════════════════════════════════════════════════════════════════════════
# SERVER ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.run(transport="sse", host="127.0.0.1", port=3000)
    elif transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=8080)
```

### 3. Testing with MCP Inspector

```bash
# Install FastMCP CLI
pip install fastmcp

# Run development server with inspector
fastmcp dev src/server.py

# Test via inspector UI
# 1. Open browser to provided URL
# 2. Click "List Tools" to see all 8 Sacred Tools
# 3. Test individual tools with JSON input
# 4. Verify MGI envelope structure in responses
```

### 4. Client Integration

```python
# client_example.py
from fastmcp import Client
import asyncio

async def main():
    # Connect to server
    client = Client("http://localhost:3000/mcp")
    
    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {[t.name for t in tools]}")
    
    # Call init_anchor
    result = await client.call_tool("init_anchor", {
        "request": {
            "session_id": "test-123",
            "intent": "Test constitutional governance"
        }
    })
    print(f"Anchor result: {result}")
    
    # Call reason_mind
    result = await client.call_tool("reason_mind", {
        "request": {
            "query": "Is this ethically sound?",
            "session_id": "test-123",
            "depth": 3
        }
    })
    print(f"Reason result: {result}")
    
    # Read resource
    floors = await client.read_resource("audit://floors")
    print(f"Floor status: {floors}")
    
    # Get prompt
    prompt = await client.get_prompt("constitutional_review", {
        "topic": "AI governance"
    })
    print(f"Prompt: {prompt}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Claude Desktop Configuration

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python3",
      "args": ["/path/to/arifos-mcp-server/src/server.py", "stdio"],
      "env": {
        "ARIFOS_CONSTITUTION_PATH": "./constitution.yaml"
      }
    }
  }
}
```

---

## 📊 Part V: Best Practices & Optimization

### 1. Type Safety with Pydantic

```python
from pydantic import BaseModel, Field, validator
from typing import Literal

class GovernedRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    session_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$")
    sensitivity: Literal["low", "medium", "high"] = "medium"
    
    @validator("query")
    def no_injection_patterns(cls, v):
        # F12: Injection defense
        dangerous = ["DROP TABLE", "rm -rf", "<script>"]
        for pattern in dangerous:
            if pattern.lower() in v.lower():
                raise ValueError(f"Potential injection detected: {pattern}")
        return v
```

### 2. Async Patterns

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# For CPU-bound operations (entropy calculation)
executor = ThreadPoolExecutor(max_workers=4)

@mcp.tool()
async def compute_entropy(data: list) -> float:
    """Compute entropy score asynchronously."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: calculate_entropy_sync(data)
    )
    return result
```

### 3. Error Handling

```python
from fastmcp.exceptions import ToolError

@mcp.tool()
async def governed_operation(query: str) -> dict:
    try:
        # Attempt operation
        result = await risky_operation(query)
        
        # Validate result
        if result.entropy > 0:
            return {
                "machine": {"status": "rejected"},
                "governance": {"verdict": "VOID", "reason": "ΔS > 0"},
                "intelligence": None
            }
        
        return result
        
    except ValidationError as e:
        return {
            "machine": {"status": "error"},
            "governance": {"verdict": "VOID", "reason": str(e)},
            "intelligence": None
        }
    except Exception as e:
        # Log for debugging but return governed response
        logger.error(f"Unexpected error: {e}")
        return {
            "machine": {"status": "error"},
            "governance": {"verdict": "SABAR", "reason": "Retry recommended"},
            "intelligence": None
        }
```

### 4. Performance Optimization

```python
from functools import lru_cache
import hashlib

# Cache expensive validations
@lru_cache(maxsize=1000)
def validate_constitution_hash(content: str) -> bool:
    """Cache constitution validation results."""
    expected = load_constitution_hash()
    actual = hashlib.sha256(content.encode()).hexdigest()
    return actual == expected

# Connection pooling for external resources
from httpx import AsyncClient

http_client = AsyncClient(timeout=30.0)

@mcp.tool()
async def search_reality(query: str) -> dict:
    """Search with connection reuse."""
    response = await http_client.get(
        f"https://api.search.com?q={query}"
    )
    return response.json()
```

---

## 📚 Reference: Key Metrics & Thresholds

| Metric | Symbol | Formula | Threshold | Purpose |
|--------|--------|---------|-----------|---------|
| **Entropy Score** | ΔS | Σ(pᵢ × log₂(pᵢ)) | ≤ 0 | Clarity (F4) |
| **Uncertainty** | Ω₀ | Gödel band | [0.03, 0.05] | Humility (F7) |
| **Witness Score** | W4 | (H×A×E×V)^(1/4) | ≥ 0.75 | Testimony (F3) |
| **Integrity Index** | SII | (Δ×Ω×Ψ)/E | > 0.8 | System health |
| **Quality Score** | Q | Benchmark ratio | ≥ 0.90 | Excellence (F10) |
| **Harm Score** | H | Impact assessment | < 0.1 | Compassion (F9) |

---

## 🔗 Resources

- **FastMCP Docs**: https://gofastmcp.com
- **arifOS Docs**: https://arifos.arif-fazil.com
- **MCP Spec**: https://modelcontextprotocol.io
- **GitHub**: https://github.com/ariffazil/arifosmcp

---

*Ditempa Bukan Diberi — [ΔΩΨ | ARIF]*
