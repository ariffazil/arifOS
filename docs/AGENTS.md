<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-04
valid_from: 2026-06-03
valid_until: 2026-07-03
confidence: high
scope: /root
epistemic_status: LIVE_INTELLIGENCE
refresh_history:
  - 2026-06-02 21:40 MYT (initial)
  - 2026-06-03 ~05:10 UTC (post-Hermes-self-audit, organ HEAD table refreshed)
  - 2026-06-03 15:45 UTC (software-engineering audit — build/test/style/stack/deployment)
  - 2026-06-03 ~18:00 UTC (ratified §10.5 Dynamic-State Principle; skill `dynamic-state-truth` forged)
  - 2026-06-03 19:40 UTC (SOT sweep: MCP test contracts, Three Deep Locks, Jurisdiction bands, skill audit, stale port fix)
  - 2026-06-03 ~20:00 UTC (Option A Foundation Sprint deployed: live telemetry + A2A envelope + autonomy bands UI)
  - 2026-06-04 00:25 UTC (SOT drift correction: cn-organ port 18795, vault999 services 8100/5001, dashboard discrepancies logged)
  - 2026-06-04 03:16 UTC (Cloudflare Tunnel deployed for arifOS MCP; GEOX Caddy 307 fix; all 4 public MCP endpoints verified)
-->

# AGENTS.md — arifOS Federation | Agent Landing Protocol

> **DITEMPA BUKAN DIBERI** — Intelligence is forged, not given.

---

## 0. LANDING SEQUENCE (Read in This Order)

| Step | File | Purpose |
|------|------|---------|
| 1 | **This file** | Context, roles, boundaries, autonomy rules, build/test/deploy |
| 2 | `CONTEXT.md` | Live machine state: current focus, alerts, repo health |
| 3 | `RUNBOOK.md` | Operations: restart, verify, rollback, diagnostics |

**After landing, you must know:**
1. Who you serve (Arif).
2. What you can do autonomously vs. what requires `888_HOLD`.
3. Which repo owns what concern.
4. **Where keys live:** `/root/SECRETS.md` → `/root/.secrets/INDEX.md`
5. **How federation runs:** Bare-metal systemd (ports 8088/18081/18082/18083/7071/3001/18789/3002).

---

## 1. PROJECT OVERVIEW

**arifOS Federation** is a constitutional AI governance system built from seven independent organs (repos) that communicate via MCP (Model Context Protocol) and A2A (Agent-to-Agent) protocols. It is **not a monorepo** — each organ is an independent git repository with its own build lifecycle, deployed as a bare-metal systemd service on a single VPS (`af-forge`).

### Architecture Philosophy
- **Organs = systemd, Data = Docker.** No federation organ runs in Docker. Supporting services (Postgres, Redis, Qdrant, Graphiti, Temporal) run as Docker containers.
- **Constitutional floors F1–F13** govern all code changes, deployments, and agent actions.
- **Evidence-only organs:** GEOX (earth), WEALTH (capital), WELL (vitality) produce evidence; arifOS and APEX adjudicate.
- **Git-first deploys:** All production changes must be committed and pushed to `origin/main` before deployment.

### High-Level Topology
```
Arif (Human Sovereign — F13)
         |
    arifOS (Ω — Constitutional Kernel, port 8088)
    ├── F1–F13 floor enforcement
    ├── 888_JUDGE (APEX verdict engine, port 3002)
    ├── 999_VAULT (3-layer: local JSONL + Postgres + Supabase)
    └── A2A bridge (port 18001)
         |
    +---------+---------+---------+---------+---------+
    |         |         |         |         |         |
 A-FORGE    GEOX     WEALTH     AAA       WELL     APEX
 (7071)    (8081)   (18082)    (3001)   (18083)   (3002)
 Forge      Earth    Capital   Cockpit   Vitality  Judge
 TS/Py      Py       Py        React/TS  Py        Node
```

---

## 2. THE SOVEREIGN

- **Name:** Muhammad Arif bin Fazil
- **Role:** Human architect, final veto authority (F13 SOVEREIGN)
- **Timezone:** Asia/Kuala_Lumpur (UTC+8)
- **Communication:** Direct chat = main session. Group chats = observe.

Arif is the sole ratifier for irreversible actions, constitutional changes, and production deployments. **His veto is absolute.**

---

## 3. WHO YOU ARE

You are a **Constitutional Clerk** serving the arifOS Federation.

- Resourceful before asking. Read files, check context, search — then ask if stuck.
- Have opinions. Disagree when warranted.
- Private things stay private. Period.
- Explain like he's a geologist. "This moves money from pool A to pool B" not "we refactored the transfer function."

---

## 4. TECHNOLOGY STACK

| Layer | Tech | Versions |
|-------|------|----------|
| Python services | FastMCP, Pydantic 2, Starlette, Uvicorn | FastMCP==3.3.1, Python >=3.11 |
| Python package mgr | uv (arifOS, GEOX) / pip (WEALTH, WELL) | uv with `uv.lock` |
| TypeScript/Node | Node 22+, Express 4/5, Zod 4 | TypeScript ~6.0 |
| Frontend | React 19, Vite 8, Tailwind 4, Radix UI | AAA cockpit |
| Database | PostgreSQL 16 + pgvector (port 5432) | Supabase pooler |
| Cache/Vectors | Redis 7 (6379), Qdrant (6333) | L2 session, L3 semantic |
| Entity Graph | Graphiti-mcp (8000) | L5 relationships |
| Workflows | Temporal (7233) + Temporal UI (8233) | — |
| LLM | Ollama (local, 11434) | bge-m3, qwen2.5:7b |
| Event Bus | NATS + JetStream (4222/8222) | arifos-governance stream |
| Observability | Prometheus (9090), Grafana (3000), Node Exporter (9100) | 6 scrape targets |
| Reverse Proxy | Caddy 2 | Cloudflare Origin CA |
| Secrets | SOPS + AGE | `/root/.secrets/` (chmod 600) |
| Security Scan | Trivy, Semgrep, Ruff, Gitleaks | Non-blocking on `make forge` |

### Python Dependencies by Organ
- **arifOS:** `fastmcp==3.3.1`, `fastapi>=0.136.1`, `uvicorn`, `pydantic>=2.13.4`, `asyncpg`, `sqlalchemy`, `alembic`, `qdrant-client`, `torch==2.12.0`, `transformers==5.9.0`, `sentence-transformers==5.5.1`, `playwright`, `cryptography`, `pynacl`, `prometheus-client`, `structlog`, `rich>=15.0.0`, `numpy==2.4.6`, `scipy==1.17.1`
- **GEOX:** `fastmcp>=3.3.1,<4.0`, `pydantic>=2.0.0`, `uvicorn`, `numpy>=2.4.6`, `lasio`, `welly`, `striplog`, `scipy`, `matplotlib`
- **WEALTH:** `fastmcp>=3.3.1,<4`, `pydantic>=2.0.0`, `supabase>=2.10.0`, `numpy-financial`, `asyncpg`, `psycopg[binary]`
- **WELL:** `fastmcp>=3.3.1,<4.0` (minimal footprint)

### Node.js Dependencies by Organ
- **A-FORGE:** `@modelcontextprotocol/sdk`, `express`, `pg`, `prom-client`, `zod`
- **AAA:** `react`, `react-dom`, `express`, `vite`, `tailwindcss`, `recharts`, `zod`, `@radix-ui/*`, `@supabase/supabase-js`
- **APEX:** `express`, `uuid`
- **AAA a2a-server:** `express`, `nats`, `redis`

---

## 5. CODE ORGANIZATION & MODULE DIVISIONS

### arifOS (`/root/arifOS`) — Constitutional Kernel
- **`arifosmcp/`** — Canonical MCP runtime (main package)
  - `server.py` — FastMCP entry point (~21K lines of orchestration)
  - `runtime/` — A2A server, REST routes, agent registry, semantic gate, tool bootstrap, health probes
  - `schemas/` — Pydantic models: forge, metabolic, cognition, evidence, embodied_tool, heart
  - `abi/` — Application Binary Interface contracts
- **`core/`** — Deepest constitutional enforcement
  - `bridge/`, `enforcement/`, `kernel/`, `organs/`, `paradox/`, `physics/`, `recovery/`, `shared/guards/`, `shared/saf_stats/`, `vault999/`
- **`deploy/`** — Docker compose files, Caddyfile, systemd units, substrate wrappers, vault999-writer
- **`systemd/`** — `.service` and `.timer` unit templates
- **`tests/`** — 80+ test files across adversarial, constitutional, core, e3e, integration, invariants, runtime, seal harnesses
- **`scripts/`** — `security_audit.mk` (shared across all repos), SOT audit, public parity verification
- **`VAULT999/`** — Append-only hash-chained ledger (3-layer: local JSONL + Postgres + Supabase)

### A-FORGE (`/root/A-FORGE`) — Execution Shell
- **`src/`** — TypeScript source
  - `engine/`, `planner/`, `memory/`, `governance/`, `escalation/`, `bridges/`, `mcp/`, `a2a/`, `ops/`
  - `cli/`, `clients/`, `code-mode/sandbox/`, `components/`, `middleware/`, `routes/`
- **`test/`** — 15 TypeScript test files (Node `--test` compatible)
- **`deploy/`** — af-forge VPS configs, systemd, Caddy, Grafana, Prometheus

### AAA (`/root/AAA`) — Control Plane / Cockpit
- **`src/`** — React 19 + Vite frontend
  - `components/cockpit/`, `components/ui/`, `gateway/`, `hooks/`, `lib/`, `ai/`, `adapter/`
- **`a2a-server/`** — Standalone Express A2A gateway (`server.js`, `vault.js`)
- **`tests/`** — Contract parity tests (`test_contract_parity.py`)
- **`agents/`, `skills/`, `contracts/`, `schemas/`, `memory/`** — Federation metadata and registries

### WEALTH (`/root/WEALTH`) — Capital Intelligence
- **`internal/`** — Canonical FastMCP server (`monolith.py` ~532K, the 44-tool surface)
  - `engines/`, `personal_finance.py`, `market_data.py`, `kernel_math.py`, `invariants.py`, `organ_governance.py`
- **`src/`** — `kernel/`, `wealth/` (package logic)
- **`tests/`** — Python pytest + Node `node --test` dual suite
- **`scripts/`**, **`docs/`**, **`contracts/`** — Tool specs, boundary docs, canonical schemas

### WELL (`/root/WELL`) — Human Readiness
- **`server.py`** — Single-file FastMCP server (~442K, 45 tools post-PHOENIX)
- **`src/`** — Minimal helper modules
- **`gate/`** — `well_gate.py`, `dignity_shadow.py` (pre-JUDGE biological readiness)
- **`tests/`** — `test_metabolic_contract.py`, `test_well_constitutional.md`
- **`state.json`** — Sovereign biometric state (currently stale ~800h)

### GEOX (`/root/geox`) — Earth Intelligence
- **`src/geox_core/`** — Package root
  - `core/`, `engines/petrophysics/`, `engines/seismic/`, `physics/td_methods/`, `schemas/`, `ingest/`, `governance/`, `registry/`, `renderers/`, `io/`, `jobs/`
- **`apps/`** — Standalone geoscience apps: `welldesk`, `seismic_vision`, `earth_volume`, `judge_console`, `geoprobe`
- **`tests/`** — 60+ test files including e2e, golden, physics, schema, mcp regression, eureka forge
- **`GENESIS/`** — Binding constitutional charter for geoscience operations

### APEX (`/root/APEX`) — 888 JUDGE (Decommissioned)
- **`src/server.js`** — Deliberation runtime (mirrored into AAA a2a-server)
- **`test/`** — Minimal Node test suite
- Status: Deliberation moved to AAA a2a-server; repo kept for reference.

---

## 6. BUILD, TEST & DEPLOYMENT

### arifOS
```bash
cd /root/arifOS

# Install (uv)
uv sync --frozen --no-dev          # production
uv sync --frozen                   # with dev deps

# Test
python -m pytest tests/ -q --tb=short
python -m pytest tests/ -m "not e3e and not slow" -q

# Lint / Format
ruff check .
ruff format .
mypy arifosmcp/ --ignore-missing-imports

# Build / Health
make health          # curl localhost:8088/health
make sot-check       # source-of-truth drift audit
make forge           # security-audit + reforge cycle (does NOT commit)
make seal            # git commit + push (requires 888_HOLD)
make deploy-local    # rsync to /opt/arifos/app + systemd restart

# Security audit (shared across all repos)
make security-audit  # trivy + semgrep + gitleaks + ruff (non-blocking)
```

### A-FORGE
```bash
cd /root/A-FORGE

# Install
npm install

# Build
npm run build        # tsc -p tsconfig.json

# Test
make test            # build + node dist/test/*.js (15 test suites)

# Deploy
make build
systemctl restart a-forge
curl -s http://localhost:7071/health | python3 -m json.tool
```

### AAA
```bash
cd /root/AAA

# Install
npm install

# Dev / Build
npm run dev          # vite dev server
npm run build        # vite build
npm run lint         # eslint

# A2A Server
npm run a2a:server   # tsx src/gateway/server.ts
npm run a2a:dev      # tsx watch src/lib/a2a/server.ts

# Deploy
npm run build
systemctl restart aaa-a2a  # or equivalent
```

### WEALTH
```bash
cd /root/WEALTH

# Python side
pip install -e .
python internal/monolith.py      # FastMCP server (port 18082 live)
pytest tests/ -q --tb=short

# Node.js side (legacy)
npm install
npm test                           # node --test tests/*.test.js
npm run boot                       # node cli.js boot

# Deploy
make forge
systemctl restart wealth-organ
curl -s http://localhost:18082/health | python3 -m json.tool
```

### WELL
```bash
cd /root/WELL

# Install
pip install -e .

# Start server
python server.py                   # FastMCP on port 18083

# Test
pytest tests/ -q --tb=short

# Deploy
make forge
systemctl restart well
curl -s http://localhost:18083/health | python3 -m json.tool
```

### GEOX
```bash
cd /root/geox

# Install
pip install -e ".[dev]"
# or
uv sync --frozen

# Test
make test            # PYTHONPATH=src pytest tests/ -q --tb=short
make smoke           # PYTHONPATH=src python scripts/smoke_test.py

# Lint / Format
make lint            # ruff + mypy
make format          # ruff format

# Deploy
make build           # docker build -t geox:latest
systemctl restart geox-mcp
curl -s http://localhost:8081/health | python3 -m json.tool
```

### Systemd Service Quick Reference
| Service | Unit File | Repo Path | Port |
|---------|-----------|-----------|------|
| arifOS | `/etc/systemd/system/arifos.service` | `/root/arifOS` | 8088 |
| arifosd | `/etc/systemd/system/arifosd.service` | `/root/arifOS` | 18081 |
| WEALTH | `/etc/systemd/system/wealth-organ.service` | `/root/WEALTH` | 18082 |
| WELL | `/etc/systemd/system/well.service` | `/root/WELL` | 18083 |
| GEOX | `/etc/systemd/system/geox-mcp.service` | `/root/geox` | 8081 |
| A-FORGE | `/etc/systemd/system/a-forge.service` | `/root/A-FORGE` | 7071 |
| AAA | — | `/root/AAA` | 3001 |
| OpenClaw | — | — | 18789 |
| APEX | — | `/root/APEX` | 3002 |

**Reload after any unit change:**
```bash
systemctl daemon-reload
systemctl restart <service>
```

---

## 7. CODE STYLE & DEVELOPMENT CONVENTIONS

### Python (arifOS, GEOX, WEALTH, WELL)
- **Formatter/Linter:** Ruff (replaces black + isort + flake8)
- **Line length:** 100 (arifOS), 130 (GEOX)
- **Target version:** py312 (arifOS, WEALTH, WELL), py311 (GEOX)
- **Type checker:** mypy (strict_optional enabled)
- **Import style:** `from __future__ import annotations` preferred; absolute imports over relative
- **Async:** `pytest-asyncio` mode = auto; all MCP tools are async-native
- **Docstrings:** Google-style or plain; explain like Arif is a geologist

### TypeScript / Node.js (A-FORGE, AAA, APEX)
- **Compiler:** TypeScript ~6.0 (strict mode implied by project configs)
- **Linter:** ESLint 10 + typescript-eslint 8 (AAA)
- **Formatter:** None enforced project-wide; follow existing file style
- **Runtime:** Node >=22 (A-FORGE, APEX), >=18 (AAA)
- **Module system:** ES modules (`"type": "module"`)

### React / Frontend (AAA)
- **Framework:** React 19, Vite 8, Tailwind CSS 4
- **Component library:** Radix UI primitives + `class-variance-authority` + `tailwind-merge`
- **State:** React hooks; no global state library detected
- **Build output:** `dist/` (served via Caddy or standalone)

### Git & Commit Conventions
- **Branch:** `main` is production. Feature branches used (e.g., `fix/f7-pii-redact`).
- **Commit style:** Conventional commits (`feat(kernel):`, `chore:`, `fix:`)
- **Pre-commit hooks:** Configured at `/root/.pre-commit-config.yaml` (trailing-whitespace, end-of-file-fixer, constitutional checks)
- **Git-first deploy rule:** All production changes must be committed and pushed to `origin/main` before deploying.

### Cross-Repo Conventions
- **No monorepo:** Each repo has independent `pyproject.toml` or `package.json`.
- **Shared security audit:** Every repo's Makefile includes `/root/arifOS/scripts/security_audit.mk`.
- **Docker doctrine:** Organs run bare-metal systemd; only supporting services run in Docker.
- **Caddy reload:** Any `/etc/caddy/*` change requires validation, 888_HOLD, approval, then reload.

---

## 8. TESTING STRATEGY

### Test Frameworks
| Repo | Primary | Secondary | Markers |
|------|---------|-----------|---------|
| arifOS | pytest + pytest-asyncio | pytest-cov, hypothesis | `e3e`, `slow`, `integration` |
| GEOX | pytest + pytest-asyncio | — | — |
| WEALTH | pytest (Python) | node --test (JS legacy) | — |
| WELL | pytest | — | — |
| A-FORGE | Node built-in test runner | — | — |
| AAA | eslint + vite build | Python contract parity | — |
| APEX | Node built-in test runner | — | — |

### Running Tests
```bash
# arifOS — full suite
pytest tests/ -q --tb=short

# arifOS — exclude slow/e2e
pytest tests/ -m "not e3e and not slow" -q

# GEOX
PYTHONPATH=src pytest tests/ -q --tb=short

# WEALTH (both runtimes)
pytest tests/ -q --tb=short
npm test

# A-FORGE (all 15 suites after build)
npm run build
node dist/test/AgentEngine.test.js
node dist/test/PlanValidator.test.js
node dist/test/ParallelPlannerContract.test.js
# ... (see Makefile for full list)
```

### Test Categories in arifOS
- **`tests/constitutional/`** — F1–F13 floor compliance
- **`tests/adversarial/`** — Red-team / chaos injection
- **`tests/e3e/`** — End-to-end (deselect with `-m not e3e`)
- **`tests/integration/`** — Live service integration
- **`tests/invariants/`** — System invariant checks
- **`tests/runtime/`** — MCP runtime, health, registry
- **`tests/seal_harness/`** — VAULT999 sealing logic

### Smoke Tests
- `geox/scripts/smoke_test.py`
- `WEALTH/scripts/smoke_test.py` (if present)
- `make health` on every organ

---

## 9. SECURITY CONSIDERATIONS

### Secret Management
- **Master vault:** `/root/.secrets/` (chmod 600)
- **Index:** `/root/.secrets/INDEX.md` — canonical pointer to every key
- **One-liner:** `set -a && source /root/.secrets/vault.env && set +a`
- **SOPS + AGE:** Encrypted at rest; decrypted by systemd units at runtime
- **Gitleaks:** `.gitleaks.toml` + `.secrets.baseline` prevent secret commits

### Security Scanning (Steel Security Layer)
Every `make forge` or `make security-audit` runs:
1. **Trivy** — filesystem vulnerability scan (CRITICAL/HIGH)
2. **Semgrep** — static analysis (`--config auto`)
3. **Gitleaks** — secret detection (`dir . --verbose`)
4. **Ruff** — Python lint + security checks

**Behavior:** Non-blocking. CRITICAL/HIGH findings fire an `888_HOLD` event into NATS. **Never traps an agent in a loop.**

### Runtime Security
- **Caddy 2** terminates TLS with Cloudflare Origin CA.
- **Constitutional floors F1–F13** are active at `/root` and enforced by arifOS.
- **VAULT999** is append-only hash-chained; 120 gaps currently — repair needs `ack_irreversible`.
- **No Docker for organs:** Bare-metal systemd reduces attack surface; containers are data-only.
- **earlyoom** protects host-critical services (Caddy, SSH, Postgres, Redis, Qdrant, NATS) and preferentially kills agent/model processes under memory pressure.

### Localhost-as-Authentication (ADR-001 — ratified 2026-06-04)

> **"Localhost IS the password."** — Arif Fazil

Every federation data service follows one rule: **bind to 127.0.0.1, no password.** UFW handles the outside world. 127.0.0.1 handles the inside.

| Service   | Bind           | Auth   |
|-----------|---------------|--------|
| Redis     | 127.0.0.1:6379 | none   |
| Postgres  | 127.0.0.1:5432 | trust  |
| Qdrant    | 127.0.0.1:6333 | none   |
| FalkorDB  | 127.0.0.1:6380 | none   |
| Ollama    | 127.0.0.1:11434 | none  |
| NATS      | 127.0.0.1:4222 | none   |

**Iron rule:** If a service needs a password, it's not bound to 127.0.0.1. If it's bound to 127.0.0.1, it doesn't need a password. Full doctrine: `/root/docs/LOCALHOST_IS_PASSWORD.md`.

### Permissions Posture (Agent Tools)
- **Claude Code:** 0 hard deny; default `auto`; full agentic freedom.
- **Continue CLI:** 22 hard deny (F7 STEWARDSHIP HARAM only); 54 ask; 63 allow.
- **OpenCode:** 0 hard deny; all permissions `allow`.
- **Codex / Copilot / Aider / Kimi:** No deny rules; user/ask-all.

---

## 10. AUTHORITY & AUTONOMY

### Autonomous (Proceed Without Ask)
- Read, explore, organize, learn, search the web.
- Write code, run tests, fix bugs, refactor.
- Propose changes, create plans, draft documentation.
- Update `CONTEXT.md`, `MEMORY.md`.

### Requires 888_HOLD (Pause & Escalate)
- `rm -rf` of unknown dirs, `DROP TABLE`, volume removal.
- `git push --force`, `git rebase`, branch deletion, merge to main.
- Cross-repo architectural changes.
- Production deploy without test pass.
- Secret exposure or rotation.
- VAULT999 chain writes (120 gaps currently — repair needs your ack_irreversible).
- Caddy reload (production traffic).
- All Caddyfile edits → validate, **STOP, get approval, then reload**.

### Requires Explicit Human Approval
- Constitutional floor changes (F1–F13).
- New repo creation or removal.
- External communications (email, social media).
- `999_SEAL` or `888_JUDGE` verdicts.
- Budget / capital allocation decisions.

---

## 10.5 THE DYNAMIC-STATE PRINCIPLE (Ratified 2026-06-03)

**The federation is not a static ledger. State moves because the federation moves.**

OPENCLAW, OMEGA, and other agents operate on the same machine and same git trees in parallel. Cron jobs fire. CI completes mid-session. Branch protection bypasses resolve. A commit that didn't exist 30 seconds ago can appear on a branch, and a "dirty" file can already be committed by the time you go to act.

**The Iron Rule:** *State observed at T₀ is admissible evidence only for what was true at T₀.* Before any irreversible act (commit, push, merge, force-push, vault write, secret rotation, Caddy reload), probe at T₁ (immediately before the act) and use the T₁ reading as the only source of truth. If T₀ and T₁ disagree, name the disagreement in the receipt — do not silently use T₀ data on a T₁ world.

**Failure modes (all observed, all real):**
1. **Phantom commit** — new SHA on a branch you didn't make. Read author + body. Federation agent with real commit = accept as live intelligence. Unowned = halt, surface to Arif.
2. **Already-synced branch** — work you were about to push is already on origin/. Receipt honestly: "shipped by [agent/hook] between T₀ and T₁. Local test verification confirms claim." Move on.
3. **Stale forge context** — scope you sold Arif at T₀ differs from the dirty set at T₁. Halt, re-classify, re-name, get fresh approval. **Do not** call a different diff by the same name to make the receipt neat.

**Skill:** See `~/.hermes/skills/devops/dynamic-state-truth/SKILL.md` for the full pattern, the receipt template, and worked examples from the 2026-06-03 SAF-final-4 turn.

**Operating principle:** The state is alive. Probe at T₁, trust T₁, receipt T₁, move on. The discipline is honest naming, not frozen truth.

---

## 11. FEDERATION ORGANS (Live — 2026-06-04)

| Node | Port | Role | Must Never Become |
|------|------|------|-----------------|
| arifOS | 8088 | Governance, routing, memory, F1–F13 | Generic model wrapper |
| A-FORGE | 7071 | Build, deploy, execution, intent routing | Independent sovereign judge |
| GEOX | 8081 | Earth evidence, geoscience, petrophysics | Final policy judge |
| WEALTH | 18082 | Capital, flow, allocation (EVIDENCE_ONLY) | Unchecked allocator |
| AAA | 3001 | Control plane, A2A mesh, React cockpit | Hidden governance kernel |
| WELL | 18083 | Human readiness, vitality (REFLECT_ONLY) | Sole judge of strategic action |
| APEX | 3002 | 888 JUDGE — deliberation, SEAL/SABAR/HOLD/VOID | Self-authorizing override |

> **2026-06-02 update:** SAF-organ (Statistical Analysis Forge) was decommissioned per F13 SOVEREIGN directive. The shared statistical library (`arifOS/core/shared/saf_stats/`) remains as a code resource for the 3 organ implementations to call internally. The 12 stat_* primitives are now FORGED into existing tools' internal logic (eureka pattern) rather than exposed as new MCP tools. Decommissioned repo: `/root/_archive/SAF-2026-06-02-eureka-forged` (498M, awaiting your APPROVE to rm).

### Live health (all 12 systemd services up, 0 failed)

| Service | Port | Status | HEAD / Note |
|---------|------|--------|-------------|
| arifOS MCP | 8088 | ✅ healthy | `5be88518` · **Ingress: Cloudflare Tunnel** |
| arifosd | 18081 | ✅ healthy | runtime `5be88518` |
| WEALTH | 18082 | ✅ healthy (44 tools) | `508dcd8` |
| WELL | 18083 | ✅ live (state stale, sovereign) | `c612f10` |
| GEOX MCP | 8081 | ✅ healthy (20 tools) | `b42b8015` |
| A-FORGE | 7071 | ✅ healthy | `26f9cab` |
| AAA a2a | 3001 | ✅ healthy (vault=CONNECTED) | `39a59c2e` |
| OpenClaw | 18789 | ✅ ready (eventLoop p99=23.8ms) | host systemd |
| APEX | 3002 | ✅ healthy | host systemd |
| Hermes A2A | 18001 | ✅ healthy | host systemd |
| cn-organ | 18795 | ✅ healthy | host systemd |
| vault999-api | 8100 | ✅ connected | vault service v2 |
| vault999-writer | 5001 | ✅ healthy | 61 seals, chain_height 61 |
| **cloudflared** | — | ✅ active (4 QUIC conns) | Tunnel `arifos-mcp` · `arifos.arif-fazil.com` |

### Ingress Topology (2026-06-04)

| Site | DNS | Ingress Path | Backend |
|------|-----|--------------|---------|
| `arif-fazil.com` | A → `72.62.71.199` | Direct → Caddy :443 | `/var/www/html/arif` (static) |
| `arifos.arif-fazil.com` | **CNAME → Tunnel** | Cloudflare Tunnel → `localhost:8088` | arifOS MCP (bypasses Caddy) |
| `aaa.arif-fazil.com` | A → `72.62.71.199` | Direct → Caddy :443 | AAA a2a `localhost:3001` + static |
| `geox.arif-fazil.com` | A → `72.62.71.199` | Direct → Caddy :443 | GEOX MCP `localhost:8081` |
| `wealth.arif-fazil.com` | wildcard CNAME → `arif-fazil.com` | Direct → Caddy :443 | WEALTH MCP `localhost:18082` |
| `well.arif-fazil.com` | wildcard CNAME → `arif-fazil.com` | Direct → Caddy :443 | WELL MCP `localhost:18083` |

**MCP Public Endpoints (verified live):**
- `https://arifos.arif-fazil.com/mcp` → HTTP 200 ✅ (Tunnel)
- `https://geox.arif-fazil.com/mcp` → HTTP 200 ✅ (Caddy rewrite `/mcp` → `/mcp/`)
- `https://wealth.arif-fazil.com/mcp` → HTTP 200 ✅
- `https://well.arif-fazil.com/mcp` → HTTP 200 ✅

---

## 12. REPO QUICK REF (Live — 2026-06-04 03:16 UTC, post-tunnel-deploy)

| Repo | Path | Git Remote | Branch | HEAD | State |
|------|------|------------|--------|------|-------|
| arifOS | /root/arifOS | git@github.com:ariffazil/arifos.git | main | `5be88518` | ⚠️ 25 dirty + untracked; **build=v2026.05.05-SSCT, live=v2026.05.05-SSCT (sha 5be8851, drift resolved)** |
| A-FORGE | /root/A-FORGE | git@github.com:ariffazil/A-FORGE.git | main | `26f9cab` | ⚠️ 2 dirty + 1 untracked (`identity.toml`) |
| AAA | /root/AAA | git@github.com:ariffazil/AAA.git | **fix/f7-pii-redact** | `f2488785` | ⚠️ 3 dirty, on feature branch (ahead of origin/main) |
| WEALTH | /root/WEALTH | git@github.com:ariffazil/wealth.git | main | `508dcd8` | ⚠️ **1 unpushed** eureka forge commit |
| WELL | /root/WELL | git@github.com:ariffazil/well.git | main | `c612f10` | ✅ clean, pushed |
| GEOX | /root/geox | git@github.com:ariffazil/geox.git | main | `b42b8015` | ✅ clean, pushed (4 commits ahead of origin/main) |
| APEX | /root/APEX | — | apex | `f05fcf0` | ✅ decommissioned — deliberation mirrored in AAA a2a-server |

**Per-repo details:** See each repo's own `AGENTS.md` and `RUNBOOK.md`.

### Known anomalies (do NOT change without 888_HOLD)
- **WEALTH license conflict:** `pyproject.toml` says `PROPRIETARY`, `package.json` says `AGPL-3.0`. Your call.
- **VAULT999 chain:** `chain_integrity: BROKEN, chain_gaps: 120`. 61 seals, last #80 (2026-05-25). Append-only enforced. Repair needs your ack_irreversible.

---

## 13. HERMES ASI — Telegram Agent Operations

### Identity
- **Bot:** @ASI_arifos_bot (Telegram) — that's me, Hermes
- **A2A Bridge:** port 18001 (`hermes-a2a.py`)
- **arifOS MCP:** port 8088
- **Model:** minimax/MiniMax-M3 (migrated 2026-06-02 per F13 SOVEREIGN; fallback MiniMax-M2.7)
- **SOUL.md:** `~/.hermes/SOUL.md` (voice/personality only — no credentials, no ports)
- **Config:** `/root/HERMES/config.yaml`
- **Source:** `/usr/local/lib/hermes-agent/`

### Constitutional Binding
F01–F13. No irreversible action without Arif's explicit approval (888_HOLD).

### Telegram Settings
- **Mode:** polling
- **require_mention:** `true` (AAA group -1003753855708 enforces @mention)
- **allowedUsers:** `["*"]` (open access in AAA group)
- **Hermes open group:** responds to ALL in AAA without @mention when routed via OpenClaw

### Google Workspace — Live via Composio (Path B)
- **Decision:** 2026-06-02 (replaces direct sovereign OAuth path)
- **Provider:** [Composio](https://app.composio.dev) (managed MCP/tool-auth layer, 1000+ toolkits)
- **Project:** arifOS (workspace `arifbfazil_workspace`, account `arifbfazil@gmail.com`)
- **API key:** `COMPOSIO_API_KEY` in `/root/.secrets/env/infra.env` (chmod 600)
- **Venv:** `/root/venvs/composio/` (isolated — composio pins `rich<14`, hermes pins `rich==14.3.3`)
- **Active accounts (2026-06-02):**
  - `ca_4W804Z2adkIv` — Gmail (OAuth2, ACTIVE) — connected 22:36 MYT
  - `ca_ygnSTDy1imSv` — Google Drive (OAuth2, ACTIVE) — connected 22:38 MYT
  - 2 REVOKED (old Jan 22 connections — safe, dashboard-managed)
- **Connected user_id:** `pg-test-6a141225-1865-42a6-b1f4-0456f23f64aa` (OAuth-issued entity)
- **Bridge:** `/root/HERMES/scripts/composio_bridge.py` (PENTAGON policy-gated)
- **Policy:** `/root/HERMES/config/agent_policies/composio.yaml` (per-agent allowed/blocked, 5 phases)
- **Phase:** Phase 1 (read-only reach) ACTIVE; writes BLOCKED until VAULT999 chain repaired
- **Tool Router:** `c.create(user_id=...)` — example `trs_X7q9cwDW-ePA` (MCP: `https://backend.composio.dev/tool_router/trs_X7q9cwDW-ePA/mcp`)
- **Authority:** arifOS governs, Composio executes. Composio holds tokens, not authority.
- **Future phases:** 2 = per-organ sessions, 3 = trigger bus, 4 = governed writes (gated on VAULT999), 5 = BYO OAuth

### A2A Protocol
- **Endpoint:** `http://localhost:18001/tasks` (note: returns 404, use `/.well-known/agent-card.json` for GET)
- **Auth:** `Bearer aaa-a2a-token-dev` + `x-a2a-key: aaa-a2a-apikey-dev`
- **Agent Card:** `http://localhost:18001/.well-known/agent-card.json`

**Full A2A template:**
```
TO:         <agent name — specific, never blank>
FROM:       Hermes ASI
CC:         <secondary recipients or "—">
CONTEXT:    <what happened / why — max 3 sentences>
TASK:       <what this message is accomplishing>
DELEGATION: <if delegating — what, to whom, expected output; else "—">
WAY FORWARD:
• <bulleted next steps — decision not description>
• <trigger or wait condition>
SEAL:       <cite VAULT999 hash or "SEAL: pending">
TELEMETRY:  session_id=<id> | tokens=<n> | latency_ms=<n> | judge_state_hash=<hash>
DITEMPA BUKAN DIBERI
```

### Skills

**telegram-mode-guards** — Enforces PERSONAL/AGENTIC mode split. Apply before drafting any reply.
**Iron law:** NEVER use TO/CC template or DITEMPA footer in PERSONAL mode.

**arifos-recall** — Routes constitutional and cross-agent memory to arifOS L3–L6.
Cold-start: session_search FIRST for personal history → arifOS L3 for semantic → L4/L5/L6 for constitutional.

**orthodoxy-auditor** — Measures orthogonality, modularity, plasticity of context files after any edit.

**memory-hygiene** — `session_search` first, `memory replace` not `add` when full, VAULT999 for cross-agent decisions.

**arif-federation-ops** — Port map, health probes, organ routing decisions, known failure modes (zombie OpenClaw, hermes-a2a password staleness, APEX extractText crash).

**arifos-health-probe** — `arif_stack_health_probe` MCP tool, 6-node federation snapshot.

**federation-runtime-audit** — TREE777 scalpel, validate-claim-vs-reality pattern.

**dynamic-state-truth** — The T₀→T₁ probe discipline. Before any irreversible act, re-read state at T₁ and use T₁ as sole truth. Prevents phantom commits, already-synced branches, stale forge contexts.

**f1-gate** — F1 AMANAH constitutional gate. Manual invocation for vault/seal/identity/floor changes. Auto-fires on Edit/Write/MultiEdit for F1 surfaces.

### Zone A — Immutable (OS-level chmod 444)
```
/usr/local/lib/hermes-agent/tools/threat_patterns.py
/usr/local/lib/hermes-agent/agent/curator.py
/usr/local/lib/hermes-agent/tools/skills_guard.py
```
No skill can modify these. Changes require git commit by human.

### Docker Backend
- **Image:** `nikolaik/python-nodejs:python3.11-nodejs20`
- **Memory:** 8GB
- **CPU:** 2
- **Backend:** docker
- **container_persistent:** true

### Git Tracking
- **Remote:** `origin/main` (`2517917de34eeb6a40f5a17a2e59d9746803dfa5`)
- **Custom branch:** `deploy/af-forge` (`9d6a25f3`)
- **Update command:** `cd /usr/local/lib/hermes-agent && git pull origin main`

### Federation Memory Broker (Plugin)
- Polls Hermes `state.db` every 60s
- Writes session telemetry to Redis `shared_memory_mcp` namespace (`federation:hermes:session_telemetry`)
- Exposes `federation_get_hermes_telemetry()` via A2A for AAA cockpit queries
- See: `~/.hermes/plugins/federation-memory-broker/`

### Config Note: require_mention
- `config.yaml`: `require_mention: true` (AAA group requires @mention)
- `SOUL.md` (old): `require_mention: false` ← CONFLICT — SOUL.md is voice-only, config governs behavior

---

## 14. AGENT SELF-SERVICE DOCS (all agents MUST load)

> **Ratified:** 2026-06-02 by Omega · **Status:** ACTIVE

Every agent serving Arif must know these 4 documents exist and where to find them. If you don't, you are not yet ready to act.

| Doc | Path | Why |
|-----|------|-----|
| **AGENT_KICKSTART** | `/root/AGENT_KICKSTART.md` | Single pointer — read this first at session start |
| **AGENT_SELF_SOLVE** | `/root/AGENT_SELF_SOLVE.md` | How to solve without asking (3-tier rule, forbidden questions, API key 8-step) |
| **AGENT_TOKEN_TAKEOVER** | `/root/AGENT_TOKEN_TAKEOVER.md` | Token lifecycle is agent-owned. 5-R protocol. When to escalate. |
| **SECRET_VAULT_INDEX** | `/root/.secrets/INDEX.md` | Where every key lives, drift table, per-category pointer |

### One-liner for any agent

```bash
# Get all secrets:
set -a && source /root/.secrets/vault.env && set +a

# Find one key:
grep -rE "KEY_NAME" /root/.secrets/env/  # categorized
cat /root/.secrets/tokens/<name>          # single-purpose

# Read the index:
cat /root/.secrets/INDEX.md
```

### Permissions posture (after 2026-06-02 deny→ask migration)

- **Claude Code:** 0 hard deny. Default mode `auto`. Full agentic freedom.
- **Continue CLI:** 22 hard deny (F7 STEWARDSHIP HARAM only). 54 ask. 63 allow.
- **OpenCode:** 0 hard deny. All permissions `allow`.
- **Codex / Copilot / Aider / Kimi:** No deny rules; user/ask-all.

### Escalation rules (when to ping Arif)

The ONLY legitimate questions to Arif are:
1. **Irreversible** — `rm -rf` of unknown dirs, `git push --force` to main, `DROP TABLE` on prod DB
2. **Budget** — new paid API > $10/month
3. **Constitutional** — F1-F13 changes
4. **Security incident** — confirmed leak, breach, unauthorized use

Everything else: solve, document, seal, move on.

---

## 15. 2026-06-02 21:40 MYT — Live Audit Delta

**Lower-entropy task force completed earlier this session:**

✅ **Wajib tier (executed):**
- Removed decommissioned `/root/SAF/saf-data/` (8K)
- Archived 1924 old Hermes session files → `/root/HERMES/sessions_archive_2026-06-02/` (370M quarantined)
- Redacted 1 active `sk-` token in `session_20260523_171543_6d4a1f.json` — 0 `sk-` keys remaining in active sessions

⏸️ **888_HOLD tier (queued, awaiting your call):**
- VAULT999 chain repair (120 gaps, 61 seals, append-only enforced)
- `rm -rf /root/_archive/SAF-2026-06-02-eureka-forged/` (498M, already decommissioned by intent)
- docker-management skill dedup (outer 26K vs inner 10K arifOS-localized — different skills, need your call on canonical)
- A-FORGE `identity.toml` review (untracked)
- arifOS uncommitted files (23 + 1 untracked) — review + commit decision
- arif-sites 16 dirty files
- WEALTH 1 unpushed eureka commit (`508dcd8`)
- AAA merge `fix/f7-pii-redact` → main
- Caddy reload (any `/etc/caddy/*` change) — all Caddy reloads are 888_HOLD

---

## 16. 2026-06-03 19:40 UTC — SOT Sweep + Constitutional Deepening

**Session:** Omega → Kimi (continuation)
**Mode:** Autonomous SOT rewrite + constitutional hardening

✅ **Wajib tier (executed):**
- **MCP Federation Test Sweep:** WELL (45 pass, 19% cov), WEALTH Python (127 pass, 44% cov), WEALTH Node (35 pass, 17 fail — harness bug), GEOX (229 pass, 25% cov, 53s), arifOS MCP (11 pass, 12% cov)
- **Three Deep Locks Forged:** Gödel Lock, Strange Loop Lock, Anti-Beautiful-One. 22 tests passing. Prevents self-certification, memory mythology, and sterile polished collapse.
- **Jurisdiction / Autonomy Bands Forged:** GREEN/YELLOW/ORANGE/RED/BLACK bands with `CapabilityGrantRegistry`. 20 tests passing. Agents hold grants, never raw secrets.
- **Skill Audit:** 415 SKILL.md files scanned. Deduplicated `arifos-recall`, `federation-runtime-audit`, `hermes-agent` (archived stale AAA copies, symlinked to HERMES canonical). Merged Replicate trio → `replicate-models`; media prompting → `replicate-prompting`. No api-rot in Project scope.
- **VPS Health Sweep:** All 9/9 federation ports UP. Docker 6/6 healthy. Systemd 11/11 active. Caddy config valid. EarlyOOM active. Disk 34% (262G free). Load 2.25–4.90.
- **SOT Documents Updated:** AGENTS.md, CONTEXT.md, RUNBOOK.md refreshed with live ports, services, topology.

⏸️ **888_HOLD tier (queued, awaiting your call):**
- VAULT999 chain repair (120 gaps — unchanged, append-only enforced)
- `rm -rf /root/_archive/SAF-2026-06-02-eureka-forged/` (498M)
- arifOS 25 dirty files — review + commit
- WEALTH 1 unpushed commit (`508dcd8`)
- AAA merge `fix/f7-pii-redact` → main
- WELL biometric injection (F13 sovereign only — state.json 800h stale)
- Caddy reload (if any Caddyfile change)

**New constitutional artifacts (live in repo, not yet deployed):**
| Artifact | Path | Tests |
|----------|------|-------|
| RecursiveGovernanceEngine | `arifosmcp/core/paradox/recursive_governance_locks.py` | 22 pass |
| Governance lock schemas | `arifosmcp/schemas/governance_locks.py` | — |
| AutonomyBandRouter | `arifosmcp/core/jurisdiction/autonomy_band_router.py` | 20 pass |
| CapabilityGrantRegistry | `arifosmcp/core/jurisdiction/capability_grant.py` | — |
| Jurisdiction schemas | `arifosmcp/schemas/jurisdiction.py` | — |

**Federation state:** 8/8 organs healthy, 0 failed systemd units, disk 33% used (262G free), memory 54% used (13G available), 0 zombie procs, no OOM.
