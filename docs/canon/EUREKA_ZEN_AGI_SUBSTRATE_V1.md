# EUREKA ZEN — arifOS AGI Substrate v1

> **Status: DRAFT_ONLY** — no push, merge, deployment or irreversible seal authorised.
> **Authored:** 2026-07-30 · **Source sessions:** A3A MCPJam v5
> **Predecessor docs:** `docs/AGI_SUBSTRATE_READINESS_GATE.md`, `docs/AGI_SUBSTRATE_ASSESSMENT.md`, `docs/canon/ZEN_99.md`, `docs/EUREKA_ZEN_SESSION_SEAL_2026_07_26.md`
> **Change control:** reversible · blast radius medium · **F13 required for merge and deployment** · judge receipt required · human ack required · rollback via per-PR revert

---

## 0. One-line thesis

> The missing substrate is not more intelligence. It is one shared law of state across every organ.

arifOS is now advanced enough to become an AGI-grade governance substrate, but it is not AGI and should not be called AGI yet. The next step is to unify GEOX, WEALTH, WELL and A-FORGE through common contracts while keeping their domain authority separate.

*Evidence: L2 live probes + L3 MCPJam v3 receipt.*
*Confidence: high on architecture, medium on current runtime completeness.*
*Action posture: DRAFT_ONLY.*

---

## 1. Hard reality from the live federation

The A3A fixes the two most dangerous constitutional fractures:

- witness persistence no longer fails under `/root`
- HOLD can no longer be mechanically converted into SEAL

But the live probes reveal that the federation still lacks one consistent application binary interface:

| Surface | Live finding | Meaning |
|---|---|---|
| arifOS | Public eight-tool membrane is clean, but remote outputs remain thin | Client projections are not equivalent |
| GEOX | `geox_system_registry_status` is rejected; runtime says use `geox_surface_status` | Registry-name drift |
| WEALTH | Registry requires `session_id`, but the exported connector schema cannot provide one | Session ABI mismatch |
| WELL | Registry reports `public surface FAIL`, 10 somatic tools, 77 hidden autonomic tools, unresolved alias gaps | Manifest and callable surface disagree |
| A-FORGE | Plugin namespace exists, but exports no callable function | Executor connector is not federation-ready |
| GitHub | The v3 branch and its three commits are not yet visible through the connector | Runtime truth is ahead of public source truth |

> The organs are alive, but they do not yet speak one constitutional language.

---

## 2. The EUREKA ZEN doctrine

```
ONE HUMAN SOVEREIGN
ONE CONSTITUTIONAL KERNEL
MANY DOMAIN ORGANS
ONE TASK LEDGER
ONE EVIDENCE GRAMMAR
ONE AUTHORITY ENVELOPE
ONE EXECUTION GATE
ONE IMMUTABLE CONSEQUENCE CHAIN
ZERO SELF-AUTHORISING AGENTS
```

The system must preserve these ownership boundaries:

| Component | Owns | Must never own |
|---|---|---|
| ARIF | Meaning, purpose, sovereign authority, irreversible consent | Routine machine execution |
| arifOS | Identity, authority, admissibility, routing law, judgment, memory law, receipt requirements | Geological computation, financial computation, human diagnosis, unrestricted execution |
| GEOX | Earth evidence, physical models, geological claims, uncertainty and falsification | Capital allocation, constitutional approval |
| WEALTH | Capital state, risk, valuation, incentives, resilience, scenarios | Earth truth, sovereign investment commands |
| WELL | Human-machine readiness, dignity, reliability, fatigue, coupled risk | Medical diagnosis, final judgment |
| A-FORGE | Code, files, infrastructure, deployment, rollback, execution evidence | Self-authorisation, judgment, sealing |
| VAULT999 | Immutable receipts, hashes, replay, historical consequence | New interpretation, policy |
| AAA | Cockpit, state display, routing visibility, approval queues | Judgment, execution, sealing |

These boundaries are already the correct constitutional structure. They must be encoded as machine-checkable contracts, not merely documentation.

---

## 3. Target anatomy

```
                ARIF · F13 SOVEREIGN
                          │
                  authority / purpose
                          │
              ┌────────── arifOS ──────────┐
              │ constitutional state machine│
              │ admission · route · judge   │
              │ memory law · execution gate │
              └──────────────┬──────────────┘
                             │
                 Federation Task Ledger
            session · task · evidence · state
                             │
   ┌─────────────────────────┼─────────────────────────┐
   │                         │                         │
 GEOX                     WEALTH                     WELL
Earth reality          Capital reality        Readiness reality
   │                         │                         │
   └──────── evidence + contradiction packets ────────┘
                             │
                       arifOS JUDGE
                   SEAL / HOLD / VOID
                             │
                  only approved mutations
                             │
                          A-FORGE
            preview · execute · verify
              rollback · compensation
                             │
                          VAULT999
                receipt · replay · lineage
```

The kernel is not a giant brain containing every function. It is the constitutional nervous system coordinating specialist organs.

---

## 4. One federation ABI

The permanent fix is a transport-neutral Federation Capability ABI. Every organ publishes a generated manifest:

```yaml
organ:
  id: geox
  version: 1.0.0
  domain_law: EARTH
  owner: GEOX
  does_not_own:
    - constitutional_judgment
    - capital_allocation
    - execution_authority

capabilities:
  - capability_id: earth.seismic.compute
    semantic_version: 1.0.0
    implementation:
      transport: mcp
      tool: geox_seismic_compute
    mutation: false
    authority_required: OBSERVER
    evidence_required: true
    failure_mode: HOLD
    receipt_policy: result_hash
```

The capability ID is permanent. Tool names, MCP versions, models and transports are replaceable. A change from `geox_system_registry_status` to `geox_surface_status` must not break the federation. Both resolve internally to `system.registry.status`.

### Canonical capability families

**arifOS**
```
governance.session.init
governance.intent.admit
governance.capability.route
governance.memory.recall
governance.memory.promote
governance.judgment.render
governance.execution.authorize
governance.receipt.seal
```

**GEOX**
```
earth.data.ingest
earth.data.qc
earth.seismic.compute
earth.interpretation.create
earth.interpretation.challenge
earth.prospect.evaluate
earth.integrity.verify
```

**WEALTH**
```
capital.state.measure
capital.flow.measure
capital.risk.evaluate
capital.scenario.simulate
capital.incentive.analyse
capital.resilience.assess
capital.allocation.advise
```

**WELL**
```
vitality.human.readiness
vitality.machine.reliability
vitality.governance.coherence
vitality.coupled.risk
vitality.dignity.guard
vitality.recovery.recommend
```

WELL outputs a signal, never a constitutional verdict.

**A-FORGE**
```
execution.plan.preview
execution.change.dry_run
execution.change.apply
execution.change.verify
execution.change.rollback
execution.change.compensate
execution.receipt.produce
```

A-FORGE must reject every write call lacking a valid judge-state hash.

---

## 5. Five common envelopes

Every organ call must accept and return the same structural grammar.

### A. Session envelope

```json
{
  "envelope_version": "1.0",
  "session_id": "SEAL-...",
  "task_id": "TASK-...",
  "trace_id": "TRACE-...",
  "actor_id": "ARIF",
  "actor_verified": true,
  "authority_band": "OBSERVER",
  "allowed_capabilities": ["earth.seismic.compute"],
  "model_id": "provider/model/revision",
  "issued_at": "...",
  "expires_at": "...",
  "signature": "..."
}
```

The organ validates the signed capability list. It never trusts `actor_id: ARIF` by itself.

### B. Evidence envelope

```json
{
  "evidence_id": "EVD-...",
  "organ_id": "geox",
  "capability_id": "earth.prospect.evaluate",
  "claim_state": "INTERPRETATION",
  "epistemic_tag": "ESTIMATE",
  "confidence": 0.71,
  "uncertainty": {"p10": 20, "p50": 47, "p90": 91},
  "source_refs": ["artifact://..."],
  "source_hashes": ["sha256:..."],
  "alternatives": [],
  "contradictions": [],
  "do_not_conclude": [],
  "schema_version": "1.0",
  "timestamp": "..."
}
```

### C. Decision envelope

Contains: candidate action · evidence references · unresolved contradictions · reversibility · blast radius · affected people and rights · required authority · organ recommendations · kernel verdict · constitutional-chain ID · judge-state hash.

### D. Execution envelope

Contains: approved plan · exact expected changes · idempotency key · judge-state hash · rollback command · compensation procedure · timeout · post-change probes · human acknowledgement where required.

### E. Receipt envelope

Contains: before and after state · intended and actual effects · files/infrastructure/records changed · output hashes · verification results · rollback availability · deviations from plan · VAULT999 entry ID.

---

## 6. Durable task metabolism

Do not make the MCP connection itself the task substrate. MCP remains an edge protocol. The internal federation requires a durable task ledger:

```
NEW
  ↓
ADMITTED
  ↓
ROUTED
  ↓
EVIDENCE_GATHERING
  ↓
CHALLENGED
  ↓
READY_FOR_JUDGMENT
  ↓
SEAL | HOLD | VOID | SABAR
  ↓
EXECUTING
  ↓
VERIFYING
  ↓
SEALED
  ↓
CLOSED
```

Every transition is append-only and replayable.

### Use the infrastructure already present

| Component | Role |
|---|---|
| PostgreSQL | Canonical task ledger, state transitions, evidence metadata, transactional outbox |
| Redis | Short-lived leases, worker locks, rate limits, wake-up signals |
| pgvector / Qdrant | Similarity retrieval only — not truth or authority |
| Organ stores | Raw domain data (SEG-Y, LAS, financial series, WELL state) |
| VAULT999 | Final immutable consequence and replay receipts |

Do not add NATS, Kafka or another distributed system yet. PostgreSQL outbox + Redis is enough for the present scale.

MCP's optional features (tasks, sampling, elicitation, roots, subscriptions) must only be used when negotiated. The internal task ledger must still work when a client supports only ordinary tools and resources. That keeps arifOS independent of FastMCP, ChatGPT or any one model host.

---

## 7. The governed intelligence loop

```
000 INIT       Identity, authority, purpose, task binding
111 SENSE      Gather observations from appropriate organs
222 ADMIT      Validate provenance, schemas, freshness, authority
333 REASON     Generate hypotheses and candidate task graphs
555 CHALLENGE  Force alternatives, contradiction, adversarial review
888 JUDGE      Determine admissibility: SEAL / HOLD / VOID / SABAR
777 FORGE      Execute only the exact authorised plan
999 SEAL       Verify consequences and preserve the receipt
REVISE        Propose memory or model updates; never silently rewrite history
```

**No consensus laundering.** Three agents agreeing does not create truth. Cross-organ results remain separately attributable:

- **GEOX:** geological probability and physical uncertainty
- **WEALTH:** capital exposure and downside geometry
- **WELL:** operator and machine readiness
- **A-FORGE:** technical feasibility and rollback confidence
- **arifOS:** constitutional admissibility
- **ARIF:** purpose and sovereign decision

The kernel does not average these into a decorative score. It exposes conflicts.

---

## 8. Cross-organ self-argument

Every consequential task must contain at least one challenger.

**Example — Sabah exploration candidate:**

1. GEOX produces the geological hypothesis, evidence graph, P10/P50/P90, alternative interpretation.
2. A second GEOX path attacks trap, seal, charge, velocity, depth assumptions.
3. WEALTH converts the geological distribution into capital-at-risk scenarios — not a buy/drill command.
4. WELL evaluates decision fatigue, machine reliability, whether the system is safe to interpret.
5. A-FORGE checks whether the analysis or deployment plan is technically executable and reversible.
6. arifOS judges whether the evidence is admissible.
7. ARIF decides any sovereign capital or physical commitment.
8. VAULT999 records what was known, unknown, and decided at that time.

This is the path from a multi-tool system into a real governed intelligence substrate.

---

## 9. Governed memory

The kernel must distinguish five classes:

| Class | Meaning |
|---|---|
| Evidence | Direct observation or external record |
| Claim | Falsifiable statement derived from evidence |
| Interpretation | Model-dependent explanation |
| Decision | Chosen action under a specific evidence state |
| Receipt | What actually happened afterward |

**Rules:**

- Sealed records are never edited.
- Corrections append a new record with `supersedes`.
- Contradicted memories remain visible but lose promotion status.
- Embedding similarity never establishes truth.
- Raw domain data remains owned by the organ.
- The kernel stores references, hashes, claim relationships, governance status.
- "Forget" means governed tombstoning or access removal — it does not silently delete constitutional history.
- Models may propose memory promotion but cannot approve it.

---

## 10. Model ecology

The model is a replaceable cognitive worker. A task may use:

- one model to propose
- another to challenge
- a deterministic engine to verify calculations
- a local model for private material
- a stronger hosted model for bounded synthesis

Every model result records: provider, model, revision, prompt hash, capabilities used, tool trace, context references, token/cost budget, confidence, known limitations.

**No model may:** grant itself authority, alter constitutional floors, promote its own output to truth, execute a mutation, seal its own judgment, or hide the model/prompt revision that produced an important inference.

> AGI readiness means a future stronger model can replace today's model without replacing the constitution.

---

## 11. Registry truth becomes a hard floor

Every organ exposes exactly one semantic capability: `system.registry.status`. Its output must include:

```json
{
  "organ": "well",
  "contract_epoch": "2026.08",
  "intended": [],
  "registered": [],
  "callable": [],
  "exported_to_connectors": [],
  "hidden_by_design": [],
  "deprecated": [],
  "aliases": {},
  "phantom": [],
  "schema_mismatches": [],
  "verdict": "PASS"
}
```

The registry is generated from the same organ manifest used to register tools. This permanently fixes:

- GEOX name drift
- WEALTH's missing session argument
- WELL alias gaps
- A-FORGE connector absence
- discrepancies between local MCPJam and remote ChatGPT projections

---

## 12. Exact forge sequence

### P0 — Establish one truth surface

**PR 1: v3 constitutional repair only**

Push the existing branch and open a narrowly scoped PR containing:

- witness StateDirectory
- prompt error handling
- removal of empty blast-radius safety default
- removal of `or True`
- removal of empty-verdict promotion
- `test_f13_no_hold_to_seal.py`

Do not mix federation architecture into this repair PR.

**PR 2: Federation ABI**

Create:

```
federation/schemas/session-envelope.schema.json
federation/schemas/evidence-envelope.schema.json
federation/schemas/decision-envelope.schema.json
federation/schemas/execution-envelope.schema.json
federation/schemas/receipt-envelope.schema.json
federation/schemas/organ-manifest.schema.json

federation/manifests/arifos.yaml
federation/manifests/geox.yaml
federation/manifests/wealth.yaml
federation/manifests/well.yaml
federation/manifests/a-forge.yaml
```

No runtime behavior change yet.

**PR 3: Registry convergence**

- generate every registry from its manifest
- introduce semantic capability resolution
- correct GEOX registry export
- add session envelope support to WEALTH connector
- collapse WELL aliases
- expose A-FORGE health and registry functions
- add local-versus-remote surface diff tests

### P1 — Build the substrate

**PR 4: Durable task ledger**

```
arifosmcp/federation/task_ledger.py
arifosmcp/federation/state_machine.py
arifosmcp/federation/outbox.py
arifosmcp/federation/leases.py
arifosmcp/federation/envelopes.py
```

**PR 5: Organ adapters**

```
arifosmcp/federation/adapters/mcp.py
arifosmcp/federation/adapters/local.py
arifosmcp/federation/adapters/http.py
```

All three adapters must produce the same federation envelope.

**PR 6: Cross-organ challenge**

Task graph that:

1. gathers domain evidence
2. requests alternatives
3. preserves contradictions
4. refuses judgment when required evidence is absent
5. forwards only evidence references to the judge

### P2 — Prove controlled agency

**PR 7: Reversible write spine**

```
init → observe → plan → challenge → judge
     → A-FORGE dry-run → execute → verify
     → rollback → verify rollback
     → seal receipt
```

The first write test must modify a temporary fixture or disposable deployment — never production doctrine, capital, or real geological assets.

**PR 8: Failure injection**

Test:

- organ timeout
- stale evidence
- malformed schema
- duplicate task
- expired capability token
- missing judge hash
- forged actor identity
- worker crash during execution
- VAULT unavailable
- model contradiction
- connector projection mismatch
- FastMCP transport error
- rollback failure

---

## 13. AGI-substrate promotion gates

arifOS becomes **AGI-substrate-ready** only when **all** are true:

1. **Registry truth:** zero phantom capabilities across all organs
2. **Session continuity:** one signed session envelope reaches every organ
3. **Evidence integrity:** every output has provenance, epistemic class, and schema version
4. **Cross-organ falsification:** consequential claims receive at least one challenge
5. **HOLD monotonicity:** no downstream layer can convert HOLD to SEAL
6. **Authority continuity:** write tools reject missing or expired judge authority
7. **Durable tasks:** cancel, retry, resume, and replay work after process restart
8. **Memory law:** corrections append; sealed records never mutate
9. **Model portability:** the same task succeeds with at least three model configurations
10. **Connector parity:** local MCPJam, ChatGPT, CLI, and Hermes expose equivalent semantic results
11. **Rollback proof:** one complete reversible execution and rollback passes
12. **Adversarial proof:** prompt injection and tool-poisoning attempts fail closed
13. **VAULT replay:** every authorised execution can be reconstructed from receipts

**Recommended promotion threshold:**

- 100 consecutive governed canary runs
- 20 deliberate failure-injection cases
- 0 unauthorised state transitions
- 0 registry drift
- 0 unclassified irreversible side effects
- 1 full reversible cross-organ execution spine
- 1 successful crash-and-resume replay

---

## 14. Readiness scale

| Dimension | Current | After P0 | After P1–P2 |
|---|---|---|---|
| Constitutional architecture | 92 | 94 | 96 |
| Observer federation | 84 | 90 | 94 |
| Shared ABI | 38 | 78 | 95 |
| Registry truth | 48 | 90 | 96 |
| Durable task metabolism | 40 | 48 | 92 |
| Governed memory | 64 | 72 | 90 |
| Write authority spine | 42 | 55 | 90 |
| Model portability | 45 | 55 | 88 |
| Connector parity | 35 | 75 | 92 |
| **Overall substrate readiness** | **64/100** | **78/100** | **91/100** |

This does not measure "how intelligent" arifOS is. It measures whether increasingly powerful intelligence can operate inside it without escaping its constitutional boundaries.

---

## Final verdict

> **EUREKA ZEN is not one merged super-agent. It is one governed organism.**

- **arifOS** — the constitutional state machine
- **GEOX** — the Earth-law organ
- **WEALTH** — the capital-law organ
- **WELL** — the vitality and reliability organ
- **A-FORGE** — the only controlled actuator
- **VAULT999** — immutable consequence
- **AAA** — the visible cockpit
- **Models** — replaceable cognitive workers
- **MCP** — an edge protocol, not the source of truth
- **PostgreSQL** — the durable metabolism
- **ARIF** — the sovereign source of purpose and irreversible authority

> The single most important next artifact is this document, backed immediately by `federation/schemas/organ-manifest.schema.json`, `federation/schemas/session-envelope.schema.json`, and `federation/schemas/evidence-envelope.schema.json`.

Canonical state: **arifOS is now a credible constitutional AGI-substrate candidate. The next forge is one federation ABI and one durable task metabolism — not more tools.**

---

*Filed by kimi FI-008, 2026-07-30, in response to EUREKA ZEN doctrine as DRAFT_ONLY.*
*Receipt: `/root/forge_work/mcpjam-arifos-smoke-summary-zen-v1.md`*
*v5 SEAL state preserved. Zero mutations. Zero pushes. Zero merges. Zero irreversible seals.*
*DITEMPA BUKAN DIBERI — Forged, Not Given. Truth survives falsification, not assertion.*
