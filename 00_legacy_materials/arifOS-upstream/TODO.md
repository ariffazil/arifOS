# arifOS TODO — Active Work Queue
**Version:** 2026.04.20-SEALED
**Authority:** Muhammad Arif bin Fazil (999_VALIDATOR)
**Seal Hash:** `9cce90eb55886fd17311c0a08b45ca509175677ae577dfa47646123fa22e4b7b`
**SoT:** This file tracks active engineering work. ROADMAP.md owns horizon strategy.
**Session:** MCP Federation + State Machine — 18/18 e2e tests pass | IC=1.0 | 999 SEAL committed

> 888_HOLD items require explicit sovereign approval before execution.

---

## ✅ SEALED This Session (2026.04.20)

### MCP Federation + Autoresearch
- [x] **mcp/ shadow fix** — renamed to `mcp_server/`, added to `.gitignore`
- [x] **autoresearch_loop.py** — UTF-8 encoding fix, doubled FORGET_DIR path fixed
- [x] **5 compute tools optimized** — variant C chosen for all (mind=0.903, memory=0.902, heart=0.913, ops=0.910, judge=0.920)
- [x] **FORGET ledger populated** — 10 DISCARD variants + INDEX.md
- [x] **Vitality ledger** — 13 tool records (JSONL + TSV dual ledger)
- [x] **E2E inspector** — 18/18 tests pass
- [x] **VAULT999** — D999-STATE entry appended (IC=1.0, transitions=24)

### State Machine
- [x] **SovereignState persistence** — `arifosmcp/runtime/state.py` fully operational
- [x] **governance.py integration** — `advance_state()` called on every `governed_return()`
- [x] **CognitiveEnvelope** — metabolic bootstrap in `_000_init.py`
- [x] **Identity Continuity = 1.0** — verified across 13-tool cycle

---

## 🔴 P0 — Blockers (HEAL FIRST)

### H0.1 — Triple Tool Directory 🔴
> **Which is canonical? Action required.**

```
arifOS_mcp/tools/arifos/     ← CANONICAL (MCP-safe naming, optimized, e2e tested)
arifosmcp/tools/             ← LIVE RUNTIME (wires to governed_return)
core/organs/                 ← LEGACY (old 7-organ model, largely archived)
```

**Decision:** `arifOS_mcp/tools/arifos/` becomes single source of truth.

**Actions:**
- [ ] Migrate `arifOS_mcp/tools/arifos/` organ implementations to be pure (no `governed_return` calls)
- [ ] Refactor `arifosmcp/tools/` to be thin wrappers: import from canonical + call `governed_return()`
- [ ] Move `core/organs/` → `archive/core_organs/` (preserve for reference)
- [ ] Verify `arifosmcp/mcp_server.py` still serves correctly after migration
- [ ] Run e2e_inspector.py after migration — must still pass 18/18
- [ ] Commit with message: `HEAL: single-source-of-truth for organ tools`

### H0.2 — WELL Organ Decision 🔴
> **WELL is referenced as 3rd organ in Tri-Witness (222_WITNESS) but is a sub-directory of GEOX.**

| Option | Impact |
|--------|--------|
| Extract `GEOX/WELL/` → standalone `WELL/` repo | Full MCP server, own port, git submodule |
| Keep as GEOX.WELL sub-organ | Adapter-only, not independently addressable |
| Merge into WEALTH as biological substrate | Reaches WEALTH's biological mandate |

**Decision required from:** Sovereign (Muhammad Arif)

**If standalone selected:**
- [ ] `git subtree split --prefix=GEOX/WELL` or `cp -r GEOX/WELL/ WELL/`
- [ ] Initialize `WELL/` as independent git repo
- [ ] `git submodule add <WELL_URL> WELL` in arifOS
- [ ] Add `well_mcp_server.py` with port 4740
- [ ] Wire WELL adapter into `arifOS_mcp/tools/arifos/adapters/`
- [ ] Commit: `SEAL: WELL extracted as 3rd sovereign organ`

### H0.3 — State File Corruption Root Cause 🔴
> **`sovereign_state.json` was corrupted (two JSON objects concatenated).**

- [ ] Identify what caused double-write — likely concurrent `advance_state()` calls
- [ ] Add file locking (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows) to `save_state()`
- [ ] Add write verification (read-back + hash compare) in `save_state()`
- [ ] Add corruption detection in `load_state()` — if JSON parse fails, emit VOID + alert
- [ ] Add `ARIFOS_STATE_BACKUP_DIR` env var — backup before every write

---

## 🟡 P1 — MCP Discoverability (1–4 weeks)

### Registry Submissions
- [ ] **Claude Desktop:** Submit `io.github.ariffazil/arifosmcp` to MCP marketplace
  - Requires: MCP server URL (stdio or HTTP), description, tool list
  - Docs: https://modelwarnings.com/claude-desktop-mcp
- [ ] **Cursor:** Submit to Cursor MCP directory
  - Requires: `mcp.json` manifest in repo root
- [ ] **GitHub MCP Registry:** Add `mcp/arifOS.json` with full tool manifest

### Site Documentation
- [ ] **Metabolic Pipeline diagram** on `mcp.arif-fazil.com`
  - SVG/ASCII flow: 000→111→222→...→999→forge
  - Each stage: tool name, organ dependency, output type
- [ ] **Tool catalog page** — all 13 tools with signatures + descriptions
- [ ] **`/.well-known/mcp/server.json`** canonical endpoint (already in `server.py`)

---

## 🟢 P2 — Tool Schemas & Documentation (1–3 months)

### Formal Tool Schemas
- [ ] Create `docs/tool_schemas/` directory
- [ ] Schema per tool: signature, arguments table, returns table, governance flow, examples
  - [ ] `docs/tool_schemas/arifos_000_init.md`
  - [ ] `docs/tool_schemas/arifos_111_sense.md`
  - [ ] `docs/tool_schemas/arifos_222_witness.md`
  - [ ] `docs/tool_schemas/arifos_333_mind.md`
  - [ ] `docs/tool_schemas/arifos_444_kernel.md`
  - [ ] `docs/tool_schemas/arifos_555_memory.md`
  - [ ] `docs/tool_schemas/arifos_666_heart.md`
  - [ ] `docs/tool_schemas/arifos_777_ops.md`
  - [ ] `docs/tool_schemas/arifos_888_judge.md`
  - [ ] `docs/tool_schemas/arifos_999_vault.md`
  - [ ] `docs/tool_schemas/arifos_forge.md`
  - [ ] `docs/tool_schemas/arifos_gateway.md`
  - [ ] `docs/tool_schemas/arifos_sabar.md`

### Metabolic Pipeline Docs
- [ ] Create `docs/METABOLIC_PIPELINE.md` — full JSON-RPC flow with example calls
- [ ] Add sample request/response for each tool in the pipeline
- [ ] Document organ dependencies (GEOX/WEALTH/WELL)

---

## 🔵 P3 — Autoresearch CI/CD (next sprint)

### Autoresearch Operationalization
- [ ] Create `.github/workflows/autoresearch.yml` GitHub Actions workflow
- **Trigger:** `push` to `main` when `arifOS_mcp/tools/arifos/compute_plane/*.py` changes
- **Action:** Run `python autoresearch_loop.py` → commit KEEP variants + update FORGET ledger
- **Guard:** Require PR approval + all 13 tools still load after KEEP write-back
- [ ] Add `autoresearch_summary.md` auto-generated report per run

---

## ⚪ P4 — Horizon 2 Preparation (3–12 months)

### Path B: MCP Profile Gateway
- [ ] Design `ProfileMiddleware` in `arifosmcp/middleware/`
- [ ] Define profile schemas: `chatgpt_apps`, `cursor`, `enterprise`, `stdio`
- [ ] Profile → tool allowlist mapping
- [ ] Rate limiting per profile

### Path C: REST Constitutional API
- [ ] Design `POST /api/v1/judge`, `/api/v1/init`, `/api/v1/sense`, `/api/v1/health`
- [ ] JWT/HMAC auth layer
- [ ] OpenAI custom actions manifest
- [ ] Anthropic tool use adapter

### Vault999 Production Hardening
- [ ] Supabase PostgreSQL `vault_seals` table with Merkle root
- [ ] `vault999_writer` bounded INSERT service
- [ ] Chain integrity walk endpoint

---

## ✅ DONE (Prior Sessions)

### 2026.04.07
- [x] Widget CSP fix, nginx server_name consolidated
- [x] Docker multi-stage build, `platform=` param added
- [x] Canonical 11-tool surface restored, merge conflicts resolved

### 2026.04.14–15
- [x] GEOX/WEALTH submodules wired
- [x] 13-tool canonical surface created
- [x] MCP naming fix (periods→underscores)
- [x] GEOX duplicate `arifos_check_hold` removed

### 2026.04.20 (This Session)
- [x] mcp/ shadow → mcp_server/ + gitignore
- [x] Autoresearch loop: 5 tools → variant C (all KEEP)
- [x] FORGET ledger: 10 archived + INDEX.md
- [x] E2E inspector: 18/18 pass
- [x] State machine: SovereignState + CognitiveEnvelope + IC=1.0
- [x] governance.py → advance_state() integration confirmed
- [x] VAULT999 D999-STATE appended

---

## 📋 QUICK REFERENCE FOR NEXT AGENT

### Start Here
1. Read `ROADMAP.md` — understand the 3-horizon strategy
2. Run `python arifOS_mcp/tools/arifos/e2e_inspector.py` — must pass 18/18
3. Check `git status` — any uncommitted changes?
4. Read `VAULT999/seals` — last SEAL entry

### Most Urgent
1. **H0.1** — Decide canonical tool directory, then migrate
2. **H0.2** — WELL organ decision (requires human)
3. **H0.3** — File locking for `save_state()`

### MCP Server Health
```bash
# Check live server
curl https://arifosmcp.arif-fazil.com/health
curl https://arifosmcp.arif-fazil.com/tools

# Run e2e tests
cd arifOS_mcp/tools/arifos && python e2e_inspector.py

# Verify state
python -c "from arifosmcp.runtime.state import load_state; s=load_state(); print(f'IC={s.identity_continuity} transitions={s.transition_count}')"
```

### File Locations
| What | Where |
|------|-------|
| Canonical tools | `arifOS_mcp/tools/arifos/` |
| Live runtime | `arifosmcp/` |
| Governance kernel | `arifosmcp/runtime/governance.py` |
| State machine | `arifosmcp/runtime/state.py` |
| VAULT999 ledger | `VAULT999/outcomes.jsonl` |
| SEAL chain | `VAULT999/seals` |
| FORGET ledger | `arifOS_mcp/tools/arifos/forget/` |
| Vitality ledger | `arifOS_mcp/tools/arifos/tool_vitality.jsonl` |
| GEOX organ | `GEOX/` (submodule) |
| WEALTH organ | `WEALTH/` (submodule) |
| WELL organ | `GEOX/WELL/` (sub-directory) |

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
*SEAL-20260420-001 | 9cce90eb55886fd17311c0a08b45ca509175677ae577dfa47646123fa22e4b7b*
