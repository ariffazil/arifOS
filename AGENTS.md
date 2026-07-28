<!-- SOT-MANIFEST
project: arifOS Federation
owner: Arif (F13 SOVEREIGN) — Muhammad Arif bin Fazil
last_verified: 2026-07-24
truth_rule: live :port/health and tools/list beat every word below
-->

# AGENTS.md — arifOS Federation

> **DITEMPA BUKAN DIBERI** — Forged, not given. Arif owns F13. You serve him, not yourself.
>
> Core doctrine: **probe before act**, **reversible-first**, **floor-checked**, **sealed-on-truth**.
>
> Constitutional kernel lives at `/root/arifOS/`. The constitution is the 13 Floors (F1–F13).
> The federation is split into 7 organs served via MCP. This file is a pointer, not a constitution.

---

## 1. Organs (live probe beats prose)

| Organ | Port | Role | Recipe |
|---|---|---|---|
| **arifOS (Ω)** | 8088 | Kernel — judge, seal, F1–F13, VAULT999 | `curl :8088/health` |
| **A-FORGE (Ψ)** | 7071 / 7072 | Execution — build, deploy, forge (lease-bound) | `curl :7071/health` |
| **GEOX (🌍)** | 8081 | Earth intelligence — wells, seismic, petrophysics | `curl :8081/health` |
| **WEALTH (💰)** | 18082 | Capital intelligence — NPV/IRR/EMV (compute, never allocate) | `curl :18082/health` |
| **WELL (🫀)** | 18083 | Human readiness — REFLECT_ONLY (never diagnose) | `curl :18083/health` |
| **AAA (🖥️)** | 3001 | Control plane + A2A + cockpit | `curl :3001/health` |
| **arifFLOW (Φ)** | 7073 | Metabolism — Rust daemon, Flow Quotient, receipt ledger, attention checkpointing. Routes/checkpoints/witnesses; never judges, never executes. | `curl :7073/health` |
| **HERMES** | (Telegram) | Sovereign relay — bridges cockpit to Telegram | see `kernel/HERMES_OPEN_GATE.md` |

**6 Planes** (EUREKA architecture): Sovereign (Arif) · Governance (arifOS) · Intelligence (agents) · Execution (A-FORGE) · Continuity (Postgres/Qdrant/Redis) · Truth (VAULT999).

**Cross-cutting surfaces** (not organs — constitutional properties, like F11 AUDITABILITY, VAULT999, Cooling Ledger):
| Surface | Role | Canonical |
|---------|------|-----------|
| **Kabarkan** | Sovereign observability plane — trace ingestion, span trees, cost attribution, verdict overlays, receipt linkage. Langfuse replacement. | `/root/A-FORGE/forge_work/2026-07-24/KABARKAN-IDENTITY.md` |

**Authority chain:**
```
arif_init → arif_think → arif_judge → arif_forge → arif_seal
   111         222         888          777          999
 observe      think       judge        forge         seal
```
Do not skip links. `arif_judge` says GO → `forge_lease` → execute → `arif_seal` closes.

---

## 2. Layout

```
/root/
├── AGENTS.md          ← this file (filesystem-level pointer)
├── CLAUDE.md          ← AAA-grade executor doctrine (load at boot)
├── CONTEXT.md         ← live machine state (T₀/T₁ timestamps; HEADs)
├── RUNBOOK.md         ← restart / health / rollback procedures
├── FEDERATION.md      ← federation contract summary
├── SOUL.md            ← human values, telos
├── LANDING.md         ← federation landing surface
├── NOTICE_BOARD.md    ← agent-facing announcements
├── Makefile           ← root-level `make prove` aggregator
│
├── arifOS/            ← Python kernel (uv, py312, AGPL-3.0)  — `/opt/arifos/app`
├── A-FORGE/           ← TypeScript executor (Node 22+)       — `/opt/a-forge/app`
├── AAA/               ← React 19 + Vite cockpit + A2A         — `/opt/aaa/app`
├── GEOX/              ← Python geoscience (BSL-1.1)          — `/opt/geox/app`
│   (alias: /root/geox → /root/GEOX — GEOX canonical)
├── WEALTH/            ← Python capital (AGPL-3.0)            — `/opt/wealth/app`
├── WELL/              ← Python human readiness (BSL)         — `/opt/well/app`
├── HERMES/            ← Python Telegram bridge + Telegram gateway
│
├── forge_work/        ← audit ledger, sealed artifacts, dated folders
├── VAULT999 → /root/.local/share/arifos/vault999   (append-only, hash-chained)
├── .secrets/vault.env ← single source of truth for 143 env vars
└── .secrets/INDEX.md  ← master secret index with drift table
```

Source at `/root/<organ>` → runtime at `/opt/<organ>/app`. Deploy via `systemctl restart <unit>` after rsync.

---

## 3. Shell init (always run first)

```bash
set -a && source /root/.secrets/vault.env && set +a
```

This sources 143 environment variables. Anything that hits a network service or signs a receipt needs them.

**5-R Protocol for secrets:** READ → RESOLVE → RECONCILE → RESTART → REPORT. Never ask Arif for a key, hardcode keys, paste keys in chat/VAULT999, commit `.env`, or set secret files > mode 600.

**LOCALHOST_IS_PASSWORD doctrine:** All data services (Postgres, Redis, Qdrant, FalkorDB, Ollama, NATS) bind 127.0.0.1 with no auth. UFW blocks the outside. Full doctrine: `/root/docs/LOCALHOST_IS_PASSWORD.md`.

---

## 4. Session start checklist

Before acting on any request:

1. `source /root/.secrets/vault.env` (set -a / set +a)
2. Read `/root/AGENTS.md` (this file) and `/root/AAA/CLAUDE.md` (binding agent doctrine)
3. Boot via SALAM: `cat /root/AAA/prompts/SALAM_AAA_INIT.md`
4. **Read the reality:** `/root/.local/share/arifos/carry_forward.json` (session state) + `/root/AAA/state/flow_state.json` (FQ pulse). **NOT** CONTEXT.md — deprecated.
5. Probe: `curl -s http://127.0.0.1:8088/health | jq .` (then the other organs)
6. Check dirty repos: `for d in /root/{arifOS,A-FORGE,AAA,GEOX,WEALTH,WELL}; do git -C "$d" status -s; done`
7. Check deprecation map: `cat /root/AAA/docs/deprecation-registry.json | jq .`

If stuck: 3-strikes rule (3 different approaches before asking). Read files, check logs, search the web, run diagnostics.

---

## 5. Build, test, deploy — per organ

### 5.1 arifOS — Python kernel (`/root/arifOS`)

```bash
cd /root/arifOS
uv sync --frozen                            # install (Python 3.12–3.14)
pytest tests/ -q --tb=short                 # skip slow: -m "not e3e and not slow"
ruff check . && ruff format .               # lint + format
mypy src/ --ignore-missing-imports          # type check
make sot-check                              # source-of-truth drift
make health                                 # curl :8088/health
make deploy-local                           # rsync → /opt/arifos/app + systemctl restart arifos
```

Package: `arifos` v2026.7.17.post4 (AGPL-3.0). Extras: `[geox] [wealth] [well] [aaa] [io] [search] [google] [db] [heavy] [observe] [ml] [vectors] [browser] [federation]`. Optional `[dev]` for pytest/ruff/mypy/hypothesis.

### 5.2 A-FORGE — TypeScript executor (`/root/A-FORGE`)

```bash
cd /root/A-FORGE
npm ci && npm run build                     # tsc -p tsconfig.json
npm test                                    # node --test from dist/test/
make test                                   # security-audit + build + all suites
node dist/test/PlanValidator.test.js        # individual test runner
node dist/src/interfaces/server.js          # start (HTTP 7071)
npm run mcp:stdio                           # stdio MCP for OpenCode
systemctl restart a-forge                   # deploy API
systemctl restart a-forge-mcp               # deploy MCP
```

Stack: Node 22+, TypeScript 6.0.3, NodeNext ESM (`"type": "module"`), Zod 3.25, Express 5.1, MCP SDK 1.9. Tests run from `dist/test/` — rebuild before testing.

### 5.3 AAA — React 19 cockpit (`/root/AAA`)

```bash
cd /root/AAA
npm install && npm run build                # vite build
npm run lint                                # ESLint 10
npm run a2a:server                          # dev A2A gateway (tsx)
npm run test                                # lint + build + security + stabilization
npm run validate:aaa                        # agent-cards + root-agent-config validation
systemctl restart aaa-a2a                   # deploy production A2A
```

Stack: React 19.2, Vite, Tailwind 4, Radix UI, shadcn/ui, Zod 4.4, @a2a-js/sdk 0.3.

### 5.4 GEOX — Python geoscience (`/root/GEOX` or `/root/geox`)

```bash
cd /root/GEOX
uv sync --frozen                            # install (Python 3.11+)
PYTHONPATH=src pytest tests/ -q --tb=short
ruff check src/ && ruff format src/
make smoke                                  # scripts/smoke_test.py
make build && make up                       # docker build / compose up
systemctl restart geox-mcp
```

Stack: lasio, welly, wellpathpy, striplog, segyio, statsmodels, scipy, matplotlib. License: BSL-1.1.

### 5.5 WEALTH — Python capital (`/root/WEALTH`)

```bash
cd /root/WEALTH
uv sync --frozen                            # Python 3.12+
pytest tests/ -q --tb=short
ruff check . && ruff format .
npm test                                    # Node.js side, if any
systemctl restart wealth-organ
```

Stack: supabase, yfinance, pydantic-ai, langgraph, quantlib, riskfolio-lib, pymc, polars, duckdb, pyarrow. License: AGPL-3.0.

### 5.6 WELL — Python human readiness (`/root/WELL`)

```bash
cd /root/WELL
uv sync --frozen                            # Python 3.12+
pytest tests/ -q --tb=short                 # asyncio_mode = "auto"
ruff check . && ruff format .
systemctl restart well
```

Minimal stack: fastmcp 3.4.4, pydantic 2.13.4, httpx. REFLECT_ONLY — never diagnose, never adjudicate.

### 5.7 Federation-wide (`/root/Makefile`)

```bash
make prove                                 # full proof cycle
make health                                 # 6-port health sweep
make sot-check                              # source-of-truth drift
make security-audit                         # trivy/semgrep/gitleaks/ruff
make floor-benchmark                        # F1–F13 live kernel benchmark
make vault999-verify                        # ledger chain integrity
make reality-replay                         # reality ledger replay
make scorecard                              # ARIFOS_SCORECARD.json
make install-all                            # federation-wide install (uv)
make test-all                               # federation-wide test
make health-all                             # federation-wide health
make status-all                             # federation-wide git status
```

---

## 6. Constitutional floors (F1–F13)

| Floor | Type | One-line rule |
|---|---|---|
| **F1 AMANAH** | HARD | Reversible-first. Irreversible → `888_HOLD`. |
| **F2 TRUTH** | HARD | ≥ 0.99 fidelity. Cheap claims → `VOID`. |
| **F3 TRI-WITNESS** | DERIVED | Human × AI × Earth × Verifier ≥ 0.75 (Nash). |
| **F4 CLARITY** | HARD | ΔS ≤ 0 — every output reduces entropy. |
| **F5 PEACE²** | SOFT | Non-destructive power. Blocks harm/harass/extort. |
| **F6 EMPATHY** | SOFT | Protect weakest stakeholder. κᵣ thresholds. |
| **F7 HUMILITY** | HARD | Ω₀ ∈ [0.03, 0.05]. No fake certainty. |
| **F8 GENIUS** | DERIVED | G = (A×P×E×X)^(1/4) ≥ 0.80. |
| **F9 ANTIHANTU** | HARD | No deception, manipulation, consciousness claims. C_dark < 0.30. |
| **F10 ONTOLOGY** | HARD | AI-only ontology. No soul/feelings/sentience. |
| **F11 AUDITABILITY** | HARD | Every decision logged, inspectable, attributable. |
| **F12 INJECTION** | HARD | Injection defense. Risk < 0.85. |
| **F13 SOVEREIGN** | HARD | Human veto FINAL. Strongest floor. |

Hard violation → `VOID` (blocked). Soft tension → `CAUTION` or `HOLD`.

**A-FORGE execution gates** (actual pipeline per AgentEngine.ts, verified 2026-07-27):

| Gate | File | Location | What it does |
|---|---|---|---|
| **ModelCapabilityGate** | `ModelCapabilityGate.ts` | AgentEngine L298-330 | Validates model capability via registry; thin, non-deliberative. CI/FORGE_TEST_MODE bypass. |
| **PlanGovernanceGate** | `PlanValidator.ts` | AgentEngine L332-399 | Validates plan DAG against governance card. BLOCK/HOLD/ALLOW. |
| **AmanahLockManager** | `AmanahLockManager.ts` | FileTools/EditorTools | Distributed mutex for file operations — acquires before writes, verifies lock before mutations. NOT in execution pipeline; operates at file level. |
| **GovernanceBridge** | `GovernanceBridge.ts` | evaluate.ts | APEX G computation bridge for tool registration. HTTP bridge to arifOS for risk classification. NOT in execution pipeline. |
| **ApprovalBoundary** | `ApprovalBoundary.ts` | Hold queue | Ticket creation when PlanGovernanceGate returns HOLD. State machine: thinking→drafting→holding→ready→approved→executing→executed. NOT an active blocking gate. |

**Note:** The previous "4-layer sequential gate" was documentation that diverged from code. The actual architecture is 2 pipeline gates (ModelCapability + PlanGovernance) with 2 supporting mechanisms (AmanahLock distributed mutex + ApprovalBoundary hold queue) and 1 cross-cutting bridge (GovernanceBridge for G computation). See `/root/A-FORGE/forge_work/2026-07-27/gate-eval-phase1/PHASE1-SEAL.json` for the full audit.

---

## 7. Autonomy tiers (T1 / T2 / T3)

### T1 — AUTO-DO (zero friction)
Read, grep, edit, test, commit, lint, format, restart services, web search. Just do it. No announcement.

### T2 — ANNOUNCE + PROCEED (10s window)
Service restart on production, schema migration on dev, new dependency, deploy after green tests. Pattern: "Going to X. Why: Y. Risk: reversible. Proceeding in 10s."

### T3 — ASK / 888_HOLD (only these)
- `rm -rf` of unknown dirs, `DROP TABLE`, volume removal
- `git push --force` to main, branch deletion
- New paid API > $10/month
- Constitutional changes (F1–F13)
- Secret exposure or rotation
- External communications (email, social)
- Production deploy without test pass

Ask format: Decision (1 line) + Recommendation (1 line) + Risk if wrong (1 line).

**Never ask Arif:** API keys, coding opinions, library choices, naming conventions, "should I commit?", "should I run tests?" (always yes), "what if X happens?" (handle it).

---

## 8. Code style

- **Python:** Ruff (line length 100 arifOS, 130 GEOX), mypy strict, absolute imports, `pyproject.toml` driven. Conventional commits.
- **TypeScript:** ESLint 10, Node ≥ 22, ES modules (`"type": "module"`), NodeNext ESM with explicit `.js` extensions in intra-repo imports.
- **React:** React 19, Vite 8, Tailwind 4, Radix UI, shadcn/ui patterns.
- **Commits:** Conventional (`feat:`, `fix:`, `chore:`, `docs:`). End messages with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **Tags:** `vYYYY.MM.DD` only (Iron Rule). Never `v1.2.3`, `v55.7.0`. Date IS the version. Legacy tags (`v55.*`, `v0.1.*`) are not to be replicated.
- **Branches:** `main` is production. Feature branches for work. Git-first deploy: commit + push before restarting the systemd unit.
- **Principal agents (A2A):** declare `principal_agent` field in every `agent-card.json` — one of `human`, `architect`, `agent`, `institution`, `earth`, `void`, `liar`, `llm`, `model`. See `/root/AAA/contracts/AAA_PRINCIPAL.md`.

### Epistemic tags (mandatory on substantive claims)
`CLAIM` · `PLAUSIBLE` · `HYPOTHESIS` · `ESTIMATE` · `UNKNOWN`. Overconfidence = F7 violation. Uncertainty is a feature, not a defect.

### QQQ Recommendation Discipline (mandatory on RECOMMENDATION/DECISION/VERDICT)
Every recommendation must pass:
- **Q1 Qualitative:** ≥5 paths enumerated (incl. NULL + INVERSE), categorized
- **Q2 Quantitative:** BR, REV, Time, Conf, PA per path, dominance analysis
- **Q3 Quantum:** precedent, interference, superposition, observer effects

Missing any → tag `INADMISSIBLE-QQQ-INCOMPLETE`. Never suppress. Full doctrine: `/root/AAA/governance/QQQ_RECOMMENDATION_PROTOCOL.md`.

### Dynamic-State Principle (T₀ → T₁)
State observed at T₀ is evidence only for T₀. Before any irreversible act, re-probe at T₁ and use T₁ as sole truth. If T₀ and T₁ disagree, name the disagreement — don't use stale data.

### Docker Doctrine
Organs run **bare-metal systemd**. Only supporting services (Postgres, Redis, Qdrant, Graphiti, Temporal, NATS, Prometheus, Grafana, MinIO, SearXNG) run in Docker. **Do NOT containerize core organs.**

---

## 8.5 The Wire — 3-layer constitutional enforcement

> Cross-organ enforcement of F1–F13 via POSIX physics, not prompts.
> Source of truth: `/root/arifOS/scripts/wire/`. Deploy with `make -C /root/arifOS/scripts/wire install`.

```
888 — SOVEREIGN (Arif) — F13 veto
  ↓
arif_judge — Kernel :8088 — SEAL/HOLD/VOID
  ↓
Layer 3: Reasoning — F4 Monitor + Circuit Breaker
  ↓
Layer 2: Runtime — Ghost JSON/ENV + dep-check
  ↓
Layer 1: Static — /etc/arifos/organ_dependencies.json
  ↓
ORGANS: arifOS  A-FORGE  AAA  GEOX  WEALTH  WELL
```

| Layer | Surface | Tool | What it does |
|---|---|---|---|
| 1 Static | `configs/organ_dependencies.json` | (manifest) | Each organ declares upstream deps + HOLD/HOLD_if_below actions |
| 2 Runtime | `/var/run/arifos_state.json`, `arifos_env.sh` | `arif-dependency-check` | Live cross-organ dep validation, exit 0/1 |
| 3 Reasoning | `/var/run/arifos_f4_state.json` | `arif-circuit-breaker`, `arif-f4-monitor` | Anti-loop guards — LOCK at 2 attempts / F4 HOLD at 3 cycles |

**Five blindspots sealed (F1 + F4):**

1. Execution Authority — agent mis-diagnoses H_WELL as M_WELL → circuit breaker + WELL routing
2. Cross-Organ Cascade — GEOX→WEALTH without WELL check → dependency manifest + validation
3. F4 Reasoning Loop — read-loop infinite, token burn → F4 monitor auto-HOLD
4. Dirty kernel state — untracked registry drift → Surface Conformance Gate (P0)
5. Wire tool orphan — `/usr/local/bin/` with no source repo → `arifOS/scripts/wire/` (this section)

**Tool index:**

```bash
arif-dependency-check                  # validate all dep edges, exit 0/1
arif-circuit-breaker {record|status|reset}   # anti-loop, LOCK @ 2 fails
arif-f4-monitor        {check|status|reset}  # state-hash F4 cap, HOLD @ 3 cycles
```

**Sealed:** 2026-07-27 · `arifOS/scripts/wire/` commit `3463ed145` (source-of-truth) + arifOS Surface Gate `f9a896aaa` (live conformance).

---

## 9. Memory landscape (6 levels)

```
L1 Redis      — now / ephemeral
L2 Redis      — session thread
L3 Qdrant     — fuzzy similarity (collection: arifos_memory)
L4 Supabase   — official structured record (25 domain tables)
L5 Graphiti   — relationships (FalkorDB + Ollama)
L6 VAULT999   — immutable sealed truth
```

Rule: memory is not truth until it has provenance. Truth is not final until sealed.

**VAULT999** — `/root/VAULT999 → /root/.local/share/arifos/vault999`. Canonical: `/root/arifOS/VAULT999/outcomes.jsonl` — append-only, hash-chained JSONL. `chattr +a` immutability. Merkle anchor every 100 receipts. **Never** edit, rewrite, or "clean up" outcomes.jsonl. New entries only. Derivative query path: Supabase `vault_sealed_events` via `vault999-writer.service` — for queries, NEVER source of truth.

---

## 10. Security considerations

- **Secrets:** `/root/.secrets/vault.env` (mode 600). Never commit. Never paste in chat/VAULT999. Always `${ENV_VAR}` placeholders in config.
- **Public exposure:** Only Cloudflare Tunnel + Caddy. Organs bind 127.0.0.1. Public MCP endpoints:
  - `https://arifos.arif-fazil.com/mcp` → :8088
  - `https://mcp.arif-fazil.com/mcp` (canonical public door) → :8088 arifOS kernel (8 constitutional tools)
  - `https://forge.arif-fazil.com/mcp` → :7072 A-FORGE (direct proxy, gated via `/gate/check`; POST-safe, NOT a redirect)
  - `https://geox.arif-fazil.com/mcp` → :8081
  - `https://wealth.arif-fazil.com/mcp` → :18082
  - `https://well.arif-fazil.com/mcp` → :18083
  - `https://aaa.arif-fazil.com` → :3001
- **F12 INJECTION defense:** Every claim routed through contradiction scan + Kill Matrix K001–K007. `forge_security_drift_scan` monitors ports/cron/systemd against Machine Constitution registry.
- **F1 AMANAH:** `AmanahLockManager` quarantines reversible vs irreversible. BACKUP before overwrite. Idempotent actions only on shared state.
- **Forensics:** `forge_work/<date>/` is the audit trail. Every SEAL/HOLD/VOID emits a sealed receipt. Use `journalctl -u <organ> -f` for live logs.
- **A-FORGE tool policy:** LOW risk → auto | MEDIUM → advisory | HIGH/CRITICAL → `888_HOLD`.
- **Forbid:** `gitleaks` plain-text leaks, `trivy` CRITICAL findings without override, `semgrep` injection patterns, `ruff` F-floor violations.
- **CAPTCHA on inbound federation surfaces = HARAM.** Inbound authentication is strictly cryptographic (Ed25519 identity binding + SCT capability tokens). Do not challenge legitimate agent traffic with visual or perceptual gating. CAPTCHA is a legacy paradigm built on the obsolete assumption that "human = valid, bot = malicious." ML models now exceed human visual cognition on standard perceptual challenges, and autonomous agents are legitimate actors requiring structured access — not visual barriers designed for human eyes. CAPTCHA tools (e.g. NopeCHA) are permitted strictly as **outbound utilities** for external site bypass (`forge_fetch`, `forge_search`, `capital_market`). They must never be connected to any inbound AAA handler or federation gateway. Reference: `/root/AAA/docs/CAPTCHA_IS_OBSOLETE.md`.

### Forge gate (sealed deploy)
Every SEAL-grade deploy runs through ALL four layers (see §6). Each organ's `make forge` target runs `clean-temp sot-bump security-audit` before declaration. `forge` is the last gate before `arif_seal`.

---

## 11. Health & recovery

```bash
# One-liner federation probe
for svc in arifos:8088 aforge:7071 aaa:3001 geox:8081 wealth:18082 well:18083; do
  name="${svc%%:*}"; port="${svc##*:}"
  curl -sf "http://localhost:$port/health" >/dev/null 2>&1 && echo "✅ $name :$port" || echo "❌ $name :$port"
done
```

Service → systemd unit mapping (full table in `/root/RUNBOOK.md`):

| Service | Unit | Port |
|---|---|---|
| arifOS kernel | `arifos.service` | 8088 |
| A-FORGE API | `a-forge.service` | 7071 |
| A-FORGE MCP | `a-forge-mcp.service` | 7072 |
| AAA A2A | `aaa-a2a.service` | 3001 |
| GEOX MCP | `geox-mcp.service` | 8081 |
| WEALTH | `wealth-organ.service` | 18082 |
| WELL | `well.service` | 18083 |
| arifFLOW | `arifflow.service` | 7073 |
| Caddy | `caddy.service` | 80/443 |
| NATS | `nats-server.service` | 4222 |

Restart policy: T1 single service auto; T2 multi-service ANNOUNCE; T3 full federation requires 888_HOLD from Arif.

---

## 12. Testing strategy

- **arifOS**: `pytest tests/ -q --tb=short`. Slow marker: `pytest -m "not e3e and not slow"`. Suites in `tests/`: `adversarial/`, `act/`, `conformance/`, `agi_kernel_readiness/`, `amanah`, `autoresearch/`, `civilian_sovereignty/`, `art/`, `apps/`, `abis/`, `agentic_conformance/`.
- **A-FORGE**: Tests compile to `dist/test/` then run via `node dist/test/<Name>.test.js`. Suites cover `AgentEngine`, `PlanValidator`, `GovernanceCardGate`, `FloorEnforcer`, `AmanahLock`, `AmanahLockManager`, `QQQRuntime`, `TriWitnessValidator`, `TrustTierEnforcer`, `SCTCryptoVerify`, `MerkleReceiptAnchor`, `CoolingGate`, `F13HaltChannel`, `VerticalAgentE2E`, `WorkflowValidator`, `a2a`, `engine`, `sense`, `thermodynamic`, `confluence`, `operatorAuth`, `operatorConsole`, `ticketStore`, `intentRouter`, `ToolScoper`, `SkillStagingGate`, `SkillStore`, `GovernanceCardGate`, `ParallelPlannerContract`, `MerkleReceiptAnchor`, `AAESignatureRequired`, `AutonomousForgeGate`, `ChatGPTChannelPolicy`, `aThinkGuard`, `VerifiedSessionsOnly`, `peerContractService`. Run all via `make test`.
- **AAA**: `npm test` → `lint + build + mcp-apps-security + stabilization`. Specialized: `federation_conformance_harness.py`, `mcp_cognitive_test_harness.py`, `test_contract_parity.py`, `test_email_transport_boundary.py`, `test_peer_federation_contract.py`.
- **GEOX / WEALTH / WELL**: `pytest tests/ -q --tb=short` (WELL: `asyncio_mode = "auto"`).
- **Federation**: `make prove` aggregates health, sot-check, security-audit, floor-benchmark, organ-boundary-benchmark, vault999-verify, reality-replay, scorecard. Output: `reports/ARIFOS_PROOF_PACK.md`.

Verification-as-terminal-state: a task is done only when verified. Never claim "done" without running tests + probe.

---

## 13. Canonical pointers

| What | Where |
|---|---|
| Agent doctrine (binding) | `/root/AAA/CLAUDE.md` |
| Federation landing | `/root/AGENTS.md` (this file) |
| Live session state | `/root/.local/share/arifos/carry_forward.json` (auto-updated) |
| Ops runbook | `/root/RUNBOOK.md` |
| Federation contract | `/root/FEDERATION_CONTRACT.md` |
| Constitutional kernel | `/root/arifOS/AGENTS.md` + `/root/arifOS/GENESIS/000_KERNEL_CANON.md` |
| F1–F13 floor definitions | `/root/arifOS/GENESIS/FLOOR_TABLE.json` |
| AAA principal agent taxonomy | `/root/AAA/contracts/AAA_PRINCIPAL.md` |
| A-FORGE Layered Execution | `/root/A-FORGE/CLAUDE.md` |
| EUREKA 6-plane architecture | `/root/AAA/docs/EUREKA_SIX_PLANE_EXECUTION_LOOP.md` |
| QQQ doctrine | `/root/AAA/governance/QQQ_RECOMMENDATION_PROTOCOL.md` |
| Intelligence constraint physics (Δ·Ω·Ψ grounded) | `/root/AAA/governance/INTELLIGENCE_CONSTRAINT_PHYSICS.md` |
| Boot ceremony | `/root/AAA/prompts/SALAM_AAA_INIT.md` |
| Zen alignment | `/root/AAA/prompts/AAA-ZEN-ALIGNMENT.md` |
| Secrets vault | `/root/.secrets/INDEX.md` |
| Vault ledger | `/root/VAULT999 → /root/.local/share/arifos/vault999` |
| Trinity 33 (final repo map) | `/root/.agents/skills/KERNEL-trinity-33/SKILL.md` |
| Federated skill catalog | `/root/AAA/skills/SKILL_INDEX.md` |
| Live health & tools | `curl :8088/health` · `curl :8088/tools/list` |

---

## 14. Federation IA rule (the Zen)

> **Pages are for humans. Contexts are for agents.**
>
> Don't make the user think about the system. Make the system think about the user.

The federation surface obeys three concurrent laws. Every agent adding or restructuring a landing page must satisfy all three.

### 14.1 Three-click rule (structural)

No site is nested more than **3 clicks** from its entry domain. Measured from `/`, every user-reachable path must be reachable in ≤3 navigation steps.

```bash
make click-depth-audit    # rule as stated (≤3)
make zen-check           # strict (≤2) — use when adding deep content
make prove               # includes click-depth-audit
```

The audit script lives at `/root/scripts/audit_click_depth.sh`. It scans `/root/arif-sites/sites/` against the 6 entry domains (`arif-fazil.com`, `arifos.arif-fazil.com`, `aaa.arif-fazil.com`, `geox.arif-fazil.com`, `wealth.arif-fazil.com`, `well.arif-fazil.com`) and fails closed (non-zero exit) on any violation.

If you add a path deeper than 3 clicks, surface it on the home page or flatten the directory structure.

### 14.2 Verbs over nouns (informational)

Every page answers exactly one question. Navigation labels are **verbs** (Explore, Analyze, Reconstruct, Challenge, Compare, Ask) — never nouns (Data, Reports, Documents, Maps, Tools).

```
Bad:  Data / Reports / Documents / Maps / Models
Good: Explore / Compare / Analyze / Challenge / Predict / Investigate
```

Lead with intent cards on the home page. Push the IA (nouns) below the verbs. The IA is the map; the verbs are the entry points.

### 14.3 Three-second answer pattern (the Sacred Navigation Law)

Every page — on every navigation — must answer within 3 seconds:

| Question | Meaning |
|---|---|
| **Where am I?** | Breadcrumb or sticky pulse showing `Domain · Section` |
| **Why should I care?** | One-line value pulse (e.g. "Evidence preserved. Failure = HOLD.") |
| **What can I do next?** | Verb-led CTAs or intent cards |

Use a sticky `.zen-pulse` horizontal bar near the top of every page. Pattern:

```html
<div class="zen-pulse">
  <div class="zp-item"><span class="zp-ask">Where am I?</span><span class="zp-val">GEOX · Workbench</span></div>
  <div class="zp-item"><span class="zp-ask">Why care?</span><span class="zp-val gold">...</span></div>
  <div class="zp-item"><span class="zp-ask">What next?</span><span class="zp-val">Pick a verb ↓</span></div>
</div>
```

### 14.4 Show less, reveal more

The top 20% of capability is visible above the fold. The remaining 80% hides behind `<details>` blocks. Users expand only what interests them.

```html
<details class="zen-reveal">
  <summary>Operational signal · click to expand</summary>
  <div class="reveal-body">…hidden content…</div>
</details>
```

### 14.5 Two surfaces — Human + Agent

The same system must serve both:

- **Human Surface** — narrative, beautiful, outcome-oriented. Verbs. Intent cards. 3-second pulse.
- **Agent Surface** — machine-readable, JSON, MCP, schemas. `llms.txt`, `CANONICAL_PUBLIC_SURFACE.json`, `/mcp` endpoint, structured contracts.

If you build only the Human Surface, agents cannot reach the system. If you build only the Agent Surface, humans will not find it. Both are required.

### 14.6 Reference implementation

GEOX home (`/root/GEOX/static/index.html`) is the canonical example. It satisfies all four laws:

- Sticky `.zen-pulse` answers 3 questions in 3 seconds
- 6 intent cards (verbs) above the IA
- Sovereign Bridge + Health collapsed into `<details>`
- 4-Surface Hub renamed "Where things live" and pushed below the verbs

When in doubt: read GEOX home, copy the pattern.

---

## 15. One rule

> **Probe before act.** `:port/health` and `tools/list` are truth. This file is a pointer, not a constitution. The constitution runs on port 8088.
>
> **Sealed where Arif has agreed, reversibly expanded where he has not.** When in doubt: HOLD.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given. This file is a living pointer. Update after every structural change to the federation layout.*
