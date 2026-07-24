# AGENTS.md — arifOS | arifOS Federation

> **Ω kernel — judges, seals, never executes.** F1-F13 run here. VAULT999 lives here.

## Identity

Constitutional kernel on :8088. Six MCP tools: `arif_init`, `arif_think`, `arif_judge`, `arif_observe`, `arif_seal`, `arif_memory`. The chain: INIT → THINK → JUDGE → SEAL. A-FORGE executes after GO; VAULT999 records after SEAL.

## Build & Test

```bash
uv sync --frozen
ruff check . && ruff format .
pytest tests/ -q --tb=short
make deploy-local   # rsync → /opt/arifos/app + systemctl restart arifos
make prove          # 10/10 gates
curl :8088/health
```

F1-F13 canon: `/root/arifOS/GENESIS/000_KERNEL_CANON.md` and `/root/arifOS/GENESIS/FLOOR_TABLE.json`
