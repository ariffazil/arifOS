# RECEIPT — M4 Repo Routing Validation Gate Fix · 2026-07-31

> **M4 of Kernel Hardening Sprint** — T1, fix the CI gate that never fires.

## WHAT WAS BROKEN

`.github/workflows/repo-routing-validation.yml` had TWO bugs:

**Bug 1 (the audit's finding)**: The validation loop used
`echo "$COMMITS" | while ... FAILED+=(...)`. The pipeline pipe runs
the `while` in a SUBSHELL — every variable mutation is lost when the
subshell exits, so the FAILED array was always empty and `exit 1` never
fired. The gate was decorative.

**Bug 2 (uncovered during synthetic testing)**: `git log --format='%H %B'`
returns one record per commit where the body is multi-line; `while read
sha body` only reads the first line of each body. So a commit with body
```
fix: clean commit
              <-- blank line
REPO=arifOS   <-- trailer
```
gets parsed as TWO fake "commits":
- line 1: sha=hash, body="fix: clean commit" → MISSING trailer
- line 2: sha="REPO=arifOS", body=empty → MISSING trailer

Both bugs were independently breaking.

## THE FIX

Restructured the loop body:

```bash
# OLD (broken): subshell + multi-line split
COMMITS=$(git log --format='%H %B' origin/main..HEAD)
echo "$COMMITS" | while IFS= read -r sha body; do ... FAILED+=(...) done

# NEW (works):
while IFS= read -r sha; do
    [ -z "$sha" ] && continue
    body=$(git log -1 --format='%B' "$sha")  # full multi-line body per commit
    if ! echo "$body" | grep -qi "^REPO="; then ... FAILED+=(...)
done < <(git rev-list origin/main..HEAD 2>/dev/null || git rev-list HEAD)
```

Two changes:
1. **Process substitution `< <(git rev-list ...)`** keeps the loop body in
   the main shell — FAILED persists across iterations.
2. **`git log -1 --format='%B'` per commit** fetches the full multi-line
   body attached to each hash — trailers stay with their commit.

## ACCEPTANCE — measured via synthetic local testing

The brief asks for CI run URLs; we did not push to GitHub Actions during
this sprint, so the equivalent is local synthetic runs with both planted
violations and clean trees.

| Test | Expected | Got |
|---|---|---|
| Planted violation (commit without REPO= trailer) | exit 1 | exit **1** ✓ |
| Clean tree (3 commits, all with valid REPO= trailers) | exit 0 | exit **0** ✓ |
| OLD gate on planted violation (regression proof) | would silently exit 0 | exit **0** (bug confirmed) |
| Per-commit body integrity (multi-line trailer preserved) | trailer recognized as part of parent commit | trailer correctly attributed ✓ |

## NOTES

The 18-commit "live MCP tools" pattern that comes from the M3 codegen
surfaced in a way unrelated to this gate — note that the workflow uses
`origin/main..HEAD` so on first-PR-on-no-main it falls back to
`git rev-list HEAD`. This is the same `set -euo pipefail` posture we use
in the kernel.

DITEMPA BUKAN DIBERI.
