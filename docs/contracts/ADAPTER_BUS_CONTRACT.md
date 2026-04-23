# arifOS Adapter Bus Contract

**Classification:** Canonical Specification | **Authority:** Muhammad Arif bin Fazil  
**Version:** 1.0.0 | **Seal:** VAULT999

---

## 1. Contract Philosophy

> **"The constitution travels with the agent; SDKs are merely transport skins."**

The Adapter Bus is the **universal translation layer** between arifOS constitutional governance and external agent frameworks. It ensures:

1. **F1-F13 enforcement** occurs regardless of underlying SDK
2. **Audit normalization** into VAULT999 regardless of trace format
3. **Vendor independence** through swappable adapters

---

## 2. The Wire Format

### 2.1 InputEnvelope

All SDK adapters receive requests in this canonical format:

```python
class InputEnvelope(BaseModel):
    """
    Canonical input to any Adapter Bus SDK adapter.
    SDK-agnostic representation of an agent request.
    """
    
    # Identity
    identity: IdentityClaims
    # {
    #   "did": "did:arif:abc123...",
    #   "roles": ["geoscientist", "contractor"],
    #   "permissions": ["read:seismic", "write:prospects"],
    #   "issuer": "BLS-DID",
    #   "expiry": "2026-04-09T12:00:00Z"
    # }
    
    # Request
    objective: str                    # Natural language or structured query
    context: Dict[str, Any]           # Session context, memory references
    risk_tier: Literal["low", "medium", "high"]
    budget_tier: Literal["T0", "T1", "T2", "T3"] = "T1"
    
    # Constitutional metadata
    required_floors: List[str] = ["F1", "F2", "F7", "F13"]  # Floors to enforce
    witness_required: bool = False    # F3 Tri-Witness: force human checkpoint
    
    # Routing
    preferred_sdk: Optional[str] = None  # Hint: "microsoft_sk", "pydanticai", etc.
    tool_constraints: List[str] = []     # Allowed/forbidden tool patterns
    
    # Provenance
    trace_id: str = Field(default_factory=lambda: f"trace-{uuid.uuid4().hex[:16]}")
    parent_trace_id: Optional[str] = None  # For sub-requests
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # MCP context (when invoked via FastMCP)
    mcp_context: Optional[Dict[str, Any]] = None
    # {
    #   "request_id": "req-123",
    #   "client_id": "claude-desktop",
    #   "session_id": "sess-456"
    # }
```

### 2.2 OutputEnvelope

All SDK adapters return responses in this canonical format:

```python
class OutputEnvelope(BaseModel):
    """
    Canonical output from any Adapter Bus SDK adapter.
    Normalized for VAULT999 audit regardless of SDK source.
    """
    
    # Identification
    trace_id: str                     # Matches InputEnvelope.trace_id
    correlation_id: str               # SDK-specific run ID
    
    # Status
    status: Literal["OK", "HOLD", "REFUSE", "ERROR"]
    
    # Constitutional verdict
    verdict: JudgeVerdict
    # {
    #   "verdict": "ALLOW" | "HOLD" | "REFUSE",
    #   "reason": "F13 Sovereign: High-risk operation requires human approval",
    #   "entropy_delta": 0.15,
    #   "confidence_cap": 0.90,
    #   "requires_human": true,
    #   "constitutional_floors_invoked": ["F1", "F13"]
    # }
    
    # Output content
    output: Union[str, Dict[str, Any], BaseModel]
    output_schema: Optional[str] = None  # Name of schema if structured
    
    # Epistemic metadata (F2 Truth, F7 Humility)
    confidence: float = Field(ge=0.0, le=0.90)  # HARD CAP per F7
    evidence_basis: List[str] = []              # Citations, sources
    uncertainty_score: float = Field(ge=0.0, le=1.0)
    unknowns: List[str] = []                    # Explicit gaps
    
    # Action tracking (F1 Amanah)
    actions_taken: List[ActionRecord] = []
    # {
    #   "action_id": "act-789",
    #   "tool_name": "geox_evaluate_prospect",
    #   "reversible": false,
    #   "rollback_procedure": null,
    #   "audit_hash": "sha256:abc..."
    # }
    
    # SDK provenance
    sdk_trace: SDKTrace
    # {
    #   "sdk": "microsoft_sk",
    #   "adapter_version": "1.0.0",
    #   "sdk_specific": {  # Opaque blob per SDK
    #     "sk_agent_name": "geox_agent",
    #     "sk_conversation_id": "conv-xyz"
    #   }
    # }
    
    # Timing
    latency_ms: int
    tokens_consumed: Optional[TokenUsage] = None
    
    # MCP response context (when returning via FastMCP)
    mcp_response: Optional[MCPResponse] = None
    
    class Config:
        # Ensure F7 compliance on all outputs
        @validator('confidence')
        def enforce_f7_humility(cls, v):
            return min(v, 0.90)
```

### 2.3 ToolContract

Tools exposed through the Adapter Bus:

```python
class ToolContract(BaseModel):
    """
    Canonical tool definition for Adapter Bus registration.
    """
    
    # Identity
    name: str                         # Unique tool identifier
    description: str                  # For agent consumption
    
    # Schema (F12 Injection Guard)
    input_schema: Type[BaseModel]     # Pydantic model for validation
    output_schema: Type[BaseModel]    # Expected output structure
    
    # Risk classification (F1 Amanah)
    risk_tier: Literal["low", "medium", "high"]
    reversible: bool                  # Can action be undone?
    rollback_procedure: Optional[str] = None  # How to undo
    
    # Execution
    executor: Callable[..., Any]      # The actual tool function
    sandbox_required: bool = True     # Must run in isolated environment
    timeout_seconds: int = 60
    
    # Governance
    allowed_identities: List[str] = []  # Role/DID patterns
    audit_level: Literal["full", "summary", "none"] = "full"
    
    # MCP exposure (via FastMCP)
    expose_via_mcp: bool = True
    mcp_annotations: Optional[Dict[str, Any]] = None
```

---

## 3. Adapter Responsibilities

### 3.1 Core Contract

Every SDK adapter MUST:

| Responsibility | Implementation |
|---------------|----------------|
| **F1 Amanah** | Check `reversible` flag; require `rollback_procedure` for high-risk tools |
| **F2 Truth** | Extract and validate `evidence_basis` from SDK response; flag uncited claims |
| **F3 Tri-Witness** | Intercept handoffs/agent-delegation; force human checkpoint if `witness_required` |
| **F7 Humility** | HARD CAP `confidence` at 0.90; reject or normalize SDK confidence scores |
| **F12 Injection** | Validate all inputs against `ToolContract.input_schema` before execution |
| **F13 Sovereign** | Check `identity.permissions` against tool `allowed_identities`; trigger 888_HOLD on violation |
| **VAULT999 Audit** | Emit `OutputEnvelope` with full trace to audit ledger |

### 3.2 SDK-Specific Mapping

Each adapter maps SDK concepts to the canonical contract:

#### Microsoft SK / Agent Framework

| SK Concept | Adapter Bus Mapping |
|-----------|---------------------|
| `ChatCompletionAgent` | `InputEnvelope` → agent invocation |
| `KernelPlugin` / tools | `ToolContract` registration |
| `AgentGroupChat` handoffs | F3 Tri-Witness checkpoint |
| `ChatMessageContent` | `OutputEnvelope.output` |
| `termination_strategy` | `verdict` determination |
| `Kernel` telemetry | `SDKTrace.sdk_specific` |

**Injection Points:**
- System prompt concatenation (constitutional preamble)
- `FunctionCallBehavior` wrapper (tool pre-execution check)
- `AgentChat` callback (handoff interception)

#### PydanticAI

| PydanticAI Concept | Adapter Bus Mapping |
|-------------------|---------------------|
| `Agent` | `InputEnvelope` → typed agent run |
| `@tool` decorated functions | `ToolContract` with Pydantic validation |
| `result_type` / `output_type` | `OutputEnvelope.output_schema` |
| `system_prompt` | Constitutional preamble injection |
| `model` | Via `preferred_sdk` routing hint |
| `instrumentation` (OTel) | `SDKTrace` + custom exporter |

**Injection Points:**
- `Agent` construction (system prompt)
- Tool wrapper (pre-execution F12 validation)
- `ResultValidator` (F2 evidence extraction)

#### OpenAI Agents SDK

| OpenAI Agents Concept | Adapter Bus Mapping |
|----------------------|---------------------|
| `Agent` | `InputEnvelope` → agent |
| `handoffs` | F3 Tri-Witness on delegation |
| `@function_tool` | `ToolContract` |
| `Runner.run()` | Full execution with tracing |
| `Guardrail` | F13 permission check |
| `Trace` | `SDKTrace.sdk_specific` + VAULT999 export |

**Injection Points:**
- `Agent.instructions` (constitutional preamble)
- Tool wrapper (pre-call kernel check)
- `trace` processor (audit normalization)

#### LangChain

| LangChain Concept | Adapter Bus Mapping |
|------------------|---------------------|
| `AgentExecutor` | `InputEnvelope` → chain |
| `BaseTool` | `ToolContract` |
| `CallbackHandler` | Constitutional enforcement hooks |
| `AgentFinish` | `OutputEnvelope` construction |
| `LLMChain` telemetry | `SDKTrace` |

**Injection Points:**
- `BaseCallbackHandler.on_tool_start` (F13 check)
- `BaseCallbackHandler.on_llm_end` (F7 confidence cap)
- Tool wrapper (F12 schema validation)

#### LlamaIndex

| LlamaIndex Concept | Adapter Bus Mapping |
|-------------------|---------------------|
| `ReActAgent` | `InputEnvelope` → agent |
| `FunctionTool` | `ToolContract` |
| `Retriever` / query engines | Evidence basis extraction (F2) |
| `Response` source_nodes | `evidence_basis` population |
| `CallbackManager` | Audit trace collection |

**Injection Points:**
- `system_prompt` (constitutional preamble)
- Retrieval callback (score threshold for F2)
- Response synthesis (citation enforcement)

---

## 4. FastMCP Integration

FastMCP is the **MCP transport layer**, not an SDK adapter peer:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              MCP HOSTS (Claude, Gemini, Copilot)                            │
│                                    ↓ MCP Protocol (JSON-RPC)                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                              FASTMCP TRANSPORT LAYER                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FastMCP Server (arifosmcp)                                                         │   │
│  │  • Tool registration: `arifos_kernel.execute()` wrapped tools                       │   │
│  │  • Resource exposure: VAULT999 audit logs                                           │   │
│  │  • Prompt templates: Constitutional system prompts                                  │   │
│  │  • Auth: Bearer/OAuth 2.1 (transport-level)                                         │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                    ↓ Python call                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                              ADAPTER BUS (SDK Orchestration)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   adapter_   │  │   adapter_   │  │   adapter_   │  │   adapter_   │  │   adapter_   │  │
│  │   microsoft  │  │   pydanticai │  │   openai     │  │   llamaindex │  │   langchain  │  │
│  │     _sk      │  │              │  │   _agents    │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                    ↓ Unified Interface                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                              ARIFOS CONSTITUTIONAL CORE                                     │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │    F0       │   │    F1       │   │    F2       │   │    F7       │   │    F13      │   │
│  │  SOVEREIGN  │   │   AMANAH    │   │   TRUTH     │   │  HUMILITY   │   │  SOVEREIGN  │   │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   │
│                                                                                             │
│                              arifOS Kernel (Sense→Judge→Route→Execute)                     │
│                              VAULT999 Audit Ledger                                          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 FastMCP Responsibilities

| Layer | FastMCP | Adapter Bus |
|-------|---------|-------------|
| **Protocol** | MCP JSON-RPC, STDIO/HTTP/SSE | N/A (abstracted) |
| **Auth** | Bearer tokens, OAuth 2.1 | IdentityClaims validation |
| **Tool exposure** | `@mcp.tool()` decoration | `ToolContract` execution |
| **Constitutional logic** | NONE (pass-through) | FULL (F1-F13) |
| **Audit** | Forward to VAULT999 | VAULT999 ledger |

### 4.2 FastMCP Tool Wrapper

```python
# arifosmcp/server.py

from fastmcp import FastMCP, Context
from arifos.kernel import ArifOSKernel
from arifos.adapter_bus import AdapterBus

mcp = FastMCP("arifos")
kernel = ArifOSKernel()
bus = AdapterBus(kernel)

@mcp.tool()
async def arifos_execute(
    objective: str,
    risk_tier: str = "low",
    ctx: Context = None
) -> dict:
    """
    Execute through arifOS constitutional kernel.
    FastMCP is transport; governance is in kernel.
    """
    # Build InputEnvelope from MCP context
    envelope = InputEnvelope(
        objective=objective,
        risk_tier=risk_tier,
        identity=extract_identity_from_mcp(ctx),
        mcp_context={
            "request_id": ctx.request_id,
            "client_id": ctx.client_id
        }
    )
    
    # Route via Adapter Bus (selects appropriate SDK)
    result = bus.execute(envelope)
    
    # Return normalized OutputEnvelope
    return result.dict()
```

---

## 5. Adapter Implementation Template

```python
# arifos/adapters/base.py

from abc import ABC, abstractmethod
from typing import Type

class SDKAdapter(ABC):
    """
    Base class for all SDK adapters.
    Implements the Adapter Bus contract.
    """
    
    SDK_NAME: str = "abstract"
    ADAPTER_VERSION: str = "1.0.0"
    
    def __init__(self, kernel: ArifOSKernel):
        self.kernel = kernel
        self.tools: Dict[str, ToolContract] = {}
    
    @abstractmethod
    def execute(self, envelope: InputEnvelope) -> OutputEnvelope:
        """
        Execute request through SDK runtime.
        MUST:
        1. Inject constitutional preamble
        2. Wrap all tools with F1-F13 checks
        3. Cap confidence at 0.90 (F7)
        4. Extract evidence basis (F2)
        5. Normalize to OutputEnvelope
        6. Audit to VAULT999
        """
        pass
    
    @abstractmethod
    def register_tool(self, contract: ToolContract) -> str:
        """
        Register tool with SDK-specific wrapper.
        """
        pass
    
    def _create_constitutional_preamble(self, floors: List[str]) -> str:
        """
        Generate constitutional system prompt for injection.
        """
        return f"""
[arifOS CONSTITUTIONAL FRAMEWORK - MANDATORY]

Active Floors: {', '.join(floors)}

F1 AMANAH: Check reversibility before action. High-risk ops require rollback plan.
F2 TRUTH: All claims require evidence (τ ≥ 0.99). Cite sources explicitly.
F3 TRI-WITNESS: Human approval required for: irreversible actions, high uncertainty, conflicting evidence.
F7 HUMILITY: Confidence must be stated as 0.00-0.90. Never exceed 0.90.
F13 SOVEREIGN: 888_HOLD triggers automatically on constitutional violation.

Response format:
- Evidence: [Specific citations]
- Confidence: [0.00-0.90]
- Verdict: [PROCEED/HOLD/REFUSE]

[END CONSTITUTION]
        """.strip()
    
    def _enforce_f7_humility(self, confidence: float) -> float:
        """HARD CAP confidence at 0.90."""
        return min(float(confidence), 0.90)
    
    def _audit_to_vault999(self, envelope: OutputEnvelope):
        """Normalize and write to audit ledger."""
        self.kernel.audit.log(envelope)
```

---

## 6. Framework Coverage Matrix

| Framework / SDK | Status | Governance Hooks | Adapter Location |
|----------------|--------|-----------------|------------------|
| **Microsoft SK / Agent Framework** | Production | Agent registry, termination strategy, middleware | `arifos/adapters/microsoft_sk.py` |
| **PydanticAI** | Production | Typed outputs, validation, OTel instrumentation | `arifos/adapters/pydanticai.py` |
| **OpenAI Agents SDK** | Beta | Handoffs, traces, guardrails | `arifos/adapters/openai_agents.py` |
| **LangChain** | Beta | Callback handlers, tool middleware | `arifos/adapters/langchain.py` |
| **LlamaIndex** | Beta | Retrieval pipelines, score thresholds | `arifos/adapters/llamaindex.py` |
| **FastMCP** | Production | MCP transport, NOT SDK peer | `arifosmcp/server.py` (transport layer) |

---

## 7. Validation

### 7.1 Contract Test Suite

```python
# tests/test_adapter_contract.py

class TestAdapterContract:
    """
    All adapters must pass these tests.
    """
    
    def test_f7_confidence_cap(self, adapter: SDKAdapter):
        """Confidence > 0.90 must be capped."""
        envelope = InputEnvelope(
            objective="Test query",
            identity=test_identity
        )
        
        # Mock SDK returning confidence 0.95
        with mock_sdk_response(confidence=0.95):
            result = adapter.execute(envelope)
        
        assert result.confidence <= 0.90
    
    def test_f12_schema_validation(self, adapter: SDKAdapter):
        """Invalid tool inputs must be rejected."""
        tool = ToolContract(
            name="test_tool",
            input_schema=ValidInputSchema,
            risk_tier="low"
        )
        
        adapter.register_tool(tool)
        
        # Try invalid input
        with pytest.raises(F12Violation):
            adapter.execute_tool("test_tool", invalid_input)
    
    def test_vault999_audit(self, adapter: SDKAdapter):
        """All executions must write to audit ledger."""
        envelope = InputEnvelope(objective="Test", identity=test_identity)
        result = adapter.execute(envelope)
        
        # Verify audit record exists
        audit_record = kernel.audit.get(result.trace_id)
        assert audit_record is not None
        assert audit_record.sdk_trace["sdk"] == adapter.SDK_NAME
```

---

## 8. Summary

The Adapter Bus Contract ensures:

1. **InputEnvelope**: Canonical request format from any source (MCP, direct API, internal)
2. **OutputEnvelope**: Canonical response format to VAULT999 regardless of SDK
3. **ToolContract**: Standardized tool definition with F1-F13 metadata
4. **SDKAdapter**: Abstract base enforcing constitutional compliance
5. **FastMCP**: Transport layer, NOT governance layer

**The Constitution travels. SDKs are interchangeable skins. The Bus is the universal translator.**

---

**Seal:** VAULT999 | **Contract Version:** 1.0.0 | **Status:** ACTIVE

*DITEMPA BUKAN DIBERI — The constitution is portable law.*
