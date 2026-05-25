<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-05-25
valid_from: 2026-05-25
valid_until: 2026-06-25
confidence: high
scope: /root/arifOS
-->

# AGENTS.md — arifOS

> **Constitutional Intelligence Kernel**
>
> The law kernel of the arifOS Federation. arifOS structures decision; it does not decide.
> Constitutional judgment (SEAL / SABAR / VOID) and floor enforcement remain in arifOS.

## Mandatory Boot Sequence

1. Read `/root/AGENTS.md` (workspace-level federation rules)
2. Read `INVARIANTS.md`
3. Read `README.md`
4. Install: `pip install -e ".[dev]"` or `uv sync --extra dev`

## Allowed Actions

- Read, explore, organize, code, test, refactor
- Propose changes, create plans, draft documentation
- Work within the arifOS repo boundary
- Run `docker compose config`, health checks, diagnostics
- Update `memory/YYYY-MM-DD.md`, `CONTEXT.md`, `MEMORY.md`

## Forbidden Actions

- Issue SEAL / SABAR / VOID without human approval (F13 SOVEREIGN)
- Modify constitutional floors F1-F13 without explicit approval
- Force push, reset hard, overwrite unknown local changes
- Drop databases or delete data directories
- Mutate archived/read-only repos
- Perform broad formatting churn

## Verification Commands

```bash
python -m pytest tests/ -q --tb=short
ruff check .
ruff format .
make health
make sot-check
```

## Escalation Rules

- **888_HOLD:** Irreversible actions, git mutations, secret exposure, cross-repo architecture changes, production deployment without verified build + test pass
- **F13 SOVEREIGN (Arif):** Constitutional floor changes, new repo creation, external communications, budget/capital allocation

## Repo-Specific Notes

- Canonical MCP runtime lives in `arifosmcp/`
- Deepest constitutional enforcement lives in `core/`
- `arifosmcp/AGENTS.md` contains MCP-tool-specific guidance
