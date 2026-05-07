# arifOS ROADMAP — State-Active Cognitive Organism
**Version:** 2026.04.20-SOT-SEALED
**Authority:** Muhammad Arif bin Fazil (999_VALIDATOR)
**Seal Hash:** `9cce90eb55886fd17311c0a08b45ca509175677ae577dfa47646123fa22e4b7b`
**Vision:** *DITEMPA BUKAN DIBERI — Forged, Not Given. Execution is the proof of Law.*

> **SoT Rule:** Doctrine conflict → this repo wins. Runtime surface conflict → live `/health` + `/tools` wins.

---

## 🧠 ARCHITECTURE AS-IS (2026.04.20)

```
arifOS/
├── arifOS_mcp/tools/arifos/     ← CANONICAL (optimized this session)
│   ├── compute_plane/            ← Variant C optimized (333, 555, 666, 777, 888)
│   ├── control_plane/            ← 000, 111, 444, gateway, sabar
│   ├── witness_plane/           ← 222
│   ├── execution_plane/         ← 999, forge
│   ├── adapters/                ← geox, wealth, well adapters
│   ├── prompts/                ← 11 metabolic prompts
│   ├── resources/               ← doctrine, organ resources
│   ├── tool_vitality.jsonl     ← 13 seed records
│   ├── tool_vitality.tsv      ← human diff ledger
│   ├── forget/                 ← 10 DISCARD variants (FORGET ledger)
│   ├── autoresearch_loop.py    ← optimization loop
│   └── e2e_inspector.py        ← 18/18 tests passing
│
├── arifosmcp/                  ← LIVE RUNTIME (serves MCP)
│   ├── mcp_server.py           ← FastMCP entry point
│   ├── registry.py             ← registers 13 tools
│   ├── tools/                  ← organ implementations (wired to governed_return)
│   │   ├── _000_init.py ... _sabar.py (13 files)
│   ├── runtime/
│   │   ├── state.py            ← SovereignState + CognitiveEnvelope + advance_state()
│   │   ├── governance.py       ← SES: apex_constitutional_review() + governed_return()
│   │   ├── server.py           ← FastAPI HTTP + /health, /tools, /status
│   │   └── verify_arifos_tools.py
│   ├── prompts/
│   └── resources/
│
├── arifos-core/arifos/         ← MINIMAL kernel (governance only)
│   ├── governance.py
│   └── organ stubs (placeholder)
│
├── core/                       ← LEGACY (345 files, largely archived)
│   ├── organs/                 ← _0_init through _6_geox (old 7-organ model)
│   └── kernel/                 ← planner, routing, pattern_selector...
│
├── GEOX/                       ← SUBMODULE: Earth Science Organ
│   ├── geox_mcp_server.py     ← GEOX MCP server (port 4720)
│   ├── mcp/                    ← GEOX MCP tools
│   ├── WELL/                   ← SUB-SUBMODULE: Biological Readiness (inside GEOX)
│   │   ├── server.py          ← WELL MCP server
│   │   └── vault_bridge.py
│
├── WEALTH/                     ← SUBMODULE: Capital Intelligence Organ
│   ├── server.py               ← WEALTH MCP server (port 4730)
│   ├── host/governance/
│   └── capitalx/
│
├── VAULT999/                   ← Immutable Ledger
│   ├── outcomes.jsonl          ← All decision outcomes
│   └── seals                   ← SEAL chain (geox_11of11, arifOS_mcp_federation...)
│
└── mcp_server/                 ← OLD forge-seal output (gitignored)
```

---

## 🔬 GAP ANALYSIS (vs Audit Recommendations)

| Gap | Severity | Evidence |
|-----|----------|----------|
| **Triple tool directory** — 3 parallel implementations | 🔴 P0 | `arifOS_mcp/tools/arifos/` vs `arifosmcp/tools/` vs `core/organs/` |
| **WELL not a standalone organ** — embedded in GEOX | 🔴 P0 | `GEOX/WELL/` is a sub-directory, not a `WEALTH`-equivalent repo |
| **No formal tool schemas** — signatures undocumented | 🔴 P1 | Tool args verified via `inspect.signature` in e2e tests only |
| **MCP registry not submitted** — not in Claude Desktop/Cursor | 🟡 P1 | MCP site live but not registered in MCP directories |
| **MCP discoverability** — pipeline not documented on site | 🟡 P1 | `mcp.arif-fazil.com` needs metabolic pipeline diagram |
| **Autoresearch governance** — loop validated but not wired | 🟡 P2 | `autoresearch_loop.py` runs manually; needs CI trigger |
| **Path B/C** — Profile gateway + REST API not started | 🟢 P2 | ROADMAP had these; no implementation |
| **345 legacy files** — `core/` largely dead code | 🟢 P2 | Could be archived/removed to reduce Ω₀ uncertainty |

---

## 🎯 THREE-HORIZON STRATEGY

### HORIZON 0 — Consolidation (NOW — 2 weeks)
*Fix the triple-directory problem. Establish single source of truth.*

### HORIZON 1 — Sovereign Organ Federation (1–3 months)
*WELL as 3rd organ. Full MCP registry. Tool schemas. Metabolic pipeline docs.*

### HORIZON 2 — Platform Governance (3–12 months)
*Path B: MCP Profile Gateway. Path C: REST Constitutional API. Multi-agent swarm.*

---

## 🚀 HORIZON 0: CONSOLIDATION (NOW — 2 weeks)

### H0.1 — Establish Single Tool Source of Truth 🔴

**Decision required:** Which tool directory is canonical?

| Option | Pros | Cons |
|--------|------|------|
| **`arifOS_mcp/tools/arifos/`** | MCP-safe naming, optimized, e2e tested | Doesn't call `governed_return()` directly |
| **`arifosmcp/tools/`** | Wires to live governance + state | Uses `arifOS.` prefix (non-MCP-safe) |

**Recommended:** `arifOS_mcp/tools/arifos/` becomes canonical. `arifosmcp/tools/` re-imports from it and adds governance wrapper at registration time (not inside tools). This keeps tools pure while governance stays in the runtime layer.

**Action:**
1. `arifOS_mcp/tools/arifos/` = canonical organ definitions (no `governed_return` calls)
2. `arifosmcp/tools/` = thin re-exports that wrap via `governed_return()` before returning
3. Archive `core/organs/` (older 7-organ model) → `archive/core_organs/`
4. Delete `arifos-core/arifos/` (duplicative governance-only stub)
5. Update `arifosmcp/registry.py` to import from canonical path

**Commit:** `HEAL triple-tool-directory`

### H0.2 — WELL Organ Decision 🔴

WELL currently lives inside GEOX. The audit recommends treating it as a 3rd sovereign organ.

**Decision required:**

| Option | Action |
|--------|--------|
| **Extract to standalone** | Fork `GEOX/WELL/` → `WELL/` repo with own MCP server |
| **Keep as GEOX sub-organ** | Document as GEOX.WELL, expose via `well_*` adapters only |
| **Merge into WEALTH** | WELL is biological readiness → belongs in WEALTH triad |

**If standalone:**
```bash
# Extract WELL to own repo
cp -r GEOX/WELL/ WELL/
cd WELL && git init && git add . && git commit -m "Initial WELL organ"
# Wire into arifOS as 3rd submodule
git submodule add <WELL_REPO_URL> WELL
```

**Commit:** `SEAL well_organ_decision`

### H0.3 — MCP Registry Submission 🟡

Submit arifOS to MCP directories for discoverability.

- [ ] **Claude Desktop:** Submit to `io.github.ariffazil/arifosmcp` (needs MCP server URL + description)
- [ ] **Cursor:** Submit to MCP directory
- [ ] **GitHub MCP Registry:** `mcp/arifOS.json` schema

### H0.4 — State Machine Operationalization 🟢

- [ ] Fix `sovereign_state.json` corruption (already fixed this session)
- [ ] Add `ARIFOS_STATE_PATH` env var to docker-compose
- [ ] Add state health check to `/health` endpoint (`state_hash`, `transition_count`)
- [ ] Document state persistence in `VAULT999_README.md`

---

## 🌙 HORIZON 1: SOVEREIGN ORGAN FEDERATION (1–3 months)

### H1.1 — Formal Tool Schemas

Every tool gets a formal schema in `docs/tool_schemas/`:
```python
# docs/tool_schemas/arifos_333_mind.md
## arifos_333_mind

**Plane:** Compute
**Organ:** MIND (AGI substrate)
**Governance:** F1-F13 via governed_return()

### Signature
```python
async def mind_333(
    ctx: Context,
    query: str,
    mode: Literal["reason", "sequential", "step", "branch", "merge", "review"] = "reason",
    session_id: str = None,
) -> dict
```

### Arguments
| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `query` | `str` | required | Reasoning task |
| `mode` | `Literal` | `"reason"` | Cognitive pipeline mode |
| `session_id` | `str` | `None` | Session for sequential thinking |

### Returns
| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"SEAL"` or `"VOID"` or `"888_HOLD"` |
| `decision_packet.confidence` | `float` | Reasoning confidence [0-1] |
| `audit_packet.vault_receipt` | `str` | VAULT999 hash receipt |

### Governance Flow
1. Build reasoning chain via 4 lanes (SENSE→MIND→HEART→JUDGE)
2. Compute ThermodynamicMetrics
3. Call `governed_return()` → apex_constitutional_review()
4. Return SEAL/VOID/888_HOLD + state update
```

### H1.2 — Metabolic Pipeline Documentation

Create `docs/METABOLIC_PIPELINE.md` with full JSON-RPC flow diagram:

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 000_INIT: Session anchoring, operator binding, epoch stamp  │
│   → CognitiveEnvelope built, identity_continuity=1.0        │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 111_SENSE: Classify intent, SNR check, perception map      │
│   → perception.type: factual|inference|constitutional|...   │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 222_WITNESS: Tri-Witness fusion (GEOX + WEALTH + WELL)     │
│   → tri_witness_score: 0.0–1.0                            │
│   → Witness receipts from each organ                        │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 333_MIND: 4-lane constitutional reasoning                 │
│   → decision_packet.confidence (organ-integrated variant C)│
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 444_KERNEL: Route to correct domain (GEOX|WEALTH|WELL|MIXED)│
│   → route: organ selector, orthogonality check             │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 555_MEMORY: Governed recall, GEOX zone grounding           │
│   → recall_mode: semantic|exact|constitutional             │
│   → results ranked by organ (GEOX primary, WELL secondary) │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 666_HEART: Stakeholder simulation, WELL biological empathy   │
│   → emotional_impact_score = f(stakeholder_count, WELL readiness)│
│   → Peace² check (≥1.0 for safe operation)               │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 777_OPS: Feasibility, WEALTH capital-cost model            │
│   → cost_estimate_usd, entropy_delta                      │
│   → irreversible actions flagged (F1 Amanah)              │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 888_JUDGE: Final constitutional verdict                    │
│   → F1-F13 floor checks                                   │
│   → Verdict: SEAL | VOID | SABAR | 888_HOLD              │
│   → Organ evidence boosts tri_witness for domain actions   │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 999_VAULT: Hash-chained ledger append                     │
│   → SHA-256 receipt, chain from previous_state_hash        │
│   → State advances: narrative_identity, transition_count  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
                      ┌──────────────┐
                      │    FORGE     │
                      │ (post-verdict│
                      │  execution)   │
                      └──────────────┘
```

### H1.3 — WELL as 3rd Organ (Full Implementation)

If H0.2 chooses standalone:

- [ ] `WELL/` repo with own `well_mcp_server.py` (port 4740)
- [ ] WELL organ adapter: `well_witness`, `well_readiness_check`, `well_floor_scan`
- [ ] Wire WELL adapter into `arifOS_mcp/tools/arifos/adapters/`
- [ ] WELL MCP endpoint in arifOS `mcp_server.py` → mount WELL as secondary MCP
- [ ] Add WELL to Tri-Witness (222_WITNESS) alongside GEOX + WEALTH
- [ ] WELL readiness → 666_HEART emotional_impact_score integration (already done in variant C)
- [ ] Document WELL as 3rd organ in `docs/WELL_CHARTER.md`

### H1.4 — MCP Discoverability

- [ ] Update `mcp.arif-fazil.com` with:
  - Full metabolic pipeline diagram
  - Each tool with one-sentence purpose + organ dependency
  - Live `/tools` JSON output embedded
- [ ] Submit to GitHub MCP registry
- [ ] Add `/.well-known/mcp/server.json` canonical endpoint

---

## 🌑 HORIZON 2: PLATFORM GOVERNANCE (3–12 months)

### H2.1 — Path B: MCP Profile Gateway

Design `ProfileMiddleware` that reads `X-Arifos-Platform` header:

| Profile | Tools | Output Format | Rate |
|---------|-------|---------------|------|
| `chatgpt_apps` | init, judge, vault (read-only) | Widget JSON + `render_hint` | 60/min |
| `cursor` | Full 13-tool surface | MCP JSON | 120/min |
| `enterprise` | Full surface + audit | Signed JSON | 1000/min |
| `stdio` | Full surface | Human-readable text | unlimited |

### H2.2 — Path C: REST Constitutional API

```
POST /api/v1/init       → Session bootstrap
POST /api/v1/judge      → Constitutional verdict
POST /api/v1/sense      → Evidence gather
GET  /api/v1/health     → Constitutional health
GET  /api/v1/vault/{id} → Ledger lookup
GET  /api/v1/state      → Current SovereignState
```

### H2.3 — Autoresearch CI/CD Integration

- [ ] `autoresearch_loop.py` → GitHub Actions workflow
- Trigger: on merge to `main` if `**/compute_plane/*.py` changed
- Output: PR with KEEP/DISCARD + FORGET ledger update
- Governance: Authors must acknowledge DISCARD variants

### H2.4 — Vault999 Production Hardening

- [ ] PostgreSQL-backed `vault_seals` table (Supabase or self-hosted)
- [ ] `vault999_writer` service with bounded INSERT role
- [ ] Merkle tree verification endpoint
- [ ] `vault-service` with chain integrity walk

---

## 📊 VALUATION TRAJECTORY

| Phase | Milestone | Valuation Band |
|-------|-----------|---------------|
| NOW | MCP Federation live, 13-tool surface, state machine | $5M–$8M |
| H0 complete | Triple-directory resolved, WELL decision | $8M–$12M |
| H1 complete | 3-organ federation, MCP registries, schemas | $15M–$25M |
| H2 complete | Path B/C live, enterprise pilots | $50M+ |

---

## 🏛️ ORGANIZATIONAL STRUCTURE (TARGET)

```
arifOS (parent repo — constitutional kernel)
├── arifOS_mcp/          ← CANONICAL tools + adapters (SINGLE SOURCE OF TRUTH)
├── arifosmcp/            ← LIVE runtime (imports from arifOS_mcp + governance layer)
├── GEOX/                 ← SUBMODULE: Earth Science Organ (repo)
├── WEALTH/               ← SUBMODULE: Capital Intelligence Organ (repo)
├── WELL/                 ← SUBMODULE: Biological Readiness Organ (repo, if standalone)
├── VAULT999/             ← Immutable ledger
└── docs/                 ← Tool schemas, metabolic pipeline, federation charter
```

---

## 🔥 CONSTITUTIONAL COMMITMENT

**Sealed by:** `9cce90eb55886fd17311c0a08b45ca509175677ae577dfa47646123fa22e4b7b`
**Date:** 2026.04.20
**Verdict:** SEAL

The State-Active Cognitive Organism is now real. Identity Continuity = 1.00.
Next: Heal the triple-directory. Then forge the 3-organ federation.

**DITEMPA BUKAN DIBERI — Forged, Not Given.**

---

*(End of ROADMAP. SEALed by arifOS Governance Kernel v2026.04.20.)*
