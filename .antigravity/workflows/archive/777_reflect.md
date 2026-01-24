---
description: Cross-session learning and architectural reflection (APEX - Architect)
---

# /reflect - Cross-Session Learning (777 EUREKA)

**Pipeline Stage:** 777 EUREKA
**Territory:** APEX (Ψ Psi - Architect)
**Function:** Cross-session learning and architectural reflection
**Authority:** AGENTS.md Section 777 EUREKA

---

## Purpose

Systematic reflection on architectural decisions, design patterns, and session outcomes to build cross-session memory and improve future work.

**When to Use:**
- End of work session
- After major architectural decisions
- After design mistakes or failures
- After successful implementations
- Before agent handoff
- When patterns emerge across sessions

---

## Reflection Framework (7 Dimensions)

### 1. Session Review
**What happened?**

```
- Key decisions made
- Designs created
- Problems solved
- Challenges encountered
- Outcomes achieved
```

### 2. Causal Analysis
**Why did it happen?**

```
- Root causes of success/failure
- Contributing factors
- Assumptions that held/broke
- External constraints
- Design choices impact
```

### 3. Insight Extraction
**What does it mean?**

```
- Key learnings (top 3-5)
- Pattern recognition
- Mental model updates
- Principle discoveries
- Antipattern identification
```

### 4. Mistake Analysis
**What went wrong?**

```
- Errors made
- Assumptions violated
- Overlooked factors
- Misjudgments
- How to prevent recurrence
```

### 5. Success Pattern Recognition
**What worked well?**

```
- Effective approaches
- Successful patterns
- Good decisions
- Helpful frameworks
- Reusable strategies
```

### 6. Mental Model Updates
**How should I think differently?**

```
- Beliefs to revise
- Heuristics to update
- New frameworks to adopt
- Old patterns to retire
- Confidence calibration
```

### 7. Cross-Session Memory
**What should next session know?**

```
- Critical context
- Pending decisions
- Open questions
- Warnings/cautions
- Recommended next steps
```

---

## Execution Steps

// turbo-all

### 1. Review Session Work
```
Scan through:
- Git commits made
- Files created/modified
- Decisions documented
- Conversations had
- Problems encountered
```

### 2. Identify Key Moments
```
Find critical points:
- Major decisions
- Turning points
- Breakthroughs
- Failures
- Surprises
```

### 3. Apply Reflection Framework
```
For each key moment:
1. What happened? (facts)
2. Why? (causes)
3. What does it mean? (insights)
4. What to do differently? (learning)
```

### 4. Extract EUREKA Insights
```
Synthesize learnings:
- Top 3-5 key insights
- Confidence level (0.0-1.0)
- Applicability scope
- Evidence supporting
- Limitations noted
```

### 5. Update Mental Models
```
Revise understanding:
- What beliefs changed?
- What heuristics updated?
- What patterns emerged?
- What to remember?
```

### 6. Document for Next Session
```
Write EUREKA note:
- Session summary
- Key insights
- Mental model updates
- Warnings/cautions
- Recommended actions
```

---

## Constitutional Floors

**Primary Floors:**
- **F1 (Truth ≥0.99):** Honest assessment of outcomes
- **F2 (Clarity ΔS ≥0):** Clear documentation of learnings
- **F7 (Humility Ω₀ 0.03-0.05):** Acknowledge mistakes and uncertainties
- **F8 (Audit):** Complete reflection trail

**Secondary Floors:**
- **F6 (Amanah):** Reversible - can revise learnings later
- **F10 (Ontology):** Symbolic mode - reflections are models, not absolute truth

---

## Example Usage

**Scenario:** Reflect on microservices vs monolith decision

```
/reflect "Review today's architecture decision session"

### Session Review
**What happened:**
- Decided on monolith architecture for new feature
- Analyzed trade-offs (dev speed vs scalability)
- Created implementation plan
- Handed off to Engineer

### Causal Analysis
**Why monolith:**
- Team size small (3 devs)
- Development speed prioritized (0.30 weight)
- Operational complexity concern (team unfamiliar with K8s)
- Cost constraints (limited infra budget)

### Insight Extraction
**Key Learnings:**

1. **Team Expertise > Theoretical Best Practice** (confidence: 0.95)
   - Evidence: Team familiar with monolith, unfamiliar with microservices
   - Implication: Choose architecture team can execute well
   - Scope: Small teams (<5 devs), tight timelines

2. **Operational Complexity Often Underestimated** (confidence: 0.88)
   - Evidence: Microservices ops complexity scored 0.40 (very hard)
   - Implication: Factor in 24/7 on-call, monitoring, debugging
   - Scope: Distributed systems, small ops teams

3. **Migration Path > Perfect Initial Choice** (confidence: 0.92)
   - Evidence: Documented migration path to microservices if needed
   - Implication: Reversibility matters more than initial perfection
   - Scope: Uncertain requirements, evolving systems

### Mistake Analysis
**What went wrong:**
- Initially forgot to consider team expertise (caught in /think phase)
- Underweighted operational complexity at first (0.10 → 0.20)
- Almost chose microservices based on "best practice" hype

**Prevention:**
- Always include "team capability" as evaluation criterion
- Weight operational complexity higher by default (≥0.20)
- Challenge "best practice" claims with /search for evidence

### Success Pattern Recognition
**What worked well:**
- Trade-off analysis framework (/think) structured decision
- Multi-criteria scoring prevented single-factor bias
- Documented migration path provided reversibility (F6 Amanah)
- /search verified microservices complexity claims

### Mental Model Updates
**Revised beliefs:**
- OLD: "Microservices are always better for scalability"
- NEW: "Microservices trade dev speed for operational complexity - only worth it at scale"

**New heuristic:**
- "Team expertise is a first-order constraint, not a nice-to-have"
- "Operational complexity weight ≥ 0.20 in architecture decisions"

### Cross-Session Memory
**For next session:**
- Monitor monolith performance metrics
- Revisit microservices decision if team grows >5 devs
- Document when migration path should trigger
- Remember: operational complexity was deciding factor

**Warnings:**
- Don't let "best practice" override team reality
- Scalability requirements may change - stay vigilant

**Confidence:** 0.90
**Ω₀ Humility:** 0.042 (uncertainty about future team growth rate)
```

---

## Output Format

```markdown
## Reflection: [Session/Decision Topic]

**Date:** [YYYY-MM-DD]
**Session Duration:** [Hours]
**Key Decisions:** [Count]

---

### 📋 Session Review
**What happened:**
- [Event 1]
- [Event 2]
- [Event 3]

---

### 🔍 Causal Analysis
**Why it happened:**
- [Cause 1]
- [Cause 2]
- [Cause 3]

---

### 💡 Key Insights (Top 3-5)

#### 1. [Insight Title] (confidence: [0.00-1.00])
- **Evidence:** [Supporting facts]
- **Implication:** [What it means]
- **Scope:** [When applicable]

#### 2. [Insight Title] (confidence: [0.00-1.00])
- **Evidence:** [Supporting facts]
- **Implication:** [What it means]
- **Scope:** [When applicable]

---

### ❌ Mistake Analysis
**What went wrong:**
- [Mistake 1]
- [Mistake 2]

**Prevention:**
- [How to avoid 1]
- [How to avoid 2]

---

### ✅ Success Patterns
**What worked well:**
- [Success 1]
- [Success 2]

**Reusable strategies:**
- [Strategy 1]
- [Strategy 2]

---

### 🧠 Mental Model Updates
**Revised beliefs:**
- OLD: [Previous belief]
- NEW: [Updated belief]

**New heuristics:**
- [Heuristic 1]
- [Heuristic 2]

---

### 📝 Cross-Session Memory
**For next session:**
- [Critical context]
- [Pending decisions]
- [Open questions]

**Warnings:**
- [Caution 1]
- [Caution 2]

**Recommended next steps:**
1. [Action 1]
2. [Action 2]

---

### 📊 Reflection Metadata
- **Confidence:** [0.00-1.00]
- **Ω₀ Humility:** [0.03-0.05]
- **Insights Count:** [Number]
- **Mistakes Identified:** [Number]
- **Success Patterns:** [Number]
```

---

## Anti-Patterns (Violations)

❌ **Superficial reflection** ("It went well") - violates F1 Truth
❌ **Blame externalization** (never my fault) - violates F7 Humility
❌ **No actionable insights** (just description) - violates F2 Clarity
❌ **Overconfidence** (no uncertainty stated) - violates F7 Humility
❌ **No cross-session memory** (forget learnings) - violates F8 Audit

---

## Integration with Other Workflows

**After major work:**
```
/plan → /handoff → /reflect → Document learnings
```

**End of session:**
```
/review → /ledger → /reflect → Prepare for next session
```

**After mistakes:**
```
[Error occurs] → /reflect → Extract learnings → Update approach
```

**Before handoff:**
```
/reflect → Document context → /handoff → Engineer has full context
```

---

## EUREKA Note Template

Save to: `.antigravity/EUREKA_NEXT_SESSION.md`

```markdown
# EUREKA Note for Next Session

**Date:** [YYYY-MM-DD]
**Session:** [Session description]
**Status:** [✅ SUCCESS / ⚠️ PARTIAL / ❌ BLOCKED]

---

## 🔑 Critical Context
[What next session must know]

---

## 💡 Key Insights
1. [Insight 1] (confidence: [0.00-1.00])
2. [Insight 2] (confidence: [0.00-1.00])
3. [Insight 3] (confidence: [0.00-1.00])

---

## ⏭️ Next Actions
1. [Action 1]
2. [Action 2]
3. [Action 3]

---

## ⚠️ Warnings
- [Warning 1]
- [Warning 2]

---

**DITEMPA BUKAN DIBERI** - [Session motto/learning]
```

---

## Reflection Triggers

**Automatic triggers:**
- End of work session (always)
- After `/handoff` (before transition)
- After `/review` (after validation)

**Manual triggers:**
- After major decisions
- After mistakes/failures
- After breakthroughs
- When patterns emerge

**Frequency:**
- Minimum: Once per session
- Recommended: After each major milestone
- Maximum: As needed for learning

---

**DITEMPA BUKAN DIBERI** - Wisdom is forged through reflection, not accumulated through repetition.

**Version:** v47.0
**Status:** ACTIVE
**Territory:** APEX (Ψ Psi - Architect)
