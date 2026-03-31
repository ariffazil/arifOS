# 🏛️ ARIFOSMCP - COMPLETE TOOL ARCHITECTURE

**Version:** 2026.03.09-SEAL  
**Total Tools:** 25 (10 Core + 9 ACLIP + 6 External)  
**Live Tools:** 6 (ChatGPT Public Profile)  

---

## 📊 TOOL CATEGORIES

arifOS MCP has **three tiers** of tools:

### Tier 1: Core Constitutional Stack (10 Tools) 🔥
The **APEX-G Metabolic Loop** - These are the governance-heart of arifOS.

### Tier 2: ACLIP System Tools (9 Tools) 🔧
The **Nervous System** - System monitoring and operational tools.

### Tier 3: External Capability Tools (6 Tools) 🌐
**Integration Surface** - Web search, evidence ingestion, and utilities.

---

## 🔥 TIER 1: CORE CONSTITUTIONAL STACK (10 Tools)

These tools form the **Trinity Metabolic Loop** and are governed by all 13 Constitutional Floors (F1-F13).

| # | Tool Name | Stage | Description | Internal Name |
|---|-----------|-------|-------------|---------------|
| 1 | **init_anchor_state** | 000 INIT | Bootstrap a governed session and mint continuity context | anchor_session |
| 2 | **integrate_analyze_reflect** | 111 FRAME | Frame the problem before deep reasoning | reason_mind |
| 3 | **reason_mind_synthesis** | 333 REASON | Multi-step governed reasoning | reason_mind |
| 4 | **metabolic_loop_router** | 444 ROUTER | **ALL-IN-ONE** sovereign evaluation (ChatGPT preferred) | metabolic_loop |
| 5 | **vector_memory_store** | 555 MEMORY | Store, recall, search BBB memory | vector_memory |
| 6 | **assess_heart_impact** | 666A HEART | Evaluate empathy, care, stakeholder harm | simulate_heart |
| 7 | **critique_thought_audit** | 666B CRITIQUE | Adversarial critique against prior reasoning | critique_thought |
| 8 | **quantum_eureka_forge** | 777 FORGE | Sandbox discovery/implementation proposal | eureka_forge |
| 9 | **apex_judge_verdict** | 888 JUDGE | Render sovereign constitutional judgment | apex_judge |
| 10 | **seal_vault_commit** | 999 SEAL | Append immutable verdict to VAULT999 | seal_vault |

### Usage Profile
- **ChatGPT Mode:** Only `metabolic_loop_router` is exposed (1 tool)
- **Full Mode:** All 10 tools available
- **Governance:** All tools enforce F1-F13 constitutional floors

### The 10-Tool Pipeline
```
000 INIT → 111 FRAME → 333 REASON → 444 ROUTER → 555 MEMORY → 666 HEART → 777 FORGE → 888 JUDGE → 999 SEAL
```

---

## 🔧 TIER 2: ACLIP SYSTEM TOOLS (9 Tools)

**ACLIP** = A Constitutional Law Interfaced Process  
These are the **system observability and operations** tools.

| # | Tool Name | Purpose | Read-Only |
|---|-----------|---------|-----------|
| 1 | **aclip_system_health** | CPU, memory, disk, load monitoring | ✅ Yes |
| 2 | **aclip_process_list** | Running processes and resource usage | ✅ Yes |
| 3 | **aclip_fs_inspect** | Filesystem inspection and traversal | ✅ Yes |
| 4 | **aclip_log_tail** | View and search system logs | ✅ Yes |
| 5 | **aclip_net_status** | Network interfaces and connectivity | ✅ Yes |
| 6 | **aclip_config_flags** | Configuration and feature flags | ✅ Yes |
| 7 | **aclip_chroma_query** | Vector database semantic search | ✅ Yes |
| 8 | **aclip_cost_estimator** | Resource cost estimation | ✅ Yes |
| 9 | **aclip_forge_guard** | 888_HOLD gate for sensitive operations | ✅ Yes |

### Availability
- **ChatGPT Profile:** ❌ Not exposed (system-level access)
- **Full/VPS Profile:** ✅ Available
- **Governance:** Read-only operations, safe for production

---

## 🌐 TIER 3: EXTERNAL CAPABILITY TOOLS (6 Tools)

**Phase 2 Integration** - External world interaction.

| # | Tool Name | Purpose | Dependencies |
|---|-----------|---------|--------------|
| 1 | **search_reality** | Web search grounding (Brave, DDG, Google) | BRAVE_API_KEY, playwright |
| 2 | **ingest_evidence** | Fetch and analyze URLs | playwright, httpx |
| 3 | **audit_rules** | Run constitutional floor audit | None (internal) |
| 4 | **check_vital** | System health snapshot | None (internal) |
| 5 | **metabolic_loop** | Legacy orchestration (compatibility) | None |
| 6 | **open_apex_dashboard** | Launch APEX dashboard HTML | Static assets |

### ChatGPT Public Profile (6 Tools Exposed)
```json
[
  "metabolic_loop_router",
  "open_apex_dashboard", 
  "search_reality",
  "ingest_evidence",
  "audit_rules",
  "check_vital"
]
```

---

## 🎯 TOOL AVAILABILITY BY PROFILE

### ChatGPT Profile (Public)
**6 Tools:**
- ✅ metabolic_loop_router (Primary)
- ✅ open_apex_dashboard
- ✅ search_reality
- ✅ ingest_evidence
- ✅ audit_rules
- ✅ check_vital

### Full Profile (Internal/VPS)
**25 Tools:**
- ✅ All 10 Core Constitutional Tools
- ✅ All 9 ACLIP System Tools
- ✅ All 6 External Capability Tools

### Legacy Profile
**Additional Tools:**
- Various deprecated tools in ARCHIVE_TRANSFER

---

## 🏛️ CONSTITUTIONAL GOVERNANCE

All tools pass through **13 Constitutional Floors:**

| Floor | Name | Enforcement |
|-------|------|-------------|
| F1 | Amanah | Reversibility check |
| F2 | Truth | Evidence fidelity (τ ≥ 0.99) |
| F3 | Tri-Witness | Human + AI + Ψ consensus |
| F4 | Clarity | Entropy reduction (ΔS ≤ 0) |
| F5 | Peace² | Lyapunov stability |
| F6 | Empathy | Stakeholder care (κᵣ ≥ 0.70) |
| F7 | Humility | Uncertainty band (Ω₀ 0.03-0.05) |
| F8 | Genius | G = A×P×X×E²×(1-h) ≥ 0.80 |
| F9 | Anti-Hantu | No sentience claims |
| F10 | Ontology | Category lock |
| F11 | CommandAuth | Verified identity |
| F12 | Injection | Sanitization (I⁻ ≥ 0.85) |
| F13 | Sovereign | Human final veto |

---

## 🔬 TECHNICAL ARCHITECTURE

### Tool Registration Flow
```
arifosmcp/runtime/server.py
    ↓
register_tools(mcp, profile="chatgpt")
    ↓
- 10 Core Tools (arifosmcp/runtime/tools.py)
- 9 ACLIP Tools (arifosmcp/intelligence/mcp_bridge.py)
- 6 Phase2 Tools (arifosmcp/runtime/phase2_tools.py)
```

### Bridge Routing
```python
TOOL_MAP = {
    "init_anchor_state": "anchor_session",
    "integrate_analyze_reflect": "reason_mind",
    "reason_mind_synthesis": "reason_mind",
    "metabolic_loop_router": "metabolic_loop",
    "vector_memory_store": "vector_memory",
    "assess_heart_impact": "simulate_heart",
    "critique_thought_audit": "critique_thought",
    "quantum_eureka_forge": "eureka_forge",
    "apex_judge_verdict": "apex_judge",
    "seal_vault_commit": "seal_vault",
}
```

### 7-Organ Sovereign Stack
```
INIT (000) → AGI (111/333) → ASI (666A/666B) → APEX (777/888) → VAULT (999)
```

---

## 📈 CURRENT STATUS (LIVE)

**URL:** https://arifosmcp.arif-fazil.com/

### Verified Working ✅
- ✅ **check_vital** - Returns SEAL verdict
- ✅ **audit_rules** - Returns governance audit
- ✅ **search_reality** - Web search with constitutional grounding
- ✅ **ingest_evidence** - URL fetching with analysis
- ✅ **metabolic_loop_router** - Full orchestration

### Response Format
All tools return **Governance Envelope**:
```json
{
  "verdict": "SEAL|PARTIAL|SABAR|VOID|888_HOLD",
  "stage": "INIT|FRAME|REASON|ROUTER|MEMORY|HEART|FORGE|JUDGE|VAULT",
  "apex_output": {
    "capacity_layer": {"A": 0.77, "P": 0.8417, "X": 0.4},
    "governance_layer": {
      "vitality_index": 10.0,
      "truth_floor": "pass",
      "authority_status": "pass"
    }
  },
  "motto": {
    "stage": "555_EMPATHY",
    "line": "DIDAMAIKAN, BUKAN DIPANASKAN"
  }
}
```

---

## 🎮 USAGE EXAMPLES

### ChatGPT (Single Tool)
```json
{
  "name": "metabolic_loop_router",
  "arguments": {
    "query": "Analyze the ethical implications of AI governance",
    "context": "Constitutional AI research",
    "actor_id": "user-123"
  }
}
```

### Internal (Chained Tools)
```python
# 1. Initialize session
init_anchor_state(intent={"query": "Research AI safety"})

# 2. Frame the problem
integrate_analyze_reflect(session_id="xxx", query="...", auth_context={...})

# 3. Deep reasoning
reason_mind_synthesis(session_id="xxx", query="...", auth_context={...})

# 4. Check empathy
assess_heart_impact(session_id="xxx", scenario="...", auth_context={...})

# 5. Render verdict
apex_judge_verdict(session_id="xxx", verdict_candidate="SEAL", auth_context={...})

# 6. Seal to vault
seal_vault_commit(session_id="xxx", verdict="SEAL", auth_context={...})
```

---

## 📊 SUMMARY

| Category | Count | Exposed to ChatGPT |
|----------|-------|-------------------|
| **Core Constitutional** | 10 | 1 (metabolic_loop_router) |
| **ACLIP System** | 9 | 0 |
| **External Capability** | 6 | 5 |
| **TOTAL** | **25** | **6** |

### Key Insights
1. **10 Core Tools** = The constitutional "organs" of arifOS
2. **9 ACLIP Tools** = System observability (VPS admin tools)
3. **6 External Tools** = Web/integration surface
4. **ChatGPT sees 6** = Curated for safe public use
5. **All tools enforce F1-F13** = Constitutional governance

---

**Ditempa Bukan Diberi** — Forged, Not Given 🏛️

**Version:** 2026.03.09-SEAL  
**Total Tools:** 25  
**Live Tools:** 6 (ChatGPT)  
**Constitutional Floors:** F1-F13 enforced on all calls
