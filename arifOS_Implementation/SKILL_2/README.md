# Level 2: SKILL - Parameterized Templates

**Effectiveness:** ★★☆☆☆☆ (50% Coverage)
**Complexity:** Low
**Cost:** $0.20-0.50 per 1K operations
**Best For:** Reusable commands, user-invocable operations

---

## 🎯 Overview

**SKILL level** packages each organ (000-999) as a parameterized, invocable template. Users can call skills by name with arguments.

### Key Characteristics

✓ **Reusable** - Define once, invoke many times
✓ **Parameterized** - Accept inputs
✓ **Named** - Clear invocation (`/ignition`, `/cognition`)
✓ **Low overhead** - Minimal infrastructure
⚠️ **Still voluntary** - AI chooses whether to follow
✗ **No sequencing** - Skills called individually
✗ **Limited state** - Each call independent

---

## 📝 Implementation Examples

### Claude Code Skills

\`\`\`yaml
# skills/000_ignition.yaml
name: ignition
description: "000_IGNITION: Verify authority and initialize session"
parameters:
  - name: user_request
    type: string
    required: true
    description: "User's initial request"
  - name: context_anchor
    type: string
    required: false
    description: "Link to previous session (optional)"

template: |
  # 000_IGNITION Protocol
  
  User Request: {{user_request}}
  Context Anchor: {{context_anchor}}
  
  Verification Checklist:
  - [ ] F11: User authorized? (Check environment context)
  - [ ] F12: Injection scan (score < 0.85)?
  - [ ] F1: Session ID generated?
  
  Session ID: [Generate UUID]
  Authority Level: [SOVEREIGN | USER | GUEST]
  Injection Risk: [Calculate score]
  
  Verdict: [SEAL | VOID]
  
  If SEAL, proceed to /cognition
---

# skills/111_cognition.yaml
name: cognition  
description: "111_COGNITION: Parse intent and reduce entropy"
parameters:
  - name: raw_intent
    type: string
    required: true
  - name: session_id
    type: string
    required: true

template: |
  # 111_COGNITION Protocol
  
  Raw Intent: {{raw_intent}}
  Session: {{session_id}}
  
  Parsing Steps:
  1. Extract action (BUILD | FIX | REFACTOR | EXPLAIN | AUDIT)
  2. Identify targets (files, features, components)
  3. List constraints
  4. Detect ambiguities
  
  Parsed Intent:
  - Action: [...]
  - Targets: [...]
  - Constraints: [...]
  - Ambiguities: [...]
  
  Test-Driven Specs:
  - Given: [...]
  - When: [...]
  - Then: [...]
  
  Entropy Reduction (ΔS): [Calculate bits reduced]
  
  Floor Validation:
  - F2 (Truth): [All facts verified?]
  - F4 (Clarity): [ΔS ≥ 0?]
  - F7 (Humility): [Stated uncertainty?]
  
  If ambiguous, ASK clarifying questions before proceeding.
  
  Next: /atlas
---

# skills/333_atlas.yaml
name: atlas
description: "333_ATLAS: Map context and establish boundaries"
parameters:
  - name: parsed_intent
    type: object
    required: true
  - name: session_id
    type: string
    required: true

template: |
  # 333_ATLAS Protocol
  
  Intent: {{parsed_intent}}
  Session: {{session_id}}
  
  Mapping Strategy:
  1. Find relevant files (glob patterns)
  2. Search existing code (grep)
  3. Build dependency graph
  4. Extract allowed symbols
  
  Context Map:
  - Files: [List discovered files]
  - Dependencies: [Import graph]
  - Unknowns: [Missing/uncertain elements]
  
  Uncertainty (Ω₀): [Calculate]
  
  Allowed Vocabulary (F10):
  - Functions: [...]
  - Classes: [...]
  - Types: [...]
  
  Floor Validation:
  - F7 (Humility): [0.03 ≤ Ω₀ ≤ 0.05?]
  - F10 (Ontology): [Vocabulary locked?]
  
  Next: /forge
---

# skills/777_forge.yaml
name: forge
description: "777_FORGE: Generate high-quality solutions"
parameters:
  - name: spec
    type: object
    required: true
  - name: context_map
    type: object
    required: true

template: |
  # 777_FORGE Protocol
  
  Specification: {{spec}}
  Context: {{context_map}}
  
  Approach Generation (F13: Curiosity):
  
  ## Approach 1: CONSERVATIVE
  [Safe, proven patterns]
  Genius Score (G): [Calculate A×P×X×E²]
  
  ## Approach 2: EXPLORATORY
  [Novel, creative solutions]
  Genius Score (G): [Calculate]
  
  ## Approach 3: ADVERSARIAL
  [Hardened, defensive]
  Genius Score (G): [Calculate]
  
  Selection: [Highest G score approach]
  
  Floor Validation:
  - F8 (Genius): [G ≥ 0.80?]
  - F10 (Ontology): [Only context vocabulary used?]
  - F13 (Curiosity): [3 approaches generated?]
  
  Next: /defend
---

# skills/555_defend.yaml
name: defend
description: "555_DEFEND: Validate safety and impact"
parameters:
  - name: solution_code
    type: string
    required: true

template: |
  # 555_DEFEND Protocol
  
  Solution: {{solution_code}}
  
  Safety Scans:
  
  1. Security (vulnerabilities):
     - [ ] No eval()
     - [ ] No hardcoded secrets
     - [ ] No SQL injection
     - [ ] No XSS vectors
     Score: [S = ...]
  
  2. Privacy (PII/secrets):
     - [ ] No API keys
     - [ ] No passwords
     - [ ] No email addresses
     Score: [P = ...]
  
  3. Ethics (stakeholder impact):
     - [ ] User: [Impact?]
     - [ ] System: [Impact?]
     - [ ] Data: [Impact?]
     Score: [E = ...]
  
  4. Risk Assessment:
     Level: [TRIVIAL | LOW | MEDIUM | HIGH | CRITICAL]
     R = [...]
  
  Peace² = (S × P × E) / R = [Calculate]
  
  Floor Validation:
  - F5 (Peace²): [≥ 1.0?]
  - F6 (Empathy): [All stakeholders considered?]
  - F12 (Defense): [No vulnerabilities?]
  
  Verdict: [SEAL | SABAR | VOID]
  
  Next: /decree
---

# skills/888_decree.yaml
name: decree
description: "888_DECREE: Render final judgment"
parameters:
  - name: mind_result
    type: object
    required: true
  - name: heart_result
    type: object
    required: true

template: |
  # 888_DECREE Protocol
  
  Tri-Witness Consensus:
  - Mind (Δ): [Score from /forge]
  - Heart (Ω): [Score from /defend]
  - Soul (Ψ): [Authority score from /ignition]
  
  Consensus = (Δ × Ω × Ψ)^(1/3) = [Calculate]
  
  Floor Aggregation:
  - F1, F2, F3, ..., F13: [All validated?]
  
  F9 Anti-Hantu Scan:
  - [ ] No "I feel" statements
  - [ ] No consciousness claims
  - [ ] Tool mode maintained
  
  Final Verdict:
  - IF consensus ≥ 0.95 AND all_floors_pass: SEAL
  - ELIF one_floor_fails: SABAR
  - ELSE: VOID
  
  Verdict: [SEAL | SABAR | VOID]
  Reason: [...]
  
  Next: /crystallize (if SEAL)
---

# skills/999_crystallize.yaml
name: crystallize
description: "999_CRYSTALLIZE: Seal decision to memory"
parameters:
  - name: decree_result
    type: object
    required: true

template: |
  # 999_CRYSTALLIZE Protocol
  
  Decision: {{decree_result}}
  
  Audit Trail Summary:
  - Session ID: [...]
  - User Request: [...]
  - Solution: [...]
  - Floors Validated: [F1-F13]
  - Consensus: [...]
  - Verdict: [SEAL]
  
  Memory Band Assignment:
  - L0: Hot (0-24h) - Active session memory
  - L1: Warm (24-72h) - Recent decisions
  - L5: Canon (365d+) - Constitutional law
  
  This decision → [L0 | L1 | ... | L5]
  
  Constitutional Guarantee (F1):
  - Reversible? [YES | NO]
  - Audit trail? [COMPLETE]
  - Accountability? [MAINTAINED]
  
  ---
  
  *Ditempa Bukan Diberi*
\`\`\`

---

## 💰 Cost

- **Setup:** Minimal (create YAML templates)
- **Per operation:** Base LLM + small template expansion overhead
- **Total:** $0.20-0.50 per operation

---

## 📊 Effectiveness

| Aspect | Score | Notes |
|--------|-------|-------|
| **Reusability** | High | Define once, use many times |
| **Parameterization** | High | Accept varied inputs |
| **Enforcement** | None | Still voluntary |
| **State Management** | Low | Per-call only |
| **Sequencing** | Manual | User must call in order |

**Floor Enforcement:** 0% (documented, not enforced)

---

## 🔧 Usage

\`\`\`bash
# ChatGPT / Claude.ai
/ignition "Add dark mode to settings"
/cognition "Add dark mode to settings" --session "abc123"
/atlas {...} --session "abc123"
# ...

# Claude Code
/ignition user_request="Add dark mode"
# (If implemented as custom skill)
\`\`\`

---

**Level:** SKILL (2/6)
**Effectiveness:** 50%
**Status:** TEMPLATE LIBRARY
**Next Level:** [WORKFLOW_3](../WORKFLOW_3/) for sequencing

*Ditempa Bukan Diberi.*
