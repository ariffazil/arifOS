# Constitutional Git Worktree Toolchain

> **F1-F13 enforcement at the filesystem layer**

This toolchain implements constitutional governance for AI agent development using git worktrees as the enforcement mechanism.

## Quick Start

```bash
# Add to PATH
export PATH="$PATH:/mnt/arifos/scripts/constitutional-gitops"

# Create constitutional sandbox
arifos-worktree-add.sh claude mcp-hardening

# Enter and evaluate
cd ../arifos-worktrees/arifos-claude-mcp-hardening
arifos_f3_eval.py --worktree . --pr-draft

# Push if SEAL
git push origin feature/claude-mcp-hardening
```

## Tools

| Tool | Purpose | Floors |
|------|---------|--------|
| `arifos-worktree-add.sh` | Create F1 sandbox | F1, F2, F4, F11, F12 |
| `arifos-worktree-remove.sh` | Collapse → VOID | F1 |
| `arifos-agent-run.sh` | Agent runtime | F2, F7, F11 |
| `arifos-f3-eval.sh` | Tri-Witness (bash) | F3 |
| `arifos_f3_eval.py` | Tri-Witness (Python/PyPI) | F3 |

## Architecture

```
/mnt/arifos/                    # THE VAULT (main)
└── scripts/constitutional-gitops/   # This toolchain

/mnt/arifos-worktrees/          # Parallel universes
├── arifos-claude-*/            # Agent sandboxes
└── arifos-hotfix-*/            # F13 emergency
```

## F3 Tri-Witness

```
W₃ = (H × A × E)^(1/3)

H = Human witness (0.0-1.0)
A = AI witness (0.0-1.0)  
E = Earth witness (0.0-1.0)

Thresholds:
- low:     0.85
- medium:  0.95
- high:    0.99
- critical: 1.00 (requires H=1.0)
```

## Verdicts

| Verdict | W₃ Range | Action |
|---------|----------|--------|
| SEAL | ≥ threshold | Ready for merge |
| PROVISIONAL | threshold-0.1 | Proceed with reservations |
| HOLD | 0.5-0.7 | Needs more work |
| HOLD_888 | medium+ without human | F13 required |
| VOID | < 0.5 | Rejected |

## CI Integration

See `.github/workflows/888-judge.yml` — runs on every PR to main.

*Ditempa bukan diberi.*
