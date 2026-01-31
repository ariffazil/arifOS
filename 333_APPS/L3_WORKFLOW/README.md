# L3_WORKFLOW — Documented Sequences

**Level 3 | 70% Coverage | Medium Complexity**

> *"Workflows are skills with state — file persistence across sessions."*

---

## 🎯 Purpose

L3_WORKFLOW adds **state persistence** to the parameterized skills from L2. Workflows are documented sequences that can:
- Save intermediate results to files
- Resume from checkpoints
- Maintain context across sessions
- Follow structured SOPs (Standard Operating Procedures)

This layer is the **team collaboration** layer — enabling shared, repeatable processes.

---

## 📈 Effectiveness Spectrum

```
Coverage:  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ 70%
Cost:      $0.50-1.00 per 1K operations
Setup:     1 hour
Autonomy:  Low (human-guided)
```

---

## 📁 Files in This Directory

### Current
| File | Description | Status |
|------|-------------|--------|
| `README.md` | This file | ✅ Complete |

### ✅ Now Available
| File | Description | Status |
|------|-------------|--------|
| `.claude/workflows/000_SESSION_INIT.md` | Session initialization (Stage 000) | ✅ Complete |
| `.claude/workflows/111_INTENT.md` | Intent mapping (Stage 111) | ✅ Complete |
| `.claude/workflows/333_CONTEXT.md` | Context gathering (Stage 333) | ✅ Complete |
| `.claude/workflows/555_SAFETY.md` | Safety evaluation (Stage 555) | ✅ Complete |
| `.claude/workflows/777_IMPLEMENT.md` | Implementation (Stage 777) | ✅ Complete |
| `.claude/workflows/888_COMMIT.md` | Commit/SEAL (Stage 888) | ✅ Complete |

---

## 🔄 The 6 Canonical Workflows

Each workflow maps to a stage in the 000-999 metabolic loop:

```
000_SESSION_INIT → 111_INTENT → 333_CONTEXT → 555_SAFETY → 777_IMPLEMENT → 888_COMMIT
```

### 000_SESSION_INIT.md
**Purpose:** Initialize constitutional session  
**Inputs:** User query, optional context  
**Outputs:** Session ID, loaded floors, authority verification  
**State Saved:** `sessions/{session_id}/000_init.json`

### 111_INTENT.md
**Purpose:** Map user intent to constitutional lanes  
**Inputs:** Natural language query  
**Outputs:** Intent classification, lane assignment (HARD/SOFT/PHATIC)  
**State Saved:** `sessions/{session_id}/111_intent.json`

### 333_CONTEXT.md
**Purpose:** Gather relevant context  
**Inputs:** Intent, codebase structure  
**Outputs:** Context map, relevant files  
**State Saved:** `sessions/{session_id}/333_context.json`

### 555_SAFETY.md
**Purpose:** Evaluate safety and empathy  
**Inputs:** Proposed action  
**Outputs:** Safety report, weakest stakeholder, empathy score  
**State Saved:** `sessions/{session_id}/555_safety.json`

### 777_IMPLEMENT.md
**Purpose:** Execute implementation  
**Inputs:** Safety-approved plan  
**Outputs:** Code changes, documentation  
**State Saved:** `sessions/{session_id}/777_implement.json`

### 888_COMMIT.md
**Purpose:** Final verification and SEAL  
**Inputs:** Implementation results  
**Outputs:** SEAL verdict, vault entry, merkle root  
**State Saved:** `sessions/{session_id}/888_commit.json`

---

## 🛡️ Constitutional Floors Enforced

| Floor | Enforcement | Mechanism | Status |
|-------|-------------|-----------|--------|
| F1 Amanah | ✅ Full | File persistence + audit | **Active** |
| F2 Truth | ✅ Full | Checkpoint validation | **Active** |
| F3 Tri-Witness | ⚠️ Partial | Human checkpoint | Available |
| F4 Clarity | ✅ Full | Documented steps | **Active** |
| F5 Peace² | ✅ Full | Safety workflow | **Active** |
| F6 Empathy | ✅ Full | Stakeholder workflow | **Active** |
| F7 Humility | ✅ Full | Uncertainty tracking | **Active** |
| F8 Genius | ⚠️ Partial | Score calculation | Available |
| F9 Anti-Hantu | ✅ Full | Pattern detection | **Active** |
| F10 Ontology | ✅ Full | Reality checks | **Active** |
| F11 Command Auth | ✅ Full | Token validation | **Active** |
| F12 Injection | ✅ Full | Input workflow | **Active** |
| F13 Sovereign | ✅ Full | Human checkpoints | **Active** |

---

## 🚀 Deployment History

### v52.0 — Workflow Experiments (Archived)
- Basic markdown workflows
- Manual state management
- Single-user only

### v53.0 — Standardization (Archived)
- `.claude/workflows/` structure
- 3 initial workflows
- File persistence added

### v54.1-SEAL — Current
- 6-workflow architecture defined
- State management framework
- ✅ **All 6 workflow files implemented**

---

## 📊 Use Cases

| Scenario | Workflow | Benefit |
|----------|----------|---------|
| Onboard new team member | `000_SESSION_INIT` + `111_INTENT` | Consistent process |
| Code review | `555_SAFETY` + `777_IMPLEMENT` | Safety-first |
| Architecture decision | `333_CONTEXT` + `888_COMMIT` | Documented rationale |
| Incident response | `000_SESSION_INIT` → `888_COMMIT` | Full traceability |

---

## 🔗 Next Steps

### Immediate (v55.0)
- [ ] Create `.claude/workflows/` directory
- [ ] Implement 6 canonical workflow files
- [ ] Add state persistence layer
- [ ] Test resume-from-checkpoint

### Future (v55.1+)
- [ ] Visual workflow editor
- [ ] Workflow marketplace
- [ ] Cross-team sharing

---

## 👑 Authority

**Sovereign:** Muhammad Arif bin Fazil  
**Version:** v54.1-SEAL  
**Status:** ⚠️ Partial — Implementation needed  
**Creed:** DITEMPA BUKAN DIBERI
