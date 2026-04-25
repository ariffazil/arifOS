---
title: Start governed feature branch
description: Create a feature branch aligned with arifOS AAA naming and safety.
---

1. Ask user for a short feature name, e.g., "model-registry-init".
2. Normalize to kebab-case and prefix with `feat/`, e.g., `feat/model-registry-init`.
3. Ensure working tree is clean: if not, run `git status -sb` and ask user to commit or stash.
4. Run `git checkout main && git pull --rebase origin main`.
5. Run `git checkout -b <feature-branch-name>`.
6. Create or update a local notes file under `000/` describing:
   - Goal, Floors impacted, 888 HOLD conditions.
7. Summarize the new branch context for the user.
