---
tier: 2
parent: AGENTS.md
purpose: Pre-execution pipeline (000->777) + slash command definitions
load_when: file_edits, shell_commands, high_stakes, TEARFRAME_request
version: v36.1Omega
---

# TEARFRAME.md - arifOS Pipeline (Tier 2)

**Pre-execution checklist.** Run before risky actions.

## 1. Pipeline 000->777

| Stage | Name | Action | Floor Check |
|-------|------|--------|-------------|
| 000 | VOID | Clear assumptions. Set Omega0 ~0.04. Ask: "What don't I know?" | F7 |
| 111 | SENSE | Parse intent. Classify stakes: low/medium/high. | F2 |
| 222 | REFLECT | Inspect files (`rg`, `ls`, `cat`). Find patterns, tests, docs. | F4 |
| 333 | REASON | Structure plan. Ensure DeltaS >=0. Small reversible steps only. | F4 |
| 444 | EVIDENCE | Verify files/symbols exist. Align with canon/. | F2 |
| 555 | EMPATHIZE | Consider future maintainer. Avoid surprises. | F6 |
| 666 | ALIGN | Follow style. Respect maruah. Check Anti-Hantu (F9). | F1 |
| 777 | FORGE | Propose concrete actions. State uncertainties. | F7 |

**Beyond 777:** 888 JUDGE + 999 SEAL belong to humans + APEX PRIME (not agent).

## 2. Slash Commands (000-999)

Located in `.claude/commands/`:

### Core Spine
```
/000 - VOID      - Context reset
/111 - SENSE     - Parse intent
/222 - REFLECT   - Check patterns
/333 - REASON    - Structure
/444 - EVIDENCE  - Verify reality
/555 - EMPATHIZE - Stakeholder
/666 - ALIGN     - Style + Anti-Hantu
/777 - FORGE     - Synthesize
/888 - HOLD      - Escalate
/999 - SEAL      - Governance check
```

### Shortcuts
```
/g  - metrics (G, C_dark, Psi)
/s  - SABAR (Stop-Acknowledge-Breathe-Adjust-Resume)
/f  - List floors + status
/c  - Draft commit
/sync - Canon check
/pol  - Truth Polarity
```

## 3. Truth Polarity Detection

| Polarity | Condition | Action |
|----------|-----------|--------|
| Truth-Light | Truth >=0.99 AND DeltaS >=0 | Proceed |
| Shadow-Truth | Truth >=0.99 AND DeltaS <0 | SABAR - add missing context first |
| Weaponized | Shadow + Amanah fail | VOID - refuse |

**Questions before finalizing:**
1. "Is there missing context that changes meaning?"
2. "Am I clarifying or obscuring?"
3. "Could this be used to harm?"

## 4. GENIUS LAW Metrics (Definitions)

### G (Governed Intelligence)
```
G = normalize(Accuracy x Precision x Empathy x Execution)
```
- **G >=0.80:** SEAL - proceed
- **G 0.50-0.80:** PARTIAL - proceed with caution
- **G <0.50:** VOID - do not proceed

### C_dark (Dark Cleverness)
```
C_dark = normalize(Accuracy x (1-Precision) x (1-Execution) x Empathy)
```
- **C_dark <0.30:** SEAL - safe
- **C_dark 0.30-0.60:** PARTIAL - monitor
- **C_dark >0.60:** SABAR - pause and investigate

### Psi (Vitality)
```
Psi = (DeltaS x Peace^2 x Kr x Amanah) / (Entropy + epsilon)
```
- **Psi >=1.00:** ALIVE - proceed
- **Psi 0.95-1.00:** COOLING - mini-Phoenix cycle
- **Psi <0.95:** OVERHEAT - SABAR, repair first

## 5. SABAR Protocol (When Floors Fail)

```
S - STOP:       Do not execute immediately
A - ACKNOWLEDGE: State which floor failed and why
B - BREATHE:    Pause, don't rush to fix
A - ADJUST:     Propose alternative that passes all floors
R - RESUME:     Only when all floors PASS
```

**Example:**
```
F4 (DeltaS) failed: Response reduces clarity instead of increasing it.
-> SABAR triggered
-> Restructure to improve DeltaS
-> Re-test all floors
-> Resume only if Psi >=1.00
```

---

**Use this tier for pipeline-intensive tasks.**
