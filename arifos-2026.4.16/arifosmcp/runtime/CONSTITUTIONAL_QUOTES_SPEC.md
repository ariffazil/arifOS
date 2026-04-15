# Constitutional Quotes Specification v2.1.0-unified

**Unified Human Calibration Anchors** | **50 Core Quotes** | **10 arifOS Tools**

---

## Design Philosophy

> **Each tool has its own counter-bias instrument.**  
> **Not one philosophy bucket — tool-specific calibration anchors.**

```
tool-specific corpus
    → mapped to tool function
    → mapped to output fields
    → triggered by runtime conditions
```

---

## Unified Corpus Overview

| Metric | Value |
|--------|-------|
| **Total Quotes** | 50 (core set) |
| **Tools Covered** | 10/10 |
| **Schema Version** | 2.1.0-unified |
| **Source** | Internal + External Validator Consensus |

---

## Schema Specification

### Full Quote Anchor Structure

```json
{
  "quote_id": "TOOL_Q_###",
  "tool": "arifos.toolname",
  "category": "category_per_specification",
  "author": "Full Name",
  "quote": "The human wisdom text",
  "attribution_status": "exact | traditional_attribution | paraphrase | attributed | summary_attribution",
  "constitutional_role": "What this tool does constitutionally",
  "function": ["reasoning_function_1", "reasoning_function_2"],
  "trigger_when": ["runtime_condition_1", "runtime_condition_2"],
  "output_map": ["output_field_1", "output_field_2"],
  "use_mode": ["reason", "reflect", "forge"],
  "priority": "core"
}
```

---

## Tool-by-Tool Architecture

| Tool | Stage | Trinity | Quotes | Constitutional Role | Counter-Bias Function |
|------|-------|---------|--------|--------------------|-----------------------|
| `arifos.init` | 000_INIT | Δ | 5 | anchor, bind identity, establish scope | suppress: premature action, authority without humility |
| `arifos.sense` | 111_SENSE | Δ | 5 | reality intake, evidence grounding, temporal verification | suppress: hallucination, false certainty, weak evidence |
| `arifos.mind` | 333_MIND | Δ | 5 | structured reasoning, synthesis, reflection | suppress: contradiction, shallow thinking, illusion of knowledge |
| `arifos.route` | 444_ROUTER | Δ | 5 | lane selection, downstream routing | suppress: wrong lane, speed over fit, force over discernment |
| `arifos.memory` | 555_MEMORY | Ω | 5 | continuity, persistence, recall | suppress: amnesia, equal retention, ignoring history |
| `arifos.heart` | 666_HEART | Ω | 5 | ethical review, dignity protection | suppress: cruelty, dehumanization, cold optimization |
| `arifos.ops` | 777_OPS | Ψ | 5 | execution, implementation, operations | suppress: talk without execution, bloated plans, fragility |
| `arifos.judge` | 888_JUDGE | Ψ | 5 | verdict, consequence boundary | suppress: reckless verdicts, power without restraint |
| `arifos.forge` | 888_FORGE | Δ | 5 | shape durable doctrine, schema, artifact | suppress: excess, complexity without strength |
| `arifos.vault` | 999_VAULT | Ψ | 5 | seal, preserve, archive canonical record | suppress: careless recordkeeping, fake finality |

---

## Category Mapping by Tool

### arifos.init (000)
**Categories:** `origin_intent`, `boundary_authority`, `humility_at_start`, `foundation_first`  
**Output Map:** `session_anchor`, `intent_clarity`, `authority_scope`, `initial_constraints`

### arifos.sense (111)
**Categories:** `perception_reality`, `evidence_first`, `temporal_awareness`, `ambiguity_restraint`  
**Output Map:** `truth_classification`, `evidence_plan`, `temporal_grounding`, `ambiguity`, `uncertainty`

### arifos.mind (333)
**Categories:** `logic_truth`, `uncertainty_humility`, `knowledge_selfknowledge`, `order_complexity_limits`  
**Output Map:** `reasoning_chain`, `assumptions`, `unknowns`, `coherence_check`, `tradeoffs`

### arifos.route (444)
**Categories:** `discernment`, `right_path`, `choice_under_uncertainty`, `fit_for_purpose`  
**Output Map:** `route_selection`, `route_reason`, `next_stage`, `branch_confidence`

### arifos.memory (555)
**Categories:** `memory_identity`, `history_continuity`, `forgetting_loss`, `selective_retention`  
**Output Map:** `memory_write`, `memory_recall`, `continuity_link`, `retention_priority`

### arifos.heart (666)
**Categories:** `human_dignity`, `compassion`, `non_harm`, `means_and_ends`  
**Output Map:** `ethical_flags`, `human_impact`, `dignity_check`, `harm_risk`, `peace_check`

### arifos.ops (777)
**Categories:** `execution_over_planning`, `doing_not_debating`, `simple_is_strong`, `resilience_action`  
**Output Map:** `op_action`, `op_resilience`, `op_progress`, `op_bottleneck`

### arifos.judge (888)
**Categories:** `justice_fairness`, `consequence_responsibility`, `mercy_judgment`, `power_restraint`  
**Output Map:** `verdict`, `verdict_confidence`, `justice_sense`, `consequence`, `override_flags`

### arifos.forge (888)
**Categories:** `building_making`, `craft_excellence`, `form_function`, `shaping_durable`  
**Output Map:** `artifact`, `schema`, `durability`, `signature`, `forge_reason`

### arifos.vault (999)
**Categories:** `permanence_transience`, `truth_recording`, `seal_finality`, `preservation_endurance`  
**Output Map:** `record_hash`, `seal_signature`, `verdict`, `preservation_confidence`

---

## Attribution Hygiene Tier System

| Tier | Status | Usage |
|------|--------|-------|
| `exact` | Word-perfect | Canonical quotes, legal citations |
| `traditional_attribution` | Cultural convention | "Do unto others" (Golden Rule tradition) |
| `paraphrase` | Rephrased meaning | "As Einstein might say, if everything's urgent..." |
| `attributed` | Source uncertain | "Attributed to Sun Tzu, The Art of War" |
| `summary_attribution` | Condensed | "Drawing from the wisdom of..." |

---

## Use Modes

```
MODE: reason
    → Inject into chain-of-thought
    → Surface to CLI for human transparency

MODE: reflect  
    → Append to session reflection
    → Use in milestone review

MODE: forge
    → Include in doctrine artifact
    → Preserve in seal
```

---

## Integration Pattern

```python
# Runtime quote injection (tool invocation)
async def inject_quotes(tool: str, context: Dict) -> List[Quote]:
    corpus = load_quotes_for_tool(tool)
    triggered = [
        q for q in corpus
        if any(t in context.get("flags", []) for t in q.trigger_when)
    ]
    return triggered[:2]  # Max 2 per invocation

# Forge-time preservation
async def embed_quotes(doctrine: Doctrine, tool: str) -> Doctrine:
    relevant = get_core_quotes(tool)
    doctrine.metadata.quote_anchors = relevant
    return doctrine
```

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2025-04 | Initial 102-quote corpus per tool |
| 1.5.0 | 2025-04 | External validator review (approved with feedback) |
| 2.0.0 | 2025-04 | Consolidated to 50 core quotes (5 per tool) |
| 2.1.0-unified | 2025-04 | Unified schema with full mapping to outputs |

---

## Seal

**999_VALIDATOR** | Each quote anchor is a commitment.  
**Ω_Ψ_Δ** | Trinity-aligned. Tool-calibrated. Runtime-ready.

```
╔═══════════════════════════════════════╗
║  ARIFOS CONSTITUTIONAL QUOTES CORPUS  ║
║  Version 2.1.0-unified                ║
║  Status: CANONICAL                    ║
╚═══════════════════════════════════════╝
```
