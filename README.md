<!-- SOT-MANIFEST
federation_release: v2026.08.25
last_verified: 2026-08-25T04:30:00Z
live_commit: 6de71a0d7 (docs(readme): ZEN first-fold)
source_commit: 2258694 (aligned: source = built = deployed)
tools_exposed_via_mcp: 8 (canonical public verbs — live-witnessed 2026-08-25 via :8088/health)
total_declared_tools: 48 (8 public + 13 internal + 27 diagnostic)
registry_size: 62 (includes aliases)
floors_active: 13 (F1–L13, all passing)
federation_schema: 2.0.0
organs: 7 (arifOS:8088, A-FORGE:7071/7072, AAA:3001, GEOX:8081, WEALTH:18082, WELL:18083, arifFlow:7073)
infra: FED:7074 ADVISORY, FLAME:18901 ADVISORY, FRAME:frame-organ OBSERVE
truth_rule: live :8088/health + tools/list beat any static count in prose
vault999: healthy (outcomes.jsonl 67K+ records, append-only, 0 broken lines)
readme_note: ZEN first-fold — full reference at docs/README-FULL.md; federation card at docs/FEDERATION_CARD.md
-->

# arifOS — Constitutional AI Governance Kernel

> **Separates judgment from execution for regulated AI deployment.**

Enterprises deploying AI at scale face a critical gap: agents that act are also certifying their own actions. Without an independent authority to evaluate proposals against safety, compliance, and policy constraints before execution, organizations risk regulatory violations, data breaches, and untraceable decisions. arifOS solves this by acting as a constitutional judge — evaluating every consequential AI action against 13 immutable policy floors and returning a verdict **before** any execution occurs.

**Forged, Not Given.**

---

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           arifOS Kernel (:8088)         │
                    │  ┌───────────────────────────────────┐  │
  User Intent ─────▶│  │  13 Constitutional Floors (F1-F13) │  │──▶ SEAL / HOLD / SABAR / VOID
                    │  │  State Observation & Gap Detection │  │
                    │  │  VAULT999 Append-Only Ledger       │  │
                    │  └───────────────────────────────────┘  │
                    └─────────────┬───────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
     ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
     │   SEAL       │    │   HOLD       │    │   VOID       │
     │              │    │              │    │              │
     │  A-FORGE     │    │  Human Review│    │  Blocked     │
     │  Executes    │    │  Approves    │    │  by Floor    │
     └──────┬───────┘    └──────────────┘    └──────────────┘
            │
            ▼
     ┌──────────────┐
     │  VAULT999    │  67K+ immutable records
     │  Audit Log   │  append-only, zero gaps
     └──────────────┘
```

**The judge never executes. The executor never certifies.**

---

## Quick Start

### Docker

```bash
docker run -d --name arifos \
  -p 8088:8088 \
  -v $(pwd)/data:/app/data \
  arifos/kernel:latest
```

### Health Check

```bash
curl http://localhost:8088/health
```

### MCP Connection

```bash
# Connect via MCP endpoint
mcp connect http://localhost:8088/mcp
```

---

## Core Features

### 13 Constitutional Floors (F1–F13)

Every proposal is evaluated against a chain of 13 policy constraints spanning safety, reversibility, scope, authority, evidence, and governance. A single floor failure produces a **VOID** verdict — no action proceeds until the constraint is resolved.

### Four Verdict Types

| Verdict | Meaning |
|---------|---------|
| **SEAL** | Authorized under stated conditions |
| **HOLD** | Insufficient evidence or human approval required |
| **SABAR** | Proceed with caution — partial authorization |
| **VOID** | Blocked by a constitutional floor |

### VAULT999 — Immutable Audit Ledger

Every verdict, evidence chain, and execution receipt is recorded in VAULT999 — an append-only JSONL ledger currently holding 67,000+ records with zero broken lines. Designed for compliance auditing, forensic review, and regulatory proof of governance.

### MCP Interface

The kernel exposes 8 MCP verbs over `/mcp` (and `/webmcp` locally on :8088). No public console — programmatic access only.

---

## Federation Topology

The arifOS Federation comprises 7 organs, each with a distinct responsibility:

| Organ | Port | Responsibility |
|-------|------|----------------|
| **arifOS** | :8088 | Law — constitutional judgment |
| **AAA** | :3001 | Routing — intelligence & task orchestration |
| **A-FORGE** | :7071/:7072 | Execution — hands that build and act |
| **GEOX** | :8081 | Earth sciences — geospatial reasoning |
| **WEALTH** | :18082 | Capital management — financial operations |
| **WELL** | :18083 | Biometric & health — vitality monitoring |
| **arifFlow** | :7073 | Orchestration — workflow coordination |

**ARIF vetoes. arifOS judges. AAA routes. A-FORGE executes.**

---

## MCP Verbs Reference

| Verb | Purpose |
|------|---------|
| `arif_init` | Establish session context, actor identity, and constraints |
| `arif_observe` | State observation & gap detection — inspect current conditions |
| `arif_think` | Constitutional reasoning against floors before judgment |
| `arif_route` | Route intent to the appropriate federation organ |
| `arif_memory` | Query and manage institutional memory |
| `arif_judge` | Evaluate a proposal and return a verdict (SEAL/HOLD/SABAR/VOID) |
| `arif_forge` | Dispatch authorized actions to A-FORGE for execution |
| `arif_seal` | Seal a completed action chain with full evidence and receipt |

---

## Sister Repositories

| Repository | Description |
|------------|-------------|
| [AAA](https://github.com/arif-os/AAA) | Intelligence, routing, and multi-agent orchestration |
| [A-FORGE](https://github.com/arif-os/A-FORGE) | Execution engine — containerized task execution |
| [GEOX](https://github.com/arif-os/GEOX) | Geospatial and earth sciences reasoning organ |
| [WEALTH](https://github.com/arif-os/WEALTH) | Capital management and financial operations organ |
| [WELL](https://github.com/arif-os/WELL) | Biometric monitoring and health management organ |
| [arifFlow](https://github.com/arif-os/arifFlow) | Workflow orchestration and pipeline management |

---

## Documentation

- [Federation Card](./docs/FEDERATION_CARD.md) — Full organ topology and relationships
- [Full README Reference](./docs/README-FULL.md) — Complete feature documentation
- [Constitution](./GENESIS/000_KERNEL_CANON.md) — Constitutional floors and doctrine
- [ZEN Doctrine](./docs/ZEN.md) — Governance philosophy and design principles

---

## License

**AGPL-3.0** — This software is licensed under the GNU Affero General Public License v3.0. See [LICENSE](./LICENSE) for details.

When deployed over a network, the complete source code must be made available to all users interacting with the service, consistent with AGPL-3.0 terms.
