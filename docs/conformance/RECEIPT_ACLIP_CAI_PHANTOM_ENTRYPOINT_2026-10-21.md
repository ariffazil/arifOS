# RECEIPT — aclip-cai phantom console_script (P1 live defect)

Date: 2026-10-21 · Actor: claude-code-kvm8 (FI-002) · Lane: B (receipt, not SEAL)

## Claim
`aclip-cai` console_script points at a module that has never existed in git history.

## Evidence (OBS)
```
pyproject.toml:282   aclip-cai  = "arifosmcp.intelligence.cli:main"
$ ls arifosmcp/intelligence/
__init__.py  embeddings.py  thinking_session.py  tools  triad      # no cli.py
$ git log --diff-filter=D -- arifosmcp/intelligence/cli.py
(empty — never tracked, never deleted)
$ aclip-cai --help
ModuleNotFoundError: No module named 'arifosmcp.intelligence.cli'
$ which aclip-cai -> /usr/local/bin/aclip-cai (installed Sep 28)
```
`scripts/reachability_analysis.py` classifies this path as `CLI_ADAPTER / PRODUCTION_ROOT`
— a live entrypoint whose target does not exist. That is why the dead-code sweep kept
protecting it.

## Impact
- Any deployment using the `aclip-cai` console script fails at import.
- Reachability tooling over-counts one production root (phantom).

## Status
OPEN. Not fixed here — removing a declared entrypoint is a packaging decision
(publish-break risk if an external consumer calls it). Awaiting F13.

## Related
- `scripts/reachability_analysis.py:26` lists the phantom as a root; should be
  corrected or the entrypoint restored.
