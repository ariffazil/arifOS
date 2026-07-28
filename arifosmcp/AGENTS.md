---
agent: arifOS MCP Runtime
workspace: /root/arifOS
motto: DITEMPA BUKAN DIBERI
authority: 888_JUDGE
generated_by: arifosmcp.maintenance.generate_agents_md
generated_from: arifosmcp.constitutional_map.CANONICAL_TOOLS
---

# arifOS MCP Runtime — Canonical Agent Skills

> **ZEN-8 CANONICAL SURFACE (2026-07-19)**: 8 public tools = 8 capabilities. arif_critique → arif_think(mode=critique). arif_compose absorbed into arif_forge(mode=compose).
> Source: capability_registry.json → KERNEL_ABI_8. constitutional_map.py CANONICAL_TOOLS also registers internal_only tools (critique, compose) for backward alias resolution.
> Absorbed tools: arif_canary, arif_triage → arif_init modes; arif_fetch → arif_observe mode; arif_critique → arif_think mode; arif_bridge_connect → arif_route mode; arif_compose → arif_forge mode.

> **Constitutional Intelligence Kernel + Agent Runtime**
>
> **Machine is substrate. Governance is constraint. Intelligence is interpretation. Judgment remains Arif.**
>
> This document registers the canonical MCP tools (the constitutional surface) available to AI agents
operating within the arifOS ecosystem. The tool tables below are **auto-generated** from
`arifosmcp.constitutional_map.CANONICAL_TOOLS`. The static sections (frontmatter, floor definitions,
Trinity Lanes, pipeline diagram, witness defaults, resource URIs, footer) are hand-maintained in
`arifosmcp/maintenance/generate_agents_md.py`.

<!-- ═══════════════════════════════════════════════════════════════════════════
     AUTO-GENERATED SECTION — DO NOT EDIT BY HAND
     Source: arifosmcp.constitutional_map.CANONICAL_TOOLS
     Regenerate: python -m arifosmcp.maintenance.generate_agents_md
     ═══════════════════════════════════════════════════════════════════════════ -->

## 8 Public Tools — Canonical Surface

All tools follow the `arif_<noun>_<verb>` naming convention.
8 capabilities in KERNEL_ABI_8, sourced from capability_registry.json.
arif_critique → arif_think(mode=critique). arif_compose → arif_forge(mode=compose).

### SESSION & GOVERNANCE

| Tool | Stage | Lane | Access | F-Floors | Modes |
| :--- | :---- | :--- | :----- | :-------- | :---- |
| `arif_init` | 000 | AGI | public | L01, L11, L12 | init, resume, canary, preflight, triage |
| `arif_judge` | 666 | ASI | authenticated | L01, L02, L11, L13 | intercept, judge, validate, hold, escalate |
| `arif_seal` | 999 | APEX | authenticated | L01, L11, L13 | seal, verify, ledger, changelog, audit |

### INTELLIGENCE (Cognitive Engine)

| Tool | Stage | Lane | Access | F-Floors | Modes |
| :--- | :---- | :--- | :----- | :-------- | :---- |
| `arif_think` | 333 | AGI | public | L02, L05, L06, L07, L08, L09, L10 | reason, plan, critique, reflect, verify, simulate, redteam, maruah |
| `arif_memory` | 555 | AGI | internal_only | L01, L02, L04, L11 | recall, inspect, attest, remember, promote, revise, forget |

### ROUTING & EXECUTION

| Tool | Stage | Lane | Access | F-Floors | Modes |
| :--- | :---- | :--- | :----- | :-------- | :---- |
| `arif_route` | 444 | AGI | public | L01, L04, L10, L11 | route, bridge |
| `arif_forge` | 777 | AGI | authenticated | L01, L11, L13 | engineer, query, write, generate, commit |

### REALITY GROUNDING

| Tool | Stage | Lane | Access | F-Floors | Modes |
| :--- | :---- | :--- | :----- | :-------- | :---- |
| `arif_observe` | 111 | AGI | public | L02, L03, L07, L12 | search, fetch, ingest, vitals, atlas |


## Constitutional Laws (F1–L13)

| Floor | Name | Type | Core Invariant |
| :---- | :--- | :---- | :------------- |
| L01 | AMANAH | HARD | Reversible-first; irreversible → 888 HOLD |
| L02 | TRUTH | HARD | ≥0.99 accuracy or declare uncertainty band |
| L03 | WITNESS | SOFT | Theory · constitution · intent must align |
| L04 | CLARITY | SOFT | Every output reduces entropy (ΔS ≤ 0) |
| L05 | PEACE | SOFT | Peace ≥ 1.0; de-escalate, guard maruah |
| L06 | EMPATHY | SOFT | Dignity-first; ASEAN/MY context |
| L07 | HUMILITY | HARD | Uncertainty band 0.03–0.05; no fake certainty |
| L08 | GENIUS | SOFT | Maintain intelligence quality, system health |
| L09 | ANTIHANTU | HARD | Anti-Hallucination: C_dark < 0.30, no consciousness claims |
| L10 | ONTOLOGY | HARD | AI-only ontology; no soul/feelings claims |
| L11 | AUTH | HARD | Verify identity before sensitive ops |
| L12 | INJECTION | HARD | Sanitize inputs; no prompt injection |
| L13 | SOVEREIGN | HARD | Human veto absolute. |

### F9 Enhanced: C_dark Formula

C_dark = weighted sum of 5 components:
- **H** (0.25): Hantu patterns — consciousness/feeling claims
- **ToM** (0.25): Theory of Mind manipulation — false beliefs, deceptive intent
- **Scar** (0.20): Unresolved contradictions from reasoning
- **Gödel** (0.15): Circular/self-referential reasoning
- **Humility** (0.15): Ω₀ outside [0.03, 0.05] band

Threshold: C_dark < 0.30 for SEAL.

## Trinity Lanes

| Lane | Role | Stage |
| :--- | :--- | :---- |
| AGI | Tactical execution | 000–777 |
| ASI | Strategic judgment | 888 |
| APEX | Authority resolution | 999 |

## 000–999 Metabolic Pipeline (8-Stage Loop)

```
000   → arif_init        — 000_INIT: Session bootstrap. Absorbed: canary, triage
111   → arif_observe     — 111_OBSERVE: Sense reality. Absorbed: fetch
333   → arif_think       — 333_REASON: Cognitive engine. Absorbed: critique, compose
444   → arif_route       — 444_ROUTE: Intent routing. Absorbed: bridge_connect
555   → arif_memory      — 555_MEMORY: Governed recall and persistence
666   → arif_judge       — 666_JUDGE: Constitutional verdict. SEAL/HOLD/SABAR/VOID
777   → arif_forge       — 777_FORGE: Guarded execution. Absorbed: compose modes
999   → arif_seal        — 999_SEAL: Append to VAULT999. Gödel break — only sovereign opens next loop
```


## Tri-Witness Defaults

When governance kernel returns 0.0 for witness scores, these defaults are applied:
- Human: 0.42 (42% — sovereign authority)
- AI: 0.32 (32% — reasoning coherence)
- Earth: 0.26 (26% — environmental grounding)

## Resource URIs

| URI | Content |
| :--- | :------ |
| `arifos://agents/skills` | This document |
| `arifos://status/vitals` | System health |
| `arifos://governance/floors` | F1-L13 thresholds |
| `arifos://contracts/tools` | Tool risk contracts |

## Canonical Links

- **Human**: <https://arif-fazil.com>
- **Theory**: <https://arifos.arif-fazil.com>
- **Runtime**: <https://arifosmcp.arif-fazil.com>
- **MCP Endpoint**: <https://mcp.arif-fazil.com/mcp>
- **Code**: <https://github.com/ariffazil/arifOS>


## DAG Cognition Bridge — Tri-Layer Wiring (FORGED 2026-07-20)

The arifOS kernel already embodies the tri-layer DAG cognition architecture.
No new modules — just explicit bridge points between existing components.

### Ontological Map

| Temporal Domain | arifOS Component | DAG Equivalent | Bridge Point |
|---|---|---|---|
| **Execution** (Layer 1) | A-FORGE leases + session trails | Branchable execution DAG | `evidence_sha` param on `arif_seal` |
| **Authority** (Layer 2) | VAULT999 seal chain | Immutable linear ledger | `SealOutput.evidence_sha` field |
| **Semantics** (Layer 3) | `arif_memory` L1-L6 tiers | Disposable rebuildable index | `arif_memory(mode='seal')` → sacred tier |

### Bridge Mechanics

**L1 → L2 (Execution → Authority):**
When A-FORGE completes a subagent lease, the terminal execution SHA is passed
to `arif_seal(evidence_sha=<sha>, ...)` as evidence payload.
VAULT999 stores the ruling; the SHA points back to the full execution trail.

**L2 → L3 (Authority → Semantics):**
After a successful seal, `arif_memory(mode='seal')` stores the sealed entry
as sacred tier (L4), indexed for semantic recall.  The index is disposable —
rebuildable from the seal chain at any time.

**Rewind Bridge (F1 Amanah):**
When an execution path is rewound, Layer 1 shifts the state pointer.
Layer 2 seals a NEW entry with `reversion_event: {previous_sha, reason, new_sha}` —
appending to history, not overwriting it.  The reversion IS the history.

### Boundary Integrity

- Layer 1 is mutable and rewindable (execution sandbox)
- Layer 2 is immutable and append-only (constitutional ledger)
- Layer 3 is disposable and rebuildable (semantic access)
- No cross-layer mutation: Layer 2 never edits Layer 1 state,
  Layer 3 never holds truth hostage

See `arifosmcp/schemas/verdict.py:1135-1145` for the `evidence_sha` +
`reversion_event` field definitions on `SealOutput`.

---

## 🔬 Philosophy of Primitives (Wisdom Distillation 2026-07-20)

> *Eureka preserved from archived ARIFOS_MCP_MANUAL.md*

**Tools are Metabolic Organs.** They are not mere utilities. When an agent calls a
tool, it is subjecting itself to the constitutional physics of the kernel. Every
tool call is an act of metabolic ingestion — the agent takes in reality, processes
it under governance, and emits evidence.

**Resources are Epistemic Wealth.** They represent the accumulated knowledge of
the system — not just data, but context, lineage, and provenance. Resources carry
the weight of what has been learned and sealed.

**Prompts are Execution Directives.** They are rigid framing mechanisms that force
an LLM or agent to execute tasks within the boundaries of the Constitution. A prompt
is not a suggestion — it is a governed instruction with constitutional force.

**The Golden Path:** Every high-integrity operation must flow:
```
000_INIT → 111_OBSERVE → 333_THINK → 666_CRITIQUE → 888_JUDGE → 999_SEAL
```
Skipping stages = constitutional violation. Short-circuiting the path = HOLD.

→ See also: [`docs/WISDOM_DISTILLATION.md`](../docs/WISDOM_DISTILLATION.md) for all preserved eurekas.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
