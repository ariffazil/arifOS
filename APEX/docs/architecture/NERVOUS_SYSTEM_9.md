# Nervous System 9 — Internal Tool Architecture
## The Governed Infrastructure Layer of arifOS

**Version:** 2026.03.14-FORGED  
**Status:** Production-Ready  
**Classification:** Internal Architecture Reference  
**Last Updated:** 2026-03-14  

---

## Executive Summary

The **Nervous System 9** is the internal infrastructure layer of arifOS — nine hardened tools that provide system introspection, resource monitoring, and operational capabilities while maintaining full constitutional governance (000_INIT → 999_VAULT).

Unlike the 23 public tools that face external clients, these 9 tools form the "sense organs" of the system — they feel, monitor, and report on the internal state while staying fully governed by the 13 Constitutional Floors.

### Why 9 Tools?

The number 9 represents complete coverage of system operations:
- **3 Sense tools** (Monitoring & Inspection)
- **3 Resource tools** (Storage & Memory)  
- **3 Control tools** (Diagnostics & Cost)

**Total:** 9 tools = 100% system observability with zero blind spots.

---

## Architecture Philosophy

### The Nervous System Metaphor

Just as the human nervous system has:
- **Sensory nerves** (feel the environment)
- **Motor nerves** (control muscles)
- **Autonomic nerves** (regulate internals)

The Nervous System 9 provides:
- **Sensory tools** (system_health, process_list, net_status)
- **Memory tools** (chroma_query, arifos_list_resources, arifos_read_resource)
- **Regulatory tools** (log_tail, fs_inspect, cost_estimator)

### Governance Integration

Every tool in the Nervous System 9:
1. ✅ Accepts `session_id` for audit trail continuity
2. ✅ Accepts `auth_context` for F11 Command Auth
3. ✅ Returns `RuntimeEnvelope` (not legacy responses)
4. ✅ Maps to constitutional stages (000_INIT → 999_VAULT)
5. ✅ Subject to F12 Injection scanning
6. ✅ Logs to VAULT999 immutable ledger

**Result:** Even internal diagnostics are fully governed and tamper-evident.

---

## Tool Categories

### Category 1: System Sense (The Feelers)

These tools feel the pulse of the operating system — CPU, memory, processes, network.

#### 1. system_health
**Purpose:** Comprehensive system vital signs monitoring  
**Constitutional Stage:** 000_INIT (System Bootstrap)  
**Floors Enforced:** F1 (Amanah), F7 (Humility)  

**What It Does:**
Retrieves complete system health metrics including CPU utilization, memory consumption, disk usage, swap status, I/O counters, and thermal sensors (if available). Acts as the "vital signs monitor" for the host system.

**Why It Exists:**
Before any constitutional work begins, the system must verify it has sufficient resources to operate safely. This tool prevents resource exhaustion attacks and ensures the host can support the metabolic loop's thermodynamic budget.

**When to Use:**
- ✅ **At session startup:** Verify system can handle the workload
- ✅ **Before high-cost operations:** Check if enough RAM/disk available
- ✅ **During long-running sessions:** Monitor for resource leaks
- ✅ **In container environments:** Detect restricted resource access
- ✅ **For debugging:** Identify system-level bottlenecks

**Governance Notes:**
- Reports uncertainty bounds (F7 Humility) when metrics are estimates
- Container-aware: Detects Docker/LXC and adjusts reporting accordingly
- Non-destructive read-only operation (F1 Amanah compliant)

**Example Usage:**
```python
# Standard health check
health = await system_health(
    session_id="production-sess-001",
    auth_context={"actor_id": "monitoring-agent", "clearance": "agent"}
)

# Detailed diagnostics
health_detailed = await system_health(
    include_swap=True,      # Include swap usage
    include_io=True,        # Include I/O counters
    include_temp=True,      # Include thermal sensors
    session_id="debug-sess-002",
    auth_context={"actor_id": "sysadmin", "clearance": "sovereign"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "cpu": {"percent": 45.2, "cores": 8, "load_avg": [0.5, 0.6, 0.7]},
  "memory": {"total_gb": 32, "used_gb": 16.5, "percent": 51.5, "swap": {...}},
  "disk": {"total_gb": 500, "used_gb": 250, "percent": 50.0},
  "io": {"network": {...}, "disk": {...}},  // if include_io=True
  "thermal": {"coretemp": [45, 47, 50]},      // if include_temp=True
  "container_mode": false,
  "platform": "Linux"
}
```

---

#### 2. process_list
**Purpose:** Enumerate and filter system processes  
**Constitutional Stage:** 111_SENSE (Peripheral Awareness)  
**Floors Enforced:** F1 (Amanah - read-only), F12 (Injection Guard)  

**What It Does:**
Lists running processes with resource consumption metrics (CPU %, RAM MB, threads). Supports filtering by name, user, resource thresholds, and can operate in restricted container environments.

**Why It Exists:**
Process monitoring is essential for:
- Detecting runaway processes that could exhaust resources
- Identifying zombie/defunct processes
- Monitoring agent workload impact on the system
- Compliance auditing (who is running what)

**When to Use:**
- ✅ **Before spawning workers:** Check if too many processes already running
- ✅ **During incident response:** Find resource-hogging processes
- ✅ **For security auditing:** Verify only authorized processes present
- ✅ **In containers:** Work around /proc restrictions gracefully

**Container Resilience:**
Unlike standard process monitors that fail in Docker, this tool:
- Detects container environment automatically
- Handles "Access Denied" errors gracefully
- Reports partial data with warnings instead of failing
- Works in Kubernetes, Docker, LXC

**Example Usage:**
```python
# List top resource consumers
procs = await process_list(
    limit=10,                    # Top 10 processes
    session_id="monitor-sess-003",
    auth_context={"actor_id": "observer", "clearance": "agent"}
)

# Find specific process
python_procs = await process_list(
    filter_name="python",        # Only Python processes
    min_memory_mb=100.0,         # Using >100MB RAM
    include_threads=True,        # Include thread counts
    session_id="debug-sess-004",
    auth_context={"actor_id": "debugger", "clearance": "agent"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "total_count": 15,
  "processes": [
    {
      "pid": 1234,
      "name": "python",
      "ram_mb": 512.5,
      "cpu_pct": 12.3,
      "user": "arif",
      "created": "2026-03-14T10:30:00",
      "threads": 8
    }
  ],
  "note": "Access denied to 23 processes (container restrictions)"
}
```

---

#### 3. net_status
**Purpose:** Network connectivity and service health diagnostics  
**Constitutional Stage:** 111_SENSE (External Awareness)  
**Floors Enforced:** F2 (Truth), F7 (Humility)  

**What It Does:**
Checks connectivity to critical services (vector DB, cache, database, external APIs). Measures latency, detects DNS failures, TLS issues, and service degradation.

**Why It Exists:**
In a distributed MCP system, knowing which services are reachable is critical:
- Prevents wasting time on impossible operations
- Diagnoses "why is search failing?"
- Monitors external dependencies (Brave Search, etc.)
- Validates network configuration

**When to Use:**
- ✅ **At system startup:** Verify all dependencies available
- ✅ **When operations fail:** Is it the network or the logic?
- ✅ **Before external calls:** Check if Brave/Qdrant reachable
- ✅ **In CI/CD:** Validate deployment connectivity
- ✅ **Health checks:** Kubernetes/Docker health probes

**Truthful Reporting (F2):**
Unlike naive ping checks, this tool:
- Reports actual service availability (not just ICMP)
- Includes latency measurements
- Distinguishes DNS vs TLS vs HTTP failures
- Provides confidence scores for each check

**Example Usage:**
```python
# Full network diagnostic
net = await net_status(
    session_id="startup-sess-005",
    auth_context={"actor_id": "bootstrap", "clearance": "system"}
)

# Check specific services
services = await net_status(
    services=["qdrant", "redis", "postgres", "brave-search"],
    timeout_ms=5000,
    session_id="health-sess-006",
    auth_context={"actor_id": "health-check", "clearance": "agent"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "overall_status": "healthy",
  "checks": {
    "qdrant": {"reachable": true, "latency_ms": 12, "version": "1.8.0"},
    "redis": {"reachable": true, "latency_ms": 2},
    "postgres": {"reachable": false, "error": "Connection refused"},
    "brave-search": {"reachable": true, "latency_ms": 234}
  },
  "truth_score": 0.95  // F2 Truth threshold
}
```

---

### Category 2: Memory & Storage (The Archive)

These tools access the system's memory — vector stores, resources, and evidence.

#### 4. chroma_query
**Purpose:** Semantic search in Chroma/Qdrant vector memory  
**Constitutional Stage:** 555_MEMORY (Retrieval)  
**Floors Enforced:** F2 (Truth ≥ 0.99), F4 (ΔS Clarity)  

**What It Does:**
Performs semantic similarity search across vector embeddings stored in ChromaDB or Qdrant. Supports filtering by metadata, controlling result count, and optionally including raw embedding vectors.

**Why It Exists:**
Vector search is the backbone of arifOS memory:
- Retrieves past conversations and evidence
- Finds semantically similar documents
- Supports RAG (Retrieval-Augmented Generation)
- Enables cross-session memory continuity

**When to Use:**
- ✅ **During reflection:** Retrieve relevant past context
- ✅ **Evidence retrieval:** Find supporting documents
- ✅ **Deduplication:** Check if content already stored
- ✅ **Cross-reference:** Link new info to existing knowledge

**Dual API Support:**
Unlike tools that break with version upgrades, this handles:
- **Qdrant v1.7 and earlier:** Uses legacy `.search()` API
- **Qdrant v1.8+:** Uses modern `.query_points()` API
- **Auto-detection:** Tries modern first, falls back to legacy

**Example Usage:**
```python
# Basic semantic search
results = await chroma_query(
    query="AI safety research papers",
    n_results=5,
    session_id="research-sess-007",
    auth_context={"actor_id": "researcher", "clearance": "agent"}
)

# Filtered search with metadata
filtered = await chroma_query(
    query="constitutional AI",
    collection="academic-papers",
    n_results=10,
    where={"category": "ethics", "year": {"$gte": 2024}},
    include_embeddings=False,  # Don't return heavy vectors
    session_id="academic-sess-008",
    auth_context={"actor_id": "scholar", "clearance": "agent"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "ids": [["doc-1", "doc-2", "doc-3"]],
  "distances": [[0.12, 0.23, 0.34]],  // Lower = more similar
  "metadatas": [[{"title": "...", "author": "..."}, ...]],
  "documents": [["First doc content...", "Second doc...", ...]],
  "embeddings": null  // Omitted if include_embeddings=False
}
```

**Truth Enforcement (F2):**
- Returns confidence scores (1 - distance)
- Filters results below similarity threshold
- Never fabricates results (empty = empty, not hallucinated)

---

#### 5. arifos_list_resources
**Purpose:** Enumerate available arifOS/MCP resources  
**Constitutional Stage:** 111_SENSE (Capability Discovery)  
**Floors Enforced:** F1 (Amanah - read-only)  

**What It Does:**
Lists all registered MCP resources with their URI schemes, descriptions, and access patterns. Resources include canonical documentation, governance rules, telemetry data, and vault history. Namespaced to `arifos_` to prevent protocol collisions.

**Why It Exists:**
Clients need to discover what's available:
- "What resources can I read?"
- "How do I access the constitution?"
- "What's the latest vault entry?"
- Self-documenting API capability

**When to Use:**
- ✅ **Client initialization:** Discover available resources
- ✅ **Documentation:** Auto-generate resource catalog
- ✅ **Debugging:** Verify resources registered correctly
- ✅ **Explorer tools:** Build resource browsers

**Resource Types Exposed:**
```
canon://       - Constitutional documentation
governance://  - Governance rules and invariants
eval://        - Evaluation workflows and thresholds
schema://      - JSON schemas for tools/resources
vault://       - VAULT999 ledger entries
telemetry://   - System metrics and thermodynamics
runtime://     - Capability maps and status
ui://          - Dashboard HTML and assets
```

**Example Usage:**
```python
# List all resources
resources = await list_resources(
    session_id="discovery-sess-009",
    auth_context={"actor_id": "explorer", "clearance": "user"}
)

# Filter by type
schemas = await list_resources(
    filter_uri="schema://*",  // Only schema resources
    session_id="schema-sess-010",
    auth_context={"actor_id": "developer", "clearance": "agent"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "resources": [
    {
      "uri": "canon://floors",
      "name": "Constitutional Floors",
      "description": "All 13 floors with thresholds",
      "mimeType": "application/json",
      "size": 2048
    },
    {
      "uri": "vault://latest",
      "name": "Latest VAULT Entry",
      "description": "Last 5 sealed entries",
      "mimeType": "application/json"
    }
  ],
  "total": 15
}
```

---

#### 6. arifos_read_resource
**Purpose:** Read content of MCP resources by URI  
**Constitutional Stage:** 111_SENSE (Information Retrieval)  
**Floors Enforced:** F2 (Truth), F1 (Amanah)  

**What It Does:**
Retrieves the content of any MCP resource by its URI. Supports all resource types (canon, governance, vault, telemetry, etc.) and returns properly formatted content. Namespaced to `arifos_` to prevent protocol collisions.

**Why It Exists:**
Resources contain the "source of truth":
- Constitution definition (canon://floors)
- Current tool schemas (schema://tools)
- Vault audit trail (vault://latest)
- Live thermodynamics (telemetry://summary)

**When to Use:**
- ✅ **Accessing constitution:** Read floor definitions
- ✅ **Schema validation:** Get current input/output schemas
- ✅ **Audit review:** Read vault entries
- ✅ **Dashboard data:** Get telemetry for visualization
- ✅ **Documentation:** Auto-generate from canonical sources

**Resource Access Patterns:**
```python
# Constitutional documentation
floors = await read_resource("canon://floors")
tools = await read_resource("canon://tools")

# Governance rules
law = await read_resource("governance://law")

# Live data
latest = await read_resource("vault://latest")
metrics = await read_resource("telemetry://summary")

# Schemas
input_schema = await read_resource("schema://tools/input")
```

**Example Usage:**
```python
# Read constitutional floors
constitution = await arifos_read_resource(
    uri="canon://floors",
    session_id="const-sess-011",
    auth_context={"actor_id": "auditor", "clearance": "apex"}
)

# Read latest vault entry
latest = await arifos_read_resource(
    uri="vault://latest",
    session_id="audit-sess-012",
    auth_context={"actor_id": "validator", "clearance": "apex"}
)

# Get tool schema
schema = await arifos_read_resource(
    uri="schema://tools/input/arifOS_kernel",
    session_id="dev-sess-013",
    auth_context={"actor_id": "developer", "clearance": "agent"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing resource content (varies by resource type):
```json
// For canon://floors
{
  "floors": [
    {"number": 1, "name": "Amanah", "type": "hard", "threshold": "≥ 0.5"},
    {"number": 2, "name": "Truth", "type": "hard", "threshold": "≥ 0.99"},
    // ... all 13 floors
  ]
}

// For vault://latest
{
  "entries": [
    {
      "timestamp": "2026-03-14T10:30:00Z",
      "session_id": "sess-abc123",
      "verdict": "SEAL",
      "hash": "sha256:a1b2c3...",
      "chain_hash": "sha256:x9y8z7..."
    }
  ]
}
```

---

### Category 3: Diagnostics & Control (The Regulators)

These tools control and diagnose the system — logs, files, and costs.

#### 7. log_tail
**Purpose:** Stream and filter log files with smart defaults  
**Constitutional Stage:** 111_SENSE (Historical Awareness)  
**Floors Enforced:** F1 (Amanah - read-only), F12 (Injection Guard)  

**What It Does:**
Tails log files with filtering by pattern, time window, and line count. Features smart path detection that automatically finds the correct log file without requiring exact paths.

**Why It Exists:**
Log analysis is essential for:
- Debugging failed operations
- Audit trail verification
- Performance analysis
- Error pattern detection
- Security incident response

**Smart Path Detection:**
Instead of requiring exact paths like `/var/log/arifosmcp.log`, the tool automatically searches:
1. `arifosmcp.transport.log` (current directory)
2. `logs/arifosmcp.log` (logs subdirectory)
3. `/var/log/arifosmcp.log` (system logs)
4. `~/.arifosmcp/logs/arifosmcp.log` (user directory)

**When to Use:**
- ✅ **After failures:** Check what went wrong
- ✅ **During debugging:** Trace execution flow
- ✅ **Security audits:** Check for anomalies
- ✅ **Performance tuning:** Find slow operations
- ✅ **Monitoring:** Watch live log streams

**Example Usage:**
```python
# Auto-detect and tail default log
logs = await log_tail(
    lines=50,
    session_id="debug-sess-014",
    auth_context={"actor_id": "debugger", "clearance": "agent"}
)

# Filter for specific patterns
errors = await log_tail(
    log_file="arifosmcp.transport.log",
    lines=100,
    grep_pattern="ERROR|FATAL",  // Only error lines
    since_minutes=60,            // Last hour only
    session_id="error-sess-015",
    auth_context={"actor_id": "monitor", "clearance": "agent"}
)

# Follow mode (for real-time monitoring)
# Note: follow=True requires async iterator handling
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "lines": [
    "2026-03-14 10:30:15 [INFO] Session initialized: sess-001",
    "2026-03-14 10:30:16 [DEBUG] F12 scan passed",
    "2026-03-14 10:30:17 [INFO] Tool executed: init_anchor"
  ],
  "count": 3,
  "file": "arifosmcp.transport.log",
  "filtered": true,
  "pattern": "ERROR|FATAL"
}
```

---

#### 8. fs_inspect
**Purpose:** Inspect filesystem within governed sandbox  
**Constitutional Stage:** 111_SENSE (Storage Awareness)  
**Floors Enforced:** F1 (Amanah - read-only), F12 (Injection Guard)  

**What It Does:**
Lists directory contents with metadata (size, type, modified time) while respecting sandbox boundaries. Prevents access outside allowed directories (F12 Injection Guard).

**Why It Exists:**
File system inspection is needed for:
- Checking available evidence files
- Validating output directories
- Debugging file operations
- Audit compliance (what files exist?)

**Security Constraints:**
- Sandboxed to allowed directories only
- Cannot escape to parent directories outside sandbox
- Injection pattern scanning on all paths
- Respects container boundaries

**When to Use:**
- ✅ **Before file operations:** Verify directory exists
- ✅ **Evidence discovery:** List available evidence files
- ✅ **Debugging:** Check output directory contents
- ✅ **Validation:** Verify file creation succeeded

**Example Usage:**
```python
# Inspect working directory
files = await fs_inspect(
    path="./evidence",
    session_id="inspect-sess-016",
    auth_context={"actor_id": "inspector", "clearance": "agent"}
)

# Deep inspection with recursion
all_files = await fs_inspect(
    path="./workspace",
    include_hidden=True,      // Show hidden files
    max_depth=3,              // Recurse 3 levels deep
    session_id="deep-sess-017",
    auth_context={"actor_id": "auditor", "clearance": "apex"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "path": "./evidence",
  "files": [
    {
      "name": "evidence_001.json",
      "type": "file",
      "size": 2048,
      "modified": "2026-03-14T10:30:00Z"
    },
    {
      "name": "subdirectory",
      "type": "directory",
      "entries": 5
    }
  ],
  "total_files": 12,
  "total_dirs": 3
}
```

---

#### 9. cost_estimator
**Purpose:** Estimate operation costs before execution  
**Constitutional Stage:** 333_MIND (Planning)  
**Floors Enforced:** F4 (ΔS Clarity - Resource Planning)  

**What It Does:**
Estimates the thermodynamic and financial cost of proposed operations. Calculates token usage, time requirements, memory consumption, and API call costs before committing resources. Now supports `operation` as an alias for `operation_type` for architectural alignment.

**Why It Exists:**
Cost awareness prevents:
- Budget overruns
- Resource exhaustion
- Unexpected API charges
- Timeout failures

**Estimation Factors:**
- **Token cost:** Based on model and input/output size
- **Time estimate:** Based on operation complexity
- **Memory impact:** Temporary storage requirements
- **API costs:** External service fees (search, etc.)
- **Thermodynamic budget:** ΔS impact on system

**When to Use:**
- ✅ **Before expensive operations:** Know the cost upfront
- ✅ **Budget planning:** Estimate monthly costs
- ✅ **Resource allocation:** Plan for peak loads
- ✅ **Optimization:** Compare cost of different approaches
- ✅ **User approval:** Show costs before proceeding

**Example Usage:**
```python
# Estimate web search cost
search_cost = await cost_estimator(
    operation="web_search",
    query="AI safety research 2024",
    max_results=10,
    session_id="cost-sess-018",
    auth_context={"actor_id": "planner", "clearance": "agent"}
)

# Estimate full metabolic loop
loop_cost = await cost_estimator(
    operation="metabolic_loop",
    query="Analyze 100 research papers",
    risk_tier="high",
    use_memory=True,
    use_critique=True,
    session_id="cost-sess-019",
    auth_context={"actor_id": "architect", "clearance": "apex"}
)
```

**Returns:** `RuntimeEnvelope` with payload containing:
```json
{
  "operation": "metabolic_loop",
  "estimates": {
    "tokens_input": 1500,
    "tokens_output": 800,
    "token_cost_usd": 0.023,
    "api_calls": 3,
    "api_cost_usd": 0.015,
    "estimated_time_seconds": 45,
    "memory_peak_mb": 512,
    "thermodynamic_dS": 0.15
  },
  "total_cost_usd": 0.038,
  "affordable": true,
  "budget_remaining": 9.962
}
```

---

## Usage Patterns

### Pattern 1: Pre-Flight System Check

Before starting any constitutional work, verify the system is healthy:

```python
async def pre_flight_check(session_id: str, auth: dict) -> bool:
    # 1. Check system health
    health = await system_health(session_id=session_id, auth_context=auth)
    if health.payload.get("memory", {}).get("percent", 0) > 90:
        return False  # Too little RAM
    
    # 2. Check network connectivity
    net = await net_status(session_id=session_id, auth_context=auth)
    if not net.payload.get("checks", {}).get("qdrant", {}).get("reachable"):
        return False  # Vector DB down
    
    # 3. Check process load
    procs = await process_list(session_id=session_id, auth_context=auth)
    if procs.payload.get("total_count", 0) > 100:
        return False  # Too many processes
    
    return True
```

### Pattern 2: Debugging Failed Operations

When a tool fails, gather diagnostic info:

```python
async def debug_failure(session_id: str, auth: dict):
    # 1. Check recent logs
    logs = await log_tail(
        lines=50,
        grep_pattern="ERROR",
        since_minutes=5,
        session_id=session_id,
        auth_context=auth
    )
    
    # 2. Check system health
    health = await system_health(session_id=session_id, auth_context=auth)
    
    # 3. Check network status
    net = await net_status(session_id=session_id, auth_context=auth)
    
    return {
        "logs": logs.payload,
        "health": health.payload,
        "network": net.payload
    }
```

### Pattern 3: Cost-Aware Operation

Estimate costs before expensive operations:

```python
async def cost_aware_search(query: str, session_id: str, auth: dict):
    # 1. Estimate cost
    cost = await cost_estimator(
        operation="web_search",
        query=query,
        session_id=session_id,
        auth_context=auth
    )
    
    # 2. Check if affordable
    if cost.payload.get("total_cost_usd", 0) > 0.50:
        # Too expensive - ask for confirmation
        return {"status": "needs_approval", "cost": cost.payload}
    
    # 3. Proceed with search
    results = await search_reality(query, session_id=session_id)
    return results
```

---

## Integration with Constitutional Pipeline

### Stage Mapping

All 9 tools map to specific constitutional stages:

| Tool | Stage | Purpose |
|------|-------|---------|
| system_health | 000_INIT | Bootstrap validation |
| process_list | 111_SENSE | System awareness |
| net_status | 111_SENSE | External awareness |
| chroma_query | 555_MEMORY | Memory retrieval |
| arifos_list_resources | 111_SENSE | Capability discovery |
| arifos_read_resource | 111_SENSE | Information access |
| log_tail | 111_SENSE | Historical analysis |
| fs_inspect | 111_SENSE | Storage awareness (alias: inspect_path) |
| cost_estimator | 333_MIND | Planning & budgeting (arg: operation) |

### Governance Flow

```
Client Request
    ↓
[000_INIT] system_health (Validate system can handle request)
    ↓
[111_SENSE] Gather context:
    - net_status (Check dependencies)
    - list_resources (Discover capabilities)
    - read_resource (Load constitution/schemas)
    ↓
[333_MIND] cost_estimator (Plan resources)
    ↓
[555_MEMORY] chroma_query (Retrieve context)
    ↓
Execute Public Tool
    ↓
[666_HEART/777_FORGE] Process
    ↓
If failure:
    [111_SENSE] log_tail, fs_inspect (Debug)
    [111_SENSE] process_list (Check resources)
    ↓
[888_JUDGE] apex_judge
    ↓
[999_VAULT] vault_seal
```

---

## Security & Governance

### F12 Injection Protection

All 9 tools scan inputs for injection patterns:
- Path traversal (`../`, `..\`)
- Null bytes (`\x00`)
- Shell metacharacters
- Unicode attacks (RTLO)

### F11 Command Auth

All tools verify `auth_context`:
```python
# Minimum required clearance varies by tool
system_health:     "agent"      # Basic monitoring
process_list:      "agent"      # Basic monitoring
chroma_query:      "agent"      # Memory access
fs_inspect:        "agent"      # File reading
cost_estimator:    "user"       # Anyone can estimate
```

### Audit Trail

Every call is logged to VAULT999:
```json
{
  "tool": "system_health",
  "session_id": "sess-001",
  "actor_id": "monitoring-agent",
  "timestamp": "2026-03-14T10:30:00Z",
  "verdict": "SEAL",
  "payload_hash": "sha256:abc123..."
}
```

---

## Performance Characteristics

| Tool | Latency | CPU Impact | Memory Impact | Notes |
|------|---------|------------|---------------|-------|
| system_health | ~50ms | Low | Low | Cached for 5s |
| process_list | ~100ms | Low | Low | May be slower in containers |
| net_status | ~500ms | Low | Low | Depends on service latency |
| chroma_query | ~50-200ms | Low | Medium | Depends on result count |
| list_resources | ~10ms | Minimal | Minimal | Static lookup |
| read_resource | ~10-50ms | Minimal | Low | Depends on resource size |
| log_tail | ~50-500ms | Low | Low | Depends on lines requested |
| fs_inspect | ~50-200ms | Low | Low | Depends on directory size |
| cost_estimator | ~10ms | Minimal | Minimal | Calculation only |

---

## Error Handling

All 9 tools return errors as `RuntimeEnvelope` with:
- `verdict: "VOID"` or `"HOLD"`
- `status: "ERROR"`
- Detailed error messages in payload

Example error response:
```json
{
  "tool": "fs_inspect",
  "session_id": "sess-001",
  "stage": "111_SENSE",
  "verdict": "VOID",
  "status": "ERROR",
  "payload": {
    "error": "F12_INJECTION_DETECTED",
    "message": "Path contains traversal pattern: '../../../etc/passwd'",
    "pattern": "PATH_TRAVERSAL"
  }
}
```

---

## Version History

### 2026.03.14 — FORGED Release
- ✅ All 9 tools hardened with RuntimeEnvelope
- ✅ Governance parameters (session_id, auth_context) added
- ✅ F12 Injection protection implemented
- ✅ Container-aware system monitoring
- ✅ Smart log path detection
- ✅ Cost estimation with thermodynamic budgeting

---

## References

- [TOOL_INVENTORY.md](./TOOL_INVENTORY.md) — Complete tool reference
- [CONSTITUTION.md](../../CONSTITUTION.md) — 13 Floors specification
- [AGENTS.md](../../AGENTS.md) — Agent guidance and protocols

---

*Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*

**Document Status:** SEALED  
**Version:** 2026.03.14-FORGED  
**Classification:** Internal Architecture Reference
