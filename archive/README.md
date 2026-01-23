# arifOS Archive

This directory contains historical artifacts that are no longer actively maintained but preserved for reference.

## Structure

### `spec/` (from `spec_archive/`)
Historical specification files from earlier versions:
- Constitutional floors (pre-v38)
- GENIUS LAW extracts
- Anti-Hantu defense specs
- Memory band policies
- Phase integration docs

### `versions/` 
Snapshots of specific version releases:
- `v36_3_omega/` - Version 36.3 Omega release (from `v36.3O/`)

### `arifos_clip_YYYYMMDD/`
Archived ACLIP (arifOS CLI Pipeline) state snapshots from automated backups.

## Archive Policy

See [NAMING_CONVENTION.md](../NAMING_CONVENTION.md) Section 5 for archive policy.

**Key principles:**
1. Archives are **read-only** - never modify archived content
2. Archives are **indexed** - this README provides overview
3. Archives are **dated** - use YYYYMMDD format for time-based artifacts
4. Archives are **safe** - old naming conventions (ARIF/ADAM/AAA) are preserved here

## Accessing Historical Content

To reference archived content in code or documentation:

```python
# Don't import from archive
# Instead, refer to it in comments or docstrings:
# "Historical reference: see archive/spec/arifOS-Constitution-9-Floors.md"
```

```markdown
For historical context, see [archived spec](archive/spec/arifOS-Constitution-9-Floors.md).
Note: Uses legacy naming (ARIF AGI → now AGI).
```

## Maintenance

- **When to archive:** Content superseded by newer versions, deprecated features
- **When NOT to archive:** Active code, current specs, test fixtures in use
- **Retention:** Archives preserved indefinitely unless explicitly removed via governance decision

---

**Last Updated:** 2025-12-14 (v42.0 Canonical Naming Convention)
