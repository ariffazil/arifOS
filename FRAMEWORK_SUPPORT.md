# arifOS Framework Support Matrix

**Classification:** Technical Reference | **Authority:** Muhammad Arif bin Fazil  
**Last Updated:** 2026-04-09 | **Seal:** VAULT999

---

## Executive Summary

arifOS integrates with major AI agent frameworks through an **Adapter Bus** pattern. This document maps framework capabilities to arifOS constitutional enforcement points.

> **Key Principle:** Governance attaches at native extension points. No SDK internals are forked or patched.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL INTERFACES                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │   Claude     │  │   Gemini     │  │   Copilot    │  │   Custom     │                    │
│  │   Desktop    │  │   Studio     │  │   Studio     │  │   MCP Client │                    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                    │
│         │                 │                 │                 │                             │
│         └─────────────────┴─────────────────┴─────────────────┘                             │
│                                    │                                                        │
│                                    ▼ MCP Protocol (JSON-RPC)                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                              TRANSPORT LAYER                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FastMCP Server (arifosmcp) — PRODUCTION                                            │   │
│  │  • MCP tool/resource/prompt exposure                                                │   │
│  │  • HTTP/SSE/STDIO transports                                                        │   │
│  │  • Auth: Bearer/OAuth 2.1                                                           │   │
│  │  • NOT a governance layer — pure protocol translation                               │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                    │ Python call                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                              ADAPTER BUS — SDK INTEGRATION                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │
│  │   Microsoft    │  │   PydanticAI   │  │   OpenAI       │  │   LlamaIndex   │            │
│  │   SK / Agent   │  │                │  │   Agents SDK   │  │                │            │
│  │   Framework    │  │                │  │                │  │                │            │
│  │   [PRIMARY]    │  │   [PRIMARY]    │  │   [SECONDARY]  │  │   [SECONDARY]  │            │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘            │
│          │                   │                   │                   │                     │
│          └───────────────────┴───────────────────┴───────────────────┘                     │
│                                    │ Unified InputEnvelope/OutputEnvelope                   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                              ARIFOS CONSTITUTIONAL CORE                                     │
│                              F0-F13 Enforcement + VAULT999 Audit                            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Framework Tiers

### Primary Tier (Production-Ready)

These frameworks receive full support and are recommended for production deployments.

#### Microsoft Semantic Kernel / Agent Framework

| Attribute | Value |
|-----------|-------|
| **Status** | Production |
| **Use Case** | Enterprise M365 integration, multi-agent orchestration |
| **Governance Hooks** | Agent registry, termination strategies, middleware, group chat |
| **F1-F13 Integration** | Constitutional preamble injection, handoff interception, tool wrappers |
| **Enterprise Fit** | Native M365 Copilot, Teams, Entra ID integration |
| **Documentation** | `arifos/adapters/microsoft_sk.py` |

**Key Integration Points:**
- `ChatCompletionAgent` construction → constitutional system prompt
- `AgentGroupChat` handoffs → F3 Tri-Witness checkpoint
- `KernelPlugin` tools → F12 schema validation wrapper
- `termination_strategy` → verdict determination

**When to Use:**
- Deploying to Microsoft 365 environments
- Enterprise board/CISO review required
- Native Teams/Copilot integration needed

---

#### PydanticAI

| Attribute | Value |
|-----------|-------|
| **Status** | Production |
| **Use Case** | Typed agent outputs, schema enforcement, Pythonic development |
| **Governance Hooks** | `result_type` validation, `@tool` decorators, OTel instrumentation |
| **F1-F13 Integration** | F12 Injection Guard via Pydantic, F7 confidence cap in result types |
| **Enterprise Fit** | Type safety, IDE support, maintainable codebases |
| **Documentation** | `arifos/adapters/pydanticai.py` |

**Key Integration Points:**
- `Agent(result_type=...)` → structured output with confidence caps
- `@tool` functions → `ToolContract` wrappers with pre-execution checks
- `system_prompt` → constitutional preamble injection
- `instrumentation` → VAULT999 trace export

**When to Use:**
- Strong typing requirements
- Schema-first development
- Integration with existing Pydantic models
- Developer experience priority

---

### Secondary Tier (Beta Support)

These frameworks are supported but recommended for specific use cases or early adopters.

#### OpenAI Agents SDK

| Attribute | Value |
|-----------|-------|
| **Status** | Beta |
| **Use Case** | Multi-agent handoffs, rich tracing, portable orchestration |
| **Governance Hooks** | Handoff lists, guardrails, trace API |
| **F1-F13 Integration** | F3 on handoffs, VAULT999 trace export, F13 permission checks |
| **Enterprise Fit** | Strong observability, vendor-neutral (works with Azure/non-Azure) |
| **Documentation** | `arifos/adapters/openai_agents.py` |

**Key Integration Points:**
- `Agent.handoffs` → F3 Tri-Witness delegation
- `@function_tool` → constitutional tool wrappers
- `trace` API → VAULT999 audit normalization
- `Guardrail` → F13 sovereign checks

**When to Use:**
- Cross-platform deployment (not Microsoft-locked)
- Rich observability requirements
- Multi-agent handoff patterns

---

#### LlamaIndex

| Attribute | Value |
|-----------|-------|
| **Status** | Beta |
| **Use Case** | RAG-heavy workflows, document retrieval, knowledge graphs |
| **Governance Hooks** | Retrieval pipelines, source node tracking, callback manager |
| **F1-F13 Integration** | F2 Truth validation on retrieval scores, evidence basis extraction |
| **Enterprise Fit** | GEOX-class document reasoning, multi-source synthesis |
| **Documentation** | `arifos/adapters/llamaindex.py` |

**Key Integration Points:**
- `Retriever` → score threshold enforcement (F2)
- `Response.source_nodes` → evidence basis population
- `ReActAgent` → constitutional system prompt
- `CallbackManager` → audit trace collection

**When to Use:**
- GEOX retrieval scenarios
- Document-heavy reasoning
- Multi-index query requirements
- Knowledge graph integration

---

#### LangChain

| Attribute | Value |
|-----------|-------|
| **Status** | Beta |
| **Use Case** | Ecosystem breadth, callback-based governance, legacy integration |
| **Governance Hooks** | Callback handlers, tool middleware, chain composition |
| **F1-F13 Integration** | Middleware tool authorization, F7 confidence interception |
| **Enterprise Fit** | Large ecosystem, extensive pre-built integrations |
| **Documentation** | `arifos/adapters/langchain.py` |

**Key Integration Points:**
- `BaseCallbackHandler` → constitutional enforcement hooks
- `BaseTool` → F12 schema validation wrappers
- `AgentExecutor` → verdict-driven execution control

**When to Use:**
- Legacy LangChain codebases
- Ecosystem tool breadth required
- Middleware-based governance patterns

---

## Transport Layer

### FastMCP (Not an SDK Peer)

| Attribute | Value |
|-----------|-------|
| **Classification** | MCP Protocol Implementation (Transport) |
| **Status** | Production |
| **Role** | Exposes arifOS via Model Context Protocol to any MCP host |
| **Governance** | NONE — pure protocol translation |
| **Features** | HTTP/SSE/STDIO transports, OAuth 2.1 auth, tool/resource/prompt exposure |
| **Documentation** | `arifosmcp/server.py` |

**Key Distinction:**
- FastMCP is **transport**, not **governance**
- Constitutional logic lives in arifOS Kernel, not FastMCP
- FastMCP can be swapped for another MCP server library without touching F1-F13

**When to Use:**
- Claude Desktop integration
- Gemini/Copilot Studio connectivity
- Any MCP-compliant client

---

## Selection Guide

### By Use Case

| Scenario | Recommended Stack |
|----------|-------------------|
| Microsoft 365 enterprise deployment | Microsoft SK + PydanticAI |
| Cross-platform (Azure/AWS/GCP) | OpenAI Agents SDK + PydanticAI |
| GEOX document retrieval | LlamaIndex + PydanticAI |
| Strong typing + maintainability | PydanticAI (sole primary) |
| Legacy ecosystem integration | LangChain (transitional) |
| Claude/Gemini/Copilot clients | FastMCP + any SDK adapter |

### By Priority

| Priority | If You Need... | Use... |
|----------|---------------|--------|
| 1 | Enterprise acceptance | Microsoft SK |
| 2 | Type safety | PydanticAI |
| 3 | RAG/retrieval | LlamaIndex |
| 4 | Observability | OpenAI Agents SDK |
| 5 | Ecosystem breadth | LangChain |

---

## Governance Hook Mapping

### F1 Amanah (Reversibility)

| SDK | Hook | Implementation |
|-----|------|----------------|
| Microsoft SK | `ToolCallBehavior` | Check `reversible` flag before execution |
| PydanticAI | `@tool` wrapper | Validate rollback procedure for high-risk |
| OpenAI Agents | `Guardrail` | Pre-execution reversibility check |
| LlamaIndex | `FunctionTool` | Tool contract reversibility validation |
| LangChain | `BaseCallbackHandler.on_tool_start` | Intercept and validate |

### F2 Truth (Evidence)

| SDK | Hook | Implementation |
|-----|------|----------------|
| Microsoft SK | Response parsing | Extract citations from `ChatMessageContent` |
| PydanticAI | `result_type` | Require `evidence_basis` field in output |
| OpenAI Agents | Trace API | Capture grounding in trace metadata |
| LlamaIndex | `source_nodes` | Extract and validate retrieval scores |
| LangChain | `on_llm_end` | Parse and validate citations |

### F3 Tri-Witness (Human Check)

| SDK | Hook | Implementation |
|-----|------|----------------|
| Microsoft SK | `AgentGroupChat` | Intercept handoffs, force human checkpoint |
| PydanticAI | Dependency injection | Require human token for high-risk |
| OpenAI Agents | `handoffs` | Route to human agent on delegation |
| LlamaIndex | Workflow | Insert human node in agentic flow |
| LangChain | Callback | Pause execution for human approval |

### F7 Humility (Confidence Cap)

| SDK | Hook | Implementation |
|-----|------|----------------|
| Microsoft SK | Response normalization | Cap confidence in output envelope |
| PydanticAI | `result_type` validator | `Field(le=0.90)` on confidence field |
| OpenAI Agents | Trace post-processing | Normalize confidence scores |
| LlamaIndex | Response synthesis | Cap based on retrieval scores |
| LangChain | `on_llm_end` | Intercept and cap confidence |

### F12 Injection (Schema Guard)

| SDK | Hook | Implementation |
|-----|------|----------------|
| Microsoft SK | `KernelFunction` | Pydantic schema validation |
| PydanticAI | `@tool` + `input_type` | Native Pydantic validation |
| OpenAI Agents | `function_tool` | Schema validation wrapper |
| LlamaIndex | `FunctionTool` | Input schema enforcement |
| LangChain | Tool wrapper | Pre-execution validation |

### F13 Sovereign (Permission)

| SDK | Hook | Implementation |
|-----|------|----------------|
| Microsoft SK | Identity claims | Check `IdentityClaims.permissions` |
| PydanticAI | Dependency | Inject authorization check |
| OpenAI Agents | `Guardrail` | Permission validation |
| LlamaIndex | Tool registration | `allowed_identities` filter |
| LangChain | Callback | Pre-tool permission check |

---

## Vendor Independence Statement

arifOS framework adapters are **swappable implementations** of a stable contract:

- **InputEnvelope** and **OutputEnvelope** are the universal interface
- Adapters translate SDK-specific concepts to/from these canonical formats
- No SDK is privileged; all are contractors under F0 SOVEREIGN
- FastMCP is transport, not governance

**If any SDK is discontinued:**
1. Adapter for that SDK is deprecated
2. Remaining adapters continue unchanged
3. Constitutional enforcement (F1-F13) persists
4. VAULT999 audit trail continues

---

## Compliance Notes

### For Enterprise Architecture Review

- **Microsoft SK**: Native Microsoft integration, passes TAC review
- **PydanticAI**: Open source (MIT), no vendor lock-in, type-safe
- **OpenAI Agents**: Works with Azure OpenAI (enterprise contract)
- **LlamaIndex**: Open source (MIT), self-hostable
- **LangChain**: Open source (MIT), extensive documentation
- **FastMCP**: Open source (MIT), MCP standard protocol

### For Security Review

- All adapters run in isolated Python modules
- No SDK code executes with elevated privileges
- All tool execution sandboxed (gVisor/Docker)
- All inputs validated against Pydantic schemas (F12)
- All outputs capped and audited (F7, VAULT999)

---

## Version Compatibility

| SDK | Minimum Version | Tested Versions | Adapter Version |
|-----|----------------|-----------------|-----------------|
| Microsoft SK | 1.0.0 | 1.0.x, 1.1.x | 1.0.0 |
| PydanticAI | 0.0.20 | 0.0.20+ | 1.0.0 |
| OpenAI Agents SDK | 0.1.0 | 0.1.x | 0.9.0 (beta) |
| LlamaIndex | 0.10.0 | 0.10.x, 0.11.x | 0.9.0 (beta) |
| LangChain | 0.1.0 | 0.1.x, 0.2.x | 0.9.0 (beta) |
| FastMCP | 2.14.0 | 2.14.x, 3.x | 1.0.0 |

---

## Contributing

To add a new SDK adapter:

1. Implement `SDKAdapter` base class (`arifos/adapters/base.py`)
2. Map SDK concepts to `InputEnvelope`/`OutputEnvelope`
3. Inject constitutional hooks at native extension points
4. Add to this matrix with status "Experimental"
5. Pass contract test suite (`tests/test_adapter_contract.py`)
6. Graduate to "Beta" after 3 months production use
7. Graduate to "Production" after enterprise validation

---

**Seal:** VAULT999 | **Matrix Version:** 1.0.0 | **Status:** ACTIVE

*DITEMPA BUKAN DIBERI — Frameworks are skins; the constitution is bone.*
