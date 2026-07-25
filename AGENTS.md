# AGENTS.md — arifOS | arifOS Federation

> **DITEMPA BUKAN DIBERI**
> **Ω kernel — judges, seals, never executes.** F1-F13 run here. VAULT999 lives here.
> **Canonical AAA surface:** `/root/AAA/CLAUDE.md` · **Zen:** `/root/AAA/prompts/AAA-ZEN-ALIGNMENT.md`

## Identity

Constitutional kernel on :8088. MCP tools: `arif_init`, `arif_think`, `arif_judge`, `arif_observe`, `arif_route`, `arif_memory`, `arif_forge`, `arif_seal`. Chain: INIT → THINK → JUDGE → SEAL. A-FORGE executes after GO; VAULT999 records after SEAL.
Count is a runtime fact — verify with `tools/list`.

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
Canonical DID: `did:web:arifos.arif-fazil.com` — see `/root/arifOS/docs/CANONICAL_DID.md` and `arifosmcp.runtime.did_inventory`.
