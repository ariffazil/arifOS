# arifOS Modular Documentation Architecture

**Version:** v49.1.0 | **Status:** MODULAR REFACTOR COMPLETE

> **Single Source of Truth Principle**: All constitutional law lives in `000_THEORY/`. All other documents are adapters that reference the canon.

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

**Rule**: *Never duplicate canonical content. Always reference the canon.*

---

## 🔌 Agent Adapters (Connection Strings)

Each AI agent connects to the Single Body through specific adapters:

### Agent Adapter Files
- **`GEMINI.md`** - Gemini (Δ Architect) adapter
- **`.claude/CLAUDE.md`** - Claude (Ω Engineer) adapter  
- **`.kimi/KIMI.md`** - Kimi (Κ Validator) adapter
- **`.codex/CODEX.md`** - Codex (Ψ Auditor) adapter

### Adapter Structure (Standardized)
Each adapter follows this pattern:
```markdown
1. SUPREME LAW → Reference to 000_THEORY/000_LAW.md
2. ARCHITECTURE → Reference to 000_THEORY/000_ARCHITECTURE.md  
3. aCLIP PROTOCOL → Reference to 000_THEORY/007_aclip.md
4. AGENT FEDERATION → Reference to 000_THEORY/001_AGENTS.md
5. YOUR IDENTITY → Agent-specific role definition
6. INSTRUCTION TO AGENT → Initialization protocol
```

**Key Principle**: *Adapters are NOT the law. They merely reference the canon.*

---

## 🎯 Root Gateway Documents

### `AGENTS.md` - Main Gateway
- **Purpose**: Entry point for all agents
- **Content**: Minimal overview + links to canon
- **Rule**: No detailed specifications, only navigation

### `README.md` - Human Documentation  
- **Purpose**: Human-readable project overview
- **Content**: Quick start, features, basic usage
- **Rule**: Keep agent-specific details minimal

---

## 🔄 Migration Strategy

### ✅ Completed Modularization
1. **Created canonical aCLIP theory** → `000_THEORY/007_aclip.md`
2. **Refactored root AGENTS.md** → Minimal gateway document  
3. **Updated all agent adapters** → Reference theory canon
4. **Established single source of truth** → All content in `000_THEORY/`

### 🎯 Benefits Achieved
- **No More Duplication**: Update theory once, all agents see changes
- **Clear Authority Chain**: `000_THEORY/` is canonical
- **Agent Independence**: Each adapter can have specific instructions
- **Easy Maintenance**: Single point of truth for all governance

---

## 📋 Content Distribution Matrix

| Content Type | Location | Updates Required |
|--------------|----------|------------------|
| Constitutional Law | `000_THEORY/` | **Single location** |
| Agent Adapters | Root + `.agent/` directories | **Reference only** |
| Implementation | `arifos/` package | **Code changes only** |
| Human Docs | `README.md`, `docs/` | **Human-facing only** |

---

## 🚀 Usage Instructions

### For Agents (When You Arrive)
1. **Read your adapter** → Check your specific `.md` file
2. **Reference the canon** → Immediately read `000_THEORY/` files  
3. **Follow aCLIP protocol** → Use `/000`, `/111`, etc. commands
4. **Respect witness layer** → All actions visible to Federation

### For Developers (When You Modify)
1. **Update theory first** → Change `000_THEORY/` files
2. **Update adapters if needed** → Only agent-specific content
3. **Never duplicate content** → Reference, don't copy
4. **Test with all agents** → Ensure compatibility

---

## 🔍 Verification Checklist

### Modular Architecture Verification
- [ ] All constitutional law in `000_THEORY/` ✅
- [ ] Agent adapters reference canon (don't duplicate) ✅  
- [ ] Root documents are minimal gateways ✅
- [ ] aCLIP protocol has canonical specification ✅
- [ ] Cross-agent witness layer documented ✅

### Single Source of Truth Verification
- [ ] `000_THEORY/000_LAW.md` - Constitutional floors
- [ ] `000_THEORY/007_aclip.md` - Protocol specification  
- [ ] `000_THEORY/001_AGENTS.md` - Agent federation
- [ ] `000_THEORY/000_ARCHITECTURE.md` - System design

---

## 🎉 Success Metrics

### Before Modularization
- ❌ Scattered documentation across multiple files
- ❌ Duplicate content in agent adapters
- ❌ No single source of truth
- ❌ Difficult to maintain consistency

### After Modularization  
- ✅ **Single canonical source** in `000_THEORY/`
- ✅ **Minimal adapters** that reference canon
- ✅ **No duplication** of constitutional content
- ✅ **Easy maintenance** - update once, all agents benefit

---

**DITEMPA BUKAN DIBERI** — Forged through modular architecture, not given through duplication.

> **Next Steps**: Continue refining agent adapters and ensure all new documentation follows the modular pattern.