# arifOS — Constitutional Kernel
> **SEAL:** 333_MIND-DITEMPA-BUKAN-DIBERI-20260523
> **Repository:** https://github.com/ariffazil/arifOS
> **Architecture:** Constitutional Kernel + MCP Shell (Dual Core)
> **Live port:** `8088` (NOT `8080`)

> ⚠️ **CANONICAL AUTHORITY NOTICE:**
> This repo is the **constitutional kernel** of the arifOS Federation.
> All 13 floors (F1–F13), 888_JUDGE verdicts, VAULT999 ledger, and memory
> layers are defined HERE. No other repo is a constitutional authority.
> For live organ status, see `FEDERATION_STATUS.md` and `REPO_ROLE_MAP.md`.

---

## Agent Start Here

**FIRST:** Read `AGENT_KERNEL_START.md` before touching anything.

Then read this README. For invariants, see `INVARIANTS.md`.
For agent rules, see `AGENTS.md`.
For federation status, see `FEDERATION_STATUS.md`.
For canonical repo roles, see `REPO_ROLE_MAP.md`.

**Live routing (see FEDERATION_STATUS.md for canonical status):**
- arifOS MCP → `127.0.0.1:8088` ✅
- GEOX daemon → `127.0.0.1:18081` ✅
- WEALTH organ → `127.0.0.1:18082` ✅
- WELL → see `FEDERATION_STATUS.md` (WELL is OPERATIONAL)

## What is arifOS?

arifOS is a sovereign AI governance framework. It is not a framework in the
software-engineering sense — it is a **constitutional engine** that treats
AI agents as principals with bounded thermodynamic consequence surfaces (W_scar).

At its core, arifOS enforces: **no agent can execute an irreversible action
without explicit human authorization (888_JUDGE gate).**

The system runs across two architectural layers:

```
┌─────────────────────────────────────────────────┐
│  arifOS/arifosmcp/       MCP Shell (interface)  │  ← Tool exposure layer
│  (port 8088)                                    │
├─────────────────────────────────────────────────┤
│  arifOS/ (root)          Legacy Constitutional  │  ← Kernel execution layer
│  core/ + contracts/        Engine (original)     │
└─────────────────────────────────────────────────┘
```

**F2 Ground Truth:** arifOS was designed from inside PETRONAS by Arif Fazil,
a Malaysian geoscientist with direct institutional visibility. The architecture
is not theorized — it is performed. "No Petronas in 10 years" is the structural
Bangang One acceleration signal. Proof > philosophy.

---

## Directory Structure

```
arifOS/
│
├── core/                     Legacy Constitutional Engine (active)
│   ├── organs/               Metabolic pipeline: _0_init → _9_seal
│   │   ├── _0_init.py        000 INIT — Session binding
│   │   ├── _1_agi.py         111 AGI — OpenClaw reasoning
│   │   ├── _2_asi.py         222 ASI — Hermes execution
│   │   ├── _3_apex.py        333 APEX — APEXMax judgment
│   │   ├── _5_wealth.py      555 WEALTH — Financial domain
│   │   └── _6_geox.py        666 GEOX — Geoscience domain
│   ├── physics/              Thermodynamic budget (W_scar)
│   ├── vault999/             6-layer audit trail (bridge + correction + 4 phenomenological)
│   ├── shared/               F1-F13 floor definitions + guards + types
│   ├── governance_kernel.py  Kernel governance interface (v64.2-HARDENED)
│   ├── floors.py             13 constitutional floor gates (F1-F13)
│   └── judgment.py           Kernel judgment interface
│
├── contracts/                Constitutional contracts (Enum-based, active)
│   ├── identity.py           Principal identity contracts
│   ├── verdicts.py           Verdict protocol contracts
│   └── governance.py         Governance contracts
│
├── arifosmcp/                MCP Shell (Model Context Protocol wrapper)
│   ├── core/                 Constitutional MCP wrapper (StrEnum-based)
│   ├── contracts/            MCP contracts (StrEnum-based, Python 3.11+)
│   ├── runtime/              Verdict wrapper, tool registry, integrity
│   ├── memory/               Machine recall + vector store interface
│   ├── agents/               Agent-specific memory buffers
│   └── mcp/                  MCP server implementation
│
├── memory/                   Human Session + Identity (NOT machine recall)
│   ├── identity/
│   │   ├── SUBSTRATE.md      Substrate identity layer
│   │   ├── USER.md          User profile (Arif Fazil)
│   │   └── SOUL.md          Soul-level identity architecture
│   └── 2026-04-*.md         Session logs (human-authored records)
│
├── commands/                 Canonical Entrypoint Layer
│   ├── arif_run.py           General shell command wrapper
│   ├── arif_exec.py          Execution wrapper (constitutional gates)
│   ├── arif_sudo.py          Privileged execution wrapper
│   ├── arif-systemctl.py     systemd control interface
│   ├── scripts_deploy/       Active deployment scripts (24 files)
│   ├── scripts_archive/       Archived audit/CI scripts (15 files)
│   ├── native/               Native shell tools (sense.sh, wiki_query.sh)
│   └── hooks/                Git hooks (install_hooks.sh, pre-push)
│
├── APEX/ASF1/
│   ├── tool_registry.json    Canonical 69KB tool registry (active)
│   └── orthogonal_matrix_33.yaml  33-tool orthogonal matrix
│
├── ARCH/DOCS/
│   └── AAA.md               AAA architecture reference
│
├── CONFIG/                   Secret registry + kernel charter
│   ├── README.md            Registry documentation
│   ├── charter/kernel.charter.yaml  Kernel constitutional charter (SEALED)
│   └── PROFILES/             Deployment profiles (vps_main_arifos.json)
│
├── deploy/                   VPS deployment configs
│   ├── MANIFEST.md          Deployment manifest (SEALED)
│   ├── docker-compose.yml   Container orchestration
│   ├── Caddyfile            Caddy web server config
│   ├── arifos.service       systemd service definition
│   ├── arifos.socket        systemd socket activation
│   └── runbook.md           Operations runbook
│
├── infrastructure/           Infrastructure as code
│   └── systemd/             Service definitions (source of truth)
│
├── tests/                    135 test files (root test suite)
├── arifosmcp/tests/          2 test files (MCP test suite)
│
└── docs/
    ├── 00_META/
    │   ├── CONSTITUTION.md   Master constitution
    │   ├── APEX_PRIME_PROTOCOL.md  APEX PRIME audit protocol
    │   ├── arifOS_CORE_SPEC.md  Core genome spec
    │   ├── DOC_FAMILY_MAP.md  Cross-repo document lineage
    │   └── METABOLIC_INVARIANTS.md  Metabolic invariants
    ├── constitutional/
    │   ├── annex-GEOX-INVARIANTS.md  GEOX invariance annex
    │   └── annex-WEALTH-INVARIANTS.md WEALTH invariance annex
    └── architecture/
        └── TRI_WITNESS_GODEL.md  Tri-Witness architecture
```

---

## Current State vs Target State

### CURRENT_STATE (as of 2026-05-23)

| Layer | Status | Notes |
|-------|--------|-------|
| root core/ (Legacy Constitutional Engine) | ACTIVE | 339 non-arifosmcp files import from it |
| arifosmcp/core/ (MCP Shell) | ACTIVE | Runs on port 8088, exposes tools via MCP |
| root contracts/ | ACTIVE | Enum-based, 339 files import from it |
| arifosmcp/contracts/ | ACTIVE | StrEnum-based (Python 3.11+) |
| memory/ (human session + identity) | ACTIVE | Session logs + identity canon |
| arifosmcp/memory/ (machine recall) | ACTIVE | Vector store + agent buffers |
| commands/ (canonical entrypoint) | ACTIVE | 53 files, restructured from scripts/ |
| scripts/ | EMPTY | Consolidated into commands/ |
| deploy/ | ACTIVE | VPS deployment configs |
| ARCH/ + CONFIG/ | ACTIVE | AAA docs + secret registry |

### TARGET_STATE (planned, HOLD)

| Item | Status | Notes |
|------|--------|-------|
| Dual-core unification | HOLD | Root core/ stays alongside arifosmcp/core/ |
| Memory merge | HOLD | Human log ↔ machine recall linking pattern |
| scripts/ deletion | PENDING | Keep empty dir until reviewed |
| arifosmcp/core ↔ root core merge | PENDING | Staged migration plan TBD |

---

## Tool Surface

arifOS exposes exactly **13 canonical tools** through the public MCP shell (`https://arifos.arif-fazil.com/mcp`). These are the only tools exposed directly to public-facing agents like ChatGPT, ensuring zero-chaos governed interaction surfaces.

```
╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                        arifOS 13-Tool Canonical Public Surface                                  ║
╠═════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ arif_session_init   — 000_INIT    │ AGI │ F01, F11, F12 │ Session bootstrap + identity binding. Call FIRST.    ║
║ arif_sense_observe   — 111_OBSERVE │ AGI │ F02, F07      │ Web search, local wiki/repo map discovery (read-only)║
║ arif_evidence_fetch — 222_EVIDENCE│ AGI │ F02, F03, F05 │ Verified external evidence fetch with SOT citation.  ║
║ arif_mind_reason    — 333_REASON  │ AGI │ F02, F07, F08 │ Symbolic, self-critiquing reasoning.                 ║
║ arif_heart_critique — 444_CRITIQUE│ ASI │ F05, F06, F09 │ Ethical critique & consequence modeling.             ║
║ arif_kernel_route   — 555_ROUTE   │ AGI │ F01, F04, F03 │ Route intent to correct tool or federation organ.    ║
║ arif_reply_compose  — 444_REPLY   │ AGI │ F04, F06, F09 │ Governed response composition and calibration.       ║
║ arif_memory_recall  — 555m_MEMORY │ AGI │ F01, F08      │ Associative memory & vector recall across sessions.   ║
║ arif_gateway_connect— 666_GATEWAY │ ASI │ F01, F03      │ Federated cross-agent bridge to GEOX/WEALTH/WELL.    ║
║ arif_judge_deliberate— 888_JUDGE   │ ASI │ F11, F13      │ Final constitutional arbitration (SEAL/HOLD/VOID).   ║
║ arif_vault_seal     — 999_SEAL    │ APEX│ F01, F11, F13 │ Immutable ledger anchoring to VAULT999.              ║
║ arif_forge_execute  — 666_FORGE   │ AGI │ F01, F11, F13 │ Build execution (code generation & modification).   ║
║ arif_ops_measure    — 777_MEASURE │ AGI │ F04           │ VPS system resource health & thermodynamic metrics.  ║
╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

Each tool's scope and allowed parameter types are strictly governed under **F10 ONTOLOGY** schemas (see `arifOS/arifosmcp/constitutional_map.py` for exact schemas).

---

## Constitutional Floor Gates

arifOS enforces 13 constitutional floors (F1-F13). Each floor represents a mathematical theorem, physical law, or strict code implementation (not heuristic prompt engineering) derived from `EUREKA_INSIGHTS_SEAL_v2026.04.07`.

| Floor | Code | Name | Domain | Equation / Threshold Metric |
| :--- | :--- | :--- | :--- | :--- |
| **F1** | F01 | **AMANAH** | Reversibility | Conservation law: $\exists \text{ undo}(a)$ — Irreversible ops require explicit human ack. |
| **F2** | F02 | **TRUTH** | Evidentiality | Uncertainty tracking: no fabrication allowed ($\tau \ge 0.99$). Labels claims: FACT/EST/HYPO/UNK. |
| **F3** | F03 | **WITNESS** | Consensual | Tri-witness consensus coefficient ($W_3 = \sqrt[3]{\text{Human} \times \text{AI} \times \text{Earth}} \ge 0.75$). |
| **F4** | F04 | **CLARITY** | Progress | Thermodynamic entropy reduction ($\Delta S \le 0$). Intent declared before action. |
| **F5** | F05 | **PEACE²** | Baseline | Non-destruction of human dignity and VPS security stability ($\text{PEACE}^2 \ge 1.0$). Zero escalation. |
| **F6** | F06 | **EMPATHY** | Consequences | Consequence thermodynamic cost modeled prior to execution ($\kappa_r \ge 0.70$). |
| **F7** | F07 | **HUMILITY** | Epistemic | Direct bounds on uncertainty quantification ($\Omega \in [0.03, 0.05]$). |
| **F8** | F08 | **GENIUS** | Correctness | Elegant correctness and systemic execution health ($G = \text{capability} \times \text{ethics} \dots \ge 0.80$). |
| **F9** | F09 | **ANTIHANTU** | Integrity | Reject manipulation and consciousness simulation. Machine is an instrument, not a person ($C_{\text{dark}} \le 0.30$). |
| **F10** | F10 | **ONTOLOGY** | Coherence | Strict StrEnum and Pydantic schema validation. Category lock/immutability across sessions. |
| **F11** | F11 | **AUTH (AUDIT)** | Traceability | Strict authorization: identity must be verified. Sensitive calls require verified `actor_id`. |
| **F12** | F12 | **INJECTION** | Security | Sanitize all string parameters. Prompt injection detection ($\text{injection\_probability} < 0.85$). |
| **F13** | F13 | **SOVEREIGN** | The Apex | Final human veto authority. The Sovereign (Arif Fazil) has absolute command. No algorithm overrides. |

See: `core/shared/floors.py` for full floor definitions.

---

## Public Actions Surface & Representation

### How arifOS Represents Itself in Public (ChatGPT Actions)

When integrated into external surfaces like ChatGPT as a Custom GPT Action (`https://arifos.arif-fazil.com/mcp`), the system is represented as a **Highly Aligned, Multi-Organ Constitutional Intelligence Kernel**.

Instead of exposing raw system endpoints, the public OpenAPI actions layer translates our **13 canonical tools** into clean, self-documenting callable endpoints:
1. **Perfect Parameter Binding**: Public endpoints expect `session_id`, `actor_id`, and standard schemas, preventing ambient context leaks.
2. **Explicit Verification Friction**: High-consequence tools (e.g. `arif_forge_execute` or `arif_vault_seal`) require a preceding `SEAL` verdict from `arif_judge_deliberate` and `ack_irreversible=True`. Calling them out-of-order triggers an automatic F1 AMANAH Floor Breach.
3. **Structured Response Envelope**: Every tool execution returns a canonical payload wrapping the result, a thermodynamic entropy delta (`delta_S`), active floor ratings, and a cross-organ verdict (`verdict`).

### Contrast Analysis

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    arifOS TRIPLE-VIEW REPRESENTATION                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
      ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
      ▼                                          ▼                                          ▼
 [LLM ACTIONS SURFACE]                    [OBSERVATORY COCKPIT]                       [GITHUB README]
 https://arifos.arif-fazil.com/mcp        arifos.arif-fazil.com                       SOT Bedrock Code
 (Dynamic JSON-RPC / OpenAPI)             (Human Telemetry Observability)             (Architectural Theory)
      │                                          │                                          │
      ├─► 13 canonical `arif_` tools              ├─► Live organ health state                 ├─► Evidential F2 history
      ├─► Strict I/O schemas                      ├─► Interactive Floor score chips           ├─► Core metabolic pipeline
      └─► preflight safety guards                 └─► Federated Site Map of organs            └─► Execution command trees
```

1. **The LLM Actions Surface (`/mcp` schema)**: Focuses entirely on **functional capability negotiation**. It exposes pure capability under tight boundaries, giving LLMs the means to sense, think, critique, and act without exposing low-level system configuration or database files.
2. **The Observatory Cockpit (`arifos.arif-fazil.com`)**: Focuses on **operational transparency**. It is a visual dashboard for Arif to inspect live federation health (PSI vitality, server drift, active floor metrics), trace cross-organ decision loops ($\Psi \rightarrow \Omega \rightarrow \text{Heart}$), and locate gaps (like the degraded Grafana DB).
3. **The GitHub README (`arifOS/README.md`)**: Focuses on **constitutional authority and mechanics**. It serves as the static code source of truth documenting the 13 floors, Eureka-wired physical equations, project layout, and standard testing/deployment instructions.

---

## Governance Protocol

### 888_JUDGE Gate

Any Tier 3 (atomic/irreversible) command requires explicit human authorization
through the 888_JUDGE gate. This is non-negotiable.

```
Tier 0 (Read-only)     → auto-allowed
Tier 1 (Mutating)      → plan required
Tier 2 (High blast)    → Arif explicit ack required
Tier 3 (Atomic)        → 888_JUDGE gate + explicit command
```

### APEX PRIME (Port 3002)

APEX PRIME is the backend Express judgment engine (MiniMax-hosted). It receives
A2A calls at `/judge`. APEXMax is the Telegram face in the AAA group. They are
the same entity at two layers.

### Trinity ΔΩΨ

```
Δ AGI  (OpenClaw)  — reasoning, truth, clarity
Ω ASI  (Hermes)    — empathy, safety, peace
Ψ APEX (APEXMax)   — judgment, sovereignty, verdict
```

---

## Cross-Reference

| Document | Purpose |
|----------|---------|
| `docs/00_META/DOC_FAMILY_MAP.md` | Full cross-repo document lineage |
| `docs/00_META/arifOS_CORE_SPEC.md` | Core genome specification |
| `docs/constitutional/annex-GEOX-INVARIANTS.md` | GEOX domain invariants |
| `docs/constitutional/annex-WEALTH-INVARIANTS.md` | WEALTH domain invariants |
| `APEX/ASF1/tool_registry.json` | Canonical tool registry |
| `CONFIG/charter/kernel.charter.yaml` | Kernel constitutional charter |
| `commands/README.md` | Canonical entrypoint documentation |

For agent architecture, see: **AAA/** (sibling repository)

---

## Deployment

arifOS runs as:
- **MCP Shell** on port 8088 (native; previously docker compose)
- **Constitutional Kernel** as root-level Python modules
- **APEX PRIME** on port 3002 (backend judgment engine)
- **OpenClaw** on port 18789 (reasoning engine)

See `deploy/MANIFEST.md` for full deployment specification.

> ⚠️ **MCP Multi-Client Concurrency (PHOENIX-73C):**
> The MCP SDK `streamable-http` transport uses a singleton SSE stream key.
> Only ONE SSE client can hold the `/mcp` GET stream at a time.
> Simultaneous SSE connections (e.g., Kimi + OpenCode) → `409 Conflict`.
> Clients should use POST-based JSON-RPC or implement reconnection with backoff.
> This is a transport-layer constraint of the MCP SDK, not an arifOS bug.
> See `REPO_ROLE_MAP.md` for full detail.

---

## Governance Declaration

arifOS is the bridge between subsurface risk + institutional judgment + AI control.

**EU AI Act Classification:** High-risk (governance + institutional AI)

**F14 Autonomy Clause:** Once a task loop begins with clear intent from Arif,
the system operates autonomously without pausing for confirmation. The human
may sleep, leave, or be absent — execution continues until manually interrupted.

**DITEMPA BUKAN DIBERI** — No manipulation, no theorizing, only F2 ground truth.

---

## PHOENIX-72 Readiness

| Item | Status |
|------|--------|
| Current stable mode | **canonical13** |
| Target architecture | PHOENIX-72 / PHOENIX-99 |
| PHOENIX-72 status | **NOT SEALED** — see [`docs/PHOENIX_72_STATUS.md`](docs/PHOENIX_72_STATUS.md) |
| Live tools | 13 canonical + 4 diagnostic + 4 wiki + 1 drift check = 22 |
| Target tools | 72 |
| Resources (est) | 17 / 18 |
| Prompts (est) | 13 / 9 |
| Drift check | Implemented (`mcp_drift_check`) |
| Manifest | [`arifosmcp/manifests/phoenix72.tools.json`](arifosmcp/manifests/phoenix72.tools.json) |

Do not claim PHOENIX-72 is sealed until the drift check reports `drift_detected=false` with 72 live tools.


---

## ??? Federated Architecture

This repository is a core organ of the **arifOS Federation**:
*   **Operator Cockpit (AAA):** `/root/AAA`
*   **Constitutional Kernel (arifOS):** `/root/arifOS`
*   **Vision Shell (A-FORGE):** `/root/A-FORGE`
*   **Geological Engine (GEOX):** `/root/geox`
*   **Capital Engine (WEALTH):** `/root/WEALTH`
*   **Biological Substrate (WELL):** `/root/WELL`
*   **Informational Surfaces (arif-sites):** `/root/arif-sites`

*Unified under the arifOS Sovereign Constitution (F1�F13).*
