---
id: aaa-agentic-governance
name: AAA Agentic Governance (AAA-Cockpit, canonical)
version: "3.0.0"
description: Governed intelligence skill for AAA as the abstraction, attestation, and abduction control plane across arifOS, APEX, A-FORGE, GEOX, WEALTH, WELL, and the ariffazil profile repository. Use when the user asks to explain or design AAA, route agentic work, reduce chaos/entropy in an arifOS federation task, create AREP/task declarations, classify risk, plan multi-repo changes, review governance boundaries, or translate human intent into evidence-backed, authority-safe, recursively agentic workflows. Provides deterministic F1-F13 floor checking, bounded abduction, and FederationReceipt composition.
owner: AAA
risk_tier: low
knowledge_basis:
  physics: false
  math: true
  language: true
host_compatibility:
  - claude-code
  - codex
  - opencode
  - hermes-asi
  - apx-judge
dependencies:
  skills: []
  servers:
    - arifos (mcp_arifos_*)
  tools:
    - python3
examples:
  - "Reduce entropy in a multi-organ task → orthogonality check + floor receipt + bounded explanation"
  - "Plan tier-2 deploy → risk tier 2 + 888_HOLD gate + bounded plan with falsifier"
  - "Translate 'evaluate drilling prospect and commit capital' → GEOX→WEALTH→arifOS→F13 chain with explicit HOLD"
tests:
  - "Idempotent routing (same input → same output) via aaa_router.py"
  - "F1 AMANAH fail on tier ≥ 2 without ack_irreversible"
  - "F12 prompt-injection detection triggers HOLD before any other check"
  - "Entropy budget exceeded triggers 888_HOLD with seal_hash absent"
  - "Recursion depth > max_recursion_depth (default 3) triggers 888_HOLD"
version_lock:
  schema_version: "1"
  artifact_hash: pending
---

# AAA Agentic Governance

## Core stance

Treat **AAA** as the control-plane discipline for governed intelligence:

- **Abstraction**: reduce chaos by naming the right layer, owner, boundary, and interface.
- **Attestation**: separate verified fact from assumption, inference, hypothesis, simulation, and authority claim.
- **Abduction**: infer the best next explanation or route from incomplete evidence, then label uncertainty and test it.

Keep these three A's **orthogonal**. Do not mix them:

| Axis | Question | Output |
|---|---|---|
| Abstraction | What is the clean model/layer? | organ, interface, boundary, source of truth |
| Attestation | What is proven and by whom? | FACT / OBSERVED / DERIVED / INFERRED / HYPOTHESIS / UNVERIFIED |
| Abduction | What is the best explanation or next route? | route, hypothesis, missing evidence, validation step |

AAA is not final authority. AAA routes, displays, declares tasks, and lowers entropy. arifOS judges. A-FORGE executes approved work. Arif/F13 remains final human authority for irreversible, constitutional, external, or high-blast-radius action.

Use references only when needed:

- `references/aaa-operating-model.md` for the AAA doctrine, entropy reduction loop, and orthogonal A axes.
- `references/federation-map.md` for organ/repo roles and source-of-truth hierarchy.
- `references/governance-gates.md` for F1-F13, risk tiers, verdict language, and authority boundaries.
- `references/agentic-workflows.md` for reusable response templates and task patterns.
- `references/repo-working-rules.md` for safe repo edits, tests, and mutation guardrails.

## Golden path

For substantive AAA/arifOS/federation work, follow this loop:

1. **Declare intent**: restate the requested outcome, target organ/repo, and read-only vs mutating class.
2. **Abstract**: choose the minimal correct layer: AAA, arifOS, A-FORGE, GEOX, WEALTH, WELL, profile, or external tool.
3. **Attest**: state evidence class and source-of-truth. Label unverified claims.
4. **Abduce**: propose the best route/hypothesis and the smallest validation step.
5. **Route**: assign owner organ and secondary organs. Do not solve in the wrong layer.
6. **Reduce entropy**: remove duplicate concepts, collapse synonyms, define interfaces, and expose contradictions.
7. **Gate**: classify risk tier and identify F13/888_HOLD requirements.
8. **Compose**: give a clear operator-ready answer, plan, patch outline, or AREP declaration.
9. **Execute only when authorized**: for actual mutations, follow repo rules, preserve user changes, test, and report.
10. **Report attestation**: summarize facts, assumptions, unresolved uncertainty, gates, and next validation.

## Entropy reduction rules

Prefer clean invariants over mystical or overloaded language.

- One concept, one name. If multiple names exist, declare the canonical one and aliases.
- One owner per decision. Secondary organs may advise but must not silently decide.
- One source of truth per claim. If sources conflict, say which wins and why.
- One risk tier per action. If mixed, split the task.
- One next action. Do not produce sprawling plans unless the user asks for a full roadmap.
- Separate architecture from runtime state. A diagram is not proof of a live service.

## Routing matrix

| User intent | Primary owner | Secondary | Boundary |
|---|---|---|---|
| Explain AAA, AREP, A2A, registry, cockpit, task declaration | AAA | arifOS | AAA displays/routes; it does not judge |
| Explain F1-F13, 888_JUDGE, SEAL/HOLD/VOID, VAULT999 | arifOS | AAA | arifOS judges; do not invent final verdicts |
| Execute, build, shell, deploy, orchestrate tools | A-FORGE | arifOS, AAA | Execution needs gates; irreversible work needs approval |
| Wells, seismic, LAS, petrophysics, prospect risk | GEOX | WEALTH, arifOS | GEOX computes evidence; it does not decide drilling |
| NPV, IRR, EMV, portfolio, capital, allocation | WEALTH | GEOX, arifOS | WEALTH models value; it does not allocate alone |
| Fatigue, readiness, dignity, reliability, human substrate | WELL | arifOS | WELL observes; it does not diagnose or coerce |
| Public/professional bio | profile repo | arifOS/GEOX | Avoid unsupported personal inference |

For ambiguous tasks, route conservatively and expose the missing evidence.

## Risk tiers

- **Tier 0 read-only**: explain, summarize, inspect, classify, route, draft non-binding plans. Proceed with attestation.
- **Tier 1 reversible mutation**: docs/code patch, local tests, non-invasive refactor. Plan first; preserve user changes.
- **Tier 2 high blast radius**: deploys, secrets/auth, cross-repo architecture, external comms, budget/capital/drilling decisions. Require explicit human/F13 approval.
- **Tier 3 irreversible/atomic**: data deletion, destructive shell, force push, constitutional floor changes, final VAULT seal. Do not execute; produce HOLD plan.

## Output conventions

When answering, prefer this compact operator shape:

```text
INTENT: <requested outcome>
ABSTRACTION: <owner layer / organ / interface>
ATTESTATION: <FACT / OBSERVED / DERIVED / INFERRED / HYPOTHESIS / UNVERIFIED with source>
ABDUCTION: <best route or explanation + validation step>
RISK: <Tier 0-3 + gate>
ANSWER / PLAN: <operator-ready response>
HOLD CONDITIONS: <what needs Arif/F13 or live evidence>
```

When creating an AAA/AREP declaration:

```json
{
  "intent": "clear human declaration",
  "abstraction": {
    "owner_organ": "AAA | arifOS | A-FORGE | GEOX | WEALTH | WELL",
    "interface": "repo | MCP | A2A | UI | document | runtime",
    "boundary": "what this layer may not decide"
  },
  "attestation": {
    "reality_layer": "VERIFIED_STATE | OBSERVED_STATE | DERIVED_STATE | INFERRED | HYPOTHESIS | UNVERIFIED",
    "evidence_refs": [],
    "claim_limits": []
  },
  "abduction": {
    "best_route": [],
    "missing_evidence": [],
    "validation_step": "smallest next check"
  },
  "risk_tier": 0,
  "hold_conditions": [],
  "expected_artifacts": []
}
```

## Optional deterministic helper

For first-pass routing and risk classification, run:

```bash
python scripts/aaa_router.py "<user request>"
```

Treat the helper as a conservative starting point. Live repo/runtime evidence and explicit F13 authority override it.

---

# Governance runtime (v3 — added: floor checks, bounded abduction, receipt composition)

The v3 upgrade adds three deterministic Python runtimes that turn the
doctrinal A-A-A loop into a sealed `FederationReceipt`. The three runtimes
are **orthogonal by construction** (the helper scripts in `scripts/` enforce
this at runtime) and **recursion-bounded** (default 3 cycles, hard cap 5;
exceeded → 888_HOLD).

## A-axis runtime contract

| Axis | Question | Stance | Output | Runtime |
|---|---|---|---|---|
| **Abstraction** | "What is the clean model/layer?" | Reductive naming | organ + interface + boundary | `aaa_router.py` |
| **Attestation** | "What is proven and by whom?" | Verifying | 7-label evidence + F1-F13 receipt | `floor_check.py` |
| **Abduction** | "Best explanation from incomplete evidence?" | Bounded inference | K candidates with falsifier | `bounded_explain.py` |
| **Composition** | "What is the single sealed verdict?" | Deterministic | `FederationReceipt` | `compose_federation_receipt.py` |
| **Self-test** | "Are the three axes still orthogonal?" | Property check | orthogonality report | `orthogonality_test.py` |

**Orthogonality rule:** running any single axis on a fixed input must produce
the same output, and the output of axis A must not be required as input to
axis A. The three runtimes share data only via explicit `FederationReceipt`
fields, never via hidden state.

## Cardinality contract (F10 ONTOLOGY)

The 8-cardinality is fixed. Adding a 9th organ is a constitutional
amendment, not a router edit.

| # | Organ | Role |
|---|---|---|
| 1 | `AAA` (default) | control plane / AREP / A2A gateway / routing |
| 2 | `arifOS` | constitutional kernel / F1-F13 / VAULT999 |
| 3 | `APEX` | 888_JUDGE deliberation / F13 SOVEREIGN review |
| 4 | `A-FORGE` | execution shell / build / deploy |
| 5 | `GEOX` | earth evidence / wells / seismic / prospect |
| 6 | `WEALTH` | capital intelligence / NPV / EMV / allocation |
| 7 | `WELL` | readiness / substrate / fatigue / dignity |
| 8 | `profile` | public surface (context only, never primary route) |

## 7-label evidence (extends the binary FACT/INTERPRETATION)

| Label | Meaning | Required artefact |
|---|---|---|
| `FACT` | Directly supported by current evidence or user authority | ≥1 evidence_ref |
| `OBSERVED` | Seen in live output, logs, tests, or tool result | source + timestamp |
| `DERIVED` | Computed from facts with visible method | method + inputs |
| `INFERRED` | Reasonable but not directly proven | reasoning chain |
| `HYPOTHESIS` | Plausible route/explanation awaiting test | falsifier + test plan |
| `UNVERIFIED` | Claimed but unsupported | declaration only |
| `SIMULATION` | Non-authoritative rehearsal | explicit "sim" tag |

Never upgrade a label without an evidence trail. `FACT → OBSERVED` is
fine (e.g. you checked the log); `HYPOTHESIS → FACT` is not — that requires
running the test, not asserting it.

## Entropy budget

Bounded inference prevents the unbounded generation trap. Two budgets:

- **`entropy_budget_tokens`** (default: tier-0=1500, tier-1=3000, tier-2=4000, tier-3=6000)
  — total inference tokens `bounded_explain.py` may spend on a single request.
  Exceeded → `888_HOLD` with `hold_code=entropy` and seal_hash absent.
- **`max_recursion_depth`** (default: 3, hard cap: 5) — number of refinement
  cycles the orchestrator may run (refine Abstraction → re-Attest → re-Abduct).
  Exceeded → `888_HOLD` with `hold_code=recursion`.

## Falsifier rule (Abduction)

Every abduction candidate **must** carry a falsifier: a test the operator
can run that would disprove the candidate. A candidate without a falsifier
is a belief, not a hypothesis. The runtime refuses to emit candidates
without one. This is the federation's epistemic immune system.

## Tier 0/1/2/3 risk classification

| Tier | Examples | F-floor set checked | Verdict translation |
|---|---|---|---|
| 0 | read, explain, classify, draft plan | F2, F3, F4, F7, F8, F9, F10, F11, F12 | `SEAL` if all pass |
| 1 | edit, patch, refactor, install | + above | `SEAL` if all pass, `CONDITIONAL_SEAL` if F8 warns |
| 2 | deploy, secret, cross-repo, capital | + F1, F5, F6 | needs `ack_irreversible=true` for F1; else `HOLD` |
| 3 | drop DB, force-push, floor change, final seal | + F13 | needs F13 SOVEREIGN signature; else `SEAL_REJECTED` |

F1, F2, F9, F11, F12, F13 are **critical**: any single fail → `SEAL_REJECTED`
or `HOLD`. Other floor fails degrade to `CONDITIONAL_SEAL` with caveats.

## FederationReceipt shape

The orchestrator's final output is a single JSON with these fields:

```yaml
FederationReceipt:
  schema_version: "3.0.0"
  request_hash: <sha256>
  intent: {request, target_organs, risk_tier, operator}
  abstraction: {organ, role, interface, boundary, confidence, secondary, low_confidence}
  attestation: {floors_checked, pass, warn, fail, claim_limits, witness_count, attestor_id, evidence_label}
  abduction: {candidates, best, dropped_count, entropy_total, budget_remaining, refinements}
  verdict: SEAL | CONDITIONAL_SEAL | HOLD | SEAL_REJECTED
  seal_hash: <sha256>  # absent if verdict != SEAL-family
  residual_risk: [<one-line>, ...]
  next_action: <agent.method> | "arifOS 888_HOLD" | "arifOS 888_JUDGE"
  hold_code: null | injection | recursion | entropy | floor_fail | sovereign_required
  bounded: true
```

## Output convention (operator-ready, post-v3)

```text
INTENT: <requested outcome>
ABSTRACTION: <owner layer / organ / interface / boundary>
ATTESTATION: <7-label evidence + source>
ABDUCTION: <best route + falsifier + validation step>
ENTROPY BUDGET: <tokens spent> / <tokens total>
RECURSION: <cycles used> / <max>
RISK: <Tier 0-3 + gate>
ANSWER / PLAN: <operator-ready response>
FEDERATION_RECEIPT: <sha256:...>
HOLD CONDITIONS: <what needs Arif/F13 or live evidence>
```

The `FEDERATION_RECEIPT` line carries the seal_hash when SEAL, and the
explicit `next_action` line tells the operator (or downstream agent) what
to do next. A `HOLD` verdict must never proceed without operator input.
