# arifOS Versioning Policy

**Version:** v42.0 | **Status:** DRAFT | **Last Updated:** 2025-12-16

---

## Version Numbering

arifOS uses **Semantic Versioning** (SemVer) with constitutional significance:

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

| Component | Meaning | Example |
|-----------|---------|---------|
| MAJOR | Constitutional law change (floors, verdicts) | v42.0.0 |
| MINOR | Feature addition (backward compatible) | v42.1.0 |
| PATCH | Bug fix (no behavior change) | v42.0.1 |
| PRERELEASE | Release candidate, alpha, beta | v42.0.0-rc1 |

---

## Canon Version Suffix

All canonical documents carry a version suffix:

```
FILENAME_v{MAJOR}.md
```

**Examples:**
- `constitutional_floors_v42.md`
- `genius_law_v42.md`
- `pipeline_v42.yaml`

**Rule:** Version appears in **filename**, NOT in folder path.

---

## Version Lifecycle

| Phase | Suffix | Meaning |
|-------|--------|---------|
| Draft | `_v42_DRAFT.md` | Work in progress, not authoritative |
| RC | `_v42_RC.md` | Release candidate, pending review |
| Omega | `_v42.md` | Canonical, authoritative law |
| Frozen | `_v42_FROZEN.md` | Archived, read-only reference |

---

## Track A/B/C Alignment

| Track | Location | Version Source |
|-------|----------|----------------|
| A (Canon) | `canon/` | Filename suffix |
| B (Spec) | `spec/v42/` | Folder + filename |
| C (Code) | `arifos_core/` | `pyproject.toml` |

**Invariant:** All three tracks MUST reference the same MAJOR version.

---

## Amendment Process (Phoenix-72)

Constitutional changes require:

1. **Proposal** in `canon/06_paradox/` with `_PROPOSED.md` suffix
2. **72-hour cooling period** (minimum)
3. **Human seal** (explicit approval)
4. **Version bump** (MAJOR for floor changes)

See: `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md` for details.

---

## Backward Compatibility

| Change Type | Compatibility | Required Action |
|-------------|---------------|-----------------|
| Floor threshold change | BREAKING | MAJOR bump |
| New verdict type | BREAKING | MAJOR bump |
| New optional field | Compatible | MINOR bump |
| Documentation fix | Compatible | PATCH bump |

---

**DITEMPA BUKAN DIBERI** - Forged, not given; truth must cool before it rules.
