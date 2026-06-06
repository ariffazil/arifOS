# Repo working rules

Use this file before editing or running commands in federation repositories.

## Global rules

- Preserve user changes. Do not force-push, reset hard, delete unknown files, or overwrite local work.
- Do not mutate F1-F13, VAULT999, authority schemas, or deployment gates without explicit F13 approval.
- Do not expose secrets or commit runtime data.
- Avoid broad formatting churn.
- Treat execution as a state transition, not as text.
- Use smallest sufficient authority.
- Read before write; diff before patch; test before report.

## AAA

Typical verification:

```bash
npm install
npm run build
npm run validate:aaa
```

Main surfaces:

- `src/` cockpit UI.
- `a2a-server/` A2A gateway and AREP runtime.
- `public/a2a/` discovery surface.
- `agents/`, `registries/`, `schemas/` identity and contract registries.

AAA should not contain final constitutional judgment, domain calculators, or raw execution authority.

## arifOS

Typical verification:

```bash
python -m pytest tests/ -q --tb=short
ruff check .
make health
make sot-check
```

Main surfaces:

- `arifosmcp/` canonical MCP runtime.
- `core/` constitutional enforcement.
- `APEX/ASF1/tool_registry.json` registry surface.
- `FEDERATION_STATUS.md` cross-organ status.
- `AGENTS.md`, `CONSTITUTION`, `INVARIANTS` when present.

Escalate for floor changes, VAULT finalization, irreversible commands, production deployment, external comms, budget/capital allocation, and secret/auth changes.

## A-FORGE

Typical verification:

```bash
npm install
npm run build
curl http://localhost:7071/health
curl http://localhost:7071/api/federation-probe
```

A-FORGE may execute approved work but must not self-authorize irreversible or high-blast-radius actions.

## GEOX

Typical verification:

```bash
PYTHONPATH=src python -m pytest tests/ -q
ruff check src/
mypy src/geox_mcp/server.py
```

Return evidence, uncertainty, claim limits, and contradiction scans. Do not decide drilling or capital allocation.

## WEALTH

Typical verification:

```bash
pip install -e .
python internal/monolith.py
npm test
```

Expose assumptions, downside risk, and sensitivity. Do not allocate capital alone.

## WELL

Typical verification:

```bash
pip install -e .
python test_well.py
curl -s https://well.arif-fazil.com/health
```

Observe readiness and dignity risks. Do not diagnose, coerce, or override arifOS/F13.
