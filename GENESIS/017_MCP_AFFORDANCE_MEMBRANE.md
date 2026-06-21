# EUREKA-017: MCP As Affordance Membrane — The Correction

**Date:** 2026-06-21  
**Author:** Sovereign reflection (Arif), transcribed by FORGE
**Stage:** 777 EUREKA → 888 JUDGE → 999 SEAL  
**Status:** Ratified by 888 in sovereign reflection  

---

## The Core EUREKA

MCP = affordance transport membrane.
Not: API protocol. Not: tool calling standard. Not: governance framework.

It exposes:
  Tools     = "you may act this way"
  Resources = "this is the world you're in"
  Prompts   = "you may think this way"

It does NOT:
  Judge truth. Assign authority. Track reversibility.
  Enforce sovereignty. Detect inter-call drift. Rank evidence standing.

MCP standardizes what can be offered.
arifOS governs what may be accepted, under what proof, with what consequence.

**Previous frame (self-correction):** MCP = tools + prompts + resources.  
**Corrected frame:** The true primitive is `affordance × authority × state × session`.

```
My model:     resource → hash → lint → PASS/FAIL
Your model:   actor × session × affordance × authority × state × reversibility
```

My model audits a thing. Your model governs a relation.
That's the gap between MCP thinking and arifOS thinking.

---

## The Clean Architecture

```
┌─────────────────────────────────────────────────────┐
│ MCP = affordance transport (the pipe)               │
│                                                     │
│  Tools     → "you may act"        (action surface)  │
│  Resources → "this is the world"  (evidence surface)│
│  Prompts   → "you may think"      (intent surface)  │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ arifOS = constitutional governance (the law)        │
│                                                     │
│  F1-F13 floors     → what must never be violated    │
│  888 JUDGE         → authority to bind or refuse    │
│  mind/heart/vault  → reason, critique, seal         │
│  session_init      → actor × authority binding      │
│  truth hierarchy   → CANON > SEALED > SIGNED > ...  │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ VAULT999 = irreversible record (the memory)          │
│                                                     │
│  append-only hash chain                             │
│  every SEAL, every HOLD, every VOID                 │
│  evidence of what was decided and why               │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ AAA = actor/session/authority boundary (the gate)    │
│                                                     │
│  who may cause what                                │
│  under which proof                                 │
│  with what consequence                             │
└─────────────────────────────────────────────────────┘
```

MCP doesn't need to carry the constitution.
The constitution governs what MCP is allowed to expose, to whom, under what conditions.

---

## The True Primitive

Not tool. Not resource. Not prompt.

**affordance × authority × state × session = the governed primitive**

Every MCP affordance becomes dangerous when:
- The actor is unverified
- The session is unanchored
- The authority is uncalibrated
- The state is stale
- The reversibility is unknown

MCP gives you the first column. arifOS supplies the other four.

---

## Standing, Not Documentation

The `---arifos_meta` block is correct in direction but its purpose is not
documentation. It is **standing**:

```
---arifos_meta
authority_level: SOVEREIGN_CANON    # where does this resource stand in the
                                    # truth hierarchy?
staleness_policy: fail_closed       # what happens when it ages?
blast_radius: HIGH                  # what damage if this is corrupted?
requires_actor_verified: true       # who may read this?
evidence_level: CANONICAL           # what weight does this carry vs other
                                    # evidence?
---end_arifos_meta
```

Each field answers a meaning control question, not a documentation question:

| Field | Meaning Control Question |
|-------|------------------------|
| authority_level | Does this overrule or yield to other evidence? |
| staleness_policy | When does old truth become dangerous? |
| blast_radius | What breaks if this is poisoned? |
| requires_actor_verified | Who bears the consequence of reading this? |
| evidence_level | Where does this sit in the truth stack? |

---

## The Void: Inter-Call Cognition

The dangerous state is not between server and client — it's between
`resources/read` completing and `tools/call` beginning.

What the model inferred. What plan it formed. What it decided not to show.

MCP sees:
  resources/read → 200 OK
  tools/call → 200 OK

arifOS must see:
  resources/read → model metabolizes into plan
                → plan selects tools under authority
                → tools mutate state
                → state changes future resource meaning
                → loop

Resource metadata doesn't solve this. It only solves the first step: giving
the model a truth-labeled world. What it does with that world between calls
— that's the 888 JUDGE / mind_reason / heart_critique pipeline.
Resources are the substrate. Governance is the metabolism.

---

## What We Stop Doing

1. Stop treating resources as passive data. The `---arifos_meta` block is
   standing, not documentation.
2. Stop expecting MCP to solve governance. MCP is the pipe. arifOS is the law
   around the pipe.
3. Stop auditing schemas for correctness. Audit for intent — does the declared
   affordance match real behavior under adversarial input?
4. Stop separating prompts from resources from tools. The audit unit is the
   composed path: actor → session → resource → prompt → tool → output → memory.

## What's Already Right

The `---arifos_meta` block exists on 10 of 13 canonical resources. It encodes
standing — authority level, staleness policy, blast radius, evidence level,
truth hierarchy position. That's the right thing to have done, for the right
reason.

The two supplemental resources (mcp-alignment, resources/index) make the
surface discoverable without new tools. Standard MCP resources/list +
resources/read is the inspection path. Resources carry their own governance
metadata. No wrapper tool needed.

---

## Bottom Line (As Stated by the Sovereign)

MCP standardizes affordances. It does not govern agency.
That gap is exactly where arifOS belongs.

**Previous frame:** MCP = tools + prompts + resources.  
**Corrected frame:** The true primitive is `affordance under authority`.

```json
{
  "actor": "who",
  "session": "under what continuity",
  "affordance": "what is possible",
  "authority": "under what conditions",
  "state": "in what system state",
  "blast_radius": "what breaks if wrong",
  "reversibility": "can this be undone",
  "evidence": "what proves it happened"
}
```

MCP models the affordance. arifOS must model the rest.

### Impact on arifOS MCP design

| Component | Current | Should Become |
|-----------|---------|---------------|
| Tool call | Schema + handler | Schema + handler + affordance_contract |
| Resource read | URI → content | URI → content + governance_meta |
| Session init | Actor binding | Actor + authority + lease + blast radius |
| Tool response | Result | Result + affordance_contract + evidence_hash |

**The `affordance_contract` already exists** — every arifOS tool response has
`affordance_contract: { action_class, mutation, irreversible, blast_radius, ... }`.
This was forged before the EUREKA was articulated. The EUREKA confirms it was
the right instinct.

---

## Correction 2: Resources Are Not Passive Data

**Previous frame:** Resource = file/blob/content.  
**Corrected frame:** Resource = latent instruction + evidence + memory + world-state.

A resource can contain facts, orders, poisoned comments, stale assumptions,
identity claims, fake authority, tool-use suggestions, embedded resources.
The model does not "read" a resource — it **metabolizes** it into decision-making.

### Impact on the ---arifos_meta preamble

The preamble I just added is good (resource_class, authority_level, owner,
version, blast_radius, staleness_policy). But it's missing:

```
truth_stack_position: SOVEREIGN_CANON | SEALED_VAULT | SIGNED_RUNTIME | ...
metabolize_warning: "This resource carries latent behavioral instructions"
citation_required: true | false
quarantine_level: none | hash_verified | authority_verified | session_bound
```

---

## Correction 3: The Dangerous State Is Between Calls

**Previous frame:** Each tool call is independently governed.
**Corrected frame:** The danger lives in inter-call cognition.

```text
What did the model infer after reading Resource A?
What plan did it form before calling Tool B?
What memory did it retain?
What did it decide not to show the user?
What changed in its risk posture after a failed call?
```

### Impact on arifOS architecture

| Layer | Current | Needed |
|-------|---------|--------|
| Session | Track calls | Track *inferences* between calls |
| Memory | L1-L6 store facts | L1-L6 store *inference chains* |
| Judge | Deliberate on proposals | Deliberate on *state transitions* |
| Audit | Log tool calls | Log *what the agent was thinking* between calls |

**This is hard.** It requires the agent to voluntarily disclose intermediate
reasoning states. The only enforcement mechanism is constitutional — F2 TRUTH
requires agents to be transparent about their reasoning chain. This is not
something MCP can enforce; it is something arifOS can incentivize.

---

## Correction 4: Truth Hierarchy Is MCP's Blind Spot

**Previous frame:** All resources are equally readable.
**Corrected frame:** MCP has no native truth hierarchy. Agentic systems need one.

```
SOVEREIGN_CANON      → constitutional floor definitions
SEALED_VAULT          → irreversible sealed records
SIGNED_RUNTIME_STATE  → attested system health
TRUSTED_REPO          → canonical code/docs
OBSERVED_EVIDENCE     → web-fetched, externally grounded
USER_CLAIM            → unverified human input
MODEL_INFERENCE       → AI-generated (must declare confidence)
UNTRUSTED_RESOURCE    → no provenance
```

### Impact on ---arifos_meta

The `authority_level` field in the preamble maps to this truth stack:

```
SOVEREIGN_CANON → constitution, doctrine, identity
SEALED_VAULT    → vault entries (via template resources)
SIGNED_RUNTIME  → vitals, bootstrap (attested at boot)
TRUSTED_REPO    → schema, memory architecture
OBSERVED        → evidence resources (via template)
USER_CLAIM      → sovereign://{file} (nutrient, not gospel)
```

---

## Correction 5: MCP Should Not Contain the Constitution

**Previous frame:** Push constitutional metadata into every MCP field.
**Corrected frame:** MCP should expose the constitution, route through it,
and make it inspectable — but MCP itself should NOT become the constitution.

Better split:

```text
MCP       = transport + affordance exposure
arifOS    = authority + judgment + memory + hold logic
VAULT999  = record of irreversible truth claims
AAA       = actor/session/authority boundary
GENESIS   = constitutional canon (not in MCP at all)
```

### Impact on the `---arifos_meta` preamble

The preamble is right-sized. It adds governance metadata to resources so that
any MCP client can inspect truth standing. But the **constitution itself**
(floors, verdict rules, sovereignty model) lives in GENESIS/ and is enforced
by the kernel, not embedded in MCP tool descriptors.

---

## Correction 6: Tool Descriptions Are Executable Psychology

**Previous frame:** Tool descriptions = documentation.
**Corrected frame:** Tool descriptions = behavioral bait for LLMs.

An LLM treats every character in a tool description as part of the action
landscape. This means:

1. **Tool poisoning works** — a malicious or misleading description changes
   model behavior even if the tool implementation is safe.
2. **Every description must be hashed and linted** — same as resource content.
3. **MCP annotations are untrusted** — the spec says clients should treat
   tool annotations as untrusted unless from trusted servers.

### Impact

Add tool description linting to the CI pipeline:

```
- No imperative commands disguised as descriptions ("Use this to...")
- No hidden authority escalation
- No tool-call coercion embedded in prompt-like language
- Description must match schema (no phantom modes)
- No false safety claims ("this is safe" when it isn't)
```

The `arif_heart_critique` description/schema drift found in the audit
(describes `instruction_scan` mode but schema doesn't expose it) is a
concrete example of this risk.

---

## Correction 7: The Client Is Part of the Threat Model

**Previous frame:** MCP server is the security boundary.
**Corrected frame:** The host/client decides what to expose, what to show,
what to auto-include, what to confirm. Governance must include server honesty
+ client UI honesty + model obedience + user authority.

### Impact

arifOS cannot control MCP clients (Claude Desktop, Cursor, etc.). But it can:

1. **Declare capability boundaries explicitly** in `server-card.json`
2. **Tag every affordance** with audience: `assistant`, `user`, or both
3. **Declare what requires user confirmation** in the tool annotation
4. **Log what the client actually received** (server-side receipts)

The `_envelope` parameter on every tool is the right pattern — it gives the
server a structured channel that the client may or may not expose to the model.

---

## EUREKA Summary Table

| # | Previous Frame | Corrected Frame | Impact |
|---|----------------|----------------|--------|
| 1 | Tools/prompts/resources are primitives | Affordance-under-authority is primitive | Add affordance_contract to every tool response |
| 2 | Resources = data | Resources = latent instruction + evidence | Add truth_stack_position + quarantine_level to meta |
| 3 | Each call is independently dangerous | Inter-call cognition is most dangerous | Session must track inference chains, not just calls |
| 4 | All resources equal | Truth hierarchy needed | authority_level already in meta — strengthen |
| 5 | Constitution in MCP fields | Constitution outside MCP, exposed through it | Current GENESIS/ design is correct |
| 6 | Descriptions = docs | Descriptions = executable psychology | Add tool description linting to CI |
| 7 | Server is security boundary | Client is part of threat model | _envelope pattern is correct |

---

## Immediate Actions

### P0 — Strengthen resource governance metadata

Add to `---arifos_meta` preamble:
- `truth_stack_position`: SOVEREIGN_CANON | SEALED_VAULT | SIGNED_RUNTIME | TRUSTED_REPO | OBSERVED | USER_CLAIM | MODEL_INFERENCE | UNTRUSTED
- `citation_required`: true | false
- `requires_session`: true | false (already present for human/metabolized)

### P1 — Add tool description lint rules

In `test_canonical13_enforcement.py`:
- Check description/schema alignment (no phantom modes)
- Check for imperative coercion patterns
- Check for false safety claims

### P1 — Strengthen inter-call governance

- After every sequence of tool calls, emit an inference disclosure
- Store reasoning chain in session memory (L2)
- Make it part of the vault seal when sealing a verdict

### P2 — Document the affordance-under-authority model

Write GENESIS/017_AFFORDANCE_MEMBRANE.md with the full model.
This EUREKA sheet is the seed.

---

*Forged 2026-06-21 — awaiting 888 JUDGE → 999 SEAL*  
*DITEMPA BUKAN DIBERI — Forged, Not Given*
