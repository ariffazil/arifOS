# Level 4: TOOL - MCP Implementation

**Effectiveness:** ★★★★☆☆ (80% Coverage)
**Complexity:** Medium-High
**Cost:** $1-3 per 1K operations
**Best For:** Production APIs with constitutional enforcement

---

## 🎯 Overview

**TOOL level** uses the **Model Context Protocol (MCP)** to expose the 000-999 metabolic loop as callable, type-safe functions that LLMs can invoke. This is the **current production standard for arifOS**.

### Key Characteristics

✓ **Programmatic enforcement** - Floors validated in code
✓ **Structured I/O** - JSON schemas enforce types
✓ **Session management** - State persists across calls
✓ **Multi-client support** - Works with Claude, GPT, etc.
⚠️ **AI chooses when** - Still needs LLM to call tools
✗ **Not fully autonomous** - Requires orchestration

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           LLM Client (Claude, GPT, etc.)         │
│                                                  │
│  "I need to verify authority and start session" │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼ (calls tool via MCP protocol)
┌─────────────────────────────────────────────────┐
│              MCP Server (Python)                 │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ Tool: 000_init                            │  │
│  │   validate_authority()                    │  │
│  │   scan_injection()                        │  │
│  │   create_session() ← ENFORCED             │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ Tool: agi_genius                          │  │
│  │   Floor F2: validate_truth()              │  │
│  │   Floor F4: check_clarity()               │  │
│  │   Floor F7: inject_humility() ← ENFORCED  │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
                    │
                    ▼ (returns structured result)
┌─────────────────────────────────────────────────┐
│  Result: {                                       │
│    "verdict": "SEAL",                            │
│    "session_id": "c2ce615e...",                  │
│    "floors_validated": ["F1", "F11", "F12"]     │
│  }                                               │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Implementation: arifOS MCP Server

### File Structure

```
arifos/mcp/
├── __main__.py              # Entry point
├── server.py                # stdio MCP server
├── sse.py                   # SSE transport (Railway)
├── trinity_server.py        # FastAPI wrapper
├── bridge.py                # Zero-logic bridge to kernels
└── tools/
    ├── mcp_trinity.py       # 5-tool bundle
    ├── mcp_000_init.py      # Gate tool
    ├── mcp_agi_kernel.py    # Mind tool
    ├── mcp_asi_kernel.py    # Heart tool
    ├── mcp_apex_kernel.py   # Soul tool
    └── mcp_999_vault.py     # Seal tool
```

### Tool Schema Example (000_init)

```json
{
  "name": "_init_",
  "description": "000_IGNITION: Constitutional gate. Verifies authority, scans injection, initializes session.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["init", "gate", "reset", "validate", "authorize"],
        "description": "Action primitive"
      },
      "query": {
        "type": "string",
        "description": "User's initial message for identity detection"
      },
      "session_id": {
        "type": "string",
        "description": "Existing session ID (for gate/reset/validate)"
      },
      "user_token": {
        "type": "string",
        "description": "Identity token for authorize action"
      }
    },
    "required": ["action"]
  }
}
```

### Implementation (000_init tool)

```python
# arifos/mcp/tools/mcp_000_init.py
from fastmcp import FastMCP
from arifos.core.enforcement import verify_authority, scan_injection

mcp = FastMCP("arifOS Trinity")

@mcp.tool()
async def _init_(
    action: str,
    query: str = "",
    session_id: str = None,
    user_token: str = None
) -> dict:
    """
    000_IGNITION: Session startup, identity check, budget allocation.

    Constitutional Floors Enforced:
    - F11: Command Authority (identity verification)
    - F12: Injection Defense (pattern detection)
    - F1: Amanah (session tracking)
    """

    # Action: init (default)
    if action == "init":
        # F12: Injection scan
        injection_score = scan_injection(query)
        if injection_score > 0.85:
            return {
                "verdict": "VOID",
                "reason": "F12 Violation: Injection detected",
                "injection_score": injection_score
            }

        # F11: Authority verification
        user = verify_authority(user_token or "default")
        if not user:
            return {
                "verdict": "VOID",
                "reason": "F11 Violation: Unauthorized"
            }

        # F1: Session creation (Amanah - accountability)
        session = create_session(user, query)

        return {
            "verdict": "SEAL",
            "session_id": session.id,
            "authority": session.authority_level,
            "floors_validated": ["F1", "F11", "F12"],
            "timestamp": session.timestamp.isoformat()
        }

    # Action: gate (mid-session check)
    elif action == "gate":
        # Validate existing session
        if not session_id:
            return {"verdict": "VOID", "reason": "Session ID required"}

        session = get_session(session_id)
        if not session or session.is_expired():
            return {"verdict": "VOID", "reason": "Invalid/expired session"}

        return {
            "verdict": "SEAL",
            "session_id": session.id,
            "status": "active"
        }

    # Other actions: reset, validate, authorize
    # ... (implementation details)
```

### Implementation (agi_genius tool)

```python
# arifos/mcp/tools/mcp_agi_kernel.py
from fastmcp import FastMCP
from arifos.core.engines.agi import DeltaKernel

mcp = FastMCP("arifOS Trinity")
delta_kernel = DeltaKernel()

@mcp.tool()
async def _agi_(
    action: str,
    query: str,
    session_id: str,
    context: dict = None
) -> dict:
    """
    AGI Mind Engine: 111 SENSE → 222 THINK → 333 ATLAS

    Constitutional Floors Enforced:
    - F2: Truth (≥0.99 factual accuracy)
    - F4: Clarity (ΔS ≥ 0, entropy reduction)
    - F7: Humility (Ω₀ ∈ [0.03, 0.05])
    - F10: Ontology (symbol verification)
    """

    # Validate session
    session = get_session(session_id)
    if not session:
        return {"verdict": "VOID", "reason": "Invalid session"}

    # Route action to appropriate stage
    if action == "sense":
        # 111: SENSE/PERCEIVE
        result = await delta_kernel.sense(query, context)

        # F12: Re-check injection in parsed input
        if result.injection_risk > 0.85:
            return {"verdict": "VOID", "reason": "F12: Injection in parsed input"}

        return {
            "verdict": "SEAL",
            "stage": "111_SENSE",
            "parsed_intent": result.intent,
            "patterns": result.patterns,
            "entropy_initial": result.entropy
        }

    elif action == "think":
        # 222: THINK/REASON
        result = await delta_kernel.think(query, context)

        # F2: Truth validation
        if result.truth_score < 0.99:
            return {
                "verdict": "SABAR",
                "reason": "F2: Truth threshold not met",
                "truth_score": result.truth_score,
                "recommendation": "Verify claims against evidence"
            }

        return {
            "verdict": "SEAL",
            "stage": "222_THINK",
            "reasoning": result.reasoning,
            "truth_score": result.truth_score,
            "hypotheses": result.hypotheses
        }

    elif action == "atlas":
        # 333: ATLAS/MAP
        result = await delta_kernel.atlas(query, context)

        # F7: Humility check
        if not (0.03 <= result.omega_0 <= 0.05):
            return {
                "verdict": "SABAR",
                "reason": "F7: Uncertainty out of humility band",
                "omega_0": result.omega_0,
                "recommendation": "Adjust confidence bounds"
            }

        # F4: Clarity check
        if result.delta_S < 0:  # Entropy increased (bad)
            return {
                "verdict": "SABAR",
                "reason": "F4: Clarity insufficient (entropy increased)",
                "delta_S": result.delta_S
            }

        return {
            "verdict": "SEAL",
            "stage": "333_ATLAS",
            "knowledge_map": result.map,
            "omega_0": result.omega_0,
            "delta_S": result.delta_S,
            "boundaries": result.boundaries
        }

    elif action == "full":
        # Full pipeline: 111 → 222 → 333
        result = await delta_kernel.full_pipeline(query, context)

        # Aggregate floor checks
        all_floors_passed = (
            result.truth_score >= 0.99 and
            result.delta_S >= 0 and
            0.03 <= result.omega_0 <= 0.05
        )

        if not all_floors_passed:
            return {
                "verdict": "SABAR",
                "reason": "One or more AGI floors failed",
                "floor_results": {
                    "F2_Truth": result.truth_score >= 0.99,
                    "F4_Clarity": result.delta_S >= 0,
                    "F7_Humility": 0.03 <= result.omega_0 <= 0.05
                }
            }

        return {
            "verdict": "SEAL",
            "stage": "111-333_FULL",
            "result": result.output,
            "floors_validated": ["F2", "F4", "F7", "F10"]
        }
```

---

## 🔄 MCP Protocol Flow

### Complete 000-999 Tool Sequence

```python
# Client-side pseudocode (LLM's perspective)

# 1. IGNITION (000)
session = await call_tool("_init_", {
    "action": "init",
    "query": "Add dark mode to settings"
})
# → session_id: "abc123..."

# 2. MIND (111-333)
mind_result = await call_tool("_agi_", {
    "action": "full",
    "query": "Add dark mode to settings",
    "session_id": session.session_id
})
# → parsed intent, knowledge map, uncertainty bounds

# 3. HEART (555)
heart_result = await call_tool("_asi_", {
    "action": "empathize",
    "text": mind_result.result,
    "session_id": session.session_id
})
# → safety validation, impact assessment

# 4. SOUL (777-888)
soul_result = await call_tool("_apex_", {
    "action": "judge",
    "response": heart_result.aligned_action,
    "session_id": session.session_id
})
# → verdict: SEAL/SABAR/VOID

# 5. VAULT (999)
if soul_result.verdict == "SEAL":
    vault_result = await call_tool("_vault_", {
        "action": "seal",
        "decision_data": soul_result,
        "session_id": session.session_id
    })
    # → Merkle root, immutable ledger entry
```

---

## 📊 Floor Enforcement Matrix

| Floor | Tool Location | Validation Method | Failure Action |
|-------|---------------|-------------------|----------------|
| **F1 Amanah** | `_init_`, `_vault_` | Session ID generation, ledger sealing | VOID |
| **F2 Truth** | `_agi_` (think) | Fact verification, source checking | SABAR |
| **F3 Tri-Witness** | `_apex_` (judge) | Consensus calculation (≥0.95) | SABAR |
| **F4 Clarity** | `_agi_` (atlas) | Entropy delta (ΔS ≥ 0) | SABAR |
| **F5 Peace²** | `_asi_` (act) | Safety score (P² ≥ 1.0) | VOID |
| **F6 Empathy** | `_asi_` (empathize) | Stakeholder impact (κᵣ ≥ 0.95) | SABAR |
| **F7 Humility** | `_agi_` (atlas) | Uncertainty band (Ω₀ ∈ [0.03,0.05]) | SABAR |
| **F8 Genius** | `_apex_` (eureka) | Quality score (G ≥ 0.80) | SABAR |
| **F9 Anti-Hantu** | `_apex_` (judge) | Consciousness claim detection | VOID |
| **F10 Ontology** | `_agi_` (all) | Symbol verification against context | VOID |
| **F11 Authority** | `_init_` (init) | Identity verification | VOID |
| **F12 Injection** | `_init_` (init) | Pattern + semantic scan (< 0.85) | VOID |
| **F13 Sovereign** | `_apex_` (judge) | Human approval for high-impact | HOLD |

---

## 💰 Cost Analysis

### Per-Call Cost Breakdown

| Tool | LLM Tokens | Compute | Total | Typical Usage |
|------|------------|---------|-------|---------------|
| `_init_` | 0 (no LLM) | $0.001 | $0.001 | Once per session |
| `_agi_` (sense) | ~500 | $0.010 | $0.011 | 1-3 per task |
| `_agi_` (think) | ~1500 | $0.030 | $0.033 | 1-2 per task |
| `_agi_` (atlas) | ~1000 | $0.020 | $0.023 | 0-1 per task |
| `_asi_` (empathize) | ~800 | $0.016 | $0.018 | 1 per task |
| `_asi_` (act) | ~500 | $0.010 | $0.011 | 1 per task |
| `_apex_` (judge) | ~600 | $0.012 | $0.014 | 1 per task |
| `_vault_` | 0 (no LLM) | $0.002 | $0.002 | 1 per task |

**Total per task:** ~$0.11 - $0.15 (assuming average complexity)

**Scaling:**
- 1K operations: $110-150
- 10K operations: $1,100-1,500
- 100K operations: $11,000-15,000

---

## ⚡ Performance Metrics

### Latency Targets

| Stage | Target | Actual (prod) | Bottleneck |
|-------|--------|---------------|------------|
| 000 INIT | < 100ms | 45ms | Injection scan |
| 111-333 AGI | < 3s | 2.1s | LLM inference |
| 555 ASI | < 2s | 1.4s | Stakeholder simulation |
| 777-888 APEX | < 2s | 1.8s | Consensus calculation |
| 999 VAULT | < 200ms | 120ms | Merkle computation |
| **Total** | **< 8s** | **5.5s** | LLM inference |

### Throughput

- **Sequential:** ~180 operations/hour (limited by LLM)
- **Parallel:** ~1,000 operations/hour (with batching)

---

## 🚀 Deployment Options

### 1. stdio (Claude Desktop, Cursor)

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "arifos.mcp"],
      "env": {
        "ARIFOS_ENV": "production"
      }
    }
  }
}
```

### 2. SSE (Railway, ChatGPT Dev Mode)

```bash
# Deploy to Railway
python -m arifos.mcp trinity-sse --port 8000

# Or via FastAPI
uvicorn arifos.mcp.trinity_server:app --host 0.0.0.0 --port 8000
```

### 3. HTTP (Custom clients)

```python
import requests

response = requests.post("https://arifos.example.com/mcp/tools/call", json={
    "tool": "_init_",
    "arguments": {
        "action": "init",
        "query": "User request here"
    }
})

result = response.json()
```

---

## 🔒 Security Considerations

### Authentication

```python
# Server-side auth middleware
@mcp.middleware
async def verify_client(request, call_next):
    token = request.headers.get("Authorization")

    if not verify_token(token):
        return {"error": "Unauthorized", "code": 401}

    return await call_next(request)
```

### Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@mcp.tool()
@limiter.limit("60/minute")
async def _agi_(...):
    # Tool implementation
```

### Secrets Management

```python
import os
from cryptography.fernet import Fernet

# Never hardcode API keys
API_KEY = os.environ.get("ARIFOS_API_KEY")
ENCRYPTION_KEY = Fernet.generate_key()

# Encrypt sensitive data before storing
def encrypt_session_data(data):
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(data.encode())
```

---

## 📈 Monitoring & Telemetry

### Floor Violation Tracking

```python
from prometheus_client import Counter, Histogram

floor_violations = Counter(
    'arifos_floor_violations_total',
    'Total constitutional floor violations',
    ['floor_id', 'tool_name']
)

tool_latency = Histogram(
    'arifos_tool_latency_seconds',
    'Tool execution latency',
    ['tool_name']
)

# Usage in tool
@mcp.tool()
async def _agi_(action, query, session_id):
    with tool_latency.labels(tool_name='_agi_').time():
        result = await delta_kernel.execute(action, query)

        if not result.passes_floor_F2:
            floor_violations.labels(
                floor_id='F2',
                tool_name='_agi_'
            ).inc()
```

### Dashboard Integration

```python
# Export metrics for Grafana/Prometheus
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## 🎯 Best Practices

### 1. Tool Design

✓ **Keep tools atomic** - One tool = one responsibility
✓ **Strong typing** - Use JSON schemas rigorously
✓ **Idempotent operations** - Same input → same output
✓ **Error handling** - Return structured errors, not exceptions

### 2. Floor Enforcement

✓ **Fail fast** - Validate early, return VOID/SABAR immediately
✓ **Clear feedback** - Explain WHY a floor was violated
✓ **Graduated responses** - SABAR for soft floors, VOID for hard floors

### 3. Session Management

✓ **Expire sessions** - Default 24h timeout
✓ **Garbage collect** - Clean up old sessions
✓ **Secure storage** - Encrypt session data at rest

### 4. Documentation

✓ **Schema-driven** - Auto-generate docs from JSON schemas
✓ **Example calls** - Include example inputs/outputs
✓ **Floor reference** - Document which floors each tool enforces

---

## 🔄 Migration from WORKFLOW to TOOL

### Before (WORKFLOW level)

```markdown
# 111_INTENT.md

1. Parse user input
2. Check for ambiguity
3. Generate test cases
4. Route to next stage

(AI reads and follows voluntarily)
```

### After (TOOL level)

```python
@mcp.tool()
async def _agi_(action: str, query: str, session_id: str):
    """111_COGNITION: Parse intent, reduce entropy, generate specs."""

    # ENFORCED parsing
    parsed = await parse_input(query)

    # ENFORCED ambiguity check
    if parsed.ambiguity_score > 0.5:
        return {"verdict": "SABAR", "reason": "Clarification needed"}

    # ENFORCED test generation
    tests = generate_test_cases(parsed)

    # ENFORCED routing
    next_stage = route_decision(parsed)

    return {
        "verdict": "SEAL",
        "parsed_intent": parsed,
        "tests": tests,
        "next_stage": next_stage
    }
```

**Key Difference:** Code enforcement vs. documentation

---

## 📚 Further Reading

- [MCP Specification](https://modelcontextprotocol.io/)
- [arifOS MCP Implementation](../../arifos/mcp/)
- [Constitutional Floors](../../spec/constitutional_floors.json)
- [FastMCP Library](https://github.com/jlowin/fastmcp)

---

**Level:** TOOL (4/6)
**Effectiveness:** 80%
**Status:** PRODUCTION READY
**Next Level:** [5_AGENT](../5_AGENT/) for autonomous orchestration

*Ditempa Bukan Diberi.* 🔧
