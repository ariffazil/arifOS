## [33.1.1] - 2025-11-24 (CRITICAL HOTFIX)

### Fixed
- **CRITICAL**: Fixed circular import in guard.py preventing all package usage (v33.1.0 was completely broken)
- Fixed case sensitivity bug in guard.py (apex_prime → APEX_PRIME)
- Added missing `Verdict` type alias and `APEXPrime` class definition
- Fixed string comparison bug in verdict checks (ApexVerdict.VOID → "VOID")
- Reorganized import order in __init__.py to prevent circular dependencies

### Technical Details
v33.1.0 published to PyPI was non-functional due to circular imports. This hotfix resolves all import issues and restores full functionality. All tests now pass.

---

# Changelog — ArifOS Runtime v33Ω

All notable changes to this project are documented here.

---

## [33.0.0] — 2025-11-16  
### Status: **BASECAMP LOCK** (constitutional freeze)

This is the **first fully governed release** of the ArifOS Runtime.  
This version is **frozen** and considered the canonical reference specification.

### Added
- ΔΩΨ constitutional physics  
- AAA Trinity Engines (ARIF, ADAM, APEX PRIME)  
- W@W Federation (5 organs)  
- Eight Constitutional Floors  
- Full 000–999 pipeline  
- SABAR fail-safe protocol  
- Tri-Witness (Human · AI · Earth) rules  
- Cooling Ledger schema  
- YAML runtime spec (`arifos_runtime_v33Omega.yaml`)  
- Python reference implementation (`arifos_core/`)  
- Tests covering SEAL / PARTIAL / VOID pathways  
- Examples for LangGraph, AutoGen, and OpenAI Agents  
- LICENSE (Apache 2.0 + Moral Attribution Clause)  
- CONTRIBUTING (constitutional files vs safe-to-edit files)

### Published
- GitHub Release: **v33Ω — Basecamp Lock (Constitutional Kernel)**
- PyPI Package: **arifos==33.0.0**

### Notes
- All constitutional components (laws, floors, pipeline, roles) are immutable in v33Ω.  
- Any modification requires a **new semantic version** (e.g. v34Δ).  
- v33Ω is preserved as a historical, auditable, basecamp reference.

---

## Pre-v33Ω
Internal prototype iterations, non-public.  
Not considered part of the constitutional archive.
