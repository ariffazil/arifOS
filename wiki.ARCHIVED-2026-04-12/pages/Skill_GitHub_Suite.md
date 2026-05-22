---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- devops
- git
audience:
- engineers
- operators
- researchers
difficulty: intermediate
prerequisites:
- MCP_Tools
- Skill_Docker_Management
tags:
- github
- git
- repositories
- pull-requests
- code-review
- ci-cd
- releases
- secrets
- pygount
sources:
- Hermes bundled skills: github-repo-management, github-auth, github-pr-workflow, github-code-review, github-issues, codebase-inspection
- GitHub CLI docs: https://cli.github.com
- pygount docs: https://pygount.readthedocs.io
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: GitHub Suite

The **GitHub Suite** is the canonical code collaboration toolkit for the arifOS Federation. It covers repository management, authentication, PR workflows, code review, issue tracking, and codebase inspection — all available via the `gh` CLI, native `git`, and the GitHub REST API.

## Purpose

To give every federation agent the ability to:
- Clone, create, fork, and manage repositories
- Authenticate with GitHub securely
- Open, review, and merge pull requests
- Review code locally and on GitHub
- Manage issues and releases
- Inspect codebase metrics (LOC, languages, ratios)

## Specifications

- **Stage**: 010 (Forge) + 111 (Sensing)
- **Layer**: CODE
- **Trinity**: Δ (Mind — structured execution against code reality)
- **Floors touched most directly**: F1 (Amanah — destructive git ops require hold), F11 (Audit — all commits tracked), F8 (Guardrails — branch protection, secret scanning)

## Authentication

**Already configured on this VPS:**
- **gh CLI**: Authenticated as `ariffazil`
- **Token scopes**: `repo`, `workflow`, `gist`, `read:org`, `write:packages`
- **Token location**: `/root/.config/gh/hosts.yml`
- **Git identity**: `arifOS_bot <arifOS_bot@arif-fazil.com>`

**Verify status:**
```bash
gh auth status
```

**Fallback auth (without gh):**
```bash
# Read token from gh config
export GITHUB_TOKEN=$(yq '.["github.com"].oauth_token' ~/.config/gh/hosts.yml)

# Or use git credential helper
git config --global credential.helper store
git ls-remote https://github.com/ariffazil/arifos.git
```

## 1. Repository Management

### Clone
```bash
# Via gh
gh repo clone ariffazil/arifos

# Via git
git clone https://github.com/ariffazil/arifos.git

# Shallow clone (faster)
git clone --depth 1 https://github.com/ariffazil/arifos.git
```

### Create
```bash
# Public repo + clone
gh repo create my-project --public --clone

# Private, with description and license
gh repo create my-project --private --description "A useful tool" --license MIT --clone

# Under organization
gh repo create my-org/my-project --public --clone
```

### Fork
```bash
gh repo fork owner/repo-name --clone
git remote add upstream https://github.com/owner/repo-name.git
```

### Settings
```bash
gh repo edit --description "Updated description" --visibility public
gh repo edit --enable-wiki=false --enable-issues=true
gh repo edit --default-branch main
gh repo edit --add-topic "machine-learning,python"
```

## 2. PR Workflow

### Branch and commit
```bash
git checkout main && git pull origin main
git checkout -b feat/add-feature

# Make changes, then commit
git add src/feature.py tests/test_feature.py
git commit -m "feat: add new feature

- Implements X
- Adds tests for Y

Closes #42"
```

### Push and create PR
```bash
git push -u origin HEAD

gh pr create \
  --title "feat: add new feature" \
  --body "## Summary
Implements X and Y.

Closes #42" \
  --label "enhancement"
```

### Monitor CI
```bash
gh pr checks
gh pr checks --watch
```

### Merge
```bash
# Squash merge + delete branch
gh pr merge --squash --delete-branch

# Auto-merge when checks pass
gh pr merge --auto --squash --delete-branch
```

## 3. Code Review

### Review local changes (pre-push)
```bash
git diff main...HEAD --stat
git diff main...HEAD

# Check for common issues
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|debugger"
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*="
```

### Review a PR on GitHub
```bash
# View PR details and diff
gh pr view 123
gh pr diff 123

# Check out locally for full review
gh pr checkout 123

# Run tests and linters
python -m pytest 2>&1 | tail -20
ruff check . 2>&1 | head -30

# Submit review
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
```

### Inline comments
```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')

gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="Use parameterized queries here." \
  -f path="src/auth.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```

## 4. Releases

```bash
# Create release with auto-generated notes
gh release create v1.0.0 --title "v1.0.0" --generate-notes

# Draft prerelease
gh release create v2.0.0-rc1 --draft --prerelease --generate-notes

# List and download
gh release list
gh release download v1.0.0 --dir ./downloads
```

## 5. Secrets & Actions

```bash
# Set repository secrets
gh secret set API_KEY --body "your-secret-value"
gh secret set SSH_KEY < ~/.ssh/id_rsa
gh secret list

# List workflows and runs
gh workflow list
gh run list --limit 10
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID> --failed
```

## 6. Codebase Inspection (pygount)

**Installed**: `/usr/local/bin/pygount`

```bash
# Full language breakdown
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,__pycache__,.cache,dist,build,.next,.tox,.eggs" \
  .

# Specific language only
pygount --suffix=py --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Top 20 files by code lines
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

**Summary columns:**
| Column | Meaning |
| :--- | :--- |
| Language | Detected programming language |
| Files | Number of files |
| Code | Lines of actual code |
| Comment | Lines of comments/documentation |
| % | Percentage of total |

## Federation Context

- **Hermes**: All GitHub skills are bundled by default in `~/.hermes/skills/github/`
- **gh CLI**: v2.46.0 installed at `/usr/bin/gh`, authenticated as `ariffazil`
- **pygount**: v3.2.0 installed at `/usr/local/bin/pygount`
- **A-FORGE / arifOS**: Can invoke `git`, `gh`, `pygount` via ShellTool
- **Git identity**: `arifOS_bot <arifOS_bot@arif-fazil.com>`

## Commit Trailer Rule

Several federation repos enforce a `REPO=<target-repo>` trailer in every commit message. Check `.github/workflows/repo-routing-validation.yml` before committing.

Example:
```bash
git commit -m "fix: resolve auth edge case

REPO=ariffazil/arifos"
```

## Pitfalls

| Problem | Fix |
| :--- | :--- |
| `gh auth status` shows not logged in | Run `gh auth login` or set `GITHUB_TOKEN` |
| `git push` asks for password | Use PAT as password, not GitHub password |
| Permission denied | Check token scopes; regenerate with `repo` scope |
| pygount hangs | Always use `--folders-to-skip` to exclude `node_modules`, `.git`, `venv` |
| Markdown shows 0 code lines | Expected — pygount classifies Markdown as comments |
| Large monorepos slow | Use `--suffix` to target specific languages |

## Related

- [[Skill_Docker_Management]] (Container ops for CI/CD)
- [[Skill_MCP_Mcporter]] (MCP mesh CLI)
- [[MCP_Tools]] (Tool surface architecture)
- [[Audit_Repo_Chaos_Reduction]] (Pass 1 Audit — 378 active docs classified)
