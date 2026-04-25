---
title: Safe sync local main with origin/main
description: Bring local arifOS main in line with remote KANON main without data loss, honoring AAA floors.
---

1. **000 INIT** — Run:
   - `git status -sb`
   - `git log origin/main..HEAD --oneline || echo "no local ahead commits"`
   - `git log HEAD..origin/main --oneline || echo "no remote ahead commits"`
   Summarize divergence in plain text.

2. **111 THINK** — Classify local changes by risk:
   - **F1**: docs/comments/config only.
   - **F2+**: code paths touching governance, floors, kernel manifests.

3. **333 EXPLORE** — If uncommitted work exists:
   - Ask user: "Stash (F1) or commit (F2+) before sync?"
   - If stash: run `git stash -u` and record stash id.
   - If commit: propose a conventional commit message and run `git commit`.

4. **555 HEART** — Check for Windows ghost files:
   - Scan for forbidden names like `nul` using PowerShell or `find`.
   - If found, stop and propose a cleanup script; mark **888 HOLD**.

5. **777 REASON** — Perform the sync:
   - Run `git fetch origin`.
   - Run `git rebase origin/main`.
   - If conflicts, list files and propose non-destructive resolution:
     - Prefer keeping remote truth for KANON canonical tool surface.
     - Preserve local model registry wiring where compatible.

6. **888 AUDIT** — After rebase:
   - Run `git status -sb`.
   - Run `pytest` or relevant test suite if configured.
   - Summarize net changes (files, risk level).

7. **999 SEAL** — DO NOT auto-push.
   - Present a one-paragraph summary and explicit command: `git push origin main`.
   - Require user to confirm before pushing.
