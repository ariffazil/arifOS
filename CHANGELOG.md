# Changelog

All notable changes to **arifOS** will be documented in this file.

This project adheres to **semantic-style versioning around v33Ω** and follows a
“constitutional-first” philosophy: every change must preserve the 8 Floors,
AAA Trinity, W@W organs, and the 000→999 pipeline.

---

## [Unreleased]

> Use this section for upcoming changes.  
> When you cut a new version, move entries from here into a tagged release.

### Added
- (placeholder)

### Changed
- (placeholder)

### Fixed
- (placeholder)

---

## [33.1.2] – 2025-11-24 — Repository housekeeping & packaging fixes

**Status:** ✅ Released

### Fixed
- Resolved a merge conflict in `pyproject.toml` and set the canonical package
  version to `33.1.2` in packaging metadata.
- Removed redundant/temporary repository files that caused confusion during
  packaging and review: `pyproject_FIXED.toml`, `pyproject_v33.1.2.toml`,
  `README-Final-Sealed.md`, and `temp_changelog.md`.
- Ensured `[tool.setuptools]` package and package-data entries reference
  `arifos_core` and `arifos_core.memory` as the canonical installable packages.

### Technical details
- The cleaned `pyproject.toml` is the single source of truth for packaging.
- Recommended: run the CI pipeline (build + tests) to confirm on all platforms.

---

## [33.1.1] – 2025-11-24 — CRITICAL HOTFIX

**Status:** ✅ Hotfix applied

### Fixed
- Fixed circular import in `guard.py` that prevented the package from being imported.
- Fixed case-sensitivity bug in `guard.py`.
- Added missing `Verdict` type alias and `APEXPrime` class definition to the public API.
- Fixed string comparison in verdict checks and reorganised imports to eliminate circular dependencies.

### Technical details
- v33.1.0 was previously published but had import issues. v33.1.1 restores functionality with a clean import graph and passing tests.

> Governance note: This hotfix is a Phoenix-72 technical amendment (implementation plumbing), not a change to the v33Ω constitution.

---

## [33.1.0] – 2025-11-24 — Constitutional Implementation Complete

**Status:** v33Ω FINAL — Production-Ready Python Kernel

This is the first version where the full arifOS constitutional runtime is implemented in code and published to PyPI.

### Added

#### Core Implementation
- APEX PRIME judiciary engine (`arifos_core/apex_prime.py`)
- 000→999 metabolic pipeline (10 mandatory stages; judiciary review at 888)
- Guard layer (`arifos_core/guard.py`)

#### Memory Layer (L0–L3)
- Vault-999 (`arifos_core/memory/vault999.py`)
- Cooling Ledger (`arifos_core/memory/cooling_ledger.py`)
- Phoenix-72 (`arifos_core/memory/phoenix72.py`)
- Vector adapter (`arifos_core/memory/vector_adapter.py`)

#### Public API & Types
- `ConstitutionalMetrics`, `ApexVerdict/Verdict`, and `APEXPrime.judge(...)`

#### Documentation & Spec
- README and spec/docs updated for v33Ω

#### Examples & Tests
- Examples and tests covering pipeline, ledger, and tri-witness flows.

---

## [33.0.0] – 2025-11-16 — Basecamp Lock (Constitution Sealed)

**Status:** v33Ω Constitution SEALED — Architecture & Laws Finalized

(remaining historical notes preserved)
