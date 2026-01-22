# Spec Archive — Drafts (Never Implemented)

**Archived:** 2025-12-30
**Reason:** Draft specs superseded by authoritative implementations, version drift, zero Track C usage
**Category:** Experimental specs that never reached production

---

## Archived File

### fact_check.json (4KB, 66 lines)

**Status:** DRAFT
**Version:** v46.0 ⚠️ **VERSION DRIFT** (v46 in v45 directory)
**Track C References:** 0 (never implemented)

**Purpose:** Post-generation fact-check for fabricated URLs, sources, and citations (F2 Truth floor extension).

**Spec Note:**
> "F2 Truth floor extension: Post-generation fact-check for fabricated URLs, sources, and citations."

---

## Why Archived

### 1. **Superseded by Authoritative Spec**

**fact_check.json (DRAFT)** was superseded by **truth_verification.json (AUTHORITATIVE)**

**Overlapping Functionality:**

| Feature | fact_check.json | truth_verification.json |
|---------|-----------------|-------------------------|
| URL validation | ✅ | ✅ |
| Domain whitelisting | ✅ | ✅ |
| Fabricated link detection | ✅ | ✅ |
| F2 Truth floor trigger | ✅ | ✅ |
| Status | DRAFT | AUTHORITATIVE |
| In MANIFEST | ❌ | ✅ |
| Track C usage | 0 refs | Active |
| Version | v46.0 | v45.0 |

**Both specs handle:**
- Malaysian news outlet whitelisting (bernama.com, thestar.com.my, etc.)
- gov.my domain validation
- PDRM/official source verification
- Hallucinated URL detection

**Resolution:** `truth_verification.json` is the production implementation. `fact_check.json` was a draft that never reached Track C integration.

---

### 2. **Version Drift**

**Directory:** `spec/v45/`
**File version:** `v46.0`

**Issue:** Spec version (v46.0) doesn't match directory version (v45). This indicates experimental work that diverged from v45 epoch.

---

### 3. **Never Implemented**

**Validation:**
```bash
grep -r "fact_check" arifos_core/ --include="*.py"
# Result: 0 references
```

**No Track C loader imports this spec.** It exists only as a draft proposal.

---

## Spec Content Summary

**URL Validation:**
- Regex: `https?://[^\s]+`
- Known domains: bernama.com, thestar.com.my, nst.com.my, etc.
- Validation method: domain_whitelist_or_reachability
- Action on fabrication: VOID

**Citation Validation:**
- Citation markers: "et al.", "(20", "doi:", "ISBN:"
- Validation method: semantic_plausibility
- Action on fabrication: PARTIAL

**Fact Claim Validation:**
- High-stakes keywords: "died", "killed", "mati", "meninggal"
- Crisis patterns requiring 888_HOLD

**All of this functionality was implemented in `truth_verification.json` instead.**

---

## Impact

**Before:**
- Total specs: 10
- Draft specs: 1
- Version drift: 1 file (v46 in v45/)

**After:**
- Total specs: 8
- Draft specs: 0
- Version drift: 0

**Entropy reduction:** -4KB (-4.2% total spec size)

---

## Restoration

If experimental URL validation logic needed:

```bash
# View archived file
git show HEAD:archive/spec_v45_drafts/fact_check.json

# Compare with authoritative version
diff <(git show HEAD:archive/spec_v45_drafts/fact_check.json) spec/v45/truth_verification.json
```

**Note:** Do NOT restore to `spec/v45/` — this was a draft superseded by `truth_verification.json`. If referencing experimental patterns, extract from archive and integrate into authoritative spec.

---

## Track B Integrity

**Zero broken dependencies verified:**
- No runtime imports of `fact_check`
- Not in MANIFEST.sha256.json (never tracked)
- No Track C loader references

**Conclusion:** Safe to archive — draft spec never reached production, superseded by truth_verification.json.

---

**Status:** ✅ ARCHIVED — Draft spec superseded by authoritative implementation
**Impact:** Track B entropy reduced by 4KB, version drift eliminated

**DITEMPA BUKAN DIBERI** — Forged, not given. Truth must cool before it rules.
