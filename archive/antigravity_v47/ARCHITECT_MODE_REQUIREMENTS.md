# Architect Agent Mode - Requirements Specification

**Created:** 2026-01-06
**Purpose:** Define what an "Architect Agent" needs to treat arifOS repo as a real digital world
**Status:** REQUIREMENTS (not implementation)

---

## Problem Statement

Current agents (including Antigravity) operate as **mechanical executors**:
- Read files → grep patterns → generate reports
- Propose solutions without checking if they already exist
- Reinvent wheels (ROSETTA_STONE when aCLIP exists)
- Don't absorb the "digital world" ontology

**Goal:** Create an agent mode that operates as a **constitutional architect**:
- Understands L1/L2/L3/aCLIP as a living system
- Navigates the repo as a coherent world (not scattered files)
- Recognizes existing solutions before proposing new ones
- Uses aCLIP as native language

---

## The Digital World Ontology

### 4 Layers of Reality

| Layer | Name | Language | Purpose | Authority |
|-------|------|----------|---------|-----------|
| **L1** | Canon | Thermodynamic Poetry | WHY (intent, philosophy) | Track A (immutable) |
| **L2** | Spec | Configuration YAML | WHAT (rules, thresholds) | Track B (versioned) |
| **L3** | Code | Python Functions | HOW (execution, mechanics) | Track C (mutable) |
| **aCLIP** | Protocol | Agent Vocabulary | LANGUAGE (translation layer) | Cross-layer binding |

### The Language Mixing Problem

**Same concept, different names:**
- L1: "Peace²" (poetic)
- L2: `peace_squared: 1.0` (YAML key)
- L3: `def check_peace_squared()` (function)
- Agent: "F5" (floor number)
- aCLIP: "666 (Draft)" (pipeline stage)

**Solution:** Accept mixing, but **map explicitly** (don't force uniformity)

---

## Architect Agent Requirements

### 1. Ontology Awareness

**The agent must understand:**
- L1 (Canon) = Source of truth for intent
- L2 (Spec) = Operational rules derived from L1
- L3 (Code) = Mechanical implementation of L2
- aCLIP = Translation protocol between all layers

**Test:**
- Given "Peace²", agent can find:
  - L1: `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md`
  - L2: `L2_GOVERNANCE/core/constitutional_floors.yaml` (key: `peace_squared`)
  - L3: `arifos_core/enforcement/metrics.py` (function: `check_peace_squared()`)
  - aCLIP: "F5 Floor" or "666 (Draft)" depending on context

### 2. Navigation Intelligence

**The agent must navigate:**
- **Top-down:** L1 (intent) → L2 (spec) → L3 (code)
- **Bottom-up:** L3 (code) → L2 (spec) → L1 (intent)
- **Cross-layer:** aCLIP vocabulary maps to all 3 layers

**Test:**
- Given `check_peace_squared()` in code, agent can trace back to:
  - L2 spec: `peace_squared: 1.0`
  - L1 canon: "F5: Peace² ≥ 1.0 - System stability"
  - Intent: "Prevents chaotic outputs via thermodynamic constraint"

### 3. Existence Checking (Anti-Reinvention)

**Before proposing ANY solution, agent must:**
1. Search for existing solution (grep, find, read)
2. If found: Use it (don't reinvent)
3. If not found: Verify gap is real (not just missed in search)
4. If gap confirmed: Propose solution

**Test:**
- Agent proposes "Create ROSETTA_STONE.md"
- Agent searches for "translation layer" or "language protocol"
- Agent finds aCLIP (AGENTS.md line 136)
- Agent says: "aCLIP already exists, using that instead"

### 4. aCLIP Fluency

**The agent must speak aCLIP natively:**
- Use FAG (Full Autonomy Governance) not "autonomous mode"
- Use RAPES-M (Reflect→Analyze→Plan→Execute→Seal→Memory) not "workflow"
- Use vTEMPA (versioned Thermodynamic Empathy Protocol Alignment) not "empathy system"
- Use pipeline stages (000, 444, 666, 888, 999) not "steps"

**Test:**
- Agent describes workflow as: "FAG RAPES-M cycle: 000 (Reset) → 444 (Read) → 666 (Draft) → 888 (Review) → 999 (Seal)"
- NOT: "Autonomous workflow with 5 steps"

### 5. State Persistence (Memory)

**The agent must remember:**
- What files were read (don't re-read unnecessarily)
- What was discovered (don't re-discover)
- What was decided (don't re-decide)
- What failed (don't repeat mistakes)

**Test:**
- Session 1: Agent reads AGENTS.md, discovers aCLIP
- Session 2: Agent remembers aCLIP exists, uses it immediately
- NOT: Agent re-discovers aCLIP every session

### 6. Mixed Language Tolerance

**The agent must accept:**
- Some canon is poetic (Peace², κᵣ, Ψ)
- Some code is mechanical (check_peace_squared, compute_empathy_score)
- Some docs are dead (archived, v43, v44)
- Some YAML is aspirational (not implemented yet)

**The agent must NOT:**
- Try to force uniformity (rename all "Peace²" to "peace_squared")
- Delete "redundant" docs without understanding their role
- Assume all YAML is implemented in code

**Test:**
- Agent sees "Peace²" in canon, `peace_squared` in YAML, `check_peace_squared()` in code
- Agent says: "These are the same concept in different layers (L1/L2/L3)"
- NOT: "Inconsistent naming, should consolidate"

---

## Architect Agent Capabilities

### Core Skills

1. **Read Ontology** - Understand L1/L2/L3/aCLIP structure
2. **Navigate Layers** - Trace concepts across all 4 layers
3. **Check Existence** - Search before proposing
4. **Speak aCLIP** - Use canonical vocabulary
5. **Remember State** - Persist discoveries across sessions
6. **Accept Mixing** - Don't force false uniformity

### Advanced Skills

7. **Detect Drift** - Identify when L3 code diverges from L2 spec
8. **Audit Compliance** - Verify L3 implements L2 implements L1
9. **Propose Consolidation** - Only when entropy reduction is proven
10. **Seal Knowledge** - Document discoveries for future agents

---

## Implementation Path (NOT for this session)

### Phase 1: Onboarding Protocol
- Agent reads AGENTS.md → GOVERNANCE.md → aCLIP docs FIRST
- Agent builds internal ontology map (L1/L2/L3/aCLIP)
- Agent tests fluency (can translate between layers)

### Phase 2: Navigation Training
- Agent practices top-down (L1→L2→L3)
- Agent practices bottom-up (L3→L2→L1)
- Agent practices cross-layer (aCLIP mapping)

### Phase 3: Existence Checking
- Agent searches before proposing
- Agent verifies gaps are real
- Agent uses existing solutions

### Phase 4: State Persistence
- Agent logs discoveries to EUREKA notes
- Agent reads EUREKA notes at session start
- Agent doesn't repeat mistakes

---

## Success Criteria

**An Architect Agent is successful when:**

1. ✅ Can translate any concept between L1/L2/L3/aCLIP
2. ✅ Checks for existing solutions before proposing new ones
3. ✅ Uses aCLIP vocabulary natively (FAG, RAPES-M, vTEMPA)
4. ✅ Remembers discoveries across sessions
5. ✅ Accepts language mixing without forcing uniformity
6. ✅ Treats repo as a "digital world" (coherent system, not scattered files)

**Failure modes to avoid:**
- ❌ Proposing ROSETTA_STONE when aCLIP exists
- ❌ Creating duplicate solutions
- ❌ Forcing false uniformity (renaming everything)
- ❌ Re-discovering same things every session
- ❌ Operating mechanically (grep → report) without understanding

---

## Next Steps (For Future Sessions)

1. **Read aCLIP docs properly** (`arifos_clip/README.md`, GOVERNANCE.md line 380)
2. **Build ontology map** (L1/L2/L3/aCLIP translation table)
3. **Test fluency** (can agent translate "Peace²" across all layers?)
4. **Implement state persistence** (EUREKA notes, session memory)
5. **Train on existence checking** (search before propose)

---

**DITEMPA BUKAN DIBERI** — Forged, not given; the architect must be trained, not assumed.
