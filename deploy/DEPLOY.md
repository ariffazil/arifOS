# DEPLOY.md — arifOS Deployment Topology

> **DITEMPA BUKAN DIBERI.** This is not optional knowledge. Read before deploying.

## The Two-Repo Problem

arifOS lives in two places. They are NOT the same.

| Location | Purpose | Branch | Service |
|----------|---------|--------|---------|
| `/root/arifOS/` | Dev tree — where code is written | any branch | none (source only) |
| `/opt/arifos/app/` | Live kernel — where code runs | `main` (dirty) | `arifos.service` (systemd) |

**The gap:** Changes committed to the dev tree are NOT live until all 5 steps below pass.

## Deploy Sequence (5 steps, all required)

```bash
# 1. COMMIT — code in dev tree
cd /root/arifOS && git add -A && git commit -m "feat: description"

# 2. MERGE — to main (fast-forward if possible)
git checkout main && git merge --ff-only <branch>

# 3. PUSH — to origin
git push origin main

# 4. SYNC — to live kernel
cd /opt/arifos/app && git pull origin main
# OR: rsync -av --exclude='.git' /root/arifOS/ /opt/arifos/app/

# 5. RESTART — systemd service
systemctl restart arifos.service

# 6. VERIFY — external probe (not internal grep)
curl -sf http://localhost:8088/health
curl -sf http://localhost:8088/tools | python3 -c "import sys,json; print(len(json.load(sys.stdin)['tools']))"
```

## Three-Tense Contract

Every deployment claim must answer all three:

| Tense | Question | How to verify |
|-------|----------|---------------|
| **COMMITTED** | Is the code in git? | `git log --oneline -1` in dev tree |
| **DEPLOYED** | Is the process running it? | `systemctl status arifos.service` + check `MainPID` |
| **VERIFIED** | Does external HTTP confirm? | `curl localhost:8088/health` — not internal grep |

**Never claim LIVE without all three.** A file on disk is not live. A process running old code is not current. An internal self-report can lie (see: `tool_count=0` while 7 tools are callable).

## Backup Before Deploy

```bash
# Always back up the live kernel before syncing
cp -r /opt/arifos/app /root/.backups/$(date +%Y-%m-%d)-pre-deploy/
```

## History of Theater (Why This Doc Exists)

| Date | What happened | Root cause |
|------|--------------|------------|
| 2026-07-04 | actor_verified fix claimed "LIVE" but envelope still returned false | Changes copied to wrong path, never git-synced |
| 2026-07-04 | 9-tool surface claimed "deployed" but live kernel still had CANONICAL_7 | Manual file copy without service restart |
| 2026-07-04 | `tool_count=0` in organ_attest while 7 tools callable | Internal accounting broken, no external verification |

**Pattern:** Every theater incident had the same root cause — claiming deployment without external verification.

**Fix:** This document + INVARIANTS #13 + Three-Tense Contract.

## Quick Health Check

```bash
# One-liner: is the live kernel healthy AND running current code?
curl -sf http://localhost:8088/health >/dev/null && \
  LIVE=$(curl -sf http://localhost:8088/tools | python3 -c "import sys,json; print(len(json.load(sys.stdin)['tools']))") && \
  DEV=$(cd /root/arifOS && git log --oneline -1 | cut -d' ' -f1) && \
  echo "Live tools: $LIVE | Dev HEAD: $DEV"
```

---

*Forged 2026-07-04 by FORGE (000Ω). The deployment topology is not optional knowledge.*
*DITEMPA BUKAN DIBERI.*
