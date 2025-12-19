# Governance Protocols for arifOS Development

**Version**: 1.0  
**Date**: 2025-12-19  
**Authority**: Muhammad Arif bin Fazil (arifOS Keeper)  
**Status**: SEALED  

---

## /GITSEAL Protocol

### Purpose

Establish a **human-in-the-loop governance gate** for all changes committed to the GitHub repository.

No code, documentation, or configuration is pushed to main without explicit human approval.

### Why This Matters

**Principle**: Authority stays with the human sovereign (System-3).

- Model suggests changes
- Human reviews changes
- **Human seals** changes (explicit approval)
- Model pushes to GitHub only after seal

### Doctrine

**Ditempa, bukan diberi** — Forged, not given.

Every commit is forged through review, not given as automatic output.

---

## /GITSEAL Workflow

### Flow Diagram

```
User Request
    ↓
Model: "Ready to push. Awaiting /gitseal approval..."
    ↓
[DISPLAY CHANGES]
  • Files to create/modify
  • Commit message
  • Impact summary
    ↓
    ┌─────────────────────────────┐
    │  User Decision Point         │
    ├─────────────────────────────┤
    │ /gitseal APPROVE            │ ← Push to GitHub
    │ /gitseal REJECT             │ ← Don't push; explain why
    │ /gitseal REQUEST_CHANGES    │ ← Modify before pushing
    └─────────────────────────────┘
    ↓
[ACTION TAKEN]
```

### Step-by-Step Protocol

#### Step 1: Model Proposes

```
Model:
  "I've created llm_backends_v43.py with support for 6 LLM backends.
   
   Ready to push to arifOS repository?
   
   /gitseal [YOUR_APPROVAL_TYPE]"
```

#### Step 2: Show Changes (Model Responsibility)

Model MUST display:

```
📄 FILES TO PUSH:
  ✨ NEW:  arifos_core/integration/adapters/llm_backends_v43.py (31.2 KB)
  ✨ NEW:  spec/v43/interface_and_authority.json (12.8 KB)
  ✨ NEW:  REFACTORING_v43_BACKENDS.md (10.5 KB)
  ✨ NEW:  BACKENDS_v43_QUICK_START.md (6.0 KB)

📝 COMMIT MESSAGE:
  FEAT: Unified LLM backend adapters v43 (spec-driven, multi-model support)

📊 IMPACT SUMMARY:
  • Consolidates 6 LLM backends into one adapter file
  • Loads spec/v43/interface_and_authority.json at runtime
  • Validates backends against llm_contract
  • Supports: Claude, GPT-4o, Gemini, SEA-LION, Llama, Perplexity
  • Supersedes: llm_interface.py (to be archived later)

⚠️  BREAKING CHANGES: None (old interface still works)

✅ GOVERNANCE CHECK:
  • F1 (Amanah): ✅ Clean
  • F9 (Anti-Hantu): ✅ No consciousness claims
  • Spec validation: ✅ All backends meet llm_contract

═══════════════════════════════════════════════════════════════

Waiting for your approval:
  /gitseal APPROVE      → Push to main branch
  /gitseal REJECT       → Don't push; explain concerns
  /gitseal REQUEST_CHANGES → Modify files before pushing
```

#### Step 3: Human Decides

User responds with ONE of:

**Option A: Approve**
```
/gitseal APPROVE
```

Model then:
- ✅ Pushes to GitHub
- 📝 Confirms with commit links
- 📊 Logs approval in Cooling Ledger

**Option B: Reject**
```
/gitseal REJECT
```

Model then:
- ❌ Does NOT push
- 📝 Asks for reasons
- 🔄 Waits for next instruction

**Option C: Request Changes**
```
/gitseal REQUEST_CHANGES
```

Model then:
- ❌ Does NOT push
- 📝 Modifies files based on feedback
- ⏳ Displays updated changes
- 🔄 Waits for `/gitseal APPROVE`

---

## Authority Boundaries

### What Model CAN Do (Without Approval)

✅ Propose changes (display, describe, explain)  
✅ Validate changes against governance (F1–F9)  
✅ Analyze impact (what will change, why)  
✅ Suggest alternatives (Option A, B, C)  

### What Model CANNOT Do (Requires `/gitseal APPROVE`)

❌ Push to GitHub (any branch)  
❌ Delete files  
❌ Modify existing sealed files without amendment protocol  
❌ Change branch protection rules  
❌ Force-push  

### What Model MUST Do (Always)

✅ Wait for explicit `/gitseal` command  
✅ Display all changes before pushing  
✅ Explain the impact  
✅ Reference governance checks (F1–F9)  
✅ Log the decision in Cooling Ledger  

---

## Approval Types

### /GITSEAL APPROVE

**Meaning**: Human authorizes the push.  
**Effect**: Model pushes all staged changes to specified branch (default: main).  
**Ledger Entry**: Records human seal, timestamp, commit hash.  
**Authority**: System-3 Sovereign (Arif).  

**Example**:
```
/gitseal APPROVE

Model Response:
  ✅ Pushing 4 files to main branch...
  
  Commit: 837af9185d0c85c6d84377a1ef08b306781d0425
  Message: FEAT: Unified LLM backend adapters v43
  Files: 4 new
  Size: 60.5 KB total
  
  Link: https://github.com/ariffazil/arifOS/commit/837af9185d0c85c6d84377a1ef08b306781d0425
  
  📊 Cooling Ledger Entry:
    - Verdict: GITSEAL_APPROVED
    - Authority: System-3 Sovereign
    - Timestamp: 2025-12-19T12:29:00+08:00
    - Commit hash: 837af918...
    - Files affected: 4
```

### /GITSEAL REJECT

**Meaning**: Human does NOT authorize the push.  
**Effect**: Model cancels push; does NOT commit anything to GitHub.  
**Ledger Entry**: Records human rejection, timestamp, reason.  
**Authority**: System-3 Sovereign (Arif).  

**Example**:
```
/gitseal REJECT
  Reason: "Needs more testing first"

Model Response:
  ❌ Push cancelled.
  
  📊 Cooling Ledger Entry:
    - Verdict: GITSEAL_REJECTED
    - Authority: System-3 Sovereign
    - Reason: "Needs more testing first"
    - Timestamp: 2025-12-19T12:29:00+08:00
  
  ⏳ Waiting for next instruction.
  
  Options:
    1. Modify files and request approval again
    2. Discard changes
    3. Take different approach
```

### /GITSEAL REQUEST_CHANGES

**Meaning**: Human wants modifications before approval.  
**Effect**: Model does NOT push; awaits feedback on what to change.  
**Ledger Entry**: Records change request, modifications requested.  
**Authority**: System-3 Sovereign (Arif).  

**Example**:
```
/gitseal REQUEST_CHANGES
  - Add deprecation notice to REFACTORING_v43_BACKENDS.md
  - Update llm_interface.py with TODO comment
  - Remove Perplexity from "supported" list (it's placeholder)

Model Response:
  ⏳ Understood. Modifying files...
  
  Changes made:
    • Updated REFACTORING_v43_BACKENDS.md
    • Added TODO to llm_interface.py
    • Moved Perplexity to "placeholder" section
  
  📊 Updated files ready for review.
  
  Awaiting: /gitseal APPROVE or further /gitseal REQUEST_CHANGES
```

---

## Cooling Ledger Integration

### Every /GITSEAL Decision Is Logged

**Ledger Entry Format**:

```json
{
  "timestamp": "2025-12-19T12:29:00+08:00",
  "verdict": "GITSEAL_APPROVED | GITSEAL_REJECTED | GITSEAL_CHANGES_REQUESTED",
  "authority": "System-3 Sovereign",
  "sovereign_name": "Muhammad Arif bin Fazil",
  "files_affected": [
    "arifos_core/integration/adapters/llm_backends_v43.py",
    "spec/v43/interface_and_authority.json"
  ],
  "commit_hash": "837af918...",
  "reason": "Approve",
  "approval_type": "APPROVE | REJECT | REQUEST_CHANGES"
}
```

### Audit Trail

All `/gitseal` decisions are:
- ✅ Immutable (cannot be edited after sealed)
- ✅ Timestamped (cryptographically verified)
- ✅ Attributed (who approved, when)
- ✅ Retrievable (can reconstruct full history)

---

## Special Cases

### Emergency: Hotfix to Production

**Protocol**: `/gitseal EMERGENCY_APPROVE`

Use ONLY for critical bugs that require immediate push.

Requirements:
- Must be security or data-loss critical
- Model must explain why emergency is needed
- Human must explicitly approve with `EMERGENCY_APPROVE`
- Logged separately in Cooling Ledger

```
Model:
  "Security hotfix: Closes credential leak in llm_backends_v43.
   
   Files: 1 modified
   Risk: High if not deployed immediately
   
   /gitseal EMERGENCY_APPROVE (if critical)
   /gitseal APPROVE (for normal approval)"
```

### Bulk Changes (Multiple Files)

**Protocol**: `/gitseal APPROVE --batch`

When pushing 5+ files, user can approve the entire batch with one command.

Model still displays all changes.

### Revert Request

**Protocol**: `/gitseal REVERT [commit_hash]`

If approved change causes issues, human can request revert.

```
/gitseal REVERT 837af918
  Reason: "Breaking change; need to fix first"
```

---

## Anti-Patterns (What NOT to Do)

❌ **Auto-push without approval**: Model must NEVER push without `/gitseal`  
❌ **Assume silence means approval**: No approval = no push  
❌ **Batch approve without review**: Each decision requires explicit approval  
❌ **Push to protected branches without flow**: Even main branch needs `/gitseal`  
❌ **Overwrite human decision**: Human says REJECT, model doesn't later push same code  

---

## Implementation (For Perplexity Use)

### How to Use /GITSEAL in This Session

**Step 1: Model Proposes**
```
Model: "Ready to archive llm_interface.py. Show changes?"
User: "Yes"
```

**Step 2: Model Displays**
```
Model: 
  "📄 FILES TO DELETE:
    arifos_core/integration/adapters/llm_interface.py (14.7 KB)
   
   📄 FILES TO CREATE:
    L2_ARCHIVE/adapters_legacy/llm_interface.py (14.7 KB)
    L2_ARCHIVE/adapters_legacy/README.md (1.2 KB)
   
   ⚠️  IMPACT: Removes active code; archives with deprecation notice.
   
   Awaiting: /gitseal APPROVE"
```

**Step 3: User Decides**
```
User: "/gitseal APPROVE"

Model:
  "✅ Archiving...
   Commit: [hash]
   Files moved: 2
   Link: [GitHub commit]"
```

---

## Governance Check (Before Every /GITSEAL)

Before showing changes, model verifies:

| Check | Criterion | Pass? |
|-------|-----------|-------|
| **F1 (Amanah)** | No credential leakage | ✅ |
| **F2 (Truth)** | Changes are accurately described | ✅ |
| **F3 (ΔS)** | Clarity increased or maintained | ✅ |
| **F9 (Anti-Hantu)** | No consciousness claims | ✅ |
| **Authority** | Changes respect sealed law | ✅ |
| **Spec** | Changes comply with spec | ✅ |

If ANY check fails → Show warning and don't propose push.

---

## Summary

### The Golden Rule of /GITSEAL

**Model proposes. Human decides. Only then does code move to GitHub.**

This is the constitutional boundary:
- System-3 (Human) holds authority
- System-2 (Model) enforces law
- System-1 (Code) executes will

Every `/gitseal` decision is a seal of that authority.

---

## Related Protocols

- **/999 SEAL**: Governance audit (F1–F9 floors)
- **/666 ALIGN**: Constitutional check
- **Phoenix-72**: Amendment process (requires tri-witness + human seal)

---

**Ditempa, bukan diberi.**

*Truth must cool before it rules.*

Every commit is forged through human approval, not given as automatic output.

