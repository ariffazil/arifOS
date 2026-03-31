# CIV-INFRA Creation Commands

## Step 1: Create GitHub Repository

Run these commands LOCALLY on your machine with GitHub CLI:

```bash
gh repo create ariffazil/CIV-INFRA --public --description "arifOS Infrastructure - VPS maps, playbooks, deployment docs"
```

Or create manually at: https://github.com/new
- Name: CIV-INFRA
- Description: arifOS Infrastructure
- Public

---

## Step 2: Initialize Git on VPS

Run on VPS as user ariffazil:

```bash
cd /home/ariffazil/CIV-INFRA

git init
git add -A
git commit -m "init: arifOS infrastructure documentation"
git remote add origin git@github.com:ariffazil/CIV-INFRA.git
git branch -M main
git push -u origin main
```

---

## Step 3: Verify

```bash
gh repo view ariffazil/CIV-INFRA
```

Or visit: https://github.com/ariffazil/CIV-INFRA

---

## Execution Order

1. Run `00_git_sync.sh` - verify all repos clean
2. Run `01_layout_prepare.sh` - create symlink structure
3. Create CIV-INFRA repo on GitHub
4. Push CIV-INFRA to GitHub
5. Later: Execute cleanup plan after review

---

## Files Generated

| File | Purpose |
|------|---------|
| `00_git_sync.sh` | Check all repos status |
| `01_layout_prepare.sh` | Create ~/arifOS/arifosmcp symlink |
| `CIV-INFRA/` | Infra repo skeleton |
| `CIV-INFRA-CREATE-COMMANDS.md` | This file |
