# RECEIPT — M7 Credential Incident Containment · 2026-07-31

> **Mission:** M7 — Credential incident containment (P0 finding from M6 review)
> **Authority:** READ_ONLY + REVERSIBLE_LOCAL_PREP only.
> **STOP:** Rotation, deployment, history rewrite, VAULT seal — ALL require explicit F13 acknowledgement tokens.

## P0 FINDING (UNCHANGED)

A live PostgreSQL credential was included in the M1 receipt (committed in
this kernel tree as `docs/receipts/M1-postgres-auth-repair-20260731.md`,
landed in commit `4daeb9185` as part of the M2 commit bundle). That
credential is **still active** on the live `arifos_admin` role in the
docker postgres backend at `127.0.0.1:5432`.

**Verdict per the brief: P0_CREDENTIAL_COMPROMISE.**

The credential is **not reproduced** in this receipt. SHA-256 fingerprint
and length are recorded; line numbers and file paths only.

## FINGERPRINT (REDACTED)

| Field | Value (redacted) |
|---|---|
| Prefix (first 8 chars) | `ArifPost` |
| Length | 17 chars |
| SHA-256 | `ea9d5278124cbb48...7cf7375ec62a6ede` (truncated; full hash on request via `python3 -c "..."` with heredoc, never argv) |
| Active? | **YES** — postgres accepts it as the `arifos_admin` password |
| Rotation required? | **YES** (P0) |
| Rotation executed? | **NO** — awaiting `ACK_M7_ROTATE_DB_SECRET` |

## EXPOSURE LOCATIONS

| Location | Exposure class | Tracked? | Published? | Secret active? | Required response |
|---|---|---|---|---|---|
| `docs/receipts/M1-postgres-auth-repair-20260731.md` (M1 receipt) | LOCAL_GIT_HISTORY | YES (in `4daeb9185` via `git add -A` in M2 commit bundle) | YES (in repo; never pushed to remote in this sprint) | YES | Redact in new commit + new receipt; rotate secret |
| `deploy/rollback/20260729-100111/ingress_middleware.py` | LOCAL_FILE | NO (rollback archive, not in git) | NO | YES (this is an OLD credential reference in a HISTORICAL rollback snapshot) | Archive snapshot — already historical; rotation supersedes it |
| `build/lib/arifosmcp/runtime/ingress_middleware.py` | LOCAL_FILE | NO (build artefact, .gitignore'd) | NO | YES | Regenerate `build/` after rotation |
| `/root/.secrets/vault.flat.env` (POSTGRES_PASSWORD line) | LOCAL_FILE | NO (secrets are gitignored, mode 600) | NO | YES | This is the canonical secret source — must be updated atomically with the role rotation |
| `/root/.secrets/.env.postgres` | LOCAL_FILE | NO (mode 600) | NO | YES | Same — canonical source |
| `/root/.secrets/INDEX.md` and other registry files (40 files contain string under `/root/.secrets/`) | LOCAL_FILE | NO (mode 600) | NO | YES | Rotate canonical source; secondary references will need re-pinning but are not the source of truth |
| `/root/backups/` (3 files) | BACKUP | NO (backups are out-of-tree) | NO | YES | Rotation invalidates old backups; document post-rotation |
| `/tmp/hermes-snap-*.sh` (4 files) | TEMP_FILE | NO | NO | YES | Wipe `/tmp` after rotation; hermes snapshots re-create on next capture |
| `/tmp/state.db.bak` | TEMP_FILE | NO | NO | YES | Wipe after rotation |
| `/proc/<arifOS-pid>/environ` (POSTGRES_PASSWORD ×2 vars) | ACTIVE_RUNTIME_ONLY | n/a (process memory) | n/a | YES | Process env re-read after restart with new password; old env dies with old process |
| Agent session transcript (this conversation) | AGENT_TRANSCRIPT | n/a | n/a | YES | Cannot unprint; rotation supersedes |
| `journalctl -u arifos` (last 1 hour) | LOG | NO | NO | NO new entries | Confirmed: no POSTGRES_PASSWORD= leaks; no auth-success entries contain the password |
| `/root/.bash_history` | SHELL_HISTORY | n/a | NO | n/a | 0 lines mentioning psql/arifos_admin/POSTGRES — history is clean (PASSWORD was set via inline `PGPASSWORD=...` env, not on argv) |

## GIT HISTORY EXPOSURE (DETAILED)

`git log --all --source -p -S '<redacted fingerprint>'` reports **14 commits**
in HEAD whose diffs contain the literal credential value. These include:

- M1 receipt commit (`4daeb9185`, bundled with M2 fix) — **LOCAL_GIT_HISTORY exposure** but never pushed to remote in this sprint.
- Historical commits predating the M1 receipt (rollback snapshots, prior rollouts) — already in local git history.

**Constraint:** "If the credential exists in remote Git history, do not rewrite history automatically."

**Status:** The credential has NOT been pushed to remote in this sprint.
The local git history contains it (P0_CREDENTIAL_COMPROMISE for local
clone), but no remote exposure has been introduced by the M7–M11
sprint. **No history rewrite required at this time.**

## ROTATION PLAN (PREPARED, NOT EXECUTED)

A coordinated rotation is prepared but **BLOCKED on `ACK_M7_ROTATE_DB_SECRET`**.
When acknowledged, the rotation will execute in this order:

1. **Generate replacement:** `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
   → stored in a transient shell variable, never echoed to a file.
2. **Update postgres role:** `ALTER USER arifos_admin WITH PASSWORD '<new>';`
   via `docker exec -u <superuser> postgres psql -d vault999` inside the container.
3. **Update canonical secret source:** `vault.flat.env` `POSTGRES_PASSWORD=<new>` —
   ONLY this file. No documentation touched.
4. **No documentation update:** per the brief, "updates no documentation with the value."
5. **Restart dependent services:** `sudo systemctl restart arifos` (one service, 10s window).
6. **Verify:** `psql -h 127.0.0.1 -U arifos_admin -d vault999 -c "SELECT 1;"` using new password from env.
7. **Verify arif_observe:** MCP `tools/call` against `arif_observe` returns structured substrate data.
8. **Zero new auth failures:** `journalctl -u arifos --since "2 min ago" | grep -c "password authentication failed"` = 0.
9. **Old credential rejected:** `psql -h 127.0.0.1 -U arifos_admin -d vault999 -c "SELECT 1;"` using OLD password → FATAL.
10. **Record only fingerprints:** new M7-rotation-completed receipt contains only SHA-256 of new password + timestamp + PID.

**Old credential retention:** **NO.** Per the brief, the old credential is NOT preserved in any receipt. Its fingerprint (SHA-256) is the only durable reference.

## HISTORY REWRITE PLAN (PREPARED, NOT EXECUTED)

Status: **NOT REQUIRED** (credential never pushed to remote in this sprint).
If a future push is required, prepare:
- Affected repos: only `arifOS/arifOS` (this local tree)
- Affected commits: 14 commits in HEAD containing the credential value
- Affected branches: only `main` (no other local branches)
- Affected tags: none tagged in this sprint
- Collaborators requiring reclone: 1 (local + any remote collaborators who pull)
- Force-push consequences: would break local clones; would not break git objects (still in reflog until GC)
- Rollback limitations: `git reflog` retains objects for 90 days default; `--gc-reflog` purges earlier

**BLOCKED on `ACK_HISTORY_REWRITE`.**

## VERDICT

- active_secret_compromised: **YES**
- plaintext_present_in_current_tree: **YES** (3 tracked + untracked files)
- plaintext_present_in_git_history: **YES** (14 commits in HEAD, none pushed to remote in this sprint)
- rotation_required: **YES**
- rotation_executed: **NO** (awaiting ACK_M7_ROTATE_DB_SECRET)
- old_secret_rejected: **NO** (still active on `arifos_admin` role)

**HOLD — Local_PatchSet. Awaiting F13 acknowledgement.**
