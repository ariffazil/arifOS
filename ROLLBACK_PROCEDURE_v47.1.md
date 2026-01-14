# Rollback Procedure for arifOS v47.1

**Document Version:** v47.1.0  
**Date:** 2026-01-14  
**Purpose:** Emergency rollback instructions for v47.1 constitutional cleanup

---

## When to Rollback

Rollback if you experience:
- Import errors that shims don't resolve
- Test failures not related to spec validation
- Breaking changes in production
- Unexpected behavior after upgrade

**Note:** Minor spec validation warnings are expected and being addressed in Move 5.

---

## Option 1: Use Backward Compatibility Shims (Recommended)

**Duration:** 72 hours from v47.1 release

**Status:** ✅ **ACTIVE**

All deprecated import paths continue working via shims. No action needed!

```python
# These still work (with deprecation warnings)
from arifos_core.apex.governance import ledger
from arifos_core.guards.injection_guard import InjectionGuard
from arifos_core.enforcement.eval.agi import evaluate_agi_layer
```

**What to do:**
1. Keep using your existing code
2. Plan migration within 72 hours
3. Update imports gradually
4. Test with new imports in development

---

## Option 2: Git Revert (Emergency Only)

### Step 1: Identify Commits to Revert

```bash
# View recent v47.1 commits
git log --oneline --grep="Phase 444" -10

# Example output:
# abc1234 [Phase 444.1] State extraction - Create deprecation shims
# def5678 [Phase 333] Complete REASON - Proposed structure
```

### Step 2: Revert Specific Changes

**Revert State Extraction (Move 1):**
```bash
git revert <commit-hash-444.1>
```

**Revert All v47.1 Changes:**
```bash
# Find the commit before Phase 444 started
git log --oneline | grep "Phase 333"  # Find last Phase 333 commit
git revert <commit-hash-444.1>..<current-commit> --no-commit
git commit -m "Rollback v47.1 changes"
```

### Step 3: Verify Rollback

```bash
# Check that old paths work without shims
python3 -c "from arifos_core.apex.governance import ledger; print('✅ Rollback successful')"

# Run tests
pytest tests/ -v
```

---

## Option 3: Pin to Previous Version

### In pyproject.toml

```toml
[project]
dependencies = [
    "arifos-core==47.0",  # Pin to pre-v47.1
]
```

### In requirements.txt

```
arifos-core==47.0
```

### Using pip

```bash
pip install arifos-core==47.0
```

---

## Option 4: Selective Rollback (Cherry-pick)

If only specific moves cause issues:

### Rollback State Extraction Only

```bash
# Restore original files
git checkout <pre-v47.1-commit> -- arifos_core/apex/governance/ledger.py
git checkout <pre-v47.1-commit> -- arifos_core/apex/governance/ledger_cryptography.py
git checkout <pre-v47.1-commit> -- arifos_core/apex/governance/ledger_hashing.py
git checkout <pre-v47.1-commit> -- arifos_core/apex/governance/merkle.py
git checkout <pre-v47.1-commit> -- arifos_core/apex/governance/merkle_ledger.py

# Remove shims
rm arifos_core/apex/governance/ledger.py  # If it's a shim
# ... repeat for other shims

# Commit rollback
git add arifos_core/apex/governance/
git commit -m "Rollback: Restore state files to apex/governance"
```

### Rollback Guards Elevation Only

```bash
# Restore original guards/
git checkout <pre-v47.1-commit> -- arifos_core/guards/

# Commit rollback
git add arifos_core/guards/
git commit -m "Rollback: Restore guards/ directory"
```

---

## Verification After Rollback

### Test Imports

```python
# Test that all imports work
from arifos_core.apex.governance import ledger
from arifos_core.apex.governance.ledger_cryptography import CryptographicLedger
from arifos_core.guards.injection_guard import InjectionGuard
from arifos_core.enforcement.eval.agi import evaluate_agi_layer

print("✅ All imports working after rollback")
```

### Run Test Suite

```bash
# Run full test suite
pytest tests/ -v

# Run specific test modules
pytest tests/test_ledger*.py -v
pytest tests/test_hypervisor*.py -v
pytest tests/enforcement/ -v
```

### Check for Spec Validation Errors

```bash
# Test with legacy spec allowed
ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/ --collect-only -q

# Should show 0 errors if rollback successful
```

---

## Post-Rollback Actions

### 1. Report Issue

If rollback was necessary due to a bug:

```bash
# Create issue on GitHub
gh issue create \
  --title "v47.1 Rollback Required: [describe issue]" \
  --label "rollback,v47.1" \
  --body "Rolled back due to: [description]"
```

### 2. Document What Failed

Create a rollback report:

```markdown
## Rollback Report

**Date:** 2026-01-14
**Rolled Back:** [Move 1 / Move 2 / All v47.1 changes]
**Reason:** [Import errors / Test failures / Production issue]
**Steps Taken:** [git revert / selective restore / version pin]
**Verification:** [Tests passing / Imports working]
```

### 3. Update Dependencies

If you pinned to v47.0, remember to:
- Document the pin in your project README
- Set a reminder to retry v47.1 after fix
- Watch for v47.1.1 patch release

---

## Prevention for Future Upgrades

### Before Upgrading to v47.2+

1. **Test in Development First:**
   ```bash
   # Create test environment
   python -m venv test_v47
   source test_v47/bin/activate
   pip install arifos-core==47.1
   # Run your tests
   pytest
   ```

2. **Review Deprecation Warnings:**
   ```bash
   # Enable warnings
   python -W default::DeprecationWarning -m pytest tests/
   ```

3. **Check Migration Guide:**
   - Read `MIGRATION_GUIDE_v47.1.md`
   - Identify deprecated imports in your code
   - Plan migration timeline

4. **Gradual Migration:**
   - Migrate one module at a time
   - Test after each migration
   - Keep rollback option available

---

## Support

### Get Help

1. **Check Documentation:**
   - `MIGRATION_GUIDE_v47.1.md` - Migration instructions
   - `PHASE_333_SUMMARY.md` - Overview of changes

2. **Search Existing Issues:**
   ```bash
   gh issue list --label "v47.1"
   ```

3. **Create New Issue:**
   ```bash
   gh issue create \
     --title "v47.1 Issue: [brief description]" \
     --label "v47.1,help-wanted"
   ```

### Emergency Contact

For critical production issues:
- Tag issue with `critical` and `v47.1`
- Mention @ariffazil for urgent review
- Include rollback steps already attempted

---

## Timeline

### Immediate (Now)
- ✅ Backward compatibility shims active
- ✅ Old imports continue working
- ⚠️ Deprecation warnings present

### 72 Hours (2026-01-17)
- ❌ Shims will be removed in v47.2
- ✅ New imports required
- ✅ All internal code migrated

### If Rollback Needed
- ⏸️ Stay on v47.0 until issues resolved
- 📋 Wait for v47.1.1 patch release
- 🔄 Retry migration when stable

---

**Remember:** Rollback is a safety mechanism, not a failure! The 72-hour shim window exists precisely for this scenario.

**DITEMPA BUKAN DIBERI** — Built with rollback safety from the start.

**Document Status:** ACTIVE  
**Maintained By:** arifOS Core Team  
**Last Updated:** 2026-01-14
