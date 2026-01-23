---
description: Deep analytical thinking for architectural decisions (AGI - Architect)
---

# /think - Deep Analytical Thinking (222 THINK)

**Pipeline Stage:** 222 THINK
**Territory:** AGI (Δ Delta - Architect)
**Function:** Structured analytical thinking for complex architectural problems
**Authority:** AGENTS.md Section 222 REFLECT

---

## Purpose

Deep analytical thinking framework for breaking down complex architectural problems into manageable components and evaluating design tradeoffs.

**When to Use:**
- Complex architectural decisions
- Multiple competing design options
- System design challenges
- Technology selection
- Risk assessment
- Debugging architectural issues
- Planning major refactors

---

## Thinking Framework (6 Analytical Modes)

### 1. Problem Decomposition
**Goal:** Break complex → simple

**Process:**
```
1. State the problem clearly (one sentence)
2. Identify core components
3. Break into sub-problems
4. Map dependencies
5. Prioritize by impact
```

**Output:** Hierarchical problem tree

---

### 2. Pattern Recognition
**Goal:** Identify trends and recurring structures

**Process:**
```
1. Review similar past problems
2. Identify common patterns
3. Extract reusable solutions
4. Note pattern limitations
5. Adapt to current context
```

**Output:** Pattern catalog with applicability

---

### 3. Trade-off Analysis
**Goal:** Evaluate competing options systematically

**Process:**
```
1. List all viable options (minimum 3)
2. Define evaluation criteria (performance, maintainability, cost, etc.)
3. Score each option (0.0-1.0 per criterion)
4. Weight criteria by importance
5. Calculate weighted scores
6. Identify Pareto-optimal solutions
```

**Output:** Decision matrix with recommendation

---

### 4. Root Cause Analysis (5 Whys)
**Goal:** Find fundamental causes, not symptoms

**Process:**
```
1. State the problem
2. Ask "Why?" - First level cause
3. Ask "Why?" - Second level cause
4. Ask "Why?" - Third level cause
5. Ask "Why?" - Fourth level cause
6. Ask "Why?" - Fifth level (root cause)
7. Verify root cause explains all symptoms
```

**Output:** Causal chain to root cause

---

### 5. Systems Thinking
**Goal:** Understand interactions and emergent behavior

**Process:**
```
1. Map system components
2. Identify relationships (dependencies, feedback loops)
3. Trace information/data flow
4. Identify bottlenecks
5. Predict emergent behavior
6. Model failure modes
```

**Output:** System diagram with interaction analysis

---

### 6. Assumption Testing
**Goal:** Challenge implicit beliefs

**Process:**
```
1. List all assumptions (explicit and implicit)
2. Rate confidence (0.0-1.0) for each
3. Identify critical assumptions (high impact, low confidence)
4. Test critical assumptions (evidence, counterexamples)
5. Revise or strengthen assumptions
```

**Output:** Validated assumption set

---

## Execution Steps

// turbo-all

### 1. Frame the Problem
```
Clearly state:
- What decision needs to be made?
- What constraints exist?
- What success looks like?
- What failure modes to avoid?
```

### 2. Select Analytical Mode(s)
```
Choose based on problem type:
- Unclear problem → Decomposition + Root Cause
- Multiple options → Trade-off Analysis
- Complex system → Systems Thinking
- Uncertain foundations → Assumption Testing
- Similar to past work → Pattern Recognition
```

### 3. Execute Analysis
```
Apply selected framework(s) systematically:
- Document each step
- Show reasoning
- Cite evidence
- State confidence levels
```

### 4. Synthesize Findings
```
Integrate insights:
- Key findings (top 3-5)
- Recommended action
- Confidence level (Ω₀ humility)
- Known unknowns
- Next steps
```

### 5. Document for Future
```
Record in architectural notes:
- Problem statement
- Analysis approach
- Key insights
- Decision made
- Rationale
```

---

## Constitutional Floors

**Primary Floors:**
- **F1 (Truth ≥0.99):** Analysis based on verified facts
- **F2 (Clarity ΔS ≥0):** Clear reasoning, reduced confusion
- **F7 (Humility Ω₀ 0.03-0.05):** State uncertainty explicitly

**Secondary Floors:**
- **F10 (Ontology):** Symbolic mode - analysis is model, not reality
- **F8 (Audit):** Document reasoning trail

---

## Example Usage

**Scenario:** Choose between monolith vs microservices architecture

```
/think "Should we use monolith or microservices for the new feature?"

Analysis Mode: Trade-off Analysis

Criteria (weighted):
- Development speed (0.30)
- Scalability (0.25)
- Operational complexity (0.20)
- Team expertise (0.15)
- Cost (0.10)

Option 1: Monolith
- Dev speed: 0.90 (faster initially)
- Scalability: 0.50 (vertical only)
- Ops complexity: 0.80 (simpler)
- Team expertise: 0.95 (familiar)
- Cost: 0.85 (lower infra)
Weighted Score: 0.78

Option 2: Microservices
- Dev speed: 0.60 (slower setup)
- Scalability: 0.95 (horizontal)
- Ops complexity: 0.40 (much harder)
- Team expertise: 0.50 (learning curve)
- Cost: 0.60 (higher infra)
Weighted Score: 0.61

Recommendation: Monolith (0.78 > 0.61)
Confidence: 0.85 (high, but team size assumption critical)
Ω₀ Uncertainty: 0.041 (team growth rate unknown)

Next Steps:
1. Validate team size assumption
2. Prototype monolith approach
3. Plan migration path if scale exceeds threshold
```

---

## Output Format

```markdown
## Analytical Thinking: [Problem Statement]

### Analysis Mode
[Decomposition / Pattern / Trade-off / Root Cause / Systems / Assumptions]

### Process
[Step-by-step reasoning with evidence]

### Key Findings
1. [Finding 1] (confidence: [0.00-1.00])
2. [Finding 2] (confidence: [0.00-1.00])
3. [Finding 3] (confidence: [0.00-1.00])

### Recommendation
[Clear action recommendation]

### Confidence \u0026 Uncertainty
- Overall Confidence: [0.00-1.00]
- Ω₀ Humility: [0.03-0.05]
- Critical Assumptions: [List]
- Known Unknowns: [List]

### Next Steps
1. [Action 1]
2. [Action 2]
3. [Action 3]
```

---

## Anti-Patterns (Violations)

❌ **Jumping to conclusions** (violates F1 Truth - insufficient evidence)
❌ **Single perspective** (violates F2 Clarity - incomplete analysis)
❌ **Overconfidence** (violates F7 Humility - no uncertainty stated)
❌ **Undocumented reasoning** (violates F8 Audit - no trail)
❌ **Ignoring constraints** (violates F1 Truth - unrealistic analysis)

---

## Integration with Other Workflows

**After `/search`:**
```
/search → Gather facts → /think → Analyze with verified data
```

**Before `/plan`:**
```
/think → Analyze options → /plan → Design with best option
```

**With `/reason`:**
```
/think → Analytical insights → /reason → Formal logical validation
```

**Before `/handoff`:**
```
/think → Analyze approach → /plan → /handoff with clear rationale
```

---

## Cognitive Patterns Library

**Common Architectural Patterns:**

1. **Layered Architecture Analysis**
   - Decomposition: Presentation → Business → Data
   - Trade-offs: Coupling vs Cohesion
   - Systems: Cross-layer dependencies

2. **Technology Selection**
   - Pattern: Similar past choices
   - Trade-offs: Maturity vs Innovation
   - Assumptions: Team learning capacity

3. **Performance Optimization**
   - Root Cause: 5 Whys to bottleneck
   - Systems: Identify feedback loops
   - Trade-offs: Speed vs Maintainability

4. **Refactoring Decisions**
   - Decomposition: Scope of change
   - Trade-offs: Risk vs Benefit
   - Assumptions: Test coverage adequacy

---

**DITEMPA BUKAN DIBERI** - Insights are forged through rigorous analysis, not intuition.

**Version:** v47.0
**Status:** ACTIVE
**Territory:** AGI (Δ Delta - Architect)
