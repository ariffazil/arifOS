# Repo + MCP Stabilization Runbook

Version: 2026.05.11
Owner: Arif

## Doctrine

Clarity before capability.
Constraint before scale.
Governance before automation.

## Branch Truth Model

- `main`: production truth
- `dev`: integration/staging
- `feature/*`: disposable work branches
- `hotfix/*`: emergency reversible patches

Rules:
- No long-lived experimental chains.
- No stacked ambiguous final branches.
- Direct pushes to `main` are exception paths and must be acknowledged.

## Pull Request Hygiene

Run weekly or before release:

```bash
gh pr list --state open
gh pr close <id> --comment "superseded by #<new-pr>"
```

Close immediately if PR is obsolete, superseded, partially merged, or architecturally invalid.

## Hook Severity Ladder

- `INFO`: log only
- `WARN`: allow push
- `HOLD`: require explicit acknowledgment
- `BLOCK`: stop push

`BLOCK` is reserved for:
- potential secrets
- malformed governance JSON (`*charter*.json`, `*manifest*.json`)
- deleted safety-critical tests

`HOLD` covers governance friction:
- direct push to `main`
- missing/mismatched `REPO=<owner/repo>` trailer on main pushes

Ack override for `HOLD`:

```bash
ARIFOS_HOLD_ACK=1 git push origin main
```

## MCP Server Constraint Model

Treat servers as infrastructure with explicit ownership:
- `arifOSLocal`: consequential/local execution, canonical trusted path
- `arifOSPublic`: governed remote reference/read paths
- `openaiDeveloperDocs`: OpenAI/Codex docs retrieval only

Capability tiers:
- `T0`: read/log
- `T1`: local reversible
- `T2`: repo mutation
- `T3`: deployment
- `T4`: irreversible

Rules:
- one irreversible capability owner
- one route
- one audit trail
- dry-run by default for dangerous operations

## Weekly Hygiene Checklist (30-45 min)

- [ ] close stale PRs
- [ ] archive dead branches
- [ ] review failed workflows
- [ ] rotate/revoke old tokens
- [ ] inspect hook findings (`INFO/WARN/HOLD/BLOCK`)
- [ ] update governance docs
- [ ] remove duplicate scripts
- [ ] collapse redundant MCP configs

## Install and Use Guarded Pre-Push Hook

```bash
bash scripts/hooks/install_hooks.sh
```

The installed pre-push hook delegates to:
- `scripts/hooks/pre-push/repo_guard.py`

## 7-Day Stabilization Sprint

- Day 1: close stale PRs + delete dead branches
- Day 2: enforce severity pre-push guard
- Day 3: audit secrets/tokens
- Day 4: map MCP ownership and trust boundaries
- Day 5: remove duplicate capability overlap
- Day 6: review observability and trace lineage
- Day 7: freeze architecture and update docs
