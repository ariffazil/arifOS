---
type: Concept
tags: [philosophy, quotes, corpus, civilization, wisdom, G-star, constitution]
sources: [CHANGELOG.md, ROADMAP.md]
last_sync: 2026-04-08
confidence: 0.95
---

# Philosophy Registry

> **Version**: v1.2.0  
> **Total Quotes**: 83 (core: 50, extended: 33)  
> **Selection**: Deterministic  
> **Authority**: `arifosmcp/prompts.py`

---

## Purpose

The Philosophy Registry is the **civilizational quote corpus** injected at constitutional moments during arifOS runtime. It provides wisdom anchoring across the 000-999 metabolic pipeline, ensuring that agent reasoning is grounded in human philosophical heritage—not purely algorithmic optimization.

---

## Corpus Statistics

| Metric | Value |
|--------|-------|
| **Total Quotes** | 83 |
| **Core Set** | 50 (5 per tool) |
| **Schema Version** | 2.1.0-unified |
| **Attribution Hygiene** | 5-tier system (exact → summary) |
| **Diversity Score** | 0.85 (target: ≥0.80) |
| **Categories** | 8 (void, paradox, truth, wisdom, justice, discipline, power, seal) |
| **G★ Bands** | 5 |

---

## G★ Scoring Bands

Quotes are distributed across 5 **Genius Index** bands for contextual injection:

| Band | G★ Range | Quote Count | Character |
|------|----------|-------------|-----------|
| **Band 1** | 0.00–0.20 | ~17 | Void, humility, beginner's mind |
| **Band 2** | 0.20–0.40 | ~17 | Paradox, uncertainty, exploration |
| **Band 3** | 0.40–0.60 | ~17 | Truth, clarity, discernment |
| **Band 4** | 0.60–0.80 | ~17 | Wisdom, justice, discipline |
| **Band 5** | 0.80–1.00 | ~15 | Power, seal, mastery |

---

## Trinity Distribution

Quotes are mapped to the three governance aspects:

| Aspect | Tools | Count | Theme |
|--------|-------|-------|-------|
| **Δ (Discernment)** | init, sense, mind, route, forge | 25 | Observation, reasoning, planning |
| **Ω (Empathy)** | memory, heart | 10 | Care, safety, human impact |
| **Ψ (Authority)** | ops, judge, vault | 15 | Decision, verdict, finality |

---

## Deterministic Selection Algorithm

```python
selection_index = sha256(session_id + band + g_star) % band_quote_count
selected_quote = registry[band][selection_index]

```

**Properties**:

- **Reproducible**: Same session + G★ → same quote
- **Contextual**: Band selection tied to governance quality
- **Non-random**: Cryptographic hash prevents gaming

---

## Hard Overrides

Two constitutional moments bypass the algorithm:

| Moment | Override Quote | Reason |
|--------|----------------|--------|
| **INIT stage** (000) | *"DITEMPA, BUKAN DIBERI."* | Establish forge ethos |
| **SEAL verdict** (999) | *"DITEMPA, BUKAN DIBERI."* | Confirm completion |

This ensures the arifOS motto anchors every session start and successful seal.

---

## Categories

| Category | Theme | Example Trigger |
|----------|-------|-----------------|
| **void** | Nothingness, potential, emptiness | Low G★, init stage |
| **paradox** | Contradiction, tension, mystery | F7 uncertainty high |
| **truth** | Verification, reality, honesty | F2 enforcement |
| **wisdom** | Deep knowledge, experience | G★ > 0.60 |
| **justice** | Fairness, balance, consequence | F5/F6 alignment |
| **discipline** | Practice, repetition, craft | Forge operations |
| **power** | Authority, responsibility, restraint | High-stakes decisions |
| **seal** | Finality, completion, legacy | 999_VAULT stage |

---

## Attribution Hygiene (5-Tier System)

| Tier | Format | Use Case |
|------|--------|----------|
| **Exact** | `"Quote" — Author, Source, Year` | Canonical quotes |
| **Verified** | `"Quote" — Author` | Confirmed attribution |
| **Traditional** | `"Quote" — Traditional` | Ancient/oral sources |
| **Apocryphal** | `"Quote" — Attributed to Author` | Disputed sources |
| **Summary** | `As Author wrote...` | Paraphrased wisdom |

---

## Integration Points

### Runtime Injection

- **Trigger**: `trigger_when` conditions in tool calls
- **Context**: Injected into tool response envelopes
- **Display**: UI widgets show quote + seal hash

### Forge-Time Embedding

- **Output Map**: `output_map` for doctrine preservation
- **Attribution Mode**: `[reason, reflect, forge, seal, verify]`

### Constitutional Moments

| Stage | Quote Band | Purpose |
|-------|------------|---------|
| 000_INIT | void/seal | Anchor session |
| 222_THINK | truth/wisdom | Reasoning guidance |
| 444_ROUT | paradox | Route uncertainty |
| 666_HEART | justice/empathy | Safety check |
| 888_JUDGE | power/discipline | Verdict gravity |
| 999_SEAL | seal | Final commitment |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-03-14 | Initial 50 quotes |
| v1.1.0 | 2026-03-20 | Attribution hygiene added |
| v1.2.0 | 2026-04-06 | **Current** — 83 quotes, G★ bands, unified schema |

---

## Corpus Contrast: Before vs After v1.2.0

| Aspect | Before | After |
|--------|--------|-------|
| Count | 50 fixed | 83 with band distribution |
| Selection | Random | Deterministic hash |
| Override | None | INIT + SEAL hardcoded |
| Categories | 5 | 8 |
| Diversity | 0.72 | 0.85 |

---

## Open Questions

1. **Growth Policy**: Will the registry grow beyond 83? What is the ceiling?
2. **Localization**: Will Malay/Arabic quotes be added for Nusantara grounding?
3. **Custom Corpuses**: Can institutional deployments inject their own philosophy?

---

> [!NOTE]
> The Philosophy Registry is **not decorative**. It is a thermodynamic tool: wisdom injection at decision points increases the "energy cost" of the reasoning process, making cheap (low-quality) outputs less likely per F2 Truth Axiom.

---

**Related:** [[Concept_Architecture]] | [[Concept_Floors]] | [[Changelog]] | [[Roadmap]]
