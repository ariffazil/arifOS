# arifOS VPS Deployment Readiness

This file is an operator runbook for agents deploying arifOS on a VPS.
It is not a proof that production is already updated.

## Canonical Layout

| Item | Canonical path |
|------|----------------|
| Git working tree | `/srv/arifosmcp` |
| Python virtualenv | `/srv/arifosmcp/.venv` |
| Governance secret directory | `/opt/arifos/secrets` |
| Governance secret file | `/opt/arifos/secrets/governance.secret` |
| Public MCP endpoint | `https://arifosmcp.arif-fazil.com/mcp` |
| Public docs contract | `https://arifos.arif-fazil.com/public-contract` |

## What Must Match Current arifOS Core

- Runtime entrypoint: `python -m arifosmcp.runtime http`
- Public tool contract: 8 tools from `arifosmcp/runtime/public_registry.py`
- Public transports: `http`, `stdio`
- Governance secret loading: `core/enforcement/auth_continuity.py` must read `ARIFOS_GOVERNANCE_SECRET_FILE`
- Compatibility shim: `aaa_mcp/rest.py` is legacy import support only, not a second public contract

## Required Preflight

Run on the VPS inside `/srv/arifosmcp`:

```bash
python scripts/generate_public_specs.py
python scripts/generate_public_contract_docs.py
ARIFOS_GOVERNANCE_SECRET_FILE=/opt/arifos/secrets/governance.secret \
  python scripts/verify-secrets.py
ARIFOS_GOVERNANCE_SECRET_FILE=/opt/arifos/secrets/governance.secret \
  pytest \
    tests/test_public_registry.py \
    tests/test_deploy_production.py \
    tests/test_runtime_prompts.py \
    tests/test_auth_continuity_file_secret.py \
    tests/test_runtime_capability_map.py \
    -q
```

## Deploy

Preferred:

```bash
sudo /srv/arifosmcp/scripts/deploy-production.sh
```

systemd path:

```bash
sudo cp /srv/arifosmcp/infrastructure/systemd/arifos-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable arifos-mcp
sudo systemctl restart arifos-mcp
```

Manual fallback:

```bash
cd /srv/arifosmcp
ARIFOS_GOVERNANCE_SECRET_FILE=/opt/arifos/secrets/governance.secret \
AAA_MCP_TRANSPORT=http \
python -m arifosmcp.runtime http
```

## Post-Deploy Checks

```bash
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/.well-known/mcp/server.json
curl -fsS http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

Expected:

- health version matches the deployed Git commit lineage
- discovery reports 8 public tools
- `tools/list` returns the 8-tool public contract
- no ephemeral-secret fallback is used

## Notes For Agents

- Do not infer deploy readiness from stale counts like `171/171` unless you reran them now.
- Do not deploy from `/opt/arifos` as the repo root; that path is for secrets/data, not code.
- Do not treat `aaa_mcp/tools.py` as the public contract. It is legacy compatibility only.
