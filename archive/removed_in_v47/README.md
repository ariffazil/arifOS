# v47 Equilibrium Architecture - Removed Code

## Reason for Removal
Part of Phase 5: Dead Code Elimination in v47 Equilibrium Architecture reorganization.
Goal: Reduce entropy (ΔS) by removing experimental/research code not used in production.

## Archived Content

### arifos_core/system/research/
**Status:** Experimental proof-of-concept code  
**Imports:** 0 (not used in production)  
**Created:** 2026-01-06  
**Removed:** 2026-01-12 (v47 reorganization)

**Files:**
- `proof_of_causality.py` - DSPy-based demonstration of kernel-level AI governance
  - Demonstrates F5 Peace² floor enforcement
  - Neuro-symbolic integration proof-of-concept
  - Not production-ready, educational/demo purpose only

- `README.md` - Research directory guidelines
  - Explains purpose: POC code, experimental features
  - Sets boundaries between research vs production code

**Why Removed:**
1. Zero imports from production code
2. Marked as "proof-of-concept" and "may not be production-ready"
3. Uses external dependencies (dspy) not in core requirements
4. Demonstration code, not runtime functionality

**Recovery:**
This directory is preserved in `archive/removed_in_v47/research/` if needed for reference.

**Entropy Impact:**
- ΔS reduction: ~0.5 (2 files, 1 research directory)
- Eliminates conceptual confusion between research and production code

---

**DITEMPA BUKAN DIBERI** — Research cooled, archived, and separated from production law.
