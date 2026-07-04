---
agent: arifOS MCP Runtime
workspace: /root/arifOS
motto: DITEMPA BUKAN DIBERI
authority: 888_JUDGE
generated_by: arifosmcp.maintenance.generate_agents_md
generated_from: arifosmcp.constitutional_map.CANONICAL_TOOLS
---

# arifOS MCP Runtime — Canonical Agent Skills

> **ZEN-9 METABOLIC LOOP (2026-07-04)**: Public MCP is now the 9-stage metabolic loop (8 tools + critique absorbed into think as mode).
> See runtime/public_surface.py CANONICAL_9 and constitutional_map.py _PUBLIC_9.
> Absorbed tools: arif_canary, arif_triage → arif_init modes; arif_fetch → arif_observe mode; arif_critique → arif_think mode; arif_bridge_connect → arif_route mode.

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

## 8 Public Tools — 9-Stage Metabolic Loop

All tools follow the `arif_<noun>_<verb>` naming convention.
The 9th stage (critique) is absorbed into `arif_think(mode=critique)`.

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
| `arif_compose` | 888 | AGI | public | L02, L04, L06, L09 | compose, summarize, cite, tone_shift |

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
| L07 | HUMILITY | SOFT | Uncertainty band 0.03–0.05; no fake certainty |
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

## 000–999 Metabolic Pipeline (ZEN-9 Loop)

```
000   → arif_init        — 000_INIT: Session bootstrap. Absorbed: canary, triage
111   → arif_observe     — 111_OBSERVE: Sense reality. Absorbed: fetch
333   → arif_think       — 333_REASON: Cognitive engine. Absorbed: critique
444   → arif_route       — 444_ROUTE: Intent routing. Absorbed: bridge_connect
666   → arif_judge       — 666_JUDGE: Constitutional verdict. SEAL/HOLD/SABAR/VOID
777   → arif_forge       — 777_FORGE: Guarded execution. Requires prior SEAL
888   → arif_compose     — 888_COMPOSE: Governed response. Final wire
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


---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
