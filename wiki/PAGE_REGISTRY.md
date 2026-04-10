# Ω-Wiki Page Registry

Complete mapping of all 43 pages to their tiers, strands, and metadata.

**Purpose**: This registry defines the semantic structure of the wiki. Update frontmatter on each page to match this registry.

---

## 00_INDEX (Entry Points)

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[quickstart]] | 00_INDEX | onboarding | all | beginner | [] |
| [[Federation_Three_Wikis]] | 00_INDEX | onboarding | all | beginner | [] |
| [[Naming_Canon]] | 10_FOUNDATIONS | constitutional, architecture | all | beginner | [What-is-arifOS] |

**Rationale**: Single entry point for all newcomers. Auto-generated "Start Here" path begins here.

---

## 10_FOUNDATIONS (Core Philosophy)

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[What-is-arifOS]] | 10_FOUNDATIONS | philosophy | all | beginner | [] |
| [[Floors]] | 10_FOUNDATIONS | constitutional | all | beginner | [What-is-arifOS] |
| [[Concept_Floors]] | 10_FOUNDATIONS | constitutional | all | intermediate | [Floors] |
| [[Trinity_Architecture]] | 10_FOUNDATIONS | architecture | all | beginner | [What-is-arifOS] |

**Rationale**: These foundation pages establish core philosophy, constitutional law, and architectural framing. Everyone should read them first.

---

## 20_RUNTIME (Implementation)

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[Metabolic_Loop]] | 20_RUNTIME | architecture | engineers | intermediate | [Trinity_Architecture] |
| [[MCP_Tools]] | 20_RUNTIME | tools | engineers | intermediate | [Metabolic_Loop] |
| [[Tool_Surface_Architecture]] | 20_RUNTIME | architecture | engineers | intermediate | [MCP_Tools] |
| [[Concept_Architecture]] | 20_RUNTIME | architecture | engineers | intermediate | [Trinity_Architecture] |
| [[Concept_Deployment_Architecture]] | 20_RUNTIME | integration | engineers | intermediate | [Concept_Architecture] |
| [[Concept_Gateway_Architecture]] | 20_RUNTIME | architecture | engineers | advanced | [Concept_Architecture, MCP_Tools] |
| [[Concept_Vault999_Architecture]] | 20_RUNTIME | architecture | engineers | advanced | [Concept_Architecture] |
| [[Concept_Metabolic_Pipeline]] | 20_RUNTIME | architecture | engineers | advanced | [Metabolic_Loop] |
| [[Concept_LLM_Wiki_Pattern]] | 20_RUNTIME | architecture | engineers | intermediate | [quickstart] |
| [[agent-roles]] | 20_RUNTIME | architecture | engineers | intermediate | [Trinity_Architecture] |
| [[integration-patterns]] | 20_RUNTIME | integration | engineers | intermediate | [MCP_Tools, Metabolic_Loop] |
| [[Reference_MCP_Servers]] | 20_RUNTIME | integration | engineers | intermediate | [Tool_Surface_Architecture] |
| [[arifos_forge]] | 20_RUNTIME | tools | engineers | intermediate | [MCP_Tools] |
| [[arifos_vps_monitor]] | 20_RUNTIME | tools | engineers | intermediate | [MCP_Tools] |
| [[Concept_Decision_Velocity]] | 20_RUNTIME | paradox | researchers | advanced | [Concept_Metabolic_Pipeline] |

**Rationale**: Runtime pages answer "how do I build with arifOS?" They require foundation knowledge but precede governance nuance.

---

## 30_GOVERNANCE (Constitutional Rules)

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[Philosophy_Registry]] | 30_GOVERNANCE | philosophy | researchers | intermediate | [Floors] |
| [[Concept_Governance_Enforcer]] | 30_GOVERNANCE | constitutional | researchers | advanced | [Floors, Philosophy_Registry] |
| [[Concept_Godellock]] | 30_GOVERNANCE | paradox | researchers | advanced | [Floors] |
| [[Concept_Floor_Tensions]] | 30_GOVERNANCE | paradox | researchers | advanced | [Floors, Trinity_Architecture] |
| [[Concept_Epistemic_Circuit_Breakers]] | 30_GOVERNANCE | paradox | researchers | advanced | [Floors, Concept_Godellock] |
| [[Agents-and-AAA-Architecture]] | 30_GOVERNANCE | architecture | engineers | intermediate | [Trinity_Architecture] |

**Rationale**: Governance pages answer "what are the rules and edge cases?" They assume the reader understands foundations and wants constitutional depth.

---

## 40_HORIZONS (Future Roadmap)

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[Roadmap]] | 40_HORIZONS | roadmap | all | beginner | [What-is-arifOS] |
| [[Horizon_2_Swarm]] | 40_HORIZONS | roadmap | researchers | advanced | [agent-roles, Concept_Metabolic_Pipeline] |
| [[Horizon_3_Universal_Body]] | 40_HORIZONS | roadmap | researchers | advanced | [Horizon_2_Swarm] |
| [[Eigent_Backend]] | 40_HORIZONS | integration | engineers | intermediate | [integration-patterns] |

**Rationale**: Horizon pages answer "where is arifOS going?" They can be read early for context but require foundation knowledge to deeply understand.

---

## 50_AUDITS (Quality Tracking)

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[Drift_Checks]] | 50_AUDITS | operations | engineers | intermediate | [Tool_Surface_Architecture] |
| [[Audit_Surface_Fragmentation]] | 50_AUDITS | operations | engineers | intermediate | [Tool_Surface_Architecture] |
| [[Audit_999_SEAL_Runtime_Contrast]] | 50_AUDITS | operations | operators, engineers | intermediate | [Concept_Deployment_Architecture, Reference_MCP_Servers] |
| [[Audit_Repo_Chaos_Reduction]] | 50_AUDITS | operations | operators | intermediate | [Concept_Architecture] |
| [[Audit_MCP_Tools_vs_Wiki]] | 50_AUDITS | operations | engineers | intermediate | [MCP_Tools] |

**Rationale**: Audit pages answer "how do we maintain quality?" They are operational documents for maintainers.

---

## 90_ENTITIES (External References)

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[GEOX]] | 90_ENTITIES | architecture | all | beginner | [] |
| [[Entity_Andrej_Karpathy]] | 90_ENTITIES | philosophy | all | beginner | [] |

**Rationale**: Entity pages are reference material about external people/projects. They can be read standalone.

---

## Tool Specifications

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[ToolSpec_arifos_judge]] | 20_RUNTIME | tools | engineers | advanced | [MCP_Tools, Concept_Governance_Enforcer] |

**Rationale**: Tool specs are deep technical references. They belong to runtime but require governance context.

---

## Source Summaries

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[Changelog]] | 50_AUDITS | operations | operators | beginner | [What-is-arifOS] |
| [[Source_Karpathy_LLM_Wiki]] | 90_ENTITIES | philosophy | researchers | beginner | [] |
| [[Source_NotebookLM_HighLevel_Overview]] | 90_ENTITIES | philosophy | researchers | beginner | [] |

**Rationale**: Source pages summarize external/raw materials. They are reference documents.

---

## Synthesis Pages

| Page | Tier | Strand | Audience | Difficulty | Prerequisites |
|------|------|--------|----------|------------|---------------|
| [[Synthesis_OpenQuestions]] | 30_GOVERNANCE | roadmap | researchers | intermediate | [Roadmap, Floors] |
| [[Prerequisite_Map]] | 00_INDEX | onboarding | all | beginner | [] |

**Rationale**: Synthesis pages analyze and connect other pages. They sit at the governance/index level.

---

## Strand Coverage Summary

| Strand | Pages | Tiers Covered |
|--------|-------|---------------|
| **architecture** | 12 | 10, 20, 30, 90 |
| **constitutional** | 4 | 10, 30 |
| **integration** | 4 | 20, 40 |
| **operations** | 6 | 50 |
| **roadmap** | 4 | 40 |
| **paradox** | 4 | 20, 30 |
| **tools** | 4 | 20 |
| **philosophy** | 5 | 10, 30, 90 |

---

## Difficulty Distribution

| Difficulty | Count | Pages |
|------------|-------|-------|
| beginner | 13 | quickstart, Federation_Three_Wikis, Naming_Canon, What-is-arifOS, Floors, Trinity_Architecture, Roadmap, GEOX, Entity_Andrej_Karpathy, Changelog, Source_Karpathy_LLM_Wiki, Source_NotebookLM_HighLevel_Overview, Prerequisite_Map |
| intermediate | 21 | (see registry above) |
| advanced | 11 | Concept_Vault999_Architecture, Concept_Metabolic_Pipeline, Concept_Gateway_Architecture, Concept_Governance_Enforcer, Concept_Godellock, Concept_Floor_Tensions, Concept_Epistemic_Circuit_Breakers, Concept_Decision_Velocity, ToolSpec_arifos_judge, Horizon_2_Swarm, Horizon_3_Universal_Body |

---

## Auto-Generated Paths

### Path: New Engineer
```
quickstart → What-is-arifOS → Trinity_Architecture → Metabolic_Loop → MCP_Tools → integration-patterns → agent-roles
```

### Path: Safety Researcher
```
quickstart → What-is-arifOS → Floors → Philosophy_Registry → Concept_Governance_Enforcer → Concept_Floor_Tensions → Concept_Epistemic_Circuit_Breakers
```

### Path: Platform Architect
```
quickstart → Trinity_Architecture → Concept_Architecture → Concept_Deployment_Architecture → Horizon_2_Swarm → Horizon_3_Universal_Body
```

### Path: Operator (DevOps)
```
quickstart → MCP_Tools → Reference_MCP_Servers → Audit_999_SEAL_Runtime_Contrast → Drift_Checks
```

---

## Maintenance Notes

### Adding a New Page

1. Add entry to this registry
2. Determine: tier, strand, audience, difficulty, prerequisites
3. Create page with matching YAML frontmatter
4. Run `python wiki/scripts/generate_views.py`
5. Verify in `wiki/view/`

### Updating This Registry

- Bump version in header
- Log changes in wiki/log.md
- Run view generator after updates

---

**Registry Version**: 2026.04.11  
**Total Pages**: 45  
**DITEMPA BUKAN DIBERI** — Forged, Not Given.
