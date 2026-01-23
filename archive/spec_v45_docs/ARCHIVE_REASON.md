# Spec Archive — Documentation (Non-Runtime)

**Archived:** 2025-12-30
**Reason:** Documentation specs with zero Track C runtime usage
**Category:** Human-readable policy text (duplicates authoritative spec data)

---

## Archived File

### policy_text.json (8KB, 74 lines)

**Status:** DOCUMENTATION
**Version:** v45.0
**Track C References:** 0 (never used by runtime loaders)

**Purpose:** Human-readable descriptions, explanations, and examples for the 9 constitutional floors.

**Note from spec itself:**
> "Human-readable policy text for constitutional floors. NOT used by runtime loaders (thresholds in constitutional_floors.json). Safe to edit for clarity without affecting enforcement."

---

## Why Archived

**Duplicate Information:**
- All floor thresholds are authoritative in `spec/v45/constitutional_floors.json`
- `policy_text.json` was human reference only (examples, explanations)
- Runtime loaders never import this file

**Validation:**
```bash
grep -r "policy_text" arifos_core/ --include="*.py"
# Result: 0 references
```

**Constitutional Content:**
- F1 Amanah examples
- F2 Truth examples
- F4 DeltaS examples
- F5 Peace² examples
- F6 κᵣ examples
- F7 Ω₀ examples
- RASA examples
- GENIUS examples

**All examples are illustrative only — actual thresholds in `constitutional_floors.json`.**

---

## Impact

**Before:**
- Total specs: 10
- Documentation specs: 1

**After:**
- Total specs: 8
- Documentation specs: 0 (pure Track B authority only)

**Entropy reduction:** -8KB (-8.3% total spec size)

---

## Restoration

If human-readable policy examples needed:

```bash
# View archived file
git show HEAD:archive/spec_v45_docs/policy_text.json

# Restore (to docs/ NOT spec/, since it's documentation)
git show HEAD:archive/spec_v45_docs/policy_text.json > docs/policy_examples.json
```

**Note:** Do NOT restore to `spec/v45/` — this is documentation, not runtime authority. If restoring, place in `docs/` directory.

---

## Track B Integrity

**Zero broken dependencies verified:**
- No runtime imports of `policy_text`
- No manifest hash (never tracked)
- No Track C loader references

**Conclusion:** Safe to archive — pure documentation with no runtime impact.

---

**Status:** ✅ ARCHIVED — Documentation spec separated from Track B runtime authority
**Impact:** Track B entropy reduced by 8KB, 100% runtime-authoritative specs remain

**DITEMPA BUKAN DIBERI** — Forged, not given. Truth must cool before it rules.
