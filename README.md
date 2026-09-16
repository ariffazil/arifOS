<!-- SOT-MANIFEST
kernel_release: v2026.08.01
pypi_version: 1!2026.9.1
last_verified: 2026-09-16T16:59:25+00:00
live_commit: 93526c15f (fix(capability_index): D4 data-quality — classify seed at source, canonical serv)
source_commit: 93526c15f
built_commit: 24f1a4f
deployment_drift_status: drift_detected (source != deployed (drift: true) — run deploy-release.sh)
tools_exposed_via_mcp: 8 (canonical public verbs)
tools_internal_superset: 25 (13 hidden verbs — arif_challenge, arif_judge_deliberate, etc.)
floors_active: 13 (F1–F9 + L10–L13, all pass)
federation_schema: 2.0.0
mcp_protocol: 2026-07-28 (back-compat: 2025-11-25, 2025-03-26, 2024-11-05)
organs: 10 (arifOS:8088, A-FORGE:7071/7072, AAA:3001, GEOX:8081, WEALTH:18082, WELL:18083, arifFlow:7073, FED:7074, FRAME:18085, i-ARIF:18095)
vault999: healthy (205K+ records, append-only)
contract_status: 8/8 schemas complete, contract_drift: false
tool_manifest_url: https://arifos.arif-fazil.com/tools.json
apex_zen: A2A delegates ⊥ MCP equips ⊥ ACT mutates ⊥ arifOS governs ⊥ F13 decides
truth_rule: live :8088/health + tools/list beat any static count in prose
generated_by: scripts/update_readme_sot.py — numeric fields are re-stamped, never hand-maintained
holds: Merkle signing lane · WELL biometrics · medical purge (Pilihan A)
seal_readiness_gaps: graphiti=RETIRED_888(2026-09-04) · semantic_floor=off_by_choice(ARIFOS_ML_FLOORS=0) · langfuse=SOVEREIGN_CUTOVER→kabarkan(live)
-->

# arifOS — The Authority Plane of the arifOS Federation

[![Security Audit: Grade A](https://img.shields.io/badge/Security_Audit-Grade_A-2ECC71?style=flat-square)](https://mcp.arif-fazil.com/proof/)
[![MCP Compliance: 148 Rules](https://img.shields.io/badge/MCP_Scanners-148_Rules_Passed-d4a853?style=flat-square)](https://mcp.arif-fazil.com/proof/)
[![Status: Operational](https://img.shields.io/badge/MCP_Gateway-Operational-blue?style=flat-square)](https://mcp.arif-fazil.com/health)
[![Sovereign Boundary: F13](https://img.shields.io/badge/Sovereignty-F13_Enforced-critical?style=flat-square)](https://arif-fazil.com/governance/)
[![MCP Conformance](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/06-mcp-conformance.yml?label=MCP_Conformance&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/06-mcp-conformance.yml)
[![Vault Integrity](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/07-vault-integrity.yml?label=Vault_Integrity&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/07-vault-integrity.yml)
[![Floor Gate](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/floor_gate.yml?label=Floor_Gate&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/floor_gate.yml)
[![Governance](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/governance-gate.yml?label=Governance&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/governance-gate.yml)
[![Runtime Drift](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/08-runtime-drift.yml?label=Runtime_Drift&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/08-runtime-drift.yml)
[![External Witness](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/external-witness.yml?label=External_Witness&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/external-witness.yml)

**arifOS evaluates consequential AI actions against constitutional floors and returns an independent verdict _before_ execution occurs.**

When an AI agent proposes to write, delete, deploy, or spend, arifOS inserts a constitutional judgment step: the agent proposes, arifOS evaluates against F1–F13 floors, a verdict is reached, and only then does execution proceed. Every verdict is recorded with full evidence in an append-only ledger.

In a world where intelligence is abundant, authority becomes the scarce resource. arifOS exists to ensure that judgment remains independent from execution.

**This is not an AI model. It is not an agent framework. It is a constitutional authority system — the layer between "agent wants to act" and "action is permitted."**

**What arifOS is not:** not an AI model · not an agent framework · not an execution engine (A-FORGE executes) · not an attention plane (AAA compresses reality) · not a witness (arifFlow records) · not a substitute for authentication, sandboxing, or legal review.

| Audience | What you get |
|---|---|
| **Human** | A quiet veto: the agent proposes, the kernel records a verdict, you stay sovereign |
| **Agent / A2A** | MCP tools + receipts. You do not get the keys. Protocol: A2A v1.0 (not v1.2) |
| **Institution** | Policy floors F1–F13, VAULT999 audit trail, model-vendor independence |
| **Indexer / Search** | Structured metadata, [`llms.txt`](./llms.txt), [tools.json](https://arifos.arif-fazil.com/tools.json), [`CITATION.cff`](./CITATION.cff) |
| **Machine / MCP** | [Streamable HTTP endpoint](https://mcp.arif-fazil.com/mcp), 8 canonical verbs, schema-validated contracts |
| **Robot / Automation** | CI gates (conformance, vault-integrity, drift), [`Makefile`](./Makefile) targets, [`Dockerfile`](./Dockerfile) |

Live: `https://arifos.arif-fazil.com` · MCP `:8088` · sister organs [GEOX](https://github.com/ariffazil/GEOX) · [A-FORGE](https://github.com/ariffazil/A-FORGE) · [AAA](https://github.com/ariffazil/AAA)

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
| Authority | arifOS | Constitutional judgment — evaluates proposals against F1–F13 floors |
| Attention | AAA | Reality compression + routing — what matters reaches the right organ |
| Execution | A-FORGE | Governed mutation — leases, gates, receipts |
| Witness | VAULT999 | Hash-chained append-only ledger — tamper-evident record of every verdict and receipt |

Authority remains separated at every stage. No single component proposes, judges, executes, and witnesses the same action.

---

## Quick Start

> Requires **Python 3.12+** (supported range: 3.12–3.14; see `pyproject.toml`).

> **Versioning:** Two version schemes coexist. The **kernel release** (`v2026.08.01`) tracks the running service identity. The **PyPI package** (`1!2026.9.1`) uses epoch versioning (`1!`) to outrank legacy releases. They advance independently — the kernel release is the operational truth.

### Install

```bash
pip install arifos
```

### Install (Docker)

```bash
pip install arifos
```

### Install (Docker)

```bash
docker build -t arifos .
docker run -p 8088:8088 --env-file .env.docker arifos
```

### Run the kernel

ARIF = Sovereign · arifOS = Law (Authority Plane) · AAA = Institution (Attention Plane) · A-FORGE = Hands (Execution Plane)

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

### Session Flow (agents start here)

The kernel requires session initialization before judgment. The canonical flow:

```jsonc
// Step 1: Initialize session — establishes actor identity and authority
{ "name": "arif_init", "arguments": { "actor_id": "my-agent", "requested_authority": "OBSERVE_ONLY" } }
// → session_id, session_token, floors bound

// Step 2: Judge a proposal — returns verdict + evidence chain
{ "name": "arif_judge", "arguments": { "candidate": "Deploy v2.1 to production", "action_tier": "standard" } }
// → SEAL | HOLD | SABAR | VOID with constitutional_chain_id

// Step 3: Seal (only after SEAL verdict) — records receipt in VAULT999
{ "name": "arif_seal", "arguments": { "payload": "Deployed v2.1", "constitutional_chain_id": "<from judge>" } }
// → receipt_id, hash chain link
```

> **Verb numbering:** The kernel verbs follow a deliberate 000→999 progression: `arif_init` (000), `arif_observe` (111), `arif_think` (333), `arif_route` (444), `arif_memory` (555), `arif_judge` (666), `arif_forge` (777), `arif_seal` (999). Each number encodes the constitutional stage: ignition → sense → reason → route → recall → judgment → execution → sealing.

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

| Floor | Name | What it checks | Polarity |
|-------|------|---------------|----------|
| F1 | AMANAH | Reversibility — no irreversible action without consent | Higher = better |
| F2 | TRUTH | Evidence-grounded claims — uncertainty-banded | Higher = better |
| F3 | WITNESS | Three-way consistency (theory, code, intent) | Higher = better |
| F4 | CLARITY | Transparent intent | Higher = better |
| F5 | PEACE² | Non-destructive power — block harm and extraction | Higher = better |
| F6 | MARUAH | Dignity — protect the weakest stakeholder | Higher = better |
| F7 | HUMILITY | Acknowledge limits | **Lower = better** (0.04 = very humble) |
| F8 | GENIUS | Elegant correctness (G ≥ 0.80) | Higher = better |
| F9 | ANTI-HANTU | No consciousness or emotion claims | **Lower = better** (0.0 = zero claims) |
| F10 | ONTOLOGY | Structural coherence | Higher = better |
| F11 | AUDIT | Every decision logged, inspectable, attributable | Higher = better |
| F12 | INJECTION | Input sanitization | **Lower = better** (lower = less injection surface) |
| F13 | SOVEREIGN | Human veto is absolute | Higher = better |

### VAULT999 (Append-Only Audit Ledger)

Every verdict, evidence chain, and execution receipt is recorded in VAULT999 — a hash-chained, append-only JSONL ledger (live record count in the header manifest above, re-stamped by `scripts/update_readme_sot.py`). Designed for compliance auditing, forensic review, and governance proof. Chain verification tooling ships in `scripts/verify_vault_chain.py`.

---

## Architecture

```
arifOS Federation — 4 Constitutional Planes

    ┌─────────────────────────────────────────────┐
    │          Authority Plane (arifOS :8088)      │
    │    Constitutional judgment · F1–F13 floors   │
    └──────────────────────┬──────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────┐
    │          Attention Plane (AAA :3001)         │
    │    Reality compression · Routing · State     │
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

The kernel exposes 8 canonical MCP verbs over Streamable HTTP (protocol `2026-07-28`, backward-compatible to `2024-11-05`, `2025-03-26`, `2025-11-25`):

| Stage | Verb | Purpose |
|-------|------|---------|
| 000 | `arif_init` | Establish session context and actor identity |
| 111 | `arif_observe` | State observation and gap detection |
| 333 | `arif_think` | Constitutional reasoning against floors |
| 444 | `arif_route` | Route intent to the appropriate federation organ |
| 555 | `arif_memory` | Query and manage institutional memory |
| 666 | `arif_judge` | Evaluate a proposal and return a verdict |
| 777 | `arif_forge` | Dispatch authorized actions for execution |
| 999 | `arif_seal` | Seal a completed action chain with evidence and receipt |

> `arif_forge` is a **governed dispatch** verb: it routes authorized actions toward the execution organ (A-FORGE) and mutates only after a SEAL verdict. The kernel itself does not perform the underlying mutation. The judge never executes; the executor never certifies.

---

## Verification Status

> The header manifest is regenerated from the live kernel by `scripts/update_readme_sot.py` (run before release commits). Last stamp: `last_verified` above.

| Surface | Status | Evidence |
|---------|--------|----------|
| Public repository | Live | GitHub [`ariffazil/arifOS`](https://github.com/ariffazil/arifOS), AGPL-3.0-only |
| PyPI package | Published `1!2026.9.1` (2026-09-15) | `pip install arifos` — [pypi.org/project/arifos](https://pypi.org/project/arifos/) |
| Live kernel | Service green, status healthy | `curl localhost:8088/health` → `service_health: green`, `deployment_drift_status: aligned` |
| MCP interface | 8 canonical tools / 25 internal superset | Streamable HTTP; protocol `2026-07-28` (back-compat ≥ `2024-11-05`) |
| Floor enforcement | Active — 13/13 pass | `/health → runtime_floors_status` — all pass (F7=0.04, F9=0.0, F12=0.425 are lower-is-better) |
| VAULT999 ledger | Healthy | Hash-chained append-only JSONL; chain verification in `scripts/verify_vault_chain.py` |
| Source / build / deploy | Aligned — no drift | `source_commit = built_commit = deployed_commit` (verify: `curl localhost:8088/health` → `drift: false`; redeployed 2026-09-15 via `scripts/deploy-release.sh`) |
| Contract schema | 8/8 complete, no drift | `contract_status.tool_count: 8`, `contract_drift: false` |
| Federation | 10 organs | See [Architecture](#architecture) |
| Machine-readable | Live | [tools.json](https://arifos.arif-fazil.com/tools.json) (36 KB), [llms.txt](./llms.txt), [CITATION.cff](./CITATION.cff) |

## What Is Not Yet Proven

| Gap | Risk | Status |
|-----|------|--------|
| Independent security audit | Adversarial bypass testing not published | In progress — an external researcher has been reviewing the fetch surface since 2026-08-25 (private disclosure; fix released in `1!2026.9.1`). No independent audit report published yet |
| Third-party evaluation | No external reviewer has published findings | In progress — one external review under way since 2026-08-25; nothing published |
| Reproducible demo by strangers | Onboarding path not independently tested | Open |
| Enterprise deployment | No production customer reference | Open |
| Standards conformance | MCP/A2A conformance results not published externally | Partial — CI workflow `06-mcp-conformance.yml` exists; ABI artifact drift fixed 2026-09-15 (`sync_kernel_abi.py --check` passes); [conformance report](docs/evidence/conformance-report.json) generated; results not published externally |
| SBOM and signed releases | Supply chain integrity unverified externally | Partial — CycloneDX generator (`arifosmcp/arifos_sbom.py`) and an `sbom` job in `07-publish-pypi.yml` that attaches the SBOM to releases; no signing, no CVE scan |
| Comparative benchmark | No published comparison against alternative frameworks | Open |
| Semantic layer (Graphiti) | `graphiti_read: degraded` — knowledge graph not fully wired | Operational gap |
| Observability | Distributed tracing partially wired | Partial — sovereign Postgres backend active (`OBSERVABILITY_BACKEND=dual`); arifFlow FlowReceipt v1 adapter live; trace propagation parameters added; `@trace_tool` OTel spans on all 8 canonical tools; caller-side trace context wiring in progress |

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

# Health check (all 10 federation surfaces)
make health

# Start the kernel
arifos-mcp   # or: python -m arifosmcp.runtime
```

See [`CODEOWNERS`](./CODEOWNERS) for sovereign ownership of automation surfaces. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for contribution guidelines.

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

## Evidence & Trust

arifOS publishes verifiable evidence for its claims. Every public claim links to an artifact that can be independently regenerated.

| Claim | Evidence | Status |
|---|---|---|
| MCP Conformance | [CI Workflow](.github/workflows/06-mcp-conformance.yml) | Partial — CI passes, results not published externally |
| ABI Stability | [Drift Guard](scripts/sync_kernel_abi.py) | Verified — `--check` passes |
| SBOM | [Generator](arifosmcp/arifos_sbom.py) | Partial — CycloneDX generated, no CVE scan |
| Observability | [Telemetry](arifosmcp/runtime/telemetry.py) | Partial — sovereign Postgres + arifFlow + FRAME live |
| Governance | [Adversarial Spec](../AAA/docs/ADVERSARIAL_SPEC_EXTERNAL.md) | Partial — spec ready, no external audit |
| Quickstart | [Guide](docs/QUICKSTART.md) | Exists — not independently validated |

See [docs/evidence/](docs/evidence/) for the full claim registry and evidence index.

> **Honesty principle:** We publish what passed, what failed, and what remains unknown. We do not claim maturity beyond our evidence.

---

## Who Maintains This

One human, and the agents he directs.

I am a geologist, not a programmer. I did not write this codebase and I do not read it line by line. What I do is point at where the problem is — and the agents in my federation solve it, inside the constitution and the review gates I set, with the commit trail to show who ran what.

Read the commits if you want to check that claim: the author fields are agent handles, not aliases of mine. That is the deliberate shape of this project, not a detail being hidden. It also sets the honest expectation — the design and the judgment are mine, the implementation is theirs, and where the two disagree, the bug is mine to answer for.

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
