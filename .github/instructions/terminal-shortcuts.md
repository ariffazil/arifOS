# Terminal Shortcuts — arifOS Workstation

The user (Arif) has custom PowerShell shortcuts in their profile (`~/.arifos-profile.ps1`).
When suggesting terminal navigation or project switching, **prefer these shortcuts** over raw `cd` commands.

## Project Navigation

| Shortcut | Destination | Use When |
|----------|-------------|----------|
| `arifos` | `C:\ariffazil\arifOS` | Switch to main arifOS repo |
| `arifosmcp` | `C:\ariffazil\arifOS\arifosmcp` | Switch to MCP server subproject |
| `a-forge` | `C:\ariffazil\A-FORGE` + loads `.env` | Switch to A-FORGE agent workspace |
| `aforge-dir` | Same as `a-forge` | Alias for A-FORGE directory |
| `docc` | `C:\ariffazil\arifOS\docs` | Switch to docs directory |

## Virtual Environment

| Shortcut | Action |
|----------|--------|
| `venvon` | Activate arifOS `.venv` |
| `venvoff` | Deactivate current venv |

Note: The arifOS venv auto-activates when opening a terminal inside `C:\ariffazil\arifOS` or its children.

## VPS Access

| Shortcut | Action |
|----------|--------|
| `vps` | SSH to `af-forge` VPS as `ariffazil`, then `sudo -i` to root |
| `vps-tunnel` | Open SSH tunnels (Redis 6379, Postgres 5432) to VPS in background |
| `vps-tunnel-stop` | Kill all VPS tunnel processes |

The SSH key (`~/.ssh/id_ed25519`) is cached in `ssh-agent`. `vps` works without passphrase prompts after `ssh-add` has been run once per Windows session.

## Git Shortcuts

| Shortcut | Action |
|----------|--------|
| `gs` | `git status` |
| `gp` | `git pull` |
| `gc "msg"` | `git commit -m "msg"` |
| `gd` | `git diff` |
| `gl` | `git log --oneline -15` |

## MCP / Runtime

| Shortcut | Action |
|----------|--------|
| `Start-MCP` | Start arifOS MCP stdio server |
| `Start-MCP-HTTP` | Start arifOS MCP HTTP server |
| `Start-AForge` | Switch to A-FORGE and `npm start` |
| `Start-AForge-MCP` | Switch to A-FORGE and `npm run mcp:stdio` |

## Testing / Linting

| Shortcut | Action |
|----------|--------|
| `Test-All` | `pytest tests/ -v` |
| `Test-Quick` | `pytest tests/test_quick.py -v` |
| `Test-Const` | `pytest -m "constitutional" -v` |
| `Lint-MCP` | `ruff check arifosmcp/` |
| `Fix-MCP` | `ruff check arifosmcp/ --fix` |

## VS Code Terminal Profiles

The user also has VS Code terminal profiles for one-click access:

| Profile | Action |
|---------|--------|
| **arifOS** | PowerShell 7, cd to `C:\ariffazil\arifOS`, auto-activate `.venv` |
| **arifOS MCP** | PowerShell 7, cd to `C:\arifosmcp`, auto-activate `.venv` |
| **VPS (af-forge)** | SSH as `ariffazil` to Ubuntu VPS |
| **VPS (af-forge root)** | SSH + `sudo -i` straight to root |
| **VPS (Hostinger)** | SSH to Hostinger server (port 22888) |
| **Git Bash** | Unix tools locally |

## Agent Guidance

- When the user says "go to the MCP server" or "switch to MCP", suggest `arifosmcp` (not `cd arifosmcp`).
- When the user says "go to A-FORGE" or "agent forge", suggest `a-forge` (not `cd A-FORGE`).
- When the user says "VPS" or "server" or "remote", suggest `vps` (not manual SSH commands).
- When the user says "tunnel" or "Redis" or "Postgres", suggest `vps-tunnel` and `vps-tunnel-stop`.
- These shortcuts exist to reduce chaos — use them.
