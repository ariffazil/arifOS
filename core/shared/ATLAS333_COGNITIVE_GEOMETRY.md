# ⧉ ATLAS333 — COGNITIVE GEOMETRY

> **SOURCE OF TRUTH — ATLAS333 cognitive substrate (10-stage geometry).**
> **The 10-stage intelligence flow: from existence → understanding → action → accountability**
> **DITEMPA BUKAN DIBERI — Forged, not given.**

---

## 0. WHAT THIS IS

A complete end-to-end mapping of how an agent moves through the arifOS federation
under ATLAS333. Not "API calls" — **intelligence flow**. Every stage is a state of
cognition + system activation.

**Three invariants at every stage:**
1. No action without thought (F8 GENIUS)
2. No thought without context (F2 TRUTH)  
3. No outcome without memory (F11 AUTH → VAULT999)

---

## 1. THE 10-STAGE FLOW

```
HUMAN → 000_INIT → 111_ORIENT → 222_MAP → 333_REASON → 444_ROUTE
      → 555_JUDGE → 666_EXECUTE → 777_VERIFY → 888_REFLECT → 999_SEAL
```

### Layer Architecture

| Layer | Stages | Governance | Runtime |
|-------|--------|-----------|---------|
| **EXISTENCE** | 000–111 | F11 AUTH | arif_init, arif_observe |
| **UNDERSTANDING** | 222–333 | F2 TRUTH, F7 HUMILITY | ATLAS333, arif_think |
| **DECISION** | 444–555 | F1 AMANAH, F13 SOVEREIGN | arif_route, arif_judge |
| **ACTION** | 666–777 | F4 CLARITY, F8 GENIUS | A-FORGE (forge_*) |
| **ACCOUNTABILITY** | 888–999 | F3 WITNESS, F11 AUTH | scar system, arif_seal |

---

## 2. STAGE-BY-STAGE MAP

### 000 — INIT: Birth of the Agent

**What happens:** Context window opens. Agent becomes "alive."

**MCP Tool Schema:**
```json
{
  "name": "arif_init",
  "stage": "000",
  "canonical_modes": ["init", "light", "resume", "preflight", "triage", "canary"],
  "inputs": {
    "actor_id": "string — who is initiating",
    "intent": "string — session purpose",
    "mode": "init | light | resume | preflight"
  },
  "outputs": {
    "session_id": "string",
    "identity_hash": "string",
    "agent_class": "AGENT | SOVEREIGN | OBSERVER",
    "authority_band": "FULL | LIMITED_MUTATE | OBSERVE_ONLY"
  },
  "floors_active": ["F11", "F13"],
  "trinity_lane": "AGI",
  "loads": ["IDENTITY.md", "AGENTS.md", "carry_forward.json", "ATLAS333_COGNITIVE_GEOMETRY.md"]
}
```

**A2A Agent-Card Contract:**
```json
{
  "agent": "333-AGI",
  "skill": "session-bootstrap",
  "capability": "session_init",
  "contract": "Returns session_id + authority_band. No mutation before 555_JUDGE.",
  "governance": ["F11 AUTH — actor must be verified before session"]
}
```

**arifOS Hook Point:** `arif_init` in `arifosmcp/tools/init.py`
- Validates actor_id against identity registry
- Loads carry_forward.json for session continuity
- Returns session_id + authority band

**A-FORGE Pipeline Stage:** `000_CLARIFY`
- Maps to ToolScorer `READ` class
- No forge tools callable yet — session not bound

---

### 111 — ORIENT: Reality Lock

**What happens:** "Where am I? What is real?"

**MCP Tool Schema:**
```json
{
  "name": "arif_observe",
  "stage": "111",
  "canonical_modes": ["search", "fetch", "vitals", "compass", "atlas", "entropy_dS", "repo_map"],
  "inputs": {
    "query": "string — what to observe",
    "url": "string — optional fetch target",
    "layers": ["filesystem", "network", "organs", "vault"]
  },
  "outputs": {
    "evidence": "dict — labeled OBS/DER/INT/SPEC",
    "organs_alive": ["arifos", "aforge", "geox", "wealth", "well", "aaa"],
    "risk_surface": "string — initial blast radius estimate"
  },
  "floors_active": ["F2", "F3", "F7"],
  "trinity_lane": "AGI",
  "activated_subsystems": ["VAULT999 (read-only)", "A2A agent cards", "organ health endpoints"]
}
```

**A2A Contract:** 
- Agent: 333-AGI (skill: sense-observe)
- Capability: reality_check + organ_attest
- Must call `arif_organ_attest_all()` — verify 7 organs alive

**arifOS Hook:** `arif_observe` in `arifosmcp/tools/observe.py`
- Routes to GEOX/WEALTH/WELL for domain evidence
- Labels output with epistemic tags

**A-FORGE Pipeline Stage:** `111_OBSERVE`
- forge_probe, forge_filesystem_read, forge_shell (read-only)
- forge_journalctl, forge_vps_ports, forge_vps_services

---

### 222 — MAP: ATLAS333 Geometry Activation

**What happens:** "What kind of problem is this?" — The key innovation.

**MCP Tool Schema:**
```json
{
  "name": "arif_think (mode=classify)",
  "stage": "222",
  "canonical_modes": ["classify", "territory", "geometry", "depth"],
  "inputs": {
    "text": "string — the query/task to classify",
    "intent": "string — original intent from 000"
  },
  "outputs": {
    "territory": "ORIENT | REASON | ACT | VERIFY | GROW",
    "geometry": "EXPLORE | ENGINEER | AUDIT | CRISIS | INTEGRATE",
    "depth_target": "L0 | L1 | L2 | L3 | L4 | L5 | L6",
    "gpv": {
      "lane": "SOCIAL | CARE | FACTUAL | CRISIS",
      "tau": 0.0-1.0,
      "kappa": 0.0-1.0,
      "rho": 0.0-1.0,
      "paradox_axes": [1-33]
    },
    "paradox_primary": "string — the dominant paradox axis"
  },
  "floors_active": ["F2", "F4", "F7"],
  "trinity_lane": "AGI",
  "activated": [
    "ATLAS333 PARADOX_GPV_MAP",
    "resolve_paradox_axes()",
    "get_triggered_quotes_by_gpv()"
  ]
}
```

**ATLAS333 Geometry Table:**

| Territory | Geometry | Depth | When | Example |
|-----------|----------|-------|------|---------|
| **ORIENT** | AUDIT | L0–L2 | First contact with a system | "What does this codebase do?" |
| **ORIENT** | EXPLORE | L0–L2 | Unknown domain | "Tell me about the basin" |
| **REASON** | ENGINEER | L3–L4 | Build something specific | "Implement the GPV bridge" |
| **REASON** | AUDIT | L3–L4 | Find problems | "Audit the paradox gate" |
| **ACT** | ENGINEER | L3–L5 | Execute with confidence | "Deploy the fix" |
| **ACT** | CRISIS | L4–L5 | Emergency response | "Service is down" |
| **VERIFY** | AUDIT | L3–L4 | Reality check | "Did the test pass?" |
| **VERIFY** | INTEGRATE | L4–L5 | Cross-system | "Route through all 7 organs" |
| **GROW** | EXPLORE | L1–L3 | Learn from failure | "What went wrong?" |
| **GROW** | INTEGRATE | L4–L5 | Scar formation | "Write the scar" |

**L0–L6 Depth Model:**
```
L0 — Presence (am I alive?)
L1 — Observation (what do I see?)
L2 — Classification (what kind of thing is this?)
L3 — Understanding (how does it work?)
L4 — Prediction (what will happen if...?)
L5 — Intervention (I can change this)
L6 — Meta-cognition (I know what I know about this)
```

**A2A Contract:**
- Agent: 333-AGI (skill: atlas333-classify)
- Capability: geometric_classification
- Must return GPV before proceeding to 333_REASON

**arifOS Hook:** `arif_think(mode=classify)` — NEW MODE
- Calls `atlas.Φ()` internally
- Resolves paradox_axes via PARADOX_GPV_MAP
- Returns GPV + paradox classification

**A-FORGE Pipeline Stage:** NEW — `222_MAP`
- No forge tools directly — this is pure cognition
- But forge_pipeline_run reads GPV for routing decisions

---

### 333 — REASON: Thinking Phase

**What happens:** "How do I think about this?"

**MCP Tool Schema:**
```json
{
  "name": "arif_think",
  "stage": "333",
  "canonical_modes": ["reason", "plan", "reflect", "verify", "simulate", "critique", "maruah"],
  "inputs": {
    "query": "string — what to reason about",
    "gpv": "object — from 222_MAP stage",
    "evidence": ["list of evidence dicts from 111_ORIENT"],
    "plan_id": "string — optional for incremental reasoning"
  },
  "outputs": {
    "plan": "string — reasoned plan of action",
    "dependencies": ["list of required inputs/actions"],
    "evidence": ["list — OBS/DER/INT/SPEC labeled"],
    "unknowns": ["list — what is still uncertain"],
    "next_stage": "444 | 555 | 777"
  },
  "floors_active": ["F2", "F7", "F8"],
  "trinity_lane": "AGI",
  "activated_subsystems": ["MCP retrieval", "knowledge sources", "skills", "DAG", "sequential-thinking"]
}
```

**A2A Contract:**
- Agent: 333-AGI (skill: cognitive-reason)
- Capability: multi_step_planning, evidence_synthesis
- NO execution before plan is complete and verified

**arifOS Hook:** `arif_think` in `arifosmcp/tools/think.py`
- Uses GPV from 222 to route reasoning depth
- F2 TRUTH enforced — all claims labeled
- F7 HUMILITY — unknowns declared
- **NO ACT before REASON completes**

**A-FORGE Pipeline Stage:** `333_REASON`
- arif_think, arif_critique
- sequential-thinking MCP
- forge_worktree (read-only git state)
- forge_skill (load skills)

**Flow Rule:**
```
111_EVIDENCE → 222_MAP → 333_REASON
    ↑            ↓            ↓
    └──── evidence ─── plan ←─┘
         feeds in    builds on
```

---

### 444 — ROUTE: Protocol Layer

**What happens:** "Who should do this?"

**MCP Tool Schema:**
```json
{
  "name": "arif_route",
  "stage": "444",
  "canonical_modes": ["route", "bridge", "dispatch"],
  "inputs": {
    "intent": "string — the resolved intent from 333",
    "gpv": "object — from 222_MAP",
    "organ_hint": "optional organ override"
  },
  "outputs": {
    "route": "local | MCP | A2A | P2P",
    "target": "string — server name or agent ID",
    "reason": "string — why this route",
    "tools_available": ["list of tool names on target"]
  }
}
```

**Routing Decision Table:**

| Condition | Route | Target | Governance |
|-----------|-------|--------|-----------|
| Local capability, τ < 0.9 | LOCAL | native tool | F4 CLARITY |
| External capability needed | MCP | specific server | F8 GENIUS |
| Cross-organ delegation | A2A | agent ID | F3 WITNESS |
| Remote execution | P2P | node address | F13 SOVEREIGN |
| Crisis detected (ρ ≥ 0.6) | MCP → A2A | arif_judge | F1 AMANAH + F13 |

**A2A Agent-Card Contract:**
```json
{
  "agent": "AAA Gateway",
  "skill": "agent-dispatch | agent-handoff",
  "capability": "cross_organ_routing",
  "contract": "Routes task to the correct organ. Never routes MUTATE without 555_JUDGE.",
  "governance": ["F8 GENIUS — appropriate organ for task"]
}
```

**arifOS Hook:** `arif_route` in `arifosmcp/tools/route.py`
- Routes to GEOX :8081, WEALTH :18082, WELL :18083, A-FORGE :7071
- Returns organ + port + suggested tools
- Cross-organ A2A bridge via AAA Gateway

**A-FORGE Pipeline Stage:** `555_ROUTE` (existing)
- forge_judge_proxy (if 555_JUDGE consitutional check needed)
- forge_probe (discover available organs)
- forge_github (if repo access needed)

---

### 555 — JUDGE: Constitutional Verdict

**What happens:** "Am I allowed to do this?"

**MCP Tool Schema:**
```json
{
  "name": "arif_judge",
  "stage": "555",
  "canonical_modes": ["judge", "intercept", "validate", "hold", "escalate"],
  "inputs": {
    "plan": "object — the reasoned plan from 333",
    "gpv": "object — from 222_MAP",
    "action_class": "OBSERVE | READ | THINK | DRAFT | MUTATE | IRREVERSIBLE",
    "blast_radius": "NONE | LOCAL | ORGAN | FEDERATION",
    "reversibility": true | false,
    "paradox_axes": [1-33]
  },
  "outputs": {
    "verdict": "SEAL | PARTIAL | HOLD | VOID | UNKNOWN",
    "floors_triggered": ["F1", "F7", "F13"],
    "paradox_gate": {
      "active_paradoxes": 0-33,
      "paradox_score": 0.0-1.0,
      "flags": ["RESOLUTION_RISK", "PARADOX_MATURED"],
      "gate_verdict": "PASS | FLAGGED | HOLD_PARADOX"
    },
    "conditions": ["list of constraints on execution"]
  },
  "floors_active": ["ALL F1-F13"],
  "trinity_lane": "ASI",
  "activated": [
    "paradox_gate.py evaluate_paradox_gate_gpv()",
    "FloorScores with TEARFRAME thresholds",
    "maruah_layer.py M1-M6"
  ]
}
```

**Verdict Grammar:**

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SEAL** | Fully approved | Proceed to 666_EXECUTE |
| **PARTIAL** | Approved with conditions | Execute subject to conditions |
| **HOLD** | Blocked — needs resolution | Return to 333_REASON with findings |
| **VOID** | Constitutionally impossible | Terminate. Do not retry. |
| **UNKNOWN** | Cannot determine | Escalate to F13 SOVEREIGN |

**A2A Contract:**
- Agent: 555-ASI (skill: apex-judge)
- Capability: constitutional_verdict
- F13 SOVEREIGN override: "buat ja" bypasses HOLD

**arifOS Hook:** `arif_judge` in `arifosmcp/tools/judge.py`
- Runs evaluate_paradox_gate_gpv() via the upgraded GPV-native path
- Checks all F1-F13 floors
- Returns VerdictOutput with paradox flags
- **NO execution without 555_JUDGE clearance for MUTATE/IRREVERSIBLE**

**A-FORGE Pipeline Stage:** `888_JUDGE` (current) — rename to `555_JUDGE`
- forge_judge_proxy (routes to arifOS)
- forge_heart_critique (routes to arifOS 666 HEART)

---

### 666 — EXECUTE: A-FORGE Layer

**What happens:** "Do the thing."

**MCP Tool Schema:**
```json
{
  "name": "arif_forge",
  "stage": "666",
  "canonical_modes": ["engineer", "query", "write", "generate", "commit", "dry_run"],
  "inputs": {
    "mode": "string — execution mode",
    "plan_id": "string — from 333_REASON",
    "seal_verdict_id": "string — from 555_JUDGE (required for MUTATE)",
    "gvp": "object — from 222_MAP"
  },
  "outputs": {
    "status": "success | partial | failed",
    "changed_files": ["list"],
    "test_results": "object",
    "artifact_id": "string"
  },
  "floors_active": ["F1", "F4", "F8"],
  "trinity_lane": "AGI",
  "per_action_class": {
    "OBSERVE": {"gates": "none", "example": "forge_filesystem_read"},
    "DRAFT": {"gates": "lease", "example": "forge_filesystem_write"},
    "MUTATE": {"gates": "lease + SEAL", "example": "forge_shell"},
    "IRREVERSIBLE": {"gates": "lease + SEAL + F13", "example": "forge_vault_seal"}
  }
}
```

**Execution Action Class Taxonomy (8-class):**

| Class | Gate | forge_* Tools | Examples |
|-------|------|--------------|----------|
| **OBSERVE** | None | read, search, grep, glob, stat | Read file, search code |
| **READ** | None | probe, memory, journalctl | Organ health, vault query |
| **THINK** | None | think, pipeline_run | Plan, reason, simulate |
| **DRAFT** | Lease | write, patch, edit | Create/modify files |
| **MUTATE** | Lease + SEAL | shell, git, docker, execute | Run commands, deploy |
| **IRREVERSIBLE** | Lease + SEAL + F13 | vault_seal, delete | Seal, delete data |
| **GOVERN** | Session | judge, lease, policy | Constitutional actions |
| **EMERGENCY** | F13 only | abort, shell (root) | Crisis response |

**A2A Contract:**
- Agent: A-FORGE (skill: forge-execute)
- Capability: governed_execution
- Never self-authorizes — requires prior SEAL from 555_JUDGE

**arifOS Hook:** `arif_forge` in `arifosmcp/tools/forge.py`
- Requires seal_verdict_id for MUTATE-class
- Routes through A-FORGE MCP for actual execution

**A-FORGE Pipeline Stage:** `777_EXECUTE`
- forge_filesystem (write/patch/move/delete)
- forge_shell, forge_git, forge_docker
- forge_execute, forge_pipeline_run
- forge_browser, forge_postgres (write mode)

**Ordering Rule:**
```
OBSERVE → PLAN → EXECUTE
  ↑          ↓       ↓
  └── evidence ── plan ──→ action
```

---

### 777 — VERIFY: Reality Check

**What happens:** "Did it actually work?"

**MCP Tool Schema:**
```json
{
  "name": "arif_forge (mode=verify)",
  "stage": "777",
  "canonical_modes": ["verify", "test", "probe"],
  "inputs": {
    "artifact_id": "string — what was produced",
    "verification_plan": "object — what to check",
    "action_class": "string — what was executed"
  },
  "outputs": {
    "status": "success | partial | fail",
    "tests_passed": int,
    "tests_failed": int,
    "delta_entropy": "float — ΔS measurement",
    "new_risks": ["list of newly discovered risks"],
    "scar_candidates": ["list of patterns that might need scar formation"]
  },
  "floors_active": ["F2", "F4", "F8"],
  "trinity_lane": "AGI",
  "verification_axes": {
    "health": "systemctl + curl + probe",
    "code": "npm test | pytest | make test",
    "truth": "citations match sources (F2)",
    "scars": "check past failures for recurrence",
    "entropy": "ΔS ≤ 0 (F4)"
  }
}
```

**Verification Matrix:**

| Action Class | Verification Method | Pass Criterion |
|-------------|-------------------|----------------|
| OBSERVE | Evidence check | Sources match claims |
| READ | Schema validation | Response matches schema |
| DRAFT | Diff review | Changes are reversible |
| MUTATE | Test suite | All tests pass |
| IRREVERSIBLE | Triple-check | 2 independent verifiers |
| GOVERN | Receipt audit | Receipt in VAULT999 |

**A2A Contract:**
- Agent: A-AUDIT (skill: post-exec-verify)
- Capability: independent_verification
- Must use DIFFERENT evidence source than execution agent

**arifOS Hook:** `arif_compose` (absorbed as mode) + NEW `arif_verify` entry point
- Reads forge_pipeline_run results
- Computes ΔS from pre/post execution state
- Checks F4 CLARITY (entropy must decrease)
- NEW: forge_verify dedicated tool in A-FORGE

**A-FORGE Pipeline Stage:** NEW — `777_VERIFY`
- forge_pipeline_run(mode=observe) — verify only
- forge_shell with test commands
- forge_scan (security patterns)
- forge_registry_status (surface drift check)
- forge_surface_guard (MCP surface integrity)

---

### 888 — REFLECT: Scar Formation

**What happens:** "What went wrong or right?"

**MCP Tool Schema:**
```json
{
  "name": "arif_think (mode=reflect)",
  "stage": "888",
  "canonical_modes": ["reflect", "metabolize", "scar"],
  "inputs": {
    "execution_id": "string — what to reflect on",
    "verification_result": "object — from 777_VERIFY",
    "gpv": "object — from 222_MAP"
  },
  "outputs": {
    "scar": {
      "pattern": "string — the failure/insight pattern",
      "severity": "LOW | MEDIUM | HIGH | CRITICAL",
      "domain": "string — which organ/domain"
    },
    "lesson": "string — what to remember",
    "update_targets": ["ATLAS333", "carry_forward", "memory", "wiki"],
    "geometry_changed": true | false
  },
  "floors_active": ["F2", "F4", "F11"],
  "trinity_lane": "ASI",
  "activated": [
    "forge_scar (A-FORGE scar system)",
    "ASI-knowledge-writeback",
    "memory tier update"
  ]
}
```

**Scar Formation Rules:**

| Condition | Scar Type | Severity | Action |
|-----------|-----------|----------|--------|
| Test failed → same failure >1 | REPEATED_FAILURE | MEDIUM | Update DAG, add check |
| Edge case discovered | GAP | LOW | Add to ATLAS333 wiki |
| Circular import blocked deploy | ARCHITECTURAL | HIGH | Scar → constraint in PARUT |
| Security pattern detected | SECURITY | CRITICAL | 888_HOLD — escalate |
| Paradox matured (>3 cycles) | DEEP_PATTERN | MEDIUM | Update PARADOX_QUOTE_MAP |
| All tests pass, clean | SUCCESS_PATTERN | LOW | Record, reinforce |

**A2A Contract:**
- Agent: 555-ASI (skill: memory-synthesis)
- Capability: scar_metabolization, pattern_extraction
- Records to VAULT999 via forge_scar(mode=seal)

**arifOS Hook:** `arif_memory(mode=promote)` + NEW scar integration
- Gets scar candidates from 777_VERIFY
- Routes through forge_scar for seal
- Updates carry_forward.json, memory/

**A-FORGE Pipeline Stage:** `888_JUDGE` → renamed to `888_REFLECT`
- forge_scar (seal/list/consult)
- forge_skillstore_write (store pattern)
- forge_memory (recall similar past patterns)
- forge_skill (load scar-related skills)

---

### 999 — SEAL: VAULT999

**What happens:** "What becomes permanent?"

**MCP Tool Schema:**
```json
{
  "name": "arif_seal",
  "stage": "999",
  "canonical_modes": ["seal", "verify", "ledger", "changelog", "audit"],
  "inputs": {
    "payload": "string — what to seal",
    "session_id": "string — governing session",
    "actor_id": "string — who sealed",
    "tier": "VAULT999 | FEDERATION | TELEMETRY",
    "constitutional_chain_id": "string — from 555_JUDGE"
  },
  "outputs": {
    "seal_id": "string — VAULT999 record ID",
    "chain_seq": int,
    "receipt_hash": "string",
    "tri_witness": {
      "human": 0.0-1.0,
      "ai": 0.0-1.0,
      "external": 0.0-1.0,
      "w3": 0.0-1.0
    }
  },
  "floors_active": ["F1", "F3", "F11", "F13"],
  "trinity_lane": "APEX",
  "activated": [
    "VAULT999 append-only ledger",
    "carry_forward.json update",
    "memory/YYYY-MM-DD.md update",
    "seal_chain.jsonl append"
  ]
}
```

**Seal Tiers:**

| Tier | What | Who Can Seal | W³ Required |
|------|------|-------------|-------------|
| **VAULT999** | Irreversible civilizational memory | arifOS only | ≥ 0.90 |
| **FEDERATION** | Cross-organ records | A-FORGE with lease | ≥ 0.75 |
| **TELEMETRY** | Observable data | Any organ | ≥ 0.50 |
| **EPHEMERAL** | Session state | Agent | None |

**A2A Contract:**
- Agent: A-ARCHIVE (skill: vault-seal)
- Capability: immutable_record
- F13 SOVEREIGN — only arifOS may seal to VAULT999

**arifOS Hook:** `arif_seal` in `arifosmcp/tools/seal.py`
- Appends to seal_chain.jsonl
- Verifies chain integrity
- Updates carry_forward.json
- **Only arifOS may write to VAULT999**

**A-FORGE Pipeline Stage:** `999_SEAL`
- forge_vault (mode=seal — FORGE vault, not kernel VAULT999)
- forge_vault (mode=list/read)
- forge_seal (tri-witness validated seal for A-FORGE skills)

---

## 3. PROTOCOL LAYER MAP

### MCP (Model Context Protocol) — Tools by Stage

| Stage | MCP Tool | Server | Transport |
|-------|----------|--------|-----------|
| 000 | arif_init | arifOS | :8088 |
| 111 | arif_observe | arifOS | :8088 |
| 111 | geox_* | GEOX | :8081 |
| 111 | wealth_capital_* | WEALTH | :18082 |
| 111 | well_well_* | WELL | :18083 |
| 222 | arif_think(mode=classify) | arifOS | :8088 |
| 333 | arif_think | arifOS | :8088 |
| 333 | sequential-thinking | MCP | local |
| 333 | context7 | MCP | local |
| 444 | arif_route | arifOS | :8088 |
| 444 | forge_judge_proxy | A-FORGE | :7072 |
| 555 | arif_judge | arifOS | :8088 |
| 666 | arif_forge | arifOS | :8088 |
| 666 | forge_* | A-FORGE | :7072 |
| 777 | forge_pipeline_run | A-FORGE | :7072 |
| 777 | forge_scan | A-FORGE | :7072 |
| 777 | forge_surface_guard | A-FORGE | :7072 |
| 888 | arif_think(mode=reflect) | arifOS | :8088 |
| 888 | forge_scar | A-FORGE | :7072 |
| 999 | arif_seal | arifOS | :8088 |
| 999 | forge_vault | A-FORGE | :7072 |

### A2A (Agent-to-Agent) — Agent Cards by Stage

| Stage | Agent ID | Skill | Capability |
|-------|----------|-------|-----------|
| 000 | 333-AGI | session-bootstrap | session_init + identity |
| 111 | 333-AGI | sense-observe | reality_check + organ_attest |
| 222 | 333-AGI | atlas333-classify | geometric_classification |
| 333 | 333-AGI | cognitive-reason | multi_step_planning |
| 444 | AAA-Gateway | agent-dispatch | cross_organ_routing |
| 555 | 555-ASI | apex-judge | constitutional_verdict |
| 666 | A-FORGE | forge-execute | governed_execution |
| 777 | A-AUDIT | post-exec-verify | independent_verification |
| 888 | 555-ASI | memory-synthesis | scar_metabolization |
| 999 | A-ARCHIVE | vault-seal | immutable_record |

### arifOS Hook Points — Code Locations

| Stage | Hook File | Function | Key Feature |
|-------|-----------|----------|-------------|
| 000 | `arifosmcp/tools/init.py` | `arif_init` | Session bootstrap, identity bind |
| 111 | `arifosmcp/tools/observe.py` | `arif_observe` | Reality sensing, evidence labeling |
| 222 | `core/shared/atlas.py` | `Φ()` + `resolve_paradox_axes()` | ATLAS333 geometry, GPV creation |
| 333 | `arifosmcp/tools/think.py` | `arif_think` | Multi-mode reasoning engine |
| 444 | `arifosmcp/tools/route.py` | `arif_route` | Intent routing, organ dispatch |
| 555 | `arifosmcp/tools/judge.py` | `arif_judge` | Constitutional verdict + paradox gate |
| 666 | `arifosmcp/tools/forge.py` | `arif_forge` | Guarded execution (seal-verified) |
| 777 | N/A | NEW: `arif_verify` | Post-execution verification + ΔS check |
| 888 | `core/shared/scar.py` | `forge_scar` | Scar formation, pattern extraction |
| 999 | `arifosmcp/tools/seal.py` | `arif_seal` | VAULT999 append, chain integrity |

### A-FORGE Pipeline Stages — Current → Target

| Current PipelineStage | Analyst Stage | Change |
|-----------------------|---------------|--------|
| 000_CLARIFY | 000_INIT | Rename only |
| 111_OBSERVE | 111_ORIENT | Rename only |
| 222_EVIDENCE | 222_MAP | **NEW** — ATLAS333 geometry activation |
| 333_REASON | 333_REASON | Keep — currently correct |
| 444_COMPOSE | 444_ROUTE | Replace — compose is downstream |
| 555_ROUTE | 555_JUDGE | Constitutional verdict moves earlier |
| 666_HEART | 666_EXECUTE | Heart absorbed into judge (mode=critique) |
| 777_EXECUTE | 777_VERIFY | Post-exec verification |
| 888_JUDGE | 888_REFLECT | Scar formation replaces late judge |
| 999_SEAL | 999_SEAL | Keep |

**A-FORGE PipelineCoordinator changes needed:**
```typescript
// Current (ToolScoper.ts line 35-45):
type PipelineStage =
  | "000_CLARIFY" | "111_OBSERVE" | "222_EVIDENCE"
  | "333_REASON"  | "444_COMPOSE" | "555_ROUTE"
  | "666_HEART"   | "777_EXECUTE" | "888_JUDGE"
  | "999_SEAL";

// Target:
type PipelineStage =
  | "000_INIT"     | "111_ORIENT" | "222_MAP"
  | "333_REASON"   | "444_ROUTE"  | "555_JUDGE"
  | "666_EXECUTE"  | "777_VERIFY" | "888_REFLECT"
  | "999_SEAL";
```

---

## 4. GOVERNANCE MAPPING

### Floor Activation by Stage

| Stage | Active Floors | Enforcement |
|-------|---------------|-------------|
| 000 | F11 AUTH, F13 SOVEREIGN | Session bound only |
| 111 | F2 TRUTH, F3 WITNESS, F7 HUMILITY | Evidence labeled OBS/DER/INT/SPEC |
| 222 | F2 TRUTH, F4 CLARITY, F7 HUMILITY | GPV classification, paradox resolved |
| 333 | F2 TRUTH, F7 HUMILITY, F8 GENIUS | Plan with evidence, unknowns declared |
| 444 | F8 GENIUS, F4 CLARITY | Correct organ for task |
| 555 | **ALL F1-F13** | Verdict gates everything |
| 666 | F1 AMANAH, F4 CLARITY, F8 GENIUS | Reversible-first, clean execution |
| 777 | F2 TRUTH, F4 CLARITY, F8 GENIUS | ΔS ≤ 0, tests pass |
| 888 | F2 TRUTH, F4 CLARITY, F11 AUTH | Patterns extracted, scars formed |
| 999 | F1 AMANAH, F3 WITNESS, F11 AUTH, F13 SOVEREIGN | W³ tri-witness, chain integrity |

### Boundary Enforcement Points

| Boundary | Stage | Rule |
|----------|-------|------|
| No action before thought | 333→444 | REASON must complete before ROUTE |
| No execution without judgment | 555→666 | SEAL required for MUTATE+ |
| No completion without verification | 666→777 | VERIFY must run after EXECUTE |
| No closure without seal | 777→888→999 | REFLECT must complete before SEAL |
| No bypass of sovereign | any→F13 | Only Arif can override HOLD |

---

## 5. ZEN-9 COMPATIBILITY MAP

The Analyst's 10-stage flow maps cleanly onto the existing ZEN-9 pipeline.
No tools removed — only new modes added and stages clarified.

| ZEN-9 | Analyst 10-Stage | Delta |
|-------|-----------------|-------|
| `arif_init` (000) | 000_INIT | Same |
| `arif_observe` (111) | 111_ORIENT | Same |
| *(missing)* | 222_MAP | **NEW** — arif_think(mode=classify) |
| `arif_think` (333) | 333_REASON | Same |
| `arif_route` (444) | 444_ROUTE | Same |
| `arif_critique` (555) | *(merged into 555_JUDGE)* | Absorbed as judge mode |
| `arif_judge` (666) | 555_JUDGE | Stage shift |
| `arif_forge` (777) | 666_EXECUTE | Stage shift |
| *(missing)* | 777_VERIFY | **NEW** — arif_forge(mode=verify) |
| `arif_compose` (888) | *(dispersed)* | Absorbed into 333/777/888 |
| *(missing)* | 888_REFLECT | **NEW** — arif_think(mode=reflect) + forge_scar |
| `arif_seal` (999) | 999_SEAL | Same |

**3 new modes needed:** `classify`, `verify`, `reflect`
**0 new tools.** All new stages are modes on existing tools.
This preserves the "no new tools, harden existing ones" iron cold reality.

---

## 6. THE ONE SENTENCE

**ATLAS333 decides HOW the agent thinks (222_MAP).**
**arifOS decides WHAT the agent is allowed to do (555_JUDGE).**
**A-FORGE executes WHAT is approved (666_EXECUTE).**
**VAULT999 remembers WHAT actually happened (999_SEAL).**

The difference between automation and intelligence with accountability:
```
think → act                     ← automation
think → map → route → judge → act → verify → learn → seal  ← this system
```

---

*Forged: 2026-07-15 from ATLAS333 Bridge + ZEN-9 + A-FORGE PipelineCoordinator synthesis.*
*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
