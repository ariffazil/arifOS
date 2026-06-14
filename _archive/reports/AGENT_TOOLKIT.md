# AGENT TERMINAL TOOLKIT — arifOS Federation

> **Authority:** 888 (Muhammad Arif bin Fazil, F13 SOVEREIGN)
> **Ratified:** 2026-06-04 by Omega (Ω)
> **Status:** CANONICAL — every agent MUST know these tools exist
> **Discovery:** run `agent-tools` from any terminal

## THE ONE RULE

> Read freely. Search freely. Write carefully. Delete never without permission.
> Every dangerous action requires explicit human approval (F1 AMANAH gate).

## HOW AGENTS DISCOVER THESE TOOLS

```bash
agent-tools              # list all 28 tools with versions
agent-tools --category   # organized by function
agent-tools --missing    # only show what's NOT in PATH
agent-tools probe        # test every tool (can it run?)
agent-tools --tldr <cmd> # quick usage examples for any tool
```

## MASTER INVENTORY (28 tools, all global PATH)

### FILE & CODE INTELLIGENCE (5)
```bash
rg 'pattern'              # ripgrep — grep but 10x faster, respects .gitignore
fzf                       # fuzzy finder — Ctrl+T files, Ctrl+R history, pipe anything
bat file.py               # cat with syntax highlighting, line numbers, git diff gutter
fd '*.py'                 # find but fast, smart defaults (fd, not fdfind)
tree -L 2                 # visualize directory structure
```

### VERSION CONTROL (2)
```bash
git                       # non-negotiable
gh pr create --title "x"  # GitHub CLI — PRs, issues, releases from terminal
```

### LANGUAGE RUNTIMES (4)
```bash
python3                   # Python 3.13
uv                        # fast Python package manager (pip replacement)
node --no-warnings        # Node.js 22
pnpm                      # fast Node package manager
```

### PROCESS & SYSTEM AWARENESS (9)
```bash
htop                      # interactive process monitor
btop                      # prettier htop alternative
curl -s http://host/health  # HTTP requests
http :8088/health         # httpie — curl but human-readable
jq '.key'                 # JSON parser — filter, transform, extract
yq '.key'                 # YAML equivalent of jq
socat TCP4-LISTEN:1234    # network swiss-army knife (SSL, pipes, proxies, PTY)
mlr --csv filter '$col>5' file.csv  # miller — jq for CSV/TSV/tabular data
nc -zv host port          # netcat — TCP/UDP probe
```

### CONTAINER & INFRA (1)
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}'  # container management
```

### SECRET & CONFIG SAFETY (1)
```bash
direnv allow              # auto-load .env per directory (add `source_env /root/.secrets/vault.env` to ~/.envrc)
```

### SANDBOX & AUDIT (3)
```bash
firejail --net=none cmd   # sandbox — run commands with no network, readonly fs, etc.
strace -p PID             # syscall tracer — debug what a process is actually doing
script session.log        # record terminal session for audit trail
```

### LOGS & DATA (4)
```bash
lnav /var/log/            # log file navigator — color, filter, merge multiple logs
ncdu /                    # interactive disk usage analyzer
sqlite3 db.sqlite 'SELECT * FROM t'  # lightweight SQL without Postgres
pandoc file.md -o file.pdf          # universal document converter
```

### PERFORMANCE (2)
```bash
parallel -j4 cmd ::: *.txt  # GNU Parallel — run jobs concurrently
hyperfine 'cmd1' 'cmd2'     # statistical benchmarking with warmup
```

### WATCHDOGS (3)
```bash
timeout 30 cmd            # kill command if it runs too long
watch -n5 'systemctl is-active arifos'  # repeat command every N seconds
echo *.py | entr -c pytest tests/       # auto-run when files change
```

### UTILITY (4)
```bash
ssh host                  # remote access
rsync -avz src/ dst/      # efficient file sync
xxd file.bin              # hex dump
lsof -i :8088             # what's using port 8088
pwdx PID                  # working directory of process
tldr tar                  # simplified man pages with working examples
```

## AGENTIC FLAGS — How agents call these tools

Every tool here supports non-interactive mode. Here's the pattern:

```bash
# NEVER do this (interactive, hangs):
htop
fzf
ncdu
docker ps

# ALWAYS do this (non-interactive, agentic):
htop --no-color --sort-key PERCENT_CPU -n 5
fzf --filter 'pattern' --no-sort
ncdu -0 -o /dev/stdout / | head -20
docker ps --format '{{.Names}} {{.Status}}'

# Shellcheck for safe scripting:
shellcheck script.sh     # always lint bash before execution

# Structured output for parsing:
jq -r '.items[] | [.name, .status] | @tsv' response.json
mlr --icsv --ojson cat data.csv
```

## FORBIDDEN PATTERNS (F1 AMANAH — agents must HALT)

```bash
# NEVER without explicit sovereign approval:
rm -rf /                 # F7 STEWARDSHIP HARAM
docker system prune -a   # irreversible container destruction
git push --force main    # force push to main
ufw deny 22              # lock yourself out of SSH
DROP TABLE               # database destruction
:(){ :|:& };:            # fork bomb
dd if=/dev/zero of=/dev/sda  # disk destruction
chmod -R 777 /etc        # permission catastrophe
```

## VERIFICATION

```bash
# Quick self-test — run this to confirm toolkit health:
agent-tools probe
```

**DITEMPA BUKAN DIBERI** — Forged, not given. Every tool here is earned, configured, and ready.
