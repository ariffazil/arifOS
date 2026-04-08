---
type: Meta
tier: 00_INDEX
strand: [onboarding]
audience: [all]
difficulty: beginner
prerequisites: []
tags: [meta, dependencies, graph, navigation, wiki-infrastructure]
sources: [wiki/pages/*.md]
last_sync: 2026-04-08
confidence: 0.95
---
# Ω-Wiki Prerequisite Map

> The dependency graph of arifOS knowledge. Each arrow represents a "must understand before" relationship.

## Visual Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TIER 00: FOUNDATIONS                                 │
│                                                                              │
│   SCHEMA ─────────────────────────────────────────────────────────────┐     │
│      │                                                                │     │
│      ▼                                                                ▼     │
│   What-is-arifOS ───┐                                              Trinity_Architecture
│      │              │                                                    │  │
│      ▼              ▼                                                    ▼  ▼
│   Floors ──────────┴───────────────────────────────────────────────────────┘  │
│      │                                                                        │
│      ▼                                                                        │
│   Concept_Floor_Tensions ◄────────────────────────────────────────────────────┘
│      │
├──────┴──────────────────────────────────────────────────────────────────────┤
│                         TIER 10: CONCEPTS                                    │
│                                                                              │
│      ▼                                                                       │
│   Metabolic_Loop ◄──────────────────────────────┐                            │
│      │                                           │                            │
│      ▼                                           ▼                            │
│   Concept_Godellock                          Concept_Epistemic_Circuit_Breakers
│      │                                           │                            │
│      │                                           ▼                            │
│      └──────────────────────────────────────► Concept_Decision_Velocity       │
│                                                    ▲                          │
├────────────────────────────────────────────────────┼──────────────────────────┤
│                                                    │                         │
│                         TIER 20: RUNTIME           │                         │
│                                                    │                         │
│   MCP_Tools ◄─────────────────────────────────────┘                         │
│      │                                                                       │
│      ▼                                                                       │
│   Tool_Surface_Architecture                                                  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                         TIER 30: GOVERNANCE                                  │
│                                                                              │
│   Concept_Governance_Enforcer                                                │
│      │                                                                       │
│      ▼                                                                       │
│   Philosophy_Registry                                                        │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                         TIER 40: HORIZONS                                    │
│                                                                              │
│   Horizon_2_Swarm                                                            │
│      │                                                                       │
│      ▼                                                                       │
│   Horizon_3_Universal_Body                                                   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                         TIER 50: AUDITS                                      │
│                                                                              │
│   Audit_Surface_Fragmentation                                                │
│      │                                                                       │
│      ▼                                                                       │
│   Drift_Checks                                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tabular View

### Tier 00: Foundations (Start Here)
| Page | Prerequisites | Concepts Introduced | Reading Time |
|------|--------------|---------------------|--------------|
| [[SCHEMA]] | None | Wiki constitution, YAML format | 5 min |
| [[What-is-arifOS]] | [[SCHEMA]] | Motto, core philosophy, high-level overview | 10 min |
| [[Floors]] | [[What-is-arifOS]] | F1-F13 definitions, Hard/Soft classification | 15 min |
| [[Trinity_Architecture]] | [[What-is-arifOS]] | ΔΩΨ rings, W³ consensus, AAA stack | 12 min |
| [[Concept_Floor_Tensions]] | [[Floors]], [[Trinity_Architecture]] | Conflict resolution, HARD>SOFT rule | 18 min |

### Tier 10: Concepts (The Deep Dives)
| Page | Prerequisites | Concepts Introduced | Reading Time |
|------|--------------|---------------------|--------------|
| [[Metabolic_Loop]] | [[Floors]] | 000-999 stages, floor activations | 20 min |
| [[Concept_Godellock]] | [[Floors]] | Ω₀ band, confidence calibration | 15 min |
| [[Concept_Epistemic_Circuit_Breakers]] | [[Floors]], [[Concept_Floor_Tensions]], [[Concept_Godellock]] | CB1-CB5, self-distrust triggers | 25 min |
| [[Concept_Decision_Velocity]] | [[Metabolic_Loop]], [[Concept_Floor_Tensions]], [[Concept_Epistemic_Circuit_Breakers]] | Latency budget, F1 Tax, parallelism | 22 min |

### Tier 20: Runtime (Implementation Details)
| Page | Prerequisites | Concepts Introduced | Reading Time |
|------|--------------|---------------------|--------------|
| [[MCP_Tools]] | [[Floors]], [[Metabolic_Loop]] | Tool surface, canonical UX verbs | 18 min |
| [[Tool_Surface_Architecture]] | [[MCP_Tools]], [[Concept_Governance_Enforcer]] | Spec layers, compatibility boundaries | 20 min |
| [[Agents-and-AAA-Architecture]] | [[Trinity_Architecture]] | Ring 3 execution, practical layer | 15 min |
| [[Concept_Architecture]] | [[Trinity_Architecture]] | CCC/AAA layers, vertical/horizontal maps | 16 min |
| [[Concept_Deployment_Architecture]] | [[Concept_Architecture]] | Gateway vs VPS, Horizon I/II/III | 18 min |

### Tier 30: Governance (The Rules)
| Page | Prerequisites | Concepts Introduced | Reading Time |
|------|--------------|---------------------|--------------|
| [[Concept_Governance_Enforcer]] | [[Floors]], [[Concept_Floor_Tensions]] | Hard-stops, Class A/B/C tools | 20 min |
| [[Philosophy_Registry]] | [[Concept_Godellock]] | 83 quotes, G★ bands, deterministic selection | 12 min |

### Tier 40: Horizons (Future Roadmap)
| Page | Prerequisites | Concepts Introduced | Reading Time |
|------|--------------|---------------------|--------------|
| [[Horizon_2_Swarm]] | [[Concept_Architecture]], [[MCP_Tools]] | A2A protocols, EvidenceBundle, ΔS Gauges | 25 min |
| [[Horizon_3_Universal_Body]] | [[Horizon_2_Swarm]] | HSM/BLS, WebMCP P2P, hardware sovereignty | 30 min |

### Tier 50: Audits (Quality Assurance)
| Page | Prerequisites | Concepts Introduced | Reading Time |
|------|--------------|---------------------|--------------|
| [[Audit_Surface_Fragmentation]] | [[Tool_Surface_Architecture]] | Surface inventory, drift detection | 15 min |
| [[Drift_Checks]] | [[Audit_Surface_Fragmentation]] | Automated validation, CI guidance | 12 min |

## Critical Path Analysis

### Minimum Viable Understanding
To operate arifOS, you MUST understand:
1. **What-is-arifOS** → The philosophy
2. **Floors** → The constraints  
3. **Trinity_Architecture** → The separation of concerns
4. **Metabolic_Loop** → The execution flow

**Total reading time**: ~57 minutes

### Full Runtime Understanding
To modify or extend arifOS, you ALSO need:
5. **Concept_Floor_Tensions** → How constraints conflict
6. **Concept_Epistemic_Circuit_Breakers** → Self-distrust mechanisms
7. **MCP_Tools** → The tool surface
8. **Concept_Governance_Enforcer** → Enforcement mechanisms

**Total reading time**: ~137 minutes (~2.3 hours)

### Complete Architecture Understanding
To redesign arifOS, you ALSO need:
9. **Concept_Architecture** → Deep structural patterns
10. **Concept_Decision_Velocity** → Performance tradeoffs
11. **Horizon_2_Swarm** → Multi-agent patterns
12. **Horizon_3_Universal_Body** → Hardware sovereignty

**Total reading time**: ~234 minutes (~4 hours)

## Dependency Graph (Adjacency List)

```yaml
# Machine-parseable dependency map
dependencies:
  What-is-arifOS:
    requires: [SCHEMA]
    unlocks: [Floors, Trinity_Architecture]
  
  Floors:
    requires: [What-is-arifOS]
    unlocks: [Metabolic_Loop, Concept_Godellock, Concept_Floor_Tensions, MCP_Tools]
  
  Trinity_Architecture:
    requires: [What-is-arifOS]
    unlocks: [Concept_Architecture, Agents-and-AAA-Architecture, Concept_Floor_Tensions]
  
  Concept_Floor_Tensions:
    requires: [Floors, Trinity_Architecture]
    unlocks: [Concept_Epistemic_Circuit_Breakers, Concept_Decision_Velocity, Concept_Governance_Enforcer]
  
  Metabolic_Loop:
    requires: [Floors]
    unlocks: [Concept_Decision_Velocity, MCP_Tools]
  
  Concept_Godellock:
    requires: [Floors]
    unlocks: [Concept_Epistemic_Circuit_Breakers, Philosophy_Registry]
  
  Concept_Epistemic_Circuit_Breakers:
    requires: [Floors, Concept_Floor_Tensions, Concept_Godellock]
    unlocks: [Concept_Decision_Velocity]
  
  Concept_Decision_Velocity:
    requires: [Metabolic_Loop, Concept_Floor_Tensions, Concept_Epistemic_Circuit_Breakers]
    unlocks: []
  
  MCP_Tools:
    requires: [Floors, Metabolic_Loop]
    unlocks: [Tool_Surface_Architecture]
  
  Concept_Governance_Enforcer:
    requires: [Floors, Concept_Floor_Tensions]
    unlocks: [Tool_Surface_Architecture]
  
  Tool_Surface_Architecture:
    requires: [MCP_Tools, Concept_Governance_Enforcer]
    unlocks: [Audit_Surface_Fragmentation]
  
  Audit_Surface_Fragmentation:
    requires: [Tool_Surface_Architecture]
    unlocks: [Drift_Checks]
  
  Concept_Architecture:
    requires: [Trinity_Architecture]
    unlocks: [Concept_Deployment_Architecture, Horizon_2_Swarm]
  
  Horizon_2_Swarm:
    requires: [Concept_Architecture, MCP_Tools]
    unlocks: [Horizon_3_Universal_Body]
```

## Orphaned Pages (No Prerequisites Listed)

These pages can be read in any order:
- [[SCHEMA]] — Wiki constitution (by design, it's the root)
- [[Entity_Andrej_Karpathy]] — External reference
- [[GEOX]] — Entity page (context-dependent)

## Circular Dependencies

None detected. The prerequisite graph is a **DAG** (Directed Acyclic Graph), which allows for topological sorting and guided learning paths.

## Missing Prerequisites (Audit Findings)

Pages that SHOULD list prerequisites but don't:
- [ ] [[Eigent_Backend]] — Should require [[Agents-and-AAA-Architecture]]
- [ ] [[Concept_Metabolic_Pipeline]] — Duplicate of [[Metabolic_Loop]], should merge
- [ ] [[Synthesis_OpenQuestions]] — Should require familiarity with whole wiki

## How to Use This Map

### For New Contributors
1. Start at **Tier 00** (Foundations)
2. Follow the arrows — don't skip prerequisites
3. If stuck, check the [[Start_Here]] guided path

### For Maintainers
1. Before editing a page, check its **depended_by** list
2. Changes to [[Floors]] affect 6+ downstream pages
3. Changes to [[Trinity_Architecture]] affect 4+ downstream pages

### For LLM Agents
```python
# Use this map to load context efficiently
def load_prerequisites(page_name):
    """Load all prerequisite pages before processing"""
    prereqs = dependencies[page_name]["requires"]
    for prereq in prereqs:
        load_page(prereq)
    load_page(page_name)
```

## Maintenance Notes

**Auto-generation**: This page should be regenerated when:
- New pages added to wiki/pages/
- Prerequisites change in existing pages
- Tier structure reorganized

**Update command** (future automation):
```bash
python scripts/generate_prerequisite_map.py --output wiki/pages/Prerequisite_Map.md
```

---

> **Ω-Wiki Tag**: `prerequisite_map_v1.0`
> 
> **Generated From**: YAML frontmatter of 36 wiki pages
> 
> **Last Validation**: 2026-04-08 — All prerequisite chains verified, no circular dependencies found.
