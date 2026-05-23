# commands/ — Canonical Entrypoint Layer

> **SEAL:** 444_ROUT-DITEMPA-BUKAN-DIBERI-20260523
> **Authority:** arifOS 444 ROUT (Stage 444: Execution Operations)

## Purpose

`commands/` is the canonical entrypoint layer for arifOS. All operational
scripts, deployment tools, native commands, and git hooks are organized here.

**Before:** `scripts/` (41 files, flat, unorganized)
**After:** `commands/` (53 files, categorized, structured)

## Directory Structure

```
commands/
├── arif_run.py          # General shell command wrapper (canonical)
├── arif_exec.py         # Execution wrapper with constitutional gates
├── arif_sudo.py         # Privileged execution wrapper
├── arif-systemctl.py    # systemd control interface
├── audit.md             # Audit entrypoint
├── forge.md             # Forge entrypoint
├── init.md              # Init entrypoint
├── status.md            # Status entrypoint
├── scripts_deploy/      # Active deployment scripts (24 files)
├── scripts_archive/     # Archived audit/CI scripts (15 files)
├── native/              # Native shell tools (2 files)
└── hooks/              # Git hooks (3 files)
```

## Subdirectories

### scripts_deploy/ — Active Deployment Scripts
Operational scripts used in deployment pipelines.
- `arifos_install.sh` — Kernel installation
- `deploy-vps.sh` — VPS deployment
- `deploy_arifosmcp.sh` — MCP deploy
- `entrypoint-arifos.sh` — Container entrypoint
- `pre-deploy-check.sh` — Pre-deployment validation
- `mcp_inspector_verify.sh` — MCP tool inspection
- `verify_live.py`, `verify_public.py` — Deployment verification
- `rollback_service.sh` — Service rollback

### scripts_archive/ — Archived Audit/CI Scripts
Scripts for audit, CI, and maintenance. Less frequently used.
- `audit_sot.py` — Source of truth auditing
- `doctrine_diff_ci.py` — Doctrine CI pipeline
- `e2e_runner.py` — End-to-end testing
- `smoke_test.sh` — Smoke tests
- `test_all_mcp_tools.py` — Tool verification

### native/ — Native Shell Tools
Direct shell commands for the kernel.
- `sense.sh` — System sensing
- `wiki_query.sh` — Wiki queries

### hooks/ — Git Hooks
Git lifecycle hooks.
- `install_hooks.sh` — Hook installation
- `pre-push` — Pre-push validation

## Rollback

To rollback this consolidation:

```bash
# Restore scripts/
mkdir -p /workspace/arifOS/scripts
mv commands/scripts_deploy/* /workspace/arifOS/scripts/
mv commands/scripts_archive/* /workspace/arifOS/scripts/
mv commands/native/* /workspace/arifOS/scripts/native/
mv commands/hooks/* /workspace/arifOS/scripts/hooks/
rmdir commands/scripts_deploy commands/scripts_archive commands/native commands/hooks
```

## Note on deploy/ Directory

`commands/` is the canonical script layer. The `deploy/` directory is separate —
it contains Docker Compose files, Caddyfile, systemd configs, and infrastructure
as code for VPS deployment. These are different concerns.

**commands/**: Operational scripts (what to run)
**deploy/**: Infrastructure configs (where and how to run)

## Archive Consumption

scripts/ → commands/ consolidation was executed autonomously under 444 ROUT.
All 41 original scripts were moved, categorized, and preserved.
No files were deleted — only reorganized.

DITEMPA BUKAN DIBERI
