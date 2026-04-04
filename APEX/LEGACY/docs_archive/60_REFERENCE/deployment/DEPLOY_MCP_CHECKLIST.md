# MCP Deploy Checklist

Use this checklist for every VPS MCP rollout.

## Release Source

- Source branch: `main`
- Source commit: `3f1056b8`
- Rule: deploy only from exact commit SHA tagged for release

## Pre-Deploy Sanity

- [ ] `git status --short --branch` is reviewed
- [ ] deployment commit SHA matches approved `main` SHA
- [ ] no secrets or runtime `.env` values are committed
- [ ] `.venv313/` is not tracked going forward (keep virtual envs out of git)

## Canonical Tool Contract Check

- [ ] `tools/list` returns exactly 13 tools
- [ ] output matches `TOOLS_CANONICAL_13.md`
- [ ] stage semantics are canonical:
  - [ ] forge stage emits `777_EUREKA_FORGE`
  - [ ] judge stage emits `888_APEX_JUDGE`
- [ ] canonical IDs for 777/888 are exposed in `tools/list`:
  - [ ] `eureka_forge`
  - [ ] `apex_judge`

## Transport Verification (MCP Inspector)

Initialize:

```bash
npx -y @modelcontextprotocol/inspector --cli "http://127.0.0.1:8088/mcp" --transport http --method initialize
```

Tools list:

```bash
npx -y @modelcontextprotocol/inspector --cli "http://127.0.0.1:8088/mcp" --transport http --method tools/list
```

Tool calls:

```bash
npx -y @modelcontextprotocol/inspector --cli "http://127.0.0.1:8088/mcp" --transport http --method tools/call --tool-name anchor_session --tool-arg query="deploy-check" --tool-arg actor_id="ops"
npx -y @modelcontextprotocol/inspector --cli "http://127.0.0.1:8088/mcp" --transport http --method tools/call --tool-name eureka_forge --tool-arg 'action_payload={}' --tool-arg 'session_id="deploy-check"' --tool-arg 'signature="sig"'
npx -y @modelcontextprotocol/inspector --cli "http://127.0.0.1:8088/mcp" --transport http --method tools/call --tool-name apex_judge --tool-arg 'session_id="deploy-check"' --tool-arg 'query="judge check"'
```

Alias compatibility checks:

```bash
npx -y @modelcontextprotocol/inspector --cli "http://127.0.0.1:8088/mcp" --transport http --method tools/call --tool-name eureka_forge --tool-arg 'action_payload={}' --tool-arg 'session_id="deploy-check"' --tool-arg 'signature="sig"'
npx -y @modelcontextprotocol/inspector --cli "http://127.0.0.1:8088/mcp" --transport http --method tools/call --tool-name apex_judge --tool-arg 'session_id="deploy-check"' --tool-arg 'query="judge check"'
```

## Canonical ID Migration Gate

- [ ] canonical ID migration for 777/888 completed
- [ ] aliases verified via `tools/call` for deprecated IDs (`eureka_forge`, `apex_judge`)
- [ ] operator runbooks and docs reference canonical IDs first

## Rollback Readiness

- [ ] previous image tag captured before replace
- [ ] rollback command prepared and tested in dry-run form
- [ ] post-deploy verification fails => immediate rollback
