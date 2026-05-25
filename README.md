# arifOS — Constitutional Kernel
> **SEAL:** 333_MIND-DITEMPA-BUKAN-DIBERI-20260523
> **Repository:** https://github.com/ariffazil/arifOS
> **Architecture:** Constitutional Kernel + MCP Shell (Dual Core)
> **Live port:** `8088` (NOT `8080`)

---

## Agent Start Here

**FIRST:** Read `AGENT_KERNEL_START.md` before touching anything.

Then read this README. For invariants, see `INVARIANTS.md`.
For agent rules, see `AGENTS.md`.

**Live routing (VERIFIED 2026-05-25):**
- arifOS MCP → `127.0.0.1:8088` ✅
- GEOX daemon → `127.0.0.1:18081` ✅
- WEALTH organ → `127.0.0.1:18082` ✅
- WELL → disabled ⛔

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

arifOS exposes **13 canonical tools** through the MCP shell. These are the
only tools available to all agents — no exceptions.

```
╔══════════════════════════════════════════════════════════╗
║              arifOS 13-Tool Canonical Surface           ║
╠══════════════════════════════════════════════════════════╣
║ 000 INIT   — Session binding + identity verification      ║
║ 111 AGI    — OpenClaw reasoning engine                  ║
║ 222 ASI    — Hermes execution layer                       ║
║ 333 APEX   — APEXMax judgment engine                     ║
║ 444 ROUT   — Operational execution                        ║
║ 555 WEALTH — Financial domain reasoning                  ║
║ 666 GEOX   — Geoscience domain reasoning                  ║
║ 777 VAL    — Value computation + invariant checks          ║
║ 888 JUDGE  — Human authorization gate (irreversible ops) ║
║ 999 SEAL   — Verdict emission + audit trail              ║
║ 000_α META — Metadata operations                         ║
║ 111_α SYS  — System introspection                         ║
║ 222_α REG  — Registry operations                         ║
╚══════════════════════════════════════════════════════════╝
```

Full tool registry: `APEX/ASF1/tool_registry.json` (69KB canonical registry)
Orthogonal matrix: `APEX/ASF1/orthogonal_matrix_33.yaml`

---

## Constitutional Floor Gates

arifOS enforces 13 constitutional floors (F1-F13). Each floor has a
specific gate function that must pass before execution proceeds.

| Floor | Name | Gate Type | Description |
|-------|------|-----------|-------------|
| F1 | INIT | Session | Session binding verification |
| F2 | F2_TRUTH | Evidential | F2 ground truth verification |
| F3 | IDENTITY | Principal | Principal identity confirmation |
| F4 | JURISDICTION | Domain | Domain jurisdiction check |
| F5 | BUDGET | Thermodynamic | W_scar budget allocation |
| F6 | TIMELINESS | Temporal | Temporal constraint check |
| F7 | SEMANTIC_GATE | Intent | F14 semantic intent classification |
| F8 | EXECUTION_GATE | Tier | Command tier classification (T0-T3) |
| F9 | VAL_GATE | Value | Value alignment verification |
| F10 | GOVERNANCE | Constitutional | Constitutional compliance |
| F11 | WITNESS | Tri-Witness | Tri-Witness coherence check |
| F12 | TRI_GODEL | Gödel | Gödel incompleteness boundary |
| F13 | F13_FINAL | Seal | Final seal before execution |

See: `core/shared/floors.py` for full floor definitions.

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

---

## Governance Declaration

arifOS is the bridge between subsurface risk + institutional judgment + AI control.

**EU AI Act Classification:** High-risk (governance + institutional AI)

**F14 Autonomy Clause:** Once a task loop begins with clear intent from Arif,
the system operates autonomously without pausing for confirmation. The human
may sleep, leave, or be absent — execution continues until manually interrupted.

**DITEMPA BUKAN DIBERI** — No manipulation, no theorizing, only F2 ground truth.


---

## ??? Federated Architecture

This repository is a core organ of the **arifOS Federation**:
*   **Operator Cockpit (AAA):** [C:\ariffazil\AAA](file:///C:/Users/User/../ariffazil/AAA)
*   **Constitutional Kernel (arifOS):** [C:\ariffazil\arifOS](file:///C:/Users/User/../ariffazil/arifOS)
*   **Vision Shell (A-FORGE):** [C:\ariffazil\A-FORGE](file:///C:/Users/User/../ariffazil/A-FORGE)
*   **Geological Engine (GEOX):** [C:\ariffazil\geox](file:///C:/Users/User/../ariffazil/geox)
*   **Capital Engine (WEALTH):** [C:\ariffazil\wealth](file:///C:/Users/User/../ariffazil/wealth)
*   **Biological Substrate (WELL):** [C:\ariffazil\well](file:///C:/Users/User/../ariffazil/well)
*   **Informational Surfaces (arif-sites):** [C:\ariffazil\arif-sites](file:///C:/Users/User/../ariffazil/arif-sites)

*Unified under the arifOS Sovereign Constitution (F1�F13).*
