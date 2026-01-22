---
name: arifos-workflow-000
master-version: "1.0.0"
master-source: .agent/workflows/000.md
description: Initialize arifOS session context. Use when the user types /000, asks to initialize the session, load canon/governance context, check current version, or summarize git status/branch/recent commits.
allowed-tools:
  - Read
  - Bash(cat:*)
  - Bash(git log:*)
  - Bash(git status:*)
  - Bash(git branch:*)
---

# /000 — Session Initialization (arifOS)

## Codex Integration

This skill uses the FAG (File Access Governance) system to safely read the canonical workflow from `.agent/workflows/000.md`.

### Multi-Workspace Support

Works from any subfolder - automatically detects repo root via `git rev-parse --show-toplevel`.

<!-- BEGIN CANONICAL WORKFLOW -->

# /000 - Session Initialization Protocol

This workflow sets up the complete context for an arifOS AGI coder session.

## Steps

// turbo-all

1. **Load System Canon**
   ```
   Read L1_THEORY/canon/ directory to load current system governance rules
   ```

2. **Check Version**
   ```bash
   cat pyproject.toml | grep version
   ```

3. **Review Recent Changes**
   ```bash
   git log -10 --oneline
   ```

4. **Check Git Status**
   ```bash
   git status
   ```

5. **Load AGENTS.md Context**
   ```
   Read AGENTS.md to understand multi-agent thermodynamic federation protocols
   ```

6. **Load GOVERNANCE_PROTOCOLS.md**
   ```
   Read GOVERNANCE_PROTOCOLS.md to understand fail-closed and SABAR-72 governance
   ```

7. **Check Active Branch**
   ```bash
   git branch --show-current
   ```

8. **Review CHANGELOG**
   ```
   Read CHANGELOG.md to understand recent system evolution
   ```

## Expected Output
- Current version: v43.x
- Active branch name
- Recent commit history
- Governance rules loaded
- System state understood

## Next Steps
After /000, typically run:
- `/gitforge` to analyze current branch entropy
- `/fag` to enter full autonomy governance mode

<!-- END CANONICAL WORKFLOW -->

## Codex-Specific Implementation

### Using FAG (File Access Governance)

The canonical workflow can be loaded via:
```bash
arifos-safe-read --path ".agent/workflows/000.md" --root "$(git rev-parse --show-toplevel)"
```

This ensures all file reads are governed and logged.

### Output Format

Return a concise checklist:
```
✅ Version: v45.0.0
✅ Branch: main
✅ Git status: clean
✅ Last 10 commits loaded
✅ Canon/governance context loaded

Recommendations: Run /gitforge, then /fag
```
