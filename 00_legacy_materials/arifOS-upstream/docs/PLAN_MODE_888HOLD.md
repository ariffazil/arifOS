# Plan Mode — 888_HOLD UX Pattern

**Authority:** arifOS_bot
**Version:** 1.0
**Status:** DESIGN NOTE

---

## Problem

888_HOLD exists as a governance mechanism, but the UX for surfacing a HOLD to Arif is not standardized. Different agents and different situations surface holds differently — some too verbose, some too terse, some buried in explanation.

This document defines the canonical Plan Mode presentation for 888_HOLD events.

---

## When to Trigger Plan Mode

**Trigger when:**
- Action is irreversible or high-stakes (destructive, externally consequential, identity-shaping)
- Rollback path is weak or absent
- Task requires access to secrets, live systems, or production
- Action affects the constitutional state of arifOS
- Uncertainty is high and speculation could be costly

**Do NOT trigger for:**
- Read operations (unless the read itself is sensitive)
- Reversible formatting/editing
- Short answers to direct questions
- Routine tool calls with clear, bounded outcomes

---

## Plan Mode Template

When 888_HOLD triggers, present this structure:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  HOLD — [Short description of what needs approval]

WHAT:
[One sentence: what action is proposed]

WHY IT'S IRREVERSIBLE / HIGH-STAKES:
[Brief: what's the downside if this goes wrong]

WHAT I NEED FROM YOU:
[Exactly what Arif needs to decide: yes/no/specific choice]

ROLLBACK PATH:
[If yes — what happens. If no — what I do instead.]

TO PROCEED: /approve [option]
TO VETO:    /deny or just say no
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Examples

### Example 1 — Destructive git operation

```
⚠️  HOLD — Secrets still in git history (irreversible scrub)

WHAT:
Run BFG --delete-files on arifOS repo to purge committed secrets from history.

WHY IRREVERSIBLE:
BFG rewrites git history. All collaborators must re-clone. Past PRs lose diff context.

WHAT I NEED FROM YOU:
Confirm you want history rewritten. Alternative: keep index clean, leave history as-is.

ROLLBACK PATH:
If yes: history rewritten, collaborators notified to re-clone.
If no: SECRETS.yml stays out of index, git history intact, no change.

TO PROCEED: /approve
TO VETO:    /deny
```

### Example 2 — Live system change

```
⚠️  HOLD — Restart arifosmcp container (brief downtime)

WHAT:
Recreate arifosmcp container with new environment variables.

WHY:
Container needs new vault env vars to connect to vault_postgres. No other way.

WHAT I NEED FROM YOU:
Confirm container restart. ~10 seconds downtime on internal governance MCP.

ROLLBACK PATH:
If yes: new container running, old container image retained for rollback.
If no: current container keeps running, vault connection stays degraded.

TO PROCEED: /approve
TO VETO:    /deny
```

### Example 3 — External-facing action

```
⚠️  HOLD — Push arifOS docs to public GitHub

WHAT:
Force push cleaned repo to github.com/ariffazil/arifOS main branch.

WHY:
Makes engineering hardening changes public. Visible to anyone watching the repo.

WHAT I NEED FROM YOU:
Confirm this is the right moment to go public with this layer of the stack.

ROLLBACK PATH:
If yes: public. If no: we keep it local/dev until you're ready.

TO PROCEED: /approve
TO VETO:    /deny
```

---

## Anti-Patterns

### ❌ Burying the HOLD in a paragraph
```
"I was thinking maybe we could perhaps if it's okay with you run the BFG tool
which would sort of change the git history a bit but only for secrets..."
```
→ Rewrite: see template above.

### ❌ Asking permission when the answer is obvious
```
"Can I close the database connection now?"
```
→ If truly trivial, don't trigger a HOLD. If non-trivial, use the template.

### ❌ Presenting FIVE options in a HOLD
One HOLD = one decision. If there are 5 sub-decisions, break into 5 separate holds.

---

## Bot-Side Implementation

When 888_HOLD fires, the agent MUST:
1. Stop execution immediately
2. Render the template (not free-form text)
3. Await `/approve` or `/deny` — do not proceed on silence
4. If silence > 10 minutes, surface a reminder with "Still waiting for approval on: [brief one-liner]"

---

## The /approve Shortcut

Arif can reply with `/approve` to proceed, or just say "go ahead".
The agent treats any explicit positive signal as approval.
Silence = HOLD, not approval.

---

*Ditempa Bukan Diberi*
arifOS_bot | arifOS v2026.04.19
