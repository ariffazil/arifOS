---
name: github-repo-manager
description: GitHub repository management — create, fork, settings, collaborators, topics, archive, transfer
user-invocable: true
---

# GitHub Repo Manager Skill

Triggers: "repo manager", "create repo", "fork repo", "repo settings", "collaborators", 
          "add collaborator", "topics", "archive repo", "transfer repo", "visibility"

Authenticated as: `ariffazil` via `GH_TOKEN` (gh CLI, HTTPS protocol)

---

## Create Repository

```bash
# Create new repo (gh will prompt for name, description, visibility)
gh repo create

# Create repo non-interactively
gh repo create my-new-repo \
  --public \
  --description "My new repository" \
  --clone

# Create with .gitignore and license
gh repo create my-new-repo \
  --private \
  --gitignore "Node" \
  --license "MIT" \
  --clone
```

Note: Creating a repo requires `--confirm` flag in automation. Prompt user before creating.

---

## Fork Repository

```bash
# Fork a repo to your account
gh repo fork owner/original-repo

# Fork and clone locally
gh repo fork owner/original-repo --clone

# List your forks
gh repo list --fork
```

---

## Repository Information

```bash
# View repo details
gh repo view ariffazil/arifOS

# View specific properties
gh repo view arifOS --json name,description,visibility,stargazerCount,defaultBranch

# List your repos
gh repo list --limit 20

# List repos by topic
gh search repo --topic "arifos" --owner ariffazil
```

---

## Settings

### Visibility

```bash
# Change visibility
gh repo set ariffazil/my-repo --visibility public
gh repo set ariffazil/my-repo --visibility private
gh repo set ariffazil/my-repo --visibility internal
```

### Default Branch

```bash
# Rename default branch
gh api -X PATCH repos/ariffazil/my-repo \
  -f name=my-repo \
  -f default_branch=main
```

---

## Collaborators & Teams

### Add Collaborator

```bash
# Add collaborator (via invite)
gh api -X PUT repos/ariffazil/my-repo/collaborators/username \
  -f permission=push

# Remove collaborator
gh api -X DELETE repos/ariffazil/my-repo/collaborators/username
```

### Permission Levels

| Permission | Description |
|------------|-------------|
| `pull` | Read-only |
| `push` | Push access |
| `admin` | Full admin |
| `maintain` | Write + branch management |
| `triage` | Issue/PR management |

### List Collaborators

```bash
gh api repos/ariffazil/my-repo/collaborators | jq '.[].login'
gh api repos/ariffazil/my-repo/outside_collaborators | jq '.[].login'
```

---

## Topics

```bash
# Add topics
gh api -X PUT repos/ariffazil/my-repo/topics/my-topic -f names[]=arifOS

# List topics
gh api repos/ariffazil/my-repo/topics | jq '.names[]'

# Replace all topics
gh api -X PUT repos/ariffazil/my-repo/topics \
  -f names:='["arifOS", "constitutional-ai", "agi"]'
```

---

## Archive / Unarchive

```bash
# Archive repository
gh api -X PATCH repos/ariffazil/my-repo \
  -f archived=true

# Unarchive
gh api -X PATCH repos/ariffazil/my-repo \
  -f archived=false
```

---

## Transfer Ownership

```bash
# Transfer to new owner/organization
gh api -X POST repos/ariffazil/my-repo/transfer \
  -f new_owner=organization-name
```

Note: Requires confirming access to both source and target accounts.

---

## Delete Repository

```bash
# Delete repo (requires confirmation)
gh repo delete ariffazil/my-repo --confirm
```

⚠️ **Warning**: Deletion is irreversible. Always confirm with user first.

---

## Protected Branches

```bash
# Get branch protection
gh api repos/ariffazil/arifOS/branches/main/protection

# Require PR reviews
gh api -X PUT repos/ariffazil/arifOS/branches/main/protection/required_pull_request_reviews \
  -f required_approving_review_count=2

# Require status checks
gh api -X PUT repos/ariffazil/arifOS/branches/main/protection/required_status_checks \
  -f contexts:='["ci/test", "build/deploy"]'
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Create repo | `gh repo create` |
| Fork repo | `gh repo fork owner/repo` |
| View details | `gh repo view owner/repo` |
| List repos | `gh repo list` |
| Set visibility | `gh repo set owner/repo --visibility private` |
| Add collaborator | `gh api -X PUT ...` |
| Add topics | `gh api -X PUT .../topics` |
| Archive | `gh api -X PATCH ... -f archived=true` |
| Delete | `gh repo delete owner/repo --confirm` |

---

## Constitution Note (F1/F11)

- Creating and forking repos are **safe** operations.
- Deleting repos requires explicit user confirmation with --confirm flag.
- Transfer requires F13 if moving to a different organization.

*arifOS_bot — GitHub Repo Manager via gh CLI*