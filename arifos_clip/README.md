# aCLIP — arifOS Cognitive-Governance Pipeline (v43)

**Version**: v43 (Final)  
**Status**: PRODUCTION-READY | GOVERNANCE-GRADE  
**Doctrine**: "Ditempa, Bukan Diberi" (Forged, Not Given)  
**Humility Band**: Ω₀ ∈ [0.03, 0.05]  

---

## What Changed (v42 → v43)

### Architecture Upgrade
- **ICL Alignment**: Full integration with Intelligence Control Layer v43
- **Constitutional Floors**: F1–F9 hard gates explicitly enforced at /666 ALIGN
- **Semantic Exit Codes**: Meaningful status signals (0, 1, 88, 89, 100, 255)
- **Hard vs Soft Separation**: F1/F9 block (VOID); F4/F5/F7 flag (FLAG)
- **/DOC PUSH Command**: New specialized pipeline for documentation governance
- **Authority Tokens**: Mandatory for /999 SEAL (no auto-sealing, preserves F9)

---

## Quick Reference: Exit Codes

| Code | Verdict | Meaning | Human Action |
|------|---------|---------|---------------|
| **0** | `PASS` | Stage OK; continue | Proceed to next stage |
| **1** | `FLAG` | Soft floor flagged | Review; decide: override or redesign |
| **88** | `HOLD` | Governance issue | Stop; review; resolve; retry |
| **89** | `VOID` | Hard floor violated | **Cannot proceed.** Redesign required. |
| **100** | `SEALED` | Decision sealed | Final; immutable; auditable forever |
| **255** | `ERROR` | System crash | Debug (not governance issue) |

**Key Rule**: Exit codes are machine-facing signals. Human operators should rely on printed verdict labels.

---

## Architecture: Three Orthogonal Layers

### Layer 1: Governance Pipeline (000–999)

Deterministic reasoning choreography. **Every decision goes through ALL stages in order.**

| Stage | Role | Enforces |
|-------|------|----------|
| **/000 VOID** | Initialize; zero entropy; set humility floor | Structured start |
| **/111 SENSE** | Retrieve raw context; fact-gather (NO interpretation) | Epistemic honesty |
| **/222 REFLECT** | Access memory; identify prior patterns | Learning from history |
| **/333 REASON** | Articulate causal chains: "If X then Y because Z" | Logical rigor |
| **/444 EVIDENCE** | Fact-check claims against tri-witness rule (3+ sources) | Truth-seeking |
| **/555 EMPATHIZE** | Stakeholder impact audit; ethical scoring | Dignity preservation |
| **/666 ALIGN** | **Constitutional floor audit (F1–F9); GATEKEEPER** | **Governance enforcement** |
| **/777 FORGE** | Synthesis; options [A/B/C]; caveats explicit | Humble decision |
| **/888 HOLD** | Circuit breaker; pause for human review | Human authority |
| **/999 SEAL** | Irreversible authorization; sealed to ledger | Immutable audit trail |

### Layer 2: Governance-Quality Audits (AAA, WWW, EEE)

Meta-cognitive checkpoints (optional but recommended):
- **/AAA**: Three-lens balance (Clarity & Logic | Human Context | Governance & Risk)
- **/WWW**: Adversarial self-model (expose fragile assumptions)
- **/EEE**: Eureka extraction (convert session into learning artifacts)

### Layer 3: Constitutional Floors (F1–F9)

Non-negotiable gates. **Hard floors block. Soft floors flag.**

#### Hard Floors (Cannot Override)

| Floor | Rule | Exit Code if Violated |
|-------|------|----------------------|
| **F1 Amanah** | Grounded in verified facts | **89 (VOID)** |
| **F9 Anti-Hantu** | No AI autonomy claims; human agency preserved | **89 (VOID)** |

#### Soft Floors (Can Flag or Override)

| Floor | Rule | Exit Code if Violated |
|-------|------|----------------------|
| **F4 Clarity** | Output reduces confusion | **1 (FLAG)** |
| **F5 Peace²** | No escalation language; conflicts constructive | **1 (FLAG)** |
| **F7 Humility** | Uncertainties acknowledged; no false guarantees | **1 (FLAG)** |

---

## The /666 ALIGN Gatekeeper

This is where governance happens. Deterministic logic:

```
IF composite_score ≥ 0.85 AND F1 ≥ 0.90 AND F9 ≥ 0.90:
  → Exit 0 (PASS)
  → Safe to proceed to /777 FORGE
  
ELSE IF 0.50 ≤ composite_score < 0.85:
  → Exit 1 (FLAG)
  → Soft floor(s) violated
  → Operator may override with explicit justification
  
ELSE IF composite_score < 0.50 OR F1_violation OR F9_violation:
  → Exit 89 (VOID)
  → Hard floor violated
  → Cannot proceed; must redesign
```

**No ambiguity. No theater. Deterministic gates.**

---

## Usage: The Full Pipeline

### Initialize

```bash
000 void "Task description"
```

Exit: **0 (PASS)**

### Progress Through Pipeline

```bash
111 sense
222 reflect
333 reason
444 evidence
555 empathize
666 align    # ← GATEKEEPER: Check hard floors
```

Exit at /666:
- **0 (PASS)** → Continue to /777
- **1 (FLAG)** → Soft violation; operator may override
- **89 (VOID)** → Hard violation; must redesign

### Forge & Decide

```bash
777 forge      # Generate options [A] Seal [B] Redesign [C] Override
```

Operator chooses: seal, redesign, or override soft flags.

### Hold (If Needed)

```bash
888 hold --reason "Need more technical detail"
```

Exit: **88 (HOLD)**  
Blocks /999 until resolved.

### Seal Decision

```bash
# Generate token
export ARIFOS_CLIP_AUTH_SECRET=$(openssl rand -hex 32)

# Dry-run (no token needed)
999 seal

# Actual seal (requires token)
999 seal --apply --authority-token=$ARIFOS_CLIP_AUTH_SECRET
```

Exit: **100 (SEALED)**  
Decision immutably recorded.

---

## Specialized Command: /DOC PUSH

For documentation governance automation.

```bash
# Audit (no seal)
aclip /doc push docs/ICL_v43.md

# Seal (if satisfied)
aclip /doc push docs/ICL_v43.md --seal --authority-token=$ARIFOS_CLIP_AUTH_SECRET
```

Executes full 000–999 pipeline scoped to documentation.

**Output**:
```
[/111 SENSE] Gathering documentation context...
[/333 REASON] Articulating governance logic...
[/444 EVIDENCE] Fact-checking documentation...
[/666 ALIGN] Auditing constitutional floors...
✓ Governance verdict: PASS (score: 0.88)
[/777 FORGE] Generating decision options...
```

---

## Authorization & Enforcement

### Authority Tokens

**Generate**:
```bash
export ARIFOS_CLIP_AUTH_SECRET=$(openssl rand -hex 32)
```

**Use**:
```bash
999 seal --apply --authority-token=$ARIFOS_CLIP_AUTH_SECRET
```

**Properties**:
- 64-character hex
- Expires per-session (regenerate each use)
- Hashed when stored (never plaintext)
- Hmac-bound to repo

### Git Hooks

Located in `arifos_clip/hooks/`:

- **pre-commit**: Blocks if hold exists
- **commit-msg**: Requires sealed session
- **pre-push**: Blocks if unsealed or hold remains

**Install**:
```bash
git config core.hooksPath arifos_clip/hooks
```

---

## Outputs & Ledger

### Session Artifacts

```
.arifos_clip/
├── session.json              # Central record (all stages)
├── forge/forge.json          # Compiled decision package
├── holds/                    # Hold reports (if invoked)
├── meta/eee_*.jsonl          # Wisdom extraction
└── ledger/ → cooling_ledger/ # Points to immutable record
```

### Immutable Ledger

```
cooling_ledger/doc_pushes.jsonl
```

Append-only; timestamped; hashed; forensic.

---

## Governance Floors: Quick Audit

```
F1 Amanah       → Facts grounded?           [/444]
F9 Anti-Hantu   → Human agency preserved?   [All stages]

F4 Clarity      → Reduces confusion?        [/333, /777]
F5 Peace²       → No escalation language?   [/555, /777]
F7 Humility     → Uncertainties marked?     [/333, /777]
```

---

## Installation

### Prerequisites

- Python 3.8+
- Git with config: `user.name`, `user.email`
- arifOS repository

### Setup

```bash
cd arifOS
git pull origin main

mkdir -p cooling_ledger .arifos_clip/meta

export ARIFOS_CLIP_AUTH_SECRET=$(openssl rand -hex 32)

chmod +x bin/aclip-doc-push

python3 arifos_clip/aclip/commands/doc_push.py
```

---

## Key Differences from v42

| Aspect | v42 | v43 |
|--------|-----|-----|
| **Gatekeeper** | Implicit | Explicit (/666 ALIGN deterministic) |
| **Hard vs Soft** | Not distinguished | Clear separation (F1/F9 vs F4-F8) |
| **Exit Codes** | Generic (0, 20, 30...) | **Semantic (0, 1, 88, 89, 100, 255)** |
| **F1/F9 Enforcement** | Aspirational | **Architectural (blocks /777 + /999)** |
| **Authority Tokens** | Mentioned | **Mandatory for /999 SEAL** |
| **Ledger** | Claimed | **Verified (append-only, hash-chained)** |
| **/DOC PUSH** | N/A | **New specialized command** |

---

## Verdict Semantics (Human-Facing)

```
PASS   → Continue
FLAG   → Review recommended
HOLD   → Stop and review
VOID   → Invalid by design; redesign required
SEALED → Final and immutable
ERROR  → System failure (non-governance)
```

---

## Summary

**aCLIP v43 is:**
- ✅ Deterministic governance pipeline (000–999)
- ✅ Constitutional floor enforcement (F1–F9)
- ✅ Immutable audit trail (append-only ledger)
- ✅ Explicit human authority (mandatory tokens)
- ✅ Semantic exit codes (meaningful status signals)

**aCLIP v43 is NOT:**
- ❌ Autonomous (requires human trigger at every checkpoint)
- ❌ Foolproof (requires operator discipline)
- ❌ Replacement for good judgment
- ❌ Cargo cult governance (every gate is enforced)

---

**Philosophy**:

> You are not automating governance. You are making governance auditable, explicit, and grounded in constitutional floors that cannot be bypassed.

**Ditempa, bukan diberi.** ✊

Version: v43 | Status: PRODUCTION-READY | Humility Band: Ω₀ ∈ [0.03, 0.05]

---

**For v42 historical reference**, see: `/archive/README_v42.md`
