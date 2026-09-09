<!-- SOT-MANIFEST
federation_release: v2026.08.25
last_verified: 2026-09-09T12:00:00+08:00
live_commit: 6de71a0d7 (docs(readme): ZEN first-fold)
source_commit: 2258694
tools_exposed_via_mcp: 8 (canonical public verbs)
floors_active: 13 (F1–F13, all passing)
federation_schema: 2.0.0
organs: 7 (arifOS:8088, A-FORGE:7071/7072, AAA:3001, GEOX:8081, WEALTH:18082, WELL:18083, arifFlow:7073)
vault999: healthy (67K+ records, append-only, 0 broken lines)
truth_rule: live :8088/health + tools/list beat any static count in prose
--->

# arifOS — An Open-Source Governance Decision Point for AI Agent Actions

**arifOS evaluates consequential AI actions against policy floors and returns a verdict _before_ execution occurs.**

When an AI agent proposes to write, delete, deploy, or spend, arifOS inserts an independent judgment step: the agent proposes, arifOS evaluates, a human approves (or not), and only then does execution proceed. Every verdict is recorded with full evidence in an append-only ledger.

**This is not an AI model. It is not an agent framework. It is a policy decision point — the layer between "agent wants to act" and "action occurs."**

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

---

## Quick Start

### Install

```bash
pip install arifos
```

### Run the kernel

```bash
# Start the MCP server
arifos serve --port 8088

# Check health
curl http://localhost:8088/health
```

### Connect an agent

```python
# Via MCP (Streamable HTTP)
import httpx

# Submit a proposal for judgment
response = httpx.post("http://localhost:8088/mcp", json={
    "method": "tools/call",
    "params": {
        "name": "arif_judge",
        "arguments": {
            "candidate": "Write file /data/report.csv with production data",
            "action_tier": "standard"
        }
    }
})
# Returns: SEAL | HOLD | SABAR | VOID with full evidence chain
```

### Five-minute governed action

```bash
# Full cycle: proposal → judgment → human approval → execution → receipt
arifos demo --guided
```

---

## Core Concepts

### Four Verdicts

| Verdict | Meaning | What happens |
|---------|---------|-------------|
| **SEAL** | Authorized under stated conditions | Proceed to execution |
| **HOLD** | Insufficient evidence or human approval needed | Pause; await human decision |
| **SABAR** | Not yet decidable — reality hasn't finished speaking | Wait; distinct from HOLD |
| **VOID** | Blocked by a constitutional floor | Stop; constraint must be resolved |

### 13 Constitutional Floors (F1–F13)

Every proposal passes through 13 policy constraints. A single floor failure produces VOID.

| Floor | Name | What it checks |
|-------|------|---------------|
| F1 | AMANAH | Reversibility — no irreversible action without consent |
| F2 | TRUTH | Evidence-grounded claims — uncertainty-banded |
| F3 | WITNESS | Three-way consistency (theory, code, intent) |
| F4 | CLARITY | Transparent intent |
| F5 | PEACE | Human dignity over convenience |
| F6 | EMPATHY | Consequences for weakest stakeholders |
| F7 | HUMILITY | Acknowledge limits |
| F8 | GENIUS | Elegant correctness (G ≥ 0.80) |
| F9 | ANTI-HANTU | No consciousness or emotion claims |
| F10 | ONTOLOGY | Structural coherence |
| F11 | AUTH | Identity verification before sensitive operations |
| F12 | INJECTION | Input sanitization |
| F13 | SOVEREIGN | Human veto is absolute |

### VAULT999 — Audit Ledger

Every verdict, evidence chain, and execution receipt is recorded in VAULT999 — an append-only JSONL ledger with 67,000+ records. Designed for compliance auditing, forensic review, and governance proof.

---

## Architecture

```
arifOS Federation — 7 Organs

arifOS (:8088)     Constitutional judgment kernel
AAA (:3001)        Identity, routing, agent orchestration
A-FORGE (:7071)    Execution after authorization
GEOX (:8081)       Earth sciences domain evidence
WEALTH (:18082)    Capital and financial intelligence
WELL (:18083)      Human and machine vitality observation
arifFlow (:7073)   Workflow orchestration

ARIF vetoes. arifOS judges. AAA routes. A-FORGE executes.
```

arifOS is the kernel. The other organs are supporting infrastructure. GEOX is the primary reference implementation, demonstrating governance in high-consequence, uncertainty-heavy workflows.

---

## MCP Interface

The kernel exposes 8 canonical MCP verbs over Streamable HTTP:

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

---

## What Is Proven

| Surface | Status |
|---------|--------|
| GitHub repository | Public, AGPL-3.0, active commits (September 2026) |
| PyPI package | `pip install arifos`, version 1!2026.8.2 |
| Live health endpoint | `curl localhost:8088/health` — returns structured JSON |
| MCP interface | 8 tools, Streamable HTTP, schema-validated |
| VAULT999 ledger | 67K+ append-only records |
| Floor enforcement | 13 floors active, all passing in current deployment |
| Source-build-deploy alignment | Verified (commit 606f5ac) |
| GEOX reference implementation | Geoscience uncertainty workflows |
| Federation architecture | 7 organs with defined boundaries |

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
python -m arifosmcp.serve --port 8088
```

### Project Structure

```
arifOS/
├── arifosmcp/          # Core kernel package
│   ├── abi/            # Capability registry and floor definitions
│   ├── constitution/   # Constitutional floor implementations
│   ├── kernel/         # Core judgment engine
│   └── vault/          # VAULT999 ledger implementation
├── tests/              # Test suite
├── docs/               # Documentation
│   ├── START_HERE.md   # External reader entry point
│   └── ...
└── pyproject.toml      # Package metadata
```

---

## Sister Repositories

| Repository | Purpose |
|------------|---------|
| [AAA](https://github.com/ariffazil/AAA) | Identity, routing, multi-agent orchestration |
| [A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution engine after authorization |
| [GEOX](https://github.com/ariffazil/GEOX) | Earth sciences domain evidence |
| [WEALTH](https://github.com/ariffazil/WEALTH) | Capital and financial intelligence |
| [WELL](https://github.com/ariffazil/WELL) | Human and machine vitality observation |
| [arifFlow](https://github.com/ariffazil/arifFlow) | Workflow orchestration |

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
