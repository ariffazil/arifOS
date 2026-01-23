# archive_local

**STATUS: GITIGNORED / LOCAL ONLY**

This directory contains legacy directory trees from arifOS v46/v47 that have been consolidated into the single-body `arifos/` package in v49.

## Contents
- `arifos_core/`: Previous core logic (migrated to `arifos/`).
- `arifos_clip/`: Previous CLIP protocol (migrated to `arifos/protocol/`).
- `arifos_orchestrator/`: Previous orchestrator (migrated to `arifos/orchestrator/`).
- `sessions/`, `logs/`: Past session data.
- `WISDOM/`: Old knowledge base.
- `v49 staging/`: Temporary staging files.

## Policy
- **DO NOT COMMIT**: This directory is excluded from git.
- **REFERENCE ONLY**: Use these files to recover logic if missing from v49.
- **DEPRECATED**: Do not import from these paths in live code. Use `arifos` package.
