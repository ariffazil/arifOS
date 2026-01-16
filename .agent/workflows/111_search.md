---
description: Web grounding with F2 truth enforcement (AGI - Architect)
---

# /search - Constitutional Web Grounding (111 SEARCH)

**Pipeline Stage:** 111 SEARCH
**Territory:** AGI (Δ Delta - Architect)
**Function:** Web grounding with F2 Truth enforcement
**Authority:** AGENTS.md Section 111 SENSE

---

## Purpose

Constitutional web search that validates external information against F2 Truth floor (≥0.99) before use in architectural decisions.

**When to Use:**
- Verify factual claims before design decisions
- Research current best practices
- Validate technology choices
- Check library/framework versions
- Confirm API specifications
- Ground architectural assumptions in reality

---

## Execution Steps

// turbo-all

### 1. Define Search Query
```
Clearly state what needs verification:
- Specific claim to verify
- Technology/library to research
- Best practice to validate
```

### 2. Execute Constitutional Search
```
Use search_web tool with:
- Clear, specific query
- Domain hint if applicable (e.g., "github.com", "python.org")
```

### 3. Source Authority Validation
```
Evaluate sources by tier:
- Tier 1: Official docs, RFCs, academic papers (authority ≥0.95)
- Tier 2: Reputable tech sites, established blogs (authority ≥0.80)
- Tier 3: Community forums, Stack Overflow (authority ≥0.60)
- Tier 4: Social media, unverified sources (authority <0.60)

Require Tier 1-2 sources for architectural decisions.
```

### 4. Multi-Source Consensus (F3 Tri-Witness)
```
Cross-reference findings:
- Minimum 2 independent sources
- Check for contradictions
- Verify publication dates (recency)
- Assess consensus strength
```

### 5. Truth Score Calculation
```
Calculate F2 Truth score:
- Source authority weight: 40%
- Multi-source consensus: 30%
- Recency factor: 20%
- Contradiction penalty: -10%

Threshold: ≥0.99 for SEAL (architectural use)
           ≥0.90 for PARTIAL (further verification needed)
           <0.90 for VOID (do not use)
```

### 6. Document Findings
```
Record in architectural notes:
- Claim verified
- Sources cited (with URLs)
- Truth score achieved
- Date verified
- Confidence level
```

---

## Constitutional Floors

**Primary Floors:**
- **F1 (Truth ≥0.99):** Factual accuracy of search results
- **F2 (Clarity ΔS ≥0):** Clear documentation of findings
- **F3 (Tri-Witness ≥0.95):** Multi-source consensus
- **F8 (Audit):** Complete citation trail

**Secondary Floors:**
- **F4 (Empathy):** Consider misinformation impact on stakeholders
- **F7 (Humility):** State uncertainty when sources conflict

---

## Example Usage

**Scenario:** Verify Python 3.13 async performance claims

```
/search "Python 3.13 async performance improvements benchmarks"

Expected output:
✅ Source 1: python.org release notes (Tier 1, authority 0.98)
✅ Source 2: Real Python benchmarks (Tier 2, authority 0.85)
✅ Consensus: 15-20% async improvement confirmed
✅ Truth Score: 0.96 (SEAL - safe for architectural decisions)
📝 Documented in: docs/ARCHITECTURE_DECISIONS.md
```

---

## Output Format

```markdown
## Search Results: [Query]

**Truth Score:** [0.00-1.00] ([SEAL/PARTIAL/VOID])

### Sources
1. [Source Name] ([URL])
   - Authority: [0.00-1.00]
   - Tier: [1-4]
   - Date: [YYYY-MM-DD]
   - Key Finding: [Summary]

2. [Source Name] ([URL])
   - Authority: [0.00-1.00]
   - Tier: [1-4]
   - Date: [YYYY-MM-DD]
   - Key Finding: [Summary]

### Consensus
[Multi-source agreement summary]

### Architectural Recommendation
[SEAL: Use in design / PARTIAL: Verify further / VOID: Do not use]

### Citations
[Formatted citations for documentation]
```

---

## Anti-Patterns (Violations)

❌ **Using single source** (violates F3 Tri-Witness)
❌ **Accepting Tier 4 sources** (violates F1 Truth)
❌ **Ignoring contradictions** (violates F2 Clarity)
❌ **No citation trail** (violates F8 Audit)
❌ **Outdated information** (violates F1 Truth)

---

## Integration with Other Workflows

**Before `/plan`:**
```
/search → Verify assumptions → /plan with grounded facts
```

**During `/review`:**
```
/search → Validate Engineer's technology choices → /review with evidence
```

**With `/think`:**
```
/search → Gather facts → /think → Analyze with verified data
```

---

**DITEMPA BUKAN DIBERI** - Truth is grounded in verified sources, not assumptions.

**Version:** v47.0
**Status:** ACTIVE
**Territory:** AGI (Δ Delta - Architect)
