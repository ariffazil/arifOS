
================================================================================
                    AAA MCP ARCHITECTURE v55.5
            Model-Agnostic | Platform-Universal | Constitutionally-Hardened

                    Artifact · Authority · Architecture
================================================================================

PRINCIPLES
================================================================================

1. MODEL AGNOSTICISM
   - Works with ANY AI model (Claude, GPT, Gemini, Kimi, Llama, etc.)
   - No model-specific code in core
   - Adapter pattern for model-specific quirks

2. PLATFORM UNIVERSALITY  
   - Works with ANY MCP client (Claude Desktop, Cursor, VS Code, etc.)
   - Works with ANY transport (stdio, SSE, HTTP, WebSocket)
   - Works on ANY OS (Linux, macOS, Windows)

3. CONSTITUTIONAL HARDENING
   - F1-F13 floors enforced on EVERY tool call
   - AAA band separation (human/AI data boundaries)
   - Audit trail for ALL operations

================================================================================
                    UNIFIED DIRECTORY STRUCTURE
================================================================================

mcp/
├── README.md                          # Universal AAA MCP documentation
├── __init__.py                        # Universal exports
├── __main__.py                        # Auto-detect transport & start
│
├── config/                            # Configuration management
│   ├── __init__.py
│   ├── loader.py                      # Load config from env/files
│   ├── modes.py                       # STUDIO/PROD/DEBUG modes
│   ├── mcp_config.json                # Tool schemas (dynamic)
│   └── defaults.yaml                  # Default configuration
│
├── core/                              # Core MCP protocol (MODEL AGNOSTIC)
│   ├── __init__.py
│   ├── protocol.py                    # MCP protocol abstractions
│   ├── server_base.py                 # Base server class
│   ├── tool_registry.py               # Dynamic tool registration
│   └── version.py                     # Version info
│
├── transports/                        # TRANSPORT LAYER (Universal)
│   ├── __init__.py
│   ├── base.py                        # Abstract transport base
│   ├── stdio.py                       # Standard I/O transport
│   ├── sse.py                         # Server-Sent Events
│   ├── http.py                        # HTTP/REST transport
│   ├── websocket.py                   # WebSocket transport
│   └── auto.py                        # Auto-detect transport
│
├── adapters/                          # MODEL ADAPTERS (Agnostic)
│   ├── __init__.py
│   ├── base.py                        # Abstract adapter base
│   ├── anthropic.py                   # Claude/Anthropic adapter
│   ├── openai.py                      # GPT/OpenAI adapter
│   ├── google.py                      # Gemini adapter
│   ├── kimi.py                        # Moonshot/Kimi adapter
│   ├── meta.py                        # Llama/Meta adapter
│   └── universal.py                   # Fallback universal adapter
│
├── clients/                           # CLIENT ADAPTERS (Platform Universal)
│   ├── __init__.py
│   ├── base.py                        # Abstract client base
│   ├── claude_desktop.py              # Claude Desktop
│   ├── cursor.py                      # Cursor IDE
│   ├── vscode.py                      # VS Code extension
│   ├── windsurf.py                    # Windsurf
│   └── generic.py                     # Generic MCP client
│
├── tools/                             # CONSTITUTIONAL TOOLS
│   ├── __init__.py
│   ├── registry.py                    # Dynamic tool discovery
│   ├── canonical_trinity.py           # _init_, _agi_, _asi_, _apex_
│   ├── _init_.py                      # 000_GATE initialization
│   ├── _agi_.py                       # 111-333_MIND tools
│   ├── _asi_.py                       # 444-666_HEART tools
│   ├── _apex_.py                      # 777-888_SOUL tools
│   ├── _vault_.py                     # 999_SEAL tools
│   ├── _trinity_.py                   # Cross-engine tools
│   ├── _reality_.py                   # External gateway tools
│   └── _help_.py                      # Documentation tools
│
├── constitution/                      # F1-F13 FLOOR ENFORCEMENT
│   ├── __init__.py
│   ├── floors.py                      # Floor definitions
│   ├── validators.py                  # Floor validation logic
│   ├── guards.py                      # Floor guards
│   ├── enforcer.py                    # Main enforcement engine
│   ├── metrics.py                     # Constitutional metrics
│   └── verdicts.py                    # SEAL/SABAR/VOID logic
│
├── sessions/                          # SESSION MANAGEMENT
│   ├── __init__.py
│   ├── manager.py                     # Session lifecycle
│   ├── store.py                       # Session storage interface
│   ├── backends/                      # Pluggable backends
│   │   ├── __init__.py
│   │   ├── memory.py                  # In-memory (dev)
│   │   ├── file.py                    # File-based
│   │   ├── redis.py                   # Redis backend
│   │   └── sqlite.py                  # SQLite backend
│   └── ledger.py                      # Session audit ledger
│
├── governance/                        # GOVERNANCE LAYER
│   ├── __init__.py
│   ├── apex_prime.py                  # Final judgment
│   ├── dials.py                       # APEX Dials (4 scores)
│   ├── bridge.py                      # Universal bridge
│   ├── prompts/                       # Governance prompts
│   │   ├── __init__.py
│   │   ├── constitutional.txt
│   │   ├── trinity.txt
│   │   └── coaching.txt
│   └── coaching.py                    # AI coaching (not scoring)
│
├── metrics/                           # METRICS & OBSERVABILITY
│   ├── __init__.py
│   ├── collector.py                   # Metrics collection
│   ├── exporter.py                    # Metrics export
│   ├── constitutional.py              # Floor metrics
│   └── performance.py                 # Performance metrics
│
├── presenters/                        # OUTPUT FORMATTING
│   ├── __init__.py
│   ├── base.py                        # Abstract presenter
│   ├── human.py                       # Human-readable
│   ├── json.py                        # JSON output
│   ├── markdown.py                    # Markdown output
│   └── decoder.py                     # Structured explanation
│
├── infrastructure/                    # INFRASTRUCTURE
│   ├── __init__.py
│   ├── rate_limiter.py                # Rate limiting
│   ├── circuit_breaker.py             # Circuit breaker
│   ├── caching.py                     # Caching layer
│   └── health.py                      # Health checks
│
├── external_gateways/                 # EXTERNAL INTEGRATIONS
│   ├── __init__.py
│   ├── base.py                        # Gateway base
│   ├── search.py                      # Search gateway
│   ├── knowledge.py                   # Knowledge base gateway
│   └── reality.py                     # Reality gateway
│
├── integration/                       # arifOS INTEGRATION
│   ├── __init__.py
│   ├── kernel.py                      # Kernel interface
│   ├── loop.py                        # Loop manager hook
│   ├── vault.py                       # Vault hook
│   └── engines.py                     # AGI/ASI/APEX hooks
│
└── tests/                             # TEST SUITE
    ├── __init__.py
    ├── test_transports.py
    ├── test_adapters.py
    ├── test_tools.py
    ├── test_constitution.py
    └── test_integration.py

================================================================================
                    KEY ARCHITECTURAL PATTERNS
================================================================================

1. TRANSPORT ABSTRACTION
   ----------------------
   All transports implement BaseTransport:

   class BaseTransport(ABC):
       @abstractmethod
       async def start(self, handler: Callable): ...

       @abstractmethod
       async def send(self, message: JSONRPCMessage): ...

       @abstractmethod
       async def receive(self) -> JSONRPCMessage: ...

   Transports are PLUGGABLE and HOT-SWAPPABLE.

2. MODEL ADAPTER PATTERN
   ----------------------
   All adapters implement BaseModelAdapter:

   class BaseModelAdapter(ABC):
       @abstractmethod
       def normalize_request(self, raw: Any) -> MCPRequest: ...

       @abstractmethod
       def normalize_response(self, mcp_response: MCPResponse) -> Any: ...

       @abstractmethod
       def extract_context(self, raw: Any) -> Dict: ...

   Adapters handle model-specific quirks WITHOUT changing core logic.

3. CLIENT ADAPTER PATTERN
   -----------------------
   All client adapters implement BaseClientAdapter:

   class BaseClientAdapter(ABC):
       @abstractmethod
       def detect(self) -> bool: ...  # Auto-detect if running in this client

       @abstractmethod
       def configure(self) -> Dict: ...  # Return client-specific config

       @abstractmethod
       def get_capabilities(self) -> Set[str]: ...

   Clients are AUTO-DETECTED at startup.

4. PLUGGABLE SESSION BACKENDS
   ---------------------------
   Session storage is backend-agnostic:

   class SessionBackend(ABC):
       @abstractmethod
       async def get(self, session_id: str) -> Session: ...

       @abstractmethod
       async def set(self, session_id: str, session: Session): ...

       @abstractmethod
       async def delete(self, session_id: str): ...

   Backends: memory (dev), file (single-node), Redis (distributed),
            SQLite (embedded), PostgreSQL (enterprise).

================================================================================
                    FILE MAPPINGS (Current -> Hardened)
================================================================================

CURRENT FILE                    ->  HARDENED LOCATION
--------------------------------------------------------------------------------
mcp/__init__.py                 ->  mcp/__init__.py (enhanced)
mcp/__main__.py                 ->  mcp/__main__.py (enhanced)
mcp/server.py                   ->  mcp/core/server_base.py + mcp/transports/stdio.py
mcp/sse.py                      ->  mcp/transports/sse.py
mcp/sse_simple.py               ->  ❌ REMOVE (redundant)
mcp/mcp_config.json             ->  mcp/config/mcp_config.json (dynamic)
mcp/schemas.py                  ->  mcp/core/schemas.py
mcp/models.py                   ->  mcp/core/models.py
mcp/apex_prime.py               ->  mcp/governance/apex_prime.py
mcp/bridge.py                   ->  mcp/governance/bridge.py (refactored)
mcp/dials.py                    ->  mcp/governance/dials.py
mcp/governance_prompt.py        ->  mcp/governance/prompts/constitutional.txt
mcp/constitutional_metrics.py   ->  mcp/constitution/metrics.py
mcp/metrics.py                  ->  mcp/metrics/collector.py
mcp/rate_limiter.py             ->  mcp/infrastructure/rate_limiter.py
mcp/redis_client.py             ->  mcp/sessions/backends/redis.py
mcp/session_ledger.py           ->  mcp/sessions/ledger.py
mcp/immutable_ledger.py         ->  mcp/sessions/ledger.py (merged)
mcp/mode_selector.py            ->  mcp/config/modes.py
mcp/decoder.py                  ->  mcp/presenters/decoder.py
mcp/maintenance.py              ->  mcp/infrastructure/health.py
mcp/tools/                      ->  mcp/tools/ (enhanced)
mcp/sessions/                   ->  mcp/sessions/ (reorganized)
mcp/external_gateways/          ->  mcp/external_gateways/ (enhanced)

================================================================================
