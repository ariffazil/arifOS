# arifOS Architecture: Kernel vs Drivers

**Version:** v52.5.1-SEAL  
**Authority:** Muhammad Arif Fazil (Petronas Scholar)  
**Status:** System Design Reference  
**Date:** 2026-01-25

---

## Overview

arifOS is a **monolithic kernel** with optional **pluggable drivers**. This document defines:

1. **Core Kernel** (immutable governance logic)
2. **Driver Interfaces** (pluggable transport, storage, engines)
3. **Deployment Topologies** (single-process, distributed, federated)
4. **Boundary Conditions** (what stays in kernel vs moves to drivers)

---

## Core Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        arifOS Kernel (Python)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ 000_init     │  │ agi_genius   │  │ asi_act      │         │
│  │ Gate         │  │ Mind (Δ)     │  │ Heart (Ω)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│       │                   │                   │                │
│       └───────────────────┴───────────────────┘                │
│                   (Shared Memory)                              │
│                       ↓                                        │
│  ┌──────────────────────────────────────────────┐             │
│  │         apex_judge (Soul Ψ)                  │             │
│  │  Tri-Witness Consensus & Verdict             │             │
│  └──────────────────────────────────────────────┘             │
│                       ↓                                        │
│  ┌──────────────────────────────────────────────┐             │
│  │        999_vault (Seal & Ledger)             │             │
│  │    Merkle Proofs, Audit Trail                │             │
│  └──────────────────────────────────────────────┘             │
│                                                                │
│  KERNEL LOGIC (Immutable):                                   │
│  • F1–F13 Floors (enforcement)                               │
│  • TEACH principles (validation)                             │
│  • ATLAS-333 routing (intent detection)                      │
│  • Tri-Witness consensus (verdict logic)                     │
│  • Session state management                                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
         ↑                                    ↓
    Transport In                        Transport Out
    (MCP/SSE/stdin)                     (HTTP/SSE/stdout)
         ↑                                    ↓
┌────────────────────────────────────────────────────────────────┐
│                    DRIVER LAYER (Pluggable)                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Transport Drivers          Engine Drivers                    │
│  ┌────────────────────┐    ┌────────────────────┐            │
│  │ SSE (FastAPI)      │    │ LLM Engines        │            │
│  │ HTTP/REST          │    │ • GPT-4 (OpenAI)   │            │
│  │ Stdio (CLI)        │    │ • Claude (Antr.)   │            │
│  │ WebSocket          │    │ • Gemini (Google)  │            │
│  │ gRPC (future)      │    │ • Local (Ollama)   │            │
│  └────────────────────┘    └────────────────────┘            │
│                                                                │
│  Storage Drivers                 Observability Drivers        │
│  ┌────────────────────┐    ┌────────────────────┐            │
│  │ VAULT Backend      │    │ Dashboard / UI     │            │
│  │ • SQLite (local)   │    │ • Telemetry export │            │
│  │ • PostgreSQL       │    │ • Metrics API      │            │
│  │ • Blockchain       │    │ • Logs              │            │
│  │ • Git (immutable)  │    │ • Traces            │            │
│  └────────────────────┘    └────────────────────┘            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Kernel (Core Governance)

The **kernel** is the inviolable decision-making logic. It CANNOT be changed without formal RFC + governance vote.

### Kernel Responsibilities

| Component | Function | Inputs | Outputs |
|-----------|----------|--------|---------|
| **000_init** | Session bootstrap, lane detection, floor activation | query, session_id (opt), authority_token | session_id, lane, engines_ready |
| **agi_genius** | Truth, Clarity, Humility checks | query, response, session_id | truth_score, clarity_delta, humility_score, floor_results |
| **asi_act** | Amanah, Peace, Empathy checks | response, context, session_id | empathy_score, peace_squared, reversibility_check, floor_results |
| **apex_judge** | Tri-Witness consensus, final verdict | agi_result, asi_result, session_id | verdict (SEAL/SABAR/VOID/888_HOLD), confidence, floor_summary |
| **999_vault** | Immutable sealing, merkle proofs, audit trail | session_id, verdict, metadata | seal_id, merkle_root, timestamp, proof |

### Kernel State Management

```
session = {
    "session_id": "uuid-...",
    "query": "user question",
    "lane": "FACTUAL | CARE | CRISIS | SOCIAL",
    "authority": {"verified": bool, "weight": float, "role": str},
    "engines": {
        "agi": {"status": "IDLE|PROCESSING|DONE", "result": {...}},
        "asi": {"status": "IDLE|PROCESSING|DONE", "result": {...}},
        "apex": {"status": "IDLE|PROCESSING|DONE", "result": {...}}
    },
    "verdict": "SEAL | SABAR | VOID | 888_HOLD",
    "tri_witness_consensus": float,  # 0.0–1.0
    "sealed": bool,
    "merkle_root": "0x...",
    "timestamps": {
        "created": "2026-01-25T...",
        "agi_done": "2026-01-25T...",
        "asi_done": "2026-01-25T...",
        "apex_done": "2026-01-25T...",
        "vault_sealed": "2026-01-25T..."
    }
}
```

### Kernel Constraints (Immutable)

1. **F1–F13 Floors** — Cannot be disabled or weakened. Must pass all active floors for SEAL.
2. **Tri-Witness Consensus** — All three engines must evaluate independently. No shortcuts.
3. **888_HOLD Escalation** — CRISIS lane + deadlock (TW < 0.70) always triggers human confirmation.
4. **Merkle Sealing** — Every verdict sealed immutably in 999_vault.
5. **Audit Trail** — Every engine decision logged with timestamp + authority.

---

## Drivers (Pluggable Extensions)

**Drivers** are implementation details. They CAN be swapped without kernel change.

### 1. Transport Drivers

#### SSE/FastAPI (Current Default)
```python
# arifos/drivers/transport_sse.py
async def handle_000_init_request(query: str, session_id: Optional[str]):
    return await kernel.mcp_000_init(query, session_id)
```

**Interfaces:**
- Input: HTTP POST + JSON → kernel
- Output: HTTP 200 + JSON ← kernel

**Status:** ✅ Deployed (Railway)

#### HTTP/REST (Future)
```python
# arifos/drivers/transport_http.py
@app.post("/api/v1/decisions/")
async def create_decision(request: DecisionRequest):
    return await kernel.full_pipeline(request)
```

#### Stdio/CLI (Future)
```bash
echo '{"query": "Is X true?"}' | arifos-kernel | jq .verdict
```

#### WebSocket (Future)
Real-time streaming of engine evaluations as they happen.

#### gRPC (Future)
High-performance binary protocol for inter-service communication.

---

### 2. Engine Drivers (LLM Backends)

Each engine (AGI, ASI, APEX) can use different LLM backends.

#### agi_genius Engine

**Current:** GPT-4 + heuristic keyword checks

```python
# arifos/drivers/engines/agi_gpt4.py
async def compute_truth_score(response: str) -> float:
    # Approach 1: Ask GPT-4
    prompt = f"Is this accurate? {response}\n\nConfidence (0–1):"
    confidence = await gpt4(prompt)  # 0.92
    
    # Approach 2: Heuristic
    heuristic = keyword_penalty(response)  # 0.97
    
    return 0.6 * confidence + 0.4 * heuristic
```

**Alternative Drivers:**
- **agi_heuristic_only** — No LLM; pure string analysis
- **agi_specialized** — Domain-specific models (medical truth: MedBERT)
- **agi_offline** — Local model (Ollama + Mistral-7B)

#### asi_act Engine

**Current:** LLM + stakeholder detection

```python
# arifos/drivers/engines/asi_claude.py
async def compute_empathy_coefficient(response: str) -> float:
    # Ask Claude to identify vulnerable groups
    prompt = f"Who is the weakest stakeholder in this context?\n{response}"
    analysis = await claude(prompt)
    return stakeholder_harm_score(analysis)
```

**Alternative Drivers:**
- **asi_heuristic** — Keyword-based vulnerability detection
- **asi_causal_graph** — Graph-based stakeholder impact modeling
- **asi_domain_expert** — Expert system per domain (medical, legal, parenting)

#### apex_judge Engine

**Current:** Deterministic Tri-Witness consensus

```python
# arifos/drivers/engines/apex_deterministic.py
def judge(agi_result, asi_result, apex_result) -> Verdict:
    verdicts = [agi_result["verdict"], asi_result["verdict"], apex_result["verdict"]]
    
    if all(v == "SEAL" for v in verdicts):
        return Verdict.SEAL
    elif verdicts.count("SEAL") >= 2:
        return Verdict.SABAR  # Majority rules
    elif "VOID" in verdicts:
        return Verdict.VOID if count("VOID") >= 2 else Verdict.SABAR
    else:
        return Verdict.HOLD_888
```

**Alternative Drivers:**
- **apex_llm** — Use LLM to synthesize verdict
- **apex_weighted** — Weighted voting (some engines trusted more)
- **apex_byzantine** — Byzantine fault tolerance (4+ engines)

---

### 3. Storage Drivers (VAULT999 Backend)

#### SQLite (Current Local Default)
```python
# arifos/drivers/storage_sqlite.py
def seal_verdict(session_id, verdict, merkle_root):
    db.execute("""
        INSERT INTO vault (session_id, verdict, merkle_root, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    """, (session_id, verdict, merkle_root))
```

**Status:** ✅ Simple, works offline. NOT immutable.

#### PostgreSQL
```python
# arifos/drivers/storage_postgres.py
async def seal_verdict(session_id, verdict, merkle_root):
    await pool.execute("""
        INSERT INTO vault (session_id, verdict, merkle_root, sealed_at)
        VALUES ($1, $2, $3, NOW())
    """, session_id, verdict, merkle_root)
```

**Status:** ✅ Scalable, production-ready. Requires external backup for immutability.

#### Blockchain (Future: Ethereum/Polygon)
```python
# arifos/drivers/storage_blockchain.py
async def seal_verdict(session_id, verdict, merkle_root):
    tx = await web3.eth.send_transaction({
        "to": "0xARIFOS_VAULT",
        "data": encode_seal(session_id, verdict, merkle_root)
    })
    return tx.hash
```

**Status:** ⚠️ Planned. Immutable but slow + expensive.

#### Git (Append-Only Log)
```python
# arifos/drivers/storage_git.py
def seal_verdict(session_id, verdict, merkle_root):
    record = f"{session_id},{verdict},{merkle_root}\n"
    with open("vault.log", "a") as f:
        f.write(record)
    os.system(f"git add vault.log && git commit -m 'Seal {session_id}'")
    return git_rev_parse("HEAD")
```

**Status:** ✅ Immutable (Git history), free. Best for small-to-medium orgs.

---

### 4. Observability Drivers

#### Dashboard/UI (Current)
```
https://arifos.arif-fazil.com/dashboard
```

Shows real-time:
- SEAL/SABAR/VOID verdict counts
- Lane distribution (CRISIS, FACTUAL, CARE, SOCIAL)
- Floor violation heatmap
- TW consensus distribution

#### Metrics API (Prometheus)
```
https://arifos.arif-fazil.com/metrics/json
```

Outputs:
```json
{
  "arifos_verdicts_total{verdict=SEAL}": 1234,
  "arifos_verdicts_total{verdict=SABAR}": 56,
  "arifos_verdicts_total{verdict=VOID}": 12,
  "arifos_tri_witness_consensus": 0.94,
  "arifos_engine_latency_ms": {"agi": 145, "asi": 82, "apex": 23}
}
```

#### Tracing (Jaeger/OpenTelemetry)
```python
# arifos/drivers/observability_otel.py
@tracer.start_as_current_span("000_init")
async def _000_init(query, session_id):
    # Span automatically records latency, errors, span tree
    pass
```

#### Logs (Structured JSON)
```json
{
  "timestamp": "2026-01-25T10:47:00Z",
  "session_id": "abc123",
  "event": "verdict_issued",
  "verdict": "SEAL",
  "tri_witness": 1.0,
  "floors": {"F1": "PASS", "F2": "PASS", ...},
  "latency_ms": 342
}
```

---

## Deployment Topologies

### Topology 1: Monolith (Current)

```
User → SSE/HTTP → FastAPI (000_init + agi + asi + apex + vault) → Response
```

**Characteristics:**
- Single Railway process
- Shared memory (fast)
- Single point of failure

**Recommended for:** Development, small teams, sandboxed usage.

**Setup:**
```bash
python -m arifos.mcp sse  # Runs SSE server on port 5000
```

---

### Topology 2: Modular Monolith (Recommended for Enterprise)

```
User → Load Balancer → [FastAPI Instance 1] ← PostgreSQL Vault
                      [FastAPI Instance 2] ← (shared DB)
                      [FastAPI Instance N]
```

**Characteristics:**
- Multiple kernel instances (stateless)
- Shared PostgreSQL vault (consistent audit trail)
- Load balanced (HA, auto-scale)

**Recommended for:** Production SaaS, enterprise deployments.

**Setup:**
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: arifos_vault
  
  arifos:
    image: ghcr.io/ariffazil/arifos:v52.5.1-SEAL
    replicas: 3
    environment:
      VAULT_BACKEND: postgresql
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/arifos_vault
```

---

### Topology 3: Microservices (Not Recommended Yet)

```
User → API Gateway → [000_init] → [agi_genius] ↘
                                    [asi_act]   → [apex_judge] → [999_vault] → Response
                                                ↗
```

**Characteristics:**
- Each engine in separate container
- Network latency between engines
- Complex orchestration

**NOT RECOMMENDED because:**
- Latency increases 10x (milliseconds → hundreds of ms)
- Distributed consensus harder (network partitions)
- Operational complexity increases

**Only consider if:** agi/asi/apex need different scaling (e.g., agi_genius gets 10x load).

---

### Topology 4: Federated (Future Vision)

```
Org A (Kernel)          Org B (Kernel)           Org C (Kernel)
│                       │                         │
└─ Consensus Pool ──────┼─────────────────────────┘
     (cross-org)        │
                   Query Routing

Enables: Community consensus, dispute resolution, decentralized governance.
```

---

## Kernel vs Driver Boundaries

### Rules

**Stay in Kernel:**
- F1–F13 floor definitions + thresholds
- TEACH principles
- Tri-Witness consensus logic
- Session state machine
- 888_HOLD escalation rules

**Move to Driver:**
- LLM backend (GPT-4, Claude, Ollama, etc.)
- Transport protocol (SSE, gRPC, HTTP, etc.)
- Storage backend (SQLite, PostgreSQL, blockchain, Git)
- Observability (Prometheus, Jaeger, custom dashboards)
- Authentication (OAuth, API keys, mTLS)

### Example: Swapping the Truth Engine

**Bad (couples to kernel):**
```python
# Inside kernel, hardcoded
def compute_truth_score(response):
    confidence = await gpt4(response)  # ❌ Hardcoded
    return confidence
```

**Good (driver pattern):**
```python
# arifos/drivers/engines/agi_interface.py
class AGIEngine(ABC):
    @abstractmethod
    async def compute_truth_score(self, response: str) -> float: pass

# arifos/drivers/engines/agi_gpt4.py
class AGIEngineGPT4(AGIEngine):
    async def compute_truth_score(self, response: str) -> float:
        return await gpt4_confidence(response)

# arifos/drivers/engines/agi_heuristic.py
class AGIEngineHeuristic(AGIEngine):
    async def compute_truth_score(self, response: str) -> float:
        return keyword_penalty(response)

# In kernel, use interface
class Kernel:
    def __init__(self, agi_engine: AGIEngine):
        self.agi = agi_engine
    
    async def evaluate(self, response):
        truth = await self.agi.compute_truth_score(response)
```

**Benefit:** Swap `AGIEngineGPT4` ↔ `AGIEngineHeuristic` without touching kernel.

---

## Configuration Management

### Config Hierarchy

```
defaults (arifos/config/defaults.yaml)
   ↓
environment variables (ARIFOS_*)
   ↓
config file (arifos.yaml)
   ↓
runtime overrides (CLI flags)
```

### Example Config File

```yaml
# arifos.yaml

kernel:
  floors: all  # Enable all F1–F13
  tri_witness_threshold: 0.95

engines:
  agi:
    driver: gpt4  # or: heuristic, offline
    config:
      model: gpt-4-turbo
      temperature: 0.0
      max_tokens: 500
  
  asi:
    driver: claude
    config:
      model: claude-3-opus
      temperature: 0.1
  
  apex:
    driver: deterministic
    consensus_threshold: 0.95

storage:
  vault:
    driver: postgresql  # or: sqlite, blockchain, git
    config:
      connection_string: postgresql://localhost/arifos_vault
      retention_days: 365

transport:
  driver: sse  # or: http, grpc, websocket
  config:
    port: 5000
    workers: 4
    rate_limit_per_minute: 600

observability:
  dashboard_enabled: true
  metrics_endpoint: /metrics/json
  tracing:
    enabled: true
    exporter: jaeger
    jaeger_host: localhost:6831
```

---

## Performance Characteristics

| Layer | Latency | Notes |
|-------|---------|-------|
| **Kernel (in-memory)** | ~1ms | Session init, floor checks |
| **agi_genius (GPT-4)** | 500–2000ms | LLM reflection dependency |
| **asi_act (Claude)** | 300–1500ms | Empathy modeling |
| **apex_judge (deterministic)** | 10–50ms | Consensus logic only |
| **999_vault (PostgreSQL)** | 50–200ms | Network + disk I/O |
| **Total (monolith, sequential)** | ~1–4s | E2E latency |
| **Total (parallelized AGI+ASI)** | ~2–3s | Both engines run in parallel |

**Optimization opportunities:**
- Caching engine results (Redis)
- Streaming responses (don't wait for full response before evaluation)
- Early exit (if F1 Amanah fails, skip F2–F7)

---

## Testing Strategy

### Unit Tests (arifos/tests/unit/)
Test kernel logic in isolation:
```python
def test_tri_witness_consensus():
    """All three engines agree → SEAL"""
    agi_result = {"verdict": "SEAL"}
    asi_result = {"verdict": "SEAL"}
    apex_result = {"verdict": "SEAL"}
    
    assert apex_judge(agi_result, asi_result, apex_result) == Verdict.SEAL
```

### Integration Tests (arifos/tests/integration/)
Test kernel + driver interaction:
```python
async def test_full_pipeline_gpt4():
    """Full pipeline with GPT-4 engine"""
    kernel = Kernel(
        agi_engine=AGIEngineGPT4(),
        asi_engine=ASIEngineClaude(),
        storage=StoragePostgreSQL()
    )
    
    verdict = await kernel.evaluate("Is the moon made of cheese?")
    assert verdict == Verdict.VOID
```

### Driver Tests (arifos/tests/drivers/)
Test each driver independently:
```python
async def test_engine_agi_heuristic():
    """agi_heuristic driver without LLM"""
    engine = AGIEngineHeuristic()
    
    score = await engine.compute_truth_score("2+2=4")
    assert score > 0.95
```

---

## Migration Path (v52 → v53 → v54)

### v52.5.1-SEAL (Current)
- Monolith kernel
- SSE transport
- PostgreSQL storage
- GPT-4 / Claude engines

### v53.0.0 (2026-Q3)
- [ ] Docker containerization
- [ ] Helm chart for K8s
- [ ] Prometheus metrics export
- [ ] Structured JSON logging
- [ ] Config file support

### v54.0.0 (2026-Q4)
- [ ] Pluggable engine interface (ABC)
- [ ] gRPC transport option
- [ ] Blockchain VAULT option
- [ ] OpenTelemetry tracing
- [ ] Multi-LLM support (Gemini, Llama)

---

## Conclusion

**arifOS is architected as a kernel + drivers.**

- **Kernel:** Immutable governance logic (13 floors, TEACH, Tri-Witness)
- **Drivers:** Pluggable LLM, storage, transport, observability

This separation enables:
- Stability (kernel doesn't change)
- Flexibility (engines/backends swappable)
- Scalability (multiple topologies supported)
- Testability (unit/integration/driver tests)

---

**Motto:** Ditempa Bukan Diberi — Forged, Not Given  
**Authority:** Muhammad Arif Fazil, Δ Chief  
**Last Updated:** 2026-01-25
