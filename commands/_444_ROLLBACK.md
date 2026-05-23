# scripts → commands CONSOLIDATION — ROLLBACK LOG
# SEAL: 444_ROUT-DITEMPA-BUKAN-DIBERI-20260523TXXXX
# Status: IN PROGRESS

## Pre-consolidation snapshot:
- commands/ had: arif_run.py, arif_exec.py, arif_sudo.py, arif-systemctl.py, *.md (9 files)
- scripts/ had: 41 files + hooks/ + native/ subdirs

## Migration plan:
1. commands/scripts_deploy/ — deployment/operational scripts moved here
2. commands/scripts_archive/ — CI/CD/audit scripts archived here
3. commands/native/ — native shell tools (native/sense.sh, wiki_query.sh)
4. commands/hooks/ — git hooks (hooks/install_hooks.sh, pre-push)

## Rollback: 
- cp -r commands/scripts_archive/ commands/scripts/ (restore)
- rm -rf commands/scripts_deploy/ commands/scripts_archive/

## Files NOT moved (stay in place):
- deploy/ directory (VPS deployment configs — separate from scripts/)
- infrastructure/ (systemd configs — separate)
