<!-- CURRENT-VERIFIED-STATE :: re-probed 2026-10-10/11 UTC · do not delete -->
> ### ⚠️ Current verified state (2026-10-11) — measured, not intended
>
> Re-probed live by FI-008 on this date. This block states only what was observed; it does not replace the hand-audited manifest below.
>
> **Two properties hold end-to-end:** deterministic rejection (the judge refuses without consulting a model — `gate: hard_deterministic`, `llm_consulted: false`) and prevention of an unauthorised mutation.
>
> **Four do not:** verified actor (the signing path exists and the lane on `:18900` listens, but observed calls arrived **unsigned**; `actor_verified:false`) · receipt fidelity **on the invocation-telemetry surface** (`/var/lib/arifos/metrics/tool_invocations.jsonl`, 194,243 lines, **0 governance fields**; a call whose kernel verdict was `HOLD` was persisted as `ok:true`) · sink agreement (one event: ledger `ok:false`, organ counters omit it) · independent reconstruction (no external verifier bound).
>
> **Note on two witness surfaces:** the VAULT999 verdict ledger (`outcomes.jsonl`, 95,091 lines, 89,509 carrying a verdict/decision field) is a **different object** from the invocation-telemetry ledger above. They share a shape and not a schema. A verdict is not transferable between them.
>
> **Floors: pass 2 · fail F2/F11/F12/F13 · unmeasured 10. Unmeasured is not pass.**
>
> No customers, no pilots, no signed contracts, no independent benchmark, no external security audit. Current revenue value: USD 0.
>
> Claim-level audit: `AAA/forge_work/grant-arifos-reality-reforge-2026-10-11/`.

<!-- SOT-MANIFEST
last_verified: 2026-10-10T18:48:56+00:00
kernel_release: 2026.10.10-0a109ab (version from live /health, 2026-10-11) · canon version 2026.10.10-0a109ab
pypi_version: 1!2026.10.1 (release 2026.10.1) · repo tree 1!2026.10.1 (aligned)
live_commit: 00dc0199d (fix(canon): route release-version read through the single canon owner)
source_commit: 00dc0199d
built_commit: 00dc019
deployment_drift_status: aligned (source = built = deployed (drift: false))
tools_exposed_via_mcp: 8 (canonical public verbs — verified by live tools/list)
tools_canonical_superset: 25 (8 exposed + 13 hidden verbs — arif_challenge, arif_judge_deliberate, …)
tools_declared: 48 · registry_callables: 62 (includes aliases) · proven_live_24h: 3
floors_active: 2 pass · 4 fail (F2, F11, F12, F13) · 10 unmeasured — re-probed live 2026-10-11. A prior reading of 13/13 came from a threshold defect (the fallback left the gate at "score >= 0.0" — every finite score passed); that earlier pass count was a FALSE PASS, not a loss. UNMEASURED IS NOT PASS.
federation_schema: 2.0.0
mcp_protocol: advertises 2026-07-28; live initialize and the internal conformance runner settle on 2025-11-25 (supported: 2026-07-28 · 2025-11-25 · 2025-03-26 · 2024-11-05)
organs: 7 per the ratified organ table (FEDERATION_CONTRACT §2) + plane classes for boundary services (see Architecture)
vault999: healthy (457K+ records, append-only)
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
| **Agent / A2A** | MCP tools + receipts. You do not get the keys. A2A v1.0 (`a2a_version: 1.0.1` in the agent card), not v1.2 — discovery is owned by AAA, judgment by arifOS, **execution by A-FORGE** |
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
> **Versioning:** two schemes coexist. The **kernel release** (`v2026.08.01`, reported by `/health` as `release_name`) is the operational identity of the running service. The **PyPI package** uses epoch versioning (`1!…`) to outrank legacy releases: `1!2026.9.2` is what `pip install arifos` resolves to today, while this tree is `1!2026.10.1` (staged, not yet released). The kernel release is the operational truth; PyPI is the distribution truth.

### Install

```bash
pip install arifos
pip show arifos        # → Version: 1!2026.9.2 (PyPI published; repo tree 1!2026.10.1 — see gaps table)
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
# Ports: $PORT defaults to 8080; the deployed unit runs on 8088; the Docker image listens on 3000. Use 8088 for anything in this README.
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

**Demo output renders human-readable display labels over the canonical seven seals.** The wire vocabulary is always the seven seals (`SEAL`, `HOLD`, `SABAR`, `PARTIAL`, `PROVISIONAL`, `HOLD_888`, `VOID`); the labels below are presentation only and are mapped deterministically to a canonical verdict:

| Display label | Canonical verdict |
|---|---|
| `✔ ALLOW` | `SEAL` (proceed) |
| `⏸ HOLD` | `HOLD` or `SABAR` (await human / await evidence) |
| `✘ BLOCK/VOID` | `VOID` (blocked by a hard floor) |

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

> **Stage numbering (single source of truth).** The verbs follow the ratified **eight-stage** map: `000` INIT · `111` OBSERVE · `333` THINK · `444` ROUTE · `555` MEMORY · `666` JUDGE · `777` FORGE · `999` SEAL. Source: `arifosmcp/constitutional_map.py` `ToolStage` (F13-ratified 2026-07-31: JUDGE = **666**, FORGE = **777**; the old `888` stage was retired when compose was absorbed into forge). Some mirrors still carry the retired `888` label — a description string in `constitutional_map.py`, `tools_sot.yaml`, the generated `llms.txt`, and `docs/PROMPT_666_JUDGE_DEPRECATION.md` (dated 2026-07-10, predating the correction). The live wire says `666`, and this README follows the live wire. Flagged for repair in "What Is Not Yet Proven".

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
| **PROVISIONAL** | Time-limited authorisation, expires or downgrades to PARTIAL/HOLD | Proceed with expiry timer | Auto-revoke at `valid_until`; no extension without re-judging |
| **SABAR** | Not yet decidable — reality hasn't finished speaking | Wait for evidence | Retry permitted later; distinct from HOLD |
| **HOLD** | Insufficient evidence, or human approval required | Wait for human | Pause; await a human decision |
| **HOLD_888** | Immediate sovereign escalation | Stop — the sovereign decides | Escalate to F13 |
| **VOID** | Blocked by a hard constitutional floor | Blocked | Stop; the constraint must be resolved |

Seven seals, ordered and non-compensatory (lattice at top of section). **The diagram below shows the five common verdicts for width; `PROVISIONAL` and `HOLD_888` are omitted from the diagram but present in the lattice and table.**

Floors are never averaged. One floor failure propagates into the verdict; there is no compensating score.

### 13 Constitutional Floors (F1–F13)

Every proposal is evaluated against 13 non-compensatory policy constraints. Canonical names and rules: [`FEDERATION_CONTRACT.md` §3](./FEDERATION_CONTRACT.md), `GENESIS/000_KERNEL_CANON.md`, and the constitution at `static/arifos/theory/000/000_CONSTITUTION.md`.

| Floor | Name | Rule | Pass condition |
|---|---|---|---|
| F1 | AMANAH | Reversible first. Irreversible → 888_HOLD unless the sovereign acknowledges | Score ≥ threshold (higher = better) |
| F2 | TRUTH | P(truth) ≥ 0.99. Cheap claims = VOID. Evidence carries an OBS/DER/INT/SPEC label | Score ≥ threshold (higher = better) |
| F3 | TRI-WITNESS | W₃ = ∛(Human × AI × Earth) ≥ 0.75 at judgment time (floor for admissibility; W³ ≥ 0.95 is the additional bar for SEAL) | Score ≥ threshold (higher = better) |
| F4 | CLARITY | ΔS ≤ 0 — every output reduces entropy, never adds it | Score ≥ threshold (higher = better) |
| F5 | PEACE² | Non-destructive power — block harm and extraction | Score ≥ threshold (higher = better) |
| F6 | EMPATHY (operational: MARUAH) | Protect the weakest stakeholder; dignity is not tradeable | Score ≥ threshold (higher = better) |
| F7 | HUMILITY | Ω₀ ∈ [0.03, 0.05]. No fake certainty | **In-band [0.03, 0.05] = pass; outside = fail** |
| F8 | GENIUS | G ≥ 0.80 for complex actions — the simplest correct path | Score ≥ threshold (higher = better) |
| F9 | ANTIHANTU | No deception, manipulation, or consciousness claims | **Lower = better (lower ceiling = less manipulation)** |
| F10 | ONTOLOGY | AI-only ontology. A soul claim is VOID; map it to harness content | Score ≥ threshold (higher = better) |
| F11 | AUDITABILITY | Every decision logged, inspectable, attributable | Score ≥ threshold (higher = better) |
| F12 | RESILIENCE | Injection defence. Input risk < 0.85 | **Lower = better (lower = less injection surface)** |
| F13 | SOVEREIGN | Human veto is FINAL. The harness switch belongs to the human | Score ≥ threshold (higher = better) |

**Three semantic classes — verified by the live unit on 2026-09-21:**
- **Score floors** (F1–F6, F8, F10, F11, F13): higher = better. Score ≥ canonical threshold.
- **Band floors** (F7): in-band `[0.03, 0.05]` = pass; outside = fail. 0.02 fails.
- **Ceiling floors** (F9, F12): lower = better. Value below canonical ceiling.

W₃ has two named thresholds: **W₃ ≥ 0.75** is the floor for admissibility; **W₃ ≥ 0.95** is the additional bar for SEAL. Between them a proposal can be `PARTIAL` or `HOLD`, never `SEAL`.

Three naming notes, so a reader can reconcile this table with the wire:

- **F6 has two canonical names by design** — `EMPATHY` in the public register, `MARUAH` in the kernel, logs and receipts. Both are correct; the bridge is documented in `GENESIS/000_KERNEL_CANON.md` §3.4. Public surfaces render EMPATHY.
- **The live runtime keys F10–F13 as `L10`–`L13`** in `/health → runtime_floors`. Same floors, different key prefix.
- **Lower-is-better floors** are reported as raw measurements, not as failures: live values on 2026-09-21 were F7 = 0.04, F9 = 0.15, L12 = 0.425, and `/health → runtime_floors_status` reports 13/13 pass with every floor `measured: true`.

VAULT999 (append-only audit ledger)

Every consequential verdict, evidence chain and execution receipt is written to VAULT999 — a hash-chained, append-only JSONL ledger set, **tamper-evident by construction, not tamper-proof**.

**What it stores** is provenance, not copies. An entry carries its payload hash, entry hash, previous entry hash, trace root, actor, session, decision context and evidence references. Source payloads are not duplicated into the ledger — auditability here means provenance + integrity + reconstructability, which is both stronger and safer than copying everything forever (evidence can contain sensitive material).

**A hash chain proves internal consistency.** It does NOT prove that the chain was not recomputed by whoever controls the ledger. External anchoring — periodic publication of the chain head, or signing by a key the kernel does not hold — is not yet implemented. **Treat VAULT999 today as self-verifiable, not independently attestable.** See "What Is Not Yet Proven" for the gap row.

Measured 2026-09-21: 241,765 lines across 24 JSONL ledgers in VAULT999/ (largest: `outcomes.jsonl` 93,266 · `arifflow_sealed.jsonl` 52,056 · `apex-zen-receipts.jsonl` 30,977). **Re-counted 2026-10-11: 471,067 lines across 58 JSONL ledgers** — method: `find` including subdirectories. The header above re-stamps a **different object** (top-level `*.jsonl` glob → 457K+). **The two figures are not interchangeable; neither should be quoted without its method.** Composition: the majority is operational telemetry and receipt ingestion; constitutional verdict count is published separately (see `scripts/verify_vault_chain.py --verdict-count-only`) — a 2026-10-11 re-count found `outcomes.jsonl` at 95,091 lines, of which 89,509 carry a verdict/decision field and 344 are `HOLD`. The chain report returns overall: `INTACT` for the active ledgers, reporting 2 strict link breaks in the frozen v1 legacy ledger as historical facts rather than hiding or rewriting them. Live record count is re-stamped into the header manifest above by `scripts/update_readme_sot.py`.

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

Live-probed **2026-09-21** (UTC+08); rows marked ↻ re-probed **2026-09-30** and **2026-10-05**. Re-run the commands; static counts are not evidence.

| Surface | Status | Evidence |
|---------|--------|----------|
| Public repository | Live | GitHub [`ariffazil/arifOS`](https://github.com/ariffazil/arifOS), AGPL-3.0 |
| PyPI package | Published `1!2026.9.2` (uploaded 2026-09-15T16:42Z) | `pip install arifos` — [pypi.org/project/arifos](https://pypi.org/project/arifos/); tree is `1!2026.10.1`, unreleased |
| Live kernel | Healthy, 13/13 floors | `curl localhost:8088/health` → `status: healthy`, `floors_active: 13` |
| MCP interface | 8 exposed, 3 with a durable SUCCESS in the last 24 h (tools_loaded: 8, operational_tools: 3) | live `tools/list`; protocol advertises `2026-07-28`, negotiation settles `2025-11-25` |
| Floor enforcement | 13/13 measured pass | `/health → runtime_floors_status` (F7 = 0.04, F9 = 0.15, L12 = 0.425 lower-is-better) |
| VAULT999 ledger ↻ | Healthy, chain INTACT | `scripts/verify_vault_chain.py` → `overall: INTACT` (its own scope: the 3 active ledgers under `arifOS/VAULT999/`). The previously published "241,765 lines / 24 ledgers" named no population and matched no measured root, so it is withdrawn rather than refreshed. Census **2026-09-30T07:44:35Z** — two different, both-correct denominators: (a) recursive whole-estate, `find <root> -name '*.jsonl'` then count non-blank lines: `arifOS/VAULT999` 60/354,283 · `/var/lib/arifos/vault` 7/20,986 · `~/.local/share/arifos/vault999` 66/16,555 · `AAA/VAULT999` 1/238 = **134 ledgers / 392,062 lines**; (b) the generated SOT-MANIFEST header above reports `342K+ records` because `scripts/update_readme_sot.py` counts only top-level `VAULT999/*.jsonl` in this repo, non-recursively (measured 24 files / 342,582 lines), excluding the subdirectory ledgers (a) includes. Neither is wrong; they have different populations. The vault is append-only and live, so every figure here is a snapshot — quote the timestamp with it. |
| Source / build / deploy ↻ | Aligned — no drift | `source_commit = built_commit = deployed_commit = 27409ddbf`; `/health → drift: false`, `runtime_matches_build: true`, `deployment_drift_status: aligned`. Release provenance is re-attested on every `scripts/deploy-release.sh` run (`VERDICT: PASS`, strict) — quote the live value, not this one |
| Contract schema | 8/8 published, no drift | `contract_status: {tool_count: 8, schemas_complete: true, contract_drift: false}` |
| Federation surfaces | 10/11 reachable without drift; WELL degraded (drift: true) | ports 8088 · 3001 · 7071 · 7072 · 8081 · 18082 · 18083 · 7073 · 7074 · 18085 · 18102; WELL at `127.0.0.1:18083/health` returns HTTP 200 but reports `drift: true`, so the row honestly reads 10/11 healthy + 1 degraded |
| Machine-readable ↻ | tools.json live, 56,224 bytes | [tools.json](https://arifos.arif-fazil.com/tools.json) · [llms.txt](./llms.txt) (generated mirror — see gaps) · [CITATION.cff](./CITATION.cff) |
| Scanner attestation | 148 rules · 0 unauthorised mutations; 26/26 GRADE A | [mcp.arif-fazil.com/proof/](https://mcp.arif-fazil.com/proof/) |

## What Is Not Yet Proven

Every row names its own gap. Repairing a claim by substituting a stronger one is worse than the stale claim it replaced.

| Gap | Risk | Status |
|---|---|---|
| Independent security audit | Adversarial bypass testing not published | **In progress** — external researcher reviewing since 2026-08-25. First finding (fetch-surface SSRF) fixed, released in `1!2026.9.1`. A second scan (2026-09-15/16, mcp-safeguard) found 2 confirmed issues: Cypher injection (graph-wipe risk, HIGH — key whitelist landed in `l5_sovereign_forge.py`) and a fastmcp decode-after-match path traversal (MEDIUM — arifOS-side containment guard landed in `atlas333.py`; upstream report pending). Both are at code level; neither has a released-artifact verdict. See [SECURITY.md](./SECURITY.md#known-gaps) |
| **Sovereign-binding of irreversible acknowledgement** | **`ack_irreversible: true` and `actor_signature` are transported as payload fields.** Nothing published demonstrates that a human signature is bound to `(transaction_hash ‖ state_hash ‖ nonce)`, single-use, scoped to one organ, and unforgeable by the proposing agent. | **Open** — design drafted ([`docs/judgment-integrity-2026-09-22/ARIFOS_AUTHORITY_SERVICE_DESIGN.md`](./docs/judgment-integrity-2026-09-22/ARIFOS_AUTHORITY_SERVICE_DESIGN.md)), not implemented. Until then, F13 is enforced by convention and band-gating, not by cryptographic transaction binding. This matches OWASP transaction-authorization practice: credentials unique per operation and bound to significant transaction data, not to session. |
| **Ledger head not externally anchored or signed** | **A hash chain held entirely by one party detects external modification but not wholesale rewrite by the holder**, because the holder can recompute every hash. | **Open** — periodic publication of chain head, or signing by a key the kernel does not hold, is not implemented. VAULT999 today is self-verifiable, not independently attestable. |
| Third-party evaluation | No external reviewer has published findings | In progress — one review under way since 2026-08-25; nothing published |
| Reproducible demo by strangers | Onboarding path not independently tested | **Partial** — `examples/enterprise_operations_demo.py` runs in-process and is verified here; no stranger has reproduced it unaided |
| Enterprise deployment | No production customer reference | Open |
| Standards conformance | MCP/A2A conformance results not published externally | **Partial** — CI `06-mcp-conformance.yml`; [conformance report](docs/evidence/conformance-report.json) says `result: PARTIAL`, `spec_version: 2025-11-25`, with per-tool schema validation DEFERRED |
| SBOM and signed releases | Supply-chain integrity unverified externally | **Partial** — CycloneDX generator + `sbom` job on publish; no signing, no CVE scan |
| Container image metadata | The image's own labels contradict this repository | **Fixed 2026-10-05** (`8372cecc3`) — labels aligned to measured reality: `licenses` → `AGPL-3.0` (matches the repo LICENSE file and PyPI metadata — both said AGPL; the BSL-1.1 label was the outlier), tool counts 13/7 → `8` (`tools_loaded: 8` measured), `PORT` env + MCP port label → `3000` (CMD/EXPOSE/HEALTHCHECK all listen on 3000 by design for Manufact cloud compat), image version → `2026.10.1` |
| Generated mirrors drift | `llms.txt` still prints the retired `888` judge stage and version `v2026.07.24` | **Fixed 2026-10-05** (`8372cecc3`) — `KERNEL 888` prose corrected to `KERNEL 666` in `arifosmcp/constitutional_map.py` and `tools_sot.yaml`; mirrors regenerated via `scripts/generate_tool_manifest.py`. The version line is now DERIVED from installed package metadata in the generator (was hardcoded `v2026.07.24`), so it cannot go stale again. Live tools/list confirms `KERNEL 666` post-deploy `a98af0d` |
| Generated discovery artifact drift | `smithery.yaml` no longer matches the kernel ABI registry — the guard itself fails | **Fixed 2026-10-05** (`8372cecc3`) — regenerated from the ABI registry: `Kernel ABI verified: 8 capabilities, 6 public tools`, `--check` exit 0 |
| Development test suite | The suite needs a live kernel | **Fixed 2026-09-25 (collection)** — stale 269-line duplicate `tests/test_rasa_bench_10.py` removed (canonical 632-line bench lives at `/root/.hermes/policy/test_rasa_bench_10.py` where `rasa_boundary` resolves in-place); **7,668 tests collect clean** (re-measured 2026-10-05, was 7,622); `tests/conftest.py` still refuses to run without a reachable kernel at `:8088` (by design). Collection ≠ green: the identity/authority/session/attestation subset carries **34 pre-existing failures** against 321 passes (measured 2026-09-30 on a pristine `main` worktree), so quote a failure *set*, never a bare pass count |
| Semantic layer (Graphiti) | Knowledge graph retired from the read path | Operational gap — `graphiti_read: retired_888`, `semantic_floor: disabled` by choice (`ARIFOS_ML_FLOORS=0`) |
| Observability | Tracing partially wired | **Partial** — sovereign Postgres backend active; arifFlow FlowReceipt adapter live; OTel spans on all 8 canonical verbs; `langfuse_tracing: NOT_WIRED` after the cutover to kabarkan; caller-side trace propagation incomplete |
| Comparative benchmark | No published comparison against alternative frameworks | Open |
| Maintainer continuity | Single sovereign, single reviewer; no succession or key-recovery procedure published | **Open — relevant to any institutional adoption** |
| `__version__` strings are stale | Module `__version__` lags kernel release; readers may quote it incorrectly | **Closed 2026-10-05** — `arifosmcp/__init__.py` derives `__version__` from installed package metadata (`_pkg_version("arifos")`), and the live wheel reports `1!2026.10.1`, identical to `pyproject.toml`. Submodule `__version__` strings (`webmcp`, `entropy_kernel`, `federation`, `hexagon`) are component tags, not kernel releases — they track their own artifacts |
| **Identity registry exists in two copies** | A one-sided edit ships a split-brain identity registry: `contracts/identity.py` (imported by ~9 runtime sites) and `arifosmcp/contracts/identity.py` (~3 sites, and the one the wheel ships) had already diverged — the packaged copy was missing the `I_ARIF` entry added by the 2026-08-21 Seal C fix and the `GEMINI`/`FI-004` lane entry, so `i-arif` and `agy/FI-004` resolved differently depending on which copy a module imported | **Mitigated 2026-09-30, consolidation still open** — both copies were re-aligned to 18 actors (`7796ec701`) and `tests/contracts/test_identity_registry_no_divergence.py` (31 tests) now fails on any drift in key set, aliases, normalization of 20 probe ids, or a missing `actor_lookup_candidates`; it was falsified against the pre-alignment state, where it caught exactly `gemini`, `i-arif` and `agy/FI-004`, so it is not vacuous. **Open:** pick one owner — migrate the 9 imports to `arifosmcp.contracts.identity` and retire the top-level copy, or keep both and keep the tripwire. Not decided here because it is a source-of-truth call, not a bug fix |
| **Authority floor depended on a pointer stub and an unshipped package** | Two independent faults capped every non-exempt agent at `OBSERVE_ONLY`, so mutation-capable citizens silently lost tool access — surfacing as the "tool inexplicably unauthorized" class. (a) Boot Q5 read `identity.toml` with `_file_read(A) or _file_read(B)`; both are 101-byte DERIVED stubs reading *"superseded by: /root/AAA/identity.toml"*, and a non-empty stub short-circuits the `or`, so the canonical F13 payload was never read → `Q5=NO` → `boot_state=FAIL` → `_apply_boot_gate` demoted `LIMITED_MUTATE`/`FULL`. Authority was in practice coming from the 29-entry exemption list, not from attestation. (b) `contracts*` was absent from the wheel `include`, so the kernel's identity path resolved against a July-24 leftover. A bare `except ImportError: pass` in `_apply_boot_gate` hid a wrong module path, making the 2026-08-21 alias bypass dead code | **Fixed 2026-09-30** — `5cc357974` (`_read_identity_toml_chain()` joins all candidates and follows `superseded by:` pointers; Q5 `NO`→`PARTIAL`, which passes the gate since the shipped predicate is `boot_state != "FAIL"`), `2eaec19c2`+`d43b7fece` (one shared `exempt_actor_band()` resolver replacing 7 raw-string membership tests, so the documented `name/FI-nnn` form resolves), `69175c0ec` (patched the copy production imports; boot-gate bypass moved off the fragile import), `27409ddbf` (`contracts*` ships). Verified live: 17/17 AAA identities bind `SEAL` + `mutation_allowed=True` + `VERIFIED` with an ACT carrying `LIMITED_MUTATE` and all 9 verbs, 0 boot demotions, and the control `nobody/FI-999` is still refused — trust boundary unchanged, exempt membership still does not auto-verify. **The generalizable defect: a stand-in served where the payload belonged, and a fail-silent `except` hid it — three times in one session.** |

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
├── arifosmcp/          # Core kernel package                    [wheel root]
│   ├── abi/            # Capability registry and floor definitions
│   ├── constitution/   # Constitutional floor implementations
│   ├── contracts/      # Packaged copy of the identity/verdict contracts
│   ├── kernel/         # Core judgment engine
│   └── VAULT999/       # VAULT999 ledger implementation
├── arifos/             # Phase 3 identity/consent namespace      [wheel root]
├── contracts/          # Runtime contract package — identity registry,
│                       # gateway discovery, verdicts, continuity, envelopes.
│                       # Imported by 5 runtime files; see note.    [wheel root]
├── core/               # Load-bearing legacy root (session.py imports
│                       # core.shared.types)                      [wheel root]
├── schemas/            # INIT v2 schemas (F13-ratified 2026-09-20) [wheel root]
├── examples/           # Runnable governed workflow demo
├── tests/              # Test suite (pytest — constitutional + integration)
├── scripts/            # Operational tooling (incl. update_readme_sot.py)
├── docs/               # Documentation
│   ├── START_HERE.md   # External reader entry point
│   ├── QUICKSTART.md   # Verified first governed call
│   └── evidence/        # Claim registry and evidence index
└── pyproject.toml      # Package metadata — [wheel root] marks
                        # packages.find.include
```

**The five `[wheel root]` entries are exactly what ships.** Until 2026-09-30 this
tree listed only `arifosmcp/`, and `contracts*` was absent from
`[tool.setuptools.packages.find].include` — while the runtime imported `contracts.*`
at **10 import statements across 5 files** under `arifosmcp/` (`contracts.identity`
6, `verdicts`/`continuity`/`artifacts`/`envelopes` 1 each), plus
`arifosmcp/contracts/__init__.py` doing `from contracts.identity import *`.
Scope matters: a repo-wide grep reports ~4× that, because `build/lib/` holds a
1,402-file duplicate tree and `tests/` adds its own imports (`gateway_discovery` 7,
all of them tests — 0 in the runtime). Those inflated figures were what an earlier
revision of this note published; corrected 2026-09-30. Production resolved those
imports only because pip does not delete a pre-existing unrelated
`site-packages/contracts/` leftover; a fresh venv or a machine migration would have
raised `ImportError` at kernel import time. Fixed in `27409ddbf`. **An incomplete
structure diagram is not a cosmetic gap — it is how an unshipped, runtime-critical
package stays invisible.**

`contracts/` and `arifosmcp/contracts/` are two copies of the same contract
modules and had already diverged. They are kept in agreement by
`tests/contracts/test_identity_registry_no_divergence.py`; consolidating them into
one owner is still open (see gaps).

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

**Independent audit pass 2026-09-22** (Copilot external, mode ENTERPRISE). Findings A, B, C, D, E, F, G, H, I, K, L, N — all four blocking contradictions + the two highest-leverage gaps (G sovereign-binding, H ledger anchoring) — corrected in this revision. M (TOC/badges) and a per-pass signature remain open as structural polish. See commit history for per-finding receipts.

**Ditempa Bukan Diberi** — Forged, Not Given.
