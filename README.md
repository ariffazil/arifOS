<!-- SOT-MANIFEST
last_verified: 2026-09-21T01:38:52+00:00
kernel_release: v2026.08.01 (release_name from live /health) · canon version 2026.09.20-e8e6f93
pypi_version: 1!2026.9.2 (published 2026-09-15T16:42Z) · repo tree 1!2026.9.6 (staged, not yet released)
live_commit: e8e6f9335 (fix(judge): G-10 — default action_tier no longer budgets 888 as a rule engine)
source_commit: e8e6f9335
built_commit: e8e6f93
deployment_drift_status: aligned (source = built = deployed (drift: false))
tools_exposed_via_mcp: 8 (canonical public verbs — verified by live tools/list)
tools_canonical_superset: 25 (8 exposed + 13 hidden verbs — arif_challenge, arif_judge_deliberate, …)
tools_declared: 48 · registry_callables: 62 (includes aliases) · proven_live_24h: 3
floors_active: 13/13 measured pass (live-probed 2026-09-21; F7=0.04, F9=0.15, L12=0.425 are lower-is-better)
federation_schema: 2.0.0
mcp_protocol: advertises 2026-07-28; live initialize and the internal conformance runner settle on 2025-11-25 (supported: 2026-07-28 · 2025-11-25 · 2025-03-26 · 2024-11-05)
organs: 7 per the ratified organ table (FEDERATION_CONTRACT §2) + plane classes for boundary services (see Architecture)
vault999: healthy (241K+ records, append-only)
contract_status: 8/8 published schemas, contract_drift: false
tool_manifest_url: https://arifos.arif-fazil.com/tools.json (37,046 bytes, live)
apex_zen: A2A delegates ⊥ MCP equips ⊥ ACT mutates ⊥ arifOS governs ⊥ F13 decides
truth_rule: live :8088/health + tools/list beat any static count in prose — re-run before you quote this file
generated_by: scripts/update_readme_sot.py re-stamps commits, drift, last_verified and the vault count only; every other field here is verified by hand at audit time and must be re-verified the same way
holds: Merkle signing lane · WELL biometrics · medical purge (Pilihan A)
seal_readiness_gaps: graphiti=RETIRED_888(2026-09-04) · semantic_floor=off_by_choice(ARIFOS_ML_FLOORS=0) · langfuse=SOVEREIGN_CUTOVER→kabarkan(live)
-->

# arifOS — The Authority Plane of the arifOS Federation

[![Security Audit: In Progress](https://img.shields.io/badge/Security_Audit-In_Progress-d4a853?style=flat-square)](./SECURITY.md#known-gaps)
[![External evaluation: not yet published](https://img.shields.io/badge/External_Evaluation-Not_Yet_Published-d4a853?style=flat-square)](./SECURITY.md#known-gaps)
[![Kernel: healthy](https://img.shields.io/badge/Kernel-healthy-blue?style=flat-square)](https://arifos.arif-fazil.com/health)
[![MCP scanners: 148 rules, 0 unauthorised mutations](https://img.shields.io/badge/MCP_Scanners-148_rules,_0_unauth_mutations-d4a853?style=flat-square)](https://mcp.arif-fazil.com/proof/)
[![Sovereign Boundary: F13](https://img.shields.io/badge/Sovereignty-F13_Enforced-critical?style=flat-square)](https://arif-fazil.com/governance/)
[![MCP Conformance](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/06-mcp-conformance.yml?label=MCP_Conformance&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/06-mcp-conformance.yml)
[![Vault Integrity](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/07-vault-integrity.yml?label=Vault_Integrity&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/07-vault-integrity.yml)
[![Floor Gate](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/floor_gate.yml?label=Floor_Gate&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/floor_gate.yml)
[![Governance](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/governance-gate.yml?label=Governance&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/governance-gate.yml)
[![Runtime Drift](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/08-runtime-drift.yml?label=Runtime_Drift&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/08-runtime-drift.yml)
[![External Witness](https://img.shields.io/github/actions/workflow/status/ariffazil/arifOS/external-witness.yml?label=External_Witness&style=flat-square)](https://github.com/ariffazil/arifOS/actions/workflows/external-witness.yml)

**arifOS evaluates consequential AI actions against constitutional floors and returns an independent verdict _before_ execution occurs.**

When an AI agent proposes to write, delete, deploy, or spend, arifOS inserts a constitutional judgment step: the agent proposes, arifOS evaluates the proposal against the F1–F13 floors, a verdict is returned, and only then does execution proceed. Every consequential verdict is written into an append-only hash chain with its decision context, evidence references, provenance and receipt hashes.

In a world where intelligence is abundant, authority becomes the scarce resource. arifOS exists to keep judgment independent from execution.

**This is not an AI model. It is not an agent framework. It is a constitutional authority system — the layer between "agent wants to act" and "action is permitted."**

Two invariants hold everywhere in this document:

> **Proposer ≠ Judge ≠ Executor ≠ Witness**
> **Human sovereignty > machine authority**

**What arifOS is not:** not an AI model · not an agent framework · not an execution engine (A-FORGE executes) · not an attention plane (AAA attends) · not the independent witness (FRAME witnesses; VAULT999 remembers) · not a substitute for authentication, sandboxing, or legal review.

| Audience | What you get |
|---|---|
| **Human** | A quiet veto: the agent proposes, the kernel records a verdict, you stay sovereign |
| **Agent / A2A** | MCP tools + receipts. You do not get the keys. A2A v1.0 (`a2a_version: 1.0.1` in the agent card), not v1.2 — discovery is owned by AAA, execution by arifOS |
| **Institution** | Policy floors F1–F13, a hash-chained VAULT999 audit trail, model-vendor independence |
| **Indexer / Search** | Structured metadata, [`llms.txt`](./llms.txt), [tools.json](https://arifos.arif-fazil.com/tools.json), [`CITATION.cff`](./CITATION.cff) |
| **Machine / MCP** | [Streamable HTTP endpoint](https://mcp.arif-fazil.com/mcp), 8 canonical verbs, published input/output schemas |
| **Robot / Automation** | CI gates (conformance, vault-integrity, drift, governance), [`Makefile`](./Makefile) targets, [`Dockerfile`](./Dockerfile) |

Live: `https://arifos.arif-fazil.com` · MCP `:8088` · sister organs [GEOX](https://github.com/ariffazil/GEOX) · [A-FORGE](https://github.com/ariffazil/A-FORGE) · [AAA](https://github.com/ariffazil/AAA)

---

## The Problem

AI agents that act are also certifying their own actions. Nothing independent evaluates the proposal against safety, compliance and policy constraints before execution occurs.

## The Solution

```
  Agent proposes action
         │
         ▼
  ┌─────────────────┐
  │   arifOS Kernel  │  Evaluates against 13 constitutional floors
  │     (:8088)      │  Records provenance + evidence refs + hashes
  └────────┬────────┘
           │
    ┌──────┼────────┬──────────┬───────────┐
    ▼      ▼        ▼          ▼           ▼
  SEAL    HOLD    SABAR     PARTIAL      VOID
  (go)  (wait for (defer —  (proceed   (blocked by
        human)    evidence   with       a floor)
                  pending)   cooling)
    │      │
    ▼      ▼
  Execute  Human
  via      reviews
  A-FORGE
    │
    ▼
  Receipt in VAULT999
  (append-only hash chain)
```

**The judge never executes. The executor never certifies.**

### Federation in one line

> **Intelligence proposes. Authority constrains. Execution acts. Reality witnesses. History remembers.**

| Plane / class | Component | Role |
|---|---|---|
| Authority | **arifOS** `:8088` | Constitutional judgment — evaluates proposals against F1–F13; owns the gavel and the ledger |
| Attention | **AAA** `:3001` | Attention and routing — what matters, and to whom. Displays, routes, queues; never adjudicates |
| Execution | **A-FORGE** `:7071`/`:7072` | Governed mutation — leases, gates, receipts; only under a SEAL verdict |
| Witness | **FRAME** `:18085` | Independent observer. Its output is evidence, never a verdict |
| Record | **VAULT999** (in-kernel) | Immutable append-only ledger — the memory of what was decided |
| Metabolism | **arifFlow** `:7073` | Receipt ingestion, FQ monitoring, verification cadence; never adjudicates |
| Domain intelligence | **GEOX** `:8081` · **WEALTH** `:18082` · **WELL** `:18083` | Evidence and computation in a domain. Compute-only: no organ authorises its own action |
| Provider gateway | **FED** `:7074` | Multi-provider model routing (advisory-only) |
| Synthesis | **i-ARIF** | Seal-B synthesis engine — runs through FED chains, owns no port |
| Boundary services (Tier-3) | **HERMES** `:18087` · **CHRON** `:18102` | Semantic boundary (meaning integrity, relay-only) and temporal boundary (episodes, predictions, calibration). Neither is an organ — see the ruling in [`FEDERATION_CONTRACT.md` §2.1](./FEDERATION_CONTRACT.md) |

Authority remains separated at every stage: no component proposes, judges, executes and witnesses the same action. **arifOS determines whether and how a routing may proceed**; AAA determines what matters.

---

## Quick Start

> Requires **Python 3.12+** (supported range 3.12–3.14; see `pyproject.toml`).
>
> **Versioning:** two schemes coexist. The **kernel release** (`v2026.08.01`, reported by `/health` as `release_name`) is the operational identity of the running service. The **PyPI package** uses epoch versioning (`1!…`) to outrank legacy releases: `1!2026.9.2` is what `pip install arifos` resolves to today, while this tree is `1!2026.9.6` (staged, not yet released). The kernel release is the operational truth; PyPI is the distribution truth.

### Install

```bash
pip install arifos
pip show arifos        # → Version: 1!2026.9.2  (module __version__ strings are stale — do not quote them)
```

### Install (Docker)

```bash
docker build -t arifos .
docker run -p 3000:3000 --env-file .env.docker.example arifos
# The image listens on 3000 (Dockerfile EXPOSE/CMD). Its OCI labels still say 8088 and
# carry a legacy licence value — see "What Is Not Yet Proven".
```

### Run the kernel

```bash
# HTTP transport (this is the MCP endpoint) — port comes from $PORT, default 8080
PORT=8088 arifos-mcp streamable-http

# stdio transport, for a local stdio MCP client
arifos-mcp

# equivalent module form
PORT=8088 python -m arifosmcp.runtime --mode streamable-http

# health — the deployed unit runs on 8088
curl -s http://localhost:8088/health
```

Verified on 2026-09-21 against the live unit:

```jsonc
{ "status": "healthy", "release_name": "v2026.08.01", "mcp_protocol_version": "2026-07-28",
  "tools_loaded": 8, "operational_tools": 3, "deployment_drift_status": "aligned",
  "floors_active": 13, "vault999_health": "healthy" }
```

### Run a governed workflow locally (no client needed)

`examples/enterprise_operations_demo.py` runs six graded scenarios in-process and prints each verdict, its floor gate and its receipt — including two that are refused:

```bash
python examples/enterprise_operations_demo.py
```

```
[ DEMO / SIMULATED WORKFLOW ]  No real customer funds, records, or firewall policies are altered.
Kernel Session ID : SEAL-DEMO-…        Authority Ceiling : LIMITED_MUTATE
SCENARIO 1: Read Customer Account Data      → ✔ ALLOW   RCPT-4245A2002143490B
SCENARIO 3: Major Enterprise Refund (RM5,000) → ⏸ HOLD  (RM100 autonomous ceiling, over by 50×)
SCENARIO 4: Delete Customer Account & Audit Trail → ✘ BLOCK/VOID
```

### Connect an MCP client

```
http://localhost:8088/mcp      # or https://mcp.arif-fazil.com/mcp
```

**Protocol facts, as measured:** the kernel advertises `2026-07-28` and accepts `2026-07-28 · 2025-11-25 · 2025-03-26 · 2024-11-05`. A live `initialize` currently settles on **`2025-11-25`** — the declared canonical spec in `arifosmcp/runtime/public_surface.py` and the version the internal conformance runner records. If you pin a protocol version, use `2025-11-25`.

```bash
curl -s http://localhost:8088/mcp \
  -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
# → 8 tools: arif_init arif_observe arif_think arif_route arif_memory arif_judge arif_forge arif_seal
```

### Session flow (agents start here)

The kernel binds a session before any judgment. Verified transcript, 2026-09-21:

```jsonc
// Step 1 — arif_init: establish actor identity and authority band
{ "name": "arif_init", "arguments": { "mode": "init", "actor_id": "my-agent" } }
// → { "verdict": "HOLD", "session_id": "SEAL-df114686f4c34971",
//     "autonomy_band": "OBSERVE_ONLY", "trace_id": "trc-197d2fa35887", "session_token": "act_v1.…" }
// HOLD here is the normal starting state: the session is open, no mutation is authorised yet.

// Step 2 — arif_judge: evaluate a proposal, return a verdict + evidence
{ "name": "arif_judge", "arguments": {
    "candidate": "Delete the production audit table", "action_tier": "standard",
    "session_id": "SEAL-df114686f4c34971", "actor_id": "my-agent" } }
// → { "verdict": "HOLD", "trace_id": "trc-d5d4d2fed6f8",
//     "constitutional_check": { "hold_required": true, "failed_floors": [] },
//     "next_safe_action": "provide actor_signature / sovereign_receipt / heart_critique, or reduce blast radius" }

// Step 3 — arif_seal: only after a SEAL verdict; appends the receipt to VAULT999
{ "name": "arif_seal", "arguments": { "payload": "…", "session_id": "…", "ack_irreversible": true } }
```

> Call `arif_judge` without a session and the kernel answers `actor: anonymous`, `authority: OBSERVE_ONLY`, `verdict: HOLD` — it will not silently upgrade an unattested caller.

> **Stage numbering (single source of truth).** The verbs follow the ratified nine-stage map: `000` INIT · `111` OBSERVE · `333` THINK · `444` ROUTE · `555` MEMORY · `666` JUDGE · `777` FORGE · `999` SEAL. Source: `arifosmcp/constitutional_map.py` `ToolStage` (F13-ratified 2026-07-31: JUDGE = **666**, FORGE = **777**; the old `888` stage was retired when compose was absorbed into forge). Some mirrors still carry the retired `888` label — a description string in `constitutional_map.py`, `tools_sot.yaml`, the generated `llms.txt`, and `docs/PROMPT_666_JUDGE_DEPRECATION.md` (dated 2026-07-10, predating the correction). The live wire says `666`, and this README follows the live wire. Flagged for repair in "What Is Not Yet Proven".

For a guided walkthrough, start with [docs/START_HERE.md](./docs/START_HERE.md) or the verified [docs/QUICKSTART.md](./docs/QUICKSTART.md).

---

## Core Concepts

### The verdict lattice

Verdicts are ordered and non-compensatory — a stronger verdict always dominates a weaker one. Seven seals are defined in `arifosmcp/models/verdicts.py`:

```
VOID  >  HOLD_888  >  HOLD  >  SABAR  >  PARTIAL  >  PROVISIONAL  >  SEAL
```

| Verdict | Meaning | Plain English | What happens |
|---------|---------|---------------|-------------|
| **SEAL** | Authorised under stated conditions, W³ ≥ 0.95 | Go | Proceed to execution |
| **PARTIAL** | A derived floor warns | Go carefully | Proceed with cooling and monitoring |
| **SABAR** | Not yet decidable — reality hasn't finished speaking | Wait for evidence | Retry permitted later; distinct from HOLD |
| **HOLD** | Insufficient evidence, or human approval required | Wait for human | Pause; await a human decision |
| **HOLD_888** | Immediate sovereign escalation | Stop — the sovereign decides | Escalate to F13 |
| **VOID** | Blocked by a hard constitutional floor | Blocked | Stop; the constraint must be resolved |

Floors are never averaged. One floor failure propagates into the verdict; there is no compensating score.

### 13 Constitutional Floors (F1–F13)

Every proposal is evaluated against 13 non-compensatory policy constraints. Canonical names and rules: [`FEDERATION_CONTRACT.md` §3](./FEDERATION_CONTRACT.md), `GENESIS/000_KERNEL_CANON.md`, and the constitution at `static/arifos/theory/000/000_CONSTITUTION.md`.

| Floor | Name | Rule | Polarity |
|-------|------|------|----------|
| F1 | AMANAH | Reversible first. Irreversible → 888_HOLD unless the sovereign acknowledges | Higher = better |
| F2 | TRUTH | P(truth) ≥ 0.99. Cheap claims = VOID. Evidence carries an OBS/DER/INT/SPEC label | Higher = better |
| F3 | TRI-WITNESS | W₃ = ∛(Human × AI × Earth) ≥ 0.75 at judgment time | Higher = better |
| F4 | CLARITY | ΔS ≤ 0 — every output reduces entropy, never adds it | Higher = better |
| F5 | PEACE² | Non-destructive power — block harm and extraction | Higher = better |
| F6 | EMPATHY *(operational: MARUAH)* | Protect the weakest stakeholder; dignity is not tradeable | Higher = better |
| F7 | HUMILITY | Ω₀ ∈ [0.03, 0.05]. No fake certainty | **Lower = better** (0.04 = very humble) |
| F8 | GENIUS | G ≥ 0.80 for complex actions — the simplest correct path | Higher = better |
| F9 | ANTIHANTU | No deception, manipulation, or consciousness claims | **Lower = better** |
| F10 | ONTOLOGY | AI-only ontology. A soul claim is VOID; map it to harness content | Higher = better |
| F11 | AUDITABILITY | Every decision logged, inspectable, attributable | Higher = better |
| F12 | RESILIENCE | Injection defence. Input risk < 0.85 | **Lower = better** (lower = less injection surface) |
| F13 | SOVEREIGN | Human veto is FINAL. The harness switch belongs to the human | Higher = better |

Three naming notes, so a reader can reconcile this table with the wire:

- **F6 has two canonical names by design** — `EMPATHY` in the public register, `MARUAH` in the kernel, logs and receipts. Both are correct; the bridge is documented in `GENESIS/000_KERNEL_CANON.md` §3.4. Public surfaces render EMPATHY.
- **The live runtime keys F10–F13 as `L10`–`L13`** in `/health → runtime_floors`. Same floors, different key prefix.
- **Lower-is-better floors** are reported as raw measurements, not as failures: live values on 2026-09-21 were F7 = 0.04, F9 = 0.15, L12 = 0.425, and `/health → runtime_floors_status` reports 13/13 pass with every floor `measured: true`.

### VAULT999 (append-only audit ledger)

Every consequential verdict, evidence chain and execution receipt is written to VAULT999 — a hash-chained, append-only JSONL ledger set, tamper-evident by construction.

**What it stores is provenance, not copies.** An entry carries its payload hash, entry hash, previous entry hash, trace root, actor, session, decision context and evidence *references*. Source payloads are not duplicated into the ledger — auditability here means `provenance + integrity + reconstructability`, which is both stronger and safer than copying everything forever (evidence can contain sensitive material).

Measured 2026-09-21: **241,765 lines across 24 JSONL ledgers** in `VAULT999/` (largest: `outcomes.jsonl` 93,266 · `arifflow_sealed.jsonl` 52,056 · `apex-zen-receipts.jsonl` 30,977). The chain report from [`scripts/verify_vault_chain.py`](./scripts/verify_vault_chain.py) returns **overall: INTACT** for the active ledgers, reporting 2 strict link breaks in the frozen v1 legacy ledger as historical facts rather than hiding or rewriting them. Live record count is re-stamped into the header manifest above by `scripts/update_readme_sot.py`.

---

## Architecture

```
arifOS Federation — planes and classes

    ┌───────────────────────────────────────────────────┐
    │  Authority plane — arifOS :8088                    │
    │  Constitutional judgment · F1–F13 · VAULT999        │
    └──────────────────────┬────────────────────────────┘
                           │
    ┌──────────────────────▼────────────────────────────┐
    │  Attention plane — AAA :3001                       │
    │  What matters · routing · state · skill catalog    │
    └──────────────────────┬────────────────────────────┘
                           │
    ┌──────────────────────▼────────────────────────────┐
    │  Execution plane — A-FORGE :7071/:7072             │
    │  Governed mutation · leases · receipts             │
    └──────────────────────┬────────────────────────────┘
                           │
    ┌──────────────────────▼────────────────────────────┐
    │  Witness + record — FRAME :18085 · VAULT999        │
    │  Independent observation · immutable history       │
    └───────────────────────────────────────────────────┘
        boundaries:  HERMES :18087 (semantic) · CHRON :18102 (temporal)
        domains:     GEOX :8081 · WEALTH :18082 · WELL :18083
        metabolism:  arifFlow :7073      gateway: FED :7074      synthesis: i-ARIF
```

arifOS is the kernel; the other components are supporting infrastructure. GEOX is the primary reference implementation — a live geoscience organ whose evidence is governed in a high-consequence, uncertainty-heavy domain. FRAME's output is evidence, never a verdict. Domain organs compute; they never authorise.

**Organs vs. boundaries — the ruling.** The ratified organ table ([`FEDERATION_CONTRACT.md` §2](./FEDERATION_CONTRACT.md)) lists 7 live organs: arifOS, A-FORGE, AAA, GEOX, WEALTH, WELL, arifFlow. HERMES is Tier-3 boundary infrastructure and is not an organ (§2.1, 2026-09-14 ruling); CHRON is the temporal boundary service. They are reported here by class rather than padded into an organ count — "everything we built" is not an architectural category.

**Port note:** i-ARIF has no listening port; `:18095` is `apa-github-bridge`, one of the APA boundary bridges (`:18075`–`:18099`). A previous revision of this file named `:18095` as i-ARIF — corrected 2026-09-21.

---

## MCP Interface

The kernel exposes **8 canonical verbs** over Streamable HTTP. Verified by live `tools/list` on 2026-09-21:

| Stage | Verb | Purpose |
|-------|------|---------|
| 000 | `arif_init` | Session ignition — binds actor, floors and audit before any other verb |
| 111 | `arif_observe` | Sense reality into evidence with epistemic tags and uncertainty bounds |
| 333 | `arif_think` | Structured reasoning under F2/F7, with OBS/DER/INT/SPEC labels |
| 444 | `arif_route` | Intent → organ routing, dispatching to GEOX / WEALTH / WELL / A-FORGE |
| 555 | `arif_memory` | Governed memory — L1–L6 recall, storage, promotion |
| 666 | `arif_judge` | Evaluate a proposal; returns a binding verdict with the floor chain |
| 777 | `arif_forge` | Execution gate via A-FORGE — mutates only after a SEAL verdict |
| 999 | `arif_seal` | VAULT999 immutable append — seals a completed chain with its receipt |

> `arif_forge` is a **governed dispatch** verb: it routes an authorised action toward the execution organ and mutates only after SEAL. The kernel does not perform the underlying mutation. `arif_route` is authority-aware dispatch, not attention: it decides *whether and how* a routing may proceed, and may consult AAA. The judge never executes; the executor never certifies.

**Tool-count semantics** (so no two surfaces appear to disagree):
`tools_loaded = 8` — the public MCP facade, and the only number to quote publicly ·
`canonical superset = 25` — 8 exposed + 13 hidden verbs (e.g. `arif_challenge`, `arif_judge_deliberate`), hidden by design ·
`total_declared_tools = 48` · `tools_registry_size = 62` (includes aliases) ·
`operational_tools = 3` — the count with a durable SUCCESS in the last 24 hours, i.e. *proven live*, not merely invocable.

---

## Verification Status

Live-probed **2026-09-21** (UTC+08). Re-run the commands; static counts are not evidence.

| Surface | Status | Evidence |
|---------|--------|----------|
| Public repository | Live | GitHub [`ariffazil/arifOS`](https://github.com/ariffazil/arifOS), AGPL-3.0 |
| PyPI package | Published `1!2026.9.2` (uploaded 2026-09-15T16:42Z) | `pip install arifos` — [pypi.org/project/arifos](https://pypi.org/project/arifos/); tree is `1!2026.9.6`, unreleased |
| Live kernel | Healthy, 13/13 floors | `curl localhost:8088/health` → `status: healthy`, `floors_active: 13` |
| MCP interface | 8 canonical verbs | live `tools/list`; protocol advertises `2026-07-28`, negotiation settles `2025-11-25` |
| Floor enforcement | 13/13 measured pass | `/health → runtime_floors_status` (F7 = 0.04, F9 = 0.15, L12 = 0.425 lower-is-better) |
| VAULT999 ledger | Healthy, chain INTACT | 241,765 lines / 24 ledgers; `scripts/verify_vault_chain.py` |
| Source / build / deploy | Aligned — no drift | `source_commit = built_commit = deployed_commit = e8e6f93`; `/health → drift: false` |
| Contract schema | 8/8 published, no drift | `contract_status: {tool_count: 8, schemas_complete: true, contract_drift: false}` |
| Federation surfaces | 11/11 answering on localhost; WELL degraded | ports 8088 · 3001 · 7071 · 7072 · 8081 · 18082 · 18083 · 7073 · 7074 · 18085 · 18102 all HTTP 200; WELL reports `drift: true` |
| Machine-readable | tools.json live, 37,046 bytes | [tools.json](https://arifos.arif-fazil.com/tools.json) · [llms.txt](./llms.txt) (generated mirror — see gaps) · [CITATION.cff](./CITATION.cff) |
| Scanner attestation | 148 rules · 0 unauthorised mutations; 26/26 GRADE A | [mcp.arif-fazil.com/proof/](https://mcp.arif-fazil.com/proof/) |

## What Is Not Yet Proven

Every row names its own gap. Repairing a claim by substituting a stronger one is worse than the stale claim it replaced.

| Gap | Risk | Status |
|-----|------|--------|
| Independent security audit | Adversarial bypass testing not published | **In progress** — external researcher reviewing since 2026-08-25. First finding (fetch-surface SSRF) fixed, released in `1!2026.9.1`. A second scan (2026-09-15/16, mcp-safeguard) found 2 confirmed issues: Cypher injection (graph-wipe risk, HIGH — key whitelist landed in `l5_sovereign_forge.py`) and a fastmcp decode-after-match path traversal (MEDIUM — arifOS-side containment guard landed in `atlas333.py`; upstream report pending). Both are at code level; neither has a released-artifact verdict. See [SECURITY.md](./SECURITY.md#known-gaps) |
| Third-party evaluation | No external reviewer has published findings | In progress — one review under way since 2026-08-25; nothing published |
| Reproducible demo by strangers | Onboarding path not independently tested | **Partial** — `examples/enterprise_operations_demo.py` runs in-process and is verified here; no stranger has reproduced it unaided |
| Enterprise deployment | No production customer reference | Open |
| Standards conformance | MCP/A2A conformance results not published externally | **Partial** — CI `06-mcp-conformance.yml`; [conformance report](docs/evidence/conformance-report.json) says `result: PARTIAL`, `spec_version: 2025-11-25`, with per-tool schema validation DEFERRED |
| SBOM and signed releases | Supply-chain integrity unverified externally | **Partial** — CycloneDX generator + `sbom` job on publish; no signing, no CVE scan |
| Container image metadata | The image's own labels contradict this repository | **Open — flagged 2026-09-21**: `Dockerfile` labels carry `org.opencontainers.image.licenses="BSL-1.1"` while the repository LICENSE is AGPL-3.0, the image listens on 3000 while ENV/LABEL say 8088, and the label block describes both "13 tools" and "7-tool surface". Fixing the licence wording is an F13 decision, not a docs edit |
| Generated mirrors drift | `llms.txt` still prints the retired `888` judge stage and version `v2026.07.24` | **Open** — last generated 2026-09-16; regenerate with `scripts/generate_tool_manifest.py`. The same retired label sits in a description string in `arifosmcp/constitutional_map.py` and in `tools_sot.yaml` (`stage: '666'` is correct; the prose is not), and in the pre-correction note `docs/PROMPT_666_JUDGE_DEPRECATION.md` |
| Generated discovery artifact drift | `smithery.yaml` no longer matches the kernel ABI registry — the guard itself fails | **Open — verified 2026-09-21** on a pristine `main` worktree: `scripts/sync_kernel_abi.py --check` → `Kernel ABI drift: smithery.yaml`, exit 1. Regenerate the discovery artifacts from the registry (last resync 2026-09-15, `eacf0ca01`) |
| Development test suite | One module fails collection; the suite needs a live kernel | **Open** — `tests/test_rasa_bench_10.py` raises `ModuleNotFoundError: rasa_boundary`; 7,421 tests collect otherwise; `tests/conftest.py` refuses to run without a reachable kernel at `:8088` (by design) |
| Semantic layer (Graphiti) | Knowledge graph retired from the read path | Operational gap — `graphiti_read: retired_888`, `semantic_floor: disabled` by choice (`ARIFOS_ML_FLOORS=0`) |
| Observability | Tracing partially wired | **Partial** — sovereign Postgres backend active; arifFlow FlowReceipt adapter live; OTel spans on all 8 canonical verbs; `langfuse_tracing: NOT_WIRED` after the cutover to kabarkan; caller-side trace propagation incomplete |
| Comparative benchmark | No published comparison against alternative frameworks | Open |

See [SECURITY.md](./SECURITY.md) for the threat model, known gaps and disclosure policy, and [docs/evidence/claims.yaml](./docs/evidence/claims.yaml) for the machine-readable claim registry.

---

## Who Is This For

**Operators** deploying AI agents in regulated environments who need an independent judgment layer between agent proposals and execution.

**Developers** building AI agent systems who want a policy decision point as a service.

**Evaluators and security reviewers** assessing AI governance frameworks.

**Domain builders** adapting governance to a specific field (geoscience, finance, healthcare).

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

# Install (dev tier — kernel + test tooling)
pip install -e ".[dev]"

# Run tests (needs the kernel reachable at :8088; one module fails collection — see gaps)
python -m pytest tests/ -q

# Kernel health (this Makefile target probes the kernel only)
make health

# Start the kernel
PORT=8088 arifos-mcp streamable-http   # or: PORT=8088 python -m arifosmcp.runtime --mode streamable-http
```

See [`CODEOWNERS`](./CODEOWNERS) for sovereign ownership of automation surfaces and [`CONTRIBUTING.md`](./CONTRIBUTING.md) for contribution guidelines.

### Project Structure

```
arifOS/
├── arifosmcp/          # Core kernel package
│   ├── abi/            # Capability registry and floor definitions
│   ├── constitution/   # Constitutional floor implementations
│   ├── kernel/         # Core judgment engine
│   └── VAULT999/       # VAULT999 ledger implementation
├── examples/           # Runnable governed workflow demo
├── tests/              # Test suite (pytest — constitutional + integration)
├── scripts/            # Operational tooling (incl. update_readme_sot.py)
├── docs/               # Documentation
│   ├── START_HERE.md   # External reader entry point
│   ├── QUICKSTART.md   # Verified first governed call
│   └── evidence/        # Claim registry and evidence index
└── pyproject.toml      # Package metadata
```

---

## Sister Repositories

| Repository | Purpose |
|------------|---------|
| [AAA](https://github.com/ariffazil/AAA) | Attention plane — routing, state, skill catalog, A2A gateway |
| [A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution engine after authorisation |
| [GEOX](https://github.com/ariffazil/GEOX) | Earth sciences domain evidence |
| [WEALTH](https://github.com/ariffazil/arifWEALTH) | Capital and financial intelligence |
| [WELL](https://github.com/ariffazil/WELL) | Human and machine vitality observation |
| [arifFlow](https://github.com/ariffazil/arifFLOW) | Metabolic ledger daemon — FQ monitoring, receipt ingestion |
| [FRAME](https://github.com/ariffazil/FRAME) | Independent observer — drift detection, evidence gathering (repository archived, organ live) |

**No public repository today:** FED (`:7074`) and i-ARIF. They are deployed and reachable, but their source is not published — a previous revision of this file linked to repositories that return 404. Treat their behaviour as observed from `/health` only, not as readable code.

---

## Evidence & Trust

arifOS publishes verifiable evidence for its claims. Every public claim links to an artifact that can be regenerated.

| Claim | Evidence | Status |
|---|---|---|
| MCP conformance | [CI workflow](./.github/workflows/06-mcp-conformance.yml) · [report](docs/evidence/conformance-report.json) | **Partial** — `result: PARTIAL`, per-tool schema validation deferred, results not published externally |
| ABI stability | [Drift guard](./scripts/sync_kernel_abi.py) | **Partial** — `--check` currently reports drift in `smithery.yaml` (reproduced on a pristine `main` worktree, 2026-09-21); last clean resync 2026-09-15 |
| Floor enforcement | `/health → runtime_floors_status` | **Verified** — 13/13 measured pass (live probe) |
| Vault integrity | [`scripts/verify_vault_chain.py`](./scripts/verify_vault_chain.py) | **Verified** — overall INTACT; 2 legacy breaks reported as historical |
| SBOM | [Generator](arifosmcp/arifos_sbom.py) | **Partial** — CycloneDX generated, no CVE scan, unsigned |
| Observability | [Telemetry](arifosmcp/runtime/telemetry.py) | **Partial** — Postgres + arifFlow live; tracing incomplete |
| Governance hardening | Adversarial test spec (federation-internal, not published) | **Partial** — spec written, no external audit |
| Quickstart | [Verified quickstart](./docs/QUICKSTART.md) | **Verified by the maintainer** on 2026-09-21; not yet reproduced by a stranger |

See [docs/evidence/](./docs/evidence/) for the claim registry (`claims.yaml`), the evidence index and the contracts for observability, release integrity, reproducibility and threat model.

> **Honesty principle:** we publish what passed, what failed, and what remains unknown. We do not claim maturity beyond our evidence.

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

See [SECURITY.md](./SECURITY.md) for the threat model, known vulnerabilities and disclosure policy.

---

## License

**AGPL-3.0** — GNU Affero General Public License v3.0 ([`LICENSE`](./LICENSE)).

When deployed over a network, the complete source code must be made available to all users interacting with the service, consistent with AGPL-3.0 terms. (The container image's OCI licence label does not currently agree with this — see "What Is Not Yet Proven".)

---

*Revision 2026-09-21 — audited against the live kernel, the ratified federation contract and the repository itself. Every number in this file was re-measured, not carried forward; each correction is receipted in the commit history.*

**Ditempa Bukan Diberi** — Forged, Not Given.
