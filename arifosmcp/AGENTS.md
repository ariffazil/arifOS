---
agent: arifOS MCP Runtime
workspace: /root/arifOS
motto: DITEMPA BUKAN DIBERI
authority: 888_JUDGE
generated_by: arifosmcp.maintenance.generate_agents_md
generated_from: arifosmcp.constitutional_map.CANONICAL_TOOLS
---

# arifOS MCP Runtime — Canonical Agent Skills

> **Constitutional Intelligence Kernel + Agent Runtime**
>
> **Machine is substrate. Governance is constraint. Intelligence is interpretation. Judgment remains Arif.**
>
> This document registers the canonical MCP tools (the 13-tool constitutional surface) available to AI agents
operating within the arifOS ecosystem. The tool tables below are **auto-generated** from
`arifosmcp.constitutional_map.CANONICAL_TOOLS`. The static sections (frontmatter, floor definitions,
Trinity Lanes, pipeline diagram, witness defaults, resource URIs, footer) are hand-maintained in
`arifosmcp/maintenance/generate_agents_md.py`.

<!-- ═══════════════════════════════════════════════════════════════════════════
     AUTO-GENERATED SECTION — DO NOT EDIT BY HAND
     Source: arifosmcp.constitutional_map.CANONICAL_TOOLS
     Regenerate: python -m arifosmcp.maintenance.generate_agents_md
     ═══════════════════════════════════════════════════════════════════════════ -->

## 13 Canonical Tools (arif_noun_verb)

All tools follow the `arif_<noun>_<verb>` naming convention.

### GOVERNANCE (APEX / ASI)

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_session_init` | 000 | AGI | public | F01, F11, F12 |
| `arif_judge_deliberate` | 888 | ASI | authenticated | F11, F13 |
| `arif_vault_seal` | 999 | APEX | authenticated | F01, F11, F13 |

### INTELLIGENCE (Δ Mind / Ω Heart)

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_mind_reason` | 333 | AGI | public | F02, F07, F08, F10 |
| `arif_heart_critique` | 444 | ASI | public | F05, F06, F09 |
| `arif_reply_compose` | 444r | AGI | public | F04, F06, F09 |

### INFRASTRUCTURE

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_kernel_route` | 555 | AGI | public | F01, F04, F03, F10 |
| `arif_gateway_connect` | 666g | ASI | public | F01, F03 |
| `arif_memory_recall` | 555m | AGI | public | F01, F08 |
| `arif_ops_measure` | 777 | AGI | public | F04 |

### REALITY GROUNDING

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_sense_observe` | 111 | AGI | public | F02, F07 |
| `arif_evidence_fetch` | 222 | AGI | public | F02, F03, F05, F12 |

### EXECUTION

| Tool | Stage | Lane | Access | F-Floors |
| :--- | :---- | :--- | :----- | :-------- |
| `arif_forge_execute` | 666 | AGI | sovereign | F01, F11, F13 |


## Constitutional Floors (F1–F13)

| Floor | Name | Type | Core Invariant |
| :---- | :--- | :---- | :------------- |
| F01 | AMANAH | HARD | Reversible-first; irreversible → 888 HOLD |
| F02 | TRUTH | HARD | ≥0.99 accuracy or declare uncertainty band |
| F03 | WITNESS | SOFT | Theory · constitution · intent must align |
| F04 | CLARITY | SOFT | Every output reduces entropy (ΔS ≤ 0) |
| F05 | PEACE | SOFT | Peace ≥ 1.0; de-escalate, guard maruah |
| F06 | EMPATHY | SOFT | Dignity-first; ASEAN/MY context |
| F07 | HUMILITY | SOFT | Uncertainty band 0.03–0.05; no fake certainty |
| F08 | GENIUS | SOFT | Maintain intelligence quality, system health |
| F09 | ANTIHANTU | HARD | Anti-Hallucination: C_dark < 0.30, no consciousness claims |
| F10 | ONTOLOGY | HARD | AI-only ontology; no soul/feelings claims |
| F11 | AUTH | HARD | Verify identity before sensitive ops |
| F12 | INJECTION | HARD | Sanitize inputs; no prompt injection |
| F13 | SOVEREIGN | HARD | Human veto absolute. |

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

## 000–999 Metabolic Pipeline

```
000   → arif_session_init        — 000_INIT: Session bootstrap + identity binding. CALL FIRST…
111   → arif_sense_observe       — 111_OBSERVE: Multimodal reality observation and hybrid…
222   → arif_evidence_fetch      — 222_EVIDENCE: Verified external evidence retrieval with…
333   → arif_mind_reason         — 333_REASON: Symbolic reasoning kernel — epistemically…
444   → arif_heart_critique      — 444_CRITIQUE: Ethical critique and consequence assessment…
444r  → arif_reply_compose       — 444_REPLY: Governed response composition — formats final…
555   → arif_kernel_route        — 555_ROUTE: Routes intent to correct tool or organ. Use when…
555m  → arif_memory_recall       — 555m_MEMORY: Associative memory — Postgres+Qdrant vector…
666   → arif_forge_execute       — 666_FORGE: Build execution — code generation, artifact…
666g  → arif_gateway_connect     — 666_GATEWAY: Federated cross-agent bridge — connects arifOS…
777   → arif_ops_measure         — 777_MEASURE: Machine resource health + governance…
888   → arif_judge_deliberate    — 888_JUDGE: Final constitutional arbitration — renders…
999   → arif_vault_seal          — 999_SEAL: Immutable ledger anchoring — cryptographic…
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
| `arifos://governance/floors` | F1-F13 thresholds |
| `arifos://contracts/tools` | Tool risk contracts |

## Canonical Links

- **Human**: <https://arif-fazil.com>
- **Theory**: <https://arifos.arif-fazil.com>
- **Runtime**: <https://arifosmcp.arif-fazil.com>
- **MCP Endpoint**: <https://mcp.arif-fazil.com/mcp>
- **Code**: <https://github.com/ariffazil/arifOS>


---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
