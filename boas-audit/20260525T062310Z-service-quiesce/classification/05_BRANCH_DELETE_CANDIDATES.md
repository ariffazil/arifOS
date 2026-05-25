# BRANCH_DELETE_CANDIDATES.md
**Mission:** Identify stale merged branches safe to delete.
**Date:** 2026-05-25
**Rule:** Do NOT delete without explicit Arif approval.

---

## Merged Branches in arifOS

| Branch | Merged Into | Last Commit | Age | Safe to Delete? | Reason |
|--------|-------------|-------------|-----|-----------------|--------|
| `arifOS/sync-repo-routing-2026-05-02` | main | 2026-05-02 | 23d | **YES** | Old routing sync, superseded |
| `arifos/repo-routing-2026-05-02` | main | 2026-05-02 | 23d | **YES** | Old routing sync, superseded |
| `chore/repo-hygiene-arifos-20260521` | main | 2026-05-21 | 4d | **YES** | Repo hygiene, merged |
| `docs/mcp-endpoint-registry` | main | ? | ? | **REVIEW** | May contain docs still needed |
| `feat/repo-routing-validation-2026-05-02` | main | 2026-05-02 | 23d | **YES** | Old routing validation |
| `feature/components` | main | ? | ? | **REVIEW** | May be referenced |
| `forensic-gemini-wisdom-breach-20260426-073938` | main | 2026-04-26 | 29d | **YES** | Forensics complete |
| `h1-roadmap-1778019150` | main | ? | ? | **YES** | Roadmap artifact |
| `h1-roadmap-1778019163` | main | ? | ? | **YES** | Roadmap artifact |
| `hermes-forge/step1-kernel-bridge` | main | ? | ? | **REVIEW** | May be part of Hermes work |
| `memory-fix` | main | ? | ? | **REVIEW** | Check if memory fix is still active |

**Total merged branches:** 12 identified
**Safe to delete (preliminary):** 7
**Needs review:** 5

---

## Do NOT Delete (protect these)

| Branch | Reason |
|--------|--------|
| `main` | Protected |
| Any branch with unmerged work | Check with `git log --not --oneline main` |
| `apex` (if exists) | APEX lives on apex branch |
| `hermes-*` branches | Hermes ASI work — needs hermes-ops review |

---

## Delete Commands (once approved)

```bash
cd /root/arifOS

# Dry run (safe):
git branch --merged main | grep -v "^\*" | xargs -n1 echo "Would delete:"

# Execute (after approval):
git branch --merged main | grep -v "^\*" | xargs -n1 git branch -d
```

**Branch protection rule:** Never `git branch -D` on merged branches. Use `-d` (safe delete).

---

## Risks

- `docs/mcp-endpoint-registry` — may contain endpoint documentation still referenced
- `feature/components` — may be referenced in AAA or other repos
- `hermes-forge/step1-kernel-bridge` — Hermes work may depend on this
- `memory-fix` — if memory fix is live, deleting branch is fine; if not, needs verification

**Recommendation:** Request Arif approval for the 7 clear "YES" candidates. Hold the 5 "REVIEW" candidates for a follow-up pass.

---

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
