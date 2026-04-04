# AAA MCP Hardening Baseline

Date: 2026-02-27
Scope: arifOS node at `/root/arifOS`

## Current Baseline

- Canonical repo path: `/root/arifOS`
- GitHub origin: `https://github.com/ariffazil/arifos.git`
- OpenCode project config: `opencode.json`
- AAA MCP mode: local stdio (`/root/arifOS/.venv/bin/python -m arifos_aaa_mcp stdio`)
- MCP enabled: `true`
- Skills detected: `aaa-governance`, `thermo-ops`
- Agents detected: `arif-architect`, `devops-builder`, `recon-researcher`, `arifos-forge-agent.prompt`

## Hardening Completed

1. Removed alias drift
   - Removed `/root/arifos` symlink.
   - Canonicalized to `/root/arifOS` only.

2. Sanitized git remote URL
   - Replaced tokenized URL with tokenless HTTPS:
   - `origin https://github.com/ariffazil/arifos.git`

## Immediate Hardening Recommendations

1. OpenCode permission tightening
   - Current root permission is very broad (`"*": "allow"`).
   - Move to least-privilege defaults and grant extra permissions at agent level.

2. Separate kernel defaults vs node-local state
   - Decide whether `.opencode/agents`, `.opencode/skills`, and `opencode.json` are:
     - canonical repo assets (commit and review), or
     - node-local runtime config (ignore from git).
   - Keep only one policy to avoid governance drift.

3. Keep L4 docs synced to runtime truth
   - Tool counts and naming differ across docs.
   - Source-of-truth should be `aaa_mcp/server.py` tool registrations.

## Drift Check Commands

Use these to verify baseline integrity quickly:

```bash
git -C /root/arifOS remote -v
git -C /root/arifOS status --short --branch
opencode debug config
opencode debug skill
```

## Notes

- For irreversible actions (production deployment, destructive data ops, history rewrite), enforce `888 HOLD` with explicit human approval.
- Keep changes small and reversible; prefer additive docs and tests before behavior changes.
