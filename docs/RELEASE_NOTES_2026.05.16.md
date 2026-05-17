# RELEASE NOTES — arifOS Federation (v2026.05.16)

> **Epoch:** 2026-05-16 | **Status:** SEALED | **Authority:** 888_JUDGE

This release marks the completion of the **Horizon Alignment** and **Root Hygiene** mission across the seven core repositories.

## 🚀 Unified Changes

### 🏛️ Infrastructure Alignment
- **Centralized Deployment**: All `docker-compose` and `Caddy` logic has been moved from domain repos to the `A-FORGE` orchestration shell.
- **Relative Pathing**: All volume mounts refactored to use relative paths anchored in the federation topology.

### 🧹 Root Hygiene (888 Grade)
- **Entropy Reduction**: Cleared root directories of ad-hoc scripts, stale backups, and misplaced logs.
- **Canonical Grammar**: Enforced the `src/`, `specs/`, `docs/`, `tests/`, `data/`, `scripts/`, `archive/` directory structure.
- **Decommissioning**: Successfully archived technical debt (e.g., the root WEALTH monolith).

### 📖 Documentation Hardening
- **SOT READMEs**: Root READMEs across all repos have been rewritten as "Truth Sensors," linking to siblings and reflecting actual file system reality.
- **Agent Contracts**: Established `AGENT_LAYOUT_CONTRACT.md` and `NO_BANGANG_CHECKLIST.md` to prevent future "Stochastic Entropy."

### 🛡️ Organ Specifics
- **well**: Hardened `server.py` with multi-tier `state.json` resolution.
- **arifOS**: Standardized `arifosmcp` CLI entrypoints.
- **AAA**: Verified `npm` build/dev lifecycle.

---
*Ditempa Bukan Diberi — 999 SEAL ALIVE*
