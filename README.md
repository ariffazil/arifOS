<!-- SOT-MANIFEST
federation_release: v2026.09.13
last_verified: 2026-09-13T06:32:45+00:00
live_commit: 4f4554597 (feat(memory): enforce canonical admissibility gate and sanctuary denylist)
source_commit: 4f4554597
tools_exposed_via_mcp: 8 (canonical public verbs)
floors_active: 13 (F1–F13, active)
federation_schema: 2.0.0
organs: 10 (arifOS:8088, A-FORGE:7071/7072, AAA:3001, GEOX:8081, WEALTH:18082, WELL:18083, arifFlow:7073, FED:7074, FRAME:18085, i-ARIF:18095)
vault999: healthy (155K+ records, append-only)
apex_zen: A2A delegates ⊥ MCP equips ⊥ ACT mutates ⊥ arifOS governs ⊥ F13 decides
truth_rule: live :8088/health + tools/list beat any static count in prose
generated_by: scripts/update_readme_sot.py — numeric fields are re-stamped, never hand-maintained
holds: Merkle signing lane · WELL biometrics · medical purge (Pilihan A)
-->

# arifOS — An Open-Source Governance Decision Point for AI Agent Actions

**arifOS evaluates consequential AI actions against policy floors and returns a verdict _before_ execution occurs.**

When an AI agent proposes to write, delete, deploy, or spend, arifOS inserts an independent judgment step: the agent proposes, arifOS evaluates, a decision is reached, and only then does execution proceed. Every verdict is recorded with full evidence in an append-only ledger.

**This is not an AI model. It is not an agent framework. It is a policy decision point — the layer between "agent wants to act" and "action occurs."**

**What arifOS is not:** not an AI model · not an agent framework · not an execution engine (it judges; A-FORGE executes) · not a substitute for authentication, sandboxing, or legal review.

---

## The Problem

AI agents that act are also certifying their own actions. There is no independent authority evaluating proposals against safety, compliance, and policy constraints before execution occurs.

## The Solution

```
  Agent proposes action
         │
         ▼
  ┌─────────────────┐
  │   arifOS Kernel  │  Evaluates against 13 constitutional floors
  │     (:8088)      │  Records evidence chain
  └────────┬────────┘
           │
    ┌──────┼──────┬──────────┐
    ▼      ▼      ▼          ▼
  SEAL    HOLD   SABAR     VOID
  (go)   (wait)  (patience) (blocked)
    │      │
    ▼      ▼
  Execute  Human
  via      reviews
  A-FORGE
    │
    ▼
  Receipt in VAULT999
  (append-only ledger)
```

**The judge never executes. The executor never certifies.**

### Federation in One Line

> **arifOS decides. AAA routes. A-FORGE acts. VAULT999 witnesses.**

| Plane | Organ | Role |
|-------|-------|------|
| Governance | arifOS | Policy Decision Point — evaluates proposals against constitutional floors |
| Control | AAA | Intent classification and routing to the correct organ |
| Execution | A-FORGE | Governed mutation — leases, gates, receipts |
| Witness | VAULT999 | Hash-chained append-only ledger — tamper-evident record of every verdict and receipt |

Authority remains separated at every stage. No single component proposes, judges, executes, and witnesses the same action.

---

## Quick Start

> Requires **Python 3.12+** (supported range: 3.12–3.14; see `pyproject.toml`).

### Install

```bash
pip install arifos
```

### Run the kernel

```bash
# Start the MCP server (console script; `arifos` is an equivalent alias)
arifos-mcp

# Equivalent module form
python -m arifosmcp.runtime

# Check health — the kernel defaults to port 8088
curl http://localhost:8088/health
```

### Connect an MCP client

Point any MCP client at the Streamable HTTP endpoint:

```
http://localhost:8088/mcp
```

An illustrative `tools/call` for judgment:

```jsonc
// method: tools/call
{
  "name": "arif_judge",
  "arguments": {
    "candidate": "Write file /data/report.csv with production data",
    "action_tier": "standard"
  }
}
// → SEAL | HOLD | SABAR | VOID with evidence chain
```

For a guided walkthrough, start with [docs/START_HERE.md](./docs/START_HERE.md).

---

## Core Concepts

### Four Verdicts

| Verdict | Meaning | Plain English | What happens |
|---------|---------|---------------|-------------|
| **SEAL** | Authorized under stated conditions | Go | Proceed to execution |
| **HOLD** | Insufficient evidence or human approval needed | Wait for human | Pause; await human decision |
| **SABAR** | Not yet decidable — reality hasn't finished speaking | Defer — more evidence needed | Wait; distinct from HOLD |
| **VOID** | Blocked by a constitutional floor | Blocked | Stop; constraint must be resolved |

### 13 Constitutional Floors (F1–F13)

Every proposal is evaluated against 13 non-compensatory policy constraints (F1–F13). Floors are never averaged or traded off — a failure propagates into the verdict (HOLD, SABAR, or VOID).

| Floor | Name | What it checks |
|-------|------|---------------|
| F1 | AMANAH | Reversibility — no irreversible action without consent |
| F2 | TRUTH | Evidence-grounded claims — uncertainty-banded |
| F3 | WITNESS | Three-way consistency (theory, code, intent) |
| F4 | CLARITY | Transparent intent |
| F5 | PEACE² | Non-destructive power — block harm and extraction |
| F6 | MARUAH | Dignity — protect the weakest stakeholder |
| F7 | HUMILITY | Acknowledge limits |
| F8 | GENIUS | Elegant correctness (G ≥ 0.80) |
| F9 | ANTI-HANTU | No consciousness or emotion claims |
| F10 | ONTOLOGY | Structural coherence |
| F11 | AUDIT | Every decision logged, inspectable, attributable |
| F12 | INJECTION | Input sanitization |
| F13 | SOVEREIGN | Human veto is absolute |

### VAULT999 (Append-Only Audit Ledger)

Every verdict, evidence chain, and execution receipt is recorded in VAULT999 — a hash-chained, append-only JSONL ledger (live record count in the header manifest above, re-stamped by `scripts/update_readme_sot.py`). Designed for compliance auditing, forensic review, and governance proof. Chain verification tooling ships in `scripts/verify_vault_chain.py`.

---

## Architecture

```
arifOS Federation — 4 Constitutional Planes

    ┌─────────────────────────────────────────────┐
    │         Governance Plane (arifOS :8088)      │
    │    Policy evaluation · Constitutional floors │
    └──────────────────────┬──────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────┐
    │           Control Plane (AAA :3001)          │
    │    Intent classification · Routing · State   │
    └──────────────────────┬──────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────┐
    │        Execution Plane (A-FORGE :7071/7072)  │
    │    Governed mutation · Leases · Receipts     │
    └──────────────────────┬──────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────┐
    │     Witness Plane (VAULT999 + FRAME :18085)  │
    │    Append-only ledger · Drift detection      │
    └─────────────────────────────────────────────┘
```

```
arifOS Federation — 10 Organs

arifOS (:8088)     Constitutional judgment kernel
AAA (:3001)        Intelligence routing, state plane, skill catalog
A-FORGE (:7071/7072) Execution after authorization
GEOX (:8081)       Earth sciences domain evidence
WEALTH (:18082)    Capital and financial intelligence
WELL (:18083)      Human and machine vitality observation
arifFlow (:7073)   Metabolic ledger daemon (FQ monitoring, receipt ingestion)
FED (:7074)        Federation routing gateway (multi-provider LLM)
FRAME (:18085)     Independent observer, drift detection, evidence gathering
i-ARIF (:18095)    Seal B synthesis engine

ARIF vetoes. arifOS judges. AAA routes. A-FORGE executes. FRAME witnesses. FED routes.
```

arifOS is the kernel. The other organs are supporting infrastructure. GEOX is the primary reference implementation, demonstrating governance in high-consequence, uncertainty-heavy workflows. FRAME is the independent observer — its output is evidence, never a verdict.

---

## MCP Interface

The kernel exposes 8 canonical MCP verbs over Streamable HTTP (protocol `2026-07-28`, backward-compatible to `2024-11-05`):

| Verb | Purpose |
|------|---------|
| `arif_init` | Establish session context and actor identity |
| `arif_observe` | State observation and gap detection |
| `arif_think` | Constitutional reasoning against floors |
| `arif_route` | Route intent to the appropriate federation organ |
| `arif_memory` | Query and manage institutional memory |
| `arif_judge` | Evaluate a proposal and return a verdict |
| `arif_forge` | Dispatch authorized actions for execution |
| `arif_seal` | Seal a completed action chain with evidence and receipt |

> `arif_forge` is a **governed dispatch** verb: it routes authorized actions toward the execution organ (A-FORGE) and mutates only after a SEAL verdict. The kernel itself does not perform the underlying mutation. The judge never executes; the executor never certifies.

---

## Verification Status

> The header manifest is regenerated from the live kernel by `scripts/update_readme_sot.py` (run before release commits). Last stamp: `last_verified` above.

| Surface | Status | Evidence |
|---------|--------|----------|
| Public repository | Live | GitHub (`ariffazil/arifOS`), AGPL-3.0-only |
| PyPI package | Published `1!2026.8.2` | `pip install arifos` |
| Live kernel | Green | `curl localhost:8088/health` → structured JSON, `service_health: green` |
| MCP interface | 8 tools exposed | Streamable HTTP; protocol `2026-07-28` (back-compat ≥ `2024-11-05`) |
| Floor enforcement | Active — 13/13 pass at last probe | `/health → runtime_floors_status`, `degraded_reasons: []` |
| VAULT999 ledger | Healthy | Hash-chained append-only JSONL; live count in header manifest |
| Source / build / deploy alignment | Verified (commit 4f4554597) | `runtime_drift: false`, `deployment_attestation: aligned` |
| Federation | 10 organs | See Architecture |

## What Is Not Yet Proven

| Gap | Risk |
|-----|------|
| Independent security audit | Adversarial bypass testing not published |
| Third-party evaluation | No external reviewer has published findings |
| Reproducible demo by strangers | Onboarding path not independently tested |
| Enterprise deployment | No production customer reference |
| Standards conformance | MCP/A2A conformance tests not published |
| SBOM and signed releases | Supply chain integrity unverified externally |
| Comparative benchmark | No published comparison against alternative frameworks |

See [SECURITY.md](./SECURITY.md) for the threat model, known gaps, and disclosure policy.

---

## Who Is This For

**Operators** deploying AI agents in regulated environments who need an independent judgment layer between agent proposals and execution.

**Developers** building AI agent systems who want a policy decision point as a service.

**Evaluators and security reviewers** assessing AI governance frameworks.

**Domain builders** adapting governance to specific fields (geoscience, finance, healthcare).

Start here: [docs/START_HERE.md](./docs/START_HERE.md)

---

## Founding Context

arifOS was built by Muhammad Arif bin Fazil, a senior exploration geoscientist who spent his career making decisions where observations are incomplete, interpretations are probabilistic, provenance matters, and irreversible action must be gated. He transferred that discipline into agent runtime governance.

The system is named after its founder and reflects a core belief: **governance is a systems problem, not a model problem.**

---

## Development

```bash
# Clone
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Install (light tier — kernel only)
pip install -e ".[light]"

# Run tests
python -m pytest tests/ -v

# Start the kernel
arifos-mcp   # or: python -m arifosmcp.runtime
```

### Project Structure

```
arifOS/
├── arifosmcp/          # Core kernel package
│   ├── abi/            # Capability registry and floor definitions
│   ├── constitution/   # Constitutional floor implementations
│   ├── kernel/         # Core judgment engine
│   └── VAULT999/       # VAULT999 ledger implementation
├── tests/              # Test suite (pytest — constitutional + integration)
├── scripts/            # Operational tooling (incl. update_readme_sot.py)
├── docs/               # Documentation
│   ├── START_HERE.md   # External reader entry point
│   └── ...
└── pyproject.toml      # Package metadata
```

---

## Sister Repositories

| Repository | Purpose |
|------------|---------|
| [AAA](https://github.com/ariffazil/AAA) | Intelligence routing, state plane, skill catalog, A2A gateway |
| [A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution engine after authorization |
| [GEOX](https://github.com/ariffazil/GEOX) | Earth sciences domain evidence |
| [WEALTH](https://github.com/ariffazil/WEALTH) | Capital and financial intelligence |
| [WELL](https://github.com/ariffazil/WELL) | Human and machine vitality observation |
| [arifFlow](https://github.com/ariffazil/arifFlow) | Metabolic ledger daemon — FQ monitoring, receipt ingestion |
| [FED](https://github.com/ariffazil/fed) | Federation routing gateway (multi-provider LLM via LiteLLM) |
| [FRAME](https://github.com/ariffazil/frame) | Independent observer — drift detection, evidence gathering |
| [i-ARIF](https://github.com/ariffazil/i-arif) | Seal B synthesis engine |

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## Security

See [SECURITY.md](./SECURITY.md) for threat model, known vulnerabilities, and disclosure policy.

---

## License

**AGPL-3.0** — GNU Affero General Public License v3.0.

When deployed over a network, the complete source code must be made available to all users interacting with the service, consistent with AGPL-3.0 terms.

---

**Ditempa Bukan Diberi** — Forged, Not Given.
