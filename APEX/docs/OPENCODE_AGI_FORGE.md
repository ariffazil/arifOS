# OpenCode AGI Forge (VPS)

Status: SEALED baseline
Host: `72.62.71.199`
Operator: `ariffazil`
Primary workspace: `/srv/arifOS`

---

## 1) What Is Forged

- Clean global OpenCode config at `/home/ariffazil/.config/opencode/opencode.json`
- Project OpenCode config at `/srv/arifOS/.opencode/opencode.json`
- MCP wired to local AAA runtime (`arifos-aaa`)
- LSP wiring added for Python, TS/JS, YAML, JSON, Bash
- Skill directories forged globally and in-project
- Baseline custom tool scripts forged in `/srv/arifOS/tools`

---

## 2) Installed Toolbelt (LSP/CLI)

Installed globally (npm):

- `pyright`
- `typescript`
- `typescript-language-server`
- `eslint`
- `yaml-language-server`
- `vscode-langservers-extracted`
- `bash-language-server`

Installed system CLI:

- `zip`, `unzip`, `shellcheck`

---

## 3) Permission Model (Safe Forge)

Current model in OpenCode config:

- `read/edit/glob/grep/list`: `allow`
- `bash/task/external_directory`: `ask`
- `webfetch/websearch`: `allow`
- `skill` namespace rules:
  - `safe-*`: `allow`
  - `docs-*`: `allow`
  - `infra-*`: `ask`
  - `codebase-*`: `ask`
  - `danger-*`: `deny`

This supports infra and code forging while reducing brick risk.

---

## 4) MCP Layer

Configured server:

- `arifos-aaa` (local)
  - command: `bash -lc cd /srv/arifOS && /srv/arifOS/.venv/bin/python -m aaa_mcp stdio`
  - timeout: `20000`
  - env: `PYTHONPATH`, `ARIFOS_CONSTITUTIONAL_MODE=AAA`

Validation command:

```bash
opencode mcp list
```

Expected: `arifos-aaa connected`

---

## 5) Skills Forged

Global skills:

- `/home/ariffazil/.opencode/skills/infra-deploy/SKILL.md`
- `/home/ariffazil/.opencode/skills/codebase-refactor/SKILL.md`
- `/home/ariffazil/.opencode/skills/docs-update/SKILL.md`
- `/home/ariffazil/.opencode/skills/safe-inspect/SKILL.md`

Project skills:

- `/srv/arifOS/.opencode/skills/infra-deploy/SKILL.md`
- `/srv/arifOS/.opencode/skills/docs-update/SKILL.md`
- `/srv/arifOS/.opencode/skills/safe-inspect/SKILL.md`
- existing: `aaa-governance`, `thermo-ops`

---

## 6) Custom Tool Scripts Forged

- `/srv/arifOS/tools/infra_status.sh`
  - read-only machine/service status
- `/srv/arifOS/tools/backup_now.sh`
  - returns `888_HOLD` (explicit manual approval gate)
- `/srv/arifOS/tools/governance_log.py`
  - appends governance events to `VAULT999/opencode_governance.jsonl`

---

## 7) Verification Commands

```bash
ssh ariffazil@72.62.71.199
export PATH="$HOME/.local/bin:$PATH"
opencode debug config
opencode mcp list
command -v pyright-langserver
command -v typescript-language-server
command -v yaml-language-server
command -v vscode-json-language-server
command -v bash-language-server
/srv/arifOS/tools/infra_status.sh
```

---

## 8) Next Upgrade (Optional)

- Add local HTTP tools microservice (`/srv/opencode-tools-server`) and expose only on localhost.
- Register that service as an MCP endpoint when stable.
- Add per-service env sync (`master .env` -> `arifos.env`, `openclaw.env`, `agentzero.env`).

SEAL: 97% (OpenCode AGI baseline forged; HTTP tools server deferred by design)
