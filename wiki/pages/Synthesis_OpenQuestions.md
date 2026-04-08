---
type: Synthesis
tags: [open-questions, todos, unknowns, ghosts, blockers]
sources: [ROADMAP.md, CHANGELOG.md, K000_LAW.md]
last_sync: 2026-04-08
confidence: 1.0
---

# Open Questions & Ghosts

> Living page — append items as they arise. Remove when resolved.  
> **Ghost** = concept referenced across wiki but not yet defined as a page.  
> **Blocker** = something external that must happen before progress.  
> **Unknown** = internally unresolved design question.

---

## 🚧 Active Blockers

| Item | Source | Status |
|------|--------|--------|
| DNS A record: `mcp.af-forge.io` → VPS IP | [[Roadmap]] Path D | Human action required |
| TLS certbot run on VPS | [[Roadmap]] Path D | 888_HOLD — after DNS resolves |
| `vault-seal-widget.html` live tool connection | [[Roadmap]] Path D | Pending TLS |

---

## ❓ Design Unknowns

### Execution & Tooling

- **Path A (`platform=` dispatch):** `_stamp_platform()` stamps context on every envelope — but what does the `output_formatter` dispatch look like? Which tool handles it: `tools.py` + `schemas.py`, or a new middleware? *(Source: [[Roadmap]] Path A)*
- **`arifos.forge` gate:** Does `arifos.forge` technically accept a `judge_receipt` parameter carrying the SEAL verdict, or is it implicit session state? *(Source: [[Concept_Architecture]])*
- **ToM field scope:** Does every governance tool carry the full ToM schema, or only `arifos.mind`? The [[Changelog]] shows the `arifos.mind` example — unclear if `arifos.init` and `arifos.sense` also carry `alternative_hypotheses`. *(Source: [[Concept_Architecture]])*

### Roadmap Decisions

- **B→C transition trigger:** What metric or event triggers the decision to start Path C (REST Constitutional API) rather than extending Path B? Is there a defined KPI threshold? *(Source: [[Roadmap]])*
- **Next release after SOT-SEALED:** What is the next named milestone? SOT-SEALED closed the versioning chaos; what's the next architectural leap? *(Source: [[Changelog]])*
- **Philosophy Registry growth:** Is the registry at 83 quotes (v1.2.0) still current, or has it grown? The [[Changelog]] references 50 core quotes elsewhere. *(Source: [[Changelog]])*

### Infrastructure

- **Qdrant RAG:** When does cross-agent RAG (H2 roadmap) activate for VPS-wide memory? What indexes AAA canon first? *(Source: [[Roadmap]] H2)*
- **`/dashboard` spec:** What does the real-time ΔS + psi_LE gauge dashboard look like? Is it served from `arifosmcp` or a separate service? *(Source: [[Roadmap]] H2)*

---

## 👻 Ghosts (Referenced but No Wiki Page Yet)

| Ghost | Referenced In | Priority |
|-------|--------------|----------|
| **AAA Architecture** | `AGENTS.md`, [[Roadmap]] (HF AAA dataset sync) | ~~High~~ → see [[Agents-and-AAA-Architecture]] |
| **Vault999 / VaultLedger** | [[Roadmap]] H1, [[Changelog]], [[Concept_Floors]] | High |
| **A-RIF Canon** | [[Roadmap]] H1 (000_A-RIF.md) | Medium |
| **Eigent Backend** | [[Roadmap]] H1+H2 | Medium |
| **Philosophy Registry** | [[Changelog]], [[Concept_Architecture]] | Medium |
| **Vitality Index (Ψ)** | `000_MANIFESTO.md` | Medium |
| **G★ Scoring formula** | [[Concept_Architecture]], [[Changelog]] | Low (partially covered) |
| **HIKMAH formula** | `000_MANIFESTO.md` | Low |
| **Earth System Governance** | [[Concept_Floors]] (K000_LAW Part III) | Low |

---

## ✅ Recently Resolved (Archive)

*(Move items here when closed, with resolution note)*

| Item | Resolved | How |
|------|----------|-----|
| Versioned file chaos (`tools_v2.py` etc.) | 2026-04-07 | SOT-SEALED — consolidated to single canonical modules |
| `arifos.v2` namespace leaks | 2026-04-07 | Fully purged from runtime Python |
| `core/` vs `arifosmcp/` split | 2026-04-05 | Archive Surgery — 153 files migrated, `core/` deleted |
| 42 tools sprawl | 2026-03-20 | Consolidated to 11 Mega-Tools |

---

**Related:** [[Roadmap]] | [[Changelog]] | [[Concept_Architecture]] | [[Concept_Floors]]
