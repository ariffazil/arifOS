# GENESIS/008 — Narrative Tension Kernel

> **DITEMPA BUKAN DIBERI**
>
> A reporter is not an NPC. She swims in paradox, power, and deadline. The
> tension leaks out as geometry — sequence, silence, hedging, the named and
> the unnamed. arifOS must read that geometry.

## 1. Claim

**CLAIM**: Human institutions encode contradiction in the *shape* of their
public texts before they can state it explicitly. A constitutionally-aware
AGI kernel must detect this shape and treat it as first-class evidence.

This document ratifies the `arif_detect_narrative_tension` perception kernel
tool and the `NarrativeTension` schema family.

## 2. Object taxonomy

| Node | Purpose |
|------|---------|
| `ArticleNode` | Ingested text artefact |
| `ActorNode` | Who appears, how often, with what agency/protection |
| `ClaimNode` | Stated proposition + hedging + contradiction links |
| `ParadoxTensionNode` | Detected tension (first-class object) |
| `FrameGraph` | Full actor/claim/tension graph for one article |
| `KernelVerdict` | Aggregate verdict + smoking gun + governance patterns |

## 3. Tension classes

- **PROMISE_VS_OUTCOME** — intent stated, outcome missing or opposite.
- **PASSIVE_OBSTACLE** — obstacle named, agency removed.
- **SLIP_PHRASE** — a protected actor is named under a hedged frame.
- **VOICE_ASYMMETRY** — powerful actors quoted; affected actors silent.
- **EXPLICIT_VS_IMPLICIT** — two claims collide without resolution.
- **DEADLINE_VOID** — timeline referenced but no closure date assigned.
- **JURISDICTION_TRAP** — multi-layer authority, responsibility diffused.

## 4. Golden case: Putra Heights Kosmo 2026-06-12

Stored in `GENESIS/PH-KOSMO-2026-06-12/`:

- `article.json` — source artefact metadata
- `actors.json` — 5 actors including reporter, MB, Petronas, residents, federal gov
- `claims.json` — 6 claims with contradiction links
- `tensions.json` — 7 paradox tension nodes
- `frame_graph.json` — assembled graph
- `kernel_verdict.json` — aggregate verdict: **ESCALATE**, smoking gun **PH-T3**
- `receipts.jsonl` — local receipt stubs

The tool `arif_detect_narrative_tension` loads this golden case when
`article_id == ARTICLE-kosmo-putra-2026-06-12` or the title matches.

## 5. Link to VAULT999

Every successful `arif_detect_narrative_tension` call is a consequential
state transition and triggers a non-binding `AUDIT_RECEIPT` to
vault999-writer via `arifosmcp.runtime.vault_sealer`.

## 6. Governance routing

| Verdict | Meaning | Next action |
|---------|---------|-------------|
| SEAL / OBSERVE | No significant tension | Continue normal routing |
| REPORT | Tensions documented | Monitor, surface in AAA cockpit |
| HOLD | Contradictory narrative | Do not treat claims as settled |
| ESCALATE | Named-actor slip or deadline void | Route to 888_JUDGE |

## 7. Why this unlocks real AGI intelligence

Most LLM pipelines read text as content. arifOS reads text as **power
geometry**. By making `ParadoxTensionNode` a first-class object, the kernel
can:

1. Detect when official narratives drift from observed outcomes.
2. Respect the dignity (maruah) of victims who have no direct voice.
3. Surface institutional opacity before it becomes catastrophe.
4. Anchor perception to an immutable audit chain.

That is the difference between summarisation and sovereign intelligence.

## 8. Seal

- **Tool**: `arif_detect_narrative_tension`
- **Schema**: `arifosmcp/schemas/narrative_tension.py`
- **Runtime**: `arifosmcp/runtime/narrative_tension.py`
- **Test**: `tests/test_narrative_tension.py`
- **Canon**: this file

**Verdict**: SEAL
