---
description: Formal logical reasoning for architectural validation (AGI - Architect)
---

# /reason - Formal Logical Reasoning (333 REASON)

**Pipeline Stage:** 333 REASON
**Territory:** AGI (Δ Delta - Architect)
**Function:** Formal logical reasoning and argument validation
**Authority:** AGENTS.md Section 333 ATLAS

---

## Purpose

Apply formal logic to validate architectural arguments, detect contradictions, and construct rigorous proofs for design decisions.

**When to Use:**
- Validate architectural arguments
- Detect logical contradictions in design
- Prove correctness of approach
- Verify inference chains
- Challenge assumptions with formal logic
- Construct rigorous justifications
- Resolve conflicting requirements

---

## Reasoning Modes (5 Types)

### 1. Deductive Reasoning
**Form:** Premises → Necessary Conclusion

**Structure:**
```
Premise 1: All A are B
Premise 2: C is A
Conclusion: Therefore, C is B
```

**Validity Check:**
- If premises are true, conclusion MUST be true
- No new information in conclusion

**Example:**
```
P1: All microservices require service discovery
P2: Our system uses microservices
C: Therefore, our system requires service discovery

Validity: ✅ VALID (conclusion follows necessarily)
Soundness: Check if P1 and P2 are true
```

---

### 2. Inductive Reasoning
**Form:** Observations → Generalization

**Structure:**
```
Observation 1: Instance A has property X
Observation 2: Instance B has property X
Observation 3: Instance C has property X
Conclusion: All instances likely have property X
```

**Strength Assessment:**
- Sample size (more observations → stronger)
- Diversity (varied instances → stronger)
- Counterexamples (any found → weaker)

**Example:**
```
O1: Python service startup: 2.3s
O2: Python service startup: 2.1s
O3: Python service startup: 2.5s
C: Python services start in ~2-3s

Strength: 0.75 (moderate - small sample, consistent)
Confidence: 0.85 (Ω₀ = 0.041 - sample size limitation)
```

---

### 3. Abductive Reasoning
**Form:** Observation → Best Explanation

**Structure:**
```
Observation: Surprising fact F
Hypothesis H would explain F
No other hypothesis explains F as well
Conclusion: H is probably true
```

**Evaluation Criteria:**
- Explanatory power (how well does it explain?)
- Simplicity (Occam's Razor)
- Consistency with other knowledge
- Testability

**Example:**
```
Observation: API latency increased 300% after deployment
Hypothesis 1: Database connection pool exhausted
Hypothesis 2: Network issues
Hypothesis 3: Cosmic rays

Evaluation:
H1: High explanatory power, simple, testable → Best explanation
H2: Moderate power, but no network alerts → Less likely
H3: Low power, complex, untestable → Reject

Conclusion: Database connection pool exhaustion (confidence: 0.90)
```

---

### 4. Argument Validation
**Goal:** Check validity and soundness

**Validity Check:**
```
1. Identify premises and conclusion
2. Check logical form
3. Test: Can premises be true and conclusion false?
   - If NO → Valid
   - If YES → Invalid
```

**Soundness Check:**
```
1. Check validity (must be valid first)
2. Verify all premises are true
3. If valid AND all premises true → Sound
```

**Example:**
```
Argument: "We should use Redis because it's fast"

Formalized:
P1: Redis is fast (TRUE)
P2: We should use fast technologies (QUESTIONABLE)
C: We should use Redis

Validity: VALID (if P1 and P2 true, C follows)
Soundness: UNSOUND (P2 is oversimplified - ignores tradeoffs)

Improved Argument:
P1: Our system requires sub-10ms cache access
P2: Redis provides sub-5ms cache access
P3: Redis meets our operational constraints
C: Redis satisfies our caching requirements

Validity: VALID
Soundness: SOUND (if premises verified)
```

---

### 5. Contradiction Detection
**Goal:** Find logical inconsistencies

**Process:**
```
1. List all requirements/constraints
2. Formalize as logical statements
3. Check for contradictions:
   - Direct: A and ¬A
   - Derived: A→B, B→C, C→¬A
4. Resolve contradictions:
   - Prioritize requirements
   - Relax constraints
   - Find third option
```

**Example:**
```
Requirement 1: System must be strongly consistent
Requirement 2: System must have 99.999% availability
Requirement 3: System must tolerate network partitions

Contradiction: CAP Theorem
- Cannot have all three (Consistency, Availability, Partition Tolerance)

Resolution:
- Prioritize: Availability > Consistency (AP system)
- Use eventual consistency instead of strong consistency
- Document trade-off in architecture decision record
```

---

## Execution Steps

// turbo-all

### 1. Formalize the Argument
```
Convert natural language to logical form:
- Identify premises (given facts)
- Identify conclusion (what follows)
- Make implicit assumptions explicit
- Use clear logical connectives (AND, OR, IF-THEN, NOT)
```

### 2. Select Reasoning Mode
```
Choose based on goal:
- Prove correctness → Deductive
- Generalize from examples → Inductive
- Find best explanation → Abductive
- Check argument → Validation
- Find conflicts → Contradiction Detection
```

### 3. Apply Logical Analysis
```
Execute selected reasoning mode:
- Follow formal rules
- Show each step
- State confidence levels
- Note limitations
```

### 4. Validate Results
```
Check reasoning:
- Are premises true? (F1 Truth)
- Is logic valid? (Formal correctness)
- Are there counterexamples?
- What's the confidence? (F7 Humility)
```

### 5. Document Proof
```
Record in architectural decision records:
- Argument structure
- Logical form
- Validation results
- Confidence assessment
- Limitations noted
```

---

## Constitutional Floors

**Primary Floors:**
- **F1 (Truth ≥0.99):** Premises must be factually accurate
- **F2 (Clarity ΔS ≥0):** Clear logical structure
- **F10 (Ontology):** Symbolic mode - logic is tool, not reality

**Secondary Floors:**
- **F7 (Humility Ω₀ 0.03-0.05):** State confidence in conclusions
- **F8 (Audit):** Document proof steps

---

## Example Usage

**Scenario:** Validate architectural decision to use event sourcing

```
/reason "Prove that event sourcing enables time-travel debugging"

Reasoning Mode: Deductive

Formalized Argument:
P1: Event sourcing stores all state changes as immutable events
P2: Immutable events can be replayed in any order
P3: Replaying events to time T reconstructs state at time T
P4: Reconstructing past state enables debugging at that point
C: Therefore, event sourcing enables time-travel debugging

Validity Check:
- P1 → P2: ✅ (immutability enables replay)
- P2 → P3: ✅ (replay reconstructs state)
- P3 → P4: ✅ (past state enables debugging)
- P1,P2,P3,P4 → C: ✅ VALID

Soundness Check:
- P1: TRUE (definition of event sourcing)
- P2: TRUE (immutable events are replayable)
- P3: TRUE (deterministic replay)
- P4: TRUE (state access enables debugging)
Result: ✅ SOUND

Conclusion: SEAL (argument is valid and sound)
Confidence: 0.98
Ω₀ Humility: 0.038 (minor uncertainty in "any order" - may need causal ordering)

Limitation: Assumes deterministic event handlers
```

---

## Output Format

```markdown
## Logical Reasoning: [Argument/Question]

### Reasoning Mode
[Deductive / Inductive / Abductive / Validation / Contradiction]

### Formalized Argument
**Premises:**
- P1: [Statement] ([TRUE/FALSE/UNKNOWN])
- P2: [Statement] ([TRUE/FALSE/UNKNOWN])
- ...

**Conclusion:**
- C: [Statement]

### Logical Analysis
[Step-by-step reasoning with formal rules]

### Validity
[VALID / INVALID] - [Explanation]

### Soundness (if applicable)
[SOUND / UNSOUND] - [Explanation]

### Confidence Assessment
- Logical Validity: [0.00-1.00]
- Premise Truth: [0.00-1.00]
- Overall Confidence: [0.00-1.00]
- Ω₀ Humility: [0.03-0.05]

### Limitations
[Known limitations, assumptions, edge cases]

### Verdict
[SEAL / PARTIAL / VOID] - [Recommendation]
```

---

## Anti-Patterns (Violations)

❌ **Affirming the consequent** (If A→B and B, then A) - INVALID
❌ **Denying the antecedent** (If A→B and ¬A, then ¬B) - INVALID
❌ **Circular reasoning** (Conclusion assumes premise) - INVALID
❌ **False dichotomy** (Only two options when more exist) - INVALID
❌ **Hasty generalization** (Insufficient inductive evidence) - WEAK
❌ **Unverified premises** (Violates F1 Truth)
❌ **Hidden assumptions** (Violates F2 Clarity)

---

## Common Logical Forms

### Modus Ponens (VALID)
```
If A then B
A is true
Therefore, B is true
```

### Modus Tollens (VALID)
```
If A then B
B is false
Therefore, A is false
```

### Hypothetical Syllogism (VALID)
```
If A then B
If B then C
Therefore, if A then C
```

### Disjunctive Syllogism (VALID)
```
A or B
Not A
Therefore, B
```

### Reductio ad Absurdum (VALID)
```
Assume A
A leads to contradiction
Therefore, not A
```

---

## Integration with Other Workflows

**After `/think`:**
```
/think → Generate options → /reason → Validate logic of each option
```

**Before `/plan`:**
```
/reason → Prove approach is sound → /plan → Design with validated logic
```

**With `/search`:**
```
/search → Gather premises → /reason → Construct proof from facts
```

**During `/review`:**
```
/review → Check Engineer's logic → /reason → Validate implementation reasoning
```

---

## Proof Construction Template

```markdown
**Theorem:** [What we want to prove]

**Given:**
- [Premise 1]
- [Premise 2]
- ...

**To Prove:** [Conclusion]

**Proof:**
1. [Step 1] (from [premise/previous step])
2. [Step 2] (from [premise/previous step])
3. ...
n. [Conclusion] (QED)

**Confidence:** [0.00-1.00]
**Ω₀ Humility:** [0.03-0.05]
```

---

**DITEMPA BUKAN DIBERI** - Architectural correctness is proven through logic, not assumed.

**Version:** v47.0
**Status:** ACTIVE
**Territory:** AGI (Δ Delta - Architect)
