# ICL v42 → v43 Migration Notes

**Status**: Reference document  
**Read if**: You worked with ICL v42.x and want to understand v43 changes  
**Key Message**: No breaking changes. Three major clarifications.

---

## Summary

v43 ICL spec removes ambiguity that existed in v42.x. The **actual behavior remains the same**—these are clarifications of what was already true.

---

## Three Major Clarifications

### 1. ICL is Explicitly Orthogonal to aCLIP (000–999)

**v42.x ambiguity**:
- Were AAA/WWW/EEE stages in the pipeline?
- Could they block /999 seals?
- Were they part of 000–999?

**v43 clarity**:
- **aCLIP (Layer 3)** = 000–999 decision choreography (immutable state machine)
- **ICL (Layer 2)** = AAA/WWW/EEE quality instruments (orthogonal, optional)
- AAA/WWW/EEE do NOT advance aCLIP state
- AAA/WWW/EEE do NOT block /999 seals
- AAA/WWW/EEE run independently, called by operator
- /666 BRIDGE (inside aCLIP) enforces floors—ICL does not

**Migration**: No code changes needed. Just understand the boundary.

---

### 2. AAA / WWW / EEE are Quality Instruments, NOT Process Steps

**v42.x ambiguity**:
- Do they have output ports/buffers like 000–999?
- Do they write to vault_999 or cooling_ledger?
- Are they mandatory for any decision type?

**v43 clarity**:
- **AAA** = pre-pipeline quality framing (optional)
- **WWW** = stress-test before commit (optional, context-selective)
- **EEE** = post-pipeline wisdom extraction (recommended after high-stakes)
- **None are mandatory**
- None write to cooling_ledger directly
- EEE output goes to human-operator memory, not model memory
- Operator consciously applies EEE insights in future /222 stages

**Migration**: No changes if you were using them informally. Formalize expectations.

---

### 3. Governance is Enforcement, NOT Aspiration

**v42.x ambiguity**:
- Are floors (F1–F9) hard constraints or soft guidelines?
- Do they always block?
- Are they "constitutional aspirations"?

**v43 clarity**:
- **Hard floors** (F1, F2, F3, F4, F7, F9) = violations → VOID (refuse progression)
- **Soft floors** (F5, F6, F8) = violations → PARTIAL (warn, but allow override)
- **Enforcement point**: /666 BRIDGE inside aCLIP
- **Not aspirations**: Architectural constraints, automatically checked
- **Non-negotiable**: F1 and F9 cannot be overridden (human or otherwise)

**Migration**: Review your /666 logic. Ensure F1 and F9 are truly non-negotiable.

---

## What Stays the Same

✔ /000–/999 stages and their purposes  
✔ /666 floor checking logic  
✔ /999 seal ceremony  
✔ aCLIP determinism  
✔ Constitutional floors F1–F9  
✔ Humility band Ω₀ ∈ [0.03, 0.05]  
✔ vault_999 integration  
✔ cooling_ledger audit trail  

---

## Document Changes

### Old Documents (v42.x)

- `docs/Intelligence-Control-Layer-ICL-Formal-Spec.md` (attached to thread; comprehensive but unclear boundaries)
- Scattered across `docs/` folder without clear hierarchy

### New Document (v43)

- [`docs/ICL_v43_CANONICAL_SPEC.md`](ICL_v43_CANONICAL_SPEC.md) (canonical, clean, no ambiguity)
- Explicitly states what ICL IS and IS NOT
- Clear section on relationship to aCLIP
- Removed all "future-looking" language
- Focused on current v43 reality

---

## For Different Roles

### If You're a Prompt Engineer

**Read**: Section 4 of [ICL_v43_CANONICAL_SPEC.md](ICL_v43_CANONICAL_SPEC.md) (AAA/WWW/EEE)  
**Action**: 
- Use /AAA before high-stakes decisions
- Use /WWW to stress-test your logic
- Use /EEE after surprises

### If You're a Systems Architect

**Read**: Sections 3, 5, and full spec  
**Action**:
- Confirm aCLIP does not auto-trigger ICL
- Verify /666 floor checks are exhaustive
- Plan EEE → /222 feedback loop

### If You're Building Tooling

**Read**: Sections 5 and 6  
**Action**:
- Do NOT block aCLIP progression in ICL layer
- Floor enforcement must happen in /666 BRIDGE, not outside
- Audit trails in cooling_ledger, not ICL output buffers

---

## Testing Checklist

**After v43 migration, verify**:

- [ ] /AAA output does not affect /666 verdict
- [ ] /WWW output does not affect /666 verdict
- [ ] /EEE output does not write to cooling_ledger
- [ ] /666 floor checks are identical (behavior unchanged)
- [ ] F1 and F9 violations still cause VOID
- [ ] Soft floor violations still cause PARTIAL
- [ ] aCLIP state machine remains deterministic
- [ ] vault_999 integration works via /222, not ICL

---

## FAQ

### Q: Do I need to rewrite my ICL integrations?

**A**: No. If you were using ICL informally (calling AAA before decisions, WWW for stress-test, EEE for reflection), nothing changes. The new spec just formalizes what you were already doing.

### Q: Can AAA/WWW/EEE block /999 seals?

**A**: No. Only /666 BRIDGE (inside aCLIP) can block /999. AAA/WWW/EEE are informative layers.

### Q: Is EEE memory persisted in vault_999?

**A**: No. EEE is extracted by the human operator and consciously applied in future /222 REFLECT stages. The model does not auto-learn from EEE.

### Q: If I ignore AAA/WWW/EEE, does aCLIP still work?

**A**: Yes. aCLIP is self-contained. ICL instruments are optional enhancements. Run 000→999 with or without them.

### Q: What if I discover a floor violation in AAA/WWW analysis?

**A**: /AAA and /WWW are pre-pipeline. If they surface a floor violation (e.g., "we're building on false assumption"), that's input to your /000 initialization. Redesign before running the pipeline.

---

## Next Steps

1. **Read** [`ICL_v43_CANONICAL_SPEC.md`](ICL_v43_CANONICAL_SPEC.md)
2. **Review** your current ICL integrations against Section 5 (Relationship to aCLIP)
3. **Verify** /666 floor checks (Section 6)
4. **Update** any documentation referring to v42.x ICL
5. **Test** that aCLIP determinism is preserved

---

**Ditempa, bukan diberi.** ✊

arifOS v43 — Intelligence governed, not unleashed.
