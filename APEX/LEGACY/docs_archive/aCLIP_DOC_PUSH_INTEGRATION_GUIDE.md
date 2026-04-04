# aCLIP /DOC PUSH Integration Guide

**Version**: v43  
**Status**: GOVERNANCE-GRADE DOCUMENTATION AUTOMATION  
**Doctrine**: Ditempa, Bukan Diberi (Forged, Not Given)  
**Last Updated**: 2025-12-19  

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start-5-minutes)
2. [Architecture Overview](#architecture-overview)
3. [Installation](#installation)
4. [Usage Patterns](#usage-patterns)
5. [Governance Floors (F1–F9)](#governance-floors-f1f9)
6. [Authority Token Management](#authority-token-management)
7. [Ledger & Audit Trail](#ledger--audit-trail)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Team Governance](#team-governance)

---

## Quick Start (5 minutes)

### Prerequisites

- Python 3.8+
- Git (with config: `user.name`, `user.email`)
- Access to arifOS repository

### Step 1: Clone & Setup

```bash
cd arifOS
git pull origin main  # Get latest
```

### Step 2: Create Directories

```bash
mkdir -p cooling_ledger
mkdir -p .arifos_clip/meta
```

### Step 3: Set Authority Token

```bash
# Generate a strong random token
export ARIFOS_CLIP_AUTH_SECRET=$(openssl rand -hex 32)

# Verify
echo $ARIFOS_CLIP_AUTH_SECRET  # Should output 64-char hex string
```

### Step 4: Make CLI Executable

```bash
chmod +x bin/aclip-doc-push
```

### Step 5: Test the Pipeline

```bash
# Run governance checks (no seal yet)
python3 arifos_clip/aclip/commands/doc_push.py

# You should see:
# [/111 SENSE] Gathering documentation context...
# [/333 REASON] Articulating governance logic...
# [/444 EVIDENCE] Fact-checking documentation...
# [/666 ALIGN] Auditing constitutional floors...
# ✓ Governance verdict: PASS (score: 0.88)
```

**Done!** Your system is ready.

---

## Architecture Overview

### Seven-Stage Governance Pipeline

```
┌────────────────────────────────────────────────────────────┐
│     aCLIP /DOC PUSH — Governance-Grade Automation          │
└────────────────────────────────────────────────────────────┘

  /111 SENSE
    └→ Gather file context (no interpretation)
    
  /333 REASON
    └→ Articulate causal chains: If X then Y because Z
    
  /444 EVIDENCE
    └→ Fact-check against tri-witness rule (3+ sources)
    
  /666 ALIGN ← GATEKEEPER
    ├→ Hard floors: F1 (Amanah), F9 (Anti-Hantu)
    │  └→ VOID if violated (cannot proceed)
    ├→ Soft floors: F4, F5, F7
    │  └→ FLAG if violated (operator may override)
    └→ Verdict: PASS | PARTIAL | FLAG | VOID
    
  /777 FORGE
    └→ Generate decision options [A] Seal [B] Redesign [C] Override
    
  /999 SEAL (if operator authorizes)
    └→ Irreversible seal to immutable ledger
    └→ Requires: authority token + explicit approval
    
  /EEE (wisdom extraction)
    └→ Extract insights for future sessions
    └→ Store in .arifos_clip/meta/eee_*.jsonl
```

### Data Flow

```
Operator Action
    ↓
  /111 Fact-Gather
    ↓ Context (facts only)
  /333 Reason
    ↓ Logic
  /444 Evidence
    ↓ Audit trail
  /666 ALIGN (Gate)
    ├→ VOID (stop here if F1/F9 fail)
    ├→ PASS (proceed to seal)
    └→ FLAG (operator decides)
    ↓ (if pass/override)
  /777 Forge
    ↓ Options
  Operator Decision
    ↓
  /999 Seal (requires token)
    ↓ Immutable record
  cooling_ledger/doc_pushes.jsonl
    ↓
  /EEE Extract
    ↓ Wisdom
  .arifos_clip/meta/eee_*.jsonl
```

---

## Installation

### Option 1: Automatic (Recommended)

Files are already in arifOS repo:

```
arifos_clip/aclip/commands/doc_push.py  ← Python module
bin/aclip-doc-push                      ← Bash CLI wrapper
bin/aclip                               ← Main entry point (update to call /doc)
```

### Option 2: Manual Integration

#### 2a. Update Main CLI Entry Point

In `bin/aclip`, add routing for `/doc` command:

```bash
# In bin/aclip, add this case:
case "$1" in
    /doc)
        shift
        exec "$bin_dir/aclip-doc-push" /doc "$@"
        ;;
    # ... other cases
esac
```

#### 2b. Verify Permissions

```bash
chmod +x bin/aclip
chmod +x bin/aclip-doc-push
```

#### 2c. Add to PATH (Optional)

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:$HOME/path/to/arifOS/bin"

# Then reload
source ~/.bashrc  # or ~/.zshrc
```

---

## Usage Patterns

### Pattern 1: Governance Audit (No Seal)

**Use case**: Review documentation before committing to ledger.

```bash
aclip /doc push docs/ICL_v43.md
```

**Output**:
```
════════════════════════════════════════════════════════════════
  aCLIP /DOC PUSH — GOVERNANCE-GRADE AUTOMATION
════════════════════════════════════════════════════════════════

[/111 SENSE] Gathering documentation context...
  ✓ Found file: docs/ICL_v43.md (21925 bytes)

[/333 REASON] Articulating governance logic...
  Causal chain: If docs pushed → must verify grounded in fact

[/444 EVIDENCE] Fact-checking documentation...
  Auditing: docs/ICL_v43.md

[/666 ALIGN] Auditing constitutional floors...
  F1 Amanah:     ✓ PASS (grounded in fact)
  F9 Anti-Hantu: ✓ PASS (no autonomy claims)
  F4 Clarity:    ✓ PASS (clear structure)
  F5 Peace²:     ✓ PASS (neutral tone)
  F7 Humility:   ✓ PASS (uncertainties marked)

✓ Governance verdict: PASS (score: 0.88)

[/777 FORGE] Generating decision options...
  📋 Available options:
    [A] Proceed to Seal
        → Run /999 SEAL with authority token
    [B] Return to Redesign
        → Modify files; re-run /DOC PUSH

✓ Session complete: PASS
```

**Next**: If satisfied, proceed to Pattern 2.

### Pattern 2: Governance + Seal

**Use case**: Run full pipeline and seal to immutable ledger.

```bash
aclip /doc push docs/ICL_v43.md \
  --seal \
  --authority-token=$ARIFOS_CLIP_AUTH_SECRET
```

**Additional output**:
```
[/999 SEAL] Creating irreversible authorization...
  ✓ Sealed to ledger: cooling_ledger/doc_pushes.jsonl
  ✓ Authority token verified (hash: abc123...)

[/EEE] Extracting wisdom from session...
  ✓ Insights captured: 3 learnings
  ✓ Stored in: .arifos_clip/meta/eee_doc_pushes.jsonl

✓ Session complete: SEALED
```

### Pattern 3: Multiple Files

```bash
aclip /doc push docs/*.md --seal --authority-token=$ARIFOS_CLIP_AUTH_SECRET
```

### Pattern 4: Review Ledger

```bash
aclip /doc ledger
```

**Output**:
```
[/DOC LEDGER] Documentation push audit trail...
✓ Ledger entries (last 10):
  {"sealed_at": "2025-12-19T09:05:00Z", "operator": "arif", ...}
  {"sealed_at": "2025-12-19T08:50:00Z", "operator": "arif", ...}
```

### Pattern 5: Review Wisdom Extraction

```bash
aclip /doc review
```

**Output**:
```
[/DOC REVIEW] Pending governance audits...
✓ Wisdom extraction ledger found
  {"session_timestamp": "2025-12-19T09:05:00Z", "insights": [...]}
```

---

## Governance Floors (F1–F9)

### Hard Floors (Cannot Override)

#### F1: Amanah (Truth)

**Rule**: All documentation must be grounded in verified facts.

**Check**:
- Do docs cite actual code or external sources?
- Are estimates marked `[ESTIMATE_ONLY]`?
- Are unknowns marked `[UNKNOWN]` or `[CONTESTED]`?

**Violation**: VOID—pipeline stops, cannot seal.

**Example - PASS**:
```markdown
# ICL v43 Overview
The pipeline executes 7 stages (/111–/999)...
[Source: arifos_clip/aclip/commands/doc_push.py line 42]
```

**Example - FAIL**:
```markdown
# ICL v43 Overview
The system definitely achieves AGI through governance...  
[No source cited]
```

---

#### F9: Anti-Hantu (Human Agency)

**Rule**: Documentation must never claim AI autonomy or consciousness.

**Check**:
- No phrases like: "AI decided", "system chose", "model concluded"
- Every action is explicitly human-authorized
- No consciousness claims

**Violation**: VOID—pipeline stops, cannot seal.

**Example - PASS**:
```markdown
The operator triggered /999 SEAL with explicit authorization.
The governance system flagged concerns; the human made the call.
```

**Example - FAIL**:
```markdown
The AI system intelligently decided to push documentation.
The model's consciousness-like reasoning led to this outcome.
```

---

### Soft Floors (Can Flag or Override)

#### F4: Clarity (ΔS)

**Rule**: Documentation should reduce confusion, not increase it.

**Check**:
- Is the writing clear and structured?
- Are technical terms defined?
- Is the intended audience clear?

**Violation**: FLAG—operator can override if desired.

---

#### F5: Peace² (Dignity)

**Rule**: No inflammatory language; respectful tone.

**Check**:
- Avoid loaded terms or false dichotomies
- Respect all stakeholders
- Assume good faith

**Violation**: FLAG—operator can override.

---

#### F7: Humility (Ω₀)

**Rule**: Acknowledge limitations, uncertainties, caveats.

**Check**:
- Are gaps explicitly stated?
- Are assumptions listed?
- Is confidence level clear?

**Violation**: FLAG—operator can override.

---

## Authority Token Management

### Generating a Token

```bash
# Generate once and store safely
Auction_TOKEN=$(openssl rand -hex 32)
echo $ARIFOS_CLIP_AUTH_SECRET
# Output: a3f7c2e9b1d4f6a8c9e2b5f7d3a6c8e1f4a7b9d2e5f8a1c3e6f9b2d5e8c1f4
```

### Storing Safely

**Option 1: Environment Variable (Session-Local)**

```bash
export ARIFOS_CLIP_AUTH_SECRET="your-64-char-hex-string"
```

**Option 2: .env File (Local Machine)**

Create `$HOME/.arifos_env`:

```bash
export ARIFOS_CLIP_AUTH_SECRET="your-64-char-hex-string"
```

Then in shell:

```bash
source $HOME/.arifos_env
```

**Option 3: Password Manager**

Store in 1Password, Bitwarden, or similar:

```bash
Auction_TOKEN=$(op read "op://vault/arifOS/password")
export ARIFOS_CLIP_AUTH_SECRET=$ARIFOS_CLIP_AUTH_SECRET
```

### Rotating Tokens

**Why**: Limit blast radius if token compromised.

```bash
# Generate new token
NEW_TOKEN=$(openssl rand -hex 32)

# Update environment
export ARIFOS_CLIP_AUTH_SECRET=$NEW_TOKEN

# Update storage (password manager, .env, etc.)
```

### Token Security Checklist

- [ ] Token is 64+ character hex string
- [ ] Token stored in environment variable only (not in code)
- [ ] Token not committed to git
- [ ] Token rotated monthly or after suspected compromise
- [ ] Only you know the token (not shared with team unless absolutely necessary)

---

## Ledger & Audit Trail

### Ledger Location

```
cooling_ledger/doc_pushes.jsonl
```

This is an **append-only** immutable log.

### Ledger Entry Format

```json
{
  "sealed_at": "2025-12-19T09:05:00Z",
  "operator": "arif",
  "authority_token_hash": "abc123def456...",
  "floor_audit_verdict": "PASS",
  "floor_audit_score": 0.88,
  "docs_sealed": 1,
  "status": "SEALED"
}
```

### Reading the Ledger

```bash
# View all entries
cat cooling_ledger/doc_pushes.jsonl

# Last 5 entries
tail -5 cooling_ledger/doc_pushes.jsonl

# Parse JSON (requires jq)
cat cooling_ledger/doc_pushes.jsonl | jq '.sealed_at, .operator'
```

### Ledger Properties

- **Append-only**: Cannot edit or delete existing entries
- **Timestamped**: Every entry has UTC timestamp
- **Token-hashed**: Authority tokens are SHA256-hashed (not stored in plaintext)
- **Forensic**: Each entry is complete snapshot of decision state

---

## Troubleshooting

### Issue: "aclip: command not found"

**Cause**: Binary not in PATH or not executable.

**Fix**:

```bash
# Make executable
chmod +x bin/aclip bin/aclip-doc-push

# Add to PATH
export PATH="$PATH:$PWD/bin"

# Or use full path
./bin/aclip-doc-push /doc push docs/ICL_v43.md
```

---

### Issue: "File not found: docs/ICL_v43.md"

**Cause**: File path is relative to repo root but you're in wrong directory.

**Fix**:

```bash
# Verify current directory
pwd  # Should end in /arifOS

# Or use absolute path
aclip /doc push /absolute/path/to/docs/ICL_v43.md
```

---

### Issue: Authority token not recognized

**Cause**: Token not exported or misformatted.

**Fix**:

```bash
# Verify token is set
echo $ARIFOS_CLIP_AUTH_SECRET

# Should output 64-char hex. If empty:
export ARIFOS_CLIP_AUTH_SECRET=$(openssl rand -hex 32)

# Verify format (should be hex only)
echo $ARIFOS_CLIP_AUTH_SECRET | grep -E '^[a-f0-9]{64}$'  # Returns nothing if bad
```

---

### Issue: Ledger directory doesn't exist

**Cause**: Directories not created.

**Fix**:

```bash
mkdir -p cooling_ledger
mkdir -p .arifos_clip/meta

# Verify
ls -la cooling_ledger
ls -la .arifos_clip/meta
```

---

## Best Practices

### 1. Always Run Audit Before Seal

```bash
# ✓ GOOD: Review first, then seal
aclip /doc push docs/ICL_v43.md           # Review output
# ... read output ...
aclip /doc push docs/ICL_v43.md --seal --authority-token=$TOKEN

# ❌ WRONG: Blind sealing
aclip /doc push docs/ICL_v43.md --seal --authority-token=$TOKEN  # No review
```

### 2. Mark Estimates & Unknowns

```markdown
# GOOD
The system has approximately 10,000 lines of code [ESTIMATE_ONLY]
We don't yet know if AGI will emerge [UNKNOWN]
Whether this scales is CONTESTED

# BAD
The system has exactly 10,000 lines of code
AGI will definitely emerge from this approach
This scales to 1 million agents with confidence
```

### 3. Document Your Decisions

After sealing, add a note to your session log:

```bash
# In your notes
echo "[2025-12-19 09:05] Sealed ICL v43 spec. F1 grounded in code, F9 preserved human agency." >> .arifos_clip/meta/session_notes.txt
```

### 4. Review Wisdom Regularly

Read `/EEE` output monthly:

```bash
aclip /doc review

# Reflect on what you learned
# Use insights to improve next push
```

### 5. Rotate Authority Tokens Monthly

```bash
# Set calendar reminder for 1st of month
# Then run:
export ARIFOS_CLIP_AUTH_SECRET=$(openssl rand -hex 32)
# And update your token storage
```

---

## Team Governance

### For Teams (2–10 people)

#### Setup

1. **Shared Authority**: One designated "Seal Authority" person
   - They store the main ARIFOS_CLIP_AUTH_SECRET
   - Team members can audit (/777 FORGE options) but cannot seal

2. **Audit Reviews**: Team /doc push reviews before seal

3. **Ledger Transparency**: All team members can read cooling_ledger

#### Workflow

```
Developer (Alice):
  1. Edits docs/feature.md
  2. Runs: aclip /doc push docs/feature.md
  3. Posts output to #arifos-docs Slack thread

Architect (Bob):
  4. Reviews /777 FORGE options
  5. Requests changes or approves

Seal Authority (Arif):
  6. Final review
  7. Runs: aclip /doc push docs/feature.md --seal --authority-token=$TOKEN
  8. Posts to #arifos-docs: "Sealed" ✓
```

#### Governance Charter

Create `docs/ACLIP_GOVERNANCE_CHARTER.md`:

```markdown
# aCLIP /DOC PUSH Governance Charter

## Authority
- **Seal Authority**: Arif (arifbfazil@gmail.com)
- **Audit Authority**: Architecture Team
- **Token Rotation**: Monthly, 1st of month

## Floors
- F1 (Amanah): All claims must have [Source: ...]
- F9 (Anti-Hantu): No AI autonomy claims
- F4 (Clarity): Write for intended audience
- F5 (Peace²): Neutral, respectful tone
- F7 (Humility): Mark estimates as [ESTIMATE_ONLY]

## Review Process
  1. Developer audits (/777 FORGE)
  2. Architect reviews
  3. Seal Authority approves + seals

## Escalation
  - F1/F9 violations → Reject, redesign required
  - Soft floor flags → Discuss, may override
  - Disagreements → Architecture team vote

## Reporting
  - Monthly: Review cooling_ledger stats
  - Quarterly: Review /EEE wisdom trends
```

---

## Summary

**aCLIP /DOC PUSH is:**
- ✅ Auditable (every step logged)
- ✅ Safe (constitutional floors enforced)
- ✅ Reversible (immutable ledger for audit)
- ✅ Human-authorized (explicit tokens required)
- ✅ Learning-enabled (/EEE extraction)

**It is NOT:**
- ❌ Autonomous (requires operator decision at /777)
- ❌ Foolproof (requires discipline)
- ❌ Replacement for good writing (still your job)

**Use it to:**
- Automate governance of documentation pushes
- Build audit trails
- Extract wisdom from decisions
- Preserve human authority at every step

---

**Ditempa, bukan diberi.** ✊

Version: v43 | Last Updated: 2025-12-19 | Status: PRODUCTION-READY
