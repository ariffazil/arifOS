---
type: Synthesis
tier: 30_GOVERNANCE
strand:
- roadmap
audience:
- researchers
difficulty: intermediate
prerequisites:
- Roadmap
- Floors
tags:
- open-questions
- todos
- unknowns
- ghosts
- blockers
sources:
- ROADMAP.md
- CHANGELOG.md
- K000_LAW.md
- wiki/raw/governed_packet_bands_and_godellock_ingest_2026-04-11.md
- wiki/raw/meta_theory_atoms_and_governed_utility_ingest_2026-04-11.md
last_sync: '2026-04-11'
confidence: 0.98
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
- **`arifos_forge` gate:** Does `arifos_forge` technically accept a `judge_receipt` parameter carrying the SEAL verdict, or is it implicit session state? *(Source: [[Concept_Architecture]])*
- **ToM field scope:** Does every governance tool carry the full ToM schema, or only `arifos_mind`? The [[Changelog]] shows the `arifos_mind` example — unclear if `arifos_init` and `arifos_sense` also carry `alternative_hypotheses`. *(Source: [[Concept_Architecture]])*
- **Wajib band enforcement point:** Should Physics + Math + Linguistic output bands be enforced in each tool, in a shared envelope formatter, or by `arifos_judge` as a postcondition? *(Source: governed packet doctrine ingest)*
- **INIT/VAULT hard override path:** Where should `DITEMPA BUKAN DIBERI` be forced — quote registry, formatter, or tool-specific wrapper? *(Source: Philosophy Registry + governed packet doctrine ingest)*
- **Gödel lock implementation boundary:** Is stronger undecidable labeling a new floor, a `mind/judge` submode, or an envelope-level tag only? *(Source: [[Concept_Godellock]])*
- **AC-T / PSS tripwires:** Which layer computes anomalous contrast and paradox-scar overlap — `sense`, `ops`, or shared telemetry middleware? *(Source: meta-theory ingest)*
- **Governed Utility scalar:** What exact weights define `U`, and is it global or tool-family specific? *(Source: meta-theory ingest)*

### Roadmap Decisions

- **B→C transition trigger:** What metric or event triggers the decision to start Path C (REST Constitutional API) rather than extending Path B? Is there a defined KPI threshold? *(Source: [[Roadmap]])*
- **Next release after SOT-SEALED:** What is the next named milestone? SOT-SEALED closed the versioning chaos; what's the next architectural leap? *(Source: [[Changelog]])*
- **Philosophy Registry growth:** Is the registry at 83 quotes (v1.2.0) still current, or has it grown? The [[Changelog]] references 50 core quotes elsewhere. *(Source: [[Changelog]])*
- **Autoresearch test harness:** Which batch of MCP outputs becomes the fixed eval corpus for ratcheting `U` without overfitting doctrine prose? *(Source: meta-theory ingest)*

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
| **Governed Utility Score** | doctrine ingest, future eval harness | Medium |
| **APE / AC / PSS** | doctrine ingest, telemetry proposals | Medium |

---

## ✅ Recently Resolved (Archive)

*(Move items here when closed, with resolution note)*

| Item | Resolved | How |
|------|----------|-----|
| Versioned file chaos (`tools_v2.py` etc.) | 2026-04-07 | SOT-SEALED — consolidated to single canonical modules |
| `arifos_v2` namespace leaks | 2026-04-07 | Fully purged from runtime Python |
| `core/` vs `arifosmcp/` split | 2026-04-05 | Archive Surgery — 153 files migrated, `core/` deleted |
| 42 tools sprawl | 2026-03-20 | Consolidated to 11 Mega-Tools |

---

**Related:** [[Roadmap]] | [[Changelog]] | [[Concept_Architecture]] | [[Concept_Floors]]
