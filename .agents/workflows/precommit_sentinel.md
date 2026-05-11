---
title: Pre-commit sentinel check
description: Run 3-question check before any commit on arifOS.
---

1. Show `git diff --stat` and `git status -sb`.
2. Ask and answer:
   - **Q1**: Critical paths modified? (governance_kernel, floors, manifests, tools)
   - **Q2**: README / registry / code drift introduced?
   - **Q3**: Any invariant violations or TODO markers left in?
3. If any answer is **yes/uncertain**:
   - Propose splitting the changes into smaller commits.
   - Mark commit as **F2+** and append `[risk]` tag in message.
4. Only then propose a structured commit message following your house style.
