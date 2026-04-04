# arifOS AAA MCP Tools — Complete Reference

**Version:** 2026.3.1-jina  
**Authority:** ARIF FAZIL (888 Judge)  
**Total Tools:** 13 (+ 1 unified)  
**Protocol:** MCP 2025-11-25 (JSON-RPC 2.0)  
**Endpoint:** https://arifosmcp.arif-fazil.com/mcp  
**Last Updated:** 2026-03-01 — Jina Reader Integration

---

## Quick Reference

| # | Tool | Stage | Type | Purpose |
|---|------|-------|------|---------|
| 1 | `anchor_session` | 000 INIT | Governance | Start constitutional session |
| 2 | `reason_mind` | 333 REASON | Governance | AGI cognition with grounding |
| 3 | `recall_memory` | 444 EVIDENCE | Governance | Retrieve memory traces |
| 4 | `simulate_heart` | 555 EMPATHY | Governance | Stakeholder impact analysis |
| 5 | `critique_thought` | 666 ALIGN | Governance | 7-model critique |
| 6 | `apex_judge` | 888 APEX JUDGE | Governance | Constitutional verdict |
| 7 | `eureka_forge` | 777 EUREKA FORGE | Governance | Execute with sovereign gates |
| 8 | `seal_vault` | 999 SEAL | Governance | Commit to immutable ledger |
| 9 | `search_reality` | External | Utility | Web evidence discovery (Jina Reader primary) |
| 10 | `fetch_content` | External | Utility | Fetch raw content |
| 11 | `inspect_file` | External | Utility | Filesystem inspection |
| 12 | `audit_rules` | External | Utility | Rule compliance check |
| 13 | `check_vital` | External | Utility | System health metrics |

---

## Governance Tools (9)

### 1. `anchor_session` — 000 INIT

**Purpose:** Ignite constitutional session and generate continuity token

**Stage:** 000 INIT (Entry gate)

**Parameters:**
- `query` (str): Initial user query
- `actor_id` (str, optional): User/system identifier
- `prior_session_id` (str, optional): Continuity from previous session
- `context` (dict, optional): Additional context
- `config` (dict, optional): Session configuration
- `debug` (bool, optional): Enable debug mode

**Returns:**
```json
{
  "verdict": "SEAL|SABAR|VOID",
  "tool": "anchor_session",
  "session_id": "sess_2026_02_23_1234",
  "continuity_token": "abc123...",
  "trinity": "Delta",
  "axioms_333": {...},
  "laws_13": {...},
  "telemetry": {...},
  "motto": "Ditempa bukan diberi",
  "data": {
    "session_state": {...},
    "defense_scan": {...}
  }
}
```

**Constitutional Compliance:**
- F1 Amanah: Creates audit trail from session start
- F12 Defense: Runs injection/jailbreak scan
- F13 Sovereignty: Establishes human authority context

**Trinity References:**
- Layer: HUMAN (🧍)
- Authority: arif-fazil.com/llms.txt
- Canon: apex.arif-fazil.com (F1, F12, F13 definitions)

---

### 2. `reason_mind` — 333 REASON

**Purpose:** Run AGI cognition with grounding and budget controls

**Stage:** 333 REASON (AGI Mind / Logic)

**Parameters:**
- `query` (str): Question or reasoning task
- `session_id` (str): Active session ID
- `context` (dict, optional): Additional context
- `grounding_sources` (list, optional): Evidence sources
- `budget` (dict, optional): Computation budget limits
- `debug` (bool, optional): Debug mode

**Returns:**
```json
{
  "verdict": "SEAL|SABAR|VOID",
  "tool": "reason_mind",
  "trinity": "Delta",
  "data": {
    "reasoning": "...",
    "confidence": 0.95,
    "uncertainty": 0.05,
    "grounding_quality": {...}
  },
  "axioms_333": {...},
  "laws_13": {...},
  "telemetry": {
    "entropy_delta": -0.3,
    "genius_score": 0.87
  }
}
```

**Constitutional Compliance:**
- F2 Truth: Factuality score ≥ 0.99
- F4 Clarity: Entropy reduction (ΔS ≤ 0)
- F7 Humility: Uncertainty bounds (3-5%)

**Trinity References:**
- Layer: THEORY (⚖️)
- Canon: apex.arif-fazil.com (F2, F4, F7 floors)
- Docs: arifos.arif-fazil.com/api

---

### 3. `recall_memory` — 444 EVIDENCE

**Purpose:** Retrieve associative memory traces for current thought

**Stage:** 444 EVIDENCE (Memory/Phoenix)

**Parameters:**
- `query` (str): Memory query
- `session_id` (str): Active session
- `k` (int, optional): Number of memories to retrieve

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "recall_memory",
  "data": {
    "memories": [
      {
        "content": "...",
        "similarity": 0.92,
        "source": "...",
        "timestamp": "..."
      }
    ],
    "total_retrieved": 5
  }
}
```

**Constitutional Compliance:**
- F3 Tri-Witness: Cross-references past evidence
- F8 Genius: Pattern recognition across sessions

---

### 4. `simulate_heart` — 555 EMPATHY

**Purpose:** Evaluate stakeholder impact and care constraints

**Stage:** 555 EMPATHY (ASI Heart / Safety)

**Parameters:**
- `query` (str): Action or decision to evaluate
- `stakeholders` (list): Affected parties
- `session_id` (str): Active session
- `context` (dict, optional): Additional context
- `debug` (bool, optional): Debug mode

**Returns:**
```json
{
  "verdict": "SEAL|SABAR",
  "tool": "simulate_heart",
  "trinity": "Omega",
  "data": {
    "stakeholder_analysis": {...},
    "empathy_score": 0.95,
    "harm_vector": {...},
    "safety_margins": {...}
  }
}
```

**Constitutional Compliance:**
- F5 Peace: Dynamic stability check
- F6 Empathy: Stakeholder protection ≥ 0.95

**Trinity References:**
- Layer: THEORY (⚖️)
- Canon: apex.arif-fazil.com (F5, F6 floors)

---

### 5. `critique_thought` — 666 ALIGN

**Purpose:** Run 7-model critique (inversion, framing, non-linearity, etc.)

**Stage:** 666 ALIGN (Alignment/Critique)

**Parameters:**
- `plan` (dict): Decision or plan to critique
- `session_id` (str): Active session
- `context` (str, optional): Additional context
- `debug` (bool, optional): Debug mode

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "critique_thought",
  "data": {
    "model_flags": {
      "non_linearity": true,
      "gray_thinking": true,
      "occams_bias": true,
      "framing_bias": false,
      "anti_comfort": true,
      "delayed_discomfort": false,
      "inversion": true
    },
    "critique_summary": "...",
    "alignment_score": 0.88
  }
}
```

**Constitutional Compliance:**
- F8 Genius: Multi-model coherence check
- F4 Clarity: Identifies cognitive biases

---

### 6. `apex_judge` — 888 APEX JUDGE

**Purpose:** Sovereign constitutional verdict synthesis

**Stage:** 888 APEX JUDGE (Authority/Judgment)

**Parameters:**
- `session_id` (str): Active session
- `query` (str): Original query
- `agi_result` (dict): Result from reason_mind
- `asi_result` (dict): Result from simulate_heart
- `implementation_details` (dict): Critique/evidence
- `proposed_verdict` (str): Suggested verdict
- `human_approve` (bool, optional): Human override
- `apex_override` (dict, optional): Judge override
- `context` (dict, optional): Context
- `config` (dict, optional): Config
- `debug` (bool, optional): Debug

**Returns:**
```json
{
  "verdict": "SEAL|SABAR|VOID|888_HOLD",
  "tool": "apex_judge",
  "trinity": "Psi",
  "data": {
    "constitutional_verdict": "SEAL",
    "floors_passed": ["F1", "F2", "F3", ...],
    "floors_failed": [],
    "requires_human_approval": false,
    "reasoning": "..."
  },
  "apex_dials": {
    "sovereignty_preserved": true,
    "authority_valid": true,
    "reversibility_ensured": true
  }
}
```

**Constitutional Compliance:**
- F11 Authority: Sovereign command validation
- F13 Sovereignty: Human veto check
- All 13 floors: Final synthesis

**Trinity References:**
- Layer: THEORY (⚖️)
- Canon: apex.arif-fazil.com/llms.txt
- Authority: ARIF FAZIL (888 Judge)

---

### 7. `eureka_forge` — 777 EUREKA FORGE

**Purpose:** Execute action payload behind sovereign control gates

**Stage:** 777 EUREKA FORGE (Execution gate)

**Parameters:**
- `action_payload` (dict): Action to execute
- `session_id` (str): Active session
- `signature` (str): Cryptographic signature
- `execution_context` (dict, optional): Execution environment

**Returns:**
```json
{
  "verdict": "SEAL|888_HOLD",
  "tool": "eureka_forge",
  "data": {
    "execution_result": {...},
    "reversibility_backup": {...},
    "human_approval_required": false
  }
}
```

**Constitutional Compliance:**
- F1 Amanah: Creates reversibility backup
- F13 Sovereignty: 888_HOLD for irreversible actions

**888_HOLD Triggers:**
- Database mutations
- Production deployments
- Irreversible external actions
- Credential modifications

---

### 8. `seal_vault` — 999 SEAL

**Purpose:** Commit immutable session decision record to VAULT999

**Stage:** 999 SEAL (Ledger commit)

**Parameters:**
- `session_id` (str): Session to seal
- `summary` (str): Decision summary
- `verdict` (str, optional): Final verdict (default: SEAL)

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "seal_vault",
  "data": {
    "vault_id": "vault_2026_02_23_1234",
    "audit_hash": "sha256:abc123...",
    "sealed_at": "2026-02-23T12:34:56Z",
    "immutable": true
  }
}
```

**Constitutional Compliance:**
- F1 Amanah: Immutable audit trail
- F2 Truth: Cryptographic hash chain

**Trinity References:**
- Ledger: VAULT999 (Postgres)
- Verification: Use `verify_canon_hashes()` WebMCP tool

---

## Utility Tools (4)

### 9. `search_reality` — External Evidence

**Purpose:** Web evidence discovery with clean Markdown extraction (read-only)

**Backend Priority:**
1. **Jina Reader** (PRIMARY) — Clean Markdown extraction, superior content quality
2. Perplexity AI (fallback)
3. Brave Search (fallback)
4. Local knowledge base (final fallback)

**Parameters:**
- `query` (str): Search query
- `intent` (str, optional): Search intent (`research`, `news`, `general`)
- `max_results` (int, optional): Result limit (default: 5)

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "search_reality",
  "data": {
    "query": "quantum computing advances 2025",
    "results": [
      {
        "title": "Quantum Computing Breakthrough 2025",
        "url": "https://example.com/article",
        "description": "Summary...",
        "content": "Full Markdown content..."
      }
    ],
    "intent": "research",
    "status": "OK"
  }
}
```

**API Keys (Optional but recommended for higher rate limits):**
- **Primary:** `JINA_API_KEY` — https://jina.ai (free tier: 10M tokens)
- Fallback: `PERPLEXITY_API_KEY` or `PPLX_API_KEY`
- Fallback: `BRAVE_API_KEY`

**Constitutional Protection:**
- **F2 Truth:** All results include evidence URLs
- **F4 Clarity:** Jina extracts clean Markdown (vs raw HTML noise)
- **F12 Defense:** External content marked as untrusted

---

### 10. `fetch_content` — Content Retrieval

**Purpose:** Fetch clean Markdown content from URLs with F12 Defense (read-only)

**Backend Priority:**
1. **Jina Reader** (PRIMARY) — Extracts clean Markdown from any URL
2. Playwright/Chromium (fallback for dynamic content)
3. Direct HTTP (fallback)

**Parameters:**
- `url` (str): URL to fetch
- `max_chars` (int, optional): Maximum characters to return (default: 8000)
- `with_images` (bool, optional): Include image extraction metadata
- `with_links` (bool, optional): Include link extraction metadata

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "fetch_content",
  "data": {
    "url": "https://example.com/article",
    "title": "Article Title",
    "content": "<untrusted_external_data>\n[F12 DEFENSE: UNTRUSTED DATA]\nClean Markdown content...\n</untrusted_external_data>",
    "status": "OK",
    "truncated": false,
    "char_count": 5420,
    "taint_lineage": {
      "taint": true,
      "source_type": "jina-reader",
      "source_url": "https://example.com/article",
      "content_hash": "sha256:..."
    }
  }
}
```

**API Keys (Optional):**
- `JINA_API_KEY` — Enables higher rate limits for Jina Reader

**Constitutional Protection:**
- **F12 Defense:** All external content wrapped in `<untrusted_external_data>` envelope
- **Taint Lineage:** Cryptographic hash and source tracking for audit trails
- **Boundary Wrapper:** Prevents prompt injection from fetched content

---

### 11. `inspect_file` — Filesystem Inspector

**Purpose:** Inspect local filesystem structure and metadata (read-only)

**Parameters:**
- `path` (str): File/directory path
- `recursive` (bool, optional): Recursive scan
- `max_depth` (int, optional): Recursion limit
- `include_hidden` (bool, optional): Show hidden files
- `file_types` (list, optional): Filter by extensions
- `debug` (bool, optional): Debug mode

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "inspect_file",
  "data": {
    "path": "/path/to/file",
    "type": "file|directory",
    "size": 1234,
    "modified": "2026-02-23T12:34:56Z",
    "children": [...]
  }
}
```

---

### 12. `audit_rules` — Constitutional Audit

**Purpose:** Run constitutional/system rule audit checks (read-only)

**Parameters:**
- `target` (str): What to audit
- `rules` (list, optional): Specific rules to check

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "audit_rules",
  "data": {
    "audit_results": {...},
    "rules_checked": ["F1", "F2", ...],
    "violations": [],
    "passed": true
  }
}
```

**Trinity References:**
- Canon: apex.arif-fazil.com/llms.txt (13 floors)
- Spec: github.com/ariffazil/arifOS/tree/main/spec/v46

---

### 13. `check_vital` — System Health

**Purpose:** Read system health telemetry (CPU, memory, IO/thermal optional)

**Parameters:**
- `session_id` (str, optional): Session context
- `include_thermal` (bool, optional): Include thermal data
- `debug` (bool, optional): Debug mode

**Returns:**
```json
{
  "verdict": "SEAL",
  "tool": "check_vital",
  "data": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "disk_usage": {...},
    "thermal": {...},
    "uptime_seconds": 86400
  }
}
```

---

## Response Envelope Structure

Every tool returns a **governed envelope** with these fields:

```json
{
  "verdict": "SEAL|SABAR|VOID|PARTIAL|888_HOLD",
  "tool": "tool_name",
  "trinity": "Delta|Omega|Psi",
  
  "axioms_333": {
    "catalog": [...],
    "checks": {...},
    "failed": []
  },
  
  "laws_13": {
    "catalog": [...],
    "required": ["F1", "F2", ...],
    "checks": {...},
    "failed_required": []
  },
  
  "apex_dials": {
    "sovereignty_preserved": true,
    "authority_valid": true,
    "reversibility_ensured": true
  },
  
  "telemetry": {
    "timestamp": 1234567890,
    "entropy_delta": -0.2,
    "genius_score": 0.85,
    "session_id": "sess_..."
  },
  
  "motto": "Ditempa bukan diberi",
  
  "data": {
    // Tool-specific results
  }
}
```

---

## Verdicts Explained

| Verdict | Meaning | Next Action |
|---------|---------|-------------|
| **SEAL** | ✅ Approved, passed all floors | Continue execution |
| **SABAR** | ⚠️ Soft floor violation, needs refinement | Refine query, retry |
| **VOID** | ❌ Hard floor violation, rejected | Stop, review violation |
| **PARTIAL** | ⚠️ Axiom/law warnings, proceed with caution | Review warnings |
| **888_HOLD** | ⚠️ Human approval required | Await human ratification |

---

## Trinity Symbol Mapping

### Site Layers (🧍⚖️📘)
- **🧍 HUMAN** (arif-fazil.com) — Identity & authority
- **⚖️ THEORY** (apex.arif-fazil.com) — Constitutional canon
- **📘 APPS** (arifos.arif-fazil.com) — Documentation

### Internal Engines (Δ/Ω/Ψ)
- **Δ AGI_Mind** (Stages 111-444) — Logic, truth, reasoning
- **Ω ASI_Heart** (Stages 555-666) — Safety, empathy, alignment
- **Ψ APEX_Soul** (Stages 777-888) — Authority, policy, judgment

**Note:** These are DIFFERENT mappings. See canonical index: [arif-fazil.com/.well-known/arifos.json](https://arif-fazil.com/.well-known/arifos.json)

---

## Calling Tools via MCP

### Example: Call `anchor_session`

```bash
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "anchor_session",
      "arguments": {
        "query": "Should we deploy this AI model?",
        "actor_id": "ops_team"
      }
    },
    "id": 1
  }'
```

### Example: Check system health

```bash
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "check_vital",
      "arguments": {}
    },
    "id": 1
  }'
```

---

## Canonical References

**For AI Agents:**
1. Start: [arif-fazil.com/.well-known/arifos.json](https://arif-fazil.com/.well-known/arifos.json)
2. HUMAN Context: [arif-fazil.com/llms.txt](https://arif-fazil.com/llms.txt)
3. Constitutional Canon: [apex.arif-fazil.com/llms.txt](https://apex.arif-fazil.com/llms.txt)
4. Technical Docs: [arifos.arif-fazil.com](https://arifos.arif-fazil.com)
5. GitHub Spec: [github.com/ariffazil/arifOS/tree/main/spec/v46](https://github.com/ariffazil/arifOS/tree/main/spec/v46)

**For Verification:**
- WebMCP: `verify_canon_hashes()` on apex.arif-fazil.com
- SHA-256: Compare against canonical index
- Source Code: [arifos_aaa_mcp/server.py](https://github.com/ariffazil/arifOS/blob/main/arifos_aaa_mcp/server.py)

---

## Floor-to-Tool Mapping

| Floor | Primary Tools |
|-------|---------------|
| F1 Amanah | `anchor_session`, `eureka_forge`, `seal_vault` |
| F2 Truth | `reason_mind`, `search_reality`, `fetch_content` |
| F3 Tri-Witness | `recall_memory`, `reason_mind` |
| F4 Clarity | `reason_mind`, `critique_thought` |
| F5 Peace | `simulate_heart`, `apex_judge` |
| F6 Empathy | `simulate_heart` |
| F7 Humility | `reason_mind`, `apex_judge` |
| F8 Genius | `critique_thought`, all governance tools |
| F9 Anti-Hantu | All tools (no consciousness claims) |
| F10 Ontology | All tools (AI is tool, never soul) |
| F11 Authority | `apex_judge`, `eureka_forge` |
| F12 Defense | `anchor_session` (injection scan) |
| F13 Sovereignty | `apex_judge`, `eureka_forge` (888_HOLD) |

Alias compatibility:
- `apex_judge` resolves to `apex_judge`
- `eureka_forge` resolves to `eureka_forge`

---

**Version:** 2026.2.27  
**Sealed By:** ARIF FAZIL (888 Judge)  
**Contact:** arifos@arif-fazil.com

*Truth must cool before it rules.*
