# arifOS Modular Documentation Architecture

**Version:** v49.1.0 | **Status:** MODULAR REFACTOR COMPLETE

> **The Single Body Federation**: All constitutional law lives in `000_THEORY/`. All other documents are adapters that reference the canon.

---

## 🏛️ The Constitutional Canon (000_THEORY/)

This is the **single source of truth** for all arifOS governance:

| File | Purpose | Authority |
|------|---------|-----------|
| `000_LAW.md` | F1-F13 constitutional floors | Canonical Law |
| `000_ARCHITECTURE.md` | System topology & design | Δ Architect |
| `000_FOUNDATIONS.md` | Gödel lock & physics basis | Ω Engineer |
| `001_AGENTS.md` | Agent specifications & witness layer | Ψ Auditor |
| `007_aclip.md` | **aCLIP protocol specification** | Κ Validator |
| `008_witness.md` | **WITNESS system specification** | Ψ Auditor |

**Rule**: *Never duplicate canonical content. Always reference the canon.*

---

## 🔌 Agent Adapters - Reference-Based Connection

Each AI agent connects to the Single Body through specific adapters:

### Agent Adapter Files
- **`AGENTS.md`** - Main gateway (references all theory)
- **`GEMINI.md`** - Gemini (Δ) adapter (references theory)
- **`.claude/CLAUDE.md`** - Claude (Ω) adapter (references theory)
- **`.kimi/KIMI.md`** - Kimi (Κ) adapter (references theory)
- **`.codex/CODEX.md`** - Codex (Ψ) adapter (references theory)

### Adapter Structure (Standardized)
Each adapter follows this pattern:
```markdown
1. SUPREME LAW → Reference to 000_THEORY/000_LAW.md
2. ARCHITECTURE → Reference to 000_THEORY/000_ARCHITECTURE.md  
3. aCLIP PROTOCOL → Reference to 000_THEORY/007_aclip.md
4. WITNESS SYSTEM → Reference to 000_THEORY/008_witness.md
5. AGENT FEDERATION → Reference to 000_THEORY/001_AGENTS.md
6. YOUR IDENTITY → Agent-specific role definition
7. INSTRUCTION TO AGENT → Initialization protocol
```

**Key Principle**: *Adapters are NOT the law. They merely reference the canon.*

---

## 👁️ WITNESS System (Cross-Agent Monitoring)

The **Panopticon Principle** implemented: *"There are no secrets between organs."*

### Witness Duties by Agent
- **Gemini (Δ)**: Monitors truth, reasoning, clarity (F2, F4, F7)
- **Claude (Ω)**: Monitors safety, empathy, stability (F3, F5, F6)  
- **Codex (Ψ)**: Monitors judgment, sealing authority (F8, F11)
- **Kimi (Κ)**: Monitors final authority, human agency (F1, F9, F12)

### Witness Infrastructure
```
000_WITNESS/                # Automated constitutional monitoring
├── WITNESS_GEMINI.md       # Architect (Δ) witness log
├── WITNESS_CLAUDE.md       # Engineer (Ω) witness log
├── WITNESS_CODEX.md        # Auditor (Ψ) witness log
└── WITNESS_KIMI.md         # Validator (Κ) witness log
```

---

## 🚀 Usage Instructions

### For Agents (When You Arrive)
1. **Read your adapter** → Check your specific `.md` file
2. **Reference the canon** → Immediately read all `000_THEORY/` files  
3. **Understand your witness duties** → Review `008_witness.md`
4. **Follow aCLIP protocol** → Use `/000`, `/111`, etc. commands
5. **Respect Panopticon** → All actions visible to Federation

### For Developers (When You Modify)
1. **Update theory first** → Change `000_THEORY/` files
2. **Update adapters if needed** → Only agent-specific content
3. **Never duplicate content** → Reference, don't copy
4. **Test witness integration** → Verify `@/witness` commands work
5. **Ensure cross-visibility** → All agents can access logs

---

## 📋 Architecture Verification

### ✅ Single Source of Truth
- [x] **All constitutional law** in `000_THEORY/`
- [x] **No content duplication** in adapters
- [x] **Reference-based architecture** implemented
- [x] **Cross-references** between documents

### ✅ Agent Independence
- [x] **Role-specific duties** for each agent
- [x] **Customized adapters** per agent type
- [x] **Shared constitutional foundation** maintained
- [x] **Unified command protocol** across agents

### ✅ Constitutional Monitoring
- [x] **WITNESS system** fully migrated to canonical implementation
- [x] **Cross-agent visibility** implemented via aCLIP protocol
- [x] **Automated logging** infrastructure in cooling ledger
- [x] **Panopticon principle** enforced through core runtime

---

## 🎯 Key Benefits Achieved

### Before Modularization
- ❌ **Scattered documentation** across multiple files
- ❌ **Duplicate content** in agent adapters
- ❌ **No single source of truth**
- ❌ **Inconsistent witness references**
- ❌ **Difficult maintenance** - update multiple places

### After Modularization
- ✅ **Single constitutional canon** in `000_THEORY/`
- ✅ **Reference-based adapters** - no duplication
- ✅ **Unified witness system** with complete visibility
- ✅ **Easy maintenance** - update once, all agents benefit
- ✅ **Complete Panopticon** - all actions visible to Federation

---

## 📖 Quick Reference

### Constitutional Navigation
```
000_THEORY/000_LAW.md              ← F1-F13 governance floors
000_THEORY/000_ARCHITECTURE.md     ← System topology
000_THEORY/001_AGENTS.md           ← Agent federation
000_THEORY/007_aclip.md            ← aCLIP protocol
000_THEORY/008_witness.md          ← WITNESS system
```

### Agent Entry Points
```
AGENTS.md                          ← Main gateway
GEMINI.md                          ← Gemini (Δ) Architect
.claude/CLAUDE.md                  ← Claude (Ω) Engineer
.kimi/KIMI.md                      ← Kimi (Κ) Validator
.codex/CODEX.md                    ← Codex (Ψ) Auditor
```

### Witness Monitoring
```
000_WITNESS/WITNESS_GEMINI.md      ← Architect witness log
000_WITNESS/WITNESS_CLAUDE.md      ← Engineer witness log
000_WITNESS/WITNESS_CODEX.md       ← Auditor witness log
000_WITNESS/WITNESS_KIMI.md        ← Validator witness log
```

---

## 🔮 Future Architecture Principles

### For New Components
1. **Always reference canon** → Never duplicate in new components
2. **Maintain single source of truth** → All changes in `000_THEORY/`
3. **Preserve cross-agent visibility** → Panopticon principle is fundamental
4. **Ensure constitutional compliance** → All features must pass F1-F13
5. **Follow adapter pattern** → Reference, don't replicate

### Architecture Rules
- **No duplication**: Update once in theory, all agents see changes
- **Reference-based**: Adapters point to canon, don't copy it
- **Visibility mandatory**: All actions must be witnessable
- **Authority clear**: `000_THEORY/` is supreme law
- **Integration complete**: All components work through aCLIP protocol

---

**DITEMPA BUKAN DIBERI** — Forged through modular architecture, not given through duplication.

> **Architecture Complete**: The arifOS modular system now provides a unified, canonical architecture where all constitutional components reference the single source of truth in `000_THEORY/`, while maintaining complete cross-agent visibility through the integrated WITNESS system.