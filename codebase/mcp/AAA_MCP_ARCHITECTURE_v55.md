# AAA MCP Architecture v55.0

## Constitutional AI Governance — Model-Agnostic, Platform-Universal MCP Server

**Version:** 55.0 | **Date:** 2026-01-31 | **Authority:** 888_Judge
**Status:** SABAR → Conditional SEAL pending implementation

---

## 1. Current State Audit: What's Unhardened

### Files Requiring Hardening

| Current File | Issue | Severity | Action |
|-------------|-------|----------|--------|
| `server.py` | Stdio transport tightly coupled with tool registration; tools defined inline | HIGH | Split → `core/server_base.py` + `transports/stdio.py` |
| `sse.py` | Duplicates all 7 tool registrations from server.py; FastMCP-specific | HIGH | Extract → `transports/sse.py` (transport only) |
| `sse_simple.py` | Hardcoded mock responses, no kernel calls, duplicate tool names | CRITICAL | **REMOVE** — redundant with proper fallback in bridge |
| `bridge.py` | 24KB monolith: CircuitBreaker + BridgeRouter + serialization + action mapping all in one file | HIGH | Split → `governance/bridge.py` + `infrastructure/circuit_breaker.py` |
| `session_ledger.py` | File-only backend, no pluggable storage interface | MEDIUM | Refactor → `sessions/manager.py` + `sessions/backends/file.py` |
| `immutable_ledger.py` | Overlaps session_ledger; Merkle logic mixed with storage | MEDIUM | Merge audit logic → `sessions/ledger.py`, Merkle → `integration/vault.py` |
| `constitutional_metrics.py` | In-memory only, overlaps metrics.py | MEDIUM | Merge → `metrics/constitutional.py` |
| `metrics.py` | Prometheus-style but not exported; overlaps constitutional_metrics | MEDIUM | Merge → `metrics/collector.py` |
| `redis_client.py` | Hardcoded Redis with memory fallback; not pluggable | MEDIUM | Refactor → `sessions/backends/redis.py` |
| `mode_selector.py` | BRIDGE/STANDALONE/AUTO but STANDALONE never implemented | LOW | Move → `config/modes.py`, implement all modes |
| `models.py` | Good Pydantic models but not shared across tools | LOW | Move → `core/models.py` |
| `maintenance.py` | Session cleanup loop; mixed concerns | LOW | Move → `infrastructure/health.py` |
| `trinity_server.py` | Legacy 5-tool server (v51), superseded by 7-core | LOW | Archive or **REMOVE** |
| `tools/mcp_tools_v53.py` | 28KB: authorize/reason/evaluate/decide/seal all in one file | HIGH | Already wrapped by canonical_trinity.py; keep as internal engine |
| `tools/integration_claude_api.py` | Claude-specific; violates model agnosticism | HIGH | Move → `adapters/anthropic.py` |

### Tool Registration Duplication (The Core Problem)

Currently, the 7 tools are registered **three separate times**:

```
1. server.py      → @server.call_tool("_init_") ... (stdio)
2. sse.py         → @mcp.tool("_init_") ...         (SSE/HTTP)
3. sse_simple.py  → @mcp.tool("init_000") ...       (fallback, different names!)
```

**Fix:** Single `core/tool_registry.py` → all transports consume it.

---

## 2. AAA MCP Target Architecture

```
codebase/mcp/
│
├── __init__.py                    # Package version, public API exports
├── __main__.py                    # Entry point: dispatches to transport
│
├── core/                          # ═══ PROTOCOL LAYER (Model-Agnostic) ═══
│   ├── __init__.py
│   ├── server.py                  # AAAServer: transport-agnostic server core
│   ├── tool_registry.py           # Single source of truth for all 7 tools
│   ├── models.py                  # Pydantic request/response models (from models.py)
│   ├── schemas.py                 # JSON Schema definitions for tool inputs/outputs
│   └── version.py                 # Version constants, capability negotiation
│
├── transports/                    # ═══ TRANSPORT LAYER (Pluggable) ═══
│   ├── __init__.py
│   ├── base.py                    # BaseTransport ABC
│   ├── stdio.py                   # StdioTransport (from server.py)
│   ├── sse.py                     # SSETransport via FastMCP (from sse.py)
│   ├── http.py                    # Streamable HTTP (FastMCP v2 recommended)
│   └── auto.py                    # Auto-detect best transport at startup
│
├── adapters/                      # ═══ MODEL ADAPTERS (AI-Agnostic) ═══
│   ├── __init__.py
│   ├── base.py                    # BaseModelAdapter ABC
│   ├── anthropic.py               # Claude-specific normalization (from integration_claude_api.py)
│   ├── openai.py                  # GPT/ChatGPT normalization
│   ├── google.py                  # Gemini normalization
│   ├── kimi.py                    # Kimi/Moonshot normalization
│   ├── meta.py                    # Llama/SEA-LION normalization
│   └── universal.py               # Fallback: accepts any JSON-RPC input
│
├── clients/                       # ═══ CLIENT ADAPTERS (Platform-Universal) ═══
│   ├── __init__.py
│   ├── base.py                    # BaseClientAdapter ABC
│   ├── claude_desktop.py          # Claude Desktop config generation
│   ├── cursor.py                  # Cursor IDE config generation
│   ├── vscode.py                  # VS Code / Continue config generation
│   ├── windsurf.py                # Windsurf/Codeium config generation
│   └── generic.py                 # Generic MCP client fallback
│
├── tools/                         # ═══ 7 CANONICAL TOOLS (Constitutional) ═══
│   ├── __init__.py
│   ├── canonical_trinity.py       # Async tool implementations (KEPT - core logic)
│   ├── _init_.py                  # 000_GATE: Session ignition + injection scan
│   ├── _agi_.py                   # 111-333_MIND: Truth engine
│   ├── _asi_.py                   # 444-666_HEART: Safety/empathy engine
│   ├── _apex_.py                  # 777-888_SOUL: Judgment + 9-paradox
│   ├── _vault_.py                 # 999_SEAL: Immutable ledger
│   ├── _trinity_.py               # Full 000→999 pipeline
│   ├── _reality_.py               # External fact-checker gateway
│   ├── mcp_tools_v53.py           # Internal engine (authorize/reason/evaluate/decide/seal)
│   ├── context_scope.py           # Context7 scope validation
│   └── trinity_validator.py       # Request validation
│
├── constitution/                  # ═══ FLOOR ENFORCEMENT ═══
│   ├── __init__.py
│   ├── floors.py                  # F1-F13 floor definitions + thresholds
│   ├── validators.py              # Floor validation logic (from enforcement/)
│   ├── guards.py                  # F10 Ontology, F11 Auth, F12 Injection guards
│   ├── enforcer.py                # Pre/post tool-call enforcement pipeline
│   └── verdicts.py                # SEAL/PARTIAL/VOID/888_HOLD/SABAR logic
│
├── sessions/                      # ═══ SESSION MANAGEMENT (Pluggable Backends) ═══
│   ├── __init__.py
│   ├── manager.py                 # SessionManager: open/close/recover
│   ├── ledger.py                  # Immutable audit ledger (merged from session_ledger + immutable_ledger)
│   └── backends/                  # Storage backends
│       ├── __init__.py
│       ├── base.py                # SessionBackend ABC
│       ├── memory.py              # In-memory (dev/testing)
│       ├── file.py                # JSON file-based (current default)
│       ├── redis.py               # Redis (from redis_client.py)
│       └── sqlite.py              # SQLite (embedded production)
│
├── governance/                    # ═══ APEX PRIME + BRIDGE ═══
│   ├── __init__.py
│   ├── bridge.py                  # BridgeRouter: routes tools → kernels (from bridge.py)
│   ├── apex_prime.py              # Final judgment engine
│   ├── dials.py                   # APEX 4-dial scoring
│   └── prompts/                   # Constitutional prompt templates
│       ├── constitutional.txt
│       ├── trinity.txt
│       └── coaching.txt
│
├── metrics/                       # ═══ OBSERVABILITY ═══
│   ├── __init__.py
│   ├── collector.py               # Unified metrics (merged metrics.py + constitutional_metrics.py)
│   ├── constitutional.py          # Floor/verdict/bundle tracking
│   ├── exporter.py                # Prometheus / JSON export
│   └── performance.py             # Latency, throughput, error rates
│
├── presenters/                    # ═══ OUTPUT FORMATTING ═══
│   ├── __init__.py
│   ├── base.py                    # BasePresenter ABC
│   ├── human.py                   # Human-readable (terminal/chat)
│   ├── json_presenter.py          # Structured JSON
│   └── markdown.py                # Markdown (for LLM consumption)
│
├── infrastructure/                # ═══ CROSS-CUTTING CONCERNS ═══
│   ├── __init__.py
│   ├── rate_limiter.py            # Token bucket rate limiting (from rate_limiter.py)
│   ├── circuit_breaker.py         # Circuit breaker (extracted from bridge.py)
│   ├── caching.py                 # Response cache layer
│   └── health.py                  # Health checks + maintenance (from maintenance.py)
│
├── external_gateways/             # ═══ EXTERNAL INTEGRATIONS ═══
│   ├── __init__.py
│   ├── base.py                    # BaseGateway ABC
│   ├── brave_client.py            # Brave Search (existing)
│   ├── context7_client.py         # Context7 (existing)
│   └── reality.py                 # Reality grounding orchestrator
│
├── integration/                   # ═══ arifOS KERNEL HOOKS ═══
│   ├── __init__.py
│   ├── kernel.py                  # get_kernel_manager() bridge
│   ├── loop.py                    # 000↔999 metabolic loop integration
│   ├── vault.py                   # VAULT-999 Merkle sealing
│   └── engines.py                 # AGI/ASI/APEX engine wrappers
│
├── config/                        # ═══ CONFIGURATION ═══
│   ├── __init__.py
│   ├── loader.py                  # Config loading from env/file/defaults
│   ├── modes.py                   # STUDIO/PROD/DEBUG modes (from mode_selector.py)
│   ├── mcp_config.json            # Tool schemas (existing)
│   └── defaults.py                # Default values
│
└── _archive/                      # ═══ ARCHIVED (Pre-v55) ═══
    ├── trinity_server.py          # Legacy 5-tool server
    ├── sse_simple.py              # Removed minimal fallback
    └── trinity_hat.py             # Legacy decorator patterns
```

---

## 3. Core Interfaces (Abstract Base Classes)

### 3.1 BaseTransport

```python
# codebase/mcp/transports/base.py
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any

class BaseTransport(ABC):
    """Abstract transport layer — all transports implement this."""

    @abstractmethod
    async def start(self, tool_registry: "ToolRegistry") -> None:
        """Start the transport, registering all tools from the registry."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shut down the transport."""
        ...

    @abstractmethod
    async def send_response(self, request_id: str, response: Dict[str, Any]) -> None:
        """Send a response back to the client."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Transport identifier (e.g., 'stdio', 'sse', 'http')."""
        ...
```

### 3.2 BaseModelAdapter

```python
# codebase/mcp/adapters/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..core.models import MCPRequest, MCPResponse

class BaseModelAdapter(ABC):
    """Normalizes model-specific request/response formats to MCP standard."""

    @abstractmethod
    def normalize_request(self, raw: Dict[str, Any]) -> MCPRequest:
        """Convert model-specific input to canonical MCPRequest."""
        ...

    @abstractmethod
    def normalize_response(self, response: MCPResponse) -> Dict[str, Any]:
        """Convert canonical MCPResponse to model-specific output."""
        ...

    @abstractmethod
    def detect(self, headers: Optional[Dict] = None, metadata: Optional[Dict] = None) -> bool:
        """Auto-detect if this adapter should handle the request."""
        ...

    @property
    @abstractmethod
    def model_family(self) -> str:
        """Model family identifier (e.g., 'anthropic', 'openai', 'google')."""
        ...
```

### 3.3 BaseClientAdapter

```python
# codebase/mcp/clients/base.py
from abc import ABC, abstractmethod
from typing import Dict, Set

class BaseClientAdapter(ABC):
    """Generates client-specific configuration for MCP integration."""

    @abstractmethod
    def detect(self) -> bool:
        """Auto-detect if running inside this client environment."""
        ...

    @abstractmethod
    def get_config(self) -> Dict:
        """Return client-specific MCP configuration."""
        ...

    @abstractmethod
    def get_capabilities(self) -> Set[str]:
        """Return set of capabilities this client supports."""
        ...

    @property
    @abstractmethod
    def client_name(self) -> str:
        """Client identifier (e.g., 'claude_desktop', 'cursor')."""
        ...
```

### 3.4 SessionBackend

```python
# codebase/mcp/sessions/backends/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class SessionBackend(ABC):
    """Pluggable session storage backend."""

    @abstractmethod
    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    async def set(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        ...

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        ...

    @abstractmethod
    async def list_active(self) -> list[str]:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
```

### 3.5 ToolRegistry (Single Source of Truth)

```python
# codebase/mcp/core/tool_registry.py
from typing import Dict, Callable, Any
from dataclasses import dataclass, field

@dataclass
class ToolDefinition:
    name: str                          # e.g., "_init_"
    handler: Callable                  # async function
    description: str                   # Human-readable
    input_schema: Dict[str, Any]       # JSON Schema
    gate: str                          # e.g., "000_GATE"
    enforces: list[str] = field(default_factory=list)  # e.g., ["F1", "F11", "F12"]

class ToolRegistry:
    """Single source of truth for all 7 canonical tools.
    All transports consume this registry — no duplication."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        return self._tools[name]

    def all_tools(self) -> Dict[str, ToolDefinition]:
        return dict(self._tools)

    def names(self) -> list[str]:
        return list(self._tools.keys())
```

---

## 4. Migration Map (Current → Target)

| Current File | → Target Location | Transformation |
|-------------|-------------------|----------------|
| `__main__.py` | `__main__.py` | Enhanced: uses ToolRegistry + transport auto-detect |
| `server.py` | `transports/stdio.py` | Strip tool defs, implement BaseTransport |
| `sse.py` | `transports/sse.py` | Strip tool defs, implement BaseTransport |
| `sse_simple.py` | `_archive/sse_simple.py` | **REMOVED** from active |
| `bridge.py` (BridgeRouter) | `governance/bridge.py` | Keep routing logic |
| `bridge.py` (CircuitBreaker) | `infrastructure/circuit_breaker.py` | Extract class |
| `bridge.py` (_serialize) | `presenters/json_presenter.py` | Extract serializer |
| `bridge.py` (action mapping) | `adapters/universal.py` | Extract to adapter |
| `session_ledger.py` | `sessions/manager.py` + `sessions/backends/file.py` | Split interface from backend |
| `immutable_ledger.py` | `sessions/ledger.py` | Merge with session audit |
| `constitutional_metrics.py` | `metrics/constitutional.py` | Move |
| `metrics.py` | `metrics/collector.py` | Merge as base collector |
| `rate_limiter.py` | `infrastructure/rate_limiter.py` | Move |
| `redis_client.py` | `sessions/backends/redis.py` | Implement SessionBackend |
| `mode_selector.py` | `config/modes.py` | Move + implement STANDALONE |
| `models.py` | `core/models.py` | Move |
| `maintenance.py` | `infrastructure/health.py` | Move |
| `trinity_server.py` | `_archive/trinity_server.py` | **ARCHIVED** |
| `mcp_config.json` | `config/mcp_config.json` | Move |
| `tools/canonical_trinity.py` | `tools/canonical_trinity.py` | Keep (core logic) |
| `tools/mcp_tools_v53.py` | `tools/mcp_tools_v53.py` | Keep (internal engine) |
| `tools/integration_claude_api.py` | `adapters/anthropic.py` | Move to adapters |
| `tools/trinity_hat.py` | `_archive/trinity_hat.py` | **ARCHIVED** |
| `tools/agi_tool.py` | `tools/_agi_.py` | Rename |
| `tools/asi_tool.py` | `tools/_asi_.py` | Rename |
| `tools/apex_tool.py` | `tools/_apex_.py` | Rename |
| `tools/vault_tool.py` | `tools/_vault_.py` | Rename |
| `tools/reality_grounding.py` | `tools/_reality_.py` | Rename |
| `tools/mcp_trinity.py` | `tools/_trinity_.py` | Rename |
| `external_gateways/*` | `external_gateways/*` | Keep + add base.py |

---

## 5. Data Flow (Hardened Architecture)

```
                    ┌─────────────────────────────────┐
                    │         MCP CLIENT               │
                    │  (Claude Desktop / Cursor /       │
                    │   VS Code / ChatGPT / Any)        │
                    └──────────────┬───────────────────┘
                                   │ JSON-RPC 2.0
                    ┌──────────────▼───────────────────┐
                    │      TRANSPORT LAYER              │
                    │  transports/auto.py detects:      │
                    │  ┌─────┐ ┌─────┐ ┌──────┐       │
                    │  │stdio│ │ SSE │ │ HTTP │       │
                    │  └──┬──┘ └──┬──┘ └──┬───┘       │
                    └─────┼───────┼───────┼────────────┘
                          │       │       │
                    ┌─────▼───────▼───────▼────────────┐
                    │     MODEL ADAPTER LAYER           │
                    │  adapters/base.py detects:        │
                    │  normalize_request() →            │
                    │  ┌─────────┐ ┌───────┐ ┌──────┐ │
                    │  │Anthropic│ │OpenAI │ │Univ. │ │
                    │  └────┬────┘ └───┬───┘ └──┬───┘ │
                    └───────┼──────────┼────────┼──────┘
                            │          │        │
                    ┌───────▼──────────▼────────▼──────┐
                    │     TOOL REGISTRY                 │
                    │  core/tool_registry.py            │
                    │  ┌──────────────────────────────┐│
                    │  │ _init_ │ _agi_ │ _asi_       ││
                    │  │ _apex_ │ _vault_ │ _trinity_ ││
                    │  │ _reality_                     ││
                    │  └──────────────────────────────┘│
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │     CONSTITUTION ENFORCER         │
                    │  constitution/enforcer.py         │
                    │  PRE-CALL:  F11 Auth, F12 Inject │
                    │  POST-CALL: F1-F10, F13          │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │     GOVERNANCE BRIDGE             │
                    │  governance/bridge.py             │
                    │  Routes to arifOS kernels:        │
                    │  AGI (Δ) → ASI (Ω) → APEX (Ψ)   │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │     INTEGRATION LAYER             │
                    │  integration/kernel.py            │
                    │  integration/vault.py             │
                    │  000 → 111-333 → 444-666 →       │
                    │  888 → 999 (VAULT seal)           │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │     SESSION + METRICS             │
                    │  sessions/manager.py (pluggable)  │
                    │  metrics/collector.py             │
                    │  sessions/ledger.py (immutable)   │
                    └─────────────────────────────────┘
```

---

## 6. Universal Compatibility Matrix

### AI Models (via adapters/)

| Model | Adapter | Status | Notes |
|-------|---------|--------|-------|
| Claude (Anthropic) | `adapters/anthropic.py` | ✅ Production | Primary development target |
| GPT-4/o (OpenAI) | `adapters/openai.py` | 🔨 Build | ChatGPT MCP Dev Mode |
| Gemini (Google) | `adapters/google.py` | 🔨 Build | Google AI Studio |
| Kimi K2.5 (Moonshot) | `adapters/kimi.py` | 🔨 Build | Kimi MCP support |
| Llama / SEA-LION | `adapters/meta.py` | 🔨 Build | Local Ollama integration |
| Any JSON-RPC | `adapters/universal.py` | ✅ Fallback | Accepts standard MCP |

### MCP Clients (via clients/)

| Client | Adapter | Transport | Config File |
|--------|---------|-----------|-------------|
| Claude Desktop | `clients/claude_desktop.py` | stdio | `claude_desktop_config.json` |
| Cursor IDE | `clients/cursor.py` | stdio | `.cursor/mcp.json` |
| VS Code (Continue) | `clients/vscode.py` | stdio | `.vscode/mcp.json` |
| Windsurf | `clients/windsurf.py` | stdio | `~/.codeium/windsurf/mcp.json` |
| ChatGPT Dev | `clients/generic.py` | SSE/HTTP | URL-based |
| Any MCP Client | `clients/generic.py` | auto | Standard MCP config |

### Transports (via transports/)

| Transport | File | Use Case | Protocol |
|-----------|------|----------|----------|
| stdio | `transports/stdio.py` | Desktop apps (Claude Desktop, Cursor) | stdin/stdout pipes |
| SSE | `transports/sse.py` | HTTP clients, remote servers | Server-Sent Events |
| HTTP | `transports/http.py` | Production REST APIs, Railway | Streamable HTTP (recommended) |
| Auto | `transports/auto.py` | Default — detects best option | Negotiated |

### Session Backends (via sessions/backends/)

| Backend | File | Use Case | Persistence |
|---------|------|----------|-------------|
| Memory | `backends/memory.py` | Development, testing | None (process lifetime) |
| File | `backends/file.py` | Single-node, current default | JSON files in `sessions/` |
| Redis | `backends/redis.py` | Distributed, production | Redis server |
| SQLite | `backends/sqlite.py` | Embedded production | Local `.db` file |

---

## 7. Implementation Priority

### Phase 1: Foundation (Week 1)
1. Create `core/tool_registry.py` — eliminate tool duplication
2. Create `transports/base.py` — BaseTransport ABC
3. Refactor `server.py` → `transports/stdio.py` (consume registry)
4. Refactor `sse.py` → `transports/sse.py` (consume registry)
5. Archive `sse_simple.py`, `trinity_server.py`, `trinity_hat.py`

### Phase 2: Separation (Week 2)
6. Extract CircuitBreaker from bridge.py → `infrastructure/circuit_breaker.py`
7. Split session_ledger → `sessions/manager.py` + `sessions/backends/file.py`
8. Merge immutable_ledger into `sessions/ledger.py`
9. Merge metrics → `metrics/collector.py` + `metrics/constitutional.py`
10. Move config files → `config/`

### Phase 3: Adapters (Week 3)
11. Create `adapters/base.py` — BaseModelAdapter ABC
12. Move integration_claude_api.py → `adapters/anthropic.py`
13. Create `adapters/universal.py` — fallback adapter
14. Create `clients/base.py` — BaseClientAdapter ABC
15. Create client configs for Claude Desktop, Cursor, VS Code

### Phase 4: Hardening (Week 4)
16. Create `constitution/enforcer.py` — pre/post tool enforcement
17. Create `sessions/backends/base.py` + memory/redis/sqlite backends
18. Create `integration/` — kernel, loop, vault hooks
19. Create `presenters/` — human, JSON, markdown output
20. Full test coverage for new architecture

---

## 8. Backward Compatibility

### Preserved
- All 7 tool names unchanged: `_init_`, `_agi_`, `_asi_`, `_apex_`, `_vault_`, `_trinity_`, `_reality_`
- JSON-RPC 2.0 protocol compliance maintained
- Entry points in pyproject.toml unchanged
- Tool input/output schemas unchanged
- Session file format backward-compatible

### Deprecated (v55, removed v56)
- Direct import of tools from `server.py` or `sse.py`
- `sse_simple.py` (removed immediately — mock responses are anti-F2)
- `trinity_server.py` (superseded by 7-core canonical)
- `MCPMode.STANDALONE` without implementation

### New
- `ToolRegistry` as single source of truth
- `BaseTransport` for pluggable transports
- `BaseModelAdapter` for model agnosticism
- `BaseClientAdapter` for platform universality
- `SessionBackend` for pluggable storage
- `constitution/enforcer.py` for systematic floor enforcement

---

**DITEMPA BUKAN DIBERI** — Architecture forged through constitutional audit, not assumed from templates.
